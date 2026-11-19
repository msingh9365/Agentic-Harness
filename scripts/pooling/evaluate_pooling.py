#!/usr/bin/env python
"""
Evaluate the pooling experiment (models A, B, C x seeds 0, 1, 2) with scripts/go_no_go/common.py.

    python scripts/pooling/evaluate_pooling.py --src <Kaggle output folder> [--boot 1000]

Input  : the Kaggle output (scores/pool_<V>_seed<N>_{april,janval}.parquet, logs/<V>_s<N>.json).
Writes : results/pooling/scores/pool_<V>_{april,janval}.parquet   (long: row, seed, score; as results/go_no_go/scores)
         results/pooling/logs/*.json                              (copies of the training logs)
         results/pooling/tables.md, results/pooling/evaluation.json

Models: A, B, C (each seed); released Nebula and the bag-of-API LightGBM (results/go_no_go/scores); and the
rank average of each of A, B, C with the LightGBM of the same seed (percentile ranks within the April set
and within the January-validation set, as in test 1; no labels are used). "(Jan ref)" is the variant of test 1
that ranks April scores against the January-validation scores, so that a January threshold transfers to April.
Metrics, thresholds (a) April benign / (b) January-validation benign, group bootstrap over hash_apis
(1,000 resamples, seed 0, paired across models) are common.evaluate_models. A model's value is the mean over its
seeds; the per-seed values are listed too.
Subsets: all, seen, unseen, 1 / 2-3 / 4-8 chunks, the unseen distance quartiles and the window-share groups
of test 3 (the same definitions as scripts/go_no_go/test3_unseen_distance.py, read from
results/go_no_go/scores/test3_unseen_sequences.parquet), plus "distance Q2-Q4" (the three farther quartiles together).
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "go_no_go"))
import common as C  # noqa: E402  (chdir to the repository root)

OUT = "results/pooling"
SEEDS = [0, 1, 2]
WIN = 16
VARIANTS = {"A": "A: flatten pooling", "B": "B: mean pooling", "C": "C: mean pooling + fixed position encoding"}


def pct_rank(s):
    return rankdata(s, method="average") / len(s)


def ref_rank(s, ref):
    """Percentile of s within a fixed reference sample (the January-validation scores; labels unused). As test 1."""
    ref = np.sort(ref)
    return (np.searchsorted(ref, s, "left") + np.searchsorted(ref, s, "right")) / (2 * len(ref))


def load_pool(src, v, part, seeds):
    out = {}
    for s in seeds:
        p = os.path.join(src, "scores", f"pool_{v}_seed{s}_{part}.parquet")
        if os.path.exists(p):
            d = pd.read_parquet(p)
            out[s] = pd.Series(d.score.values, index=d.row.values)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Kaggle output folder (with scores/ and logs/)")
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    a = ap.parse_args()

    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    yv = val.label.values
    tb = lambda s: {f: C.thr_from(yv, s, f) for f, _ in C.FPRS}
    os.makedirs(f"{OUT}/scores", exist_ok=True)
    os.makedirs(f"{OUT}/logs", exist_ok=True)

    # ---- scores
    ap_, jv_ = {}, {}                                   # {variant: {seed: array in test / val order}}
    for v in VARIANTS:
        for part, dst in (("april", ap_), ("janval", jv_)):
            d = load_pool(a.src, v, part, SEEDS)
            rows = test.row.values if part == "april" else val.row.values
            dst[v] = {s: d[s].loc[rows].values for s in d}
            long = pd.concat([pd.DataFrame({"row": d[s].index.values, "seed": s, "score": d[s].values}) for s in d])
            long.to_parquet(f"{OUT}/scores/pool_{v}_{part}.parquet", index=False)
    seeds = sorted(set(ap_["A"]) & set(ap_["B"]) & set(ap_["C"]))
    print("seeds found for all of A, B, C:", seeds, flush=True)
    assert seeds, "no complete seed"
    for f in os.listdir(os.path.join(a.src, "logs")):
        if f.endswith(".json") or f.endswith(".log"):
            shutil.copy2(os.path.join(a.src, "logs", f), f"{OUT}/logs/{f}")

    neb_a = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    neb_v = C.load_scores("nebula", "janval")[0].loc[val.row.values].values
    lg_a, lg_v = C.load_scores("lgbm_bag_full", "april"), C.load_scores("lgbm_bag_full", "janval")
    lgb_a = {s: lg_a[s].loc[test.row.values].values for s in seeds}
    lgb_v = {s: lg_v[s].loc[val.row.values].values for s in seeds}

    models, thr_b = {}, {}

    def add(name, a_by_seed, v_by_seed):
        models[name] = a_by_seed
        thr_b[name] = {s: tb(v_by_seed[s]) for s in a_by_seed}

    for v, title in VARIANTS.items():
        add(v, {s: ap_[v][s] for s in seeds}, {s: jv_[v][s] for s in seeds})
    for v in VARIANTS:                                   # rank average with the LightGBM of the same seed
        add(f"{v} + LightGBM", {s: (pct_rank(ap_[v][s]) + pct_rank(lgb_a[s])) / 2 for s in seeds},
            {s: (pct_rank(jv_[v][s]) + pct_rank(lgb_v[s])) / 2 for s in seeds})
    for v in VARIANTS:                                   # variant of test 1: ranks against the January-validation scores,
        add(f"{v} + LightGBM (Jan ref)",                 # so that a January threshold transfers to April
            {s: (ref_rank(ap_[v][s], jv_[v][s]) + ref_rank(lgb_a[s], lgb_v[s])) / 2 for s in seeds},
            {s: (ref_rank(jv_[v][s], jv_[v][s]) + ref_rank(lgb_v[s], lgb_v[s])) / 2 for s in seeds})
    add("released Nebula", {0: neb_a}, {0: neb_v})
    add("LightGBM bag of API names", lgb_a, lgb_v)
    add("released Nebula + LightGBM", {s: (pct_rank(neb_a) + pct_rank(lgb_a[s])) / 2 for s in seeds},
        {s: (pct_rank(neb_v) + pct_rank(lgb_v[s])) / 2 for s in seeds})

    # ---- subsets (same definitions as test 3)
    seqdf = pd.read_parquet(f"{C.OUT}/scores/test3_unseen_sequences.parquet").set_index("hash_apis")
    rep_d = test.hash_apis.map(seqdf.nearest_dist).values.astype(float)
    rep_w = test.hash_apis.map(seqdf.window_share).values.astype(float)
    qd = np.nanpercentile(seqdf.nearest_dist.values, [25, 50, 75])
    qw = np.nanpercentile(seqdf.window_share.values, [25, 50, 75])
    edges = [-np.inf, *qd, np.inf]
    qm = [(f"distance Q{i + 1} ({'≤' if i < 3 else '>'} {qd[min(i, 2)]:.3f})",
           (rep_d > edges[i]) & (rep_d <= edges[i + 1]) & ~np.isnan(rep_d)) for i in range(4)]
    unseen = ~test.seen.values
    wm = [("window share = 100%", unseen & (rep_w == 1)),
          (f"window share {qw[0]:.3f}–<100%", unseen & (rep_w > qw[0]) & (rep_w < 1)),
          (f"window share ≤ {qw[0]:.3f} (lowest quartile)", unseen & (rep_w <= qw[0])),
          (f"shorter than {WIN} calls (no window)", unseen & np.isnan(rep_w))]
    q24 = ("distance Q2-Q4 (farther three quartiles)", qm[1][1] | qm[2][1] | qm[3][1])
    masks = C.subsets(test) + qm + [q24] + wm
    print("subsets:", {n: int(m.sum()) for n, m in masks}, flush=True)

    diffs = [("B", "A"), ("C", "A"), ("C", "B"),
             ("B + LightGBM", "A + LightGBM"), ("C + LightGBM", "A + LightGBM"), ("C + LightGBM", "B + LightGBM"),
             ("B + LightGBM (Jan ref)", "A + LightGBM (Jan ref)"), ("C + LightGBM (Jan ref)", "A + LightGBM (Jan ref)"),
             ("C + LightGBM (Jan ref)", "B + LightGBM (Jan ref)")]
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)

    # ---- tables
    names = [n for n, _ in masks]
    main_models = ["A", "B", "C", "A + LightGBM", "B + LightGBM", "C + LightGBM",
                   "A + LightGBM (Jan ref)", "B + LightGBM (Jan ref)", "C + LightGBM (Jan ref)",
                   "released Nebula", "LightGBM bag of API names", "released Nebula + LightGBM"]
    t_all = C.result_tables(point, ci, masks, main_models, sub_filter=["all"]).drop(columns=["subset"])
    t_seed = C.seed_spread(point, masks, main_models)
    t_diff_all = C.diff_table(point, dci, masks, diffs)
    t_diff_all = t_diff_all[t_diff_all.subset.isin(names)]

    keep = ["AUC", "TPR@1% (a)", "TPR@1% (b)"]
    sub_rows = C.result_tables(point, ci, masks, ["A", "B", "C", "released Nebula", "LightGBM bag of API names"])
    sub_rows = sub_rows[["subset", "model", "n (malware)"] + keep]
    sub_rows2 = C.result_tables(point, ci, masks, ["A + LightGBM", "B + LightGBM", "C + LightGBM",
                                                   "A + LightGBM (Jan ref)", "B + LightGBM (Jan ref)", "C + LightGBM (Jan ref)"])
    sub_rows2 = sub_rows2[["subset", "model", "n (malware)"] + keep]

    # distance-quartile gap (point estimates, mean over seeds): TPR@1% (a) in Q1 minus the other three together
    gap = []
    for m in ["A", "B", "C", "released Nebula", "LightGBM bag of API names", "A + LightGBM", "B + LightGBM", "C + LightGBM"]:
        g = {"model": m}
        for k, tag in [("tpr1%_a", "TPR@1% (a)"), ("tpr1%_b", "TPR@1% (b)")]:
            q1, q2 = point[m][qm[0][0]][k], point[m][q24[0]][k]
            g[f"{tag} Q1"] = C.fmt(k, q1)
            g[f"{tag} Q2-Q4"] = C.fmt(k, q2)
            g[f"{tag} gap Q1 − Q2-Q4 (points)"] = f"{100 * (q1 - q2):+.1f}"
        gap.append(g)
    t_gap = pd.DataFrame(gap)

    # training summary from the logs
    tr = []
    for v in VARIANTS:
        for s in seeds:
            p = f"{OUT}/logs/{v}_s{s}.json"
            if os.path.exists(p):
                j = json.load(open(p))
                h = j["history"]
                tr.append({"run": f"{v} seed {s}", "epochs run": len(h), "best epoch": j["best_epoch"],
                           "stopped by": j["stopped_by"], "best val loss": f"{j['best_val_loss']:.4f}",
                           "val AUC by epoch": " / ".join(f"{x['val_auc']:.4f}" for x in h),
                           "val loss by epoch": " / ".join(f"{x['val_loss']:.3f}" for x in h),
                           "s per epoch": f"{j['mean_epoch_s']:.0f}", "GPU": j["gpu"]})
    t_train = pd.DataFrame(tr)

    md = ["## Overall (all April reports)\n", "Mean over seeds [95% group-bootstrap interval].\n", C.md_table(t_all),
          "\n## Per-seed values (all April reports)\n", "Seed 0 / 1 / 2.\n", C.md_table(t_seed),
          "\n## Paired differences (all subsets)\n",
          "Difference of the seed means, with the 95% interval of the paired group bootstrap. TPR in percentage points.\n",
          C.md_table(t_diff_all),
          "\n## Distance quartiles: the gap between the nearest quartile and the rest\n", C.md_table(t_gap),
          "\n## Results by subset\n", C.md_table(sub_rows), "\n## Rank average with LightGBM, by subset\n", C.md_table(sub_rows2),
          "\n## Training runs\n", C.md_table(t_train)]
    open(f"{OUT}/tables.md", "w").write("\n".join(md))
    ev = {"seeds": seeds, "n_boot": a.boot, "quartiles_distance": qd.tolist(), "quartiles_window": qw.tolist(),
          "point": {m: {s: {k: float(v) for k, v in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point},
          "diffs": {f"{a_} - {b_}|{s}|{k}": [float(point[a_][s][k] - point[b_][s][k]), *map(float, dci[(a_, b_, s, k)])]
                    for a_, b_ in diffs for s in names for k in C.METRIC_COLS}}
    json.dump(ev, open(f"{OUT}/evaluation.json", "w"), indent=1)
    print("wrote", f"{OUT}/tables.md", f"{OUT}/evaluation.json")


if __name__ == "__main__":
    main()
