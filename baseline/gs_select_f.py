"""
Stage F of NOTES 23: selection of the M2 and M4 settings on the group-split validation slice, from VALIDATION numbers only.   (OURS)

    python -m baseline.gs_select_f --runs <Stage F outputs> --out results/groupsplit/stage_fgh/stage_f

Cells (5 seeds, 3 epochs, no April logit produced): M2 = two-level, no padding: fm2_lr1e-3, fm2_lr2e-3 (epoch 1-3 -> 6 candidates). M4 = two-level, balanced padding before chunking, p 0.5: fm4_{scratch,warm}_lr{1e-3,2e-3}
(epoch 1-3 -> 12 candidates; warm = level 1 initialised from the Step-3b ATT+bal of the same seed).
Rule (fixed in NOTES 23), per model separately: (1) AUC guard: a candidate in which any seed has validation AUC < 0.6 is excluded; (2) best = highest mean validation pAUC@1e-2; (3) candidates within one SE
of best (SE = std over the seeds, ddof 1, / sqrt(5), the SE of best) are tied; among tied: fewer epochs, then lower lr, then scratch before warm. R20 is reported, descriptive only.
Checks (NOTES 23, STOP on failure): 5 seeds per cell, split hash c3a2c99b..., 66,580 training reports, tokenizer bpe50k, no April logit file in the outputs, warm-start sha256 equal to the local file (when --weights-sha is given).
"""
import argparse
import glob
import json
import os

import numpy as np

EPOCHS = [1, 2, 3]
SPLIT_HASH = "c3a2c99bbf5dc6ddc60697e7b9468bf8"
CELLS = {"m2": [("fm2_lr1e-3", 1e-3, "scratch"), ("fm2_lr2e-3", 2e-3, "scratch")],
         "m4": [("fm4_scratch_lr1e-3", 1e-3, "scratch"), ("fm4_scratch_lr2e-3", 2e-3, "scratch"), ("fm4_warm_lr1e-3", 1e-3, "warm"), ("fm4_warm_lr2e-3", 2e-3, "warm")]}


def select(rows):
    """rows: {(tag, epoch): {mean_pauc, se_pauc, min_auc, mean_loss, lr, init}} -> (rows with flags, chosen key or None, best key or None). Pure function (unit-tested)."""
    for r in rows.values():
        r["collapsed"] = bool(r["min_auc"] < 0.6)
    elig = [k for k in rows if not rows[k]["collapsed"]]
    for k in rows:
        rows[k]["eligible"], rows[k]["tied_with_best"] = k in elig, False
    if not elig:
        return rows, None, None
    best = max(elig, key=lambda k: rows[k]["mean_pauc"])
    thr = rows[best]["mean_pauc"] - rows[best]["se_pauc"]
    tied = [k for k in elig if rows[k]["mean_pauc"] >= thr]
    for k in tied:
        rows[k]["tied_with_best"] = True
    chosen = min(tied, key=lambda k: (k[1], rows[k]["lr"], 0 if rows[k]["init"] == "scratch" else 1))
    return rows, chosen, best


