"""
Selection of the padded-training recipe of ATT+bal under EVAL_PROTOCOL.md section 4 (NOTES 16.4), from VALIDATION numbers only.   (OURS)

    python -m baseline.tune_select --make-reference                 # robustness of the existing ATT+bal on the fixed padded validation set (CPU, 10 models)
    python -m baseline.tune_select --runs results/tune              # table of the 16 candidates + the selection -> validation_table.md, selection.json

Input: results/tune/<tag>/seed<k>.json (per-epoch validation metrics, validation loss, validation robustness written by baseline/v2pe.py) and, for the reproduction check, the epoch-2 validation logits
of the cell (2e-3, 0.5). This script never opens an April logit.

Candidates: (lr, p, epoch) for lr in {1e-3, 2e-3}, p in {0.25, 0.5}, epoch 1..4. Rule (fixed in NOTES 16.4 before training):
 1. exclude a candidate in which any seed has validation AUC < 0.6 at that epoch;
 2. exclude a candidate whose mean validation robustness R is more than 0.02 below that of the existing ATT+bal (lr 2e-3, p 0.5, epoch 2; the 10 existing models on the same fixed padded validation set);
 3. best = highest mean validation pAUC@1e-2 among the rest; candidates within one SE of best (SE of best = std over seeds, ddof 1, / sqrt(10)) are tied; among tied: fewest epochs, then p = 0.5,
    then the lower mean validation loss, then the lower learning rate.
If nothing survives 1 and 2 the existing ATT+bal stays.
"""
import argparse
import glob
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELLS = [(1e-3, 0.25), (1e-3, 0.5), (2e-3, 0.25), (2e-3, 0.5)]
EPOCHS = [1, 2, 3, 4]
EXISTING = (2e-3, 0.5, 2)
ROBUST_MARGIN = 0.02


def tag_of(lr, p):
    return f"tune_lr{lr:.0e}_p{p:g}".replace("e-0", "e-")


def load_cell(runs, lr, p):
    """per-candidate arrays [seeds] for epochs 1..4 from the run files: pauc, auc, loss, robust."""
    fs = sorted(glob.glob(os.path.join(runs, tag_of(lr, p), "seed*.json")), key=lambda f: int(os.path.basename(f)[4:-5]))
    recs = [json.load(open(f)) for f in fs]
    out = {}
    for e in EPOCHS:
        rows = [r["per_epoch"][e - 1] for r in recs]
        out[e] = {"pauc": np.array([x["val"]["pauc@0.01"] for x in rows]), "auc": np.array([x["val"]["auc"] for x in rows]), "loss": np.array([x["val_loss"] for x in rows]),
                  "robust": np.array([x["val_robust_tpr"] for x in rows]), "seeds": [r["seed"] for r in recs]}
    return out


def select(cands, ref_robust, n_seeds=10):
    """cands: {(lr, p, epoch): {pauc, auc, loss, robust}} -> (table rows, chosen key or None). Pure function (unit-tested)."""
    rows = {}
    for k, c in cands.items():
        rows[k] = {"mean_pauc": float(c["pauc"].mean()), "se_pauc": float(c["pauc"].std(ddof=1) / np.sqrt(len(c["pauc"]))), "mean_robust": float(c["robust"].mean()), "mean_loss": float(c["loss"].mean()),
                   "min_auc": float(c["auc"].min()), "collapsed": bool((c["auc"] < 0.6).any())}
        rows[k]["robust_excluded"] = bool(rows[k]["mean_robust"] < ref_robust - ROBUST_MARGIN)
        rows[k]["eligible"] = not rows[k]["collapsed"] and not rows[k]["robust_excluded"]
    elig = [k for k in rows if rows[k]["eligible"]]
    if not elig:
        return rows, None, None
    best = max(elig, key=lambda k: rows[k]["mean_pauc"])
    thr = rows[best]["mean_pauc"] - rows[best]["se_pauc"]
    tied = [k for k in elig if rows[k]["mean_pauc"] >= thr]
    for k in rows:
        rows[k]["tied_with_best"] = k in tied
    chosen = min(tied, key=lambda k: (k[2], 0 if k[1] == 0.5 else 1, rows[k]["mean_loss"], k[0]))
    return rows, chosen, best


