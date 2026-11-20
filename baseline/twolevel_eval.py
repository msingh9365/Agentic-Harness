"""
Clean April evaluation of ATT+bal-2L (A) and its control B (NOTES 19.6 / 19.12).   (OURS)

    python -m baseline.twolevel_eval --a-dir <A cell folder> --b-dir <B cell folder> --out results/attbal_2l/clean [--boot 1000]

Reads April / validation logits of the CHOSEN cells (epoch 1 of A_warm_lr1e-3 and B_lr2e-3; the choice is in results/attbal_2l/selection.json), and the logits of ATT+bal (REPORT 5.10, results/att_bal/attbal) and v2-PE
(results/logits/v2_pe.npz). Writes tables.md, per_model.json, bootstrap.json, cluster.json, family.json. Scores only.
Statistics = EVAL_PROTOCOL.md 5: stratified bootstrap (gap_final.bootstrap: 1,000 resamples, numpy seed 0), per-seed paired differences, claim rule (CI excludes 0 and >= 7 of 10 seeds with the same sign), the
ensemble next to it, and the cluster bootstrap over hash_apis groups (cells (group, class) resampled; numpy seed 0).
Per family: TPR at the 1% FPR threshold of each model and seed (benign logit at rank floor(0.01 n)). Coinminer cluster = the 265 April reports with hash_apis d91b96b4... (baseline/coinminer.py).
"""
import argparse
import json
import os

import numpy as np
import pandas as pd

from baseline import att_report as AR, common as C, gap_final, padtest
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

ROOT = AR.ROOT
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
LAB = {"a2l": "**ATT+bal-2L (A)**", "b2l": "B: 2L without padding", "attbal": "ATT+bal", "v2_pe": "v2-PE"}
CLUSTER_HASH = "d91b96b425798fc031fc1b3c8cdcdf3f998bd9b3"
PAIRS = [("a2l", "attbal"), ("a2l", "v2_pe"), ("a2l", "b2l"), ("b2l", "v2_pe"), ("b2l", "attbal")]


def april_meta():
    """family and duplicate-group id of every April report in our row order."""
    meta = pd.read_csv(os.path.join(ROOT, "results", "hier", "data", "meta.csv"))
    rm = np.load(os.path.join(ROOT, "results", "padding", "row_map.npz"))
    a = meta.iloc[rm["test"]].reset_index(drop=True)
    r = pd.read_csv(os.path.join(ROOT, "results", "misses", "reports.csv"), usecols=["split", "sample_id", "hash_apis"]).drop_duplicates("sample_id")
    h = r[r.split == "testset"].set_index("sample_id").loc[a.id.values, "hash_apis"].values
    return a.family.values, h, pd.factorize(h)[0]


def load(a_dir, b_dir, epoch_a=1, epoch_b=1):
    test, val = {}, {}
    for k, d, e in (("a2l", a_dir, epoch_a), ("b2l", b_dir, epoch_b)):
        test[k] = np.stack([np.load(os.path.join(d, f"seed{s}_epoch{e}_test_logits.npy")).astype(np.float64) for s in SEEDS])
        val[k] = np.stack([np.load(os.path.join(d, f"seed{s}_epoch{e}_val_logits.npy")).astype(np.float64) for s in SEEDS])
    test["v2_pe"], val["v2_pe"] = AR.load_family("v2_pe", os.path.join(ROOT, "results", "att_bal"))
    # ATT+bal (REPORT 5.10, lr 2e-3, epoch 2): the April logits are row 0 (unedited) of the scoring file of the attack run (the .npy logits are not in the repository); no validation logits are kept for it
    z = np.load(os.path.join(ROOT, "results", "review", "attack", "a3pad_attbal.npz"))
    test["attbal"] = np.stack([z[f"seed{s}"][0].astype(np.float64) for s in SEEDS])
    val["attbal"] = None
    return test, val


