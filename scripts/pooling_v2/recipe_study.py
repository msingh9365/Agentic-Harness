#!/usr/bin/env python
"""
Recipe study for the retrained flatten model A (results/pooling_v2/recipe_study.md).

    python scripts/pooling_v2/recipe_study.py --src <Kaggle output folder> [--runs A,A_steps3000,A_all]

Goal set for the study: A reaches April AUC >= 0.95. Options, in this order (one change at a time):
  1. base         : 10 epochs, a checkpoint and the scores after every epoch, epoch selected on January-validation
                    AUC (primary) or on validation TPR at 1% FPR (secondary)
  2. fixed 6      : the epoch-6 weights of the base runs (same schedule, so identical to stopping at 6 epochs)
  3. step budget  : 3000 optimiser steps (the only step budget written in Nebula's cross-validation script)
  4. all January  : train on January train + validation for the epoch count chosen on the split in option 1
April numbers decide whether the goal is reached, but the epoch of options 1 is chosen on validation only.
Writes results/pooling_v2/recipe_study.md and recipe_study.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "go_no_go"))
import common as C  # noqa: E402

OUT = "results/pooling_v2"
GOAL = 0.95


def tpr_a(y, s, fpr=0.01):
    t = C.thr_from(y, s, fpr)
    return float(((s > t) & (y == 1)).sum() / max(1, (y == 1).sum()))


def tpr_val(y, s, fpr=0.01):
    return tpr_a(y, s, fpr)


def load_run(src, run):
    p = os.path.join(src, "scores", f"{run}_epochs.npz")
    if not os.path.exists(p):
        return None
    d = np.load(p)
    return d["april"], d["janval"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--runs", default="A,A_steps3000", help="run-name prefixes (before _s<seed>)")
    ap.add_argument("--seeds", default="0,1,2")
    a = ap.parse_args()
    meta = C.meta_full()
    ya = meta[meta.split == "testset"].label.values
    yv = meta[meta.side == "val"].label.values
    seeds = [int(s) for s in a.seeds.split(",")]
    res = {}
    lines = []
    for pref in a.runs.split(","):
        per_seed = []
        for s in seeds:
            r = load_run(a.src, f"{pref}_s{s}")
            if r is None:
                continue
            za, zv = r
            E = len(za)
            va = np.array([roc_auc_score(yv, zv[e]) for e in range(E)])
            vt = np.array([tpr_val(yv, zv[e]) for e in range(E)])
            aa = np.array([roc_auc_score(ya, za[e]) for e in range(E)])
            at = np.array([tpr_a(ya, za[e]) for e in range(E)])
            e_auc, e_tpr = int(np.argmax(va)), int(np.argmax(vt))
            per_seed.append({"seed": s, "epochs": E, "val_auc": va.tolist(), "val_tpr1": vt.tolist(),
                             "april_auc": aa.tolist(), "april_tpr1": at.tolist(),
                             "epoch_by_val_auc": e_auc + 1, "epoch_by_val_tpr1": e_tpr + 1})
        res[pref] = per_seed
    json.dump(res, open(f"{OUT}/recipe_study.json", "w"), indent=1)

    def row(name, f):
        v = [f(p) for p in res[name]]
        return v

    md = ["# Recipe study: can the retrained flatten model A reach April AUC 0.95?\n",
          f"Goal: mean April AUC >= {GOAL} over seeds. Released Nebula: AUC 0.9586 on the same April set. "
          "Epoch selection uses the January-validation side only; April numbers are reported, not used to pick an epoch.\n"]
    summary = []
    for pref, ps in res.items():
        if not ps:
            continue
        md.append(f"\n## {pref}\n")
        md.append("| seed | epochs | epoch by val AUC | April AUC | April TPR@1% (a) | epoch by val TPR@1% | April AUC | April TPR@1% (a) |")
        md.append("|---|---|---|---|---|---|---|---|")
        for p in ps:
            ea, et = p["epoch_by_val_auc"] - 1, p["epoch_by_val_tpr1"] - 1
            md.append(f"| {p['seed']} | {p['epochs']} | {ea + 1} | {p['april_auc'][ea]:.4f} | {100 * p['april_tpr1'][ea]:.1f}% | "
                      f"{et + 1} | {p['april_auc'][et]:.4f} | {100 * p['april_tpr1'][et]:.1f}% |")
        mA = np.mean([p["april_auc"][p["epoch_by_val_auc"] - 1] for p in ps])
        mT = np.mean([p["april_auc"][p["epoch_by_val_tpr1"] - 1] for p in ps])
        md.append(f"| **mean** | | | **{mA:.4f}** | {100 * np.mean([p['april_tpr1'][p['epoch_by_val_auc'] - 1] for p in ps]):.1f}% | "
                  f"| **{mT:.4f}** | {100 * np.mean([p['april_tpr1'][p['epoch_by_val_tpr1'] - 1] for p in ps]):.1f}% |")
        summary.append((f"{pref}: selected on validation AUC", mA, [p["april_auc"][p["epoch_by_val_auc"] - 1] for p in ps]))
        summary.append((f"{pref}: selected on validation TPR@1%", mT, [p["april_auc"][p["epoch_by_val_tpr1"] - 1] for p in ps]))
        E = min(p["epochs"] for p in ps)
        md.append("\nPer epoch, mean over seeds (validation = January grouped validation side):\n")
        md.append("| epoch | val AUC | val TPR@1% | April AUC | April TPR@1% (a) |")
        md.append("|---|---|---|---|---|")
        for e in range(E):
            md.append(f"| {e + 1} | {np.mean([p['val_auc'][e] for p in ps]):.4f} | {100 * np.mean([p['val_tpr1'][e] for p in ps]):.1f}% | "
                      f"{np.mean([p['april_auc'][e] for p in ps]):.4f} | {100 * np.mean([p['april_tpr1'][e] for p in ps]):.1f}% |")
        if E >= 6:
            summary.append((f"{pref}: fixed 6 epochs", float(np.mean([p["april_auc"][5] for p in ps])), [p["april_auc"][5] for p in ps]))
        summary.append((f"{pref}: end of run ({E} epochs or the step budget)", float(np.mean([p["april_auc"][E - 1] for p in ps])),
                        [p["april_auc"][E - 1] for p in ps]))
    md.append("\n## Summary: mean April AUC (per seed in brackets)\n")
    md.append("| option | mean April AUC | seeds | reaches 0.95 |")
    md.append("|---|---|---|---|")
    for name, m, v in summary:
        md.append(f"| {name} | {m:.4f} | {' / '.join(f'{x:.4f}' for x in v)} | {'yes' if m >= GOAL else 'no'} |")
    open(f"{OUT}/recipe_study.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md[-(len(summary) + 6):]))


if __name__ == "__main__":
    main()
