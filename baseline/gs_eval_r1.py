"""
April evaluation of item R1 (NOTES 30.3; April opening 32): the windowed M3 (r1) next to the final M1 (f1), M3 (f3), M4 (f4) and the test-time multi-window baseline of M3 (mw, NOTES 27.2); the tables of Stage I.   (OURS)

    python -m baseline.gs_eval_r1 --runs <dir(s) with r1fin/seed<k>_epoch<E>_test_logits.npy> --epochs E --out results/groupsplit/r1 [--boot 1000]

r1: 10 seeds, the chosen variant and epochs (results/groupsplit/r1/choice.json), all January, April logits after the last epoch only. f1, f3, f4 = Stage I models (stored logits); mw = the unedited row of the stored multi-window
scores of M3 (results/groupsplit/stage_fgh/part3/combined/scores_m3_mw.npz). Pairs (both bootstraps, seeds each way, resolved = the cluster interval of pAUC@1e-2 excludes 0): r1 - f3, r1 - f4, r1 - mw, r1 - f1.
STOP (STOP.txt, exit) if an r1 seed has April AUC < 0.6.
"""
import argparse
import json
import os

import numpy as np

from baseline import att_report as AR, common as C, gap_final, padtest
from baseline.twolevel_eval import CLUSTER_HASH, april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

ROOT = AR.ROOT
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
NAME = {"f1": "M1 Nebula (final)", "f3": "M3 ATT+bal (final)", "f4": "M4 ATT+bal-2L (final)", "mw": "M3 + test-time multi-window max", "r1": "R1 windowed M3"}
STAGE_I = os.path.join(ROOT, "results", "groupsplit", "stage_fgh", "stage_i", "logits_fixed_models.npz")


