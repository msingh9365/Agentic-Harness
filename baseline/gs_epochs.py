"""
Stage D, Step 1 of NOTES 22: validation metrics of every epoch of the Stage C runs of both new-split models (10 seeds each), computed from the stored per-epoch VALIDATION logits (no checkpoint is needed, and no April
logit is opened).   (OURS)

    python -m baseline.gs_epochs --runs <Stage C outputs: gsf_v2pe/ gsf_attbal/> --out results/groupsplit/stage_d

Per seed and epoch: validation pAUC@1e-2, TPR@1e-2 (threshold from the validation benign reports), AUC, validation loss (recomputed from the logits and checked against the loss logged during training), mean |logit|.
Reports the epoch of the highest mean validation pAUC, the per-seed best epochs, and whether validation pAUC falls as validation loss rises (change of the means from epoch 1 to the last epoch, Spearman correlations over
the epoch means and over all seed-epoch points, per-seed change) or stays flat (overconfidence rather than worse ranking). Figure: validation pAUC per epoch next to validation loss.
"""
import argparse
import json
import os

import numpy as np

from baseline import common as C, gap, groupsplit as G

SEEDS = list(range(10))
MODELS = [("v2pe", "gsf_v2pe", "v2-PE (lr 2e-3)", 4, 1), ("attbal", "gsf_attbal", "ATT+bal (lr 1e-3, p 0.5)", 6, 3)]       # name, tag, label, epochs, chosen epoch of Stage C


