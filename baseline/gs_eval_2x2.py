"""
April evaluation of the four 2 x 2 cells (head x padding) of NOTES 26 item 3 (same table format and rules as Stage I, baseline/gs_eval_i.py).   (OURS)

    python -m baseline.gs_eval_2x2 --runs <final outputs: x2f_fn/ x2f_ab/ x2f_an/ x2f_fb/> --epochs <chosen> --ref results/groupsplit/stage_fgh/stage_i/logits_fixed_models.npz --out results/groupsplit/stage_fgh/item3/eval

Cells: fn = flatten head, no padding; ab = attention head, balanced padding; an = attention head, no padding; fb = flatten head, balanced padding (all at ONE budget, corrected tokenizer, all of January, 10 seeds; April logits after the last epoch only).
Reference rows (descriptive; other budgets): the final M1 (flatten, none) and M3 (attention, balanced) of Stage I. Comparisons (both bootstraps, seeds each way; resolved = the cluster interval of pAUC@1e-2 excludes 0): the head effect without padding (an - fn), the head effect with
padding (ab - fb), the padding effect for the flatten head (fb - fn) and for the attention head (ab - an); the interaction (ab - an) - (fb - fn) with its cluster interval (the same resamples). STOP if any seed has an April AUC below 0.6.
"""
import argparse
import json
import os

import numpy as np

from baseline import common as C, gap_final, padtest
from baseline.twolevel_eval import april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
NAME = {"fn": "flatten head, no padding", "ab": "attention head, balanced padding", "an": "attention head, no padding", "fb": "flatten head, balanced padding", "r1": "M1 Nebula, Stage I (reference: lr 2e-3, 1 epoch)", "r3": "M3 ATT+bal, Stage I (reference: lr 1e-3, 3 epochs)"}


