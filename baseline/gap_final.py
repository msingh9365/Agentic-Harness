"""
Final comparison of the gap follow-up: released checkpoint vs our current recipe vs baseline v2 (the recipe chosen on the validation slice).   (OURS)

    python -m baseline.gap_final --gap results/F_gap --plots results/baseline/plots [--boot 1000]

Inputs
  results/F_gap/calib_arrays.npz         April test logits of the released checkpoint (1 model) and of our current recipe (9 fold models, 3 seeds x 3 folds)
  results/F_gap/v2/seed{k}_test_logits.npy + results/F_gap/v2/seed{k}.json      baseline v2 (5 seeds), logits at the chosen epoch
Statistics (the B2 method): stratified bootstrap over the April test reports (malware and benign resampled separately, 1,000 resamples, the same
resample for every model); two statistics per group: "ps" = mean over the group's models of each model's own metric (matches the per-seed tables),
"ens" = metric of the mean logit over the group's models. CIs are 95% percentile intervals; a difference is RESOLVED when its CI excludes 0.
All rankings use logits (decision 0.0); the literal float32-probability TPR@1e-3 is reported next to them.
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C, gap_report as G

M = [("tpr@0.001", "TPR@1e-3"), ("tpr@0.01", "TPR@1e-2"), ("auc", "AUC")]


def roc_metrics(y, z):
    """(TPR@1e-3, TPR@1e-2, AUC) from one roc_curve call (the authors' get_tpr_at_fpr rule)."""
    from sklearn.metrics import auc, roc_curve
    fpr, tpr, _ = roc_curve(y, z)
    return np.array([tpr[fpr <= 1e-3][-1], tpr[fpr <= 1e-2][-1], auc(fpr, tpr)])


def group_metrics(y, Z, kind):
    return roc_metrics(y, Z.mean(0)) if kind == "ens" else np.mean([roc_metrics(y, z) for z in Z], axis=0)


def bootstrap(y, groups, n_boot=1000, seed=0):
    y = np.asarray(y).astype(int)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    rng = np.random.default_rng(seed)
    draws = {k: {g: np.empty((n_boot, 3)) for g in groups} for k in ("ps", "ens")}
    for b in range(n_boot):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        for g, Z in groups.items():
            for k in ("ps", "ens"):
                draws[k][g][b] = group_metrics(y[idx], Z[:, idx], k)
    out = {}
    for k in ("ps", "ens"):
        pt = {g: group_metrics(y, Z, k) for g, Z in groups.items()}
        out[k] = {}
        for g in groups:
            e = {}
            for j, (key, _) in enumerate(M):
                lo, hi = np.percentile(draws[k][g][:, j], [2.5, 97.5])
                e[key] = {"point": float(pt[g][j]), "lo": float(lo), "hi": float(hi)}
            out[k][g] = e
        out[k]["diffs"] = {}
        for a, b in (("v2", "released"), ("v2", "current"), ("released", "current")):
            if a in groups and b in groups:
                e = {}
                for j, (key, _) in enumerate(M):
                    d = draws[k][a][:, j] - draws[k][b][:, j]
                    lo, hi = np.percentile(d, [2.5, 97.5])
                    e[key] = {"point": float(pt[a][j] - pt[b][j]), "lo": float(lo), "hi": float(hi), "resolved": bool(lo > 0 or hi < 0)}
                out[k]["diffs"][f"{a} - {b}"] = e
    return out


def per_model(y, Z):
    """metrics of every model: TPR@1e-3, TPR@1e-2, AUC, F1@logit 0, literal float32-probability TPR@1e-3."""
    rows = []
    for z in Z:
        m = C.binary_metrics(y, z, decision=0.0)
        lit = C.binary_metrics(y, C.sigmoid32(z))["tpr@0.001"]
        rows.append([m["tpr@0.001"], m["tpr@0.01"], m["auc"], m["f1@0.5"], lit])
    return np.array(rows)


def fmt(a, d=3):
    return f"{a.mean():.{d}f} ± {a.std(ddof=1):.{d}f}" if len(a) > 1 else f"{a[0]:.{d}f}"


def load_v2(gap):
    fs = sorted(glob.glob(os.path.join(gap, "v2", "seed*_test_logits.npy")))
    return np.array([np.load(f).astype(np.float64) for f in fs]), [int(os.path.basename(f)[4]) for f in fs]


def tables(gap, y, groups, stats, n_boot):
    pm = {g: per_model(y, Z) for g, Z in groups.items()}
    L = ["| model | n | TPR@1e-3 | TPR@1e-2 | AUC | F1@0.5 | TPR@1e-3 literal float32 |", "|---|---|---|---|---|---|---|"]
    names = {"released": "released checkpoint (authors)", "current": "ours, current recipe (A: lr 2.5e-4, 2/3 of January, fixed budget)", "v2": "**baseline v2** (lr 2e-3, 90% of January, 2 epochs)"}
    for g in groups:
        a = pm[g]
        L.append(f"| {names[g]} | {len(a)} | " + " | ".join(fmt(a[:, j]) if j != 2 else fmt(a[:, j], 4) for j in (0, 1, 2, 3, 4)) + " |")
    L += ["", f"Bootstrap 95% CI over the April test reports ({n_boot} stratified resamples). `ps` = mean of the models' own values, `ens` = ensemble of the group's logits.", "",
          "| group | statistic | TPR@1e-3 | TPR@1e-2 | AUC |", "|---|---|---|---|---|"]
    for g in groups:
        for k in ("ps", "ens"):
            e = stats[k][g]
            L.append(f"| {g} | {k} | " + " | ".join(f"{e[key]['point']:.3f} [{e[key]['lo']:.3f}, {e[key]['hi']:.3f}]" if key != "auc" else
                                                     f"{e[key]['point']:.4f} [{e[key]['lo']:.4f}, {e[key]['hi']:.4f}]" for key, _ in M) + " |")
    L += ["", "Paired differences (same resample):", "", "| difference | statistic | TPR@1e-3 | TPR@1e-2 | AUC |", "|---|---|---|---|---|"]
    for k in ("ps", "ens"):
        for dname, e in stats[k]["diffs"].items():
            L.append(f"| {dname} | {k} | " + " | ".join(
                (f"{e[key]['point']:+.3f} [{e[key]['lo']:+.3f}, {e[key]['hi']:+.3f}]" if key != "auc" else f"{e[key]['point']:+.4f} [{e[key]['lo']:+.4f}, {e[key]['hi']:+.4f}]")
                + (" **resolved**" if e[key]["resolved"] else "") for key, _ in M) + " |")
    return "\n".join(L), pm


def appendix(gap):
    """Test numbers of every recipe of the grid at the epoch chosen on validation, and at every epoch: NOT used for selection."""
    R = G.load_recipes(gap)
    L = ["Appendix: the full grid on the April test set. **Not used for selection** (every choice was made on the validation slice). Mean ± std over 5 seeds, logit-ranked.", "",
         "| recipe | epoch (picked on validation) | val TPR@1e-3 | test TPR@1e-3 | test TPR@1e-2 | test AUC | test F1@0.5 |", "|---|---|---|---|---|---|---|"]
    for name, runs in R.items():
        if name.startswith("_"):
            continue
        ep = G.select_epoch(runs)
        v = G.curve(runs, "tpr@0.001")[:, ep - 1]
        t = lambda k: np.array([r["per_epoch"][ep - 1]["test_NOT_FOR_SELECTION"][k] for r in runs])
        L.append(f"| {name} | {ep} | {fmt(v)} | {fmt(t('tpr@0.001'))} | {fmt(t('tpr@0.01'))} | {fmt(t('auc'), 4)} | {fmt(t('f1@0.5'))} |")
    return "\n".join(L)


def plot_val_curves(gap, plots):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pal = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6", "#898782", "#0b3d91", "#8c2d04", "#00695c"]
    R = {k: v for k, v in G.load_recipes(gap).items() if not k.startswith("_")}
    drawn = {k: v for k, v in R.items() if not k.startswith(("R6", "R9"))}               # R6 and R9 collapsed (constant predictor): off every axis
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    for ax, (key, title) in zip(axes, M):
        for i, (name, runs) in enumerate(drawn.items()):
            c = pal[int(name[1]) % len(pal)]
            v = G.curve(runs, key)
            x = np.arange(1, v.shape[1] + 1)
            m, sd = v.mean(0), v.std(0, ddof=1)
            hi = name.startswith(("R4", "R8"))
            ax.plot(x, m, color=c, lw=2.6 if hi else 1.3, ls="-" if int(name[1]) < 7 else "--", label=name)
            ax.fill_between(x, m - sd, m + sd, color=c, alpha=0.06)
        ax.set_xlabel("epoch"); ax.set_title(f"validation {title} (mean of 5 seeds)", loc="left", fontsize=10.5)
        ax.set_ylim({"auc": (0.995, 0.9990), "tpr@0.01": (0.92, 0.99)}.get(key, (0.4, 1.0)))
        ax.grid(alpha=0.3); [ax.spines[s_].set_visible(False) for s_ in ("top", "right")]
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=8.5, loc="center right")
    fig.text(0.01, 0.01, "Bands = ± std over seeds (first panel only is noisy by design: 2,467 validation benign reports allow 2 false alarms at FPR 1e-3). "
             "Not drawn: R6 (lr 1e-2) collapsed to a constant predictor (AUC 0.5) in all 5 seeds; R9 (lr 5e-3) in 3 of 5.", fontsize=7.5, color="#555")
    fig.tight_layout(rect=(0, 0.04, 0.88, 1)); fig.savefig(os.path.join(plots, "gap_val_curves.png"), dpi=160); plt.close(fig)


