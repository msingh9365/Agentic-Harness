"""
NOTES 26 item 1a (CPU, stored scores only): cluster-bootstrap 95% intervals for EVERY cell of an attack report (detection and padded-benign false-positive rate, 1% and 0.1% thresholds, all edit sets, white-box steps).   (OURS)

    python -m baseline.followups_ci --scores <dir with scores_m*.npz and wb_m*_seed*.npz> --results <results.json of gs_attack_report> --out results/groupsplit/stage_fgh/followups [--boot 1000] [--tag stage_j]

Method = the clean tables (`twolevel_eval.cluster_bootstrap`): cells (hash_apis group, class) of the April reports resampled with replacement within each class, `numpy` seed 0, ONE resample per draw for every model, seed and edit set. In every draw the threshold of each model and seed is
recomputed on the resample (the unedited April benign logit at rank floor(fpr n), flagged = strictly above), detection = share of the resampled April malware flagged after the edit, padded-benign FPR = share of the resampled April benign reports flagged after the same
edit; the white-box rows use the same resample as multiplicities of the 500 attacked reports (detection) and of the 500 padded benign reports (FPR). The interval is the 2.5 / 97.5 percentile of the MEAN OVER THE SEEDS; the point value is the mean over the seeds on the full
April set and is asserted equal to the value in `results.json`. Scores only; no edited report is built.
"""
import argparse
import glob
import json
import os
from multiprocessing import Pool

import numpy as np

STEPS = (0, 5, 10, 20, 50)
WB_KS = (5, 10, 20, 50)
FPRS = (0.01, 0.001)


def thr_of(z0, idx_b, fpr):
    zb = np.sort(z0[idx_b])[::-1]
    k = int(np.floor(fpr * len(zb)))
    return zb[k] if k < len(zb) else -np.inf


def one_draw(Z, wbs, y, cnt, idx):
    """Z: [seeds, sets, n] float32; wbs: list of per-seed dicts or None. cnt: multiplicity of every April report (1 everywhere = the full set); idx: the resampled indices.
    returns det[sets, 2], fpr[sets, 2], wb_det[len(STEPS), 2], wb_fpr[len(WB_KS), 2] (mean over seeds)."""
    idx_m, idx_b = idx[y[idx] == 1], idx[y[idx] == 0]
    S, J = Z.shape[0], Z.shape[1]
    det, fpr = np.zeros((J, 2)), np.zeros((J, 2))
    wd, wf = np.zeros((len(STEPS), 2)), np.zeros((len(WB_KS), 2))
    wdx, wfx = np.zeros((len(STEPS), 2)), np.zeros((len(WB_KS), 2))                       # white-box with the attack's OWN fixed threshold (the full-set threshold the greedy search stopped at)
    for s in range(S):
        z0 = Z[s, 0]
        for ti, f in enumerate(FPRS):
            t = thr_of(z0, idx_b, f)
            det[:, ti] += (Z[s][:, idx_m] > t).mean(1)
            fpr[:, ti] += (Z[s][:, idx_b] > t).mean(1)
            if wbs is not None:
                w = wbs[s]
                cm = cnt[w["sel"]].astype(np.float64)
                cb = cnt[w["ben_ids"]].astype(np.float64)
                for si, k in enumerate(STEPS):
                    wd[si, ti] += ((w["best"][k] > t) * cm).sum() / cm.sum()
                for ki, k in enumerate(WB_KS):
                    wf[ki, ti] += ((w[f"ben_k{k}"] > t) * cb).sum() / cb.sum()
                tx = w["t1" if ti == 0 else "t01"]
                for si, k in enumerate(STEPS):
                    wdx[si, ti] += ((w["best"][k] > tx) * cm).sum() / cm.sum()
                for ki, k in enumerate(WB_KS):
                    wfx[ki, ti] += ((w[f"ben_k{k}"] > tx) * cb).sum() / cb.sum()
    return det / S, fpr / S, wd / S, wf / S, wdx / S, wfx / S


