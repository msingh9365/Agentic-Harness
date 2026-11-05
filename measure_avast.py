#!/usr/bin/env python
"""
Length study for the Avast-CTU Public CAPEv2 dataset (reduced reports).

Nebula has no finished preprocessing for this dataset. The repository only has
  * scripts/concept-testing/preprocessing/avast_1_preprocessing/initial.ipynb:
    keeps behavior.summary.resolved_apis and behavior.summary.mutexes,
    lower-cased, train/test split by detection date < 2019-08-01;
  * nebula/preprocessing/wrappers.py: preprocess_nebula_avast(), which trains a
    NEW JSONTokenizerBPE (vocab 50,000, JSON_CLEANUP_SYMBOLS, stopwords=[]) on
    the training split and keeps the first 512 tokens.
This script follows those two pieces of Nebula code (variant A) and adds one
sensitivity variant (B) that keeps all 13 behavior.summary lists.

Sub-commands
    train    train the BPE tokenizer(s) with Nebula's JSONTokenizerBPE.train()
    measure  per-sample token counts, per-field tokens and what survives 512
"""
import argparse
import csv
import json
import math
import os
import random
import sys
import time
from multiprocessing import Pool

import pandas as pd

from measure_lengths import bootstrap_nebula, field_segments, SEQ_LEN, CHUNK

SPLIT_DATE = "2019-08-01"                  # from Nebula's Avast notebook
A_FIELDS = ["resolved_apis", "mutexes"]    # from Nebula's Avast notebook (capa_normalizer)
SUMMARY_FIELDS = ["keys", "resolved_apis", "executed_commands", "write_keys", "files", "read_files",
                  "started_services", "created_services", "write_files", "delete_keys", "read_keys",
                  "delete_files", "mutexes"]   # order as stored in the reports
VARIANTS = {"A": A_FIELDS, "B": SUMMARY_FIELDS}
B_TRAIN_SUBSET = 5000                      # variant B tokenizer is trained on a subset (memory)


def load_labels(data_dir):
    L = pd.read_csv(os.path.join(data_dir, "public_labels.csv"))
    L["split"] = (pd.to_datetime(L.date) < pd.Timestamp(SPLIT_DATE)).map({True: "trainset", False: "testset"})
    return L


def record(summary, variant):
    """Exactly the notebook's normalisation for A: x.lower() on every element."""
    return {f: [str(x).lower() for x in (summary.get(f) or [])] for f in VARIANTS[variant]}


def read_summary(path):
    import orjson
    with open(path, "rb") as fh:
        return orjson.loads(fh.read())["behavior"]["summary"]


def tok_paths(tok_dir, variant):
    prefix = os.path.join(tok_dir, f"avast_{variant}_bpe_50000")
    return prefix, prefix + ".model", prefix + "_vocab.json"


def make_tokenizer(nb, tok_dir, variant):
    from nebula.constants import JSON_CLEANUP_SYMBOLS
    _, model, vocab = tok_paths(tok_dir, variant)
    return nb["JSONTokenizerBPE"](vocab_size=50000, seq_len=SEQ_LEN, model_path=model, vocab=vocab,
                                   cleanup_symbols=JSON_CLEANUP_SYMBOLS, stopwords=[])


# --------------------------------------------------------------------------
def cmd_train(args):
    nb = bootstrap_nebula(args.nebula)
    from nebula.constants import JSON_CLEANUP_SYMBOLS
    L = load_labels(args.data_dir)
    train = L[L.split == "trainset"].sha256.tolist()
    os.makedirs(args.tok_dir, exist_ok=True)
    for v in args.variants:
        ids = train
        if v == "B":
            ids = random.Random(0).sample(train, B_TRAIN_SUBSET)
        print(f"variant {v}: training on {len(ids)} training reports", flush=True)
        recs = [record(read_summary(os.path.join(args.data_dir, "public_small_reports", h + ".json")), v)
                for h in ids]
        prefix, _, _ = tok_paths(args.tok_dir, v)
        t0 = time.time()
        tok = nb["JSONTokenizerBPE"](vocab_size=50000, seq_len=SEQ_LEN,
                                     cleanup_symbols=JSON_CLEANUP_SYMBOLS, stopwords=[])
        tok.train(recs, vocab_size=50000, model_prefix=prefix)
        print(f"variant {v}: trained in {(time.time()-t0)/60:.1f} min, vocab {len(tok.vocab)}", flush=True)


