"""
Tables and plots of the long pre-training follow-up (experiment B2), called by baseline/report.py.   (OURS)

Writes  <out>/plots/fig6_long.png, ar_epochs_curve.png, lm_loss_curves.png  and returns the markdown section "B2".
Needs   <long>/bootstrap.json  (python -m baseline.long_stats) next to the per-seed metrics of <long> and <first>.
"""
import json
import os

import numpy as np

from baseline import common as C
from baseline import long_stats as S

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6", "#898782"]
STYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1)), "-"]


def md(rows, header):
    out = "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n"
    for r in rows:
        out += "| " + " | ".join(str(c) for c in r) + " |\n"
    return out


def vals(runs, name, key, p32=False):
    out = []
    for s in S.SEEDS:
        if s in runs.get(name, {}):
            m = runs[name][s][2]
            out.append((m["test_p32"] if p32 else m["test"])[key])
    return np.array(out)


def pm(v, d=3):
    return f"{v.mean():.{d}f} ± {v.std():.{d}f}"


def ci(e, d=3):
    return f"{100 * e['point']:+.1f} [{100 * e['lo']:+.1f}, {100 * e['hi']:+.1f}]" if "point" in e else ""


def section(first, long, out, bootstrap_path=None):
    runs = S.collect(first, long)
    if not any(n.startswith(("ar_lasttoken_ep", "mlm_bert_best", "mlm_theirs_best")) for n in runs):
        return ""
    boot = json.load(open(bootstrap_path or os.path.join(long, "bootstrap.json")))
    B = boot["bootstrap"]
    names = [n for n in S.LABELS if n in runs]
    txt = "## B2. Longer self-supervised pre-training (follow-up to B)\n\n"
    txt += ("Same tokens, seeds, 80/20 splits and fine-tuning as B (10 epochs on the labeled 20%); only the pre-training is longer (up to 15 epochs, "
            "early stop: patience 2, min delta 0.01 on the validation LM loss, best epoch restored). Upper bound, lower bound and the controls are the runs "
            "of B (not retrained). Logit-ranked TPR. 'best' = the epoch with the lowest validation LM loss.\n\n")

    # ---- absolute numbers
    rows = []
    for n in names:
        v = vals(runs, n, "tpr@0.001")
        rows.append([S.LABELS[n], len(v), f"{pm(v)} ({v.min():.3f}–{v.max():.3f})", pm(vals(runs, n, "tpr@0.001", p32=True)), pm(vals(runs, n, "tpr@0.01")),
                     pm(vals(runs, n, "auc"), 4), pm(vals(runs, n, "f1@0.5"), 4)])
    txt += "### Absolute numbers (mean ± std over seeds, April test set)\n\n"
    txt += md(rows, ["run", "seeds", "TPR@1e-3 (min–max)", "same, literal float32", "TPR@1e-2", "AUC", "F1 (0.5)"]) + "\n"

    # ---- paired differences + bootstrap
    txt += "### Paired differences (same seed, same split) and bootstrap CIs\n\n"
    txt += ("Per-seed differences: mean ± std over the 5 seeds, and in how many seeds the difference is positive. **Bootstrap**: 95% CI over the April test "
            "reports (1,000 stratified resamples, same resample for every run and seed), in points of TPR; **resolved** = the CI excludes 0. Two statistics: "
            "**per-seed mean** = the mean over the 5 seeds of each seed's own TPR (matches the per-seed columns); **ensemble** = the TPR of the seed-averaged "
            "score (mean logit over the 5 seeds), i.e. a 5-model ensemble. The ensemble lifts the low-FPR TPR of every run, the lower bound most, so its differences are "
            "smaller (or of opposite sign) than the per-seed ones. The bootstrap measures test-set sampling noise only; the seed std measures training noise.\n\n")

    def cell(e):
        return (ci(e) + (" **resolved**" if e["resolved"] else " not resolved")) if e else ""

    for key, label in (("tpr@0.001", "TPR@1e-3"), ("tpr@0.01", "TPR@1e-2")):
        rows = []
        for n in names:
            if n in ("upper", "lower") or n not in B:
                continue
            r = boot["runs"].get(n)
            if not r:
                continue
            a, b = r["minus_lower"][key], r["upper_minus"][key]
            ps, en = B[n][key]["ps"], B[n][key]["ens"]
            rows.append([S.LABELS[n], f"{100 * a['mean']:+.1f} ± {100 * a['std']:.1f} ({a['n_positive']}/{a['n']} > 0)",
                         cell(ps.get("vs_lower")), cell(en.get("vs_lower")),
                         f"{100 * b['mean']:+.1f} ± {100 * b['std']:.1f}", cell(ps.get("upper_minus")), cell(en.get("upper_minus"))])
        txt += f"**{label}** (points; run − lower > 0 = better than the lower bound; upper − run > 0 = below the upper bound)\n\n"
        txt += md(rows, ["run", "run − lower, per seed", "CI, per-seed mean", "CI, ensemble", "upper − run, per seed", "CI, per-seed mean", "CI, ensemble"]) + "\n"
    rows = []
    for n in names:
        if n in ("upper",) or n not in boot["runs"]:
            continue
        a, b = boot["runs"][n]["minus_lower"]["auc"], boot["runs"][n]["upper_minus"]["auc"]
        rows.append([S.LABELS[n], f"{100 * a['mean']:+.2f} ± {100 * a['std']:.2f} ({a['n_positive']}/{a['n']} > 0)", f"{100 * b['mean']:+.2f} ± {100 * b['std']:.2f}"])
    txt += "**AUC** (points, per seed)\n\n" + md(rows, ["run", "run − lower", "upper − run"]) + "\n"
    if "upper" in B and "lower" in B:
        txt += "Bootstrap point estimates and 95% CIs of the two bounds (TPR in %): " + "; ".join(
            f"{S.LABELS[n]}: " + ", ".join(
                f"TPR@{lab} per-seed mean {100 * B[n][k]['ps']['point']:.1f} [{100 * B[n][k]['ps']['lo']:.1f}, {100 * B[n][k]['ps']['hi']:.1f}], "
                f"ensemble {100 * B[n][k]['ens']['point']:.1f} [{100 * B[n][k]['ens']['lo']:.1f}, {100 * B[n][k]['ens']['hi']:.1f}]"
                for k, lab in (("tpr@0.001", "1e-3"), ("tpr@0.01", "1e-2"))) for n in ("upper", "lower")) + ".\n\n"

    # ---- AR epoch curve table
    rows = []
    for k, n in ((3, "ar_lasttoken_ep3"), (6, "ar_lasttoken_ep6"), (10, "ar_lasttoken_ep10"), ("best", "ar_lasttoken_best")):
        if n not in runs:
            continue
        be = [runs[n][s][2].get("pretrain_epoch") for s in sorted(runs[n])]
        lab = k if k != "best" else f"best (epochs {min(be)}–{max(be)}, mean {np.mean(be):.1f})"
        rows.append([lab, len(runs[n]), pm(vals(runs, n, "tpr@0.001")), pm(vals(runs, n, "tpr@0.01")), pm(vals(runs, n, "auc"), 4)])
    if "ar_lasttoken_3ep" in runs:
        rows.insert(0, ["3 (first run)", len(runs["ar_lasttoken_3ep"]), pm(vals(runs, "ar_lasttoken_3ep", "tpr@0.001")),
                        pm(vals(runs, "ar_lasttoken_3ep", "tpr@0.01")), pm(vals(runs, "ar_lasttoken_3ep", "auc"), 4)])
    txt += "### AR last-token: detection against pre-training length\n\n" + md(rows, ["AR pre-training epoch", "seeds", "TPR@1e-3", "TPR@1e-2", "AUC"])
    for key, ln in (("lower", "lower bound"), ("upper", "upper bound")):
        txt += f"\n{ln}: TPR@1e-3 {pm(vals(runs, key, 'tpr@0.001'))}, TPR@1e-2 {pm(vals(runs, key, 'tpr@0.01'))}, AUC {pm(vals(runs, key, 'auc'), 4)}.\n"
    txt += "\n![AR epochs curve](plots/ar_epochs_curve.png)\n\n"

    # ---- epoch-3 reproduction check
    if "ar_lasttoken_ep3" in runs and "ar_lasttoken_3ep" in runs:
        rows = []
        for s in S.SEEDS:
            if s in runs["ar_lasttoken_ep3"] and s in runs["ar_lasttoken_3ep"]:
                a, b = runs["ar_lasttoken_3ep"][s][2], runs["ar_lasttoken_ep3"][s][2]
                h1 = [e["val_loss"] for e in a["pretraining"]["epochs"]][:3]
                h2 = [e["val_loss"] for e in b["pretraining"]["epochs"]][:3]
                rows.append([s, f"{h1[-1]:.4f}", f"{h2[-1]:.4f}", f"{a['test']['tpr@0.001']:.3f}", f"{b['test']['tpr@0.001']:.3f}",
                             f"{a['test']['tpr@0.01']:.3f}", f"{b['test']['tpr@0.01']:.3f}", f"{a['test']['auc']:.4f}", f"{b['test']['auc']:.4f}"])
        txt += ("### Check: epoch 3 of the long run against the first run\n\nSame procedure (same seed, split, RNG order); GPU kernels are not deterministic, "
                "so exact equality is not expected.\n\n")
        txt += md(rows, ["seed", "val LM loss ep 3 (first)", "(long)", "TPR@1e-3 (first)", "(long)", "TPR@1e-2 (first)", "(long)", "AUC (first)", "(long)"]) + "\n"

    # ---- pre-training table
    rows = []
    for kind, lab in (("ar", "AR"), ("mlm_bert", "MLM per-position"), ("mlm_theirs", "MLM authors'")):
        for s in S.SEEDS:
            p = os.path.join(long, f"seed{s}", f"pretrain_{kind}_long.json")
            if os.path.exists(p):
                h = json.load(open(p))
                ep = h["epochs"]
                rows.append([lab, s, len(ep), h["best_epoch"], "yes" if h["stopped_early"] else "no (reached the maximum)", f"{ep[0]['val_loss']:.3f}",
                             f"{ep[-1]['val_loss']:.3f}", f"{min(e['val_loss'] for e in ep):.3f}", f"{h['seconds'] / 60:.0f}"])
    if rows:
        txt += "### Pre-training runs\n\n" + md(rows, ["method", "seed", "epochs run", "best epoch", "stopped early", "val loss, epoch 1", "last epoch", "lowest", "minutes"])
        txt += "\n![LM loss curves](plots/lm_loss_curves.png)\n\n![Fig 6 long](plots/fig6_long.png)\n\n"

    plots(runs, long, out)
    return txt


