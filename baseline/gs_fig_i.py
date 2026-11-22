"""
Stage I figure of NOTES 25: training and validation loss per epoch of the four final models with the corrected tokenizer (top row) next to the same four models with the current tokenizer (bottom row), 10 seeds, mean +- SD.   (OURS)

    python -m baseline.gs_fig_i --z-loss <dir with loss_curves/gsz_v2pe, gsz_attbal> --z-runs <zm2/ zm4/> --cur-gsy <dir with loss_curves/gsy_v2pe, gsy_attbal> --cur-g <gm2/ gm4/> --out <dir>

All eight models are trained on ALL of January, so the "validation" loss is IN-SAMPLE for every curve; one-epoch models show a single point. The curves of the current tokenizer are the loss-log reruns of Stage G.
"""
import argparse
import glob
import json
import os

import numpy as np


def curves(files):
    recs = [json.load(open(f))["per_epoch"] for f in files]
    ne = len(recs[0])
    tr = np.array([[e["train_epoch_mean_loss"] for e in r] for r in recs])
    va = np.array([[e["val_loss"] for e in r] for r in recs])
    return np.arange(1, ne + 1), tr, va


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--z-loss", required=True)
    ap.add_argument("--z-runs", required=True)
    ap.add_argument("--cur-gsy", required=True)
    ap.add_argument("--cur-g", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    g = lambda *p: sorted(glob.glob(os.path.join(*p, "seed*.json")))
    new = {"M1 v2-PE": g(a.z_loss, "loss_curves", "gsz_v2pe"), "M2 two-level, no padding": g(a.z_runs, "zm2"), "M3 ATT+bal": g(a.z_loss, "loss_curves", "gsz_attbal"), "M4 ATT+bal-2L": g(a.z_runs, "zm4")}
    cur = {"M1 v2-PE": g(a.cur_gsy, "loss_curves", "gsy_v2pe"), "M2 two-level, no padding": g(a.cur_g, "gm2"), "M3 ATT+bal": g(a.cur_gsy, "loss_curves", "gsy_attbal"), "M4 ATT+bal-2L": g(a.cur_g, "gm4")}
    fig, ax = plt.subplots(2, 4, figsize=(15, 6.4), dpi=200)
    for j, name in enumerate(new):
        for i, (src, lab) in enumerate(((new, "corrected tokenizer bpe50k_fix (all January; validation loss IN-SAMPLE)"), (cur, "current tokenizer (all January; validation loss IN-SAMPLE)"))):
            files = src[name]
            assert files, (name, i)
            ep, tr, va = curves(files)
            for arr, col, l in ((tr, "#1baf7a", "training loss"), (va, "#eb6834", "validation-slice loss")):
                m, sd = arr.mean(0), arr.std(0, ddof=1) if len(arr) > 1 else np.zeros(arr.shape[1])
                ax[i, j].plot(ep, m, "-o", ms=3, color=col, label=l)
                ax[i, j].fill_between(ep, m - sd, m + sd, color=col, alpha=0.18, lw=0)
            ax[i, j].set_xticks(ep)
            ax[i, j].set_xlabel("epoch")
            ax[i, j].set_title(name, fontsize=9)
            ax[i, j].text(0.02, 0.97, lab, transform=ax[i, j].transAxes, fontsize=6, va="top")
            ax[i, j].spines[["top", "right"]].set_visible(False)
            if j == 0:
                ax[i, j].set_ylabel("binary cross-entropy")
                ax[i, j].legend(fontsize=6.5, frameon=False, loc="center right")
    fig.tight_layout()
    os.makedirs(a.out, exist_ok=True)
    fig.savefig(os.path.join(a.out, "fig_loss_curves_fixed_vs_current.png"))


if __name__ == "__main__":
    main()
