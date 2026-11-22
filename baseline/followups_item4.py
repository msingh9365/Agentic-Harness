"""
NOTES 26 item 4 (CPU, stored scores and logits): the malware-only padding models of the final M1 and M3 settings against the final M1 and M3.   (OURS)

    python -m baseline.followups_item4 --train-runs <malware-only padding training outputs: x2m_y_fm/ x2m_y_am/> --attack <attack scores dir of y_fm and y_am> --fixj <Stage J scores dir> --ref results/groupsplit/stage_fgh/stage_i/logits_fixed_models.npz --out <dir>

 * builds <out>/combined/ with scores_m1, scores_m3 (restricted to the edit sets of the new files, same order) and scores_y_fm, scores_y_am, ready for gs_attack_report.py and followups_ci.py;
 * the clean April metrics of the two new models (per-seed mean +- std, 10-seed ensembles; descriptive) next to the final M1 and M3, and the paired differences y_fm - M1 and y_am - M3 with both bootstraps (descriptive; resolved = the cluster interval of pAUC@1e-2 excludes 0).
STOP if a new model has a seed with April AUC < 0.6.
"""
import argparse
import json
import os

import numpy as np

from baseline import common as C, gap_final
from baseline.twolevel_eval import april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

SEEDS = list(range(10))


def load(runs, tag, epochs):
    for s in SEEDS:
        have = sorted(int(f.split("_epoch")[1].split("_")[0]) for f in os.listdir(os.path.join(runs, tag)) if f.startswith(f"seed{s}_epoch") and f.endswith("_test_logits.npy"))
        assert have == [epochs], (tag, s, have)
        r = json.load(open(os.path.join(runs, tag, f"seed{s}.json")))
        assert r["epochs"] == epochs and r["n_train"] == 75298 and r["tokenizer"] == "bpe50k_fix" and r["split_hash_asserted"] and r["pad_labels"] == "malware", (tag, s)
    return np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{epochs}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-runs", required=True)
    ap.add_argument("--attack", required=True)
    ap.add_argument("--fixj", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    _, _, groups = april_meta()
    Z = {"y_fm": load(a.train_runs, "x2m_y_fm", 1), "y_am": load(a.train_runs, "x2m_y_am", 3)}
    from sklearn.metrics import roc_auc_score
    for k, z in Z.items():
        if min(roc_auc_score(y, z[s]) for s in SEEDS) < 0.6:
            raise SystemExit(f"STOP: {k} has a collapsed seed (April AUC < 0.6)")
    ref = np.load(a.ref)
    Z = {"m1": ref["f1_test"].astype(np.float64), "y_fm": Z["y_fm"], "m3": ref["f3_test"].astype(np.float64), "y_am": Z["y_am"]}
    # combined scores directory
    comb = os.path.join(a.out, "combined")
    os.makedirs(comb, exist_ok=True)
    ref_names = [str(n) for n in np.load(os.path.join(a.attack, "scores_y_fm.npz"))["names"]]
    for fam in ("y_fm", "y_am"):
        d = np.load(os.path.join(a.attack, f"scores_{fam}.npz"))
        assert [str(n) for n in d["names"]] == ref_names
        np.savez_compressed(os.path.join(comb, f"scores_{fam}.npz"), **{k: d[k] for k in d.files})
    for fam in ("m1", "m3"):
        d = np.load(os.path.join(a.fixj, f"scores_{fam}.npz"))
        names = [str(n) for n in d["names"]]
        sel = [names.index(n) for n in ref_names]
        np.savez_compressed(os.path.join(comb, f"scores_{fam}.npz"), names=np.array(ref_names), tot=d["tot"][sel], **{f"seed{s}": d[f"seed{s}"][sel] for s in SEEDS})
    lab = {"m1": "M1 Nebula (final, no padding)", "y_fm": "M1 settings + malware-only padding", "m3": "M3 ATT+bal (final, balanced padding)", "y_am": "M3 settings + malware-only padding"}
    T = {k: metrics_of(y, Z[k]) for k in Z}
    ens = {k: C.binary_metrics(y, Z[k].mean(0), decision=0.0) for k in Z}
    pairs = [("y_fm", "m1"), ("y_am", "m3")]
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    L = ["### Item 4: clean April results of the malware-only padding models next to the final M1 and M3 (corrected tokenizer, 10 seeds; descriptive)", "",
         md([[lab[k], len(T[k]["auc"])] + [ms(T[k][c], d) for c, _, d in COLS] for k in Z], ["model", "n"] + [c[1] for c in COLS]), "", "10-seed ensembles:", "",
         md([[lab[k], f"{ens[k]['tpr@0.001']:.3f}", f"{ens[k]['tpr@0.01']:.3f}", f"{ens[k]['auc']:.4f}", f"{ens[k]['f1@0.5']:.3f}", f"**{ens[k]['pauc@0.01']:.3f}**", f"{ens[k]['pauc@0.001']:.3f}"] for k in Z], ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1 (threshold 0.5)", "**pAUC@1e-2**", "pAUC@1e-3"]), "", "### Paired differences (points ×100; stratified and cluster 95% CI; seeds paired by index only)", ""]
    rows = []
    for (n, b) in pairs:
        for c, lbl, d in BOOT:
            if c not in idx_of:
                continue
            dd = T[n][c] - T[b][c]
            ps = bs["ps"]["diffs"][f"{n} - {b}"][c]
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[c]], [2.5, 97.5])
            rows.append([f"{lab[n]} − {lab[b]}", lbl, f"{100 * dd.mean():+.2f}", f"[{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{int((dd > 0).sum())} up / {int((dd < 0).sum())} down",
                         ("**resolved**" if (lo > 0 or hi < 0) else "not resolved") if c == "pauc@0.01" else ""])
    L += [md(rows, ["difference", "metric", "mean difference", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome (pAUC only)"]), ""]
    open(os.path.join(a.out, "clean_tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}}, open(os.path.join(a.out, "clean_results.json"), "w"))
    np.savez_compressed(os.path.join(a.out, "logits_item4.npz"), y_fm_test=Z["y_fm"].astype(np.float32), y_am_test=Z["y_am"].astype(np.float32))
    print("\n".join(L))


if __name__ == "__main__":
    main()
