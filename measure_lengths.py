#!/usr/bin/env python
"""
Measure how long Nebula's input sequences really are, using Nebula's OWN
preprocessing code (imported from a clone of https://github.com/dtrizna/nebula).

Sub-commands
    sanity   run on the example reports in <nebula>/emulation/ and compare with
             the expected token counts
    inspect  load dtrizna/quovadis-speakeasy with `datasets` (streaming), print
             splits / columns / 2 rows, and check the grouping key against the
             raw files
    measure  run the measurement on the raw dataset files and write CSVs

Nothing here re-implements Nebula. The only code that is not imported from
Nebula is (a) the small bootstrap that avoids importing torch/lief through
nebula/__init__.py and (b) the bookkeeping that splits a report into its
top-level fields so we can attribute tokens to fields.
"""
import argparse
import ast
import csv
import glob
import json
import math
import os
import random
import sys
import time
import types
import warnings
from multiprocessing import Pool

warnings.filterwarnings("ignore")

SEQ_LEN = 512          # Nebula's cut (pad_sequence keeps encoded[:512])
CHUNK = 512            # chunk size for the chunking simulation
OVERLAP = 64           # overlap for long entry points
FIELDS = ["registry_access", "network_events.traffic", "file_access", "apis"]


# --------------------------------------------------------------------------
# bootstrap: import nebula.preprocessing without nebula/__init__.py
# --------------------------------------------------------------------------
def bootstrap_nebula(nebula_root):
    src = os.path.join(os.path.abspath(nebula_root), "nebula")
    if not os.path.isdir(src):
        sys.exit(f"Nebula source folder not found: {src}")
    for name, path in [("nebula", src),
                       ("nebula.preprocessing", os.path.join(src, "preprocessing")),
                       ("nebula.models", os.path.join(src, "models"))]:
        m = types.ModuleType(name)
        m.__path__ = [path]
        m.__file__ = os.path.join(path, "__init__.py")  # pe.py uses nebula.__file__
        sys.modules[name] = m

    ember = types.ModuleType("nebula.models.ember")
    ember.PEFeatureExtractor = object  # only used by PEStaticFeatureExtractor
    sys.modules["nebula.models.ember"] = ember

    # nebula.misc: copy ONLY get_alphanum_chars(), taken verbatim from the
    # source file with `ast` so it cannot drift from Nebula's version.
    misc_src = open(os.path.join(src, "misc", "__init__.py")).read()
    fn = next(n for n in ast.parse(misc_src).body
              if isinstance(n, ast.FunctionDef) and n.name == "get_alphanum_chars")
    misc = types.ModuleType("nebula.misc")
    misc.__file__ = os.path.join(src, "misc", "__init__.py")
    exec("import string\n" + ast.get_source_segment(misc_src, fn), misc.__dict__)
    sys.modules["nebula.misc"] = misc

    from nebula.constants import SPEAKEASY_RECORD_FIELDS, SPEAKEASY_RECORD_LIMITS
    from nebula.preprocessing.tokenization import JSONFilter, JSONTokenizerBPE
    from nebula.preprocessing.pe import PEDynamicFeatureExtractor
    return dict(SPEAKEASY_RECORD_FIELDS=SPEAKEASY_RECORD_FIELDS,
                SPEAKEASY_RECORD_LIMITS=SPEAKEASY_RECORD_LIMITS,
                JSONFilter=JSONFilter, JSONTokenizerBPE=JSONTokenizerBPE,
                PEDynamicFeatureExtractor=PEDynamicFeatureExtractor)


class Nebula:
    """Nebula's preprocessing objects, built exactly as Nebula builds them."""

    def __init__(self, nebula_root):
        nb = bootstrap_nebula(nebula_root)
        self.extractor = nb["PEDynamicFeatureExtractor"](
            speakeasyRecordFields=nb["SPEAKEASY_RECORD_FIELDS"],
            recordLimits=nb["SPEAKEASY_RECORD_LIMITS"])
        # the extractor builds this filter internally; we check it is the one asked for
        assert isinstance(self.extractor.parser, nb["JSONFilter"])
        assert self.extractor.parser.fields == nb["SPEAKEASY_RECORD_FIELDS"]
        objs = os.path.join(os.path.abspath(nebula_root), "nebula", "objects")
        vocab_path = os.path.join(objs, "bpe_50000_vocab.json")
        with open(vocab_path) as f:
            vocab = json.load(f)
        self.tokenizer = nb["JSONTokenizerBPE"](
            vocab_size=len(vocab), seq_len=SEQ_LEN,
            model_path=os.path.join(objs, "bpe_50000_sentencepiece.model"),
            vocab=vocab_path)
        self.vocab_size = len(vocab)

    def report(self, entry_points):
        return self.extractor.filter_and_normalize_report(entry_points)

    def n_tokens(self, report):
        return len(self.tokenizer.encode(report, pad=False)[0])

    def ids(self, obj):
        return list(self.tokenizer.encode(obj, pad=False)[0])