def spearman(a, b):
    from scipy.stats import spearmanr
    return float(spearmanr(a, b)[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", default="results/groupsplit/stage_d")
    a = ap.parse_args()
    _, vidx = G.val_slice()
    fam = G.january_table()["train"]["family"][vidx]
    yv = (~np.isin(fam, ["clean", "windows_syswow64"])).astype(int)
    assert int(yv.sum()) == 5557 and len(yv) == 8718
    os.makedirs(a.out, exist_ok=True)
    res, L = {}, ["### Step 1: validation metrics per epoch (group-split slice, 8,718 reports: 3,161 benign, 5,557 malware; 10 seeds; mean ± SD)", ""]
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 3, figsize=(13, 6.6), dpi=200)
    for r, (name, tag, label, ne, chosen) in enumerate(MODELS):
        M = {k: np.zeros((len(SEEDS), ne)) for k in ("pauc", "tpr01", "auc", "loss", "absl")}
        maxdiff = 0.0
        for s in SEEDS:
            logged = json.load(open(os.path.join(a.runs, tag, f"seed{s}.json")))["per_epoch"]
            for e in range(1, ne + 1):
                z = np.load(os.path.join(a.runs, tag, f"seed{s}_epoch{e}_val_logits.npy")).astype(np.float64).reshape(-1)
                m = C.binary_metrics(yv, z, decision=0.0)
                M["pauc"][s, e - 1], M["tpr01"][s, e - 1], M["auc"][s, e - 1] = m["pauc@0.01"], m["tpr@0.01"], m["auc"]
                M["loss"][s, e - 1], M["absl"][s, e - 1] = gap.bce_logits(yv, z), np.abs(z).mean()
                maxdiff = max(maxdiff, abs(M["loss"][s, e - 1] - logged[e - 1]["val_loss"]), abs(M["pauc"][s, e - 1] - logged[e - 1]["val"]["pauc@0.01"]))
        mean = {k: v.mean(0) for k, v in M.items()}
        peak = int(np.argmax(mean["pauc"])) + 1
        best_seed = (np.argmax(M["pauc"], axis=1) + 1).tolist()                       # ties -> earlier epoch (argmax returns the first)
        ep = np.arange(1, ne + 1)
        sp_means = spearman(mean["pauc"], mean["loss"])
        sp_pool = spearman(M["pauc"].ravel(), M["loss"].ravel())
        within = [spearman(M["pauc"][s], M["loss"][s]) for s in SEEDS]
        d_pauc, d_loss = M["pauc"][:, -1] - M["pauc"][:, 0], M["loss"][:, -1] - M["loss"][:, 0]
        res[name] = {"label": label, "epochs": ne, "stage_c_chosen_epoch": chosen, "mean": {k: v.tolist() for k, v in mean.items()}, "sd": {k: v.std(0, ddof=1).tolist() for k, v in M.items()}, "per_seed": {k: v.tolist() for k, v in M.items()},
                     "peak_epoch_of_mean_pauc": peak, "per_seed_best_epoch": best_seed, "spearman_epoch_means_pauc_vs_loss": sp_means, "spearman_all_seed_epochs": sp_pool, "spearman_within_seed": within,
                     "pauc_change_last_minus_first_per_seed": d_pauc.tolist(), "loss_change_last_minus_first_per_seed": d_loss.tolist(), "max_abs_diff_vs_logged": float(maxdiff)}
        L += [f"**{label}** (epochs 1-{ne}; the Stage C choice was epoch {chosen}; recomputed loss and pAUC agree with the logged values to {maxdiff:.1e})", "",
              "| epoch | val pAUC@1e-2 | val TPR@1e-2 | val AUC | val loss | mean abs logit |", "|---|---|---|---|---|---|"]
        for e in ep:
            sd = {k: v.std(0, ddof=1) for k, v in M.items()}
            L.append(f"| {e}{' (Stage C choice)' if e == chosen else ''}{' (peak)' if e == peak else ''} | {mean['pauc'][e-1]:.4f} ± {sd['pauc'][e-1]:.4f} | {mean['tpr01'][e-1]:.4f} ± {sd['tpr01'][e-1]:.4f} | {mean['auc'][e-1]:.4f} ± {sd['auc'][e-1]:.4f} | {mean['loss'][e-1]:.3f} ± {sd['loss'][e-1]:.3f} | {mean['absl'][e-1]:.1f} |")
        L += ["", f"Peak of the mean validation pAUC@1e-2: epoch {peak}. Best epoch per seed (seeds 0-9): {best_seed} (counts: " + ", ".join(f"epoch {e}: {best_seed.count(e)}" for e in ep) + ").",
              f"From epoch 1 to epoch {ne}: mean validation pAUC {mean['pauc'][0]:.4f} -> {mean['pauc'][-1]:.4f} (per-seed change {d_pauc.mean():+.4f} ± {d_pauc.std(ddof=1):.4f}; {int((d_pauc < 0).sum())}/10 seeds lower); mean validation loss {mean['loss'][0]:.3f} -> {mean['loss'][-1]:.3f}; mean AUC {mean['auc'][0]:.4f} -> {mean['auc'][-1]:.4f}; mean |logit| {mean['absl'][0]:.1f} -> {mean['absl'][-1]:.1f}.",
              f"Spearman correlation of validation pAUC with validation loss: over the {ne} epoch means {sp_means:+.2f}; over all {len(SEEDS) * ne} seed-epoch points {sp_pool:+.2f}; within a seed (mean of 10) {np.mean(within):+.2f}. (Negative = pAUC falls as loss rises.)", ""]
        a0, a1, a2 = ax[r]
        for s in SEEDS:
            a0.plot(ep, M["pauc"][s], color="#6250d6", alpha=0.18, lw=0.8)
            a1.plot(ep, M["loss"][s], color="#eb6834", alpha=0.18, lw=0.8)
            a2.plot(ep, M["absl"][s], color="#1baf7a", alpha=0.18, lw=0.8)
        for a_, k, col in ((a0, "pauc", "#6250d6"), (a1, "loss", "#eb6834"), (a2, "absl", "#1baf7a")):
            a_.plot(ep, mean[k], "-o", ms=3.5, color=col, lw=2)
            a_.fill_between(ep, mean[k] - M[k].std(0, ddof=1), mean[k] + M[k].std(0, ddof=1), color=col, alpha=0.15, lw=0)
            a_.axvline(chosen, color="#888", ls=":", lw=1)
            a_.set_xticks(ep)
            a_.set_xlabel("epoch")
            a_.spines[["top", "right"]].set_visible(False)
        a0.set_title(f"{label}: validation pAUC@1e-2", fontsize=9)
        a1.set_title("validation loss", fontsize=9)
        a2.set_title("mean |logit| on validation (confidence)", fontsize=9)
        a1.set_yscale("log")
    fig.suptitle("Group-split validation slice, 10 seeds (thin = seeds, thick = mean ± SD, dotted = the epoch chosen in Stage B)", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_step1_val_pauc_vs_loss.png"))
    open(os.path.join(a.out, "step1_val_per_epoch.md"), "w").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(a.out, "step1_val_per_epoch.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
