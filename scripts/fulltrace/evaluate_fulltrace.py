#!/usr/bin/env python
"""
Evaluation of results/fulltrace: model F (C over the whole report, up to 4,096 tokens) in regime J, 5 seeds.

    python scripts/fulltrace/evaluate_fulltrace.py --src-f <fulltrace kernel output> --src-j <regime J output of pooling_v2> --epochs-f 10

Models (regime J: trained on all of January; thresholds (b) do not exist; (a) = from the April benign scores):
  F   full-trace C, --epochs-f epochs, seeds 0-4                          (this experiment)
  A   flatten, 512 tokens, 1 epoch, seeds 0-4                             (reference asked for; the regime-J runs of pooling_v2)
  C   mean pooling + fixed PE, 512 tokens, 10 epochs, seeds 0-4           (extra reference: same model, first 512 tokens only)
  released Nebula, bag-of-API LightGBM (seeds 0-2 reused as seed mod 3), and the percentile rank average of each
  of A, C, F and of the released model with the LightGBM of the same seed.
Subsets as in results/pooling_v2: all, seen, unseen, 1 / 2-3 / 4-8 chunks, distance quartiles and Q2-Q4 (test 3), window-share groups.
Group bootstrap (April hash_apis, 1,000 resamples, paired across models) from scripts/go_no_go/common.py.
Writes results/fulltrace/tables.md and evaluation.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
sys.path.insert(0, os.path.join(HERE, "..", "pooling"))
import common as C  # noqa: E402
from evaluate_pooling import pct_rank  # noqa: E402

OUT = "results/fulltrace"
WIN = 16
SEEDS = list(range(5))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-f", required=True)
    ap.add_argument("--src-j", required=True)
    ap.add_argument("--epochs-f", type=int, default=10)
    ap.add_argument("--tag", default="_all")
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    a = ap.parse_args()
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    models, thr_b = {}, {}
    never = {f: np.inf for f, _ in C.FPRS}                          # no January threshold in regime J

    def add(name, d):
        models[name] = d
        thr_b[name] = {s: never for s in d}
    load = lambda src, run, ep: sigmoid(np.load(os.path.join(src, "scores", f"{run}_epochs.npz"))["april"][ep - 1])
    add("F (J)", {s: load(a.src_f, f"F{a.tag}_s{s}", a.epochs_f) for s in SEEDS})
    add("A (J)", {s: load(a.src_j, f"A{a.tag}_s{s}", 1) for s in SEEDS})
    add("C 512 tokens (J)", {s: load(a.src_j, f"C{a.tag}_s{s}", 10) for s in SEEDS})
    neb = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    lg = C.load_scores("lgbm_bag_full", "april")
    lgb = lambda s: lg[s % 3].loc[test.row.values].values
    add("released Nebula", {0: neb})
    add("LightGBM bag of API names", {s: lgb(s) for s in SEEDS})
    add("released Nebula + LightGBM", {s: (pct_rank(neb) + pct_rank(lgb(s))) / 2 for s in SEEDS})
    for n in ("F (J)", "A (J)", "C 512 tokens (J)"):
        add(f"{n} + LightGBM", {s: (pct_rank(models[n][s]) + pct_rank(lgb(s))) / 2 for s in SEEDS})

    seqdf = pd.read_parquet(f"{C.OUT}/scores/test3_unseen_sequences.parquet").set_index("hash_apis")
    rep_d = test.hash_apis.map(seqdf.nearest_dist).values.astype(float)
    rep_w = test.hash_apis.map(seqdf.window_share).values.astype(float)
    qd = np.nanpercentile(seqdf.nearest_dist.values, [25, 50, 75])
    qw = np.nanpercentile(seqdf.window_share.values, [25, 50, 75])
    edges = [-np.inf, *qd, np.inf]
    qm = [(f"distance Q{i + 1} ({'≤' if i < 3 else '>'} {qd[min(i, 2)]:.3f})", (rep_d > edges[i]) & (rep_d <= edges[i + 1]) & ~np.isnan(rep_d)) for i in range(4)]
    unseen = ~test.seen.values
    wm = [("window share = 100%", unseen & (rep_w == 1)), (f"window share {qw[0]:.3f}–<100%", unseen & (rep_w > qw[0]) & (rep_w < 1)),
          (f"window share ≤ {qw[0]:.3f} (lowest quartile)", unseen & (rep_w <= qw[0])), (f"shorter than {WIN} calls (no window)", unseen & np.isnan(rep_w))]
    q24 = ("distance Q2-Q4 (farther three quartiles)", qm[1][1] | qm[2][1] | qm[3][1])
    masks = C.subsets(test) + qm + [q24] + wm
    diffs = [("F (J)", "A (J)"), ("F (J)", "C 512 tokens (J)"), ("C 512 tokens (J)", "A (J)"), ("F (J)", "released Nebula"), ("A (J)", "released Nebula"),
             ("F (J) + LightGBM", "released Nebula + LightGBM"), ("F (J) + LightGBM", "A (J) + LightGBM"), ("F (J) + LightGBM", "C 512 tokens (J) + LightGBM"),
             ("A (J) + LightGBM", "released Nebula + LightGBM")]
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)
    names = [n for n, _ in masks]
    order = ["F (J)", "C 512 tokens (J)", "A (J)", "released Nebula", "LightGBM bag of API names", "F (J) + LightGBM", "C 512 tokens (J) + LightGBM",
             "A (J) + LightGBM", "released Nebula + LightGBM"]
    cols = ["auc", "tpr1%_a", "tpr0.1%_a"]

    def tab(sub_filter):
        rows = []
        for sub, _ in masks:
            if sub not in sub_filter:
                continue
            for m in order:
                r = {"subset": sub, "model": m, "n (malware)": f"{point[m][sub]['n']:,.0f} ({point[m][sub]['n_mal']:,.0f})"}
                for k in cols:
                    lo, hi = ci[(m, sub, k)]
                    r[C.HEAD[k]] = f"{C.fmt(k, point[m][sub][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
                rows.append(r)
        return pd.DataFrame(rows)
    drows = []
    for x, y in diffs:
        for sub, _ in masks:
            r = {"difference": f"{x} − {y}", "subset": sub}
            for k in cols:
                lo, hi = dci[(x, y, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x][sub][k] - point[y][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            drows.append(r)
    t_diff = pd.DataFrame(drows)
    sp = []
    for m in ("F (J)", "C 512 tokens (J)", "A (J)"):
        for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1% (a)"), ("tpr0.1%_a", "TPR@0.1% (a)")):
            v = np.array([p["all"][k] for p in point[m]["_seeds"]])
            sp.append({"model": m, "metric": tag, "seeds": len(v), "mean": f"{v.mean():.4f}" if k == "auc" else f"{100 * v.mean():.1f}%",
                       "sd": f"{v.std(ddof=1):.4f}" if k == "auc" else f"{100 * v.std(ddof=1):.1f}",
                       "per seed": " / ".join((f"{x:.4f}" if k == "auc" else f"{100 * x:.1f}") for x in v)})
    chunk_names = ["all", "1 chunk", "2-3 chunks", "4-8 chunks"]
    md = ["## Overall and by number of chunks\n", "Mean over 5 seeds [95% group-bootstrap interval]. Regime J: thresholds (a) from the April benign scores.\n",
          C.md_table(tab(chunk_names)), "\n## Seed spread (all April reports)\n", C.md_table(pd.DataFrame(sp)),
          "\n## Other subsets\n", C.md_table(tab([n for n in names if n not in chunk_names])),
          "\n## Paired differences\n", "TPR in percentage points.\n", C.md_table(t_diff)]
    open(f"{OUT}/tables.md", "w").write("\n".join(md))
    json.dump({"point": {m: {s: {k: float(v) for k, v in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point},
               "diffs": {f"{x} - {y}|{s}|{k}": [float(point[x][s][k] - point[y][s][k]), *map(float, dci[(x, y, s, k)])] for x, y in diffs for s in names for k in C.METRIC_COLS},
               "epochs_f": a.epochs_f}, open(f"{OUT}/evaluation.json", "w"), indent=1)
    print(C.md_table(tab(["all"])))
    print(C.md_table(t_diff[t_diff.subset.isin(["all", "4-8 chunks"])]))


if __name__ == "__main__":
    main()