def load(runs, tag, epoch, n_epochs, variant, expect_train=75298):
    """the M3-2ep run folder: exactly one epoch of test logits (epoch 2), settings asserted"""
    for s in SEEDS:
        have = sorted(int(f.split("_epoch")[1].split("_")[0]) for f in os.listdir(os.path.join(runs, tag)) if f.startswith(f"seed{s}_epoch") and f.endswith("_test_logits.npy"))
        assert have == [epoch], (tag, s, have)
        r = json.load(open(os.path.join(runs, tag, f"seed{s}.json")))
        assert r["epochs"] == n_epochs and r["n_train"] == expect_train and r["tokenizer"] == variant and r["split_hash_asserted"], (tag, s, r["epochs"], r["n_train"], r["tokenizer"])
    return np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{epoch}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--tag", default="r1fin")
    ap.add_argument("--allow-collapsed", action="store_true", help="the STOP rule (a seed with April AUC < 0.6) is reported and written to <out>/STOP.txt but the descriptive tables are still produced with ALL seeds (no seed is excluded)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    fam, hsh, groups = april_meta()
    assert len(set(groups)) == 2509 and len(y) == len(fam)
    z1 = np.load(STAGE_I)
    r1 = {}
    for d in a.runs:
        for s_ in SEEDS:
            p = os.path.join(d, a.tag, f"seed{s_}_epoch{a.epochs}_test_logits.npy")
            if os.path.exists(p):
                rj = json.load(open(os.path.join(d, a.tag, f"seed{s_}.json")))
                assert rj["epochs"] == a.epochs and rj["n_train"] == 75298 and rj["tokenizer"] == "bpe50k_fix" and rj["mode"] == "final", (d, s_)
                have = [f for f in os.listdir(os.path.join(d, a.tag)) if f.startswith(f"seed{s_}_epoch") and f.endswith("_test_logits.npy")]
                assert len(have) == 1, (d, s_, have)
                assert s_ not in r1, f"seed {s_} present twice"
                r1[s_] = np.load(p).astype(np.float64).reshape(-1)
    assert sorted(r1) == SEEDS, f"seeds present: {sorted(r1)}"
    mw = np.load(os.path.join(ROOT, "results", "groupsplit", "stage_fgh", "part3", "combined", "scores_m3_mw.npz"))
    mwn = [str(n) for n in mw["names"]]
    test = {"f1": z1["f1_test"].astype(np.float64), "f3": z1["f3_test"].astype(np.float64), "f4": z1["f4_test"].astype(np.float64), "mw": np.stack([mw[f"seed{s_}"][mwn.index("unedited")].astype(np.float64) for s_ in SEEDS]), "r1": np.stack([r1[s_] for s_ in SEEDS])}
    from sklearn.metrics import roc_auc_score
    for k in test:
        assert test[k].shape == (len(SEEDS), len(y)), (k, test[k].shape)
    aucs = [roc_auc_score(y, test["r1"][s_]) for s_ in SEEDS]
    os.makedirs(a.out, exist_ok=True)
    if min(aucs) < 0.6:
        open(os.path.join(a.out, "STOP.txt"), "w").write(f"STOP: r1 seeds with April AUC < 0.6: {[s_ for s_ in SEEDS if aucs[s_] < 0.6]} (min {min(aucs):.3f})\n")
        raise SystemExit("STOP: a windowed-M3 seed has April AUC < 0.6")
    order = ["f1", "f3", "f4", "mw", "r1"]
    lab = lambda k: ("**" + NAME[k] + "**") if k == "r1" else NAME[k]
    pairs = [("r1", "f3"), ("r1", "f4"), ("r1", "mw"), ("r1", "f1")]
    Z = {k: test[k] for k in order}
    T = {k: metrics_of(y, Z[k]) for k in Z}
    ens = {k: C.binary_metrics(y, Z[k].mean(0), decision=0.0) for k in Z}
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    L = [f"### Clean April test, 10 seeds each, one evaluation per model (the windowed M3 next to M1, M3, M4 and the test-time multi-window baseline): per-seed mean ± std", "",
         md([[lab(k), len(T[k]["auc"])] + [ms(T[k][c], d) for c, _, d in COLS] for k in Z], ["model", "n"] + [c[1] for c in COLS]), "", "10-seed ensembles (mean logit):", "",
         md([[lab(k), f"{ens[k]['tpr@0.001']:.3f}", f"{ens[k]['tpr@0.01']:.3f}", f"{ens[k]['auc']:.4f}", f"{ens[k]['f1@0.5']:.3f}", f"**{ens[k]['pauc@0.01']:.3f}**", f"{ens[k]['pauc@0.001']:.3f}"] for k in Z], ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1", "**pAUC@1e-2**", "pAUC@1e-3"]), "",
         "(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores: the 1% clean false-positive rate is true by construction.)", ""]
    rows, cl = [], {}
    for (n, b) in pairs:
        for c, lbl, d in BOOT:
            dd = T[n][c] - T[b][c]
            ps = bs["ps"]["diffs"][f"{n} - {b}"][c]
            if c not in idx_of:
                continue
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[c]], [2.5, 97.5])
            res = ("**RESOLVED " + ("better" if dd.mean() > 0 else "worse") + "**" if (lo > 0 or hi < 0) else "not resolved") if c == PRIMARY else ("cluster CI excludes 0 (descriptive)" if (lo > 0 or hi < 0) else "cluster CI contains 0 (descriptive)")
            cl[f"{n}-{b}|{c}"] = {"mean": float(dd.mean()), "strat_lo": float(ps["lo"]), "strat_hi": float(ps["hi"]), "cluster_lo": float(lo), "cluster_hi": float(hi), "seeds_up": int((dd > 0).sum()), "seeds_down": int((dd < 0).sum())}
            rows.append([f"{n} − {b}", lbl, f"{100 * dd.mean():+.2f}", f"[{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{int((dd > 0).sum())} up / {int((dd < 0).sum())} down", res])
    L += ["### Differences (points ×100; mean of the 10 per-seed differences; stratified and cluster 95% CI; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs the seed pairing is index with index only.", "",
          md(rows, ["difference", "metric", "mean difference", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome"]), "", "Ensemble pAUC@1e-2 differences (stratified bootstrap only):", "",
          md([[f"{n} − {b}", f"{100 * bs['ens']['diffs'][f'{n} - {b}'][PRIMARY]['point']:+.2f}", f"[{100 * bs['ens']['diffs'][f'{n} - {b}'][PRIMARY]['lo']:+.2f}, {100 * bs['ens']['diffs'][f'{n} - {b}'][PRIMARY]['hi']:+.2f}]"] for (n, b) in pairs], ["difference", "ensemble pAUC@1e-2 difference", "stratified 95% CI"]), ""]
    thr = {k: np.array([padtest.thresholds(Z[k][s], y, 0.01) for s in SEEDS]) for k in Z}
    flag = {k: Z[k] > thr[k][:, None] for k in Z}
    frows = [[g, int((fam == g).sum())] + [f"{100 * flag[k][:, fam == g].mean(1).mean():.1f} ± {100 * flag[k][:, fam == g].mean(1).std(ddof=1):.1f}" for k in Z] for g in sorted(set(fam))]
    L += ["### Detection rate per family, thresholds on the APRIL benign scores (%; clean and windows_syswow64 = false-positive rate, equal to the target BY CONSTRUCTION)", "", md(frows, ["family", "n"] + [lab(k) for k in Z])]
    cm, coin = hsh == CLUSTER_HASH, fam == "coinminer"
    rest = coin & ~cm
    crow, cout = [], {}
    for k in Z:
        sh = flag[k][:, cm].mean(1)
        margin = np.array([np.median(Z[k][s][cm]) - thr[k][s] for s in SEEDS])
        cout[k] = {"cluster_share_flagged_per_seed": sh.tolist(), "seeds_flagging": int((sh > 0.5).sum()), "median_margin_per_seed": margin.tolist(), "other_coinminer_tpr": [float(flag[k][:, rest].mean(1).mean()), float(flag[k][:, rest].mean(1).std(ddof=1))],
                   "all_coinminer_tpr": [float(flag[k][:, coin].mean(1).mean()), float(flag[k][:, coin].mean(1).std(ddof=1))]}
        crow.append([lab(k), f"{int((sh > 0.5).sum())}/10", f"{np.median(margin):+.1f} (IQR {np.percentile(margin, 25):+.1f} to {np.percentile(margin, 75):+.1f})", f"{100 * cout[k]['other_coinminer_tpr'][0]:.1f} ± {100 * cout[k]['other_coinminer_tpr'][1]:.1f}",
                     f"{100 * cout[k]['all_coinminer_tpr'][0]:.1f} ± {100 * cout[k]['all_coinminer_tpr'][1]:.1f}"])
    L += ["", f"### The coinminer cluster (hash_apis d91b96b4…, {int(cm.sum())} April reports with the same first 512 tokens of the OLD tokenizer, the same set of reports for all models; one input counted {int(cm.sum())} times)", "",
          "Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold (threshold on the April benign scores). Margin = median cluster logit minus the threshold (positive = flagged).", "",
          md(crow, ["model", "seeds flagging the cluster", "median margin (logit)", f"TPR of the other {int(rest.sum())} coinminer reports (%)", f"TPR of all {int(coin.sum())} coinminer reports (%)"])]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}, "ensemble": {k: {c: v for c, v in m_.items() if c != "roc_on_grid"} for k, m_ in ens.items()}, "pairs": cl, "coinminer_cluster": cout}, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap_stratified.json"), "w"), indent=1)
    np.savez_compressed(os.path.join(a.out, "logits_r1.npz"), r1_test=test["r1"].astype(np.float32))      # for P2 (seen / unseen)
    pass
    print("\n".join(L))


if __name__ == "__main__":
    main()
