"""
NOTES 28 (epoch study), report (CPU, stored per-epoch validation numbers of baseline/epoch_study.py runs; January data only; no April file exists or is opened).   (OURS)

    python -m baseline.epoch_study_report --dirs <kernel output dirs> --out results/groupsplit/epoch_study [--summary results/groupsplit/epoch_study/readme_summary.md]

Writes tables.md and results.json (per model / cell, fold and epoch: mean +- std over seeds; mean over folds with +- 1 SE across folds; best epoch and one-SE bands), facts.md (the numbers behind the four questions
of NOTES 28.7), fig_epochs_M1_M4 and fig_epochs_2x2_fold9 (single-column 3.5 in and double-column 7.16 in; PDF and PNG 300 dpi; captions) and README.md (the plain-English summary file, if given, then the generated sections).
STOP (assert) if an April file or a weights file is found in any input directory, a (model, fold, seed, epoch) is missing, or a run json does not record the study fold, hash and the corrected tokenizer.
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline.paper_figs import COL, NAME

SEEDS = list(range(5))
FOLDS = [9, 4]
EPOCHS = [1, 2, 3, 4, 5]
CHOSEN = {"m1": 1, "m2": 1, "m3": 3, "m4": 1}
HASH = {9: "c3a2c99bbf5dc6ddc60697e7b9468bf8", 4: "357649ad3fa664517dc8e48262f93126"}
MODELS = [("m1", "M1"), ("m2", "M2"), ("m3", "M3"), ("m4", "M4")]
CELLS = [("fn", "flatten, no padding"), ("an", "attention, no padding"), ("fb", "flatten, balanced padding"), ("ab", "attention, balanced padding")]
CELL_COL = {"fn": "#0072B2", "an": "#CC79A7", "fb": "#E69F00", "ab": "#009E73"}
METRICS = [("train_loss", "training loss"), ("val_loss", "validation loss"), ("pauc", "val pAUC@1e-2"), ("tpr1e2", "val TPR@1e-2"), ("auc", "val AUC"), ("rand50_tpr", "random 50 prepend: detection"),
           ("rand50_fpr", "random 50 prepend: padded-benign FPR"), ("lgbm50_tpr", "LightGBM 50 prepend: detection")]


def parse_run(path, tag, seed):
    r = json.load(open(path))
    assert r["tokenizer"] == "bpe50k_fix" and r["study"] and r["study"]["fold"] == int(tag.split("_f")[-1]) and r["study"]["split_hash"] == HASH[r["study"]["fold"]], (tag, seed, "run json does not match the study")
    assert len(r["per_epoch"]) == len(EPOCHS), (tag, seed, len(r["per_epoch"]))
    lc = os.path.join(os.path.dirname(os.path.dirname(path)), "loss_curves", tag, f"seed{seed}.json")
    curve = json.load(open(lc))["per_epoch"] if os.path.exists(lc) else None
    out = {k: [] for k, _ in METRICS}
    for i, rec in enumerate(r["per_epoch"]):
        assert rec["epoch"] == i + 1
        out["train_loss"].append(rec["train_epoch_mean_loss"] if "train_epoch_mean_loss" in rec else curve[i]["train_epoch_mean_loss"])
        out["val_loss"].append(rec["val_loss"])
        out["pauc"].append(rec["val"]["pauc@0.01"])
        out["tpr1e2"].append(rec["val"]["tpr@0.01"])
        out["auc"].append(rec["val"]["auc"])
        out["rand50_tpr"].append(rec["study_rand50_tpr"])
        out["rand50_fpr"].append(rec["study_rand50_benign_fpr"])
        out["lgbm50_tpr"].append(rec["study_lgbm50_tpr"])
    return out


def load(dirs):
    data = {}
    for d in dirs:
        bad = glob.glob(os.path.join(d, "**", "*test_logits*"), recursive=True) + glob.glob(os.path.join(d, "**", "*_model.pt"), recursive=True)
        assert not bad, f"April / weights files found: {bad[:3]}"
        for p in sorted(glob.glob(os.path.join(d, "**", "es_*_f*", "seed*.json"), recursive=True)):
            if "loss_curves" in p:
                continue
            tag = os.path.basename(os.path.dirname(p))
            unit, fold = tag.split("_")[1], int(tag.split("_f")[-1])
            seed = int(os.path.basename(p)[4:-5])
            data.setdefault(unit, {}).setdefault(fold, {})[seed] = parse_run(p, tag, seed)
    out = {}
    for unit, folds in data.items():
        out[unit] = {}
        for fold, seeds in folds.items():
            out[unit][fold] = {m: np.array([seeds[s][m] for s in sorted(seeds)]) for m, _ in METRICS}      # [seeds, epochs]
            out[unit][fold]["seeds"] = sorted(seeds)
    return out


def get(data, key):
    """unit key of a figure line: the cell ab is the m3 runs on fold 9"""
    return data["m3"] if key == "ab" else data[key]


def band(vals, se, chosen_ok=None):
    """epochs whose mean >= best - SE(best)"""
    b = int(np.argmax(vals))
    return b + 1, [e + 1 for e in range(len(vals)) if vals[e] >= vals[b] - se[b]]


def fold_stats(arr):
    m, sd = arr.mean(0), arr.std(0, ddof=1) if arr.shape[0] > 1 else np.zeros(arr.shape[1])
    return m, sd, sd / np.sqrt(arr.shape[0])


def across(data_u, metric, folds):
    fm = np.stack([data_u[f][metric].mean(0) for f in folds])
    return fm.mean(0), (fm.std(0, ddof=1) / np.sqrt(len(folds)) if len(folds) > 1 else np.zeros(fm.shape[1])), fm


def table_for(name, du, folds, chosen):
    L = [f"#### {name}" + (f" (chosen epoch of the final model: {chosen})" if chosen else ""), ""]
    for f in folds:
        L += [f"fold {f}, mean ± SD over {du[f]['train_loss'].shape[0]} seeds:", "", "| epoch | " + " | ".join(lbl for _, lbl in METRICS) + " |", "|---|" + "---|" * len(METRICS)]
        for e in EPOCHS:
            row = []
            for m, _ in METRICS:
                mm, sd, _ = fold_stats(du[f][m])
                row.append(f"{mm[e - 1]:.4f} ± {sd[e - 1]:.4f}" if m in ("train_loss", "val_loss", "pauc", "auc") else f"{100 * mm[e - 1]:.1f} ± {100 * sd[e - 1]:.1f}")
            L.append(f"| {e}{' *' if chosen == e else ''} | " + " | ".join(row) + " |")
        L.append("")
    if len(folds) > 1:
        L += [f"mean over the {len(folds)} folds ± 1 SE across folds (SE = SD of the fold means / sqrt({len(folds)})):", "", "| epoch | " + " | ".join(lbl for _, lbl in METRICS) + " |", "|---|" + "---|" * len(METRICS)]
        for e in EPOCHS:
            row = []
            for m, _ in METRICS:
                mm, se, _ = across(du, m, folds)
                row.append(f"{mm[e - 1]:.4f} ± {se[e - 1]:.4f}" if m in ("train_loss", "val_loss", "pauc", "auc") else f"{100 * mm[e - 1]:.1f} ± {100 * se[e - 1]:.1f}")
            L.append(f"| {e}{' *' if chosen == e else ''} | " + " | ".join(row) + " |")
        L.append("")
    return L


def make_fig(items, folds_of, base, out, caption, band_note):
    """items: [(key, label, colour, chosen epoch)]; three panels; lines = mean over folds (or seeds) , bands = +-1 SE across folds (or seeds when there is one fold)."""
    from baseline.paper_figs import style, SC, DC
    plt = style()
    for width, suffix in ((SC, "_single_column"), (DC, "_double_column")):
        if width == SC:
            fig, axs = plt.subplots(3, 1, figsize=(SC, 6.3), sharex=True)
        else:
            fig, axs = plt.subplots(1, 3, figsize=(DC, 2.5))
        panels = [("loss", "loss (BCE)"), ("pauc", "validation pAUC@1e-2"), ("lgbm50_tpr", "validation detection,\nLightGBM 50 prepend (%)")]
        for ax, (kind, ylab) in zip(axs, panels):
            for key, label, col, chosen, du in items:
                folds = folds_of(key)
                mets = ["val_loss", "train_loss"] if kind == "loss" else [kind]
                for mi, m in enumerate(mets):
                    if len(folds) > 1:
                        mean, se, _ = across(du, m, folds)
                    else:
                        mean, _, se = fold_stats(du[folds[0]][m])
                    scale = 100 if kind == "lgbm50_tpr" else 1
                    ls = "-" if mi == 0 else (0, (3, 1.5))
                    ax.plot(EPOCHS, scale * mean, ls=ls, color=col, marker="o", ms=2.5, label=label if (kind == "pauc" or (kind == "loss" and mi == 0)) and ax is axs[1 if width == SC else 0] else None)
                    ax.fill_between(EPOCHS, scale * (mean - se), scale * (mean + se), color=col, alpha=0.15, lw=0)
                    if mi == 0 and chosen in EPOCHS:
                        ax.plot([chosen], [scale * mean[chosen - 1]], marker="D", ms=6, mfc="none", mec=col, mew=1.1, ls="none", zorder=5)
            ax.set_ylabel(ylab)
            ax.set_xticks(EPOCHS)
            if width != SC or ax is axs[-1]:
                ax.set_xlabel("epoch")
        axs[0].set_title("loss (solid: validation, dashed: training)" if width != SC else "loss (solid: validation, dashed: training)", fontsize=7)
        axs[1 if width == SC else 0].legend(fontsize=6.5, loc="best")
        os.makedirs(out, exist_ok=True)
        fig.savefig(os.path.join(out, base + suffix + ".pdf"))
        fig.savefig(os.path.join(out, base + suffix + ".png"), dpi=300)
        plt.close(fig)
    open(os.path.join(out, base + "_caption.txt"), "w").write(caption.strip() + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary", default=None)
    a = ap.parse_args()
    data = load(a.dirs)
    os.makedirs(a.out, exist_ok=True)
    folds_present = {u: sorted(data[u]) for u in data}
    for u in ("m1", "m2", "m3", "m4"):
        assert u in data and sorted(data[u]) == sorted(FOLDS), (u, folds_present.get(u))
        for f in FOLDS:
            assert data[u][f]["seeds"] == SEEDS, (u, f, data[u][f]["seeds"])
    for u in ("fn", "an", "fb"):
        assert u in data and data[u][9]["seeds"] == SEEDS, u
    folds = FOLDS
    L = ["# Epoch study: tables (NOTES 28; validation parts of the folds only; no April)", "", "Mean ± SD over 5 seeds per fold; mean over folds ± 1 SE across folds (two folds: weak, see NOTES 28.1). `*` = chosen epoch of the final model. Detection and padded-benign FPR in %. "
         "Training loss = mean BCE of the training batches of the epoch (dropout on; for M3, M4 and the balanced cells on the padded mix).", ""]
    res, facts = {}, []
    info = {}
    for key, name in MODELS:
        du = data[key]
        L += table_for(NAME[name], du, folds, CHOSEN[key])
        pa, se_a, fm = across(du, "pauc", folds)
        be, bd = band(pa, se_a)
        per = {}
        for f in folds:
            m, sd, se = fold_stats(du[f]["pauc"])
            bf, bandf = band(m, se)
            per[f] = {"best_epoch": bf, "band": bandf, "chosen_in_band": CHOSEN[key] in bandf, "peak_at_chosen": bf == CHOSEN[key], "pauc_by_epoch": m.round(4).tolist(), "se_by_epoch": se.round(4).tolist()}
        vl = {f: du[f]["val_loss"].mean(0) for f in folds}
        res[key] = {"chosen": CHOSEN[key], "across_folds": {"best_epoch": be, "band": bd, "chosen_in_band": CHOSEN[key] in bd, "pauc_mean": pa.round(4).tolist(), "se": se_a.round(4).tolist()}, "per_fold": per,
                    "val_loss_by_epoch": {f: vl[f].round(4).tolist() for f in folds}}
        L += [f"best epoch (mean over folds of val pAUC@1e-2): **{be}**; epochs within one SE of it (SE across folds {se_a[be - 1]:.4f}): {bd}; per fold: " + "; ".join(f"fold {f}: best {per[f]['best_epoch']}, band {per[f]['band']}" for f in folds), ""]
    for key, label in CELLS:
        du = get(data, key)
        L += table_for(f"2 x 2 cell: {label}" + (" (= M3 runs on fold 9)" if key == "ab" else ""), {9: du[9]}, [9], None)
        m, sd, se = fold_stats(du[9]["pauc"])
        bf, bandf = band(m, se)
        res["cell_" + key] = {"best_epoch": bf, "band": bandf, "pauc_by_epoch": m.round(4).tolist(), "se_by_epoch": se.round(4).tolist()}
        L += [f"best epoch (fold 9, mean over 5 seeds): **{bf}**; within one SE (SD/sqrt(5) of the best epoch): {bandf}", ""]
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    # facts for the four questions
    F = ["## Facts behind the four questions (computed by baseline/epoch_study_report.py)", "", "**Q1 peak of validation pAUC at the chosen epoch**", ""]
    for key, name in MODELS:
        F.append(f"- {NAME[name]} (chosen epoch {CHOSEN[key]}): " + "; ".join(f"fold {f}: best epoch {res[key]['per_fold'][f]['best_epoch']}" + (" (= chosen)" if res[key]['per_fold'][f]['peak_at_chosen'] else " (NOT the chosen epoch)") for f in folds) + f"; mean over folds: best epoch {res[key]['across_folds']['best_epoch']}")
    F += ["", "**Q2 validation loss after epoch 1** (mean over seeds, per fold; rises = the loss of every later epoch is above epoch 1)", ""]
    for key, name in MODELS:
        parts = []
        for f in folds:
            v = res[key]["val_loss_by_epoch"][f]
            parts.append(f"fold {f}: " + " / ".join(f"{x:.3f}" for x in v) + (" -> rises after epoch 1" if all(x > v[0] for x in v[1:]) else (" -> minimum at epoch " + str(int(np.argmin(v)) + 1)) if np.argmin(v) != 0 else " -> epoch 1 is the minimum but not every later epoch is above it"))
        F.append(f"- {NAME[name]}: " + "; ".join(parts))
    for key, label in CELLS:
        du = get(data, key)
        v = du[9]["val_loss"].mean(0)
        F.append(f"- cell {label} (fold 9): " + " / ".join(f"{x:.3f}" for x in v) + (" -> rises after epoch 1" if all(x > v[0] for x in v[1:]) else f" -> minimum at epoch {int(np.argmin(v)) + 1}"))
    F += ["", "**Q3 robustness over epochs of the padded models** (epoch 1 -> epoch 5; detection under LightGBM 50 prepend / random 50 prepend in points, padded-benign FPR at epoch 5, validation pAUC change)", ""]
    for key, label in [("m3", "M3 ATT+bal"), ("m4", "M4 ATT+bal-2L"), ("fb", "cell flatten, balanced"), ("ab", "cell attention, balanced"), ("m1", "M1 (no padding, for reference)"), ("m2", "M2 (no padding, for reference)")]:
        du = get(data, key)
        fl = [9] if key in ("fb", "ab") else folds
        for f in fl:
            g = lambda m: du[f][m].mean(0)
            F.append(f"- {label}, fold {f}: LightGBM 50: {100 * g('lgbm50_tpr')[0]:.1f} -> {100 * g('lgbm50_tpr')[4]:.1f} (by epoch: {', '.join(f'{100 * x:.1f}' for x in g('lgbm50_tpr'))}); random 50: {100 * g('rand50_tpr')[0]:.1f} -> {100 * g('rand50_tpr')[4]:.1f} (by epoch: {', '.join(f'{100 * x:.1f}' for x in g('rand50_tpr'))}); padded-benign FPR epoch 1 / 5: {100 * g('rand50_fpr')[0]:.2f} / {100 * g('rand50_fpr')[4]:.2f}; val pAUC {g('pauc')[0]:.3f} -> {g('pauc')[4]:.3f} (by epoch: {', '.join(f'{x:.3f}' for x in g('pauc'))})")
    F += ["", "**Q4 chosen epoch inside the one-SE band** (per fold: SE = SD over 5 seeds / sqrt(5) at the best epoch; across folds: SE of the two fold means)", ""]
    for key, name in MODELS:
        F.append(f"- {NAME[name]} (chosen {CHOSEN[key]}): " + "; ".join(f"fold {f}: band {res[key]['per_fold'][f]['band']} -> {'inside' if res[key]['per_fold'][f]['chosen_in_band'] else 'OUTSIDE'}" for f in folds) + f"; across folds: band {res[key]['across_folds']['band']} -> {'inside' if res[key]['across_folds']['chosen_in_band'] else 'OUTSIDE'}")
    open(os.path.join(a.out, "facts.md"), "w").write("\n".join(F) + "\n")
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    # figures
    items = [(key, NAME[name], COL[name], CHOSEN[key], data[key]) for key, name in MODELS]
    cap1 = ("Epoch study (validation parts of folds 9 and 4 only; no April data). Per epoch of 5-epoch runs with the learning rate and padding of the final models, 5 seeds per fold: (left or top) validation loss (solid) and training loss "
            "(dashed; for M3 and M4 on the padded training mix), (middle) validation pAUC at 1% FPR, (right or bottom) share of validation malware still detected at the 1% threshold after 50 LightGBM-chosen calls are prepended. "
            "Lines: mean over the two folds and five seeds; bands: ±1 SE across the two folds. Open diamonds mark the epoch chosen for each final model (M1 1, M2 1, M3 3, M4 1). Two folds make the bands rough.")
    make_fig(items, lambda k: folds, "fig_epochs_M1_M4", a.out, cap1, "folds")
    items2 = [(key, label, CELL_COL[key], {"fn": 1, "an": 3, "fb": 1, "ab": 3}[key], get(data, key)) for key, label in CELLS]
    cap2 = ("Epoch study of the 2 x 2 cells (head x padding) on fold 9 only; learning rate 1e-3 for all four cells, 5 seeds, validation part of fold 9 only, no April data. Panels as in Figure 1: validation (solid) and training (dashed) loss, "
            "validation pAUC at 1% FPR, validation detection under LightGBM 50 prepend. Lines: mean over five seeds; bands: ±1 SE across the five seeds (one fold). Open diamonds mark the epoch of the matching final model "
            "(flatten/none like M1: epoch 1; attention/balanced like M3: epoch 3; the cells without a final model use the epoch of their head type). The attention/balanced cell is the M3 run on fold 9.")
    make_fig(items2, lambda k: [9], "fig_epochs_2x2_fold9", a.out, cap2, "seeds")
    # README
    R = []
    if a.summary and os.path.exists(a.summary):
        R += [open(a.summary).read().strip(), ""]
    R += ["## Contents", "", "- `tables.md`: tables per model and fold (mean ± SD over seeds), mean over folds ± 1 SE across folds, best epochs and one-SE bands; `results.json`: the same numbers;",
          "- `facts.md`: the numbers behind the four questions; `folds.md`: the folds (NOTES 28.1);", "- `fig_epochs_M1_M4_{single,double}_column.{pdf,png}` + `fig_epochs_M1_M4_caption.txt`; `fig_epochs_2x2_fold9_{single,double}_column.{pdf,png}` + caption;",
          "- design and rules: NOTES 28 (written before any computation). **Diagnostic only. The final models are NOT changed by this study; any change needs the owner's approval after reading the results.**", ""]
    R += F
    open(os.path.join(a.out, "README.md"), "w").write("\n".join(R) + "\n")
    print("\n".join(F))


if __name__ == "__main__":
    main()