def cluster_bootstrap(y, groups, Z, pairs, n_boot):
    """cells (group, class) resampled; draws of every metric of C.roc_summary for the mean over seeds."""
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    rng = np.random.default_rng(0)
    draws = {p: [] for p in pairs}
    for b in range(n_boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        m = {f: np.mean([C.roc_summary(y[sel], z[sel]) for z in Z[f]], axis=0) for f in Z}
        for p in pairs:
            draws[p].append(m[p[0]] - m[p[1]])
        if b % 100 == 0:
            print(f"  cluster bootstrap {b}/{n_boot}", flush=True)
    return {p: np.array(v) for p, v in draws.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a-dir", required=True)
    ap.add_argument("--b-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--epoch-a", type=int, default=1)
    ap.add_argument("--epoch-b", type=int, default=1)
    a = ap.parse_args()
    lab = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))
    y_test, y_val = lab["y_test"].astype(int), lab["y_val"].astype(int)
    test, val = load(a.a_dir, a.b_dir, a.epoch_a, a.epoch_b)
    fam, hsh, groups = april_meta()
    assert len(fam) == len(y_test) and len(set(groups)) == 2509
    fams = list(LAB)
    T = {f: metrics_of(y_test, test[f]) for f in fams}
    V = {f: metrics_of(y_val, val[f]) for f in fams if val[f] is not None}
    ens = {f: C.binary_metrics(y_test, test[f].mean(0), decision=0.0) for f in fams}
    bs = gap_final.bootstrap(y_test, {f: test[f] for f in fams}, a.boot, pairs=PAIRS)
    L = ["### Clean April test: per-seed mean ± std (10 seeds, logit-ranked)", ""]
    L.append(md([[LAB[f], len(T[f]["auc"])] + [ms(T[f][k], d) for k, _, d in COLS] for f in fams], ["model", "n"] + [c[1] for c in COLS]))
    L += ["", "10-seed ensembles (mean logit):", "", md([[LAB[f], f"{ens[f]['tpr@0.001']:.3f}", f"{ens[f]['tpr@0.01']:.3f}", f"{ens[f]['auc']:.4f}", f"{ens[f]['f1@0.5']:.3f}", f"**{ens[f]['pauc@0.01']:.3f}**", f"{ens[f]['pauc@0.001']:.3f}"] for f in fams],
                                                  ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1", "**pAUC@1e-2**", "pAUC@1e-3"])]
    L += ["", "Validation slice (7,530 reports, clean; no validation logits are kept for ATT+bal): per-seed mean ± std", "", md([[LAB[f], len(V[f]["auc"])] + [ms(V[f][k], d) for k, _, d in COLS] for f in fams if f in V], ["model", "n"] + [c[1] for c in COLS])]
    L += ["", f"### Differences, stratified bootstrap ({a.boot} resamples, numpy seed 0; points ×100; same resamples for all models)", ""]
    rows, verdicts = [], {}
    for (n, b) in PAIRS:
        for kind, kl in (("ps", "per-seed means"), ("ens", "10-seed ensembles")):
            for k, lbl, d in BOOT:
                e = bs[kind]["diffs"][f"{n} - {b}"][k]
                rows.append([f"{n} − {b}", kl, lbl, f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]" + (" **CI excludes 0**" if e["resolved"] else " CI contains 0")])
        verdicts[f"{n} vs {b}"] = AR.verdict(bs["ps"]["diffs"][f"{n} - {b}"][PRIMARY], T[n][PRIMARY] - T[b][PRIMARY], n)
    L.append(md(rows, ["difference", "statistic", "metric", "difference in points, 95% CI"]))
    L += ["", "### Per-seed paired differences of the primary metric (same seed index; points ×100)", ""]
    prow = []
    for (n, b) in PAIRS:
        dd = T[n][PRIMARY] - T[b][PRIMARY]
        prow.append([f"{n} − {b}"] + [f"{100 * x:+.1f}" for x in dd] + [f"{100 * dd.mean():+.2f} ± {100 * dd.std(ddof=1):.2f}", f"{int((dd > 0).sum())}/10"])
    L.append(md(prow, ["pair"] + [f"s{s}" for s in SEEDS] + ["mean ± std", "seeds > 0"]))
    L += ["", "**Claim rule (EVAL_PROTOCOL.md 5) on pAUC@1e-2, stratified bootstrap of the per-seed means:**", ""] + [f"- {k}: {v}" for k, v in verdicts.items()]
    # cluster bootstrap
    cd = cluster_bootstrap(y_test, groups, {f: test[f] for f in fams}, PAIRS, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    cl, crows = {}, []
    for (n, b) in PAIRS:
        for key, lbl in (("pauc@0.01", "pAUC@1e-2 (primary)"), ("tpr@0.01", "TPR@1e-2"), ("tpr@0.001", "TPR@1e-3"), ("auc", "AUC")):
            j = idx_of[key]
            d = T[n][key] - T[b][key]
            lo, hi = np.percentile(cd[(n, b)][:, j], [2.5, 97.5])
            pos, neg = int((d > 0).sum()), int((d < 0).sum())
            ok = (lo > 0 or hi < 0) and max(pos, neg) >= 7
            cl[f"{n}-{b}|{key}"] = {"mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "seeds_above_0": pos, "resolved": bool(ok)}
            crows.append([f"{n} − {b}", lbl, f"{100 * d.mean():+.2f}", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{pos}/10", ("**meets the rule**" if ok else "not resolved") if key == "pauc@0.01" else ("CI excludes 0 (descriptive)" if (lo > 0 or hi < 0) else "CI contains 0 (descriptive)")])
    L += ["", "### Cluster bootstrap over hash_apis groups (2,509 groups; cells (group, class) resampled; points ×100)", "", md(crows, ["difference", "metric", "mean difference", "95% CI (cluster)", "seeds > 0", "outcome"])]
    # per family and the coinminer cluster
    thr = {f: np.array([padtest.thresholds(test[f][s], y_test, 0.01) for s in SEEDS]) for f in fams}
    flag = {f: test[f] > thr[f][:, None] for f in fams}
    fam_names = sorted(set(fam))
    frows, fout = [], {}
    for g in fam_names:
        m = fam == g
        r = [g, int(m.sum())]
        for f in fams:
            v = flag[f][:, m].mean(1)
            fout.setdefault(g, {})[f] = [float(v.mean()), float(v.std(ddof=1))]
            r.append(f"{100 * v.mean():.1f} ± {100 * v.std(ddof=1):.1f}")
        frows.append(r)
    L += ["", "### Detection rate per family at the 1% FPR threshold of each model and seed (April; mean ± std over 10 seeds, %). `clean` and `windows_syswow64` rows are false-positive rates.", "", md(frows, ["family", "n"] + [LAB[f] for f in fams])]
    cm = hsh == CLUSTER_HASH
    coin = fam == "coinminer"
    rest = coin & ~cm
    crow, cout = [], {}
    for f in fams:
        sh = flag[f][:, cm].mean(1)
        margin = np.array([np.median(test[f][s][cm]) - thr[f][s] for s in SEEDS])
        cout[f] = {"cluster_share_flagged_per_seed": sh.tolist(), "seeds_flagging": int((sh > 0.5).sum()), "median_margin_per_seed": margin.tolist(), "other_coinminer_tpr": [float(flag[f][:, rest].mean(1).mean()), float(flag[f][:, rest].mean(1).std(ddof=1))],
                   "all_coinminer_tpr": [float(flag[f][:, coin].mean(1).mean()), float(flag[f][:, coin].mean(1).std(ddof=1))]}
        crow.append([LAB[f], f"{int((sh > 0.5).sum())}/10", f"{np.median(margin):+.1f} (IQR {np.percentile(margin, 25):+.1f} to {np.percentile(margin, 75):+.1f})", f"{100 * cout[f]['other_coinminer_tpr'][0]:.1f} ± {100 * cout[f]['other_coinminer_tpr'][1]:.1f}",
                     f"{100 * cout[f]['all_coinminer_tpr'][0]:.1f} ± {100 * cout[f]['all_coinminer_tpr'][1]:.1f}"])
    L += ["", f"### The coinminer cluster (hash_apis d91b96b4…, {int(cm.sum())} April reports with the same first 512 tokens; one input counted {int(cm.sum())} times)", "",
          "Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold. Margin = median cluster logit minus the threshold (positive = flagged).", "",
          md(crow, ["model", "seeds flagging the cluster", "median margin (logit)", f"TPR of the other {int(rest.sum())} coinminer reports (%)", f"TPR of all {int(coin.sum())} coinminer reports (%)"])]
    os.makedirs(a.out, exist_ok=True)
    text = "\n".join(L)
    open(os.path.join(a.out, "tables.md"), "w").write(text + "\n")
    json.dump({"test": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in T.items()}, "validation": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in V.items()},
               "ensemble_test": {f: {k: v for k, v in m.items() if k != "roc_on_grid"} for f, m in ens.items()}, "claims": verdicts}, open(os.path.join(a.out, "per_model.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap.json"), "w"), indent=1)
    json.dump(cl, open(os.path.join(a.out, "cluster.json"), "w"), indent=1)
    json.dump({"family": fout, "coinminer_cluster": cout}, open(os.path.join(a.out, "family.json"), "w"), indent=1)
    print(text)


if __name__ == "__main__":
    main()
