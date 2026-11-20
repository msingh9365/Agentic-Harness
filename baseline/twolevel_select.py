"""
Selection of the setting of A (init, lr, epoch) and of B (lr, epoch) from VALIDATION numbers only (NOTES 19.5, EVAL_PROTOCOL.md 4). It reads the per-seed run files (seed<k>.json) and never opens an April logit.

    python -m baseline.twolevel_select --runs <dir with the cell folders> --out results/attbal_2l

Rule: exclude a candidate in which ANY seed has validation AUC < 0.6 at that epoch (collapse guard); `best` = highest mean (over the 10 seeds) of validation pAUC@1e-2, SE = std (ddof 1) / sqrt(10);
tied = mean >= best - SE; among tied: fewest epochs, then lower lr, then (A only) scratch before warm.
"""
import argparse
import glob
import json
import os

import numpy as np

CELLS = {"A": [("A_scratch_lr1e-3", "scratch", 1e-3), ("A_scratch_lr2e-3", "scratch", 2e-3), ("A_warm_lr1e-3", "warm", 1e-3), ("A_warm_lr2e-3", "warm", 2e-3)],
         "B": [("B_lr1e-3", "scratch", 1e-3), ("B_lr2e-3", "scratch", 2e-3)]}
EPOCHS = (1, 2, 3)


def candidates(runs, model, seeds=range(10)):
    """runs: {cell tag: folder that contains <tag>/seed<k>.json}."""
    out = []
    for tag, init, lr in CELLS[model]:
        files = [os.path.join(runs[tag], tag, f"seed{s}.json") for s in seeds]
        if not all(os.path.exists(f) for f in files):
            raise SystemExit(f"{tag}: run files missing ({[os.path.basename(f) for f in files if not os.path.exists(f)]})")
        d = [json.load(open(f)) for f in files]
        for ep in EPOCHS:
            pa = np.array([x["per_epoch"][ep - 1]["val_pauc@1e-2"] for x in d])
            out.append({"model": model, "cell": tag, "init": init, "lr": lr, "epoch": ep, "mean": float(pa.mean()), "std": float(pa.std(ddof=1)), "se": float(pa.std(ddof=1) / np.sqrt(len(pa))),
                        "val_loss": float(np.mean([x["per_epoch"][ep - 1]["val_loss"] for x in d])), "min_val_auc": float(min(x["per_epoch"][ep - 1]["val_auc"] for x in d)),
                        "per_seed": pa.tolist()})
    return out


def select(cands):
    for c in cands:
        c["collapsed"] = c["min_val_auc"] < 0.6
    ok = [c for c in cands if not c["collapsed"]]
    if not ok:
        return None, cands
    best = max(ok, key=lambda c: c["mean"])
    for c in cands:
        c["tied"] = (not c["collapsed"]) and c["mean"] >= best["mean"] - best["se"]
    tied = [c for c in ok if c["tied"]]
    chosen = min(tied, key=lambda c: (c["epoch"], c["lr"], c["init"] != "scratch"))
    return {"best": (best["cell"], best["epoch"]), "chosen": chosen}, cands


def table(cands, best, chosen):
    rows = ["| cell | init | lr | epoch | mean val pAUC@1e-2 | SE | mean val loss | min val AUC | collapsed | within 1 SE of best |", "|---|---|---|---|---|---|---|---|---|---|"]
    for c in cands:
        mark = "**chosen**" if c is chosen else ("best" if (c["cell"], c["epoch"]) == best else ("yes" if c.get("tied") else ""))
        rows.append(f"| {c['cell']} | {c['init']} | {c['lr']:g} | {c['epoch']} | {c['mean']:.4f} | {c['se']:.4f} | {c['val_loss']:.4f} | {c['min_val_auc']:.4f} | {'yes' if c['collapsed'] else 'no'} | {mark} |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True, help="folders that contain the cell folders (searched in order)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    runs = {}
    for r in a.runs:
        for d in glob.glob(os.path.join(r, "*", "seed0.json")):
            runs.setdefault(os.path.basename(os.path.dirname(d)), os.path.dirname(os.path.dirname(d)))
    res, md = {}, ["# Selection from validation numbers only (NOTES 19.5)\n"]
    for m in ("A", "B"):
        missing = [t for t, _, _ in CELLS[m] if t not in runs]
        if missing:
            raise SystemExit(f"cells {missing} not found under {a.runs}")
        cands = candidates(runs, m)
        sel, cands = select(cands)
        if sel is None:
            res[m] = {"chosen": None, "note": "every candidate collapsed"}
            continue
        ch = sel["chosen"]
        res[m] = {"best": {"cell": sel["best"][0], "epoch": sel["best"][1]}, "chosen": {k: ch[k] for k in ("cell", "init", "lr", "epoch", "mean", "se")}, "candidates": [{k: v for k, v in c.items()} for c in cands]}
        md += [f"## Model {m}\n", table(cands, sel["best"], ch), f"\nCHOSEN {m}: cell={ch['cell']} init={ch['init']} lr={ch['lr']:g} epoch={ch['epoch']} (mean val pAUC@1e-2 {ch['mean']:.4f}, SE {ch['se']:.4f})\n"]
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(os.path.join(a.out, "selection.json"), "w"), indent=1)
    open(os.path.join(a.out, "validation_table.md"), "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
