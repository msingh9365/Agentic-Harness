"""
Loss curves of the chosen models (NOTES 19.12, 20): A, B (stage 2), A2, B2 (round 2). Writes results/attbal_2l/loss_curves/{fig_loss_curves.png, curves.md}.   (OURS)
Left: training loss (mean BCE of 10 batches, dropout on, on the padded mix for A/A2) against the training step, mean over 10 seeds (thin lines = seeds).
Right: validation loss at the end of each epoch (clean validation slice; mean ± std over seeds). Scores and losses only.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
R = os.path.join(ROOT, "results", "attbal_2l")
MODELS = [("A (stage 2: warm, lr 1e-3, constant)", os.path.join(R, "stage2", "A_warm_lr1e-3"), "#1baf7a", "-"),
          ("B (stage 2: no padding, lr 2e-3, constant)", os.path.join(R, "stage2", "B_lr2e-3"), "#6250d6", "-"),
          ("A2 (round 2: level 1 frozen in epoch 1, lr decay)", os.path.join(R, "round2", "runs", "R5_dec_freeze1ep"), "#0b6b4a", "--"),
          ("B2 (round 2: no padding, lr decay)", os.path.join(R, "round2", "runs", "B2_dec_scratch"), "#8a7be0", "--")]


def load(d):
    return [json.load(open(os.path.join(d, f"seed{s}.json"))) for s in range(10)]


def main():
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.4), dpi=200)
    rows = []
    for name, d, col, ls in MODELS:
        runs = load(d)
        step = np.array(runs[0]["train_loss_step"])
        tl = np.array([r["train_loss_mean_last_10"] for r in runs])
        for t in tl:
            ax[0].plot(step, t, color=col, lw=0.4, alpha=0.18)
        ax[0].plot(step, tl.mean(0), color=col, lw=1.8, ls=ls, label=name)
        ep = np.array([[e["epoch"] for e in r["per_epoch"]] for r in runs])[0]
        vl = np.array([[e["val_loss"] for e in r["per_epoch"]] for r in runs])
        ax[1].errorbar(ep + (0.04 * MODELS.index((name, d, col, ls)) - 0.06), vl.mean(0), yerr=vl.std(0, ddof=1), color=col, ls=ls, marker="o", ms=5, capsize=3, lw=1.6, label=name)
        rows.append([name] + [f"{vl[:, i].mean():.4f} ± {vl[:, i].std(ddof=1):.4f}" for i in range(len(ep))] + [f"{tl[:, -1].mean():.4f}"])
    ax[0].set_yscale("log")
    ax[0].set_ylim(0.01, 0.4)
    ax[0].set_xlabel("training step (706 per epoch)")
    ax[0].set_ylabel("training loss (BCE)")
    ax[0].set_title("Training loss (dropout on)")
    ax[1].set_xlabel("epoch")
    ax[1].set_xticks([1, 2, 3])
    ax[1].set_ylabel("validation loss (BCE)")
    ax[1].set_title("Validation loss at the end of each epoch")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
        a.grid(alpha=0.25)
    ax[1].legend(fontsize=7.5, frameon=False)
    fig.tight_layout()
    out = os.path.join(R, "loss_curves")
    os.makedirs(out, exist_ok=True)
    fig.savefig(os.path.join(out, "fig_loss_curves.png"))
    md = ["| model | val loss epoch 1 | epoch 2 | epoch 3 | last training loss |", "|---|---|---|---|---|"] + ["| " + " | ".join(r) + " |" for r in rows]
    open(os.path.join(out, "curves.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