def run_model(args):
    f, scores_dir, boot, _unused = args
    from baseline.twolevel_eval import april_meta
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    _, _, groups = april_meta()
    d = np.load(os.path.join(scores_dir, f"scores_{f}.npz"))
    names = [str(n) for n in d["names"]]
    seeds = sorted(int(k[4:]) for k in d.files if k.startswith("seed"))
    Z = np.stack([d[f"seed{s}"] for s in seeds]).astype(np.float32)
    wbs = None
    fs = sorted(glob.glob(os.path.join(scores_dir, f"wb_{f}_seed*.npz")))
    if fs:
        wbs = []
        for p_ in fs:
            w = np.load(p_)
            wbs.append({"sel": w["sel"], "ben_ids": w["ben_ids"], "t1": float(w["t1"]), "t01": float(w["t01"]), "best": w["best"].astype(np.float64), **{f"ben_k{k}": w[f"ben_k{k}"].astype(np.float64) for k in WB_KS}})
    n = len(y)
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    point = one_draw(Z, wbs, y, np.ones(n, dtype=np.int64), np.arange(n))
    rng = np.random.default_rng(0)
    draws = [[] for _ in range(6)]
    for b in range(boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        out = one_draw(Z, wbs, y, np.bincount(sel, minlength=n), sel)
        for j in range(6):
            draws[j].append(out[j])
        if b % 200 == 0:
            print(f"[{f}] draw {b}/{boot}", flush=True)
    ci = [np.percentile(np.array(x), [2.5, 97.5], axis=0) for x in draws]
    return f, {"names": names, "seeds": seeds, "has_wb": wbs is not None, "point": [p_.tolist() for p_ in point], "ci": [c.tolist() for c in ci]}


def fmt(pt, lo, hi, d=1, scale=100.0):
    return f"{scale * pt:.{d}f} [{scale * lo:.{d}f}, {scale * hi:.{d}f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--results", required=True, help="results.json of gs_attack_report for the same scores (the point values are asserted equal to it)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--tag", default="stage_j")
    ap.add_argument("--models", nargs="*", default=["m1", "m2", "m3", "m4"])
    ap.add_argument("--labels", nargs="*", default=None, help="display names, same order as --models")
    ap.add_argument("--report-sets", nargs="*", default=["unedited", "random_20_prepend", "random_50_prepend", "random_100_prepend", "random_200_insert", "lgbm_50_prepend"])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    disp = dict(zip(a.models, a.labels or ["M1 Nebula", "M2 two-level", "M3 ATT+bal", "M4 ATT+bal-2L"][:len(a.models)]))
    with Pool(min(a.procs, len(a.models))) as pool:
        res = dict(pool.map(run_model, [(m, a.scores, a.boot, 0) for m in a.models], chunksize=1))
    R = json.load(open(a.results))
    names = res[a.models[0]]["names"]
    # the point values must equal the report's values
    worst = 0.0
    for m in a.models:
        for j, nm in enumerate(names):
            for ti, key in enumerate(("t1", "t01")):
                e = R[f"{m}|{nm}|{key}"]
                worst = max(worst, abs(np.mean(e["detection"]) - res[m]["point"][0][j][ti]), abs(np.mean(e["padded_benign_fpr"]) - res[m]["point"][1][j][ti]))
        if res[m]["has_wb"]:
            for ti, key in enumerate(("t1", "t01")):
                sh = np.mean(R[f"wb|{m}|{key}"]["flagged_share_by_step_per_seed"], axis=0)
                for si, k in enumerate(STEPS):
                    worst = max(worst, abs(sh[k] - res[m]["point"][2][si][ti]))
    print("largest difference between the point values and results.json:", worst)
    assert worst < 1e-6, "point values differ from results.json"
    # tables
    def cell(m, which, j, ti):
        r = res[m]
        return fmt(r["point"][which][j][ti], r["ci"][which][0][j][ti], r["ci"][which][1][j][ti], 1 if which == 0 else 2)
    L = [f"### Cluster-bootstrap 95% intervals of the {a.tag} cells (value = mean over 10 seeds [2.5%, 97.5% interval of the seed mean]; cells = (hash_apis group, class), {a.boot} resamples, seed 0; thresholds recomputed on every resample)", ""]
    hd = ["row"] + [disp[m] for m in a.models]
    def md(rows):
        return ["| " + " | ".join(hd) + " |", "|" + "---|" * len(hd)] + ["| " + " | ".join(r) + " |" for r in rows]
    rows = [[nm.replace("_", " ")] + [cell(m, 0, names.index(nm), 0) for m in a.models] for nm in a.report_sets if nm in names]
    for k in (20, 50):
        si = STEPS.index(k)
        rows.append([f"white-box {k} steps"] + [fmt(res[m]["point"][2][si][0], res[m]["ci"][2][0][si][0], res[m]["ci"][3 - 1][1][si][0]) if res[m]["has_wb"] else "pending" for m in a.models])
    rows.append(["padded-benign FPR (%), random 50 prepend"] + [cell(m, 1, names.index("random_50_prepend"), 0) for m in a.models] if "random_50_prepend" in names else ["padded-benign FPR, random 50 prepend"] + ["n/a"] * len(a.models))
    L += ["**The cells of the Stage J report table (detection of April malware at the 1% clean-FPR threshold, %; last row padded-benign FPR %)**", ""] + md(rows) + [""]
    for ti, tl in ((0, "1%"), (1, "0.1%")):
        L += [f"**Detection of April malware after the edit, {tl} threshold (%)**", ""] + md([[nm.replace("_", " ")] + [cell(m, 0, j, ti) for m in a.models] for j, nm in enumerate(names)]) + [""]
        L += [f"**Padded-benign FPR after the same edit, {tl} threshold (%)**", ""] + md([[nm.replace("_", " ")] + [cell(m, 1, j, ti) for m in a.models] for j, nm in enumerate(names)]) + [""]
    if any(res[m]["has_wb"] for m in a.models):
        for ti, tl in ((0, "1%"), (1, "0.1%")):
            rows = []
            for si, k in enumerate(STEPS):
                rows.append([f"white-box {k} steps: still flagged ({tl})"] + [fmt(res[m]["point"][2][si][ti], res[m]["ci"][2][0][si][ti], res[m]["ci"][2][1][si][ti]) if res[m]["has_wb"] else "pending" for m in a.models])
            for ki, k in enumerate(WB_KS):
                rows.append([f"white-box {k} steps: padded-benign FPR ({tl})"] + [fmt(res[m]["point"][3][ki][ti], res[m]["ci"][3][0][ki][ti], res[m]["ci"][3][1][ki][ti], 2) if res[m]["has_wb"] else "pending" for m in a.models])
            L += [f"**White-box greedy attack ({tl} threshold; 500 attacked April malware, 500 padded benign; resampled as multiplicities)**", ""] + md(rows) + [""]
            rows = []
            for si, k in enumerate(STEPS):
                rows.append([f"white-box {k} steps: still flagged ({tl}, fixed threshold)"] + [fmt(res[m]["point"][4][si][ti], res[m]["ci"][4][0][si][ti], res[m]["ci"][4][1][si][ti]) if res[m]["has_wb"] else "pending" for m in a.models])
            for ki, k in enumerate(WB_KS):
                rows.append([f"white-box {k} steps: padded-benign FPR ({tl}, fixed threshold)"] + [fmt(res[m]["point"][5][ki][ti], res[m]["ci"][5][0][ki][ti], res[m]["ci"][5][1][ki][ti], 2) if res[m]["has_wb"] else "pending" for m in a.models])
            L += [f"**White-box, the attack's own fixed threshold ({tl}): only the reports are resampled, the threshold stays at the full-set value the greedy search stopped at. The recomputed-threshold intervals above are wider and lopsided for the white-box rows because the greedy search stops as soon as a report falls below the full-set threshold, so a resample with a lower threshold flags such reports again.**", ""] + md(rows) + [""]
    open(os.path.join(a.out, f"{a.tag}_cluster_ci.md"), "w").write("\n".join(L) + "\n")
    json.dump({"method": "cluster bootstrap, cells (hash_apis group, class), seed 0, thresholds recomputed per resample, CI of the seed mean", "boot": a.boot, "names": names, "models": res, "max_point_difference_to_results_json": worst},
              open(os.path.join(a.out, f"{a.tag}_cluster_ci.json"), "w"))
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()
