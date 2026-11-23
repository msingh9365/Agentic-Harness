"""
Metrics, cluster bootstrap and figures of the order tests (NOTES_ORDER.md). Reads results/order_tests/scores_test{1,2}_<model>.npz, writes metrics_test{1,2}.json, tables_*.md and the two figures.

    python results/order_tests/analyze.py --test 1 [--models m1 m3] [--boot 1000] [--dir results/order_tests]
    python results/order_tests/analyze.py --test 2 ...
Bootstrap: the resampling of `twolevel_eval.cluster_bootstrap` (cells = hash_apis group x class, numpy seed 0, same resample for every variant and model), metrics recomputed on every resample per seed, then averaged over the seeds.
"""
import argparse
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from baseline import common as C  # noqa: E402
from baseline.twolevel_eval import april_meta  # noqa: E402
from baseline.paper_figs import COL, NAME  # noqa: E402

MK = {"m1": "M1", "m2": "M2", "m3": "M3", "m4": "M4"}
V1 = ["clean", "a", "b", "c", "d"]
V1_LABEL = {"clean": "clean", "a": "(a) window shuffle", "b": "(b) local shuffle (5)", "c": "(c) reversal", "d": "(d) full shuffle (reference)"}
PAUC, AUC, TPR = 3, 2, 1                                              # indices of C.roc_summary


def groups_and_members(y):
    _, _, groups = april_meta()
    assert len(set(groups)) == 2509 and len(groups) == len(y)
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    return members


def draws_selection(members, n_boot):
    rng = np.random.default_rng(0)
    for b in range(n_boot):
        yield np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])


def summ(y, z):                                                       # [seeds, 5]
    return np.array([C.roc_summary(y, zz) for zz in z])


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def resolved(d_draws, d_seeds):
    """RESOLVED (NOTES_ORDER section 0): cluster 95% interval excludes 0 AND >= 7 of 10 seeds (all 3 of 3) have the same sign."""
    lo, hi = ci(d_draws)
    k = len(d_seeds)
    need = 7 if k == 10 else k
    mean = float(np.mean(d_seeds))
    same = int((np.sign(d_seeds) == np.sign(mean)).sum()) if mean != 0 else 0
    return bool((lo > 0 or hi < 0) and same >= need)


