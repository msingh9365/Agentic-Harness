#!/usr/bin/env python
"""
Test 2: information ceiling. The same bag-of-API-names LightGBM as test 1, trained on the first 92
API calls only and on the full trace (January only; seeds 0/1/2). 92 = median number of complete
calls inside Nebula's first 512 tokens for reports longer than 512 tokens (REPORT.md §10.3).
The full-trace model is the one of test 1 (identical, deterministic training); it is retrained here.
"""
import json

import numpy as np

import common as C
from test1_rank_average import train_bag

K = 92


def main():
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    seqs = C.Seqs()
    full = train_bag(meta, seqs, None, "full trace")
    pre = train_bag(meta, seqs, K, f"first {K} calls")
    C.save_scores(f"lgbm_bag_first{K}", test.row.values, {s: v[0] for s, v in pre.items()}, "april")
    C.save_scores(f"lgbm_bag_first{K}", val.row.values, {s: v[1] for s, v in pre.items()}, "janval")
    ref = C.load_scores("lgbm_bag_full", "april")
    for s in C.SEEDS:     # same model as test 1
        assert np.allclose(ref[s].loc[test.row.values].values, full[s][0]), "full-trace model differs from test 1"
    yv = val.label.values
    tb = lambda s: {f: C.thr_from(yv, s, f) for f, _ in C.FPRS}
    nf, np_ = "LightGBM, full trace", f"LightGBM, first {K} calls"
    models = {nf: {s: v[0] for s, v in full.items()}, np_: {s: v[0] for s, v in pre.items()}}
    thr_b = {nf: {s: tb(v[1]) for s, v in full.items()}, np_: {s: tb(v[1]) for s, v in pre.items()}}
    diffs = [(nf, np_)]
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, diffs=diffs)
    d = point[nf]["all"]["tpr1%_a"] - point[np_]["all"]["tpr1%_a"]
    lo, hi = dci[(nf, np_, "all", "tpr1%_a")]
    long_ok = (test.n_chunks > 1).values
    share_cut = float(np.mean(meta.loc[test.row.values, "n_tokens_full"].values > 512))
    decision = (f"The full trace adds {100 * d:+.1f} points of TPR at 1% FPR [{100 * lo:+.1f}, {100 * hi:+.1f}] "
                f"over the first {K} calls, " +
                ("so long-context modelling has little to win (less than 1 point)." if d < 0.01 else
                 "which is more than 1 point, so the rule does not say that long-context modelling has little to win."))
    y = test.label.values
    s92 = models[np_][0]
    t92 = C.thr_from(y, s92, 0.01)
    ties = int(((s92 == t92) & (y == 0)).sum())
    dd = {sub: point[nf][sub]["auc"] - point[np_][sub]["auc"] for sub, _ in masks}
    dt = {sub: point[nf][sub]["tpr1%_a"] - point[np_][sub]["tpr1%_a"] for sub, _ in masks}
    note = (f"How to read this. (1) The first-{K}-call model gives many reports the same score: {ties} April benign "
            f"reports (seed 0) sit exactly on its 1% threshold, which pushes its TPR (a) down. (2) Reports that need one "
            f"chunk mostly have fewer than {K} calls, so both models see almost the same input there; yet TPR at 1% "
            f"FPR differs by {100 * dt['1 chunk']:+.1f} points, which comes from the different model and threshold, not "
            f"from more information. AUC is the cleaner measure: {dd['1 chunk']:+.4f} for 1-chunk reports, "
            f"{dd['2-3 chunks']:+.4f} for 2-3 chunks and {dd['4-8 chunks']:+.4f} for 4-8 chunks. So later calls do carry "
            f"signal for long reports, for a model that counts API names. (Released Nebula itself does not improve "
            f"beyond about 100 calls: REPORT.md §10.3.)")
    json.dump({"tpr1_a_diff": d, "ci": [lo, hi], "decision": decision, "auc_diff": dd, "ties": ties},
              open(f"{C.OUT}/test2.json", "w"), indent=1)
    txt = (f"## Test 2: information ceiling (first {K} calls vs full trace)\n\n"
           f"Same LightGBM as test 1 (bag of API names, early stopping on group-weighted January-validation "
           f"log-loss, seeds 0/1/2: mean over seeds). Names kept if seen in ≥ 20 January-train reports, counted on "
           f"the same prefix. {K} = median number of complete API calls in Nebula's 512-token window (reports > 512 "
           f"tokens). {100 * share_cut:.1f}% of April reports are longer than 512 tokens.\n\n"
           + C.md_table(C.result_tables(point, ci, masks, list(models))) +
           "\n**Per seed (all April):**\n\n" + C.md_table(C.seed_spread(point, masks, list(models))) +
           "\n**Full trace minus first 92 calls [95% interval]:**\n\n" + C.md_table(C.diff_table(point, dci, masks, diffs)) +
           f"\n{note}\n\n**Decision.** {decision}\n")
    open(f"{C.OUT}/parts_test2.md", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