def load_cell(runs, tag):
    fs = sorted(glob.glob(os.path.join(runs, tag, "seed*.json")), key=lambda f: int(os.path.basename(f)[4:-5]))
    recs = [json.load(open(f)) for f in fs]
    if len(recs) != 5 or [r["seed"] for r in recs] != [0, 1, 2, 3, 4]:
        raise SystemExit(f"STOP: {tag}: expected seeds 0-4, found {[r['seed'] for r in recs]}")
    for r in recs:
        if r["split_hash_asserted"] != SPLIT_HASH or r["n_train"] != 66580 or r["tokenizer"] != "bpe50k" or r["full_january"] or len(r["per_epoch"]) != 3:
            raise SystemExit(f"STOP: {tag} seed {r['seed']}: split hash / training size / tokenizer / epochs not as expected")
    leak = glob.glob(os.path.join(runs, tag, "*test_logits*"))
    if leak:
        raise SystemExit(f"STOP: April logit files exist in Stage F outputs: {leak[:2]}")
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", default="results/groupsplit/stage_fgh/stage_f")
    ap.add_argument("--weights-sha", default=None, help="results/groupsplit/stage_fgh/weights_sha256.json: warm-start files must equal the local Step-3b weights")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    sha = json.load(open(a.weights_sha))["gs-3b-attbal-weights"] if a.weights_sha else None
    result, text = {}, []
    for model, cells in CELLS.items():
        rows, curves = {}, {}
        for tag, lr, init in cells:
            recs = load_cell(a.runs, tag)
            if init == "warm" and sha:
                for r in recs:
                    got, want = r["warm_start"]["sha256"], sha[f"seed{r['seed']}.pt"]
                    if got != want or r["warm_start"]["level1_keys_loaded"] != 27:
                        raise SystemExit(f"STOP: {tag} seed {r['seed']}: warm start did not load the intended Step-3b weights ({got[:12]} vs {want[:12]})")
            for e in EPOCHS:
                pe = [r["per_epoch"][e - 1] for r in recs]
                p, au = np.array([x["val_pauc@1e-2"] for x in pe]), np.array([x["val_auc"] for x in pe])
                rows[(tag, e)] = {"lr": lr, "init": init, "mean_pauc": float(p.mean()), "se_pauc": float(p.std(ddof=1) / np.sqrt(len(p))), "mean_auc": float(au.mean()), "min_auc": float(au.min()), "mean_loss": float(np.mean([x["val_loss"] for x in pe])),
                                  "mean_train_loss": float(np.mean([x["train_epoch_mean_loss"] for x in pe])), "mean_r20": float(np.mean([x["val_robust_tpr"] for x in pe])), "pauc_per_seed": p.tolist()}
        rows, chosen, best = select(rows)
        if chosen is None:
            raise SystemExit(f"STOP: every candidate of {model} is excluded by the AUC guard")
        L = [f"### {model.upper()}: validation numbers of all candidates (5 seeds; group-split slice, 8,718 reports)", "", "| cell | lr | init | epoch | val pAUC@1e-2 | SE | val AUC (min over seeds) | val loss | train loss | R20 (descriptive) | note |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for k in sorted(rows, key=lambda k: (k[0], k[1])):
            r = rows[k]
            note = " ".join(x for x in ["**CHOSEN**" if k == chosen else "", "best" if k == best else "", "tied" if r["tied_with_best"] and k not in (best, chosen) else "", "EXCLUDED (AUC guard)" if r["collapsed"] else ""] if x)
            L.append(f"| {k[0]} | {r['lr']:g} | {r['init']} | {k[1]} | {r['mean_pauc']:.4f} | {r['se_pauc']:.4f} | {r['min_auc']:.4f} | {r['mean_loss']:.3f} | {r['mean_train_loss']:.4f} | {r['mean_r20']:.4f} | {note} |")
        L += ["", f"**Chosen for {model.upper()}: {chosen[0]}, epoch {chosen[1]}** (lr {rows[chosen]['lr']:g}, init {rows[chosen]['init']}); best by mean validation pAUC@1e-2: {best[0]} epoch {best[1]} ({rows[best]['mean_pauc']:.4f}, SE {rows[best]['se_pauc']:.4f}); tied with best: " + ", ".join(f"{k[0]}/{k[1]}" for k in rows if rows[k]["tied_with_best"]), ""]
        text += L
        result[model] = {"chosen": {"cell": chosen[0], "epoch": chosen[1], "lr": rows[chosen]["lr"], "init": rows[chosen]["init"]}, "best": {"cell": best[0], "epoch": best[1]}, "rows": {f"{k[0]}|{k[1]}": v for k, v in rows.items()}}
    open(os.path.join(a.out, "validation_tables.md"), "w").write("\n".join(text) + "\n")
    json.dump(result, open(os.path.join(a.out, "selection.json"), "w"), indent=1)
    print("\n".join(text))


if __name__ == "__main__":
    main()
