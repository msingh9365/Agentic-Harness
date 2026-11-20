"""
Selection of the second-round recipe of A (NOTES 20) from VALIDATION numbers only. Reads the per-seed run files (seed<k>.json) of the six cells; never opens an April logit.

    python -m baseline.twolevel_select2 --runs <dirs with the cell folders> --out results/attbal_2l/round2

Candidates = cell x epoch (1, 2, 3) x weights (raw, EMA). Collapse guard: any seed with validation AUC < 0.6 excludes the candidate. best = highest mean (10 seeds) validation pAUC@1e-2, SE = std (ddof 1) / sqrt(10);
tied = mean >= best - SE; among tied: fewest epochs, then lower peak lr, then raw before EMA, then scratch before warm, then fewer extra mechanisms (decay, level-1 lr factor, freeze).
"""
import argparse
import glob
import json
import os

import numpy as np

CELLS = {  # tag: (init, peak lr, sched, level-1 lr factor, freeze steps)
    "R1_dec_lr1e-3": ("warm", 1e-3, "linear", 1.0, 0),
    "R2_dec_lr5e-4": ("warm", 5e-4, "linear", 1.0, 0),
    "R3_const_lr3e-4": ("warm", 3e-4, "const", 1.0, 0),
    "R4_dec_l1x0.25": ("warm", 1e-3, "linear", 0.25, 0),
    "R5_dec_freeze1ep": ("warm", 1e-3, "linear", 1.0, 706),
    "R6_dec_scratch": ("scratch", 1e-3, "linear", 1.0, 0),
}
EPOCHS = (1, 2, 3)


def candidates(runs, seeds=range(10)):
    out = []
    for tag, (init, lr, sched, l1, fr) in CELLS.items():
        files = [os.path.join(runs[tag], tag, f"seed{s}.json") for s in seeds]
        missing = [os.path.basename(f) for f in files if not os.path.exists(f)]
        if missing:
            raise SystemExit(f"{tag}: run files missing {missing}")
        d = [json.load(open(f)) for f in files]
        for ep in EPOCHS:
            for w in ("raw", "ema"):
                rec = [x["per_epoch"][ep - 1] if w == "raw" else x["per_epoch"][ep - 1]["ema"] for x in d]
                pa = np.array([r["val_pauc@1e-2"] for r in rec])
                out.append({"cell": tag, "init": init, "lr": lr, "sched": sched, "l1_mult": l1, "freeze": fr, "epoch": ep, "weights": w, "mean": float(pa.mean()), "std": float(pa.std(ddof=1)),
                            "se": float(pa.std(ddof=1) / np.sqrt(len(pa))), "val_loss": float(np.mean([r["val_loss"] for r in rec])), "min_val_auc": float(min(r["val_auc"] for r in rec)), "per_seed": pa.tolist()})
    return out


def select(cands):
    for c in cands:
        c["collapsed"] = c["min_val_auc"] < 0.6
    ok = [c for c in cands if not c["collapsed"]]
    if not ok:
        return None
    best = max(ok, key=lambda c: c["mean"])
    for c in cands:
        c["tied"] = (not c["collapsed"]) and c["mean"] >= best["mean"] - best["se"]
    tied = [c for c in ok if c["tied"]]
    chosen = min(tied, key=lambda c: (c["epoch"], c["lr"], c["weights"] == "ema", c["init"] != "scratch", (c["sched"] == "linear") + (c["l1_mult"] != 1.0) + (c["freeze"] > 0)))
    return best, chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    runs = {}
    for r in a.runs:
        for d in glob.glob(os.path.join(r, "*", "seed0.json")):
            runs.setdefault(os.path.basename(os.path.dirname(d)), os.path.dirname(os.path.dirname(d)))
    missing = [t for t in CELLS if t not in runs]
    if missing:
        raise SystemExit(f"cells {missing} not found under {a.runs}")
    cands = candidates(runs)
    sel = select(cands)
    if sel is None:
        raise SystemExit("every candidate collapsed")
    best, ch = sel
    rows = ["| cell | epoch | weights | mean val pAUC@1e-2 | SE | mean val loss | min val AUC | collapsed | within 1 SE of best |", "|---|---|---|---|---|---|---|---|---|"]
    for c in cands:
        mark = "**chosen**" if c is ch else ("best" if c is best else ("yes" if c["tied"] else ""))
        rows.append(f"| {c['cell']} | {c['epoch']} | {c['weights']} | {c['mean']:.4f} | {c['se']:.4f} | {c['val_loss']:.4f} | {c['min_val_auc']:.4f} | {'yes' if c['collapsed'] else 'no'} | {mark} |")
    text = "# Round 2: selection from validation numbers only (NOTES 20)\n\n" + "\n".join(rows) + f"\n\nCHOSEN: cell={ch['cell']} epoch={ch['epoch']} weights={ch['weights']} (mean val pAUC@1e-2 {ch['mean']:.4f}, SE {ch['se']:.4f}); best: {best['cell']} epoch {best['epoch']} {best['weights']} ({best['mean']:.4f})\n"
    os.makedirs(a.out, exist_ok=True)
    json.dump({"chosen": {k: ch[k] for k in ch if k != "per_seed"}, "best": {k: best[k] for k in best if k != "per_seed"}, "candidates": cands}, open(os.path.join(a.out, "selection.json"), "w"), indent=1)
    open(os.path.join(a.out, "validation_table.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    main()