def make_reference(out_path):
    """Robustness of the 10 existing ATT+bal models (epoch 2) on the fixed padded validation set; thresholds from their stored epoch-2 validation logits."""
    import torch
    from baseline import callstore as CS, common as C, gap, inmem_pad, padtest
    C.setup_nebula(require_patched=True)
    torch.set_num_threads(4)
    store = CS.CallStore.load(os.path.join(ROOT, "results", "callstore", "all.npz"))
    lab = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))
    y_all = np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))["y_train"]
    trn, val = gap.val_slice(np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))["ym_train"])
    pool = inmem_pad.pool_rows_of(store, y_all, trn)
    rows, tok = inmem_pad.val_robust_set(store, y_all, val, pool)
    yv = y_all[val]
    res = {"per_seed": [], "pauc_per_seed": []}
    for s in range(10):
        m = padtest.load_model("attbal", os.path.join(ROOT, "results", "_attbal_raw2", "out", "attbal", f"seed{s}_epoch2_model.pt"), "cpu")
        zv = np.load(os.path.join(ROOT, "results", "att_bal", "attbal", f"seed{s}_epoch2_val_logits.npy")).reshape(-1)
        thr = padtest.thresholds(zv, yv, 0.01)
        zr = []
        with torch.no_grad():
            for i in range(0, len(tok), 256):
                zr.append(m(torch.as_tensor(tok[i:i + 256].astype(np.int64))).reshape(-1).numpy())
        zr = np.concatenate(zr)
        res["per_seed"].append(float((zr > thr).mean()))
        res["pauc_per_seed"].append(float(C.pauc(yv, zv)))
        print(f"existing ATT+bal seed {s}: validation R {res['per_seed'][-1]:.4f}, validation pAUC@1e-2 {res['pauc_per_seed'][-1]:.4f}", flush=True)
    res["mean_robust"] = float(np.mean(res["per_seed"]))
    res["n_malware"] = int(len(tok))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(res, open(out_path, "w"), indent=1)
    print("reference mean R:", res["mean_robust"])


def reproduction_check(runs):
    from baseline import common as C
    lab = np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))
    from baseline import gap
    _, val = gap.val_slice(lab["ym_train"])
    yv = lab["y_train"][val]
    d = []
    for s in range(10):
        a = np.load(os.path.join(runs, tag_of(2e-3, 0.5), f"seed{s}_epoch2_val_logits.npy")).reshape(-1)
        b = np.load(os.path.join(ROOT, "results", "att_bal", "attbal", f"seed{s}_epoch2_val_logits.npy")).reshape(-1)
        d.append(abs(C.pauc(yv, a) - C.pauc(yv, b)))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(ROOT, "results", "tune"))
    ap.add_argument("--make-reference", action="store_true")
    ap.add_argument("--reference", default=os.path.join(ROOT, "results", "tune", "reference_attbal.json"))
    a = ap.parse_args()
    if a.make_reference:
        return make_reference(a.reference)
    ref = json.load(open(a.reference))
    cands = {}
    for lr, p in CELLS:
        cell = load_cell(a.runs, lr, p)
        for e in EPOCHS:
            cands[(lr, p, e)] = cell[e]
    rows, chosen, best = select(cands, ref["mean_robust"])
    rep = reproduction_check(a.runs)
    reproduces = bool(max(rep) <= 0.002)
    L = [f"Reference robustness (existing ATT+bal, epoch 2, mean of 10 seeds): R = {ref['mean_robust']:.4f}; rule 2 excludes mean R < {ref['mean_robust'] - ROBUST_MARGIN:.4f}.", "",
         f"Reproduction check of the cell (2e-3, 0.5): largest per-seed difference of the epoch-2 validation pAUC@1e-2 against the stored ATT+bal = {max(rep):.4f} (criterion 0.002): {'reproduces' if reproduces else 'does NOT reproduce'}.", "",
         "| lr | p | epoch | mean val pAUC@1e-2 | SE | mean val robustness R | mean val loss | min val AUC | collapsed | R excluded | within 1 SE of best |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in sorted(rows, key=lambda k: (k[0], k[1], k[2])):
        r = rows[k]
        L.append(f"| {k[0]:g} | {k[1]:g} | {k[2]} | {r['mean_pauc']:.4f} | {r['se_pauc']:.4f} | {r['mean_robust']:.4f} | {r['mean_loss']:.4f} | {r['min_auc']:.4f} | {'yes' if r['collapsed'] else 'no'} | {'yes' if r['robust_excluded'] else 'no'} | "
                 f"{'**best**' if k == best else ('tied' if r.get('tied_with_best') else '')} |")
    L += ["", f"**Chosen (lr, p, epoch): {chosen}**" if chosen else "**No candidate survives rules 1 and 2: the existing ATT+bal stays.**"]
    text = "\n".join(L)
    open(os.path.join(a.runs, "validation_table.md"), "w").write(text + "\n")
    json.dump({"chosen": list(chosen) if chosen else None, "best": list(best) if best else None, "reproduces_existing": reproduces, "reproduction_max_diff": max(rep), "reference_robust": ref["mean_robust"],
               "rows": {f"{k[0]:g}|{k[1]:g}|{k[2]}": v for k, v in rows.items()}}, open(os.path.join(a.runs, "selection.json"), "w"), indent=1)
    print(text)


if __name__ == "__main__":
    main()
