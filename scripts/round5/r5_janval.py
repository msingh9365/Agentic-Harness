#!/usr/bin/env python
"""
Round 5, item 2 (second test set): TPR at 0.1% and 1% FPR on the January validation side for the regime S models of G2.

    python scripts/round5/r5_janval.py [--epoch 2]

Regime S = trained on the train side of January only (no validation reports, no augmentation row of the validation side), 2 epochs, seeds 0-9: ATT+bal, MM+bal,
C+bal and, as references, ATT (no padding) and A. The validation side is group-disjoint from the train side (results/pooling_v2); it is a second test set for
low-FPR numbers. Thresholds: 1% / 0.1% FPR of the benign scores of the same set (type (a)), per model and seed. Group bootstrap over hash_apis of the validation
side (1,000 resamples); seed-paired differences; ensembles = mean logit over the seeds. Also the April results of the same S models (April is a third, later test set).
Writes results/round5/janval.md/json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import r5_common as R  # noqa: E402
from r5_common import C, V  # noqa: E402
from r5_accuracy import pauc_weighted, sigmoid  # noqa: E402

ROWS_CSV = "/Users/manish/Code/mtp/pooling_v5_stage/tokens/rows.csv"
S_MODELS = {"ATT+bal (S)": "ATTbal", "MM+bal (S)": "MMbal", "C+bal (S)": "Cbal", "ATT (S, no padding)": "ATT", "A (S)": "A"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epoch", type=int, default=2)
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    ap.add_argument("--root", default=R.G2)
    a = ap.parse_args()
    rows = pd.read_csv(ROWS_CSV)
    val = rows[rows.side == "val"].reset_index(drop=True)
    test = rows[rows.side == "test"].reset_index(drop=True)
    yv, yt = val.label.values, test.label.values
    never = {f: np.inf for f, _ in C.FPRS}
    data = {}
    for disp, key in S_MODELS.items():
        d = {}
        for s in range(10):
            p = os.path.join(a.root, "scores", f"{key}_S_s{s}_epochs.npz")
            if os.path.exists(p):
                z = np.load(p)
                d[s] = (z["janval"][a.epoch - 1], z["april"][a.epoch - 1])
        if d:
            data[disp] = d
    print({k: len(v) for k, v in data.items()}, flush=True)
    out = {}
    md = ["# Second test set: January validation side, regime S models (round 5, item 2)\n",
          f"Validation side: {len(val):,} reports ({int((yv == 1).sum()):,} malware, {int((yv == 0).sum()):,} benign; {val.hash_apis.nunique():,} distinct API sequences = groups). "
          f"The 0.1% FPR threshold lets floor(0.001 x {int((yv == 0).sum()):,}) = {int(np.floor(0.001 * (yv == 0).sum()))} benign reports lie above it, the 1% threshold "
          f"{int(np.floor(0.01 * (yv == 0).sum()))}. Models trained on the train side of January only, {a.epoch} epochs, seeds listed in the table; thresholds from the benign scores of "
          "the same set. Group-bootstrap 95% intervals (1,000 resamples over API-sequence groups); the ensemble is the mean logit of the seeds.\n"]
    for part, (y_, df_, idx) in {"janval": (yv, val, 0), "april": (yt, test, 1)}.items():
        models, thr_b = {}, {}
        for disp, d in data.items():
            models[disp] = {s: sigmoid(v[idx]) for s, v in d.items()}
            zs = np.mean([v[idx] for v in d.values()], 0)
            models[disp + " (ensemble)"] = {0: sigmoid(zs)}
        thr_b = {m: {s: never for s in d} for m, d in models.items()}
        t = df_.copy(); t["label"] = y_
        masks = [("all", np.ones(len(t), bool))]
        diffs = [(x, z) for x in ("ATT+bal (S)", "MM+bal (S)", "C+bal (S)") for z in ("A (S)", "ATT (S, no padding)", "C+bal (S)", "ATT+bal (S)") if x in models and z in models and x != z and
                 not (z == "ATT+bal (S)" and x != "C+bal (S)" and False)]
        diffs += [(x + " (ensemble)", z + " (ensemble)") for x, z in diffs if x + " (ensemble)" in models and z + " (ensemble)" in models]
        point, cis, dci, masks = C.evaluate_models(t, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)
        rows_t = []
        for m in models:
            r = {"model": m, "seeds": len(point[m]["_seeds"])}
            for k in ("auc", "tpr1%_a", "tpr0.1%_a"):
                lo, hi = cis[(m, "all", k)]
                r[C.HEAD[k]] = f"{C.fmt(k, point[m]['all'][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
            W = np.stack(list(C.group_weights_boot(t.hash_apis.values, 300, 0)))
            sc = [d for d in models[m].values()]
            pt = np.mean([pauc_weighted(y_, z, np.ones(len(y_))) for z in sc])
            bs = np.array([np.mean([pauc_weighted(y_, z, w) for z in sc]) for w in W])
            r["standardised pAUC to 1% FPR"] = f"{pt:.4f} [{np.percentile(bs, 2.5):.4f}, {np.percentile(bs, 97.5):.4f}]"
            rows_t.append(r)
        drows = []
        for x, z in diffs:
            r = {"difference": f"{x} − {z}"}
            for k in ("auc", "tpr1%_a", "tpr0.1%_a"):
                lo, hi = dci[(x, z, "all", k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x]['all'][k] - point[z]['all'][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            drows.append(r)
        sp = []
        for m in data:
            for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1%"), ("tpr0.1%_a", "TPR@0.1%")):
                v = np.array([p["all"][k] for p in point[m]["_seeds"]])
                sp.append({"model": m, "metric": tag, "mean": f"{v.mean():.4f}" if k == "auc" else f"{100 * v.mean():.1f}%",
                           "sd": f"{v.std(ddof=1):.4f}" if k == "auc" else f"{100 * v.std(ddof=1):.1f}", "per seed": " / ".join((f"{x:.4f}" if k == "auc" else f"{100 * x:.1f}") for x in v)})
        title = "January validation side" if part == "janval" else "April test set (the same S models)"
        md += [f"\n## {title}\n", C.md_table(pd.DataFrame(rows_t)), f"\nPaired differences ({title})\n", C.md_table(pd.DataFrame(drows)),
               f"\nSeed spread ({title})\n", C.md_table(pd.DataFrame(sp))]
        out[part] = {"point": {m: {k: float(v) for k, v in point[m]["all"].items()} for m in models}, "n": int(len(y_)), "n_benign": int((y_ == 0).sum())}
    open(f"{R.OUT}/janval.md", "w").write("\n".join(md))
    json.dump(out, open(f"{R.OUT}/janval.json", "w"), indent=1)
    print("\n".join(md[:12]))


if __name__ == "__main__":
    main()
