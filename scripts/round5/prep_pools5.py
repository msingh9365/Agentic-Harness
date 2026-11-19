#!/usr/bin/env python
"""
Round 5, item 3b: the pools of calls for the padding the models have never seen.

    python scripts/round5/prep_pools5.py

From results/pooling_v4/pools.json (EVAL pool = test only, TRAIN pool = training augmentation only):
  * EVAL reports by benign source (meta.family: clean / windows_syswow64);
  * the rarest 20% of API names of the TRAIN pool: all distinct API names seen in the TRAIN-pool calls (or in the EVAL calls, count 0),
    sorted by number of calls in the TRAIN pool (ascending, ties by name); the first 20% of the names;
  * the EVAL-pool calls whose API name is in that set.
Writes results/round5/pools5.json (row numbers and counts; no reports).
"""
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
sys.path.insert(0, os.path.join(HERE, "..", "pooling_v2"))
import common as C  # noqa: E402
from perturb_check import _init, _W  # noqa: E402

OUT = "results/round5"


def main():
    _init("../nebula")
    p = json.load(open("results/pooling_v4/pools.json"))
    ev, tr = p["eval_rows"], p["train_rows"]
    fam = C.meta_full().set_index("row").family
    calls = lambda r: _W["reps"].get(int(r)).get("apis") or []
    cnt = Counter()
    for r in tr:
        cnt.update(c["api_name"] for c in calls(r))
    ev_names = Counter()
    for r in ev:
        ev_names.update(c["api_name"] for c in calls(r))
    names = sorted(set(cnt) | set(ev_names), key=lambda n: (cnt.get(n, 0), n))
    n_rare = int(np.ceil(0.2 * len(names)))
    rare = names[:n_rare]
    rare_set = set(rare)
    ev_syswow = [int(r) for r in ev if fam.loc[int(r)] == "windows_syswow64"]
    ev_clean = [int(r) for r in ev if fam.loc[int(r)] == "clean"]
    rare_calls = sum(1 for r in ev for c in calls(r) if c["api_name"] in rare_set)
    tot_calls = sum(len(calls(r)) for r in ev)
    res = {"n_distinct_names": len(names), "n_rare_names": n_rare, "rare_names": rare,
           "rare_count_threshold": int(cnt.get(rare[-1], 0)), "eval_syswow64_rows": ev_syswow, "eval_clean_rows": ev_clean,
           "n_eval_calls": int(tot_calls), "n_eval_calls_rare": int(rare_calls),
           "n_eval_calls_syswow64": int(sum(len(calls(r)) for r in ev_syswow)), "n_eval_calls_clean": int(sum(len(calls(r)) for r in ev_clean)),
           "train_calls": int(sum(cnt.values())), "train_calls_in_rare_names": int(sum(cnt.get(n, 0) for n in rare))}
    json.dump(res, open(f"{OUT}/pools5.json", "w"), indent=1)
    print({k: v for k, v in res.items() if k not in ("rare_names", "eval_syswow64_rows", "eval_clean_rows")})
    print("syswow64 EVAL rows:", ev_syswow)


if __name__ == "__main__":
    main()