def plots(runs, long, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pdir = os.path.join(out, "plots")
    os.makedirs(pdir, exist_ok=True)
    # ---- Fig 6 long: mean ROC over seeds
    order = [n for n in ("upper", "ar_lasttoken_best", "ar_flatten_best", "mlm_bert_best", "mlm_theirs_best", "lower") if n in runs]
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    for i, n in enumerate(order):
        roc = np.mean([runs[n][s][2]["test"]["roc_on_grid"] for s in sorted(runs[n])], axis=0)
        ax.plot(C.ROC_GRID, roc, color=COLORS[i], ls=STYLES[i], lw=2, label=S.LABELS[n])
    ax.axvline(1e-3, color="#898782", lw=1, ls=":")
    ax.set_xscale("log"); ax.set_xlim(1e-4, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("Long self-supervised pre-training, April test set (mean ROC over seeds)", loc="left", fontsize=10.5)
    ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(pdir, "fig6_long.png"), dpi=160); plt.close(fig)

    # ---- AR epochs curve
    pts = [(3, "ar_lasttoken_ep3"), (6, "ar_lasttoken_ep6"), (10, "ar_lasttoken_ep10"), (None, "ar_lasttoken_best")]
    pts = [(k, n) for k, n in pts if n in runs]
    if pts and "upper" in runs and "lower" in runs:
        fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
        for ax, (key, lab) in zip(axes, S.METRICS):
            xs, ms, ss = [], [], []
            for k, n in pts:
                v = np.array([runs[n][s][0][key] for s in sorted(runs[n])])
                x = k if k is not None else float(np.mean([runs[n][s][2]["pretrain_epoch"] for s in runs[n]]))
                xs.append(x); ms.append(v.mean()); ss.append(v.std())
            ax.errorbar(xs, ms, yerr=ss, color=COLORS[0], marker="o", lw=2, capsize=3, label="AR last-token (3, 6, 10, best)")
            if "ar_lasttoken_3ep" in runs:
                v = np.array([runs["ar_lasttoken_3ep"][s][0][key] for s in sorted(runs["ar_lasttoken_3ep"])])
                ax.plot([3], [v.mean()], marker="o", mfc="none", color=COLORS[1], ls="none", ms=9, label="3 epochs, first run")
            for name, color in (("upper", COLORS[2]), ("lower", COLORS[3])):
                v = np.array([runs[name][s][0][key] for s in sorted(runs[name])])
                ax.axhline(v.mean(), color=color, lw=1.5, ls="--", label=S.LABELS[name])
                ax.axhspan(v.mean() - v.std(), v.mean() + v.std(), color=color, alpha=0.12, lw=0)
            ax.set_xlabel("AR pre-training epochs (best: mean best epoch)"); ax.set_title(lab, loc="left", fontsize=10.5)
            ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
        axes[0].legend(frameon=False, fontsize=7.5, loc="best")
        fig.tight_layout(); fig.savefig(os.path.join(pdir, "ar_epochs_curve.png"), dpi=160); plt.close(fig)

    # ---- LM loss curves
    import glob
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
    for ax, (kind, title) in zip(axes, (("ar", "AR (next token)"), ("mlm_bert", "MLM per-position (ours)"), ("mlm_theirs", "MLM authors' multi-hot"))):
        for s in S.SEEDS:
            p = os.path.join(long, f"seed{s}", f"pretrain_{kind}_long.json")
            if not os.path.exists(p):
                continue
            h = json.load(open(p))
            ep = [e["epoch"] for e in h["epochs"]]
            ax.plot(ep, [e["val_loss"] for e in h["epochs"]], color=COLORS[s % 6], lw=1.8, marker="o", ms=3, label=f"seed {s} val")
            ax.plot(ep, [e["train_loss"] for e in h["epochs"]], color=COLORS[s % 6], lw=1, ls=":", alpha=0.7)
            ax.axvline(h["best_epoch"], color=COLORS[s % 6], lw=0.8, ls="--", alpha=0.5)
        ax.set_xlabel("epoch"); ax.set_ylabel("LM loss"); ax.set_title(title + " (solid: validation, dotted: train, dashed: best)", loc="left", fontsize=8.5)
        ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
        if kind == "ar":
            ax.legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(os.path.join(pdir, "lm_loss_curves.png"), dpi=160); plt.close(fig)
