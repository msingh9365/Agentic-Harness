"""
Stage G figure of NOTES 23: training and validation loss per epoch of the four final models M1 to M4 (10 seeds, mean ± SD).   (OURS)

    python -m baseline.gs_fig_g --gsy <runs with loss_curves/gsy_v2pe, gsy_attbal> --g-runs <gm2/ gm4/> --stage-c <gsf runs with loss_curves> --f-runs <Stage F outputs> --selection <selection.json> --out <dir>

Top row: the final models (trained on ALL of January: the validation slice is part of their training data, so their "validation" loss is IN-SAMPLE). Bottom row: counterparts trained on the group-split
training part, whose validation loss is held out: M1 and M3 from Stage C (new tokenizer, loss curves of the runs of NOTES 21.12), M2 and M4 the chosen Stage F cells (old tokenizer, seeds 0-4).
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
    ap.add_argument("--gsy", required=True)
    ap.add_argument("--g-runs", required=True)
    ap.add_argument("--stage-c", required=True)
    ap.add_argument("--f-runs", required=True)
    ap.add_argument("--selection", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sel = json.load(open(a.selection))
    top = {"M1 v2-PE": glob.glob(os.path.join(a.gsy, "loss_curves", "gsy_v2pe", "seed*.json")), "M2 two-level, no padding": glob.glob(os.path.join(a.g_runs, "gm2", "seed*.json")),
           "M3 ATT+bal": glob.glob(os.path.join(a.gsy, "loss_curves", "gsy_attbal", "seed*.json")), "M4 ATT+bal-2L": glob.glob(os.path.join(a.g_runs, "gm4", "seed*.json"))}
    bot = {"M1 v2-PE": glob.glob(os.path.join(a.stage_c, "loss_curves", "gsf_v2pe", "seed*.json")), "M2 two-level, no padding": glob.glob(os.path.join(a.f_runs, sel["m2"]["chosen"]["cell"], "seed*.json")),
           "M3 ATT+bal": glob.glob(os.path.join(a.stage_c, "loss_curves", "gsf_attbal", "seed*.json")), "M4 ATT+bal-2L": glob.glob(os.path.join(a.f_runs, sel["m4"]["chosen"]["cell"], "seed*.json"))}
    held = {"M1 v2-PE": "Stage C, new tokenizer", "M2 two-level, no padding": f"Stage F {sel['m2']['chosen']['cell']}", "M3 ATT+bal": "Stage C, new tokenizer", "M4 ATT+bal-2L": f"Stage F {sel['m4']['chosen']['cell']}"}
    fig, ax = plt.subplots(2, 4, figsize=(15, 6.4), dpi=200)
    for j, name in enumerate(top):
        for i, (src, lab) in enumerate(((top, "final model, trained on ALL January: validation loss is IN-SAMPLE"), (bot, f"group-split training part ({held[name]}): validation loss HELD OUT"))):
            files = src[name]
            assert files, (name, i)
            ep, tr, va = curves(files)
            for arr, col, l in ((tr, "#1baf7a", "training loss"), (va, "#eb6834", "validation-slice loss")):
                m, sd = arr.mean(0), arr.std(0, ddof=1) if len(arr) > 1 else np.zeros(arr.shape[1])
                ax[i, j].plot(ep, m, "-o", ms=3, color=col, label=l)
                ax[i, j].fill_between(ep, m - sd, m + sd, color=col, alpha=0.18, lw=0)
            ax[i, j].set_xticks(ep)
            ax[i, j].set_xlabel("epoch")
            ax[i, j].set_title(f"{name}\\n{lab}" if False else name, fontsize=9)
            ax[i, j].text(0.02, 0.97, lab, transform=ax[i, j].transAxes, fontsize=6, va="top")
            ax[i, j].spines[["top", "right"]].set_visible(False)
            if j == 0:
                ax[i, j].set_ylabel("binary cross-entropy")
                ax[i, j].legend(fontsize=6.5, frameon=False, loc="center right")
    fig.tight_layout()
    os.makedirs(a.out, exist_ok=True)
    fig.savefig(os.path.join(a.out, "fig_loss_curves_four_final_models.png"))


if __name__ == "__main__":
    main()
