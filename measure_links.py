#!/usr/bin/env python
"""
Data-flow links between API calls in Speakeasy reports, and whether they cross
Nebula's 512-token chunk boundaries.

Definitions
  address-like value  a string matching ^0x[0-9a-fA-F]+$ whose value is >= 0x10000
  link                call j has an argument equal to the address-like return value of an
                      earlier call i (i < j). The producer is the FIRST call that returned the
                      value. Every matching argument counts as one link.
  merged links        over the API list exactly as Nebula sees it after
                      filter_and_normalize_report() (all entry points merged, same order)
  per-EP links        the same, restarted inside every entry point
  chunk of a call     the 512-token chunk (0-based) holding the call's first token in Nebula's
                      tokenized report. The model reads chunks 0..7; links with an end in a
                      later chunk are counted separately ("beyond the window").
  cross-chunk link    producer and user are both in chunks 0..7, in different chunks

Token positions come from tokenizing the report in pieces with Nebula's own
tokenizer.encode (the part before the API list, then each API call) and
ASSERTING that the joined ids equal the full report's ids. If that fails for a
sample, positions are estimated from character offsets and the sample is flagged.

Sub-commands
    sanity   reproduce the reference counts on the 21 example reports (call index, not chunks)
    measure  per-sample CSV + producer/user pair counts
"""
import argparse
import csv
import glob
import json
import os
import random
import re
import sys
import time
import zlib
from collections import Counter
from multiprocessing import Pool

import numpy as np

from measure_lengths import Nebula, entry_points_of, list_files

SEQ_LEN = 512
WINDOW = 8                      # chunks 0..7, as the two-level model reads them
ADDR = re.compile(r"^0x[0-9a-fA-F]+$")
# "handle-creating" producers for the false-link check: prefixes of the API name without its DLL
HANDLE_PREFIXES = ("Create", "Open", "Alloc", "LoadLibrary", "GetProcAddress", "GetModuleHandle",
                   "RegOpen", "RegCreate")
HANDLE_EXACT = ("socket", "connect")


def is_addr(v):
    return isinstance(v, str) and ADDR.match(v) is not None and int(v, 16) >= 0x10000


def api_short(name):
    return str(name).split(".")[-1]


def is_handle_api(name):
    s = api_short(name)
    return s.startswith(HANDLE_PREFIXES) or s in HANDLE_EXACT


def find_links(calls, order=None):
    """Links over calls (list of dicts), visited in `order` (default: as given).
    Returns a list of (i, j) original call indices, producer first in visiting order."""
    first, out = {}, []
    for j in (range(len(calls)) if order is None else order):
        c = calls[j]
        for a in c.get("args") or []:
            if a in first:
                out.append((first[a], j))
        r = c.get("ret_val")
        if is_addr(r) and r not in first:
            first[r] = j
    return out


def report_pieces(rep):
    """str(rep) split into: [text before the first API call, call 0, call 1, ..., closing text].
    Cuts are at ', ' / '[' / ']' so Nebula's cleaning (symbols -> spaces) cannot join pieces."""
    s = str(rep)
    keys = list(rep.keys())
    assert keys[-1] == "apis", keys
    apis_str = str(rep["apis"])
    assert s.endswith(apis_str + "}")
    head = s[:len(s) - len(apis_str) - 1] + "["
    pieces = [head] + [(", " if i else "") + str(c) for i, c in enumerate(rep["apis"])] + ["]}"]
    assert "".join(pieces) == s
    return s, pieces


def call_positions(nb, rep):
    """-> (start token position of each call, token length of each call, total tokens, fallback flag)"""
    s, pieces = report_pieces(rep)
    full = nb.ids(rep)
    piece_ids = [nb.ids(p) for p in pieces]
    if sum(piece_ids, []) == full:
        lens = np.array([len(x) for x in piece_ids[1:-1]], dtype=np.int64)
        starts = len(piece_ids[0]) + np.concatenate([[0], np.cumsum(lens)[:-1]]) if len(lens) else lens
        return starts, lens, len(full), False, len(piece_ids[0])
    # fallback: scale character offsets to token positions
    scale = len(full) / max(1, len(s))
    clen = np.array([len(p) for p in pieces[1:-1]], dtype=np.float64)
    cstart = len(pieces[0]) + np.concatenate([[0], np.cumsum(clen)[:-1]]) if len(clen) else clen
    starts = np.floor(cstart * scale).astype(np.int64)
    lens = np.maximum(1, np.round(clen * scale)).astype(np.int64)
    return starts, lens, len(full), True, int(round(len(pieces[0]) * scale))


