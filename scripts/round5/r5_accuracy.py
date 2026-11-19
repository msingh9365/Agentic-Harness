#!/usr/bin/env python
"""
Round 5, items 1 and 2: final accuracy tables (10 seeds) and the low-FPR measurements.

    python scripts/round5/r5_accuracy.py [--epoch 2] [--boot 1000]

Models (regime J, April 17,402 reports, 9,399 malware): ATT+bal, MM+bal, C+bal (round 5 G1, epoch 2 primary, epoch 4 as a second table) against the
released Nebula, A (J), C (J) and C (J, 2 epochs), all seeds 0-9 (released: one model); each alone and with the rank average with the bag-of-API
LightGBM (seeds 0-2 reused as seed mod 3, as in results/pooling_v2) and the 10-seed ensembles (mean of the logits). Thresholds (a): fixed at 1% / 0.1%
FPR on the April benign scores of each model and seed. Subsets: all, seen, unseen, distance quartiles (+ Q2-Q4) and 1 / 2-3 / 4-8 chunks.
Group bootstrap over April hash_apis (1,000 resamples), seed-paired differences.
Item 2: benign reports above each 0.1% threshold, the TPR when 4 / 8 / 12 benign reports may lie above the threshold, standardised partial AUC up to 1% FPR
(McClish) with group intervals, and the January validation side (regime S models of G2) as a second test set.
Writes results/round5/accuracy.md/json, lowfpr.md/json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "pooling"))
sys.path.insert(0, HERE)
import r5_common as R  # noqa: E402
from r5_common import C, V  # noqa: E402
from evaluate_pooling import pct_rank  # noqa: E402

SEEDS = list(range(10))
WIN = 16


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def load_logit(key, s, ep=None):
    out, tmpl, e0 = R.SPEC[key][:3]
    return np.load(os.path.join(out, "scores", f"{tmpl.format(s=s)}_epochs.npz"))["april"][(ep or e0) - 1]


def pauc_weighted(y, s, w, fmax=0.01):
    """standardised partial AUC (McClish) up to FPR fmax, weighted by w (group-bootstrap counts); ties handled by score bins."""
    u, inv = np.unique(s, return_inverse=True)
    pos = np.bincount(inv, w * (y == 1), minlength=len(u))[::-1]
    neg = np.bincount(inv, w * (y == 0), minlength=len(u))[::-1]
    P, Nn = pos.sum(), neg.sum()
    tpr = np.concatenate([[0], np.cumsum(pos) / P]); fpr = np.concatenate([[0], np.cumsum(neg) / Nn])
    keep = fpr <= fmax
    j = int(keep.sum())
    f = np.concatenate([fpr[:j], [fmax]])
    if j < len(fpr):                       # interpolate the ROC at fmax
        t = tpr[j - 1] + (tpr[j] - tpr[j - 1]) * (fmax - fpr[j - 1]) / (fpr[j] - fpr[j - 1])
    else:
        t = tpr[-1]
    t = np.concatenate([tpr[:j], [t]])
    area = np.trapezoid(t, f)
    mn, mx = 0.5 * fmax ** 2, fmax
    return 0.5 * (1 + (area - mn) / (mx - mn))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epoch", type=int, default=2)
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    y = test.label.values
    never = {f: np.inf for f, _ in C.FPRS}
    models, thr_b = {}, {}

    def add(name, d):
        models[name] = d
        thr_b[name] = {s: never for s in d}

    def seeds_of(key):
        return [s for s in SEEDS if R.available(key, s)]

    newkeys = {"ATT+bal": "ATTbal", "MM+bal": "MMbal", "C+bal": "Cbal"} if a.epoch == 2 else {"ATT+bal": "ATTbal4", "MM+bal": "MMbal4", "C+bal": "Cbal4"}
    neb = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    lg = C.load_scores("lgbm_bag_full", "april")
    lgb = lambda s: lg[s % 3].loc[test.row.values].values
    singles = {}
    for disp, key in newkeys.items():
        singles[disp] = {s: load_logit(key, s) for s in seeds_of(key)}
    singles["C (J, 2 epochs)"] = {s: load_logit("C2", s) for s in seeds_of("C2")}
    singles["C (J)"] = {s: load_logit("C", s) for s in seeds_of("C")}
    singles["A (J)"] = {s: load_logit("A", s) for s in seeds_of("A")}
    order_models = list(singles)
    for n, d in singles.items():
        add(n, {s: sigmoid(z) for s, z in d.items()})
        add(n + " + LightGBM", {s: (pct_rank(z) + pct_rank(lgb(s))) / 2 for s, z in d.items()})
        zs = np.mean([d[s] for s in d], 0)                                   # 10-seed ensemble: mean of the logits
        add(n + " (ensemble)", {0: sigmoid(zs)})
        add(n + " (ensemble) + LightGBM", {0: (pct_rank(zs) + pct_rank(np.mean([lgb(s) for s in range(3)], 0))) / 2})
    add("released Nebula", {0: neb})
    add("LightGBM bag of API names", {s: lgb(s) for s in SEEDS})
    add("released Nebula + LightGBM", {s: (pct_rank(neb) + pct_rank(lgb(s))) / 2 for s in SEEDS})
    print({n: len(d) for n, d in models.items()}, flush=True)
    # subsets as in results/fulltrace
    seqdf = pd.read_parquet(f"{C.OUT}/scores/test3_unseen_sequences.parquet").set_index("hash_apis")
    rep_d = test.hash_apis.map(seqdf.nearest_dist).values.astype(float)
    rep_w = test.hash_apis.map(seqdf.window_share).values.astype(float)
    qd = np.nanpercentile(seqdf.nearest_dist.values, [25, 50, 75])
    edges = [-np.inf, *qd, np.inf]
    qm = [(f"distance Q{i + 1} ({'≤' if i < 3 else '>'} {qd[min(i, 2)]:.3f})", (rep_d > edges[i]) & (rep_d <= edges[i + 1]) & ~np.isnan(rep_d)) for i in range(4)]
    q24 = ("distance Q2-Q4 (farther three quartiles)", qm[1][1] | qm[2][1] | qm[3][1])
    masks = C.subsets(test) + qm + [q24]
    ben_n = {n: n for n in models}
    main_names = [n for n in order_models] + ["released Nebula"]
    diffs = []
    for n in ("ATT+bal", "MM+bal", "C+bal"):
        for o in ("released Nebula", "A (J)", "C (J)", "C (J, 2 epochs)"):
            diffs.append((n, o)); diffs.append((n + " + LightGBM", o + " + LightGBM" if o != "released Nebula" else "released Nebula + LightGBM"))
            diffs.append((n + " (ensemble)", o if o == "released Nebula" else o + " (ensemble)"))
    diffs += [("ATT+bal", "MM+bal"), ("ATT+bal", "C+bal"), ("MM+bal", "C+bal"), ("ATT+bal (ensemble)", "MM+bal (ensemble)"), ("ATT+bal (ensemble)", "C+bal (ensemble)")]
    diffs = [(x, z) for x, z in diffs if x in models and z in models]
    point, cis, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)
    names = [n for n, _ in masks]
    cols = ["auc", "tpr1%_a", "tpr0.1%_a"]
    order = []
    for n in order_models:
        order += [n, n + " + LightGBM", n + " (ensemble)", n + " (ensemble) + LightGBM"]
    order += ["released Nebula", "LightGBM bag of API names", "released Nebula + LightGBM"]
    order = [n for n in order if n in models]

    def tab(sub_filter, ordr):
        rows = []
        for sub, _ in masks:
            if sub not in sub_filter:
                continue
            for m in ordr:
                r = {"subset": sub, "model": m, "n (malware)": f"{point[m][sub]['n']:,.0f} ({point[m][sub]['n_mal']:,.0f})"}
                for k in cols:
                    lo, hi = cis[(m, sub, k)]
                    r[C.HEAD[k]] = f"{C.fmt(k, point[m][sub][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
                rows.append(r)
        return pd.DataFrame(rows)
    drows = []
    for x, z in diffs:
        for sub, _ in masks:
            r = {"difference": f"{x} − {z}", "subset": sub}
            for k in cols:
                lo, hi = dci[(x, z, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x][sub][k] - point[z][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            drows.append(r)
    t_diff = pd.DataFrame(drows)
    sp = []
    for m in order_models:
        for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1% (a)"), ("tpr0.1%_a", "TPR@0.1% (a)")):
            v = np.array([p["all"][k] for p in point[m]["_seeds"]])
            sp.append({"model": m, "metric": tag, "seeds": len(v), "mean": f"{v.mean():.4f}" if k == "auc" else f"{100 * v.mean():.1f}%",
                       "sd": f"{v.std(ddof=1):.4f}" if k == "auc" and len(v) > 1 else (f"{100 * v.std(ddof=1):.1f}" if len(v) > 1 else "-"),
                       "per seed": " / ".join((f"{x:.4f}" if k == "auc" else f"{100 * x:.1f}") for x in v)})
    # seed-paired differences (seed i of one model against seed i of the other; mean difference with 95% interval over seeds)
    rng = np.random.default_rng(0)
    sprows = []
    for n in ("ATT+bal", "MM+bal", "C+bal"):
        for o in ("A (J)", "C (J)", "C (J, 2 epochs)"):
            if n not in point or o not in point:
                continue
            nn = min(len(point[n]["_seeds"]), len(point[o]["_seeds"]))
            r = {"difference": f"{n} − {o}", "seeds": nn}
            for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1%"), ("tpr0.1%_a", "TPR@0.1%")):
                d = np.array([point[n]["_seeds"][i]["all"][k] - point[o]["_seeds"][i]["all"][k] for i in range(nn)])
                b = rng.choice(d, (20000, nn)).mean(1)
                f = (lambda v: f"{v:+.4f}") if k == "auc" else (lambda v: f"{100 * v:+.1f}")
                r[tag] = f"{f(d.mean())} [{f(np.percentile(b, 2.5))}, {f(np.percentile(b, 97.5))}]"
            sprows.append(r)
    chunk_names = ["all", "1 chunk", "2-3 chunks", "4-8 chunks"]
    md = [f"# Final accuracy, 10 seeds (round 5, item 1), epoch {a.epoch} of ATT+bal, MM+bal, C+bal\n",
          "April, regime J, thresholds (a) from the April benign scores of each model and seed; mean over seeds (released: 1 model; ensembles: mean logit of the seeds, "
          "no seed spread) [95% group-bootstrap interval]. C (J) 10 epochs, A (J) 1 epoch, C (J, 2 epochs) = C after its epoch 2.\n",
          "## Overall and by number of chunks\n", C.md_table(tab(chunk_names, order)),
          "\n## Seed spread (all April reports)\n", C.md_table(pd.DataFrame(sp)),
          "\n## Seed-paired differences (all April reports, mean over seeds [95% over seeds]; TPR in points)\n", C.md_table(pd.DataFrame(sprows)),
          "\n## Other subsets\n", C.md_table(tab([n for n in names if n not in chunk_names], order)),
          "\n## Paired differences with group-bootstrap intervals (TPR in points)\n", C.md_table(t_diff)]
    open(f"{R.OUT}/accuracy{a.tag}.md", "w").write("\n".join(md))
    json.dump({"epoch": a.epoch, "point": {m: {s: {k: float(v) for k, v in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point},
               "seeds": {m: len(point[m]["_seeds"]) for m in point},
               "diffs": {f"{x} - {z}|{s}|{k}": [float(point[x][s][k] - point[z][s][k]), *map(float, dci[(x, z, s, k)])] for x, z in diffs for s in names for k in C.METRIC_COLS}},
              open(f"{R.OUT}/accuracy{a.tag}.json", "w"), indent=1)
    print(C.md_table(tab(["all"], order)))

    # -------------------------------------------------------------- item 2: low-FPR measurements on April
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, a.boot, 0)))
    nb_ = int((y == 0).sum())
    rows_cnt, rows_k, rows_p = [], [], []
    zrel = R.load_model("released", 0)[2]                                    # logits of the published weights (CPU)
    for n in order_models + ["released Nebula"]:
        d = singles[n] if n in singles else {0: zrel}
        zs = {s: v for s, v in d.items()}
        cnt1, cnt01, tk = [], [], {4: [], 8: [], 12: []}
        for s, z in zs.items():
            neg = np.sort(z[y == 0])[::-1]
            for f, lst in ((0.01, cnt1), (0.001, cnt01)):
                thr = C.thr_from(y, z, f)
                lst.append(int((z[y == 0] > thr).sum()))
            for k in tk:
                thr = neg[k]
                tk[k].append(float((z[y == 1] > thr).mean()))
        rows_cnt.append({"model": n, "benign reports in April": nb_, "allowed above 0.1% threshold (floor)": int(np.floor(0.001 * nb_)),
                         "benign above the 0.1% threshold (mean over seeds)": f"{np.mean(cnt01):.1f}", "allowed above 1% threshold": int(np.floor(0.01 * nb_)),
                         "benign above the 1% threshold": f"{np.mean(cnt1):.1f}"})
        rows_k.append({"model": n, **{f"TPR with {k} benign above the threshold ({100 * k / nb_:.3f}% FPR)": f"{100 * np.mean(v):.1f}%" for k, v in tk.items()}})
        pt = np.mean([pauc_weighted(y, z, np.ones(len(y))) for z in zs.values()])
        bs = np.array([np.mean([pauc_weighted(y, z, w) for z in zs.values()]) for w in W[:min(len(W), 300)]])
        rows_p.append({"model": n, "standardised partial AUC to 1% FPR": f"{pt:.4f} [{np.percentile(bs, 2.5):.4f}, {np.percentile(bs, 97.5):.4f}]"})
        print("pAUC", n, flush=True)
    md2 = ["# Low-FPR measurements (round 5, item 2)\n",
           "## Benign reports above the thresholds (April)\n", "The 0.1% threshold of April is the (floor(0.001 x 8,003) + 1) = 9th highest benign score: only 8 benign reports may lie above it, which is why TPR at 0.1% FPR is unstable (ties can add reports above the threshold).\n",
           C.md_table(pd.DataFrame(rows_cnt)), "\n## TPR when 4 / 8 / 12 benign reports may lie above the threshold (April)\n", C.md_table(pd.DataFrame(rows_k)),
           "\n## Standardised partial AUC up to 1% FPR (McClish; 0.5 = chance, 1 = perfect), April\n", "Mean over seeds [95% group-bootstrap interval, 300 resamples].\n",
           C.md_table(pd.DataFrame(rows_p))]
    open(f"{R.OUT}/lowfpr_april{a.tag}.md", "w").write("\n".join(md2))
    json.dump({"count": rows_cnt, "tpr_k": rows_k, "pauc": rows_p}, open(f"{R.OUT}/lowfpr_april{a.tag}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
