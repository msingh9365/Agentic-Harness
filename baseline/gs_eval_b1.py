"""
April evaluation of item B1 (NOTES 30.4 / 30.4a; April opening 33, the TEST half only): conditions (i) no pre-training, (ii) AR pre-training on January, (iii) AR pre-training on January + the unlabelled ADAPT reports.   (OURS)

    python -m baseline.gs_eval_b1 --runs <dir(s) with b1_seed<k>.npz> --out results/groupsplit/b1

Reads only the TEST rows' logits (b1_seed<k>.npz: test_idx, logits_i, logits_ii, logits_iii) and the labels of those rows. Seeds 0 to 9. Checks: the committed split (sha256) and test_idx equal to its TEST rows; any seed and condition with TEST AUC < 0.6
-> STOP.txt (the tables are still written with all seeds, none is excluded). Metrics: normalised pAUC@1e-2 on logits (primary), TPR at FPR 1e-2 and 1e-3, AUC, on TEST and on TEST-unseen; pairs (iii) - (ii), (ii) - (i), (iii) - (i);
stratified and cluster (hash_apis) bootstrap, 1,000 resamples, numpy seed 0; resolved = the cluster interval of pAUC@1e-2 excludes 0; seeds each way.
"""
import argparse
import hashlib
import json
import os

import numpy as np

from baseline import att_report as AR, gap_final
from baseline.twolevel_eval import april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

ROOT = AR.ROOT
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
CONDS = ["i", "ii", "iii"]
NAME = {"i": "(i) no pre-training", "ii": "(ii) AR pre-training on January", "iii": "(iii) AR pre-training on January + unlabelled ADAPT"}
SPLIT = os.path.join(ROOT, "results", "groupsplit", "b1", "split.npz")
SPLIT_SHA = "c9808ac80617af62a62a233e284fce955c3993acb89f62ccecfcfbb19f9d3bd3"
idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}


def table(name, y, groups, Z, boot, pairs, L, res_out):
    from sklearn.metrics import roc_auc_score
    T = {k: metrics_of(y, Z[k]) for k in Z}
    bs = gap_final.bootstrap(y, Z, boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, boot)
    L += [f"### {name}: {len(y)} reports ({int(y.sum())} malicious, {len(y) - int(y.sum())} benign, {len(set(groups))} hash_apis groups); 10 seeds each, per-seed mean ± std", "",
          md([[NAME[k], len(T[k]["auc"])] + [ms(T[k][c], d) for c, _, d in COLS] for k in Z], ["condition", "n"] + [c[1] for c in COLS]), "",
          "(TPR@1e-2 and TPR@1e-3 use thresholds set on each model's own TEST benign scores: the false-positive rate is true by construction.)", ""]
    rows, cl = [], {}
    for (n, b) in pairs:
        for c, lbl, d in BOOT:
            if c not in idx_of:
                continue
            dd = T[n][c] - T[b][c]
            ps = bs["ps"]["diffs"][f"{n} - {b}"][c]
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[c]], [2.5, 97.5])
            res = ("**RESOLVED " + ("better" if dd.mean() > 0 else "worse") + "**" if (lo > 0 or hi < 0) else "not resolved") if c == PRIMARY else ("cluster CI excludes 0 (descriptive)" if (lo > 0 or hi < 0) else "cluster CI contains 0 (descriptive)")
            cl[f"{n}-{b}|{c}"] = {"mean": float(dd.mean()), "strat_lo": float(ps["lo"]), "strat_hi": float(ps["hi"]), "cluster_lo": float(lo), "cluster_hi": float(hi), "seeds_up": int((dd > 0).sum()), "seeds_down": int((dd < 0).sum())}
            rows.append([f"{n} − {b}", lbl, f"{100 * dd.mean():+.2f}", f"[{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{int((dd > 0).sum())} up / {int((dd < 0).sum())} down", res])
    L += [f"Differences on {name} (points x100; mean of the 10 per-seed differences; seeds paired by index only; **resolved = the CLUSTER interval of pAUC@1e-2 excludes 0**):", "",
          md(rows, ["difference", "metric", "mean difference", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome"]), ""]
    res_out[name] = {"test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}, "pairs": cl}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    assert hashlib.sha256(open(SPLIT, "rb").read()).hexdigest() == SPLIT_SHA
    sp = np.load(SPLIT)
    test, unseen = sp["test"], sp["test_unseen"]
    y_all = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    fam, hsh, groups_all = april_meta()
    assert len(y_all) == len(groups_all) == 17402
    y, groups = y_all[test], np.asarray(groups_all)[test]
    Z = {k: [] for k in CONDS}
    for s in SEEDS:
        f = [os.path.join(d, f"b1_seed{s}.npz") for d in a.runs if os.path.exists(os.path.join(d, f"b1_seed{s}.npz"))]
        assert len(f) == 1, (s, f)
        r = np.load(f[0])
        assert np.array_equal(r["test_idx"], test), f"seed {s}: test_idx differs from the committed split"
        for k in CONDS:
            z = r[f"logits_{k}"].astype(np.float64)
            assert z.shape == (len(test),) and np.isfinite(z).all()
            Z[k].append(z)
    Z = {k: np.stack(v) for k, v in Z.items()}
    from sklearn.metrics import roc_auc_score
    bad = [(k, s, round(float(roc_auc_score(y, Z[k][s])), 3)) for k in CONDS for s in SEEDS if roc_auc_score(y, Z[k][s]) < 0.6]
    os.makedirs(a.out, exist_ok=True)
    if bad:
        open(os.path.join(a.out, "STOP.txt"), "w").write(f"STOP: (condition, seed, TEST AUC) below 0.6: {bad}\nThe tables are still written with all seeds.\n")
        print("STOP written:", bad)
    pairs = [("iii", "ii"), ("ii", "i"), ("iii", "i")]
    L, res = [], {}
    table("TEST", y, groups, Z, a.boot, pairs, L, res)
    table("TEST-unseen", y[unseen], groups[unseen], {k: v[:, unseen] for k, v in Z.items()}, a.boot, pairs, L, res)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    json.dump(res, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    np.savez_compressed(os.path.join(a.out, "logits_b1_test.npz"), test_idx=test, **{f"z_{k}": Z[k].astype(np.float32) for k in CONDS})
    print("\n".join(L))


if __name__ == "__main__":
    main()