def link_stats(links, chunk, calls, prefix=""):
    """Counts for one set of links. chunk[i] = chunk of call i (uncapped)."""
    o = {f"{prefix}n_links": len(links)}
    cross = leave0 = beyond = 0
    maxd = 0
    dist = Counter()
    for i, j in links:
        ci, cj = chunk[i], chunk[j]
        if ci == 0 and cj != 0:
            leave0 += 1
        if ci >= WINDOW or cj >= WINDOW:
            beyond += 1
        elif ci != cj:
            cross += 1
            d = abs(int(cj) - int(ci))
            dist[d] += 1
            maxd = max(maxd, d)
    o[f"{prefix}n_cross_chunk_links"] = cross
    o[f"{prefix}n_links_leaving_chunk0"] = leave0
    o[f"{prefix}n_links_beyond_window"] = beyond
    o[f"{prefix}max_chunk_distance"] = maxd
    return o, dist


def measure_one(nb, entry_points, sample_key):
    rep = nb.report(entry_points)
    if not rep:
        return {"status": "filtered_by_nebula"}, Counter(), Counter()
    calls = rep["apis"]
    eps = entry_points if isinstance(entry_points, list) else []
    sizes = [len(ep.get("apis") or []) for ep in eps]
    assert sum(sizes) == len(calls), (sum(sizes), len(calls))   # merged list = entry points joined in order

    starts, lens, n_tok, fallback, head_len = call_positions(nb, rep)
    chunk = starts // SEQ_LEN
    out = {"status": "ok", "tokens": n_tok, "n_chunks": max(1, -(-n_tok // SEQ_LEN)),
           "n_calls": len(calls), "n_entry_points": len(eps), "fallback_used": int(fallback)}

    # merged links (as Nebula sees the report)
    links = find_links(calls)
    st, dist = link_stats(links, chunk, calls)
    out.update(st)
    for d in range(1, WINDOW):
        out[f"dist_{d}"] = dist.get(d, 0)
    ep_of = np.repeat(np.arange(len(sizes)), sizes) if sizes else np.zeros(0, int)
    out["n_links_across_ep"] = sum(ep_of[i] != ep_of[j] for i, j in links)
    pairs_cross = Counter()
    pairs_all = Counter()
    for i, j in links:
        p = (calls[i]["api_name"], calls[j]["api_name"])
        pairs_all[p] += 1
        if chunk[i] < WINDOW and chunk[j] < WINDOW and chunk[i] != chunk[j]:
            pairs_cross[p] += 1

    # per entry point
    ep_links, pos = [], 0
    for s in sizes:
        ep_links += [(pos + i, pos + j) for i, j in find_links(calls[pos:pos + s])]
        pos += s
    st, _ = link_stats(ep_links, chunk, calls, "ep_")
    out.update(st)

    # false-link check: producer must be a handle-creating API
    hlinks = [(i, j) for i, j in links if is_handle_api(calls[i]["api_name"])]
    st, _ = link_stats(hlinks, chunk, calls, "h_")
    out.update(st)

    # chance baseline: shuffle the order of calls, recompute links and token positions
    rng = random.Random(zlib.crc32(sample_key.encode()))
    order = list(range(len(calls)))
    rng.shuffle(order)
    new_start = np.zeros(len(calls), dtype=np.int64)
    if len(calls):
        new_start[order] = head_len + np.concatenate([[0], np.cumsum(lens[order])[:-1]])
    sh_chunk = new_start // SEQ_LEN
    sh_links = find_links(calls, order)
    st, _ = link_stats(sh_links, sh_chunk, calls, "shuf_")
    out.update(st)
    st, _ = link_stats([(i, j) for i, j in sh_links if is_handle_api(calls[i]["api_name"])], sh_chunk, calls, "shuf_h_")
    out.update(st)
    return out, pairs_cross, pairs_all


# --------------------------------------------------------------------------- sanity
def cmd_sanity(a):
    nb = Nebula(a.nebula)
    files = sorted(f for f in glob.glob(os.path.join(a.examples, "*", "*", "*.raw.json"))
                   if os.sep + "avast" + os.sep not in f)
    print(f"{len(files)} example reports in {a.examples}")
    n_ep = n_links = early = span = n_fallback = 0
    for f in files:
        with open(f) as fh:
            eps = entry_points_of(json.load(fh))
        rep = nb.report(eps)
        calls = rep["apis"]
        sizes = [len(ep.get("apis") or []) for ep in eps]
        assert sum(sizes) == len(calls)
        pos = 0
        for s in sizes:
            ep_calls = calls[pos:pos + s]; pos += s
            if s < 20:
                continue
            L = find_links(ep_calls)
            n_ep += 1; n_links += len(L)
            early += sum(i < 100 <= j for i, j in L)
            span += sum(j - i > 100 for i, j in L)
        n_fallback += call_positions(nb, rep)[3]
    got = (n_links, n_ep, early, span)
    print(f"{n_links} links in {n_ep} entry points (>= 20 calls); {early} produced in the first 100 calls "
          f"and used after them; {span} spanning more than 100 calls")
    print(f"token-position check: {len(files) - n_fallback}/{len(files)} reports exact (no fallback)")
    ok = got == (728, 19, 157, 124)
    print("MATCHES the reference (728, 19, 157, 124)" if ok else f"MISMATCH: expected (728, 19, 157, 124), got {got}")
    return 0 if ok else 1


# --------------------------------------------------------------------------- measure
_NB = None


def _init(nebula_root):
    global _NB
    _NB = Nebula(nebula_root)


def _work(item):
    import orjson
    split, folder, name, path = item
    fam = folder.replace("report_", "")
    sid = os.path.splitext(name)[0]
    row = {"split": split, "family": fam, "label": int(folder not in ("report_clean", "report_windows_syswow64")),
           "sample_id": sid}
    t0 = time.time()
    try:
        with open(path, "rb") as fh:
            data = orjson.loads(fh.read())
        res, pc, pa = measure_one(_NB, entry_points_of(data), f"{split}/{sid}")
    except Exception as ex:
        res, pc, pa = {"status": "error:" + type(ex).__name__ + ":" + str(ex)[:120]}, Counter(), Counter()
    res["seconds"] = round(time.time() - t0, 3)
    return {**row, **res}, pc, pa


COLS = (["split", "family", "label", "sample_id", "status", "tokens", "n_chunks", "n_calls", "n_entry_points",
         "n_links", "n_cross_chunk_links", "n_links_leaving_chunk0", "max_chunk_distance", "fallback_used",
         "n_links_beyond_window", "n_links_across_ep"] + [f"dist_{d}" for d in range(1, WINDOW)] +
        [f"{p}{c}" for p in ("ep_", "h_", "shuf_", "shuf_h_")
         for c in ("n_links", "n_cross_chunk_links", "n_links_leaving_chunk0", "n_links_beyond_window",
                   "max_chunk_distance")] + ["seconds"])


def cmd_measure(a):
    files = [f for f in list_files(a.data_dir) if f[2].endswith(".json")]
    if a.limit:
        random.Random(a.seed).shuffle(files)
        files = files[:a.limit]
        print(f"random subset of {len(files)} samples (seed={a.seed})")
    files.sort(key=lambda x: -os.path.getsize(x[3]))   # big ones first
    os.makedirs(a.out, exist_ok=True)
    s_path = os.path.join(a.out, f"{a.prefix}samples.csv")
    pairs_cross, pairs_all = Counter(), Counter()
    samples_cross, samples_all = Counter(), Counter()
    t0 = time.time()
    with open(s_path, "w", newline="") as fh, Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
        w = csv.DictWriter(fh, COLS, extrasaction="ignore")
        w.writeheader()
        for k, (row, pc, pa) in enumerate(pool.imap_unordered(_work, files, chunksize=4), 1):
            w.writerow(row)
            pairs_cross.update(pc); pairs_all.update(pa)
            samples_cross.update(pc.keys()); samples_all.update(pa.keys())
            if k % 5000 == 0 or k == len(files):
                el = time.time() - t0
                print(f"{k}/{len(files)} done, {el/60:.1f} min, eta {(len(files)-k)*el/k/60:.1f} min", flush=True)
    for name, pc, sc in [("pairs_cross_chunk", pairs_cross, samples_cross), ("pairs_all", pairs_all, samples_all)]:
        with open(os.path.join(a.out, f"{a.prefix}{name}.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["producer_api", "user_api", "links", "samples"])
            for (p, u), n in pc.most_common():
                w.writerow([p, u, n, sc[(p, u)]])
    print(f"wrote {s_path} and pair counts in {(time.time()-t0)/60:.1f} min")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sanity")
    p.add_argument("--examples", default="examples")
    p = sub.add_parser("measure")
    p.add_argument("--data-dir", required=True)
    p.add_argument("--out", default="results/links")
    p.add_argument("--prefix", default="")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    return {"sanity": cmd_sanity, "measure": cmd_measure}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main() or 0)
