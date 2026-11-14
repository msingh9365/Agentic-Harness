#!/usr/bin/env python
"""
Test 1: trivial competitor. LightGBM on a bag of API names (full trace, January only, seeds 0/1/2),
its percentile rank averaged with released Nebula's percentile rank. Ranks are computed within each
set (April, January validation) from the scores alone; no labels are used.
Compared with released Nebula, LightGBM alone and the two-level 8-chunk model.
"""
import json
import time

import numpy as np
import pandas as pd
from scipy.stats import rankdata

import common as C
from analyze_signal import bag_matrix, fit_lgb, group_weights, LGB_PARAMS


def pct_rank(s):
    return rankdata(s, method="average") / len(s)


def ref_rank(s, ref):
    """Percentile of s within a fixed reference sample (January validation scores, labels unused)."""
    ref = np.sort(ref)
    return (np.searchsorted(ref, s, "left") + np.searchsorted(ref, s, "right")) / (2 * len(ref))


def train_bag(meta, seqs, K=None, tag="full"):
    """LightGBM bag of API names (first K calls; None = full trace). Returns {seed: (april, janval)}."""
    rows = {s: meta.row.values[meta.side == s] for s in ["train", "val", "test"]}
    y = {s: meta.label.values[rows[s]] for s in rows}
    allr = np.concatenate([rows["train"], rows["val"], rows["test"]])
    X, keep = bag_matrix(seqs, allr, len(seqs.vocab), K=K, bigrams=False, fit_rows=rows["train"])
    cut = np.cumsum([0, len(rows["train"]), len(rows["val"]), len(rows["test"])])
    Xs = [X[cut[i]:cut[i + 1]] for i in range(3)]
    W = group_weights(meta)
    out = {}
    for seed in C.SEEDS:
        t0 = time.time()
        m = fit_lgb(Xs[0], y["train"], Xs[1], y["val"], W, seed)
        out[seed] = (m.predict(Xs[2], num_iteration=m.best_iteration), m.predict(Xs[1], num_iteration=m.best_iteration))
        print(f"  LightGBM bag of API names ({tag}) seed {seed}: {X.shape[1]} features, best iteration "
              f"{m.best_iteration} ({time.time() - t0:.0f}s)", flush=True)
    return out


def main():
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    seqs = C.Seqs()
    print("LightGBM parameters:", json.dumps(LGB_PARAMS), flush=True)
    lgb = train_bag(meta, seqs)
    C.save_scores("lgbm_bag_full", test.row.values, {s: v[0] for s, v in lgb.items()}, "april")
    C.save_scores("lgbm_bag_full", val.row.values, {s: v[1] for s, v in lgb.items()}, "janval")
    neb_a = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    neb_v = C.load_scores("nebula", "janval")[0].loc[val.row.values].values
    two_a = C.load_scores("twolevel_k8", "april")[0].loc[test.row.values].values
    two_v = C.load_scores("twolevel_k8", "janval")[0].loc[val.row.values].values
    ra_a = {s: (pct_rank(v[0]) + pct_rank(neb_a)) / 2 for s, v in lgb.items()}
    ra_v = {s: (pct_rank(v[1]) + pct_rank(neb_v)) / 2 for s, v in lgb.items()}
    C.save_scores("rank_average", test.row.values, ra_a, "april")
    C.save_scores("rank_average", val.row.values, ra_v, "janval")
    # variant: ranks against a fixed reference (the January validation scores), so a January threshold transfers
    rj_a = {s: (ref_rank(v[0], v[1]) + ref_rank(neb_a, neb_v)) / 2 for s, v in lgb.items()}
    rj_v = {s: (ref_rank(v[1], v[1]) + ref_rank(neb_v, neb_v)) / 2 for s, v in lgb.items()}
    C.save_scores("rank_average_janref", test.row.values, rj_a, "april")
    C.save_scores("rank_average_janref", val.row.values, rj_v, "janval")

    yv = val.label.values
    tb = lambda s: {f: C.thr_from(yv, s, f) for f, _ in C.FPRS}
    models = {"released Nebula": {0: neb_a}, "LightGBM bag of API names": {s: v[0] for s, v in lgb.items()},
              "rank average (LightGBM + Nebula)": ra_a, "rank average, January reference": rj_a,
              "two-level K=8 (finetune_k8)": {0: two_a}}
    thr_b = {"released Nebula": {0: tb(neb_v)}, "LightGBM bag of API names": {s: tb(v[1]) for s, v in lgb.items()},
             "rank average (LightGBM + Nebula)": {s: tb(v) for s, v in ra_v.items()},
             "rank average, January reference": {s: tb(v) for s, v in rj_v.items()},
             "two-level K=8 (finetune_k8)": {0: tb(two_v)}}
    diffs = [("rank average (LightGBM + Nebula)", "two-level K=8 (finetune_k8)"),
             ("rank average, January reference", "two-level K=8 (finetune_k8)"),
             ("rank average (LightGBM + Nebula)", "released Nebula"),
             ("two-level K=8 (finetune_k8)", "released Nebula")]
    t0 = time.time()
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, diffs=diffs)
    print(f"bootstrap: {C.N_BOOT} group resamples in {time.time() - t0:.0f}s", flush=True)
    order = list(models)
    main_t = C.result_tables(point, ci, masks, order)
    spread = C.seed_spread(point, masks, order)
    drow = []
    for a_, b_ in diffs:
        for sub, _ in masks:
            r = {"difference": f"{a_} − {b_}", "subset": sub}
            for k in C.METRIC_COLS:
                if k.startswith("fpr"):
                    continue
                lo, hi = dci[(a_, b_, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[a_][sub][k] - point[b_][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            drow.append(r)
    ra, tw = point["rank average (LightGBM + Nebula)"]["all"], point["two-level K=8 (finetune_k8)"]["all"]
    beats = {k: ra[k] >= tw[k] for k in ["auc", "tpr1%_a", "tpr0.1%_a"]}
    json.dump({"point": {m: {s: {k: v for k, v in point[m][s].items()} for s, _ in masks} for m in order},
               "beats_two_level_a": beats}, open(f"{C.OUT}/test1.json", "w"), indent=1, default=float)
    txt = ("## Test 1: trivial competitor (rank average of LightGBM and released Nebula)\n\n"
           "Cell = value [95% interval, group bootstrap]. LightGBM and the rank average: mean over seeds 0/1/2 "
           "(per-seed values below). (a) = threshold from April benign scores; (b) = threshold from January "
           "validation benign scores, with the FPR it gives on April. Subsets use the overall thresholds. "
           "`rank average`: percentile ranks within each set (April ranked among April, January among January), "
           "as asked; its threshold (b) does not transfer, because the sets have different malware shares (78% "
           "vs 54%). `rank average, January reference`: each score's percentile within the January-validation "
           "scores of the same model (labels unused); this one can be deployed with a January threshold.\n\n"
           + C.md_table(main_t) + "\n**Per seed (all April):**\n\n" + C.md_table(spread) +
           "\n**Paired differences [95% interval]:**\n\n" + C.md_table(pd.DataFrame(drow)))
    open(f"{C.OUT}/parts_test1.md", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
