#!/usr/bin/env python
"""
Round 4, step 3 (accuracy): the new poolings against C (J), A (J) and the released Nebula on April.

    python scripts/pooling_v4/evaluate_v4.py --src-v4 <Kaggle output of the round-4 runs>

Models (regime J: trained on all of January; no January threshold; (a) = thresholds from the April benign scores), seeds 0-4:
  M, MM, ATT, C+aug, ATT+aug   (round 4, 2 epochs)      C (J) (10 epochs), A (J) (1 epoch)  (results/pooling_v2, seeds 0-4)
  released Nebula; bag-of-API LightGBM (seeds 0-2 reused as seed mod 3); rank average of each model with the LightGBM of the same seed.
Subsets: all, seen, unseen, 1 / 2-3 / 4-8 chunks. Group bootstrap (April hash_apis, 1,000 resamples, paired across models).
Paired differences with C (J) and with the released Nebula. Writes results/pooling_v4/accuracy.md and accuracy.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
sys.path.insert(0, os.path.join(HERE, "..", "pooling"))
import common as C  # noqa: E402
from evaluate_pooling import pct_rank  # noqa: E402

OUT = "results/pooling_v4"
SEEDS = list(range(5))
NEW = {"M (max)": "M", "MM (mean+max)": "MM", "ATT (attention)": "ATT", "C+aug": "Caug", "ATT+aug": "ATTaug",
       "C+bal": "Cbal", "MM+bal": "MMbal", "ATT+bal": "ATTbal"}
J_DIR = "/Users/manish/Code/mtp/pooling_v2_all_output"


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-v4", default="/Users/manish/Code/mtp/pooling_v4_output")
    ap.add_argument("--epochs-new", type=int, default=2)
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    a = ap.parse_args()
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    models, thr_b = {}, {}
    never = {f: np.inf for f, _ in C.FPRS}

    def add(name, d):
        models[name] = d
        thr_b[name] = {s: never for s in d}
    load = lambda src, run, ep: sigmoid(np.load(os.path.join(src, "scores", f"{run}_epochs.npz"))["april"][ep - 1])
    for disp, fam in NEW.items():
        add(disp, {s: load(a.src_v4, f"{fam}_all_s{s}", a.epochs_new) for s in SEEDS})
    add("C (J)", {s: load(J_DIR, f"C_all_s{s}", 10) for s in SEEDS})
    add("C (J, 2 epochs)", {s: load(J_DIR, f"C_all_s{s}", 2) for s in SEEDS})        # control: C after its epoch 2 (same data order and LR schedule)
    add("A (J)", {s: load(J_DIR, f"A_all_s{s}", 1) for s in SEEDS})
    neb = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    lg = C.load_scores("lgbm_bag_full", "april")
    lgb = lambda s: lg[s % 3].loc[test.row.values].values
    add("released Nebula", {0: neb})
    add("LightGBM bag of API names", {s: lgb(s) for s in SEEDS})
    base = [*NEW, "C (J, 2 epochs)", "C (J)", "A (J)", "released Nebula"]
    for n in base:
        add(f"{n} + LightGBM", {s: (pct_rank(models[n][s] if s in models[n] else models[n][0]) + pct_rank(lgb(s))) / 2 for s in SEEDS})
    diffs = [(n, "C (J, 2 epochs)") for n in NEW] + [(n, "C (J)") for n in NEW] + [(n, "released Nebula") for n in [*NEW, "C (J, 2 epochs)", "C (J)", "A (J)"]] + \
            [("C (J, 2 epochs)", "C (J)")] + \
            [(f"{n} + LightGBM", "C (J, 2 epochs) + LightGBM") for n in NEW] + [(f"{n} + LightGBM", "released Nebula + LightGBM") for n in [*NEW, "C (J, 2 epochs)", "C (J)", "A (J)"]]
    masks = C.subsets(test)
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)
    names = [n for n, _ in masks]
    order = [*NEW, "C (J, 2 epochs)", "C (J)", "A (J)", "released Nebula", "LightGBM bag of API names"] + [f"{n} + LightGBM" for n in base]
    cols = ["auc", "tpr1%_a", "tpr0.1%_a"]
    rows = []
    for sub in ("all", "1 chunk", "2-3 chunks", "4-8 chunks", "seen", "unseen"):
        for m in order:
            r = {"subset": sub, "model": m, "n (malware)": f"{point[m][sub]['n']:,.0f} ({point[m][sub]['n_mal']:,.0f})"}
            for k in cols:
                lo, hi = ci[(m, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt(k, point[m][sub][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
            rows.append(r)
    t_main = pd.DataFrame(rows)
    drows = []
    for x, y in diffs:
        for sub in ("all", "1 chunk", "2-3 chunks", "4-8 chunks"):
            r = {"difference": f"{x} − {y}", "subset": sub}
            for k in cols:
                lo, hi = dci[(x, y, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x][sub][k] - point[y][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            drows.append(r)
    t_diff = pd.DataFrame(drows)
    sp = []
    for m in [*NEW, "C (J, 2 epochs)", "C (J)", "A (J)"]:
        for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1% (a)"), ("tpr0.1%_a", "TPR@0.1% (a)")):
            v = np.array([p["all"][k] for p in point[m]["_seeds"]])
            sp.append({"model": m, "metric": tag, "mean": f"{v.mean():.4f}" if k == "auc" else f"{100 * v.mean():.1f}%",
                       "sd": f"{v.std(ddof=1):.4f}" if k == "auc" else f"{100 * v.std(ddof=1):.1f}",
                       "per seed": " / ".join((f"{x:.4f}" if k == "auc" else f"{100 * x:.1f}") for x in v)})
    md = ["# Round 4 accuracy on April (regime J, seeds 0–4)\n",
          "Mean over 5 seeds [95% group-bootstrap interval]; (a) thresholds from the April benign scores. C (J) 10 epochs, A (J) 1 epoch (`results/pooling_v2`, seeds 0–4), "
          "new models 2 epochs.\n", "## Accuracy\n", C.md_table(t_main), "\n## Seed spread (all April reports)\n", C.md_table(pd.DataFrame(sp)),
          "\n## Paired differences (TPR in points)\n", C.md_table(t_diff)]
    open(f"{OUT}/accuracy.md", "w").write("\n".join(md))
    json.dump({"point": {m: {s: {k: float(v) for k, v in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point}},
              open(f"{OUT}/accuracy.json", "w"), indent=1)
    print(C.md_table(t_main[t_main["subset"] == "all"]))


if __name__ == "__main__":
    main()
