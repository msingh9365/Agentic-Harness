"""
Stage D of NOTES 22, April evaluation: early-stopped models (Step 2), the new split with the old epoch count (Step 3, gated), and where the thresholds are set (Step 4).   (OURS)

    python -m baseline.gs_eval_d --stage-c <gsf_runs> --stage-d <gsd_runs> --out results/groupsplit/stage_d [--boot 1000]

Conditions (10 seeds each): gs = Stage C (v2-PE epoch 1, ATT+bal epoch 3; NOTES 21.8); es = per-seed early stopping, the epoch of each seed chosen on VALIDATION logits only (`early_stop_selection.json`, written by
baseline/gs_early.py and committed before this script was run); e2 = the same Stage D runs after epoch 2 (the old epoch count; Step 3, run for a model type only if the gate of NOTES 22 is met: the early-stopped
model is still resolved worse than the old-split model of the same type, i.e. the cluster bootstrap CI of es - old on pAUC@1e-2 excludes 0 and is negative); old = the existing old-split models (REPORT 5.9, 5.10).
Reporting rules of NOTES 22: both bootstrap intervals (stratified, cluster over the 2,509 April hash_apis groups; 1,000 resamples, numpy seed 0), the number of seeds going each way, and a difference is called
"resolved" ONLY if the cluster interval excludes zero. Thresholds: TPR@1e-2, TPR@1e-3 and the per-family rates of the earlier tables use thresholds set on the April benign scores (by construction FPR = the target);
Step 4 adds the April FPR/TPR with the threshold set on the VALIDATION slice. Scores only.
"""
import argparse
import json
import os

import numpy as np

from baseline import att_report as AR, common as C, gap_final, groupsplit as G, padtest
from baseline.twolevel_eval import april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

ROOT = AR.ROOT
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
STAGE_C = {"v2pe": ("gsf_v2pe", 1), "attbal": ("gsf_attbal", 3)}                  # tag, chosen epoch (NOTES 21.8)
STAGE_D = {"v2pe": "gsd_v2pe", "attbal": "gsd_attbal"}
NAME = {"v2pe": "v2-PE", "attbal": "ATT+bal"}
OLDKEY = {"v2pe": "v2_pe", "attbal": "attbal"}


def lab_of(cond, m):
    return {"gs": f"**{NAME[m]}, new split, Stage C epoch ({STAGE_C[m][1]})**", "es": f"**{NAME[m]}, new split, early-stopped per seed (validation pAUC)**", "e2": f"**{NAME[m]}, new split, 2 epochs (old epoch count)**",
            "old": f"{NAME[m]}, old validation slice (2 epochs)"}[cond]


def load_logits(runs, tag, epochs):
    """epochs: one epoch per seed. Returns (April logits [10, n], validation logits [10, nv])."""
    t = np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{epochs[s]}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])
    v = np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{epochs[s]}_val_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])
    return t, v