# ----------------------------------------------------------------------------- Test 1
def test1(a):
    out = {}
    pool = {}
    for m in a.models:
        d = np.load(os.path.join(a.dir, f"scores_test1_{m}.npz"))
        pool[m] = d
    y = pool[a.models[0]]["y"].astype(int)
    members = groups_and_members(y)
    # point metrics
    for m, d in pool.items():
        R = {v: summ(y, d[f"z_{v}"]) for v in V1}                      # [seeds, 5]
        o = {"n_seeds": int(len(d["seeds"])), "variants": {}}
        zc = d["z_clean"].astype(np.float64)
        sd = {c: zc[:, y == c].std(axis=1) for c in (0, 1)}
        mm = d["m"]
        strata = {"m<2": mm < 2, "2<=m<10": (mm >= 2) & (mm < 10), "m>=10": mm >= 10}
        for v in V1:
            z = d[f"z_{v}"].astype(np.float64)
            dz = np.abs(z - zc)
            e = {"pauc": R[v][:, PAUC].tolist(), "pauc_mean": float(R[v][:, PAUC].mean()), "pauc_sd": float(R[v][:, PAUC].std(ddof=1)) if len(R[v]) > 1 else 0.0,
                 "auc_mean": float(R[v][:, AUC].mean()), "tpr1_mean": float(R[v][:, TPR].mean()),
                 "abs_change_malware": float(dz[:, y == 1].mean()), "abs_change_benign": float(dz[:, y == 0].mean()),
                 "abs_change_malware_over_sd": float((dz[:, y == 1].mean(axis=1) / sd[1]).mean()), "abs_change_benign_over_sd": float((dz[:, y == 0].mean(axis=1) / sd[0]).mean()),
                 "mean_signed_change_malware": float((z - zc)[:, y == 1].mean()), "mean_signed_change_benign": float((z - zc)[:, y == 0].mean()),
                 "by_stratum_abs_change": {k: {"malware": float(dz[:, (y == 1) & s].mean()) if ((y == 1) & s).any() else None, "benign": float(dz[:, (y == 0) & s].mean()) if ((y == 0) & s).any() else None,
                                              "n": int(s.sum())} for k, s in strata.items()}}
            if v != "clean":
                ch = d[f"changed_{v}"]
                e["share_reports_changed"] = float(ch.mean())
            o["variants"][v] = e
        o["share_m_ge_2"] = float((mm >= 2).mean())
        o["mean_m"], o["median_m"] = float(mm.mean()), float(np.median(mm))
        o["clean_logit_sd"] = {"malware": float(sd[1].mean()), "benign": float(sd[0].mean())}
        out[m] = o
    # bootstrap of clean - variant
    keys = [(m, v) for m in a.models for v in V1]
    draws = {k: [] for k in keys}
    for b, sel in enumerate(draws_selection(members, a.boot)):
        for m, d in pool.items():
            for v in V1:
                draws[(m, v)].append(summ(y[sel], d[f"z_{v}"][:, sel]).mean(0))
        if b % 100 == 0:
            print(f"  bootstrap {b}/{a.boot}", flush=True)
    for m in a.models:
        for v in V1[1:]:
            diff = np.array(draws[(m, "clean")]) - np.array(draws[(m, v)])          # [boot, 5]
            sd_ = np.array(out[m]["variants"]["clean"]["pauc"]) - np.array(out[m]["variants"][v]["pauc"])
            e = out[m]["variants"][v]
            e["pauc_drop_mean"] = float(sd_.mean())
            e["pauc_drop_ci"] = ci(diff[:, PAUC])
            e["pauc_drop_seeds_down"] = int((sd_ > 0).sum())
            e["pauc_drop_seeds_up"] = int((sd_ < 0).sum())
            e["pauc_drop_resolved"] = resolved(diff[:, PAUC], sd_)
            e["auc_drop_mean"] = float(out[m]["variants"]["clean"]["auc_mean"] - e["auc_mean"])
            e["auc_drop_ci"] = ci(diff[:, AUC])
            e["tpr1_drop_mean"] = float(out[m]["variants"]["clean"]["tpr1_mean"] - e["tpr1_mean"])
            e["tpr1_drop_ci"] = ci(diff[:, TPR])
            lo, hi = e["pauc_drop_ci"]
            if e["pauc_drop_resolved"] and e["pauc_drop_mean"] >= 0.05:
                e["verdict"] = "order-sensitive"
            elif lo >= -0.02 and hi <= 0.02:
                e["verdict"] = "bag-of-calls-like"
            else:
                e["verdict"] = "in between / inconclusive"
    json.dump(out, open(os.path.join(a.dir, "metrics_test1.json"), "w"), indent=1)
    md = []
    md.append("| model | variant | pAUC@1e-2 | drop vs clean (points) | cluster 95% CI (points) | seeds down/up | AUC | TPR@1% (own thr) | mean abs logit change malware / benign | verdict |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for m in a.models:
        for v in V1:
            e = out[m]["variants"][v]
            if v == "clean":
                md.append(f"| {NAME[MK[m]]} | clean | {e['pauc_mean']:.3f} ± {e['pauc_sd']:.3f} |  |  |  | {e['auc_mean']:.4f} | {e['tpr1_mean']:.3f} |  |  |")
            else:
                res = "RESOLVED" if e["pauc_drop_resolved"] else "not resolved"
                md.append(f"| {NAME[MK[m]]} | {V1_LABEL[v]} | {e['pauc_mean']:.3f} ± {e['pauc_sd']:.3f} | {100 * e['pauc_drop_mean']:+.2f} ({res}) | [{100 * e['pauc_drop_ci'][0]:+.2f}, {100 * e['pauc_drop_ci'][1]:+.2f}] | "
                          f"{e['pauc_drop_seeds_down']}/{e['pauc_drop_seeds_up']} | {e['auc_mean']:.4f} | {e['tpr1_mean']:.3f} | {e['abs_change_malware']:.3f} / {e['abs_change_benign']:.3f} | {e['verdict'] if v != 'd' else 'reference'} |")
    open(os.path.join(a.dir, "tables_test1.md"), "w").write("\n".join(md) + "\n")
    md2 = ["| model | variant | share of reports whose order changed | mean abs logit change / SD of clean logits (malware / benign) | mean abs change by stratum of m (malware / benign): m<2 | 2<=m<10 | m>=10 |", "|---|---|---|---|---|---|---|"]
    for m in a.models:
        for v in V1[1:]:
            e = out[m]["variants"][v]
            st = e["by_stratum_abs_change"]
            f = lambda k: "-" if st[k]["malware"] is None else f"{st[k]['malware']:.3f} / {st[k]['benign']:.3f} (n={st[k]['n']})"      # noqa: E731
            md2.append(f"| {NAME[MK[m]]} | {V1_LABEL[v]} | {100 * e['share_reports_changed']:.1f}% | {e['abs_change_malware_over_sd']:.3f} / {e['abs_change_benign_over_sd']:.3f} | {f('m<2')} | {f('2<=m<10')} | {f('m>=10')} |")
    open(os.path.join(a.dir, "tables_test1_logits.md"), "w").write("\n".join(md2) + "\n")
    fig1(a, out)


def fig1(a, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.9))
    nm, nv = len(a.models), len(V1)
    w = 0.8 / nm
    for j, m in enumerate(a.models):
        x = np.arange(nv) + (j - (nm - 1) / 2) * w
        ys = [out[m]["variants"][v]["pauc_mean"] for v in V1]
        ax[0].bar(x, ys, w * 0.92, color=COL[MK[m]], label=NAME[MK[m]], hatch=None)
        for xi, v in zip(x, V1):
            ax[0].scatter(np.full(len(out[m]["variants"][v]["pauc"]), xi), out[m]["variants"][v]["pauc"], s=7, color="k", zorder=3, lw=0)
        mw = [out[m]["variants"][v]["abs_change_malware"] for v in V1[1:]]
        bn = [out[m]["variants"][v]["abs_change_benign"] for v in V1[1:]]
        xx = np.arange(nv - 1) + (j - (nm - 1) / 2) * w
        ax[1].bar(xx - w * 0.23, mw, w * 0.44, color=COL[MK[m]], label=f"{NAME[MK[m]]} malware" if True else None)
        ax[1].bar(xx + w * 0.23, bn, w * 0.44, color=COL[MK[m]], alpha=0.45, hatch="///", edgecolor="k", lw=0.3, label=f"{NAME[MK[m]]} benign")
    ax[0].set_xticks(range(nv))
    ax[0].set_xticklabels([V1_LABEL[v].replace(" (", "\n(") for v in V1], fontsize=7)
    ax[0].set_ylabel("pAUC@1e-2 (normalised), April, mean of seeds (dots: seeds)")
    ax[0].set_ylim(0, 1)
    ax[0].legend(fontsize=7, loc="lower left")
    ax[0].set_title("A. Detection quality, clean against shuffled order", fontsize=9)
    ax[1].set_xticks(range(nv - 1))
    ax[1].set_xticklabels([V1_LABEL[v].replace(" (", "\n(") for v in V1[1:]], fontsize=7)
    ax[1].set_ylabel("mean |logit(variant) - logit(clean)| per report")
    ax[1].legend(fontsize=6, loc="upper left")
    ax[1].set_title("B. Change of the score per report (descriptive)", fontsize=9)
    for x_ in ax:
        x_.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(a.dir, "fig_test1_shuffle.png"), dpi=200)


