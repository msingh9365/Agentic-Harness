"""
Validation guard of NOTES_ROPE.md section 2 (January fold 9, no April): reads <dir>/rg_<variant>[_lr..]/seed<k>.json of the guard kernel, applies the rule, writes guard.json and guard.md.

    python results/rope_test/guard_eval.py --dir <downloaded kernel output>  --out results/rope_test/guard
Rule: a variant COLLAPSES if the validation AUC of any of its seeds is below 0.8 after epoch 3, and DIVERGES if its mean validation loss after epoch 3 is above 3 x the stored M3 value on fold 9, epoch 3 (0.6298, results/groupsplit/epoch_study)
or is not finite. Either -> retry once at lr 5e-4 (that retry is judged by the same rule).
"""
import argparse
import glob
import json
import os

import numpy as np

M3_VAL_LOSS_F9_E3, M3_PAUC_F9_E3 = 0.6298, 0.4663          # stored epoch study, M3, fold 9, epoch 3 (mean of 5 seeds; results/groupsplit/epoch_study/results.json)
NAMES = {"rope_blocks": "V1 M3 + RoPE (blocks)", "rope_full": "V2 M3 + RoPE (full)", "sin_full": "V3 M3 + full attention"}


def load(d):
    out = {}
    for p in sorted(glob.glob(os.path.join(d, "**", "rg_*", "seed*.json"), recursive=True)):
        tag = os.path.basename(os.path.dirname(p))
        j = json.load(open(p))
        e3 = [e for e in j["per_epoch"] if e["epoch"] == 3][0]
        out.setdefault(tag, {})[j["seed"]] = {"val_auc": e3["val"]["auc"], "val_loss": e3["val_loss"], "val_pauc": e3["val"].get("pauc@0.01"), "tpr1": e3["val"].get("tpr@0.01"),
                                              "rand50_tpr": e3.get("study_rand50_tpr"), "rand50_benign_fpr": e3.get("study_rand50_benign_fpr"), "lgbm50_tpr": e3.get("study_lgbm50_tpr"),
                                              "all_epochs": [{"epoch": e["epoch"], "val_loss": e["val_loss"], "val_auc": e["val"]["auc"], "val_pauc": e["val"].get("pauc@0.01")} for e in j["per_epoch"]]}
    return out


def judge(runs):
    aucs = [r["val_auc"] for r in runs.values()]
    loss = float(np.mean([r["val_loss"] for r in runs.values()]))
    collapsed = bool(min(aucs) < 0.8)
    diverged = (not np.isfinite(loss)) or loss > 3 * M3_VAL_LOSS_F9_E3
    return {"seeds": sorted(runs), "min_val_auc": float(min(aucs)), "mean_val_loss": loss, "mean_val_pauc": float(np.mean([r["val_pauc"] for r in runs.values()])), "collapsed": collapsed, "diverged": bool(diverged),
            "retry_needed": bool(collapsed or diverged)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    runs = load(a.dir)
    res = {t: judge(r) for t, r in runs.items()}
    os.makedirs(a.out, exist_ok=True)
    json.dump({"reference_m3_fold9_epoch3": {"val_loss": M3_VAL_LOSS_F9_E3, "val_pauc": M3_PAUC_F9_E3}, "per_tag": res, "runs": runs}, open(os.path.join(a.out, "guard.json"), "w"), indent=1)
    md = ["| tag | seeds | min validation AUC | mean validation loss | mean validation pAUC@1e-2 | collapsed | diverged | retry needed |", "|---|---|---|---|---|---|---|---|"]
    for t, r in res.items():
        md.append(f"| {t} | {r['seeds']} | {r['min_val_auc']:.4f} | {r['mean_val_loss']:.4f} | {r['mean_val_pauc']:.4f} | {r['collapsed']} | {r['diverged']} | {r['retry_needed']} |")
    md.append(f"\nReference (stored epoch study, M3, fold 9, epoch 3, 5 seeds): validation loss {M3_VAL_LOSS_F9_E3}, validation pAUC@1e-2 {M3_PAUC_F9_E3}; divergence line = 3 x loss = {3 * M3_VAL_LOSS_F9_E3:.3f}.")
    open(os.path.join(a.out, "guard.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
