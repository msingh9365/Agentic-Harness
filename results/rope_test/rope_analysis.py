"""
Evaluation of the RoPE test (NOTES_ROPE.md sections 4 and 5): clean metrics, shuffle test, shift test, attacks, contrasts with cluster bootstrap, decision rule, tables, two figures.   (OURS; CPU)

    python results/rope_test/rope_analysis.py --dir results/rope_test [--boot 1000] [--procs 4]
Inputs (scores only): v0/scores_test{1,2}_m3.npz (stored, branch cpu-order-tests), order/scores_test{1,2}_v{1,2,3}.npz, attack/scores_{m3,v1,v2,v3}.npz (+ attack/wb_*_seed*.npz), clean April logits = the z_clean of test 1.
Variants: v0 = M3 ATT+bal, v1 = M3 + RoPE (blocks), v2 = M3 + RoPE (full), v3 = M3 + full attention.
Bootstrap = cluster bootstrap over the 2,509 April hash_apis groups (cells = group x class, 1,000 resamples, numpy seed 0, the same resample for every variant, metrics per seed then mean over seeds,
thresholds recomputed on the resample's clean benign scores for the detection numbers). Resolved = the cluster 95% interval excludes 0 (NOTES_ROPE section 4.5).
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from baseline import common as C, padtest  # noqa: E402
from baseline.twolevel_eval import april_meta  # noqa: E402
from baseline.paper_figs import COL as MCOL  # noqa: E402

VARS = ["v0", "v1", "v2", "v3"]
LABEL = {"v0": "M3 ATT+bal", "v1": "M3 + RoPE (blocks)", "v2": "M3 + RoPE (full)", "v3": "M3 + full attention"}
COL = {"v0": MCOL["M3"], "v1": "#CC79A7", "v2": "#56B4E9", "v3": "#999999"}
FAM = {"v0": "m3", "v1": "v1", "v2": "v2", "v3": "v3"}
SHUF = ["a", "b", "c", "d"]
SHUF_LABEL = {"a": "window shuffle", "b": "local shuffle (5)", "c": "reversal", "d": "full shuffle (reference)"}
TARGETS = [0, 8, 16, 24, 32, 40, 48, 56, 64]
ATT_SHOW = ["random_20_prepend", "random_50_prepend", "random_100_prepend", "random_50_insert", "random_200_insert", "lgbm_50_prepend", "lgbm_50_insert"]
CRIT_SET = "lgbm_50_prepend"
G = {}


def pairs_of():
    return [("v1", "v0"), ("v2", "v0"), ("v3", "v0"), ("v2", "v3")]


def load(d):
    S = {}
    for v in VARS:
        t1 = np.load(os.path.join(d, "v0" if v == "v0" else "order", f"scores_test1_{'m3' if v == 'v0' else v}.npz"))
        t2 = np.load(os.path.join(d, "v0" if v == "v0" else "order", f"scores_test2_{'m3' if v == 'v0' else v}.npz"))
        at = np.load(os.path.join(d, "attack", f"scores_{FAM[v]}.npz"))
        seeds = [int(s) for s in t1["seeds"]]
        assert seeds == list(range(10)), (v, seeds)
        names = [str(x) for x in at["names"]]
        S[v] = {"y": t1["y"].astype(int), "clean": t1["z_clean"].astype(np.float64), "shuf": {k: t1[f"z_{k}"].astype(np.float64) for k in SHUF}, "shift": t2["z_shift"].astype(np.float64),
                "att": np.stack([at[f"seed{s}"] for s in seeds]).astype(np.float64), "att_names": names, "s_exact": t2["s_exact"]}
        assert np.allclose(S[v]["att"][:, 0], S[v]["clean"], atol=2e-3), v                 # unedited attack scores = the clean logits (batch-composition tolerance 2e-3, as the attack jobs)
    return S


def measures(sel):
    """dict v -> flat vector of metrics of the resample `sel`: [clean pAUC, a, b, c, d, 9 shift pAUCs, detection(lgbm50 prepend), det per other shown sets...]; each the mean over the seeds, plus per-seed arrays."""
    out = {}
    for v in VARS:
        s = G[v]
        y = s["y"][sel]
        per = {"clean": [], "shuf": {k: [] for k in SHUF}, "shift": [], "det": {n: [] for n in ATT_SHOW}, "tpr1": [], "auc": [], "tpr1e3": []}
        for i in range(s["clean"].shape[0]):
            zc = s["clean"][i][sel]
            r = C.roc_summary(y, zc)
            per["clean"].append(r[3])
            per["tpr1"].append(r[1])
            per["tpr1e3"].append(r[0])
            per["auc"].append(r[2])
            for k in SHUF:
                per["shuf"][k].append(C.roc_summary(y, s["shuf"][k][i][sel])[3])
            per["shift"].append([C.roc_summary(y, s["shift"][i][j][sel])[3] for j in range(len(TARGETS))])
            thr = padtest.thresholds(zc, y, 0.01)
            for n in ATT_SHOW:
                za = s["att"][i][s["att_names"].index(n)][sel]
                per["det"][n].append(float((za[y == 1] > thr).mean()))
        out[v] = per
    return out


def _init(S):
    G.update(S)


def run_boot(S, members, n_boot, procs):
    rng = np.random.default_rng(0)
    sels = [np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)]) for _ in range(n_boot)]
    with Pool(procs, initializer=_init, initargs=(S,)) as pool:
        res = pool.map(measures, sels, chunksize=4)
    return res


def vec(per):
    """seed-mean vector of one variant's measures: [clean, a, b, c, d, shifts x9, det x len(ATT_SHOW)]"""
    return np.concatenate([[np.mean(per["clean"])], [np.mean(per["shuf"][k]) for k in SHUF], np.mean(per["shift"], axis=0), [np.mean(per["det"][n]) for n in ATT_SHOW]])