# ----------------------------------------------------------------------------- Test 2
def clean_threshold(y, z0):
    """Authors' rule (last ROC point with FPR <= 1%): threshold of the clean benign scores of one seed."""
    from sklearn.metrics import roc_curve
    fpr, tpr, thr = roc_curve(y, z0.astype(np.float64))
    return float(thr[np.where(fpr <= 1e-2)[0][-1]])


def spreads(z, y):
    """per report max - min over the shifts; z [seeds, K, N] -> dict of class means/medians (mean over seeds)."""
    sp = z.max(axis=1) - z.min(axis=1)                                 # [seeds, N]
    return sp


def test2(a):
    out, pool = {}, {}
    for m in a.models:
        pool[m] = np.load(os.path.join(a.dir, f"scores_test2_{m}.npz"))
    y = pool[a.models[0]]["y"].astype(int)
    members = groups_and_members(y)
    T = pool[a.models[0]]["targets"].tolist()
    nT = len(T)
    for m, d in pool.items():
        Z = d["z_shift"].astype(np.float64)                            # [seeds, 9, N]
        Zc = d["z_ctrl"].astype(np.float64) if d["z_ctrl"].shape[1] else None
        S = d["s_exact"].astype(int)
        ns = Z.shape[0]
        o = {"n_seeds": int(ns), "targets": T, "s_exact_mean": S[:nT].mean(1).tolist(), "s_exact_min": S[:nT].min(1).tolist(), "s_exact_max": S[:nT].max(1).tolist(),
             "share_exact_hit": [float((S[k] == T[k]).mean()) for k in range(nT)], "per_s": []}
        sd0 = {c: Z[:, 0][:, y == c].std(axis=1) for c in (0, 1)}
        thr = np.array([clean_threshold(y, Z[si, 0]) for si in range(ns)])
        base = None
        for k in range(nT):
            R = summ(y, Z[:, k])
            if k == 0:
                base = R
            det = np.array([(Z[si, k][y == 1] >= thr[si]).mean() for si in range(ns)])
            fa = np.array([(Z[si, k][y == 0] >= thr[si]).mean() for si in range(ns)])
            e = {"s_target": T[k], "pauc": R[:, PAUC].tolist(), "pauc_mean": float(R[:, PAUC].mean()), "pauc_sd": float(R[:, PAUC].std(ddof=1)) if ns > 1 else 0.0,
                 "auc_mean": float(R[:, AUC].mean()), "tpr1_own_mean": float(R[:, TPR].mean()), "det_clean_thr": det.tolist(), "det_clean_thr_mean": float(det.mean()),
                 "benign_fpr_clean_thr_mean": float(fa.mean()), "mean_signed_change_malware": float((Z[:, k] - Z[:, 0])[:, y == 1].mean()), "mean_signed_change_benign": float((Z[:, k] - Z[:, 0])[:, y == 0].mean())}
            o["per_s"].append(e)
        sp = spreads(Z, y)
        o["spread"] = {"malware_mean": float(sp[:, y == 1].mean()), "benign_mean": float(sp[:, y == 0].mean()), "malware_median": float(np.median(sp[:, y == 1], axis=1).mean()),
                       "benign_median": float(np.median(sp[:, y == 0], axis=1).mean()), "malware_over_sd": float((sp[:, y == 1].mean(axis=1) / sd0[1]).mean()), "benign_over_sd": float((sp[:, y == 0].mean(axis=1) / sd0[0]).mean())}
        if Zc is not None and Zc.shape[1]:
            spc = spreads(Zc, y)
            o["spread_control_equal_length"] = {"malware_mean": float(spc[:, y == 1].mean()), "benign_mean": float(spc[:, y == 0].mean()), "malware_median": float(np.median(spc[:, y == 1], axis=1).mean()),
                                                "benign_median": float(np.median(spc[:, y == 0], axis=1).mean()), "malware_over_sd": float((spc[:, y == 1].mean(axis=1) / sd0[1]).mean()),
                                                "benign_over_sd": float((spc[:, y == 0].mean(axis=1) / sd0[0]).mean()), "exact_s_mean": float(S[nT:].mean()), "exact_s_min": int(S[nT:].min()), "exact_s_max": int(S[nT:].max())}
        o["clean_logit_sd"] = {"malware": float(sd0[1].mean()), "benign": float(sd0[0].mean())}
        o["pauc_range_over_s"] = float(np.max([e["pauc_mean"] for e in o["per_s"]]) - np.min([e["pauc_mean"] for e in o["per_s"]]))
        o["_thr"] = thr.tolist()
        out[m] = o
    # bootstrap: pAUC(s) - pAUC(0) per model; spread and pAUC-range differences between models
    draws = {m: [] for m in a.models}
    sp_draws = {m: [] for m in a.models}
    spcache = {m: spreads(pool[m]["z_shift"].astype(np.float64), y).mean(0) for m in a.models}                # mean over seeds, [N]
    for b, sel in enumerate(draws_selection(members, a.boot)):
        for m in a.models:
            Z = pool[m]["z_shift"]
            draws[m].append(np.array([summ(y[sel], Z[:, k][:, sel]).mean(0)[PAUC] for k in range(nT)]))
            s_ = spcache[m][sel]
            ys = y[sel]
            sp_draws[m].append([s_[ys == 1].mean(), s_[ys == 0].mean()])
        if b % 100 == 0:
            print(f"  bootstrap {b}/{a.boot}", flush=True)
    for m in a.models:
        D = np.array(draws[m])                                          # [boot, 9]
        for k in range(1, nT):
            e = out[m]["per_s"][k]
            e0 = out[m]["per_s"][0]
            seeds_d = np.array(e["pauc"]) - np.array(e0["pauc"])
            diff = D[:, k] - D[:, 0]
            e["pauc_diff_vs_0"] = float(seeds_d.mean())
            e["pauc_diff_ci"] = ci(diff)
            e["pauc_diff_seeds_down"], e["pauc_diff_seeds_up"] = int((seeds_d < 0).sum()), int((seeds_d > 0).sum())
            e["pauc_diff_resolved"] = bool(resolved(diff, seeds_d))
            e["det_diff_vs_0"] = float(e["det_clean_thr_mean"] - e0["det_clean_thr_mean"])
        mx_p = max(abs(e["pauc_diff_vs_0"]) for e in out[m]["per_s"][1:])
        mx_d = max(abs(e["det_diff_vs_0"]) for e in out[m]["per_s"][1:])
        out[m]["max_abs_pauc_diff_vs_0"], out[m]["max_abs_det_diff_vs_0"] = float(mx_p), float(mx_d)
        out[m]["verdict"] = "flat / alignment-insensitive" if (mx_p <= 0.02 and mx_d <= 0.02) else ("position-sensitive" if (mx_p > 0.05 or mx_d > 0.05) else "in between")
        spd = np.array(sp_draws[m])
        out[m]["spread_ci_malware"], out[m]["spread_ci_benign"] = ci(spd[:, 0]), ci(spd[:, 1])
        out[m]["pauc_range_ci"] = ci(D.max(1) - D.min(1))
    if len(a.models) >= 2 and "m1" in a.models and "m3" in a.models:
        D1, D3 = np.array(draws["m1"]), np.array(draws["m3"])
        S1, S3 = np.array(sp_draws["m1"]), np.array(sp_draws["m3"])
        out["m1_minus_m3"] = {"pauc_range": {"point": out["m1"]["pauc_range_over_s"] - out["m3"]["pauc_range_over_s"], "ci": ci((D1.max(1) - D1.min(1)) - (D3.max(1) - D3.min(1)))},
                              "spread_malware": {"point": out["m1"]["spread"]["malware_mean"] - out["m3"]["spread"]["malware_mean"], "ci": ci(S1[:, 0] - S3[:, 0])},
                              "spread_benign": {"point": out["m1"]["spread"]["benign_mean"] - out["m3"]["spread"]["benign_mean"], "ci": ci(S1[:, 1] - S3[:, 1])}}
    for m in a.models:
        out[m].pop("_thr", None)
    json.dump(out, open(os.path.join(a.dir, "metrics_test2.json"), "w"), indent=1)
    md = ["| model | s (target) | mean exact s | pAUC@1e-2 | diff vs s=0 (points) | cluster 95% CI | seeds down/up | AUC | malware detected at clean 1% threshold | benign false alarms at that threshold | mean logit change malware / benign |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m in a.models:
        for k, e in enumerate(out[m]["per_s"]):
            if k == 0:
                md.append(f"| {NAME[MK[m]]} | 0 | 0.0 | {e['pauc_mean']:.3f} ± {e['pauc_sd']:.3f} |  |  |  | {e['auc_mean']:.4f} | {100 * e['det_clean_thr_mean']:.1f}% | {100 * e['benign_fpr_clean_thr_mean']:.2f}% |  |")
            else:
                res = "RESOLVED" if e["pauc_diff_resolved"] else "n.r."
                md.append(f"| {NAME[MK[m]]} | {e['s_target']} | {out[m]['s_exact_mean'][k]:.2f} | {e['pauc_mean']:.3f} ± {e['pauc_sd']:.3f} | {100 * e['pauc_diff_vs_0']:+.2f} ({res}) | [{100 * e['pauc_diff_ci'][0]:+.2f}, {100 * e['pauc_diff_ci'][1]:+.2f}] | "
                          f"{e['pauc_diff_seeds_down']}/{e['pauc_diff_seeds_up']} | {e['auc_mean']:.4f} | {100 * e['det_clean_thr_mean']:.1f}% | {100 * e['benign_fpr_clean_thr_mean']:.2f}% | {e['mean_signed_change_malware']:+.3f} / {e['mean_signed_change_benign']:+.3f} |")
    open(os.path.join(a.dir, "tables_test2.md"), "w").write("\n".join(md) + "\n")
    md2 = ["| model | mean spread (max-min over the 9 shifts), malware / benign | median, malware / benign | mean spread / SD of clean logits, malware / benign | control: spread over 9 equal-length paddings (s about 32), malware / benign | pAUC range over s (points) [cluster CI] | verdict |", "|---|---|---|---|---|---|---|"]
    for m in a.models:
        s_, c_ = out[m]["spread"], out[m].get("spread_control_equal_length")
        cs = "not run" if not c_ else f"{c_['malware_mean']:.3f} / {c_['benign_mean']:.3f}"
        md2.append(f"| {NAME[MK[m]]} | {s_['malware_mean']:.3f} [{out[m]['spread_ci_malware'][0]:.3f}, {out[m]['spread_ci_malware'][1]:.3f}] / {s_['benign_mean']:.3f} [{out[m]['spread_ci_benign'][0]:.3f}, {out[m]['spread_ci_benign'][1]:.3f}] | "
                   f"{s_['malware_median']:.3f} / {s_['benign_median']:.3f} | {s_['malware_over_sd']:.3f} / {s_['benign_over_sd']:.3f} | {cs} | {100 * out[m]['pauc_range_over_s']:.2f} [{100 * out[m]['pauc_range_ci'][0]:.2f}, {100 * out[m]['pauc_range_ci'][1]:.2f}] | {out[m]['verdict']} |")
    if "m1_minus_m3" in out:
        c = out["m1_minus_m3"]
        md2 += ["", "M1 minus M3: " + "; ".join(f"{k.replace('_', ' ')} {v['point']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}]" for k, v in c.items()) + " (pAUC range in absolute pAUC units; spreads in logit units; cluster 95% intervals)."]
    open(os.path.join(a.dir, "tables_test2_spread.md"), "w").write("\n".join(md2) + "\n")
    fig2(a, out)


def fig2(a, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
    for m in a.models:
        c, nm = COL[MK[m]], NAME[MK[m]]
        T = [e["s_target"] for e in out[m]["per_s"]]
        for j, (key, sdk) in enumerate([("pauc_mean", "pauc_sd")]):
            mu = np.array([e[key] for e in out[m]["per_s"]])
            sd = np.array([e[sdk] for e in out[m]["per_s"]])
            ax[0].plot(T, mu, marker="o", ms=3, color=c, label=nm)
            ax[0].fill_between(T, mu - sd, np.minimum(1, mu + sd), color=c, alpha=0.15, lw=0)
        det = np.array([e["det_clean_thr"] for e in out[m]["per_s"]])
        ax[1].plot(T, 100 * det.mean(1), marker="o", ms=3, color=c, label=nm)
        ax[1].fill_between(T, 100 * (det.mean(1) - det.std(1, ddof=1)), 100 * (det.mean(1) + det.std(1, ddof=1)), color=c, alpha=0.15, lw=0)
    for a_ in ax[:2]:
        a_.set_xlabel("shift s (tokens of benign calls prepended; targets)")
        a_.set_xticks(T)
        a_.spines[["top", "right"]].set_visible(False)
        a_.axvline(64, color="0.6", lw=0.6, ls=":")
    ax[0].set_ylabel("pAUC@1e-2 (normalised)")
    ax[0].set_title("A. Detection quality against shift", fontsize=9)
    ax[1].set_ylabel("malware detected at the clean 1% FPR threshold (%)")
    ax[1].set_title("B. Detection at the fixed clean threshold", fontsize=9)
    ax[0].legend(fontsize=7)
    n = len(a.models)
    w = 0.8 / n
    for j, m in enumerate(a.models):
        c = COL[MK[m]]
        x = np.arange(2) + (j - (n - 1) / 2) * w
        sp = out[m]["spread"]
        ax[2].bar(x - w * 0.23, [sp["malware_mean"], sp["benign_mean"]], w * 0.44, color=c, label=f"{NAME[MK[m]]}: 9 shifts")
        ctl = out[m].get("spread_control_equal_length")
        if ctl:
            ax[2].bar(x + w * 0.23, [ctl["malware_mean"], ctl["benign_mean"]], w * 0.44, color=c, alpha=0.45, hatch="///", edgecolor="k", lw=0.3, label=f"{NAME[MK[m]]}: control, 9 equal-length paddings")
    ax[2].set_xticks([0, 1])
    ax[2].set_xticklabels(["malware", "benign"])
    ax[2].set_ylabel("mean per-report spread of the logit (max - min)")
    ax[2].set_title("C. Spread of the logit over the shifts", fontsize=9)
    ax[2].legend(fontsize=6)
    ax[2].spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(a.dir, "fig_test2_shift.png"), dpi=200)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", type=int, required=True, choices=[1, 2])
    ap.add_argument("--models", nargs="*", default=["m1", "m3"])
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--dir", default=os.path.join(ROOT, "results", "order_tests"))
    a = ap.parse_args()
    (test1 if a.test == 1 else test2)(a)


if __name__ == "__main__":
    main()
