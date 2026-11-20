"""
Loss curves for the report (logging only; no reported result changes).   (OURS)

    python -m baseline.loss_curves --src results/loss_curves --plots results/loss_curves/plots

Input: results/loss_curves/<model>/seed<k>.json written by `baseline/v2pe.py --loss-log` (models v2_pe and attbal, seeds 0-4, 4 epochs; training loss every 10 batches, validation loss, validation pAUC@1e-2 and the
clean training-subset loss at every epoch end). CHECK before plotting: for every seed the epoch-2 validation pAUC@1e-2 must equal the stored value of the reported run (results/v2_pe/raw/seed<k>.json,
results/att_bal/attbal/seed<k>.json) within 0.002; otherwise the script reports the differences and stops without plotting.
Fig A: training loss (mean over seeds of the 5-point moving average, band = min-max over seeds), validation loss and clean training-subset loss at the epoch ends (mean +- std), chosen stop = epoch 2.
Fig B: validation pAUC@1e-2 per epoch.   No April logit is read.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = {"v2_pe": ("v2-PE (flatten pooling, no padding)", os.path.join("results", "v2_pe", "raw")), "attbal": ("ATT+bal (attention pooling, balanced padding)", os.path.join("results", "att_bal", "attbal"))}
SEEDS = range(5)
TOL = 0.002
BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"


def load(src):
    out = {}
    for m in MODELS:
        out[m] = [json.load(open(os.path.join(src, m, f"seed{s}.json"))) for s in SEEDS]
    return out


def check(runs):
    rows, ok = [], True
    for m, (label, stored_dir) in MODELS.items():
        for s, r in zip(SEEDS, runs[m]):
            new = r["per_epoch"][1]["val_pauc@1e-2"]
            old = json.load(open(os.path.join(ROOT, stored_dir, f"seed{s}.json")))["per_epoch"][1]["val"]["pauc@0.01"]
            rows.append({"model": m, "seed": s, "epoch2_val_pauc_new": new, "epoch2_val_pauc_stored": old, "abs_diff": abs(new - old)})
            ok &= abs(new - old) <= TOL
    return ok, rows


def smooth(v, w=5):
    v = np.asarray(v, dtype=float)
    h = w // 2
    return np.array([v[max(0, i - h):i + h + 1].mean() for i in range(len(v))])


def summary(runs):
    out = {}
    for m, rs in runs.items():
        ep = np.array([[e["epoch"] for e in r["per_epoch"]] for r in rs])[0]
        g = lambda k: np.array([[e[k] for e in r["per_epoch"]] for r in rs])
        vl, tl, pa = g("val_loss"), g("train_subset_clean_loss"), g("val_pauc@1e-2")
        out[m] = {"epochs": ep.tolist(), "val_loss_mean": vl.mean(0).tolist(), "val_loss_std": vl.std(0, ddof=1).tolist(), "train_subset_loss_mean": tl.mean(0).tolist(), "train_subset_loss_std": tl.std(0, ddof=1).tolist(),
                  "gap_val_minus_train_subset_mean": (vl - tl).mean(0).tolist(), "val_pauc_mean": pa.mean(0).tolist(), "val_pauc_std": pa.std(0, ddof=1).tolist(),
                  "epoch_of_min_val_loss_per_seed": (vl.argmin(1) + 1).tolist(), "epoch_of_max_val_pauc_per_seed": (pa.argmax(1) + 1).tolist(),
                  "train_epoch_mean_loss_mean": g("train_epoch_mean_loss").mean(0).tolist()}
    return out


def figures(runs, plots):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(plots, exist_ok=True)
    ink, mute, bg = "#0b0b0b", "#52514e", "#fcfcfb"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": mute, "axes.labelcolor": ink, "text.color": ink, "xtick.color": mute, "ytick.color": mute, "figure.facecolor": bg, "axes.facecolor": bg})
    spe = runs["v2_pe"][0]["steps_per_epoch"]
    n_ep = runs["v2_pe"][0]["epochs"]
    lo, hi = np.inf, 0.0
    curves = {}
    for m, rs in runs.items():
        steps = np.array(rs[0]["train_loss_step"])
        sm = np.stack([smooth(r["train_loss_mean_last_10"]) for r in rs])
        curves[m] = (steps, sm)
        vl = np.array([[e["val_loss"] for e in r["per_epoch"]] for r in rs])
        tl = np.array([[e["train_subset_clean_loss"] for e in r["per_epoch"]] for r in rs])
        lo, hi = min(lo, sm.min(), vl.min(), tl.min()), max(hi, sm[:, 3:].max(), vl.max(), tl.max())
    ylim = (lo * 0.8, min(hi * 1.15, 2.0))
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), sharey=True)
    for ax, (m, (label, _)) in zip(axes, MODELS.items()):
        rs = runs[m]
        steps, sm = curves[m]
        ax.plot(steps, sm.mean(0), color=BLUE, lw=1.6, label="training loss (mean of 10 batches; mean of 5 seeds, smoothed)" + (", padded training mix" if m == "attbal" else ""))
        ax.fill_between(steps, sm.min(0), sm.max(0), color=BLUE, alpha=0.18, lw=0, label="min to max over seeds")
        x_ep = np.array([e["step_end"] for e in rs[0]["per_epoch"]])
        vl = np.array([[e["val_loss"] for e in r["per_epoch"]] for r in rs])
        tl = np.array([[e["train_subset_clean_loss"] for e in r["per_epoch"]] for r in rs])
        ax.errorbar(x_ep + 15, vl.mean(0), yerr=vl.std(0, ddof=1), color=ORANGE, marker="s", ms=6, ls="none", capsize=3, mfc=bg, mew=1.6, label="validation loss, clean (mean ± std)")
        ax.errorbar(x_ep - 15, tl.mean(0), yerr=tl.std(0, ddof=1), color=GREEN, marker="^", ms=6, ls="none", capsize=3, mfc=bg, mew=1.6, label="training loss, fixed clean subset of 2,000 reports (mean ± std)")
        for e in range(1, n_ep + 1):
            ax.axvline(e * spe, color="#c9c8c2", lw=0.8, ls=":", zorder=0)
        ax.axvline(2 * spe, color=ink, lw=1.2, ls="--")
        ax.text(2 * spe + 20, ylim[1] * 0.97, "chosen stop (epoch 2)", rotation=90, va="top", ha="left", fontsize=9)
        ax.set_yscale("log")
        ax.set_ylim(*ylim)
        ax.set_xlim(0, n_ep * spe + 70)
        ax.set_xticks([e * spe for e in range(0, n_ep + 1)])
        ax.set_xlabel("training step (706 steps = 1 epoch)")
        ax.set_title(label, loc="left", fontsize=10.5)
        ax.grid(axis="y", color="#d8d7d2", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), fontsize=8.2, frameon=False, ncol=1)
    axes[0].set_ylabel("BCE loss (log scale)")
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.3)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(plots, f"figA_loss_curves.{ext}"), dpi=300)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6.2, 4.4))
    for m, c, mk in (("v2_pe", BLUE, "o"), ("attbal", ORANGE, "s")):
        pa = np.array([[e["val_pauc@1e-2"] for e in r["per_epoch"]] for r in runs[m]])
        x = np.arange(1, pa.shape[1] + 1) + (-0.03 if m == "v2_pe" else 0.03)
        ax.errorbar(x, pa.mean(0), yerr=pa.std(0, ddof=1), color=c, marker=mk, ms=6, lw=1.6, capsize=3, mfc=bg, mew=1.6, label=MODELS[m][0])
    ax.axvline(2, color=ink, lw=1.2, ls="--")
    ax.text(2.03, ax.get_ylim()[1] - 0.005 * (ax.get_ylim()[1] - ax.get_ylim()[0]), "chosen stop (epoch 2)", rotation=90, va="top", ha="left", fontsize=9)
    ax.set_xticks(range(1, n_ep + 1))
    ax.set_xlabel("epoch")
    ax.set_ylabel("validation pAUC@1e-2 (normalised)")
    ax.grid(axis="y", color="#d8d7d2", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=8.5, frameon=False)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(plots, f"figB_val_pauc.{ext}"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "loss_curves"))
    ap.add_argument("--plots", default=os.path.join(ROOT, "results", "loss_curves", "plots"))
    a = ap.parse_args()
    runs = load(a.src)
    ok, rows = check(runs)
    json.dump({"tolerance": TOL, "passed": bool(ok), "rows": rows}, open(os.path.join(a.src, "check.json"), "w"), indent=1)
    print(f"check of the epoch-2 validation pAUC@1e-2 against the stored values (tolerance {TOL}): " + ("PASSED" if ok else "FAILED"))
    for r in rows:
        print(f"  {r['model']:7s} seed {r['seed']}: new {r['epoch2_val_pauc_new']:.6f} stored {r['epoch2_val_pauc_stored']:.6f} |diff| {r['abs_diff']:.6f}")
    if not ok:
        print("NOT plotting: the rerun does not reproduce the stored epoch-2 values.")
        sys.exit(1)
    S = summary(runs)
    json.dump(S, open(os.path.join(a.src, "summary.json"), "w"), indent=1)
    figures(runs, a.plots)
    print(json.dumps({m: {k: v for k, v in s.items() if k in ("val_loss_mean", "train_subset_loss_mean", "gap_val_minus_train_subset_mean", "val_pauc_mean", "epoch_of_min_val_loss_per_seed")} for m, s in S.items()}, indent=1))


if __name__ == "__main__":
    main()
