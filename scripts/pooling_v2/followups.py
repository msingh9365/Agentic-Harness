#!/usr/bin/env python
"""
Follow-up checks on the pooling_v2 runs that need no new training (results/pooling_v2/followups_*.md).

    python scripts/pooling_v2/followups.py ensemble   --src <regime S output> [--src-j <regime J output>]
    python scripts/pooling_v2/followups.py same_epoch --src <regime S output>

ensemble   : average the logits of the 10 seeds of a variant (each seed at its validation-AUC epoch; regime J:
             the fixed epoch count) and evaluate the averaged score once. Seed noise is averaged out, so A, B, C
             and the released Nebula are compared without the seed spread. Group bootstrap as everywhere else.
same_epoch : A, B, C scored after the SAME number of epochs (1..10), to separate "how long it trained" from the
             variant. Per-epoch means over seeds, seed-paired differences (bootstrap over the 10 seeds), and the
             group bootstrap at epochs 1, 5 and 10.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
import common as C  # noqa: E402

OUT = "results/pooling_v2"
SEEDS = list(range(10))


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def masks_for(test):
    """all, unseen, distance Q1, distance Q2-Q4 (test 3 definitions, as evaluate_v2.py)."""
    seqdf = pd.read_parquet(f"{C.OUT}/scores/test3_unseen_sequences.parquet").set_index("hash_apis")
    rep_d = test.hash_apis.map(seqdf.nearest_dist).values.astype(float)
    qd = np.nanpercentile(seqdf.nearest_dist.values, [25, 50, 75])
    q1 = (rep_d <= qd[0]) & ~np.isnan(rep_d)
    q24 = (rep_d > qd[0]) & ~np.isnan(rep_d)
    return [("all", np.ones(len(test), bool)), ("seen", test.seen.values), ("unseen", ~test.seen.values),
            (f"distance Q1 (≤ {qd[0]:.3f})", q1), ("distance Q2-Q4 (farther three quartiles)", q24)]


def load_epochs(src, run):
    d = np.load(os.path.join(src, "scores", f"{run}_epochs.npz"))
    return d["april"], d["janval"]


def tpr_a(y, s, fpr=0.01):
    t = C.thr_from(y, s, fpr)
    return float(((s > t) & (y == 1)).sum() / max(1, (y == 1).sum()))


def auc(y, s):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, s))


def seed_boot(x, n=20000, seed=0):
    rng = np.random.default_rng(seed)
    b = rng.choice(x, (n, len(x))).mean(1)
    return float(x.mean()), [float(v) for v in np.percentile(b, [2.5, 97.5])]


def table(point, ci, masks, order, cols):
    rows = []
    for sub, _ in masks:
        for m in order:
            r = {"subset": sub, "model": m}
            for k in cols:
                lo, hi = ci[(m, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt(k, point[m][sub][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
            rows.append(r)
    return pd.DataFrame(rows)


def cmd_ensemble(a, test, val):
    yv = val.label.values
    tb = lambda s: {f: C.thr_from(yv, s, f) for f, _ in C.FPRS}
    masks = masks_for(test)
    neb_a = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    neb_v = C.load_scores("nebula", "janval")[0].loc[val.row.values].values
    models, thr_b, single = {"released Nebula": {0: neb_a}}, {"released Nebula": {0: tb(neb_v)}}, {}
    for v in ("A", "B", "C"):                                   # regime S: epoch chosen on validation AUC per seed
        za, zv = [], []
        for s in SEEDS:
            ap_, jv_ = load_epochs(a.src, f"{v}_s{s}")
            e = json.load(open(os.path.join(a.src, "logs", f"{v}_s{s}.json")))["epoch_by_val_auc"]
            za.append(ap_[e - 1]); zv.append(jv_[e - 1])
        models[f"{v} ensemble (S)"] = {0: sigmoid(np.mean(za, 0))}
        thr_b[f"{v} ensemble (S)"] = {0: tb(sigmoid(np.mean(zv, 0)))}
        single[f"{v} (S)"] = (float(np.mean([auc(test.label.values, z) for z in za])),
                              float(np.mean([tpr_a(test.label.values, z) for z in za])))
    diffs = [("C ensemble (S)", "A ensemble (S)"), ("B ensemble (S)", "A ensemble (S)"), ("C ensemble (S)", "B ensemble (S)"),
             ("A ensemble (S)", "released Nebula"), ("C ensemble (S)", "released Nebula")]
    order = ["A ensemble (S)", "B ensemble (S)", "C ensemble (S)"]
    if a.src_j:                                                 # regime J: fixed epoch count, validation is in-sample
        fixed = dict(x.split("=") for x in a.fixed_j.split(","))
        for v in fixed:
            za = []
            for s in SEEDS:
                ap_, _ = load_epochs(a.src_j, f"{v}_all_s{s}")
                za.append(ap_[int(fixed[v]) - 1])
            models[f"{v} ensemble (J)"] = {0: sigmoid(np.mean(za, 0))}
            thr_b[f"{v} ensemble (J)"] = {0: {f: np.inf for f, _ in C.FPRS}}       # no January threshold in regime J
            single[f"{v} (J)"] = (float(np.mean([auc(test.label.values, z) for z in za])),
                                  float(np.mean([tpr_a(test.label.values, z) for z in za])))
            order.append(f"{v} ensemble (J)")
        diffs += [("C ensemble (J)", "A ensemble (J)"), ("A ensemble (J)", "released Nebula"), ("C ensemble (J)", "released Nebula")]
    order.append("released Nebula")
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)
    cols = ["auc", "tpr1%_a", "tpr0.1%_a"]
    t = table(point, ci, masks, order, cols)
    rows = []
    for x, y in diffs:
        for sub, _ in masks:
            r = {"difference": f"{x} − {y}", "subset": sub}
            for k in cols + (["tpr1%_b"] if "(J)" not in x + y else []):
                lo, hi = dci[(x, y, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x][sub][k] - point[y][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            rows.append(r)
    td = pd.DataFrame(rows).fillna("—")
    sg = pd.DataFrame([{"model": k, "mean single-seed AUC": f"{v[0]:.4f}", "mean single-seed TPR@1% (a)": f"{100 * v[1]:.1f}%",
                        "ensemble AUC": f"{point[k.replace(' (', ' ensemble (')]['all']['auc']:.4f}",
                        "ensemble TPR@1% (a)": f"{100 * point[k.replace(' (', ' ensemble (')]['all']['tpr1%_a']:.1f}%"}
                       for k, v in single.items()])
    md = ["# Follow-up: seed ensembles\n",
          "The logits of the 10 seeds of a variant are averaged and the averaged score is evaluated once. (S) = trained on the "
          "January train side, each seed at its validation-AUC epoch; (J) = trained on all of January for the fixed epoch count "
          f"({a.fixed_j if a.src_j else 'not run'}). Thresholds: (a) from the April benign scores. 95% group-bootstrap intervals.\n",
          "## Single seeds versus the ensemble (all April reports)\n", C.md_table(sg),
          "\n## Ensembles and the released Nebula\n", C.md_table(t), "\n## Paired differences\n", C.md_table(td)]
    open(f"{OUT}/followups_ensemble.md", "w").write("\n".join(md))
    json.dump({"point": {m: {s: {k: float(x) for k, x in d.items()} for s, d in point[m].items() if s != "_seeds"} for m in point},
               "single": single}, open(f"{OUT}/followups_ensemble.json", "w"), indent=1)
    print("\n".join(md[4:6])); print(C.md_table(td[td.subset.isin(["all", "distance Q2-Q4 (farther three quartiles)"])]))


def cmd_same_epoch(a, test, val):
    ya, yv = test.label.values, val.label.values
    E = 10
    A = {v: [load_epochs(a.src, f"{v}_s{s}") for s in SEEDS] for v in ("A", "B", "C")}
    m_auc = {v: np.array([[auc(ya, A[v][s][0][e]) for e in range(E)] for s in SEEDS]) for v in A}
    m_tpr = {v: np.array([[tpr_a(ya, A[v][s][0][e]) for e in range(E)] for s in SEEDS]) for v in A}
    v_auc = {v: np.array([[auc(yv, A[v][s][1][e]) for e in range(E)] for s in SEEDS]) for v in A}
    rows, drows = [], []
    for e in range(E):
        r = {"epochs": e + 1}
        for v in "ABC":
            r[f"{v} April AUC"] = f"{m_auc[v][:, e].mean():.4f}"
        for v in "ABC":
            r[f"{v} TPR@1% (a)"] = f"{100 * m_tpr[v][:, e].mean():.1f}%"
        for v in "ABC":
            r[f"{v} val AUC"] = f"{v_auc[v][:, e].mean():.4f}"
        rows.append(r)
        d = {"epochs": e + 1}
        for x, y in (("C", "B"), ("C", "A"), ("B", "A")):
            mu, ci = seed_boot(m_auc[x][:, e] - m_auc[y][:, e])
            d[f"{x} − {y} AUC"] = f"{mu:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]"
            mu, ci = seed_boot(100 * (m_tpr[x][:, e] - m_tpr[y][:, e]))
            d[f"{x} − {y} TPR@1% (a), points"] = f"{mu:+.1f} [{ci[0]:+.1f}, {ci[1]:+.1f}]"
        drows.append(d)
    t1, t2 = pd.DataFrame(rows), pd.DataFrame(drows)
    # group bootstrap at epochs 1, 5, 10
    tb = lambda s: {f: C.thr_from(yv, s, f) for f, _ in C.FPRS}
    masks = [m for m in masks_for(test) if m[0] in ("all", "distance Q2-Q4 (farther three quartiles)")]
    models, thr_b, diffs = {}, {}, []
    for e in (1, 5, 10):
        for v in "ABC":
            models[f"{v} @ {e}"] = {s: sigmoid(A[v][s][0][e - 1]) for s in SEEDS}
            thr_b[f"{v} @ {e}"] = {s: tb(sigmoid(A[v][s][1][e - 1])) for s in SEEDS}
        diffs += [(f"C @ {e}", f"B @ {e}"), (f"C @ {e}", f"A @ {e}"), (f"B @ {e}", f"A @ {e}")]
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, n_boot=a.boot, diffs=diffs, masks=masks)
    g = []
    for x, y in diffs:
        for sub, _ in masks:
            r = {"difference (epochs)": f"{x} − {y}", "subset": sub}
            for k in ("auc", "tpr1%_a", "tpr1%_b"):
                lo, hi = dci[(x, y, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt_d(k, point[x][sub][k] - point[y][sub][k])} [{C.fmt_d(k, lo)}, {C.fmt_d(k, hi)}]"
            g.append(r)
    t3 = pd.DataFrame(g)
    md = ["# Follow-up: A, B and C after the same number of epochs\n",
          "Regime S (January train side), 10 seeds, no epoch selection: every model is scored after exactly this many epochs. "
          "TPR with the April threshold (a).\n", "## Mean over seeds, by epoch\n", C.md_table(t1),
          "\n## Seed-paired differences, by epoch\n", "Mean over the 10 seeds [95% interval from a bootstrap over seeds only; "
          "sampling of April reports is not in these intervals].\n", C.md_table(t2),
          "\n## Group bootstrap at epochs 1, 5 and 10\n", "Difference of the seed means [95% interval, bootstrap over April "
          "groups]; TPR in points.\n", C.md_table(t3)]
    open(f"{OUT}/followups_same_epoch.md", "w").write("\n".join(md))
    json.dump({"april_auc": {v: m_auc[v].tolist() for v in m_auc}, "april_tpr1_a": {v: m_tpr[v].tolist() for v in m_tpr},
               "val_auc": {v: v_auc[v].tolist() for v in v_auc}}, open(f"{OUT}/followups_same_epoch.json", "w"), indent=1)
    print(C.md_table(t1[[c for c in t1.columns if "val" not in c]])); print(C.md_table(t2[[c for c in t2.columns if "TPR" not in c]]))
    print(C.md_table(t3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["ensemble", "same_epoch"])
    ap.add_argument("--src", required=True)
    ap.add_argument("--src-j", default=None)
    ap.add_argument("--fixed-j", default="A=1,C=10")
    ap.add_argument("--boot", type=int, default=C.N_BOOT)
    a = ap.parse_args()
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    (cmd_ensemble if a.cmd == "ensemble" else cmd_same_epoch)(a, test, val)


if __name__ == "__main__":
    main()
