"""
Tables and plots of the gap follow-up (Step 1 and Step 2).   (OURS)

    python -m baseline.gap_report --gap results/F_gap --plots results/baseline/plots [--v2 results/F_gap/v2]

  gap_logit_hist.png   logit distributions of the released model and of ours (April test; benign and malware)
  gap_val_curves.png   validation TPR@1e-3 / TPR@1e-2 / AUC per epoch for every recipe (mean +- std over the seeds); the chosen epoch is marked
  gap_roc.png          mean ROC on the April test set: released vs current recipe vs baseline v2
Selection (select_epoch) uses ONLY the validation curves; test numbers appear in the appendix tables, marked "not used for selection".
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6", "#898782"]


def jl(p):
    return json.load(open(p))


def load_recipes(gap_dir):
    """{recipe: [per-seed result dicts]} from <gap_dir>/gap/<recipe>/seed*.json"""
    out = {}
    for d in sorted(glob.glob(os.path.join(gap_dir, "gap", "*"))):
        fs = sorted(glob.glob(os.path.join(d, "seed*.json")))
        if fs:
            out[os.path.basename(d)] = [jl(f) for f in fs]
    return out


def curve(runs, key, split="val"):
    """array [seeds, epochs] of a metric"""
    return np.array([[e[split][key] for e in r["per_epoch"]] for r in runs])


def select_epoch(runs, key="tpr@0.001", tie_key="tpr@0.01"):
    """Epoch (1-based) with the highest mean validation `key` over the seeds; among epochs within one standard error of the best, the one with the
    best mean validation `tie_key`, and among those the earliest. Validation only."""
    v = curve(runs, key)
    m, se = v.mean(0), v.std(0, ddof=1) / np.sqrt(len(v)) if len(v) > 1 else np.zeros(v.shape[1])
    best = int(m.argmax())
    cand = [e for e in range(v.shape[1]) if m[e] >= m[best] - se[best]]
    t = curve(runs, tie_key).mean(0)
    pick = max(cand, key=lambda e: (round(t[e], 6), -e))
    return pick + 1


def early_stop_epoch(runs, patience=2):
    """Early stopping on the validation loss (patience epochs, per seed); returns the per-seed stopping epochs (1-based, the epoch of the lowest loss before stopping)."""
    out = []
    for r in runs:
        loss = [e["val_loss"] for e in r["per_epoch"]]
        best, bad, best_ep = float("inf"), 0, 1
        for i, l in enumerate(loss):
            if l < best - 1e-6:
                best, bad, best_ep = l, 0, i + 1
            else:
                bad += 1
                if bad >= patience:
                    break
        out.append(best_ep)
    return out


def plot_logit_hist(gap_dir, plots_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    z = np.load(os.path.join(gap_dir, "calib_arrays.npz"))
    y, zr, zo = z["y_test"], z["released_test"], z["ours_test"]
    extra = {}
    for name, p in (("baseline v2 (5 seeds)", os.path.join(gap_dir, "v2_test_logits.npy")),):
        if os.path.exists(p):
            extra[name] = np.load(p)
    bins = np.linspace(-40, 100, 141)
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2), sharey=True)
    for ax, (lab, title) in zip(axes, ((0, "benign April reports"), (1, "malware April reports"))):
        sel = y == lab
        ax.hist(zr[sel], bins=bins, density=True, histtype="step", lw=2, color=COLORS[1], label="released checkpoint")
        ax.hist(zo[:, sel].ravel(), bins=bins, density=True, histtype="step", lw=2, color=COLORS[0], label="ours, current recipe (9 fold models)")
        for i, (n, a) in enumerate(extra.items()):
            ax.hist(a[:, sel].ravel(), bins=bins, density=True, histtype="step", lw=2, color=COLORS[2 + i], label=n)
        ax.axvline(16.64, color="#555", lw=1, ls=":")
        ax.text(17.5, ax.get_ylim()[1] * 0.5 if False else 0.0006, "float32 sigmoid = 1.0", rotation=90, fontsize=7.5, color="#555", va="bottom")
        ax.set_yscale("log"); ax.set_ylim(1e-5, 0.3)
        ax.set_xlabel("logit"); ax.set_title(title, loc="left", fontsize=10.5)
        ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    axes[0].set_ylabel("density (log scale)")
    axes[0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout(); os.makedirs(plots_dir, exist_ok=True)
    fig.savefig(os.path.join(plots_dir, "gap_logit_hist.png"), dpi=160); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", default="results/F_gap")
    ap.add_argument("--plots", default="results/baseline/plots")
    a = ap.parse_args()
    plot_logit_hist(a.gap, a.plots)
    print("wrote", os.path.join(a.plots, "gap_logit_hist.png"))


if __name__ == "__main__":
    main()