def plot_roc(plots, y, groups):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve
    grid = np.logspace(-5, 0, 400)
    col = {"released": G.COLORS[1], "current": G.COLORS[0], "v2": G.COLORS[2]}
    lab = {"released": "released checkpoint", "current": "current recipe (mean of 9 models)", "v2": "baseline v2 (mean of 5 seeds)"}
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    for g, Z in groups.items():
        curves = []
        for z in Z:
            fpr, tpr, _ = roc_curve(y, z)
            curves.append(np.interp(grid, fpr, tpr))
        ax.plot(grid, np.mean(curves, 0), color=col[g], lw=2.2, label=lab[g])
        for c in curves if g != "released" else []:
            ax.plot(grid, c, color=col[g], lw=0.6, alpha=0.25)
    for t in (1e-3, 1e-2):
        ax.axvline(t, color="#777", lw=0.8, ls=":")
    ax.set_xscale("log"); ax.set_xlim(1e-5, 1); ax.set_ylim(0, 1.01)
    ax.set_xlabel("false positive rate (log scale)"); ax.set_ylabel("true positive rate")
    ax.set_title("April test set: ROC", loc="left", fontsize=10.5)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right"); ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    fig.tight_layout(); fig.savefig(os.path.join(plots, "gap_roc.png"), dpi=160); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", default="results/F_gap")
    ap.add_argument("--plots", default="results/baseline/plots")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--no-boot", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.plots, exist_ok=True)
    z = np.load(os.path.join(a.gap, "calib_arrays.npz"))
    y = z["y_test"].astype(int)
    v2, seeds = load_v2(a.gap)
    groups = {"released": z["released_test"][None].astype(np.float64), "current": z["ours_test"].astype(np.float64), "v2": v2}
    assert v2.shape[1] == len(y), "v2 logits do not match the test set"
    np.save(os.path.join(a.gap, "v2_test_logits.npy"), v2.astype(np.float32))
    plot_val_curves(a.gap, a.plots)
    G.plot_logit_hist(a.gap, a.plots)
    plot_roc(a.plots, y, groups)
    stats = bootstrap(y, groups, a.boot) if not a.no_boot else None
    if stats:
        text, pm = tables(a.gap, y, groups, stats, a.boot)
        json.dump({"n_boot": a.boot, "v2_seeds": seeds, "bootstrap": stats, "per_model": {g: p.round(5).tolist() for g, p in pm.items()},
                   "columns": ["tpr@0.001", "tpr@0.01", "auc", "f1@0.5", "tpr@0.001_literal_float32"]}, open(os.path.join(a.gap, "final_stats.json"), "w"), indent=1)
        open(os.path.join(a.gap, "final_table.md"), "w").write(text + "\n\n" + appendix(a.gap) + "\n")
        print(text)
    print(appendix(a.gap))


if __name__ == "__main__":
    main()
