#!/usr/bin/env python
"""
Round 4, step 1: the two disjoint padding pools, fixed before any training.

    python scripts/pooling_v4/make_pools.py

Population: benign January reports (meta.split == "trainset", label 0) with at least one API call.
The reports are split by hash_apis group (a group never straddles the two pools):
  EVAL pool  : exactly 2,000 reports, used ONLY for testing (benign-call padding of April malware)
  TRAIN pool : every other report, used ONLY for training augmentation
Groups are shuffled with numpy Generator(seed 4000); a group goes into EVAL only if it still fits (groups that would exceed 2,000 are skipped, so EVAL is
made of many groups and no group is cut); every other group is TRAIN.
Writes results/pooling_v4/pools.json (row numbers = rows of meta.csv / reps.bin) and pools.md.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "go_no_go"))
import common as C  # noqa: E402

N_EVAL = 2000


def main():
    meta = C.meta_full()
    reps = C.Reps()
    ben = meta[(meta.split == "trainset") & (meta.label == 0)].copy()
    ncalls = np.array([len(reps.get(int(r)).get("apis") or []) for r in ben.row.values])
    print(f"benign January reports: {len(ben):,}; with >=1 call: {(ncalls > 0).sum():,}")
    ben = ben[ncalls > 0].copy()
    ben["ncalls"] = ncalls[ncalls > 0]
    groups = ben.groupby("hash_apis").row.apply(list)
    rng = np.random.default_rng(4000)
    order = rng.permutation(len(groups))
    eval_rows, dropped = [], []
    for g in order:                                   # random group order; a group joins EVAL only if it fits in the 2,000
        rows = groups.iloc[g]
        if len(eval_rows) + len(rows) <= N_EVAL:
            eval_rows += rows
        if len(eval_rows) == N_EVAL:
            break
    eval_groups = set(ben.set_index("row").loc[eval_rows].hash_apis)
    es = set(eval_rows); ds = set(dropped)
    train_rows = [r for r in ben.row.values if r not in es and r not in ds
                  and ben.set_index("row").at[r, "hash_apis"] not in eval_groups]
    b = ben.set_index("row")
    assert not (set(b.loc[eval_rows].hash_apis) & set(b.loc[train_rows].hash_apis))
    assert not es & set(train_rows)
    out = {"eval_rows": sorted(int(r) for r in eval_rows), "train_rows": sorted(int(r) for r in train_rows),
           "dropped_rows": sorted(int(r) for r in dropped), "seed": 4000, "n_eval": N_EVAL}
    json.dump(out, open("results/pooling_v4/pools.json", "w"))
    st = lambda rows: (len(rows), b.loc[rows].hash_apis.nunique(), float(b.loc[rows].ncalls.median()), float(b.loc[rows].ncalls.mean()),
                       int(b.loc[rows].ncalls.max()))
    md = ["# Padding pools (round 4, step 1)\n",
          "Benign January reports with at least one API call, split by `hash_apis` group (disjoint groups), numpy Generator seed 4000. "
          "Row numbers are in `pools.json`.\n",
          "| pool | reports | distinct sequences (hash_apis) | median calls | mean calls | max calls | used for |", "|---|---|---|---|---|---|---|"]
    for name, rows, use in (("EVAL", eval_rows, "testing only (padding of April malware)"), ("TRAIN", train_rows, "training augmentation only")):
        n, g, med, mean, mx = st(rows)
        md.append(f"| {name} | {n:,} | {g:,} | {med:.0f} | {mean:.1f} | {mx:,} | {use} |")
    md.append(f"\nBenign January reports without any call (in neither pool): {len(ncalls) - (ncalls > 0).sum():,}.")
    open("results/pooling_v4/pools.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
