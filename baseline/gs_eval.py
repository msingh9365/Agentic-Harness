"""
Stage C of NOTES 21: the ONE clean April evaluation of v2-PE and ATT+bal trained on the group-split training part (10 seeds each, the settings approved after Stage B), next to the old-split models.   (OURS)

    python -m baseline.gs_eval --runs <folder with gsf_v2pe/ and gsf_attbal/ and loss_curves/> --out results/groupsplit/stage_c [--boot 1000]

Models: gs_v2pe = v2-PE lr 2e-3, epoch 1; gs_attbal = ATT+bal lr 1e-3, p 0.5, epoch 3 (both on the group-split training part, tokenizer refit on it; NOTES 21.8) and, for comparison, the existing models trained on the old
random split with the old tokenizer: v2_pe (REPORT 5.9, lr 2e-3, 2 epochs) and attbal (REPORT 5.10, lr 2e-3, p 0.5, epoch 2). The April logits of the new models are those stored after the chosen epoch only
(`seed<k>_epoch<e>_test_logits.npy`); no April number was used for any choice. Scores only (no edited report is read or written).
Statistics = EVAL_PROTOCOL.md 5 as in baseline/twolevel_eval.py: stratified bootstrap (gap_final.bootstrap, 1,000 resamples, numpy seed 0), per-seed paired differences, claim rule (CI excludes 0 and >= 7 of 10 seeds with the
same sign), the ensemble next to it, the cluster bootstrap over hash_apis groups, per family detection rate at the 1% FPR threshold of each model and seed, the coinminer cluster, and the loss curves.
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
APPROVED = {"v2pe": ([0.002, 1], "gsf_v2pe"), "attbal": ([0.001, 0.5, 3], "gsf_attbal")}          # NOTES 21.8 / owner's approval
LAB = {"gs_attbal": "**ATT+bal, new split (lr 1e-3, p 0.5, epoch 3)**", "gs_v2pe": "**v2-PE, new split (lr 2e-3, epoch 1)**", "attbal": "ATT+bal, old validation slice (lr 2e-3, p 0.5, epoch 2)", "v2_pe": "v2-PE, old validation slice (lr 2e-3, epoch 2)"}
PAIRS = [("gs_attbal", "gs_v2pe"), ("gs_v2pe", "v2_pe"), ("gs_attbal", "attbal"), ("attbal", "v2_pe")]
OLD = os.path.join(ROOT, "results", "att_bal")


def load_new(runs, tag, epoch):
    t = np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{epoch}_test_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])
    v = np.stack([np.load(os.path.join(runs, tag, f"seed{s}_epoch{epoch}_val_logits.npy")).astype(np.float64).reshape(-1) for s in SEEDS])
    return t, v


def check_runs(runs, tag, epoch, epochs):
    """every run: 10 seeds, the split hash asserted, the right number of epochs, and the April logits exist for the chosen epoch ONLY."""
    for s in SEEDS:
        r = json.load(open(os.path.join(runs, tag, f"seed{s}.json")))
        assert r["split_hash_asserted"] and r["epochs"] == epochs and r["n_train"] == 66580 and r["n_val"] == 8718 and r["tokenizer"] == "bpe50k_gs", (tag, s)
        have = sorted(int(f.split("_epoch")[1].split("_")[0]) for f in os.listdir(os.path.join(runs, tag)) if f.startswith(f"seed{s}_epoch") and f.endswith("_test_logits.npy"))
        assert have == [epoch], (tag, s, have)


def loss_figure(runs, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(11, 7.4), dpi=200)
    for r, (name, tag, label) in enumerate((("v2pe", "gsf_v2pe", "v2-PE (chosen epoch 1)"), ("attbal", "gsf_attbal", "ATT+bal (chosen epoch 3)"))):
        ch = APPROVED[name][0][-1]
        cur = [json.load(open(os.path.join(runs, "loss_curves", tag, f"seed{s}.json"))) for s in SEEDS]
        ne = len(cur[0]["per_epoch"])
        ep = np.arange(1, ne + 1)
        for key, lab, col in (("train_epoch_mean_loss", "training loss (epoch mean, dropout on" + (", padded mix)" if name == "attbal" else ")"), "#1baf7a"), ("train_subset_clean_loss", "training loss, 2,000 unedited reports (eval)", "#6250d6"), ("val_loss", "validation loss (group-split slice)", "#eb6834")):
            a = np.array([[e[key] for e in c["per_epoch"]] for c in cur])
            ax[r, 0].plot(ep, a.mean(0), "-o", ms=3, color=col, label=lab)
            ax[r, 0].fill_between(ep, a.mean(0) - a.std(0, ddof=1), a.mean(0) + a.std(0, ddof=1), color=col, alpha=0.18, lw=0)
        ax[r, 0].axvline(ch, color="#888", ls=":", lw=1)
        ax[r, 0].set_xticks(ep)
        ax[r, 0].set_xlabel("epoch")
        ax[r, 0].set_ylabel("binary cross-entropy")
        ax[r, 0].set_title(f"{label}: per epoch, mean ± SD over 10 seeds (dotted = chosen epoch)", fontsize=8.5)
        ax[r, 0].legend(fontsize=6.5, frameon=False)
        st = np.array(cur[0]["train_loss_step"])
        spe = cur[0]["steps_per_epoch"]
        ax[r, 1].plot(st, np.mean([c["train_loss_mean_last_10"] for c in cur], axis=0), color="#1baf7a", lw=0.9, label="training loss, mean of the last 10 batches")
        ax[r, 1].plot(ep * spe, [np.mean([c["per_epoch"][e - 1]["val_loss"] for c in cur]) for e in ep], "o-", color="#eb6834", ms=3, label="validation loss (end of epoch)")
        for e in ep:
            ax[r, 1].axvline(e * spe, color="#ccc", lw=0.6)
        ax[r, 1].axvline(ch * spe, color="#888", ls=":", lw=1)
        ax[r, 1].set_yscale("log")
        ax[r, 1].set_xlabel("training step")
        ax[r, 1].set_title("batch-level training loss, mean over seeds", fontsize=8.5)
        ax[r, 1].legend(fontsize=6.5, frameon=False)
    for a_ in ax.ravel():
        a_.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "fig_loss_curves_train_vs_validation.png"))
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "groupsplit", "stage_c"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    sel = json.load(open(os.path.join(ROOT, "results", "groupsplit", "stage_b", "selection.json")))
    for name, (key, _) in APPROVED.items():                          # guard: the settings are those selected in NOTES 21.8 and approved by the owner; they were pushed before this script could run
        assert sel[name]["chosen"] == key, f"selection.json chooses {sel[name]['chosen']} for {name}, not the approved {key}"
    check_runs(a.runs, "gsf_v2pe", 1, 4)
    check_runs(a.runs, "gsf_attbal", 3, 6)
    lab = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))
    y = lab["y_test"].astype(int)
    test, val = {}, {}
    test["gs_v2pe"], val["gs_v2pe"] = load_new(a.runs, "gsf_v2pe", 1)
    test["gs_attbal"], val["gs_attbal"] = load_new(a.runs, "gsf_attbal", 3)
    test["v2_pe"] = AR.load_family("v2_pe", OLD)[0]
    test["attbal"] = np.stack([np.load(os.path.join(ROOT, "results", "review", "attack", "a3pad_attbal.npz"))[f"seed{s}"][0].astype(np.float64) for s in SEEDS])    # row 0 = unedited April (as in twolevel_eval.load)
    fam, hsh, groups = april_meta()
    assert len(fam) == len(y) == test["gs_v2pe"].shape[1] and len(set(groups)) == 2509
    fams = [f for f in LAB if f in test]
    T = {f: metrics_of(y, test[f]) for f in fams}
    ens = {f: C.binary_metrics(y, test[f].mean(0), decision=0.0) for f in fams}
    # the validation slice (group split) is known for the two new models only; its labels come from the family of the validation rows
    from baseline import groupsplit as G
    _, vidx = G.val_slice()
    yv = (~np.isin(G.january_table()["train"]["family"][vidx], ["clean", "windows_syswow64"])).astype(int)       # malware = every family except clean and windows_syswow64 (as in the training labels)
    assert int(yv.sum()) == 5557 and len(yv) == 8718
    V = {f: metrics_of(yv, val[f]) for f in val}
    bs = gap_final.bootstrap(y, {f: test[f] for f in fams}, a.boot, pairs=PAIRS)
    L = ["### Clean April test: per-seed mean ± std (10 seeds, logit-ranked; one evaluation per model)", "",
         md([[LAB[f], len(T[f]["auc"])] + [ms(T[f][k], d) for k, _, d in COLS] for f in fams], ["model", "n"] + [c[1] for c in COLS]), "", "10-seed ensembles (mean logit):", "",
         md([[LAB[f], f"{ens[f]['tpr@0.001']:.3f}", f"{ens[f]['tpr@0.01']:.3f}", f"{ens[f]['auc']:.4f}", f"{ens[f]['f1@0.5']:.3f}", f"**{ens[f]['pauc@0.01']:.3f}**", f"{ens[f]['pauc@0.001']:.3f}"] for f in fams], ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1", "**pAUC@1e-2**", "pAUC@1e-3"]), "",
         "Group-split validation slice (8,718 reports; per-seed mean ± std; the old models have no validation logits on this slice):", "",
         md([[LAB[f], len(V[f]["auc"])] + [ms(V[f][k], d) for k, _, d in COLS] for f in V], ["model", "n"] + [c[1] for c in COLS]),
         "", f"### Differences, stratified bootstrap ({a.boot} resamples, numpy seed 0; points ×100). Pairs: new ATT+bal vs new v2-PE (the claim of this stage); new vs old for each model; old ATT+bal vs old v2-PE", ""]
    rows, verdicts = [], {}
    for (n, b) in PAIRS:
        for kind, kl in (("ps", "per-seed means"), ("ens", "10-seed ensembles")):
            for k, lbl, d in BOOT:
                e = bs[kind]["diffs"][f"{n} - {b}"][k]
                rows.append([f"{n} − {b}", kl, lbl, f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]" + (" **CI excludes 0**" if e["resolved"] else " CI contains 0")])
        verdicts[f"{n} vs {b}"] = AR.verdict(bs["ps"]["diffs"][f"{n} - {b}"][PRIMARY], T[n][PRIMARY] - T[b][PRIMARY], n)
    L.append(md(rows, ["difference", "statistic", "metric", "difference in points, 95% CI"]))
    L += ["", "### Per-seed paired differences of the primary metric (same seed index; points ×100)", ""]
    L.append(md([[f"{n} − {b}"] + [f"{100 * x:+.1f}" for x in (T[n][PRIMARY] - T[b][PRIMARY])] + [f"{100 * (T[n][PRIMARY] - T[b][PRIMARY]).mean():+.2f} ± {100 * (T[n][PRIMARY] - T[b][PRIMARY]).std(ddof=1):.2f}", f"{int(((T[n][PRIMARY] - T[b][PRIMARY]) > 0).sum())}/10"] for (n, b) in PAIRS],
                ["pair"] + [f"s{s}" for s in SEEDS] + ["mean ± std", "seeds > 0"]))
    L += ["", "**Claim rule (EVAL_PROTOCOL.md 5) on pAUC@1e-2, stratified bootstrap of the per-seed means:** (the seeds of the new and the old models are different training runs: the 'same seed index' pairing is only a pairing of 10 values with 10 values)", ""] + [f"- {k}: {v}" for k, v in verdicts.items()]
    cd = cluster_bootstrap(y, groups, {f: test[f] for f in fams}, PAIRS, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    cl, crows = {}, []
    for (n, b) in PAIRS:
        for key, lbl in (("pauc@0.01", "pAUC@1e-2 (primary)"), ("tpr@0.01", "TPR@1e-2"), ("tpr@0.001", "TPR@1e-3"), ("auc", "AUC")):
            d = T[n][key] - T[b][key]
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[key]], [2.5, 97.5])
            pos, neg = int((d > 0).sum()), int((d < 0).sum())
            ok = (lo > 0 or hi < 0) and max(pos, neg) >= 7
            cl[f"{n}-{b}|{key}"] = {"mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "seeds_above_0": pos, "resolved": bool(ok)}
            crows.append([f"{n} − {b}", lbl, f"{100 * d.mean():+.2f}", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{pos}/10", ("**meets the rule**" if ok else "not resolved") if key == "pauc@0.01" else ("CI excludes 0 (descriptive)" if (lo > 0 or hi < 0) else "CI contains 0 (descriptive)")])
    L += ["", "### Cluster bootstrap over hash_apis groups (2,509 April groups; cells (group, class) resampled; points ×100)", "", md(crows, ["difference", "metric", "mean difference", "95% CI (cluster)", "seeds > 0", "outcome"])]
    thr = {f: np.array([padtest.thresholds(test[f][s], y, 0.01) for s in SEEDS]) for f in fams}
    flag = {f: test[f] > thr[f][:, None] for f in fams}
    frows, fout = [], {}
    for g in sorted(set(fam)):
        m = fam == g
        r = [g, int(m.sum())]
        for f in fams:
            v = flag[f][:, m].mean(1)
            fout.setdefault(g, {})[f] = [float(v.mean()), float(v.std(ddof=1))]
            r.append(f"{100 * v.mean():.1f} ± {100 * v.std(ddof=1):.1f}")
        frows.append(r)
    L += ["", "### Detection rate per family at the 1% FPR threshold of each model and seed (April; mean ± std over 10 seeds, %). `clean` and `windows_syswow64` rows are false-positive rates.", "", md(frows, ["family", "n"] + [LAB[f] for f in fams])]
    cm, coin = hsh == CLUSTER_HASH, fam == "coinminer"
    rest = coin & ~cm
    crow, cout = [], {}
    for f in fams:
        sh = flag[f][:, cm].mean(1)
        margin = np.array([np.median(test[f][s][cm]) - thr[f][s] for s in SEEDS])
        cout[f] = {"cluster_share_flagged_per_seed": sh.tolist(), "seeds_flagging": int((sh > 0.5).sum()), "median_margin_per_seed": margin.tolist(), "other_coinminer_tpr": [float(flag[f][:, rest].mean(1).mean()), float(flag[f][:, rest].mean(1).std(ddof=1))],
                   "all_coinminer_tpr": [float(flag[f][:, coin].mean(1).mean()), float(flag[f][:, coin].mean(1).std(ddof=1))]}
        crow.append([LAB[f], f"{int((sh > 0.5).sum())}/10", f"{np.median(margin):+.1f} (IQR {np.percentile(margin, 25):+.1f} to {np.percentile(margin, 75):+.1f})", f"{100 * cout[f]['other_coinminer_tpr'][0]:.1f} ± {100 * cout[f]['other_coinminer_tpr'][1]:.1f}",
                     f"{100 * cout[f]['all_coinminer_tpr'][0]:.1f} ± {100 * cout[f]['all_coinminer_tpr'][1]:.1f}"])
    L += ["", f"### The coinminer cluster (hash_apis d91b96b4…, {int(cm.sum())} April reports with the same first 512 tokens of the OLD tokenizer; one input counted {int(cm.sum())} times)", "",
          "Seeds that flag it = seeds in which more than half of the cluster is above the 1% threshold. Margin = median cluster logit minus the threshold (positive = flagged).", "",
          md(crow, ["model", "seeds flagging the cluster", "median margin (logit)", f"TPR of the other {int(rest.sum())} coinminer reports (%)", f"TPR of all {int(coin.sum())} coinminer reports (%)"])]
    os.makedirs(a.out, exist_ok=True)
    loss_figure(a.runs, a.out)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"test": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in T.items()}, "validation_new_models": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in V.items()},
               "ensemble_test": {f: {k: v for k, v in m.items() if k != "roc_on_grid"} for f, m in ens.items()}, "claims": verdicts}, open(os.path.join(a.out, "per_model.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap.json"), "w"), indent=1)
    json.dump(cl, open(os.path.join(a.out, "cluster.json"), "w"), indent=1)
    json.dump({"family": fout, "coinminer_cluster": cout}, open(os.path.join(a.out, "family.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