def seedvec(per):
    return np.concatenate([[per["clean"]], [per["shuf"][k] for k in SHUF], np.array(per["shift"]).T, [per["det"][n] for n in ATT_SHOW]], axis=0).T          # [seeds, n]


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def groups_members(y):
    _, _, groups = april_meta()
    assert len(set(groups)) == 2509 and len(groups) == len(y)
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    return members, groups


IDX = {"clean": 0, "a": 1, "b": 2, "c": 3, "d": 4}
IDX_SHIFT = {s: 5 + j for j, s in enumerate(TARGETS)}
IDX_DET = {n: 5 + len(TARGETS) + j for j, n in enumerate(ATT_SHOW)}


def derived(v):
    """name -> function of a flat vector returning the number (in pAUC units or detection share)."""
    return {
        "clean_pauc": lambda x: x[IDX["clean"]],
        "drop_window": lambda x: x[IDX["clean"]] - x[IDX["a"]],
        "drop_local": lambda x: x[IDX["clean"]] - x[IDX["b"]],
        "drop_reversal": lambda x: x[IDX["clean"]] - x[IDX["c"]],
        "drop_full": lambda x: x[IDX["clean"]] - x[IDX["d"]],
        **{f"shift_drop_{s}": (lambda s_: (lambda x: x[IDX_SHIFT[0]] - x[IDX_SHIFT[s_]]))(s) for s in TARGETS[1:]},
        **{f"det_{n}": (lambda n_: (lambda x: x[IDX_DET[n_]]))(n) for n in ATT_SHOW},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    S = load(a.dir)
    y = S["v0"]["y"]
    members, groups = groups_members(y)
    allsel = np.arange(len(y))
    point = measures(allsel)
    X = {v: vec(point[v]) for v in VARS}
    XS = {v: seedvec(point[v]) for v in VARS}                                        # [seeds, n]
    print("point estimates done", flush=True)
    boot = run_boot(S, members, a.boot, a.procs)
    B = {v: np.array([vec(b[v]) for b in boot]) for v in VARS}                          # [boot, n]
    print("bootstrap done", flush=True)
    D = derived(None)
    res = {"variants": {}, "contrasts": {}, "criteria": {}}
    # per variant
    for v in VARS:
        r = {}
        for name, f in D.items():
            pt = float(f(X[v]))
            seeds_ = np.array([f(row) for row in XS[v]])
            r[name] = {"point": pt, "ci": ci(np.array([f(b) for b in B[v]])), "seed_values": seeds_.tolist(), "seeds_positive": int((seeds_ > 0).sum()), "seeds_negative": int((seeds_ < 0).sum())}
        zc = S[v]["clean"]
        mal, ben = y == 1, y == 0
        r["logit_change_abs"] = {k: {"malware": float(np.abs(S[v]["shuf"][k] - zc)[:, mal].mean()), "benign": float(np.abs(S[v]["shuf"][k] - zc)[:, ben].mean())} for k in SHUF}
        r["clean_logit_sd"] = {"malware": float(zc[:, mal].std(axis=1).mean()), "benign": float(zc[:, ben].std(axis=1).mean())}
        sh = XS[v][:, IDX_SHIFT[0]][:, None] - XS[v][:, [IDX_SHIFT[s] for s in TARGETS[1:]]]
        r["largest_shift_drop_target"] = int(TARGETS[1:][int(np.argmax(sh.mean(0)))])
        res["variants"][v] = r
        # clean metrics (point): TPR, AUC, F1 at logit 0
        bm = [C.binary_metrics(y, zc[i], decision=0.0) for i in range(zc.shape[0])]
        res["variants"][v]["clean_metrics"] = {k: [float(np.mean([m[k] for m in bm])), float(np.std([m[k] for m in bm], ddof=1))] for k in ("auc", "tpr@0.001", "tpr@0.01", "pauc@0.01", "f1@0.5")}
        # attack tables (all sets), detection at 1% and 0.1% thresholds, padded-benign FPR (descriptive; point estimates)
        names = S[v]["att_names"]
        tabs = {}
        for si, n in enumerate(names):
            d1, d01, fb1 = [], [], []
            for i in range(zc.shape[0]):
                t1, t01 = padtest.thresholds(zc[i], y, 0.01), padtest.thresholds(zc[i], y, 0.001)
                za = S[v]["att"][i][si]
                d1.append(float((za[mal] > t1).mean()))
                d01.append(float((za[mal] > t01).mean()))
                fb1.append(float((za[ben] > t1).mean()))
            tabs[n] = {"det1": [float(np.mean(d1)), float(np.std(d1, ddof=1))], "det01": [float(np.mean(d01)), float(np.std(d01, ddof=1))], "benign_fpr1": [float(np.mean(fb1)), float(np.std(fb1, ddof=1))]}
        res["variants"][v]["attacks"] = tabs
        # shift table (point estimates, per s)
        res["variants"][v]["shift_pauc"] = {str(s): [float(np.mean(point[v]["shift"], axis=0)[j]), float(np.std(np.array(point[v]["shift"])[:, j], ddof=1))] for j, s in enumerate(TARGETS)}
        # detection at the clean threshold per s (descriptive)
        det_s = []
        for j in range(len(TARGETS)):
            ds = [float((S[v]["shift"][i][j][mal] > padtest.thresholds(zc[i], y, 0.01)).mean()) for i in range(zc.shape[0])]
            det_s.append(float(np.mean(ds)))
        res["variants"][v]["shift_detection_at_clean_threshold"] = det_s
        # seen / unseen (pAUC@1e-2 within the subset)
    from baseline import groupsplit as GS
    jt = GS.january_table()
    trn_set = set(jt["train"]["hash_apis"])
    seen = np.array([h in trn_set for h in jt["test"]["hash_apis"]])
    for v in VARS:
        zc = S[v]["clean"]
        res["variants"][v]["seen_unseen_pauc"] = {nm: [float(np.mean([C.roc_summary(y[m], zc[i][m])[3] for i in range(zc.shape[0])])), int(m.sum())] for nm, m in (("seen", seen), ("unseen", ~seen))}
    # white-box (V1, V2 seeds 0-2; V0 seeds 0-2 for the same seeds)
    wb = {}
    for v in VARS:
        rows = []
        for s in range(3):
            p = os.path.join(a.dir, "attack", f"wb_{FAM[v]}_seed{s}.npz")
            if os.path.exists(p):
                x = np.load(p)
                rows.append({k: float((x["best"][k] > float(x["t1"])).mean()) for k in (0, 5, 10, 20, 50)})
        if rows:
            wb[v] = {"seeds": len(rows), "detection_after_steps": {str(k): [float(np.mean([r[k] for r in rows])), float(np.std([r[k] for r in rows], ddof=1)) if len(rows) > 1 else 0.0] for k in rows[0]}}
    res["whitebox"] = wb
    # contrasts
    for (p, q) in pairs_of():
        c = {}
        for name, f in D.items():
            dp = np.array([f(b) for b in B[p]]) - np.array([f(b) for b in B[q]])
            sd = np.array([f(row) for row in XS[p]]) - np.array([f(row) for row in XS[q]])
            lo, hi = ci(dp)
            c[name] = {"point": float(f(X[p]) - f(X[q])), "ci": [lo, hi], "resolved": bool(lo > 0 or hi < 0), "seeds_up": int((sd > 0).sum()), "seeds_down": int((sd < 0).sum())}
        res["contrasts"][f"{p}-{q}"] = c
    # decision rule (NOTES_ROPE section 5), per variant against v0
    for v in ["v1", "v2", "v3"]:
        cr = {}
        dw = res["variants"][v]["drop_window"]
        cr["i_window_drop_ge_5_resolved"] = {"met": bool(dw["point"] >= 0.05 and (dw["ci"][0] > 0)), "drop_points": 100 * dw["point"], "ci_points": [100 * dw["ci"][0], 100 * dw["ci"][1]]}
        drops = {s: res["variants"][v][f"shift_drop_{s}"] for s in TARGETS[1:]}
        s_star = max(drops, key=lambda s: drops[s]["point"])
        ds_ = drops[s_star]
        cr["ii_largest_shift_drop_le_2_not_resolved"] = {"met": bool(ds_["point"] <= 0.02 and ds_["ci"][0] <= 0 <= ds_["ci"][1]), "largest_drop_points": 100 * ds_["point"], "at_s": s_star, "ci_points": [100 * ds_["ci"][0], 100 * ds_["ci"][1]]}
        cd = res["contrasts"][f"{v}-v0"][f"det_{CRIT_SET}"]
        cr["iii_lgbm50_prepend_detection_not_resolved_worse"] = {"met": bool(not (cd["ci"][1] < 0)), "difference_points": 100 * cd["point"], "ci_points": [100 * cd["ci"][0], 100 * cd["ci"][1]], "seeds_up_down": [cd["seeds_up"], cd["seeds_down"]]}
        cc = res["contrasts"][f"{v}-v0"]["clean_pauc"]
        cr["iv_clean_pauc_not_resolved_worse"] = {"met": bool(not (cc["ci"][1] < 0)), "difference_points": 100 * cc["point"], "ci_points": [100 * cc["ci"][0], 100 * cc["ci"][1]], "seeds_up_down": [cc["seeds_up"], cc["seeds_down"]]}
        cr["all_met"] = all(cr[k]["met"] for k in cr if k != "all_met")
        res["criteria"][v] = cr
    # v0 reference for the same criteria (descriptive)
    dw0 = res["variants"]["v0"]["drop_window"]
    res["criteria"]["v0_reference"] = {"window_drop_points": 100 * dw0["point"], "window_drop_ci_points": [100 * dw0["ci"][0], 100 * dw0["ci"][1]], "largest_shift_drop_points": 100 * max(res["variants"]["v0"][f"shift_drop_{s}"]["point"] for s in TARGETS[1:])}
    json.dump(res, open(os.path.join(a.dir, "metrics.json"), "w"), indent=1)
    write_tables(a.dir, res)
    figures(a.dir, res)
    print("done", flush=True)


def pts(x):
    return f"{100 * x:+.2f}"


def write_tables(d, res):
    V = res["variants"]
    L = []
    # clean
    L.append("### Clean April (10 seeds; mean ± SD over seeds)\n")
    L.append("| variant | pAUC@1e-2 | TPR@1e-3 | TPR@1e-2 | AUC | F1 at logit 0 | pAUC@1e-2 seen / unseen (n) |")
    L.append("|---|---|---|---|---|---|---|")
    for v in VARS:
        m = V[v]["clean_metrics"]
        su = V[v]["seen_unseen_pauc"]
        L.append(f"| {LABEL[v]} | {m['pauc@0.01'][0]:.3f} ± {m['pauc@0.01'][1]:.3f} | {m['tpr@0.001'][0]:.3f} | {m['tpr@0.01'][0]:.3f} | {m['auc'][0]:.4f} | {m['f1@0.5'][0]:.4f} | {su['seen'][0]:.3f} ({su['seen'][1]}) / {su['unseen'][0]:.3f} ({su['unseen'][1]}) |")
    L.append("\n### Shuffle test: drop of pAUC@1e-2 (clean minus variant, points), cluster 95% interval, seeds down / up\n")
    L.append("| variant | window shuffle | local shuffle (5) | reversal | full shuffle (reference) | mean abs logit change under window shuffle, malware / benign (SD of clean logits) |")
    L.append("|---|---|---|---|---|---|")
    for v in VARS:
        cells = []
        for nm in ("drop_window", "drop_local", "drop_reversal", "drop_full"):
            r = V[v][nm]
            cells.append(f"{100 * r['point']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}] {r['seeds_positive']}/{r['seeds_negative']}")
        lc = V[v]["logit_change_abs"]["a"]
        L.append(f"| {LABEL[v]} | " + " | ".join(cells) + f" | {lc['malware']:.2f} / {lc['benign']:.2f} ({V[v]['clean_logit_sd']['malware']:.1f} / {V[v]['clean_logit_sd']['benign']:.1f}) |")
    L.append("\n### Shift test: pAUC@1e-2 at the shifts (mean ± SD over seeds) and the drop against shift 0 (points; cluster 95% interval)\n")
    L.append("| variant | " + " | ".join(f"s {s}" for s in TARGETS) + " | largest drop (at s) |")
    L.append("|---|" + "---|" * (len(TARGETS) + 1))
    for v in VARS:
        row = [f"{V[v]['shift_pauc'][str(s)][0]:.3f}" for s in TARGETS]
        sstar = V[v]["largest_shift_drop_target"]
        r = V[v][f"shift_drop_{sstar}"]
        L.append(f"| {LABEL[v]} | " + " | ".join(row) + f" | {100 * r['point']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}] (s {sstar}) |")
    L.append("\nDetection of malware at the clean 1% threshold per shift (%):\n")
    L.append("| variant | " + " | ".join(f"s {s}" for s in TARGETS) + " |")
    L.append("|---|" + "---|" * len(TARGETS))
    for v in VARS:
        L.append(f"| {LABEL[v]} | " + " | ".join(f"{100 * x:.1f}" for x in V[v]["shift_detection_at_clean_threshold"]) + " |")
    L.append("\n### Padding attacks: detection of April malware at the clean 1% FPR threshold (%, mean ± SD over 10 seeds); last block: padded-benign false-alarm rate (%)\n")
    sets = [n for n in V["v0"]["attacks"]]
    L.append("| edit set | " + " | ".join(LABEL[v] for v in VARS) + " |")
    L.append("|---|" + "---|" * len(VARS))
    for n in sets:
        L.append(f"| {n.replace('_', ' ')} | " + " | ".join(f"{100 * V[v]['attacks'][n]['det1'][0]:.1f} ± {100 * V[v]['attacks'][n]['det1'][1]:.1f}" for v in VARS) + " |")
    L.append("\nPadded-benign FPR (%) at the same threshold:\n")
    L.append("| edit set | " + " | ".join(LABEL[v] for v in VARS) + " |")
    L.append("|---|" + "---|" * len(VARS))
    for n in sets[1:]:
        L.append(f"| {n.replace('_', ' ')} | " + " | ".join(f"{100 * V[v]['attacks'][n]['benign_fpr1'][0]:.2f}" for v in VARS) + " |")
    if res["whitebox"]:
        L.append("\n### White-box greedy search (500 April malware, 50 steps, seeds 0 to 2): share still flagged at the clean 1% threshold (%)\n")
        L.append("| variant | seeds | step 0 | 5 | 10 | 20 | 50 |")
        L.append("|---|---|---|---|---|---|---|")
        for v, w in res["whitebox"].items():
            dd = w["detection_after_steps"]
            L.append(f"| {LABEL[v]} | {w['seeds']} | " + " | ".join(f"{100 * dd[k][0]:.1f}" for k in ("0", "5", "10", "20", "50")) + " |")
    L.append("\n### Contrasts (point, cluster 95% interval, seeds up / down; RESOLVED = interval excludes 0)\n")
    L.append("| contrast | clean pAUC@1e-2 | window-shuffle drop | largest shift drop (s 8 / 64 shown) | detection under LightGBM 50 prepend |")
    L.append("|---|---|---|---|---|")
    for k, c in res["contrasts"].items():
        def f(n):
            r = c[n]
            return f"{100 * r['point']:+.2f} [{100 * r['ci'][0]:+.2f}, {100 * r['ci'][1]:+.2f}] {r['seeds_up']}/{r['seeds_down']}" + (" RESOLVED" if r["resolved"] else "")
        L.append(f"| {k} | {f('clean_pauc')} | {f('drop_window')} | s8: {f('shift_drop_8')}; s64: {f('shift_drop_64')} | {f('det_lgbm_50_prepend')} |")
    L.append("\n### Decision rule (NOTES_ROPE section 5)\n")
    L.append("| variant | (i) window-shuffle drop >= 5 points and resolved | (ii) largest shift drop <= 2 points, not resolved | (iii) LightGBM-50-prepend detection not resolved worse than M3 | (iv) clean pAUC not resolved worse than M3 | order-aware and position-robust |")
    L.append("|---|---|---|---|---|---|")
    for v in ["v1", "v2", "v3"]:
        cr = res["criteria"][v]
        i, ii, iii, iv = cr["i_window_drop_ge_5_resolved"], cr["ii_largest_shift_drop_le_2_not_resolved"], cr["iii_lgbm50_prepend_detection_not_resolved_worse"], cr["iv_clean_pauc_not_resolved_worse"]
        L.append(f"| {LABEL[v]} | {'met' if i['met'] else 'NOT met'} ({i['drop_points']:+.2f}; [{i['ci_points'][0]:+.2f}, {i['ci_points'][1]:+.2f}]) | {'met' if ii['met'] else 'NOT met'} ({ii['largest_drop_points']:+.2f} at s {ii['at_s']}; [{ii['ci_points'][0]:+.2f}, {ii['ci_points'][1]:+.2f}]) | "
                 f"{'met' if iii['met'] else 'NOT met'} ({iii['difference_points']:+.2f}; [{iii['ci_points'][0]:+.2f}, {iii['ci_points'][1]:+.2f}]) | {'met' if iv['met'] else 'NOT met'} ({iv['difference_points']:+.2f}; [{iv['ci_points'][0]:+.2f}, {iv['ci_points'][1]:+.2f}]) | **{'YES' if cr['all_met'] else 'no'}** |")
    ref = res["criteria"]["v0_reference"]
    L.append(f"\nReference M3 (V0): window-shuffle drop {ref['window_drop_points']:+.2f} points [{ref['window_drop_ci_points'][0]:+.2f}, {ref['window_drop_ci_points'][1]:+.2f}]; largest shift drop {ref['largest_shift_drop_points']:+.2f} points.")
    open(os.path.join(d, "tables.md"), "w").write("\n".join(L) + "\n")


def figures(d, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    V = res["variants"]
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    kinds = [("drop_window", "window shuffle"), ("drop_local", "local shuffle (5)"), ("drop_reversal", "reversal")]
    w = 0.2
    for j, v in enumerate(VARS):
        x = np.arange(3) + (j - 1.5) * w
        pt = [100 * V[v][k]["point"] for k, _ in kinds]
        lo = [100 * (V[v][k]["point"] - V[v][k]["ci"][0]) for k, _ in kinds]
        hi = [100 * (V[v][k]["ci"][1] - V[v][k]["point"]) for k, _ in kinds]
        ax.bar(x, pt, w * 0.92, color=COL[v], label=LABEL[v], yerr=[lo, hi], capsize=2, error_kw={"lw": 0.8})
    ax.axhline(5, color="k", lw=0.8, ls="--")
    ax.text(2.45, 5.6, "5-point line (criterion i)", ha="right", fontsize=7)
    ax.set_xticks(range(3))
    ax.set_xticklabels([n for _, n in kinds])
    ax.set_ylabel("drop of pAUC@1e-2 against clean (points)\nmean of 10 seeds, whiskers: cluster 95% interval")
    ax.legend(fontsize=7)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(d, "fig_shuffle_drop.png"), dpi=200)
    fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
    for v in VARS:
        mu = np.array([V[v]["shift_pauc"][str(s)][0] for s in TARGETS])
        sd = np.array([V[v]["shift_pauc"][str(s)][1] for s in TARGETS])
        ax[0].plot(TARGETS, mu, marker="o", ms=3, color=COL[v], label=LABEL[v])
        ax[0].fill_between(TARGETS, mu - sd, np.minimum(1, mu + sd), color=COL[v], alpha=0.15, lw=0)
        ax[1].plot(TARGETS, 100 * np.array(V[v]["shift_detection_at_clean_threshold"]), marker="o", ms=3, color=COL[v], label=LABEL[v])
    ax[0].set_ylabel("pAUC@1e-2 (normalised)")
    ax[1].set_ylabel("malware detected at the clean 1% FPR threshold (%)")
    for a_ in ax:
        a_.set_xlabel("shift s (tokens of benign calls prepended; targets)")
        a_.set_xticks(TARGETS)
        a_.spines[["top", "right"]].set_visible(False)
    ax[0].legend(fontsize=7)
    ax[0].set_title("A. Detection quality against shift", fontsize=9)
    ax[1].set_title("B. Detection at the fixed clean threshold", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(d, "fig_shift_curve.png"), dpi=200)


if __name__ == "__main__":
    main()