# --------------------------------------------------------------------------
# per-sample measurement
# --------------------------------------------------------------------------
def field_segments(report):
    """Split str(report) -- the exact string Nebula's tokenizer cleans -- into
    one piece per top-level field, in the dict's own order. The pieces are cut
    at ", '" so the cleaning step (symbols -> spaces) cannot join them."""
    keys = list(report.keys())
    segs = []
    for i, k in enumerate(keys):
        head = "{" if i == 0 else ", "
        segs.append(head + repr(k) + ": " + str(report[k]))
    if segs:
        segs[-1] += "}"
    else:
        segs = ["{}"]
    assert "".join(segs) == str(report)
    return keys, segs


def entry_points_of(data):
    """A file is either the entry_points list itself (all files in the HF
    dataset) or a full Speakeasy report dict holding it under 'entry_points'
    (what PEDynamicFeatureExtractor.emulate() unpacks)."""
    if isinstance(data, dict) and "entry_points" in data:
        return data["entry_points"]
    return data


def chunks_fixed(n):
    return max(1, math.ceil(n / CHUNK))


def chunks_for_ep(t):
    if t <= CHUNK:
        return 1
    stride = CHUNK - OVERLAP
    return 1 + math.ceil((t - CHUNK) / stride)


def measure_sample(nb, entry_points, with_eps=True):
    out = {"status": "ok"}
    rep = nb.report(entry_points)
    if not rep:
        out["status"] = "filtered_by_nebula"   # Nebula drops this sample
        return out, []

    ids = nb.ids(rep)
    n = len(ids)
    out["tokens"] = n
    out["tokens_kept_512"] = min(n, SEQ_LEN)
    out["tokens_dropped_512"] = max(0, n - SEQ_LEN)
    out["chunks_fixed"] = chunks_fixed(n)

    # field attribution
    keys, segs = field_segments(rep)
    out["field_order"] = "|".join(keys)
    seg_ids = [nb.ids(s) for s in segs]
    out["field_attr_exact"] = int(sum(seg_ids, []) == ids)
    start = 0
    for k, si in zip(keys, seg_ids):
        t = len(si)
        out[f"tok_{k}"] = t
        out[f"kept_{k}"] = max(0, min(t, SEQ_LEN - start))
        start += t

    # entry points
    eps = entry_points if isinstance(entry_points, list) else []
    out["n_entry_points"] = len(eps)
    out["n_module_entry"] = sum(1 for e in eps if isinstance(e, dict) and e.get("ep_type") == "module_entry")
    out["n_thread"] = sum(1 for e in eps if isinstance(e, dict) and e.get("ep_type") == "thread")
    ep_rows = []
    if with_eps:
        for j, ep in enumerate(eps):
            row = {"ep_index": j, "ep_type": ep.get("ep_type") if isinstance(ep, dict) else None,
                   "n_apis": len(ep.get("apis") or []) if isinstance(ep, dict) else 0,
                   "error_type": ((ep.get("error") or {}).get("type") if isinstance(ep, dict) else None)}
            try:
                r = nb.report([ep])
                if not r:
                    row["status"] = "filtered_by_nebula"
                else:
                    row["status"] = "ok"
                    row["tokens"] = nb.n_tokens(r)
                    row["chunks"] = chunks_for_ep(row["tokens"])
            except Exception as ex:  # keep going, record it
                row["status"] = "error:" + type(ex).__name__
            ep_rows.append(row)
        ok = [r for r in ep_rows if r["status"] == "ok"]
        out["n_ep_tokenized"] = len(ok)
        out["ep_tokens_sum"] = sum(r["tokens"] for r in ok)
        out["ep_tokens_max"] = max((r["tokens"] for r in ok), default=0)
        out["chunks_per_ep"] = sum(r["chunks"] for r in ok)
    # raw emulation size: Speakeasy stopped at max_api_count=500 (dataset config)
    out["n_apis_raw"] = sum(len(e.get("apis") or []) for e in eps if isinstance(e, dict))
    out["hit_api_cap"] = int(any(isinstance(e, dict) and (e.get("error") or {}).get("type") == "max_api_count"
                                 for e in eps))
    return out, ep_rows


