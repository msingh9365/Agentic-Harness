"""
Selection, statistics, tables and plots of experiment B3 (Fig. 6 with the v2 recipe).   (OURS)

    python -m baseline.b3_report --raw results/B3_selfsup_v2/raw --out results/B3_selfsup_v2 --plots results/baseline/plots [--boot 1000] [--val-only]

Input   <raw>/seed<k>/<run>_lr<lr>.json (+ _val_logits.npy, _test_logits.npy, shape [epochs, n]) written by baseline/b3.py.
Step 1  `choose`: the (lr, epoch) of each run type from the VALIDATION curves alone, by the rule written in NOTES.md 11.4 before any run.
        `--val-only` prints only validation numbers (used while the settings are being chosen).
Step 2  the April test logits of the chosen settings -> per-seed metrics, paired differences, stratified bootstrap (baseline/long_stats.py, the B2 method).
Output  <out>/choice.json, chosen_metrics.json, bootstrap.json, tables.md (+ the full grid on test, marked "not used for selection"),
        <plots>/fig6_v2.png, b3_val_curves.png
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C
from baseline import long_stats as LS

SEEDS = [0, 1, 2, 3, 4]
RUNS = ["upper", "lower", "lower_lasttoken", "ar_lasttoken", "mlm_bert"]
LABELS = {"upper": "upper bound (90% labeled)", "lower": "lower bound (20% labeled)", "lower_lasttoken": "control: causal last-token, 20%, no pre-training",
          "ar_lasttoken": "AR pre-training + last-token", "mlm_bert": "per-position MLM pre-training"}
COLORS = {"upper": "#2a78d6", "lower": "#898782", "lower_lasttoken": "#eda100", "ar_lasttoken": "#1baf7a", "mlm_bert": "#eb6834"}
COLLAPSE_AUC = 0.6


def load(raw):
    """R[run][lr][seed] = result dict (json); only (run, lr) cells that exist."""
    R = {}
    for f in sorted(glob.glob(os.path.join(raw, "seed*", "*_lr*.json"))):
        d = json.load(open(f))
        R.setdefault(d["run"], {}).setdefault(d["lr"], {})[int(os.path.basename(os.path.dirname(f))[4:])] = d
    return R


def stack(cell, getter):
    return np.array([[getter(e) for e in cell[s]["per_epoch"]] for s in sorted(cell)])


def val_curve(cell, key):
    return stack(cell, lambda e: e["val"][key])


def val_loss(cell):
    return stack(cell, lambda e: e["val_loss"])


def collapsed(cell):
    """Any seed with validation AUC < 0.6 at the last epoch (a constant predictor has 0.5)."""
    return [s for s in sorted(cell) if cell[s]["per_epoch"][-1]["val"]["auc"] < COLLAPSE_AUC]


def choose(R, seeds=SEEDS):
    """The rule of NOTES.md 11.4, on validation only. Returns {run: {"lr", "epoch", "cells": [...], "excluded": {lr: [seeds]}}}."""
    out = {}
    for run, by_lr in R.items():
        cells, excluded = [], {}
        full = {lr: c for lr, c in by_lr.items() if sorted(c) == sorted(seeds)}
        for lr, c in sorted(full.items(), reverse=True):
            bad = collapsed(c)
            if bad:
                excluded[lr] = bad
        use = {lr: c for lr, c in full.items() if lr not in excluded}
        if 2e-3 in excluded and 1e-3 in full and 1e-3 in use:
            use = {1e-3: use[1e-3]}
        for lr, c in use.items():
            v, l = val_curve(c, "tpr@0.001"), val_loss(c)
            for e in range(v.shape[1]):
                cells.append({"lr": lr, "epoch": e + 1, "m": float(v[:, e].mean()), "se": float(v[:, e].std(ddof=1) / np.sqrt(len(v))), "loss": float(l[:, e].mean()),
                              "tpr@0.01": float(val_curve(c, "tpr@0.01")[:, e].mean()), "auc": float(val_curve(c, "auc")[:, e].mean())})
        if not cells:
            out[run] = {"lr": None, "epoch": None, "cells": [], "excluded": excluded}
            continue
        best = max(cells, key=lambda c: c["m"])
        tied = [c for c in cells if c["m"] >= best["m"] - best["se"]]
        pick = min(tied, key=lambda c: (c["epoch"], c["loss"]))
        out[run] = {"lr": pick["lr"], "epoch": pick["epoch"], "best_cell": best, "n_tied": len(tied), "cells": cells,
                    "excluded": {str(k): v for k, v in excluded.items()}}
    return out


def bootstrap3(runs, y, names, ref="lower", other="upper", ctrl="lower_lasttoken", n_boot=1000, seed=0):
    """The B2 bootstrap (long_stats.bootstrap) with AUC as a third metric: stratified resampling of the April test reports (the same resample for every run and seed);
    "ps" = mean over the seeds of each seed's own metric, "ens" = metric of the seed-averaged logit. Returns {run: {metric: {"ps"|"ens": {point, lo, hi, vs_lower, upper_minus, vs_ctrl}}}}."""
    from baseline.gap_final import roc_metrics
    keys = ("tpr@0.001", "tpr@0.01", "auc")
    y = np.asarray(y).astype(int)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    rng = np.random.default_rng(seed)
    Z = {n: np.mean([runs[n][s][1] for s in SEEDS], axis=0) for n in names}
    L = {n: [runs[n][s][1] for s in SEEDS] for n in names}
    draws = {k: {n: np.empty((n_boot, 3)) for n in names} for k in ("ens", "ps")}
    for b in range(n_boot):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        yb = y[idx]
        for n in names:
            draws["ens"][n][b] = roc_metrics(yb, Z[n][idx])
            draws["ps"][n][b] = np.mean([roc_metrics(yb, z[idx]) for z in L[n]], axis=0)
    point = {"ens": {n: roc_metrics(y, Z[n]) for n in names}, "ps": {n: np.mean([roc_metrics(y, z) for z in L[n]], axis=0) for n in names}}
    res = {}
    for n in names:
        res[n] = {}
        for j, k in enumerate(keys):
            res[n][k] = {}
            for kind in ("ens", "ps"):
                e = LS._ci(draws[kind][n][:, j], point[kind][n][j])
                if n != ref and ref in names:
                    e["vs_lower"] = LS._ci(draws[kind][n][:, j], point[kind][n][j], draws[kind][ref][:, j], point[kind][ref][j], +1)
                if ctrl in names and n.startswith("ar_lasttoken"):
                    e["vs_ctrl"] = LS._ci(draws[kind][n][:, j], point[kind][n][j], draws[kind][ctrl][:, j], point[kind][ctrl][j], +1)
                if n != other and other in names:
                    e["upper_minus"] = LS._ci(draws[kind][n][:, j], point[kind][n][j], draws[kind][other][:, j], point[kind][other][j], -1)
                res[n][k][kind] = e
    return res