# --------------------------------------------------------------------------
_TOK = {}


def _init(nebula, tok_dir):
    nb = bootstrap_nebula(nebula)
    for v in VARIANTS:
        _TOK[v] = make_tokenizer(nb, tok_dir, v)


def ids(tok, obj):
    return list(tok.encode(obj, pad=False)[0])


def measure_one(item):
    sha, family, mtype, date, split, path = item
    row = {"sha256": sha, "family": family, "type": mtype, "date": date, "split": split,
           "file_bytes": os.path.getsize(path)}
    try:
        s = read_summary(path)
        for f in SUMMARY_FIELDS:
            row[f"n_{f}"] = len(s.get(f) or [])
        for v, fields in VARIANTS.items():
            tok = _TOK[v]
            rec = record(s, v)
            full = ids(tok, rec)
            n = len(full)
            row[f"{v}_tokens"] = n
            row[f"{v}_chunks_fixed"] = max(1, math.ceil(n / CHUNK))
            keys, segs = field_segments(rec)
            seg_ids = [ids(tok, x) for x in segs]
            row[f"{v}_field_attr_exact"] = int(sum(seg_ids, []) == full)
            start = 0
            for k, si in zip(keys, seg_ids):
                row[f"{v}_tok_{k}"] = len(si)
                row[f"{v}_kept_{k}"] = max(0, min(len(si), SEQ_LEN - start))
                start += len(si)
        row["status"] = "ok"
    except Exception as ex:
        row["status"] = "error:" + type(ex).__name__ + ":" + str(ex)[:100]
    return row


def cmd_measure(args):
    L = load_labels(args.data_dir)
    items = [(r.sha256, r.classification_family, r.classification_type, r.date, r.split,
              os.path.join(args.data_dir, "public_small_reports", r.sha256 + ".json")) for r in L.itertuples()]
    missing = [i for i in items if not os.path.exists(i[5])]
    items = [i for i in items if os.path.exists(i[5])]
    print(f"{len(items)} reports with labels; {len(missing)} labels without a report file")
    if args.limit:
        random.Random(args.seed).shuffle(items)
        items = items[:args.limit]
        print(f"random subset of {len(items)} (seed={args.seed})")
    items.sort(key=lambda x: -os.path.getsize(x[5]))
    cols = (["sha256", "family", "type", "date", "split", "file_bytes", "status"] +
            [f"n_{f}" for f in SUMMARY_FIELDS] +
            [f"{v}_{c}" for v in VARIANTS for c in ("tokens", "chunks_fixed", "field_attr_exact")] +
            [f"{v}_{p}_{f}" for v, fs in VARIANTS.items() for f in fs for p in ("tok", "kept")])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    t0 = time.time()
    with open(args.out, "w", newline="") as fh, \
            Pool(args.workers, initializer=_init, initargs=(args.nebula, args.tok_dir)) as pool:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        for i, row in enumerate(pool.imap_unordered(measure_one, items, chunksize=8), 1):
            w.writerow(row)
            if i % 5000 == 0 or i == len(items):
                el = time.time() - t0
                print(f"{i}/{len(items)} done, {el/60:.1f} min, eta {(len(items)-i)*el/i/60:.1f} min", flush=True)
    print(f"wrote {args.out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"))
    ap.add_argument("--data-dir", required=True, help="folder with public_labels.csv and public_small_reports/")
    ap.add_argument("--tok-dir", default="results/avast/tokenizer")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("train")
    p.add_argument("--variants", nargs="+", default=["A", "B"])
    p = sub.add_parser("measure")
    p.add_argument("--out", default="results/avast/samples.csv")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    args = ap.parse_args()
    {"train": cmd_train, "measure": cmd_measure}[args.cmd](args)


if __name__ == "__main__":
    main()