def seeds_way(d):
    return f"{int((d > 0).sum())} up / {int((d < 0).sum())} down"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage-c", required=True)
    ap.add_argument("--stage-d", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "groupsplit", "stage_d"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--step3", default="auto", choices=["auto", "none", "both"], help="auto = the gate of NOTES 22")
    a = ap.parse_args()
    sel = json.load(open(os.path.join(a.out, "early_stop_selection.json")))
    lab = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))
    y = lab["y_test"].astype(int)
    _, vidx = G.val_slice()
    yv = (~np.isin(G.january_table()["train"]["family"][vidx], ["clean", "windows_syswow64"])).astype(int)
    fam, hsh, groups = april_meta()
    assert len(set(groups)) == 2509 and len(y) == len(fam)
    test, val, yval = {}, {}, {}
    old_t = {"v2pe": AR.load_family("v2_pe", os.path.join(ROOT, "results", "att_bal")), "attbal": None}
    old_t["attbal"] = (np.stack([np.load(os.path.join(ROOT, "results", "review", "attack", "a3pad_attbal.npz"))[f"seed{s}"][0].astype(np.float64) for s in SEEDS]), None)
    repro = {}
    for m in ("v2pe", "attbal"):
        tag, ch = STAGE_C[m]
        test[("gs", m)], val[("gs", m)] = load_logits(a.stage_c, tag, [ch] * 10)
        best = sel[m]["best_epoch_per_seed"]
        test[("es", m)], val[("es", m)] = load_logits(a.stage_d, STAGE_D[m], best)
        t_ch = np.stack([np.load(os.path.join(a.stage_d, STAGE_D[m], f"seed{s}_epoch{ch}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])
        repro[m] = {"max_abs_April_logit_difference_stage_d_vs_stage_c_at_stage_c_epoch": float(np.abs(t_ch - test[("gs", m)]).max()), "identical_seeds": int(sum(np.array_equal(t_ch[s], test[("gs", m)][s]) for s in SEEDS))}
        test[("old", m)], val[("old", m)] = old_t[m]
    yval = {k: (yv if k[0] != "old" else lab["y_val"].astype(int)) for k in val}
    # gate (fixed in NOTES 22 before any Stage D computation): cluster CI of es - old on pAUC@1e-2 excludes 0 and is negative
    gate = {}
    for m in ("v2pe", "attbal"):
        cd = cluster_bootstrap(y, groups, {"es": test[("es", m)], "old": test[("old", m)]}, [("es", "old")], a.boot)[("es", "old")][:, 3]
        lo, hi = np.percentile(cd, [2.5, 97.5])
        gate[m] = {"cluster_ci_es_minus_old_pauc": [float(lo), float(hi)], "mean_diff": float(metrics_of(y, test[("es", m)])[PRIMARY].mean() - metrics_of(y, test[("old", m)])[PRIMARY].mean()), "run_step3": bool(hi < 0)}
    run3 = {"auto": [m for m in gate if gate[m]["run_step3"]], "none": [], "both": ["v2pe", "attbal"]}[a.step3]
    for m in run3:
        test[("e2", m)], val[("e2", m)] = load_logits(a.stage_d, STAGE_D[m], [2] * 10)
        yval[("e2", m)] = yv
    conds = [("gs", "v2pe"), ("es", "v2pe")] + ([("e2", "v2pe")] if "v2pe" in run3 else []) + [("old", "v2pe"), ("gs", "attbal"), ("es", "attbal")] + ([("e2", "attbal")] if "attbal" in run3 else []) + [("old", "attbal")]
    key = lambda c: f"{c[0]}_{c[1]}"
    L_of = {key(c): lab_of(*c) for c in conds}
    Z = {key(c): test[c] for c in conds}
    T = {k: metrics_of(y, Z[k]) for k in Z}
    ens = {k: C.binary_metrics(y, Z[k].mean(0), decision=0.0) for k in Z}
    # pairs
    pairs = []
    for m in ("v2pe", "attbal"):
        pairs += [(f"es_{m}", f"gs_{m}"), (f"es_{m}", f"old_{m}"), (f"gs_{m}", f"old_{m}")]
        if m in run3:
            pairs += [(f"e2_{m}", f"gs_{m}"), (f"e2_{m}", f"old_{m}"), (f"e2_{m}", f"es_{m}")]
    pairs += [("gs_attbal", "gs_v2pe"), ("es_attbal", "es_v2pe")] + ([("e2_attbal", "e2_v2pe")] if len(run3) == 2 else []) + [("old_attbal", "old_v2pe")]
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    L = ["### Clean April test, 10 seeds each, one evaluation per model: per-seed mean ± std", "",
         md([[L_of[k], len(T[k]["auc"])] + [ms(T[k][c], d) for c, _, d in COLS] for k in Z], ["model", "n"] + [c[1] for c in COLS]), "", "10-seed ensembles (mean logit):", "",
         md([[L_of[k], f"{ens[k]['tpr@0.001']:.3f}", f"{ens[k]['tpr@0.01']:.3f}", f"{ens[k]['auc']:.4f}", f"{ens[k]['f1@0.5']:.3f}", f"**{ens[k]['pauc@0.01']:.3f}**", f"{ens[k]['pauc@0.001']:.3f}"] for k in Z], ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1", "**pAUC@1e-2**", "pAUC@1e-3"]), "",
         "(TPR@1e-2, TPR@1e-3 and F1@FPR use thresholds set on the April benign scores, see Step 4.)", ""]
    L += [f"### Early-stopping epochs (chosen on validation logits only): v2-PE {sel['v2pe']['best_epoch_per_seed']}; ATT+bal {sel['attbal']['best_epoch_per_seed']}.",
          f"Reproduction of Stage C by the Stage D runs at the Stage C epoch (April logits): v2-PE {repro['v2pe']['identical_seeds']}/10 seeds identical (largest logit difference {repro['v2pe']['max_abs_April_logit_difference_stage_d_vs_stage_c_at_stage_c_epoch']:.2e}); ATT+bal {repro['attbal']['identical_seeds']}/10 (largest {repro['attbal']['max_abs_April_logit_difference_stage_d_vs_stage_c_at_stage_c_epoch']:.2e}).", "",
          "### Gate for Step 3 (cluster CI of early-stopped minus old-split pAUC@1e-2 excludes 0 and is negative)", ""] + [f"- {NAME[m]}: difference {100 * gate[m]['mean_diff']:+.2f} points, cluster CI [{100 * gate[m]['cluster_ci_es_minus_old_pauc'][0]:+.2f}, {100 * gate[m]['cluster_ci_es_minus_old_pauc'][1]:+.2f}] -> Step 3 {'RUN' if m in run3 else 'not run'}" for m in gate]
    cl, rows = {}, []
    for (n, b) in pairs:
        for c, lbl, d in BOOT:
            dd = T[n][c] - T[b][c]
            ps = bs["ps"]["diffs"][f"{n} - {b}"][c]
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[c]], [2.5, 97.5]) if c in idx_of else (np.nan, np.nan)
            res = ("**RESOLVED " + ("better" if dd.mean() > 0 else "worse") + "**" if (lo > 0 or hi < 0) else "not resolved") if c == PRIMARY else ("cluster CI excludes 0 (descriptive)" if (lo > 0 or hi < 0) else "cluster CI contains 0 (descriptive)")
            cl[f"{n}-{b}|{c}"] = {"mean": float(dd.mean()), "strat_lo": float(ps["lo"]), "strat_hi": float(ps["hi"]), "cluster_lo": float(lo), "cluster_hi": float(hi), "seeds_up": int((dd > 0).sum()), "seeds_down": int((dd < 0).sum())}
            if c in idx_of:
                rows.append([f"{n} − {b}", lbl, f"{100 * dd.mean():+.2f}", f"[{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", seeds_way(dd), res])
    L += ["", "### Differences (points ×100; mean of the 10 per-seed differences; stratified bootstrap CI, cluster bootstrap CI over 2,509 April groups; seeds going each way). **Resolved = the CLUSTER interval of pAUC@1e-2 excludes 0.** For pairs of different training runs (new vs old, model vs model) the seed pairing is index with index only.", "",
          md(rows, ["difference", "metric", "mean difference", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome"]), "", "Ensemble pAUC@1e-2 differences (stratified bootstrap only):", "",
          md([[f"{n} − {b}", f"{100 * bs['ens']['diffs'][f'{n} - {b}'][PRIMARY]['point']:+.2f}", f"[{100 * bs['ens']['diffs'][f'{n} - {b}'][PRIMARY]['lo']:+.2f}, {100 * bs['ens']['diffs'][f'{n} - {b}'][PRIMARY]['hi']:+.2f}]"] for (n, b) in pairs], ["difference", "ensemble pAUC@1e-2 difference", "stratified 95% CI"])]
    # per family with April-set thresholds (as before)
    thr = {k: np.array([padtest.thresholds(Z[k][s], y, 0.01) for s in SEEDS]) for k in Z}
    flag = {k: Z[k] > thr[k][:, None] for k in Z}
    frows = []
    for g in sorted(set(fam)):
        mk = fam == g
        frows.append([g, int(mk.sum())] + [f"{100 * flag[k][:, mk].mean(1).mean():.1f} ± {100 * flag[k][:, mk].mean(1).std(ddof=1):.1f}" for k in Z])
    L += ["", "### Detection rate per family, thresholds set on the APRIL benign scores of each model and seed (%; the clean and windows_syswow64 rows are false-positive rates and equal the target BY CONSTRUCTION)", "", md(frows, ["family", "n"] + [L_of[k] for k in Z])]
    # Step 4: thresholds set on validation
    benign_a, mal_a = y == 0, y == 1
    srows, per_fam_v, s4 = [], [], {}
    for cnd in conds:
        k = key(cnd)
        if val[cnd] is None:
            srows.append([L_of[k], "n/a (no validation logits were kept)", "", "", "", ""])
            continue
        thv = np.array([padtest.thresholds(val[cnd][s], yval[cnd], 0.01) for s in SEEDS])
        fv = Z[k] > thv[:, None]
        fpr, tpr = fv[:, benign_a].mean(1), fv[:, mal_a].mean(1)
        tpr_apr = flag[k][:, mal_a].mean(1)
        s4[k] = {"threshold_on_validation": thv.tolist(), "april_fpr_per_seed": fpr.tolist(), "april_tpr_per_seed": tpr.tolist(), "april_tpr_with_april_threshold_per_seed": tpr_apr.tolist()}
        srows.append([L_of[k], f"{100 * fpr.mean():.2f} ± {100 * fpr.std(ddof=1):.2f} ({100 * fpr.min():.2f} to {100 * fpr.max():.2f})", f"{100 * tpr.mean():.1f} ± {100 * tpr.std(ddof=1):.1f}", "1.00 (by construction)", f"{100 * tpr_apr.mean():.1f} ± {100 * tpr_apr.std(ddof=1):.1f}",
                      f"{int((fpr > 0.01).sum())}/10"])
        per_fam_v.append((k, {g: float(fv[:, fam == g].mean(1).mean()) for g in sorted(set(fam))}))
    L += ["", "### Step 4: where the 1e-2 threshold is set. Threshold from the VALIDATION slice (benign validation logit at rank floor(0.01 x n_benign), same model and seed) applied unchanged to April, against the April-benign threshold of the other tables", "",
          md(srows, ["model", "April FPR, validation threshold (mean ± std, range) %", "April TPR, validation threshold %", "April FPR, April threshold %", "April TPR, April threshold %", "seeds with April FPR > 1%"]), ""]
    fr = []
    for g in sorted(set(fam)):
        fr.append([g, int((fam == g).sum())] + [f"{100 * dict(per_fam_v)[key(c)][g]:.1f}" if key(c) in dict(per_fam_v) else "n/a" for c in conds])
    L += ["Per-family rates with the validation thresholds (mean over seeds, %; clean and windows_syswow64 = false-positive rate):", "", md(fr, ["family", "n"] + [L_of[key(c)] for c in conds])]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "tables_stage_d.md"), "w").write("\n".join(L) + "\n")
    json.dump({"gate": gate, "step3_run_for": run3, "reproduction": repro, "test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}, "ensemble": {k: {c: v for c, v in m_.items() if c != "roc_on_grid"} for k, m_ in ens.items()},
               "pairs": cl, "step4": s4}, open(os.path.join(a.out, "stage_d_results.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap_stratified.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
