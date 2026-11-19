#!/usr/bin/env python
"""
Evaluate the pooling_v2 runs exactly as results/pooling was evaluated (scripts/pooling/evaluate_pooling.py,
scripts/go_no_go/common.py), with 10 seeds and the selection rules of the v2 recipe.

    python scripts/pooling_v2/evaluate_v2.py --src <Kaggle output folder> [--tag ""] [--rule auc] [--boot 1000]

Models (v2 names): A flatten; B masked mean; C masked mean + fixed position encoding; B0, C0 = the unmasked B and C
(rerun with the v2 recipe where present in --src; "(v1)" = the runs of results/pooling, old recipe, seeds 0-2).
The epoch of every run is chosen on the January-validation side: --rule auc (primary: highest validation AUC) or
tpr (highest validation TPR at 1% FPR); a second evaluation of A, B, C with the other rule is written as well.
Also: released Nebula, the bag-of-API LightGBM (results/go_no_go/scores, seeds 0-2 reused as seed % 3), the rank
average of each model with the LightGBM, paired group-bootstrap differences, subsets of results/pooling (all, seen,
unseen, 1 / 2-3 / 4-8 chunks, test-3 distance quartiles and window shares, Q2-Q4), per-seed spread, and the
robustness checks in perturb_check.json when present.
Writes results/pooling_v2/tables.md and evaluation.json.
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
from evaluate_pooling import pct_rank, ref_rank  # noqa: E402

OUT = "results/pooling_v2"
WIN = 16


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--rule", default="auc", help="auc | tpr | fixed (use --fixed)")
    ap.add_argument("--fixed", default="", help="regime J: epoch count per variant, e.g. A=2,B=3,C=3 (rule=fixed). The January "
                                                "validation side is in the training set there, so thresholds (b), the Jan-ref "
                                                "rank average and validation-based selection are not computed")
    ap.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    ap.add_argument("--old", default="results/pooling", help="results folder of v1 (reference rows B0 (v1), C0 (v1), A (v1))")
    a = ap.parse_args()

    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    yv = val.label.values
    tb = lambda s: {f: C.thr_from(yv, s, f) for f, _ in C.FPRS}
    seeds_all = [int(s) for s in a.seeds.split(",")]
    fixed = dict(x.split("=") for x in a.fixed.split(",")) if a.fixed else {}
    J = a.rule == "fixed"

    def epoch_of(info, rule, v=None):
        if rule == "auc":
            return info["epoch_by_val_auc"]
        if rule == "tpr":
            return info["epoch_by_val_tpr1"]
        return int(fixed[v])

    def load(v, rule):
        """{seed: (april scores, janval scores, epoch)} for v2 variant v."""
        out = {}
        for s in seeds_all:
            run = f"{v}{a.tag}_s{s}"
            lj, nz = os.path.join(a.src, "logs", f"{run}.json"), os.path.join(a.src, "scores", f"{run}_epochs.npz")
            if not (os.path.exists(lj) and os.path.exists(nz)):
                continue
            info, d = json.load(open(lj)), np.load(nz)
            e = epoch_of(info, rule, v)
            out[s] = (sigmoid(d["april"][e - 1]), sigmoid(d["janval"][e - 1]), e)
        return out

    models, thr_b, epochs_used = {}, {}, {}

    def add(name, sc):
        """sc: {seed: (april, janval)}"""
        models[name] = {s: v[0] for s, v in sc.items()}
        thr_b[name] = {s: tb(v[1]) for s, v in sc.items()}

    for v in ("A", "B", "C", "B0", "C0"):
        d = load(v, a.rule)
        if d:
            add(v, d)
            epochs_used[v] = {s: x[2] for s, x in d.items()}
    present = [v for v in ("A", "B", "C") if v in models]
    seeds = sorted(set.intersection(*[set(models[v]) for v in present]))
    print("variants present:", present, "| seeds present for all of them:", seeds, flush=True)
    # old runs (results/pooling): reference only
    for v1, name in (("A", "A (v1)"), ("B", "B0 (v1)"), ("C", "C0 (v1)")):
        pa, pj = f"{a.old}/scores/pool_{v1}_april.parquet", f"{a.old}/scores/pool_{v1}_janval.parquet"
        if os.path.exists(pa):
            da, dj = pd.read_parquet(pa), pd.read_parquet(pj)
            sc = {}
            for s in sorted(da.seed.unique()):
                xa = da[da.seed == s].set_index("row").score.loc[test.row.values].values
                xj = dj[dj.seed == s].set_index("row").score.loc[val.row.values].values
                sc[int(s)] = (xa, xj)
            add(name, sc)
    # restricted copies for the masked-vs-unmasked control (seeds that exist for B0 / C0)
    for v, v0 in (("B", "B0"), ("C", "C0")):
        if v0 in models:
            ss = sorted(models[v0])
            models[f"{v}[seeds of {v0}]"] = {s: models[v][s] for s in ss if s in models[v]}
            thr_b[f"{v}[seeds of {v0}]"] = {s: thr_b[v][s] for s in ss if s in models[v]}

    neb_a = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    neb_v = C.load_scores("nebula", "janval")[0].loc[val.row.values].values
    lg_a, lg_v = C.load_scores("lgbm_bag_full", "april"), C.load_scores("lgbm_bag_full", "janval")
    lgb = lambda s: (lg_a[s % 3].loc[test.row.values].values, lg_v[s % 3].loc[val.row.values].values)
    models["released Nebula"], thr_b["released Nebula"] = {0: neb_a}, {0: tb(neb_v)}
    models["LightGBM bag of API names"] = {s: lgb(s)[0] for s in seeds}
    thr_b["LightGBM bag of API names"] = {s: tb(lgb(s)[1]) for s in seeds}
    models["released Nebula + LightGBM"] = {s: (pct_rank(neb_a) + pct_rank(lgb(s)[0])) / 2 for s in seeds}
    thr_b["released Nebula + LightGBM"] = {s: tb((pct_rank(neb_v) + pct_rank(lgb(s)[1])) / 2) for s in seeds}
    for v in present:
        jv = {s: x[1] for s, x in load(v, a.rule).items()}
        models[f"{v} + LightGBM"] = {s: (pct_rank(models[v][s]) + pct_rank(lgb(s)[0])) / 2 for s in seeds}
        thr_b[f"{v} + LightGBM"] = {s: tb((pct_rank(jv[s]) + pct_rank(lgb(s)[1])) / 2) for s in seeds}
        if not J:
            models[f"{v} + LightGBM (Jan ref)"] = {s: (ref_rank(models[v][s], jv[s]) + ref_rank(lgb(s)[0], lgb(s)[1])) / 2 for s in seeds}
            thr_b[f"{v} + LightGBM (Jan ref)"] = {s: tb((ref_rank(jv[s], jv[s]) + ref_rank(lgb(s)[1], lgb(s)[1])) / 2) for s in seeds}

    # ---- subsets (as results/pooling)
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

    diffs = [("C", "A"), ("A", "released Nebula"), ("C", "released Nebula"), ("C + LightGBM", "A + LightGBM")] + (
        [("B", "A"), ("C", "B"), ("B", "released Nebula"), ("B + LightGBM", "A + LightGBM"), ("C + LightGBM", "B + LightGBM")]
        if "B" in present else []) + ([] if J else [("B + LightGBM (Jan ref)", "A + LightGBM (Jan ref)"), ("C + LightGBM (Jan ref)", "A + LightGBM (Jan ref)"),
                                ("C + LightGBM (Jan ref)", "B + LightGBM (Jan ref)")])
    for v, v0 in (("B", "B0"), ("C", "C0")):
        if f"{v}[seeds of {v0}]" in models:
            diffs.append((f"{v}[seeds of {v0}]", v0))
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)

    # ---- second selection rule (A, B, C only)
    other = "tpr" if a.rule in ("auc", "fixed") else "auc"
    alt = {}
    for v in (() if J else ("A", "B", "C")):
        d = load(v, other)
        alt[f"{v} [epoch by validation {'TPR@1%' if other == 'tpr' else 'AUC'}]"] = d
    alt_models = {k: {s: x[0] for s, x in d.items()} for k, d in alt.items()}
    alt_thr = {k: {s: tb(x[1]) for s, x in d.items()} for k, d in alt.items()}
    ka = list(alt_models)
    mk2 = [m for m in masks if m[0] in ("all", "unseen") or m[0].startswith("distance Q1") or m[0].startswith("distance Q2-Q4")]
    if not J:
        p2, c2, d2, mk2 = C.evaluate_models(test, alt_models, alt_thr, n_boot=a.boot,
                                            diffs=[(ka[1], ka[0]), (ka[2], ka[0]), (ka[2], ka[1])], masks=mk2)

    names = [n for n, _ in masks]
    main_models = present + [f"{v} + LightGBM" for v in present] + (
        [] if J else [f"{v} + LightGBM (Jan ref)" for v in present]) + [
        "released Nebula", "LightGBM bag of API names", "released Nebula + LightGBM"]
    refs = [m for m in ("B0", "C0", "A (v1)", "B0 (v1)", "C0 (v1)") if m in models]
    t_all = C.result_tables(point, ci, masks, main_models + refs, sub_filter=["all"]).drop(columns=["subset"])
    t_diff = C.diff_table(point, dci, masks, diffs)
    keep = ["AUC", "TPR@1% (a)", "TPR@1% (b)"]
    t_sub = C.result_tables(point, ci, masks, present + ["released Nebula", "LightGBM bag of API names"] + refs)[["subset", "model", "n (malware)"] + keep]
    t_sub2 = C.result_tables(point, ci, masks, [m for m in main_models if "+ LightGBM" in m and "released" not in m])[["subset", "model", "n (malware)"] + keep]
    if not J:
        t_alt = C.result_tables(p2, c2, mk2, ka)[["subset", "model", "n (malware)"] + keep]
        t_alt_d = C.diff_table(p2, d2, mk2, [(ka[1], ka[0]), (ka[2], ka[0]), (ka[2], ka[1])])
    if J:                                    # validation reports are in the training set: no January threshold (b)
        keep = ["AUC", "TPR@1% (a)", "TPR@0.1% (a)"]
        drop_b = lambda df: df[[c for c in df.columns if "(b)" not in c]]
        t_sub = C.result_tables(point, ci, masks, present + ["released Nebula", "LightGBM bag of API names"] + refs)[["subset", "model", "n (malware)"] + keep]
        t_sub2 = C.result_tables(point, ci, masks, [m for m in main_models if "+ LightGBM" in m and "released" not in m])[["subset", "model", "n (malware)"] + keep]
        t_all, t_diff = drop_b(t_all), drop_b(t_diff)
        t_all = t_all.drop(columns=[c for c in t_all.columns if c.startswith("FPR")])

    # ---- seed spread
    sp = []
    for m in present + [r for r in refs]:
        per = point[m]["_seeds"]
        for k, tag in (("auc", "AUC"), ("tpr1%_a", "TPR@1% (a)")) + (() if J else (("tpr1%_b", "TPR@1% (b)"),)):
            v = np.array([p["all"][k] for p in per])
            sp.append({"model": m, "metric": tag, "seeds": len(v), "mean": f"{v.mean():.4f}" if k == "auc" else f"{100 * v.mean():.1f}%",
                       "std": f"{v.std(ddof=1):.4f}" if k == "auc" else f"{100 * v.std(ddof=1):.1f}",
                       "min": f"{v.min():.4f}" if k == "auc" else f"{100 * v.min():.1f}%",
                       "max": f"{v.max():.4f}" if k == "auc" else f"{100 * v.max():.1f}%",
                       "per seed": " / ".join((f"{x:.4f}" if k == "auc" else f"{100 * x:.1f}") for x in v)})
    t_spread = pd.DataFrame(sp)

    # ---- gap Q1 vs Q2-Q4
    gap = []
    for m in present + ["released Nebula", "LightGBM bag of API names"] + refs:
        g = {"model": m}
        for k, tag in (("tpr1%_a", "TPR@1% (a)"),) + (() if J else (("tpr1%_b", "TPR@1% (b)"),)):
            q1, q2 = point[m][qm[0][0]][k], point[m][q24[0]][k]
            g[f"{tag} Q1"], g[f"{tag} Q2-Q4"] = C.fmt(k, q1), C.fmt(k, q2)
            g[f"{tag} gap Q1 − Q2-Q4 (points)"] = f"{100 * (q1 - q2):+.1f}"
        gap.append(g)
    t_gap = pd.DataFrame(gap)

    # ---- selected epochs
    ep = []
    for v, d in epochs_used.items():
        ep.append({"model": v, "rule": a.rule, "epoch per seed": " / ".join(str(d[s]) for s in sorted(d)),
                   "mean epoch": f"{np.mean(list(d.values())):.1f}"})
    for k, d in alt.items():
        ep.append({"model": k.split(" ")[0], "rule": other, "epoch per seed": " / ".join(str(d[s][2]) for s in sorted(d)),
                   "mean epoch": f"{np.mean([x[2] for x in d.values()]):.1f}"})
    t_ep = pd.DataFrame(ep)

    md = ["## Overall (all April reports)\n", "Mean over seeds [95% group-bootstrap interval]. B0 and C0: unmasked mean pooling "
          "(v2 recipe where listed without \"(v1)\"; \"(v1)\" = results/pooling).\n", C.md_table(t_all),
          "\n## Seed spread (all April reports)\n", C.md_table(t_spread),
          "\n## Selected epochs\n", C.md_table(t_ep),
          "\n## Distance quartiles: gap between the nearest quartile and the rest\n", C.md_table(t_gap),
          "\n## Paired differences (all subsets)\n", "Difference of the seed means with the 95% interval of the paired group bootstrap; "
          "TPR in percentage points.\n", C.md_table(t_diff),
          "\n## Results by subset\n", C.md_table(t_sub), "\n## Rank average with LightGBM, by subset\n", C.md_table(t_sub2),
          ] + ([] if J else [f"\n## Epoch chosen by validation {'TPR@1%' if other == 'tpr' else 'AUC'} (A, B, C)\n", C.md_table(t_alt),
          "\nPaired differences:\n", C.md_table(t_alt_d)])
    open(f"{OUT}/tables{'_J' if J else ''}.md", "w").write("\n".join(md))
    ev = {"seeds": seeds, "rule": a.rule, "tag": a.tag, "n_boot": a.boot, "quartiles_distance": qd.tolist(),
          "point": {m: {s: {k: float(v) for k, v in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point},
          "per_seed_all": {m: [{k: float(v) for k, v in p["all"].items()} for p in point[m]["_seeds"]] for m in point},
          "diffs": {f"{x} - {y}|{s}|{k}": [float(point[x][s][k] - point[y][s][k]), *map(float, dci[(x, y, s, k)])]
                    for x, y in diffs for s in names for k in C.METRIC_COLS}}
    json.dump(ev, open(f"{OUT}/evaluation{'_J' if J else ''}.json", "w"), indent=1)
    print("wrote", f"{OUT}/tables{'_J' if J else ''}.md", f"{OUT}/evaluation{'_J' if J else ''}.json")


if __name__ == "__main__":
    main()