# --------------------------------------------------------------------------
# sanity
# --------------------------------------------------------------------------
EXPECTED = {
    "report_example_entrypoint_with_file.json": 551,
    "report_example_entrypoint_with_registry.json": 1672,
    "report_example_entrypoint_withDNS.json": 1811,
    "report_example_entrypoint_ransomware.json": 2609,
    "report_example_full.json": 57,
}


def cmd_sanity(args):
    nb = Nebula(args.nebula)
    print(f"vocab size: {nb.vocab_size}")
    folder = os.path.join(args.nebula, "emulation")
    ok_all = True
    for name, exp in EXPECTED.items():
        path = os.path.join(folder, name)
        with open(path) as f:
            data = json.load(f)
        note = ""
        if isinstance(data, dict) and "entry_points" in data:
            # full Speakeasy report: Nebula's emulate() passes report["entry_points"]
            whole = nb.n_tokens(nb.report(data))
            note = f" (whole dict instead of entry_points would give {whole})"
        rep = nb.report(entry_points_of(data))
        got = nb.n_tokens(rep)
        ok = got == exp
        ok_all &= ok
        print(f"{name:48s} type={type(data).__name__:4s} keys={list(rep.keys())} "
              f"tokens={got:5d} expected={exp:5d} {'OK' if ok else 'MISMATCH'}{note}")
        # field-attribution check on the same report
        _, segs = field_segments(rep)
        exact = sum((nb.ids(s) for s in segs), []) == nb.ids(rep)
        print(f"{'':48s} field-split tokens concat == full tokens: {exact}")
    print("ALL MATCH" if ok_all else "SOME MISMATCH")
    return 0 if ok_all else 1


# --------------------------------------------------------------------------
# inspect
# --------------------------------------------------------------------------
def cmd_inspect(args):
    from datasets import load_dataset
    ds = load_dataset("dtrizna/quovadis-speakeasy", streaming=True)
    print("splits:", list(ds.keys()))
    for split, s in ds.items():
        print(f"split={split} n_shards={s.num_shards} features={s.features}")
        it = iter(s)
        first = [next(it) for _ in range(2)]
        print("columns of first rows:", list(first[0].keys()))
        for i, r in enumerate(first):
            print(f"--- example row {i}")
            for k, v in r.items():
                print(f"  {k}: {str(v)[:200]}")
    if args.data_dir:
        verify_grouping(args.data_dir)


def list_files(data_dir):
    rows = []
    for split_dir in sorted(glob.glob(os.path.join(data_dir, "windows_emulation_*"))):
        split = os.path.basename(split_dir).replace("windows_emulation_", "")
        for fam_dir in sorted(glob.glob(os.path.join(split_dir, "report_*"))):
            folder = os.path.basename(fam_dir)
            # trainset/report_backdoor and trainset/report_clean are sharded into
            # sub-folders 0..f by the first hex digit of the sha256, so walk recursively
            for root, _, names in os.walk(fam_dir):
                for p in sorted(names):
                    rows.append((split, folder, p, os.path.join(root, p)))
    return rows


def verify_grouping(data_dir):
    """Check that the raw file is the only sample identifier available."""
    import orjson
    from collections import Counter
    files = list_files(data_dir)
    exts = Counter(os.path.splitext(f[2])[1] for f in files)
    print(f"\nraw files: {len(files)} by extension {dict(exts)}")
    jfiles = [f for f in files if f[2].endswith(".json")]
    n_rows, shapes, ep_types, keysets = 0, Counter(), Counter(), Counter()
    apihash_files = {}
    dup_apihash_across = 0
    stems = Counter(os.path.splitext(f[2])[0] for f in jfiles)
    for split, folder, name, path in jfiles:
        with open(path, "rb") as fh:
            d = orjson.loads(fh.read())
        shapes[type(d).__name__] += 1
        eps = d if isinstance(d, list) else d.get("entry_points", [])
        n_rows += len(eps)
        for e in eps:
            ep_types[e.get("ep_type")] += 1
            keysets.update(e.keys())
            h = e.get("apihash")
            if h is not None:
                prev = apihash_files.setdefault(h, path)
                if prev != path:
                    dup_apihash_across += 1
    print(f"top-level JSON type per file: {dict(shapes)}")
    print(f"total entry points (= datasets rows): {n_rows}")
    print(f"ep_type counts: {dict(ep_types)}")
    print(f"entry-point keys seen: {dict(keysets)}")
    print(f"distinct apihash values: {len(apihash_files)}; entry points whose apihash "
          f"also appears in another file: {dup_apihash_across}")
    print(f"file stems duplicated across folders: {sum(1 for v in stems.values() if v > 1)}")


