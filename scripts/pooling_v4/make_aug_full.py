#!/usr/bin/env python
"""
Round 5, G3: precomputed balanced padding augmentation over the WHOLE report (up to 4,096 tokens, ragged). Same edits (same random numbers) as make_aug.py --balanced,
re-tokenised without the 512-token cut. Files augbw_s<seed>_e<epoch>_rows.npy, _off.npy (cumulative token offsets, int64, n+1) and _tok.npy (uint16, concatenated).
(Docstring of make_aug.py follows.)


    python scripts/pooling_v4/make_aug.py --out <folder> [--seeds 0-4] [--epochs 1-2]

For every (seed, epoch) and every January MALWARE report (train + validation side, regime J) with at least one API call:
with probability 0.5 the report is edited: mode insert (k random places) or prepend (before the first call), 50/50; k uniform
from 1 to 50; each added call is a random call of a random report of the TRAIN pool (results/pooling_v4/pools.json, benign
January reports of groups disjoint from the EVAL pool). The edited report is re-tokenised with Nebula's tokenizer and cut to the
first 512 tokens. Benign reports are never edited. numpy Generator seed [7000, seed, epoch, row].
--balanced: benign training reports are edited the same way (files augb_*), so padding carries no label.
Writes aug_s<seed>_e<epoch>_rows.npy (row numbers in tokens_512.npy) and aug_s<seed>_e<epoch>_tok.npy (uint16 [n, 512]).
The training script puts these rows over the original ones for that epoch only.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_common as V  # noqa: E402
from v4_common import C, _W, _init  # noqa: E402


def _init_train(nebula, pool_rows):
    _init(nebula)
    _W["pool"] = [list(_W["reps"].get(int(r)).get("apis") or []) for r in pool_rows]


def aug_report(apis, row, seed, epoch, pool):
    """None (not edited) or (mode, k, edited apis)."""
    rng = np.random.default_rng([7000, seed, epoch, int(row)])
    if rng.random() >= 0.5 or not apis:
        return None
    mode = "insert" if rng.random() < 0.5 else "prepend"
    k = int(rng.integers(1, 51))
    add = []
    for _ in range(k):
        r = int(rng.integers(len(pool)))
        add.append(pool[r][int(rng.integers(len(pool[r])))])
    if mode == "prepend":
        return mode, k, add + list(apis)
    gaps = np.sort(rng.integers(0, len(apis) + 1, k))
    out, j = [], 0
    for i in range(len(apis) + 1):
        while j < k and gaps[j] == i:
            out.append(add[j]); j += 1
        if i < len(apis):
            out.append(apis[i])
    return mode, k, out


def _work(args):
    row, seed, epoch = args
    nb, rep, pool = _W["nb"], _W["reps"].get(int(row)), _W["pool"]
    res = aug_report(list(rep.get("apis") or []), row, seed, epoch, pool)
    if res is None:
        return int(row), None, 0, 0
    mode, k, apis = res
    r = dict(rep); r["apis"] = apis
    t = np.asarray(nb.ids(r)[:4096], dtype=np.uint16)
    return int(row), t, k, 0 if mode == "insert" else 1


def rng_range(s):
    a, b = (s.split("-") + [s])[:2]
    return list(range(int(a), int(b) + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="0-4")
    ap.add_argument("--epochs", default="1-2")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--balanced", action="store_true", help="edit benign training reports as often as malware ones (files augb_*), so padding carries no label")
    ap.add_argument("--rows-csv", required=True, help="rows.csv of the tokens dataset (row, label, side)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows = pd.read_csv(a.rows_csv)
    sel = rows.side.isin(["train", "val"]).values & ((rows.label.values == 1) | a.balanced)
    mal = rows.row.values[sel]
    pre = "augbw"
    assert a.balanced, "G3 uses balanced padding"
    if a.limit:
        mal = mal[:a.limit]
    _, train_pool = V.pools()
    stats = {}
    with Pool(a.workers, initializer=_init_train, initargs=(V.NEBULA, train_pool)) as pool:
        for s in rng_range(a.seeds):
            for e in rng_range(a.epochs):
                t0 = time.time()
                res = list(pool.imap(_work, [(r, s, e) for r in mal], chunksize=64))
                keep = [r for r in res if r[1] is not None]
                np.save(os.path.join(a.out, f"{pre}_s{s}_e{e}_rows.npy"), np.array([r[0] for r in keep], dtype=np.int64))
                toks = [r[1] for r in keep]
                np.save(os.path.join(a.out, f"{pre}_s{s}_e{e}_off.npy"), np.concatenate([[0], np.cumsum([len(t) for t in toks])]).astype(np.int64))
                np.save(os.path.join(a.out, f"{pre}_s{s}_e{e}_tok.npy"), np.concatenate(toks).astype(np.uint16))
                ks = np.array([r[2] for r in keep]); md = np.array([r[3] for r in keep])
                stats[f"s{s}_e{e}"] = {"malware": int(len(mal)), "edited": int(len(keep)), "mean_k": float(ks.mean()), "share_prepend": float(md.mean())}
                print(f"seed {s} epoch {e}: {len(keep):,} of {len(mal):,} reports edited, mean k {ks.mean():.1f}, "
                      f"prepend {100 * md.mean():.0f}% ({time.time() - t0:.0f}s)", flush=True)
    json.dump(stats, open(os.path.join(a.out, f"{pre}_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
