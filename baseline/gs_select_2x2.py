"""
NOTES 26 item 3: the ONE (learning rate, epochs) budget shared by the four cells of the 2 x 2 (head x padding), chosen from VALIDATION numbers only.   (OURS)

    python -m baseline.gs_select_2x2 --runs <grid outputs: x2g_<cell>_lr<lr>/ folders> --out results/groupsplit/stage_fgh/followups/item3

Candidates (lr, epochs) in {1e-3, 2e-3} x {1, 2, 3}; cells fn (flatten, none), ab (attention, balanced), an (attention, none), fb (flatten, balanced); group-split training part (66,580), validation slice (8,718), seeds 0-4.
Rule (fixed in NOTES 26 before any run): score of a candidate = the MEAN OVER THE FOUR CELLS of the mean validation pAUC@1e-2 (5 seeds); a candidate is excluded if any seed of any cell has validation AUC < 0.6;
best = the highest score; candidates within one SE of best (SE = std ddof 1 over the 5 per-seed scores, each the mean over the four cells, / sqrt(5), the SE of best) are tied; among tied: fewer epochs, then the lower lr.
Checks (STOP on failure): 5 seeds per run folder, split hash c3a2c99b..., 66,580 training reports, tokenizer bpe50k_fix, no April logit file in the outputs. This script never opens an April logit.
"""
import argparse
import glob
import json
import os

import numpy as np

CELLS, LRS, EPOCHS = ["fn", "ab", "an", "fb"], [1e-3, 2e-3], [1, 2, 3]
SPLIT_HASH = "c3a2c99bbf5dc6ddc60697e7b9468bf8"


def tag(cell, lr):
    return f"x2g_{cell}_lr{lr:.0e}".replace("e-0", "e-")


def select(rows):
    """rows: {(lr, epoch): {mean_score, se_score, min_auc, ...}} -> (rows with flags, chosen key or None, best key or None). Pure function (unit-tested)."""
    for r in rows.values():
        r["collapsed"] = bool(r["min_auc"] < 0.6)
    elig = [k for k in rows if not rows[k]["collapsed"]]
    for k in rows:
        rows[k]["eligible"], rows[k]["tied_with_best"] = k in elig, False
    if not elig:
        return rows, None, None
    best = max(elig, key=lambda k: rows[k]["mean_score"])
    thr = rows[best]["mean_score"] - rows[best]["se_score"]
    tied = [k for k in elig if rows[k]["mean_score"] >= thr]
    for k in tied:
        rows[k]["tied_with_best"] = True
    chosen = min(tied, key=lambda k: (k[1], k[0]))                 # fewer epochs, then the lower lr
    return rows, chosen, best


def load(runs, t):
    fs = sorted(glob.glob(os.path.join(runs, t, "seed*.json")), key=lambda f: int(os.path.basename(f)[4:-5]))
    recs = [json.load(open(f)) for f in fs]
    if [r["seed"] for r in recs] != [0, 1, 2, 3, 4]:
        raise SystemExit(f"STOP: {t}: expected seeds 0-4, found {[r['seed'] for r in recs]}")
    for r in recs:
        if r["split_hash_asserted"] is not True and r["split_hash_asserted"] != SPLIT_HASH:
            raise SystemExit(f"STOP: {t} seed {r['seed']}: split hash not asserted")
        if r["n_train"] != 66580 or r["tokenizer"] != "bpe50k_fix" or len(r["per_epoch"]) != 3:
            raise SystemExit(f"STOP: {t} seed {r['seed']}: training size / tokenizer / epochs not as expected ({r['n_train']}, {r['tokenizer']}, {len(r['per_epoch'])})")
    leak = glob.glob(os.path.join(runs, t, "*test_logits*"))
    if leak:
        raise SystemExit(f"STOP: April logit files exist in the grid outputs: {leak[:2]}")
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rows, per_cell = {}, {}
    data = {(c, lr): load(a.runs, tag(c, lr)) for c in CELLS for lr in LRS}
    for lr in LRS:
        for e in EPOCHS:
            P = np.array([[r["per_epoch"][e - 1]["val"]["pauc@0.01"] for r in data[(c, lr)]] for c in CELLS])            # [4 cells, 5 seeds]
            A = np.array([[r["per_epoch"][e - 1]["val"]["auc"] for r in data[(c, lr)]] for c in CELLS])
            L = np.array([[r["per_epoch"][e - 1]["val_loss"] for r in data[(c, lr)]] for c in CELLS])
            s = P.mean(0)                                                                                                    # per-seed score = mean over the four cells
            rows[(lr, e)] = {"mean_score": float(s.mean()), "se_score": float(s.std(ddof=1) / np.sqrt(len(s))), "min_auc": float(A.min()), "cell_pauc": P.mean(1).tolist(), "cell_min_auc": A.min(1).tolist(), "cell_val_loss": L.mean(1).tolist(), "score_per_seed": s.tolist()}
    rows, chosen, best = select(rows)
    if chosen is None:
        raise SystemExit("STOP: every candidate is excluded by the AUC guard")
    L = ["### Item 3 budget grid: validation numbers of all candidates (5 seeds; group-split slice, 8,718 reports; the cell numbers are descriptive)", "",
         "| lr | epochs | score = mean over the 4 cells of val pAUC@1e-2 | SE | min val AUC (all cells, seeds) | fn | ab | an | fb | note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in sorted(rows, key=lambda k: (k[0], k[1])):
        r = rows[k]
        note = " ".join(x for x in ["**CHOSEN**" if k == chosen else "", "best" if k == best else "", "tied" if r["tied_with_best"] and k not in (best, chosen) else "", "EXCLUDED (AUC guard)" if r["collapsed"] else ""] if x)
        L.append(f"| {k[0]:g} | {k[1]} | {r['mean_score']:.4f} | {r['se_score']:.4f} | {r['min_auc']:.4f} | " + " | ".join(f"{v:.4f}" for v in r["cell_pauc"]) + f" | {note} |")
    L += ["", f"**Chosen budget for all four cells: lr {chosen[0]:g}, {chosen[1]} epoch(s)** (best by score: lr {best[0]:g}, {best[1]} epoch(s), {rows[best]['mean_score']:.4f}, SE {rows[best]['se_score']:.4f}; tied with best: " + ", ".join(f"lr {k[0]:g}/{k[1]}" for k in rows if rows[k]["tied_with_best"]) + ")", ""]
    open(os.path.join(a.out, "validation_tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"chosen": {"lr": chosen[0], "epochs": chosen[1]}, "best": {"lr": best[0], "epochs": best[1]}, "rows": {f"{k[0]:g}|{k[1]}": v for k, v in rows.items()}}, open(os.path.join(a.out, "selection.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