# --------------------------------------------------------------------------
# measure
# --------------------------------------------------------------------------
_NB = None


def _init(nebula_root):
    global _NB
    _NB = Nebula(nebula_root)


def _work(item):
    import orjson
    split, folder, name, path, with_eps = item
    fam = folder.replace("report_", "")
    base = {"split": split, "family": fam,
            "is_malware": int(folder not in ("report_clean", "report_windows_syswow64")),
            "sample_id": os.path.splitext(name)[0], "file_bytes": os.path.getsize(path)}
    t0 = time.time()
    try:
        with open(path, "rb") as fh:
            data = orjson.loads(fh.read())
        base["file_shape"] = type(data).__name__
        res, eps = measure_sample(_NB, entry_points_of(data), with_eps=with_eps)
    except Exception as ex:
        res, eps = {"status": "error:" + type(ex).__name__ + ":" + str(ex)[:100]}, []
    res["seconds"] = round(time.time() - t0, 3)
    for e in eps:
        e.update({"split": split, "family": fam, "sample_id": base["sample_id"]})
    return {**base, **res}, eps


SAMPLE_COLS = ["split", "family", "is_malware", "sample_id", "file_bytes", "file_shape", "status",
               "tokens", "tokens_kept_512", "tokens_dropped_512", "chunks_fixed",
               "field_order", "field_attr_exact"] + \
              [f"{p}_{f}" for f in FIELDS for p in ("tok", "kept")] + \
              ["n_entry_points", "n_module_entry", "n_thread", "n_ep_tokenized",
               "ep_tokens_sum", "ep_tokens_max", "chunks_per_ep", "n_apis_raw", "hit_api_cap", "seconds"]
EP_COLS = ["split", "family", "sample_id", "ep_index", "ep_type", "status", "tokens", "chunks",
           "n_apis", "error_type"]


def cmd_measure(args):
    files = list_files(args.data_dir)
    skipped = [f for f in files if not f[2].endswith(".json")]
    files = [f for f in files if f[2].endswith(".json")]
    print(f"{len(files)} .json sample files; skipping {len(skipped)} non-json: "
          f"{[os.path.join(f[0], f[1], f[2]) for f in skipped]}")
    if args.limit and args.limit < len(files):
        random.Random(args.seed).shuffle(files)
        files = files[:args.limit]
        print(f"random subset of {len(files)} files (seed={args.seed})")
    os.makedirs(args.out, exist_ok=True)
    s_path = os.path.join(args.out, f"{args.prefix}samples.csv")
    e_path = os.path.join(args.out, f"{args.prefix}entry_points.csv")
    items = [(*f, not args.no_eps) for f in files]
    # biggest files first so the pool does not end on one huge straggler
    items.sort(key=lambda x: -os.path.getsize(x[3]))
    t0 = time.time()
    with open(s_path, "w", newline="") as fs, open(e_path, "w", newline="") as fe, \
            Pool(args.workers, initializer=_init, initargs=(args.nebula,), maxtasksperchild=500) as pool:
        ws = csv.DictWriter(fs, SAMPLE_COLS, extrasaction="ignore")
        we = csv.DictWriter(fe, EP_COLS, extrasaction="ignore")
        ws.writeheader(); we.writeheader()
        for i, (srow, eprows) in enumerate(pool.imap_unordered(_work, items, chunksize=4), 1):
            ws.writerow(srow)
            we.writerows(eprows)
            if i % 1000 == 0 or i == len(items):
                el = time.time() - t0
                print(f"{i}/{len(items)} done, {el/60:.1f} min, eta {(len(items)-i)*el/i/60:.1f} min", flush=True)
    print(f"wrote {s_path} and {e_path} in {(time.time()-t0)/60:.1f} min")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"),
                    help="path to a clone of github.com/dtrizna/nebula")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sanity")
    p = sub.add_parser("inspect")
    p.add_argument("--data-dir", default=None, help="raw snapshot of the HF repo")
    p = sub.add_parser("measure")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--out", default="results")
    p.add_argument("--prefix", default="")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p.add_argument("--no-eps", action="store_true", help="skip per-entry-point tokenization")
    args = ap.parse_args()
    return {"sanity": cmd_sanity, "inspect": cmd_inspect, "measure": cmd_measure}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