def chosen_runs(R, choice, raw, y):
    """runs[name][seed] = (test metrics, test logits, {"test", "test_p32", ...}) at the chosen settings, in the format of long_stats."""
    runs = {}
    for run, ch in choice.items():
        if ch["lr"] is None or run not in RUNS:
            continue
        for s in SEEDS:
            z = np.load(os.path.join(raw, f"seed{s}", f"{run}_lr{ch['lr']:g}_test_logits.npy"))[ch["epoch"] - 1].astype(np.float64)
            m = C.binary_metrics(y, z, decision=0.0)
            m32 = C.binary_metrics(y, C.sigmoid32(z))
            d = R[run][ch["lr"]][s]
            runs.setdefault(run, {})[s] = (m, z, {"test": m, "test_p32": m32, "lr": ch["lr"], "epoch": ch["epoch"], "pretraining": d.get("pretraining"),
                                                   "val": d["per_epoch"][ch["epoch"] - 1]["val"]})
    return runs


def pm(v, d=3):
    v = np.asarray(v)
    return f"{v.mean():.{d}f} ± {v.std(ddof=1):.{d}f}"


def md(rows, header):
    return "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n" + "".join("| " + " | ".join(str(c) for c in r) + " |\n" for r in rows)


def pts(e):
    return f"{100 * e['point']:+.1f} [{100 * e['lo']:+.1f}, {100 * e['hi']:+.1f}]" + (" **resolved**" if e.get("resolved") else " not resolved")