def load(runs, cell, epochs):
    t = f"x2f_{cell}"
    for s in SEEDS:
        have = sorted(int(f.split("_epoch")[1].split("_")[0]) for f in os.listdir(os.path.join(runs, t)) if f.startswith(f"seed{s}_epoch") and f.endswith("_test_logits.npy"))
        assert have == [epochs], (t, s, have)
        r = json.load(open(os.path.join(runs, t, f"seed{s}.json")))
        assert r["epochs"] == epochs and r["n_train"] == 75298 and r["tokenizer"] == "bpe50k_fix" and r["split_hash_asserted"], (t, s, r["epochs"], r["n_train"], r["tokenizer"])
    return np.stack([np.load(os.path.join(runs, t, f"seed{s}_epoch{epochs}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--ref", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    fam, hsh, groups = april_meta()
    assert len(set(groups)) == 2509 and len(y) == len(fam)
    test = {c: load(a.runs, c, a.epochs) for c in ("fn", "ab", "an", "fb")}
    from sklearn.metrics import roc_auc_score
    for k in test:
        assert test[k].shape == (10, len(y))
        aucs = [roc_auc_score(y, test[k][s]) for s in SEEDS]
        if min(aucs) < 0.6:
            raise SystemExit(f"STOP: cell {k} has a collapsed seed (April AUC {min(aucs):.3f} < 0.6)")
    if a.ref:
        z = np.load(a.ref)
        test["r1"], test["r3"] = z["f1_test"].astype(np.float64), z["f3_test"].astype(np.float64)
    order = [k for k in ("r1", "r3", "fn", "an", "fb", "ab") if k in test]
    lab = lambda k: ("**" + NAME[k] + "**") if k in ("fn", "an", "fb", "ab") else NAME[k]
    pairs = [("an", "fn"), ("ab", "fb"), ("fb", "fn"), ("ab", "an")] + ([("fn", "r1"), ("ab", "r3")] if a.ref else [])
    Z = {k: test[k] for k in order}
    T = {k: metrics_of(y, Z[k]) for k in Z}
    ens = {k: C.binary_metrics(y, Z[k].mean(0), decision=0.0) for k in Z}
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    L = ["### Clean April test, 10 seeds each, one evaluation per cell (NOTES 26 item 3, matched budget: " + f"{a.epochs} epoch(s)): per-seed mean ± std", "",
         md([[lab(k), len(T[k]["auc"])] + [ms(T[k][c], d) for c, _, d in COLS] for k in Z], ["cell", "n"] + [c[1] for c in COLS]), "", "10-seed ensembles (mean logit):", "",
         md([[lab(k), f"{ens[k]['tpr@0.001']:.3f}", f"{ens[k]['tpr@0.01']:.3f}", f"{ens[k]['auc']:.4f}", f"{ens[k]['f1@0.5']:.3f}", f"**{ens[k]['pauc@0.01']:.3f}**", f"{ens[k]['pauc@0.001']:.3f}"] for k in Z], ["cell", "TPR@1e-3", "TPR@1e-2", "AUC", "F1 (threshold 0.5)", "**pAUC@1e-2**", "pAUC@1e-3"]), "",
         "(TPR@1e-2 and TPR@1e-3 use thresholds set on the April benign scores; the F1 column is the F1 at the fixed threshold 0.5, NOTES 26 item 0.)", ""]
    rows, cl = [], {}
    names = {("an", "fn"): "head effect, no padding (attention - flatten)", ("ab", "fb"): "head effect, balanced padding (attention - flatten)", ("fb", "fn"): "padding effect, flatten head (balanced - none)", ("ab", "an"): "padding effect, attention head (balanced - none)",
             ("fn", "r1"): "descriptive: flatten/none at the matched budget - M1 (Stage I)", ("ab", "r3"): "descriptive: attention/balanced at the matched budget - M3 (Stage I)"}
    for (n, b) in pairs:
        for c, lbl, d in BOOT:
            dd = T[n][c] - T[b][c]
            ps = bs["ps"]["diffs"][f"{n} - {b}"][c]
            if c not in idx_of:
                continue
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[c]], [2.5, 97.5])
            res = ("**RESOLVED " + ("higher" if dd.mean() > 0 else "lower") + "**" if (lo > 0 or hi < 0) else "not resolved") if c == PRIMARY else ("cluster CI excludes 0 (descriptive)" if (lo > 0 or hi < 0) else "cluster CI contains 0 (descriptive)")
            cl[f"{n}-{b}|{c}"] = {"mean": float(dd.mean()), "strat_lo": float(ps["lo"]), "strat_hi": float(ps["hi"]), "cluster_lo": float(lo), "cluster_hi": float(hi), "seeds_up": int((dd > 0).sum()), "seeds_down": int((dd < 0).sum())}
            rows.append([names[(n, b)], lbl, f"{100 * dd.mean():+.2f}", f"[{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{int((dd > 0).sum())} up / {int((dd < 0).sum())} down", res])
    inter = cd[("ab", "an")][:, 3] - cd[("fb", "fn")][:, 3]
    ipt = float((T["ab"][PRIMARY].mean() - T["an"][PRIMARY].mean()) - (T["fb"][PRIMARY].mean() - T["fn"][PRIMARY].mean()))
    ilo, ihi = np.percentile(inter, [2.5, 97.5])
    cl["interaction|pauc@0.01"] = {"mean": ipt, "cluster_lo": float(ilo), "cluster_hi": float(ihi)}
    L += ["### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** Seeds are paired by index only.", "",
          md(rows, ["comparison", "metric", "mean difference", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome"]), "",
          f"**Interaction of head and padding on pAUC@1e-2**, (attention - flatten with padding) - (attention - flatten without padding) = (ab - an) - (fb - fn): {100 * ipt:+.2f} points, cluster 95% interval [{100 * ilo:+.2f}, {100 * ihi:+.2f}] ({'excludes 0' if (ilo > 0 or ihi < 0) else 'contains 0'}).", ""]
    thr = {k: np.array([padtest.thresholds(Z[k][s], y, 0.01) for s in SEEDS]) for k in Z}
    flag = {k: Z[k] > thr[k][:, None] for k in Z}
    frows = [[g, int((fam == g).sum())] + [f"{100 * flag[k][:, fam == g].mean(1).mean():.1f} ± {100 * flag[k][:, fam == g].mean(1).std(ddof=1):.1f}" for k in Z] for g in sorted(set(fam))]
    L += ["### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)", "", md(frows, ["family", "n"] + [lab(k) for k in Z])]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}, "ensemble": {k: {c: v for c, v in m_.items() if c != "roc_on_grid"} for k, m_ in ens.items()}, "pairs": cl},
              open(os.path.join(a.out, "results.json"), "w"))
    np.savez_compressed(os.path.join(a.out, "logits_2x2.npz"), **{f"{k}_test": test[k].astype(np.float32) for k in ("fn", "ab", "an", "fb")})
    print("\n".join(L))


if __name__ == "__main__":
    main()
