"""
Stage B of NOTES 21: the choices of v2-PE and ATT+bal on the group-split validation slice, from VALIDATION numbers only.   (OURS)

    python -m baseline.gs_select --runs <dir with gs_v2pe_lr*/ gs_attbal_lr*_p*/ loss_curves/> --out results/groupsplit/stage_b

Input per candidate cell: `<runs>/<tag>/seed<k>.json` (per-epoch validation metrics, validation loss, validation robustness R at 20 and 100 prepended calls, written by baseline/v2pe.py),
`<runs>/<tag>/seed<k>_epoch<e>_val_logits.npy` (for the per-family numbers) and `<runs>/loss_curves/<tag>/seed<k>.json` (per-epoch training loss and validation loss, written with --loss-log).
This script never opens an April logit (none is produced in Stage B).

Candidates: v2-PE (lr in {1e-3, 2e-3, 3e-3}) x epoch 1..4 = 12; ATT+bal (lr in {1e-3, 2e-3}) x (padding probability p in {0.25, 0.5}) x epoch 1..4 = 16; 5 seeds (0-4). Rule (NOTES 21, Stage B):
 1. exclude a candidate in which any seed has validation AUC < 0.6 at that epoch (collapse guard);
 2. ATT+bal only: for each of the two robustness measures R20 and R100, best R = the highest mean R over the candidates that passed rule 1; exclude a candidate whose mean R is more than 0.02 below the best
    (either of the two);
 3. best = highest mean validation pAUC@1e-2 among the rest; candidates within one SE of best (SE = std over the 5 seeds, ddof 1, / sqrt(5), the SE of best) are tied; among tied: fewest epochs,
    then the lower mean validation loss, then the lower learning rate.
Per-family validation metrics (pAUC@1e-2 of the benign validation reports against one family, and the share of the family above the overall 1% FPR threshold) are DESCRIPTIVE only and take no part in the selection.
"""
import argparse
import glob
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2_LRS, AB_LRS, AB_PS, EPOCHS = [1e-3, 2e-3, 3e-3], [1e-3, 2e-3], [0.25, 0.5], [1, 2, 3, 4]
OLD_V2, OLD_AB = (2e-3, 2), (2e-3, 0.5, 2)
ROBUST_MARGIN = 0.02
FAMILIES = ["backdoor", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan"]


def tag_v2(lr):
    return f"gs_v2pe_lr{lr:.0e}".replace("e-0", "e-")


def tag_ab(lr, p):
    return f"gs_attbal_lr{lr:.0e}_p{p:g}".replace("e-0", "e-")


def select(rows, with_robust):
    """rows: {key: {mean_pauc, se_pauc, mean_loss, min_auc, [mean_r20, mean_r100]}} where key = (lr, epoch) or (lr, p, epoch). Adds the rule flags; returns (rows, chosen key or None, best key or None). Pure function (unit-tested)."""
    for r in rows.values():
        r["collapsed"] = bool(r["min_auc"] < 0.6)
    ok = [k for k in rows if not rows[k]["collapsed"]]
    if with_robust and ok:
        best_r = {m: max(rows[k][m] for k in ok) for m in ("mean_r20", "mean_r100")}
        for k in rows:
            rows[k]["robust_excluded"] = bool(any(rows[k][m] < best_r[m] - ROBUST_MARGIN for m in best_r))
    else:
        for k in rows:
            rows[k]["robust_excluded"] = False
    elig = [k for k in rows if not rows[k]["collapsed"] and not rows[k]["robust_excluded"]]
    for k in rows:
        rows[k]["eligible"], rows[k]["tied_with_best"] = k in elig, False
    if not elig:
        return rows, None, None
    best = max(elig, key=lambda k: rows[k]["mean_pauc"])
    thr = rows[best]["mean_pauc"] - rows[best]["se_pauc"]
    tied = [k for k in elig if rows[k]["mean_pauc"] >= thr]
    for k in tied:
        rows[k]["tied_with_best"] = True
    chosen = min(tied, key=lambda k: (k[-1], rows[k]["mean_loss"], k[0]))
    return rows, chosen, best


def load_cell(runs, tag):
    fs = sorted(glob.glob(os.path.join(runs, tag, "seed*.json")), key=lambda f: int(os.path.basename(f)[4:-5]))
    recs = [json.load(open(f)) for f in fs]
    cur = {}
    for r in recs:
        f = os.path.join(runs, "loss_curves", tag, f"seed{r['seed']}.json")
        cur[r["seed"]] = json.load(open(f)) if os.path.exists(f) else None
    out = {}
    for e in EPOCHS:
        rows = [r["per_epoch"][e - 1] for r in recs]
        c = {"seeds": [r["seed"] for r in recs], "pauc": np.array([x["val"]["pauc@0.01"] for x in rows]), "auc": np.array([x["val"]["auc"] for x in rows]), "loss": np.array([x["val_loss"] for x in rows]),
             "tpr01": np.array([x["val"]["tpr@0.01"] for x in rows]), "tpr001": np.array([x["val"]["tpr@0.001"] for x in rows])}
        if "val_robust_tpr" in rows[0]:
            c["r20"], c["r100"] = np.array([x["val_robust_tpr"] for x in rows]), np.array([x["val_robust100_tpr"] for x in rows])
        if all(v is not None for v in cur.values()):
            c["train_loss"] = np.array([cur[r["seed"]]["per_epoch"][e - 1]["train_epoch_mean_loss"] for r in recs])
            c["train_clean_loss"] = np.array([cur[r["seed"]]["per_epoch"][e - 1]["train_subset_clean_loss"] for r in recs])
        out[e] = c
    return out


def row_of(c, with_robust):
    n = len(c["pauc"])
    r = {"n_seeds": n, "mean_pauc": float(c["pauc"].mean()), "se_pauc": float(c["pauc"].std(ddof=1) / np.sqrt(n)), "mean_loss": float(c["loss"].mean()), "min_auc": float(c["auc"].min()),
         "mean_tpr01": float(c["tpr01"].mean()), "mean_tpr001": float(c["tpr001"].mean())}
    if "train_loss" in c:
        r["mean_train_loss"], r["mean_train_clean_loss"] = float(c["train_loss"].mean()), float(c["train_clean_loss"].mean())
    if with_robust:
        r["mean_r20"], r["mean_r100"] = float(c["r20"].mean()), float(c["r100"].mean())
    return r


def family_numbers(runs, tag, epoch, seeds, fam_val, y_val):
    """per-seed descriptive numbers of one candidate: {family: [pAUC@1e-2 per seed]}, {family: [share above the overall 1% FPR threshold per seed]} from the stored validation logits."""
    from baseline import common as C
    from baseline.padtest import thresholds
    pa, tp = {f: [] for f in FAMILIES}, {f: [] for f in FAMILIES}
    for s in seeds:
        z = np.load(os.path.join(runs, tag, f"seed{s}_epoch{epoch}_val_logits.npy")).reshape(-1)
        thr = thresholds(z, y_val, 0.01)
        for f in FAMILIES:
            m = (y_val == 0) | (fam_val == f)
            pa[f].append(float(C.pauc(y_val[m], z[m])))
            tp[f].append(float((z[fam_val == f] > thr).mean()))
    return pa, tp


def val_families():
    from baseline import groupsplit as G
    jt = G.january_table()
    trn, val = G.val_slice()
    fam = jt["train"]["family"][val]
    y = np.isin(fam, FAMILIES).astype(int)
    return fam, y


def md_table(rows, keys, with_robust, best, chosen, old):
    h = ["lr"] + (["p"] if len(keys[0]) == 3 else []) + ["epoch", "val pAUC@1e-2", "SE", "val loss", "train loss"] + (["R20", "R100"] if with_robust else []) + ["min val AUC", "collapsed"] + (["R excluded"] if with_robust else []) + ["note"]
    L = ["| " + " | ".join(h) + " |", "|" + "---|" * len(h)]
    for k in keys:
        r = rows[k]
        note = " ".join(x for x in ["**chosen**" if k == chosen else "", "best" if k == best else "", "tied" if r["tied_with_best"] and k not in (best, chosen) else "", "old setting" if k == old else ""] if x)
        cells = [f"{k[0]:g}"] + ([f"{k[1]:g}"] if len(k) == 3 else []) + [k[-1], f"{r['mean_pauc']:.4f}", f"{r['se_pauc']:.4f}", f"{r['mean_loss']:.4f}", f"{r.get('mean_train_loss', float('nan')):.4f}"] + \
                ([f"{r['mean_r20']:.4f}", f"{r['mean_r100']:.4f}"] if with_robust else []) + [f"{r['min_auc']:.4f}", "yes" if r["collapsed"] else "no"] + (["yes" if r["robust_excluded"] else "no"] if with_robust else []) + [note]
        L.append("| " + " | ".join(str(c) for c in cells) + " |")
    return "\n".join(L)


def figure(curves, chosen, old, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4), dpi=200, sharex=True)
    cm = plt.get_cmap("tab20")
    for i, (k, c) in enumerate(sorted(curves.items())):
        lab = ",".join(f"{x:g}" for x in k)
        ls, lw = ("-", 2.2) if k == chosen[:-1] else (("--", 1.6) if k == old[:-1] else ("-", 0.9))
        ax[0].plot(EPOCHS, c["train"], ls, lw=lw, color=cm(i % 20), label=lab)
        ax[1].plot(EPOCHS, c["val"], ls, lw=lw, color=cm(i % 20), label=lab)
    ax[0].set_title("training loss (mean of the epoch's batches)")
    ax[1].set_title("validation loss (group-split slice)")
    for a in ax:
        a.set_xlabel("epoch")
        a.set_xticks(EPOCHS)
        a.spines[["top", "right"]].set_visible(False)
    ax[1].legend(fontsize=6.5, frameon=False, title="lr[,p]", title_fontsize=7, ncol=2)
    fig.suptitle(title + " (thick = chosen, dashed = old setting)", fontsize=9)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "groupsplit", "stage_b"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fam_val, y_val = val_families()
    result, text = {}, []
    for name, cells, with_robust, old in [("v2pe", [(tag_v2(lr), (lr,)) for lr in V2_LRS], False, OLD_V2), ("attbal", [(tag_ab(lr, p), (lr, p)) for lr in AB_LRS for p in AB_PS], True, OLD_AB)]:
        cands, rows, curves = {}, {}, {}
        for tag, key in cells:
            cell = load_cell(a.runs, tag)
            for e in EPOCHS:
                cands[key + (e,)] = (tag, cell[e])
                rows[key + (e,)] = row_of(cell[e], with_robust)
        rows, chosen, best = select(rows, with_robust)
        keys = sorted(rows)
        for k in keys:
            tag, c = cands[k]
            curves.setdefault(k[:-1], {"train": [], "val": []})
            curves[k[:-1]]["train"].append(rows[k].get("mean_train_loss", np.nan))
            curves[k[:-1]]["val"].append(rows[k]["mean_loss"])
        sel = list(dict.fromkeys(k for k in (chosen, old) if k is not None))
        fam = {}
        for k in sel:
            tag, c = cands[k]
            pa, tp = family_numbers(a.runs, tag, k[-1], c["seeds"], fam_val, y_val)
            fam["|".join(f"{x:g}" for x in k)] = {"pauc_per_seed": pa, "share_above_1pct_fpr_threshold_per_seed": tp}
        ft = ["| family | validation reports | " + " | ".join(("chosen " if k == chosen else "old setting ") + str(tuple(k)) + " pAUC@1e-2 | share flagged at 1% FPR" for k in sel) + " |", "|" + "---|" * (2 + 2 * len(sel))]
        for f in FAMILIES:
            cells_ = []
            for k in sel:
                v = fam["|".join(f"{x:g}" for x in k)]
                cells_ += [f"{np.mean(v['pauc_per_seed'][f]):.3f} ± {np.std(v['pauc_per_seed'][f], ddof=1):.3f}", f"{np.mean(v['share_above_1pct_fpr_threshold_per_seed'][f]):.3f}"]
            ft.append(f"| {f}{' (ONE group)' if f == 'rat' else ''} | {int((fam_val == f).sum()):,} | " + " | ".join(cells_) + " |")
        result[name] = {"chosen": list(chosen) if chosen else None, "best": list(best) if best else None, "old_setting": list(old), "rows": {"|".join(f"{x:g}" for x in k): v for k, v in rows.items()}, "per_family": fam}
        text += [f"### {name}", "", md_table(rows, keys, with_robust, best, chosen, old), "", f"**Chosen: {tuple(chosen) if chosen else None}**; best by mean validation pAUC@1e-2: {tuple(best) if best else None}; old setting {old}.", "",
                 "Per-family validation numbers (descriptive only; 5 seeds, mean ± SD; the rat reports of this slice come from a single group):", "", "\n".join(ft), ""]
        if chosen:
            figure(curves, chosen, old, os.path.join(a.out, f"fig_loss_curves_{name}.png"), f"{name}: loss per epoch, all candidates")
    open(os.path.join(a.out, "validation_tables.md"), "w").write("\n".join(text) + "\n")
    json.dump(result, open(os.path.join(a.out, "selection.json"), "w"), indent=1)
    print("\n".join(text))


if __name__ == "__main__":
    main()