def tables(R, choice, runs, boot, raw):
    B = boot["bootstrap"]
    L = ["#### Settings chosen on the validation slice (rule: NOTES.md 11.4)", ""]
    rows = []
    for run in RUNS:
        if run not in choice or choice[run]["lr"] is None:
            continue
        ch = choice[run]
        v = [c for c in ch["cells"] if c["lr"] == ch["lr"] and c["epoch"] == ch["epoch"]][0]
        rows.append([LABELS[run], f"{ch['lr']:g}", ch["epoch"], f"{v['m']:.3f} ± {v['se']:.3f} (SE)", f"{v['tpr@0.01']:.3f}", f"{v['auc']:.4f}", f"{v['loss']:.3f}",
                     ch["n_tied"], ", ".join(f"lr {k}: seeds {w}" for k, w in ch["excluded"].items()) or "none"])
    L.append(md(rows, ["run type", "lr", "epoch", "val TPR@1e-3", "val TPR@1e-2", "val AUC", "val loss", "cells tied", "collapsed"]))
    L += ["", "#### April test set at the chosen settings (logit-ranked; mean ± std over 5 seeds; bootstrap 95% CI of the per-seed mean)", ""]
    rows = []
    for run in RUNS:
        if run not in runs:
            continue
        g = lambda k, p32=False: np.array([(runs[run][s][2]["test_p32"] if p32 else runs[run][s][2]["test"])[k] for s in SEEDS])
        e3, e2 = B[run]["tpr@0.001"]["ps"], B[run]["tpr@0.01"]["ps"]
        rows.append([LABELS[run], pm(g("tpr@0.001")), f"[{100 * e3['lo']:.1f}, {100 * e3['hi']:.1f}]", pm(g("tpr@0.01")), f"[{100 * e2['lo']:.1f}, {100 * e2['hi']:.1f}]",
                     pm(g("auc"), 4), pm(g("f1@0.5")), pm(g("tpr@0.001", True))])
    L.append(md(rows, ["run", "TPR@1e-3", "95% CI (pts)", "TPR@1e-2", "95% CI (pts)", "AUC", "F1 (0.5)", "TPR@1e-3 literal float32"]))
    L += ["", "#### Paired per-seed differences in points (mean ± std over 5 seeds; positive in n of 5 seeds) and bootstrap 95% CI of the difference of the seed means", ""]
    pairs = [("upper − lower", "upper", "lower", "vs_lower"), ("AR − lower", "ar_lasttoken", "lower", "vs_lower"), ("MLM − lower", "mlm_bert", "lower", "vs_lower"),
             ("AR − its causal control", "ar_lasttoken", "lower_lasttoken", "vs_ctrl"), ("upper − AR", "ar_lasttoken", "upper", "upper_minus"),
             ("upper − MLM", "mlm_bert", "upper", "upper_minus")]
    rows = []
    for label, name, ref, kind in pairs:
        if name not in runs or ref not in runs:
            continue
        for k, kl in LS.METRICS:
            if label == "upper − lower":
                e = B["upper"][k]["ps"]["vs_lower"]
                d = LS.paired(runs, "upper", "lower")[k]
            elif kind == "upper_minus":
                e = B[name][k]["ps"]["upper_minus"]
                d = LS.paired(runs, name, "upper", sign=-1)[k]
            else:
                e = B[name][k]["ps"][kind]
                d = LS.paired(runs, name, ref)[k]
            if k == "auc":
                rows.append([label, kl, f"{100 * d['mean']:+.2f} ± {100 * d['std']:.2f}", f"{d['n_positive']}/5", pts(e)])
            else:
                rows.append([label, kl, f"{100 * d['mean']:+.1f} ± {100 * d['std']:.1f}", f"{d['n_positive']}/5", pts(e)])
    L.append(md(rows, ["difference", "metric", "per-seed mean ± std", "seeds > 0", "bootstrap 95% CI [pts]"]))
    L += ["", "(AUC differences are in points of AUC x 100.) Seed-ensemble flavour of the CI (mean logit over the 5 seeds) is in `bootstrap.json` (`ens`).", ""]
    return "\n".join(L)


def appendix(R, raw, y):
    """Full grid on test: NOT used for selection."""
    rows = []
    for run in RUNS:
        for lr in sorted(R.get(run, {}), reverse=True):
            cell = R[run][lr]
            if sorted(cell) != SEEDS:
                continue
            E = len(cell[0]["per_epoch"])
            for e in range(E):
                t = lambda k: np.array([cell[s]["per_epoch"][e]["test_NOT_FOR_SELECTION"][k] for s in SEEDS])
                rows.append([LABELS[run], f"{lr:g}", e + 1, pm(t("tpr@0.001")), pm(t("tpr@0.01")), pm(t("auc"), 4), pm(t("f1@0.5"))])
    return ("#### Appendix: the full grid on the April test set. **NOT used for selection** (every choice was made on the validation slice)\n\n"
            + md(rows, ["run", "lr", "epoch", "TPR@1e-3", "TPR@1e-2", "AUC", "F1 (0.5)"]))


