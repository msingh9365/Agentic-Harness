"""
ITEM R1, selection rule of NOTES 30.3 (CPU; validation numbers of January fold 9 only; no April file is opened).   (OURS)

    python -m baseline.r1_select --runs-a <out dir of r1sel_a> --runs-b <out dir of r1sel_b> --out results/groupsplit/r1

Candidates = variant (a / b) x epoch (1, 2, 3), 5 seeds each. Rule: (1) collapse guard: a candidate with any seed of validation AUC < 0.6 at that epoch is excluded; (2) R guard: among the remaining, a candidate whose mean
R20 or mean R100 is more than 0.02 below the best mean R20 / R100 of the remaining candidates is excluded; (3) `best` = highest mean validation pAUC@1e-2 (report-level, max over windows); SE = SD over the 5 seeds
(ddof 1) / sqrt(5) of `best`; candidates with a mean within one SE of `best` are tied; among the tied: fewest epochs, then lowest mean validation loss, then variant (a).
Writes choice.json (the choice and every candidate's numbers) and selection_tables.md. The validation numbers are read from <runs>/<tag>/seed<k>.json (written by baseline/r1.py in select mode).
"""
import argparse
import json
import os

import numpy as np

SEEDS = [0, 1, 2, 3, 4]
EPOCHS = [1, 2, 3]


def load(runs, tag):
    out = {}
    for s in SEEDS:
        r = json.load(open(os.path.join(runs, tag, f"seed{s}.json")))
        assert r["mode"] == "select" and r["split_hash_asserted"] and len(r["per_epoch"]) == len(EPOCHS), (tag, s)
        for rec in r["per_epoch"]:
            e = rec["epoch"]
            d = out.setdefault(e, {k: [] for k in ("pauc", "auc", "val_loss", "train_loss", "R20", "R100")})
            d["pauc"].append(rec["val"]["pauc@0.01"]); d["auc"].append(rec["val"]["auc"]); d["val_loss"].append(rec["val_loss"]); d["train_loss"].append(rec["train_loss"])
            d["R20"].append(rec["R20"]); d["R100"].append(rec["R100"])
    return {e: {k: np.array(v) for k, v in d.items()} for e, d in out.items()}


def select(cands, r_margin=0.02):
    """cands: {(variant, epoch): {metric: array over seeds}} -> (choice key or None, per-candidate info)"""
    info = {k: {"mean_pauc": float(v["pauc"].mean()), "sd_pauc": float(v["pauc"].std(ddof=1)), "mean_auc": float(v["auc"].mean()), "min_auc": float(v["auc"].min()), "mean_val_loss": float(v["val_loss"].mean()),
                "mean_R20": float(v["R20"].mean()), "mean_R100": float(v["R100"].mean()), "mean_train_loss": float(v["train_loss"].mean()), "excluded": None} for k, v in cands.items()}
    for k, v in cands.items():
        if v["auc"].min() < 0.6:
            info[k]["excluded"] = "collapse guard (a seed with validation AUC < 0.6)"
    alive = [k for k in cands if info[k]["excluded"] is None]
    if not alive:
        return None, info
    b20, b100 = max(info[k]["mean_R20"] for k in alive), max(info[k]["mean_R100"] for k in alive)
    for k in alive:
        if info[k]["mean_R20"] < b20 - r_margin or info[k]["mean_R100"] < b100 - r_margin:
            info[k]["excluded"] = f"R guard (best mean R20 {b20:.3f}, R100 {b100:.3f}; margin {r_margin})"
    alive = [k for k in cands if info[k]["excluded"] is None]
    best = max(alive, key=lambda k: info[k]["mean_pauc"])
    se = info[best]["sd_pauc"] / np.sqrt(len(cands[best]["pauc"]))
    tied = [k for k in alive if info[k]["mean_pauc"] >= info[best]["mean_pauc"] - se]
    for k in tied:
        info[k]["tied_with_best"] = True
    choice = sorted(tied, key=lambda k: (k[1], info[k]["mean_val_loss"], 0 if k[0] == "a" else 1))[0]
    info["_best"], info["_se_of_best"] = list(best), float(se)
    return choice, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs-a", required=True)
    ap.add_argument("--runs-b", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cands = {}
    for var, runs in (("a", a.runs_a), ("b", a.runs_b)):
        d = load(runs, f"r1sel_{var}")
        for e, v in d.items():
            cands[(var, e)] = v
    choice, info = select(cands)
    os.makedirs(a.out, exist_ok=True)
    res = {"choice": {"variant": choice[0], "epochs": choice[1]} if choice else None, "rule": "NOTES 30.3", "se_of_best": info.get("_se_of_best"), "best_candidate": info.get("_best"),
           "candidates": {f"{k[0]}_epoch{k[1]}": v for k, v in info.items() if isinstance(k, tuple)}}
    json.dump(res, open(os.path.join(a.out, "choice.json"), "w"), indent=1)
    L = ["### R1 selection on January fold 9 (5 seeds; validation only; no April)", "", "| variant | epoch | val pAUC@1e-2 (mean ± SD) | val AUC (min over seeds) | val loss | train loss | R20 | R100 | status |", "|---|---|---|---|---|---|---|---|---|"]
    for k in sorted(cands):
        i, v = info[k], cands[k]
        status = i["excluded"] or ("**CHOSEN**" if k == choice else ("tied" if i.get("tied_with_best") else "ok"))
        L.append(f"| {k[0]} | {k[1]} | {i['mean_pauc']:.4f} ± {i['sd_pauc']:.4f} | {i['min_auc']:.4f} | {i['mean_val_loss']:.4f} | {i['mean_train_loss']:.4f} | {i['mean_R20']:.3f} | {i['mean_R100']:.3f} | {status} |")
    L += ["", f"Choice: **variant ({choice[0]}), {choice[1]} epoch(s)**" if choice else "No candidate survived the guards: STOP.", ""]
    open(os.path.join(a.out, "selection_tables.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
