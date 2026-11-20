"""
Appendix of round 2 (NOTES 20): April pAUC@1e-2 of ALL 36 candidates (6 cells x epoch 1-3 x raw/EMA), 10 seeds, next to the validation number the selection used.   (OURS)
NOT used for any choice (the choice was committed in NOTES 20.1 before any April logit was opened).

    python -m baseline.twolevel_appendix --runs <folders with <cell>/seed<k>_epoch<e>_test_logits[_ema].npy> --select results/attbal_2l/round2 --out results/attbal_2l/round2/appendix_april.md
"""
import argparse
import json
import os

import numpy as np

from baseline.v2pe_report import md, metrics_of
from baseline import common as C

SEEDS = list(range(10))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--select", required=True, help="folder with the selection output of twolevel_select2 (selection.json)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    sel = json.load(open(os.path.join(a.select, "selection.json")))
    val = {(c["cell"], c["epoch"], c["weights"]): c for c in sel["candidates"]}
    rows, out = [], {}
    for run in a.runs:
        for cell in sorted(os.listdir(run)):
            d = os.path.join(run, cell)
            if not os.path.isdir(d) or cell == "logs":
                continue
            for e in (1, 2, 3):
                for w, suf in (("raw", ""), ("ema", "_ema")):
                    z = np.stack([np.load(os.path.join(d, f"seed{s}_epoch{e}_test_logits{suf}.npy")).astype(np.float64) for s in SEEDS])
                    m = metrics_of(y, z)["pauc@0.01"]
                    v = val[(cell, e, w)]
                    out[f"{cell}|{e}|{w}"] = {"april_pauc": m.tolist(), "val_pauc": v["mean"]}
                    rows.append([cell, e, w, f"{v['mean']:.4f}", f"{m.mean():.3f} ± {m.std(ddof=1):.3f}", "**chosen**" if (cell, e, w) == (sel["chosen"]["cell"], sel["chosen"]["epoch"], sel["chosen"]["weights"]) else ""])
    text = ["### Round 2, all 36 candidates: validation (used for the selection) and April (NOT used for any choice)", "",
            md(rows, ["cell", "epoch", "weights", "mean val pAUC@1e-2", "April pAUC@1e-2 (mean ± std, 10 seeds)", ""])]
    open(a.out, "w").write("\n".join(text) + "\n")
    json.dump(out, open(os.path.splitext(a.out)[0] + ".json", "w"))
    print("\n".join(text))


if __name__ == "__main__":
    main()