def plot_val_curves(R, choice, plots):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    for ax, (key, title) in zip(axes, LS.METRICS):
        for run in RUNS:
            for lr, ls in ((2e-3, "-"), (1e-3, "--")):
                cell = R.get(run, {}).get(lr)
                if not cell or sorted(cell) != SEEDS or collapsed(cell):
                    continue
                v = val_curve(cell, key)
                x = np.arange(1, v.shape[1] + 1)
                ax.plot(x, v.mean(0), color=COLORS[run], ls=ls, lw=1.8, label=f"{LABELS[run]}, lr {lr:g}")
                ax.fill_between(x, v.mean(0) - v.std(0, ddof=1), v.mean(0) + v.std(0, ddof=1), color=COLORS[run], alpha=0.05)
                ch = choice.get(run, {})
                if ch.get("lr") == lr:
                    ax.plot([ch["epoch"]], [v.mean(0)[ch["epoch"] - 1]], marker="o", ms=9, mfc="none", mec="#222", mew=1.6)
        ax.set_xlabel("fine-tuning epoch"); ax.set_title(f"validation {title} (mean of 5 seeds)", loc="left", fontsize=10.5)
        ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=8, loc="center right")
    fig.text(0.01, 0.01, "Solid: lr 2e-3 (v2 recipe), dashed: lr 1e-3. Circle = setting chosen on validation. Bands: ± std over seeds. "
             "The validation slice has 2,467 benign reports (2 false alarms at FPR 1e-3): the left panel is noisy by design.", fontsize=7.5, color="#555")
    fig.tight_layout(rect=(0, 0.04, 0.76, 1)); fig.savefig(os.path.join(plots, "b3_val_curves.png"), dpi=160); plt.close(fig)


def plot_fig6(runs, choice, plots):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    styles = {"upper": "-", "ar_lasttoken": "--", "mlm_bert": "-.", "lower_lasttoken": ":", "lower": "-"}
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    for run in ["upper", "ar_lasttoken", "mlm_bert", "lower_lasttoken", "lower"]:
        if run not in runs:
            continue
        roc = np.mean([runs[run][s][2]["test"]["roc_on_grid"] for s in SEEDS], axis=0)
        ch = choice[run]
        ax.plot(C.ROC_GRID, roc, color=COLORS[run], ls=styles[run], lw=2, label=f"{LABELS[run]} (lr {ch['lr']:g}, ep {ch['epoch']})")
    ax.axvline(1e-3, color="#898782", lw=1, ls=":")
    ax.set_xscale("log"); ax.set_xlim(1e-4, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("Fig. 6 with the v2 recipe, April test set (mean ROC over 5 seeds)", loc="left", fontsize=10.5)
    ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    ax.legend(frameon=False, fontsize=7.5, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(plots, "fig6_v2.png"), dpi=160); plt.close(fig)


def val_report(R, choice):
    for run in RUNS:
        if run not in choice:
            continue
        ch = choice[run]
        print(f"\n{run}: chosen lr {ch['lr']} epoch {ch['epoch']} (tied cells {ch.get('n_tied')}), excluded (collapsed): {ch['excluded']}")
        for c in ch["cells"]:
            print(f"   lr {c['lr']:g} ep{c['epoch']}: val TPR@1e-3 {c['m']:.3f} ± {c['se']:.3f}  TPR@1e-2 {c['tpr@0.01']:.3f}  AUC {c['auc']:.4f}  loss {c['loss']:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="results/B3_selfsup_v2/raw")
    ap.add_argument("--out", default="results/B3_selfsup_v2")
    ap.add_argument("--plots", default="results/baseline/plots")
    ap.add_argument("--y", default="results/B_selfsup_long/y_test.npy")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--val-only", action="store_true")
    a = ap.parse_args()
    R = load(a.raw)
    choice = choose(R)
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.plots, exist_ok=True)
    val_report(R, choice)
    json.dump(choice, open(os.path.join(a.out, "choice.json"), "w"), indent=1)
    plot_val_curves(R, choice, a.plots)
    if a.val_only:
        return
    y = np.load(a.y).astype(int)
    runs = chosen_runs(R, choice, a.raw, y)
    missing = [r for r in RUNS if r not in runs]
    assert not missing, f"no chosen test results for {missing}"
    boot = {"n_boot": a.boot, "seeds": SEEDS, "bootstrap": bootstrap3(runs, y, [r for r in RUNS if r in runs], n_boot=a.boot)}
    json.dump(boot, open(os.path.join(a.out, "bootstrap.json"), "w"), indent=1)
    json.dump({r: {str(s): {"lr": runs[r][s][2]["lr"], "epoch": runs[r][s][2]["epoch"], "test": {k: v for k, v in runs[r][s][2]["test"].items() if k != "roc_on_grid"},
                            "test_p32_tpr@0.001": runs[r][s][2]["test_p32"]["tpr@0.001"], "val": runs[r][s][2]["val"]} for s in SEEDS} for r in runs},
              open(os.path.join(a.out, "chosen_metrics.json"), "w"), indent=1)
    for r in runs:
        os.makedirs(os.path.join(a.out, "test_logits", r), exist_ok=True)
        for s in SEEDS:
            np.save(os.path.join(a.out, "test_logits", r, f"seed{s}.npy"), runs[r][s][1].astype(np.float32))
    plot_fig6(runs, choice, a.plots)
    txt = tables(R, choice, runs, boot, a.raw) + "\n" + appendix(R, a.raw, y)
    open(os.path.join(a.out, "tables.md"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
