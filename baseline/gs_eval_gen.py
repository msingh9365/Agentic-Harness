"""
April evaluation of Step 3b and Step 5 of NOTES 22.7 (same table format and rules as baseline/gs_eval_d.py).   (OURS)

    python -m baseline.gs_eval_gen --mode tk   --stage-c <gsf_runs> --extra <gstk runs> --out results/groupsplit/stage_d/step3b
    python -m baseline.gs_eval_gen --mode full --stage-c <gsf_runs> --extra <gsx runs> [--tk <gstk runs>] --out results/groupsplit/stage_d/step5

mode tk (Step 3b, diagnostic): Stage C (new tokenizer) vs the same setup with the OLD tokenizer (tags gstk_*) vs the old-split models. mode full (Step 5, final protocol): the full-January models (tags gsx_*)
against the old-split models, the Stage C models and (optional) the 3b models. Models: v2-PE (epoch 1) and ATT+bal (epoch 3), 10 seeds each, April logits stored after that epoch only. Per-seed mean ± std, ensembles,
stratified and cluster bootstrap (1,000 resamples, numpy seed 0, 2,509 April groups), seeds going each way, resolved = the cluster interval of pAUC@1e-2 excludes 0; per family with thresholds on the April benign scores
(by construction FPR = 1%). Scores only.
"""
import argparse
import json
import os

import numpy as np

from baseline import att_report as AR, common as C, gap_final, padtest
from baseline.twolevel_eval import april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

ROOT = AR.ROOT
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
EPOCH = {"v2pe": 1, "attbal": 3}
NAME = {"v2pe": "v2-PE", "attbal": "ATT+bal"}
LABEL = {"gs": "new split, NEW tokenizer (Stage C)", "tk": "new split, OLD tokenizer (Step 3b)", "full": "ALL January, old tokenizer (Step 5, final protocol)", "old": "old validation slice (old split, 2 epochs)"}
TAGS = {"gs": "gsf", "tk": "gstk", "full": "gsx"}


def load(runs, prefix, m):
    tag = f"{prefix}_{m}"
    e = EPOCH[m]
    for s in SEEDS:
        have = sorted(int(f.split("_epoch")[1].split("_")[0]) for f in os.listdir(os.path.join(runs, tag)) if f.startswith(f"seed{s}_epoch") and f.endswith("_test_logits.npy"))
        assert have == [e], (tag, s, have)                       # April logits only after the chosen epoch
        r = json.load(open(os.path.join(runs, tag, f"seed{s}.json")))
        assert r["epochs"] == (e if prefix != "gsf" else {"v2pe": 4, "attbal": 6}[m]) and r["split_hash_asserted"], (tag, s)         # Stage C ran past the chosen epoch (for the loss curves) but stored April logits only at the chosen one
    return np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{e}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["tk", "full"])
    ap.add_argument("--stage-c", required=True)
    ap.add_argument("--extra", required=True)
    ap.add_argument("--tk", default=None, help="Step 3b outputs, as an additional row in mode full")
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    new = "tk" if a.mode == "tk" else "full"
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    fam, hsh, groups = april_meta()
    assert len(set(groups)) == 2509 and len(y) == len(fam)
    old_v2 = AR.load_family("v2_pe", os.path.join(ROOT, "results", "att_bal"))[0]
    old_ab = np.stack([np.load(os.path.join(ROOT, "results", "review", "attack", "a3pad_attbal.npz"))[f"seed{s}"][0].astype(np.float64) for s in SEEDS])
    test = {}
    for m, old in (("v2pe", old_v2), ("attbal", old_ab)):
        test[f"gs_{m}"] = load(a.stage_c, "gsf", m)
        test[f"{new}_{m}"] = load(a.extra, TAGS[new], m)
        if a.mode == "full" and a.tk:
            test[f"tk_{m}"] = load(a.tk, "gstk", m)
        test[f"old_{m}"] = old
    order = []
    for m in ("v2pe", "attbal"):
        order += [f"old_{m}", f"gs_{m}"] + ([f"tk_{m}"] if f"tk_{m}" in test else []) + ([f"{new}_{m}"] if new == "full" else [f"{new}_{m}"])
    order = [k for i, k in enumerate(order) if k not in order[:i]]
    lab = lambda k: ("**" if k.split("_")[0] == new else "") + f"{NAME[k.split('_')[1]]}, {LABEL[k.split('_')[0]]}" + ("**" if k.split("_")[0] == new else "")
    pairs = []
    for m in ("v2pe", "attbal"):
        pairs += [(f"{new}_{m}", f"gs_{m}"), (f"{new}_{m}", f"old_{m}"), (f"gs_{m}", f"old_{m}")]
        if a.mode == "full" and f"tk_{m}" in test:
            pairs += [(f"{new}_{m}", f"tk_{m}")]
    pairs += [(f"{new}_attbal", f"{new}_v2pe"), ("gs_attbal", "gs_v2pe")]
    Z = {k: test[k] for k in order}
    T = {k: metrics_of(y, Z[k]) for k in Z}
    ens = {k: C.binary_metrics(y, Z[k].mean(0), decision=0.0) for k in Z}
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    L = [f"### Clean April test, 10 seeds each, one evaluation per model ({'Step 3b, diagnostic' if a.mode == 'tk' else 'Step 5, final protocol'}): per-seed mean ± std", "",
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
    # drop per family against the old models
    drows = []
    for g in sorted(set(fam) - {"clean", "windows_syswow64"}):
        mk = fam == g
        drows.append([g, int(mk.sum())] + [f"{100 * (flag[f'{k}_{m}'][:, mk].mean() - flag[f'old_{m}'][:, mk].mean()):+.1f}" for m in ("v2pe", "attbal") for k in [x for x in ("gs", "tk", "full") if f"{x}_{m}" in Z]])
    hdr = ["malware family", "n"] + [f"{NAME[m]} {k} − old (points)" for m in ("v2pe", "attbal") for k in [x for x in ("gs", "tk", "full") if f"{x}_{m}" in Z]]
    L += ["", "### Change of the detection rate against the old-split models, per family (points; thresholds on the April benign scores)", "", md(drows, hdr)]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}, "ensemble": {k: {c: v for c, v in m_.items() if c != "roc_on_grid"} for k, m_ in ens.items()}, "pairs": cl}, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap_stratified.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
