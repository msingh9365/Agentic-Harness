"""
Stage H report of NOTES 23: tables and the detection-vs-k figure for the attacks on M1 to M4 (scores of baseline/gs_attack.py; scores only).   (OURS)

    python -m baseline.gs_attack_report --scores <dir with scores_m*.npz and wb_m*_seed*.npz> --out results/groupsplit/stage_fgh/stage_h

Thresholds: the benign logit at rank floor(0.01 n) (1% FPR) and floor(0.001 n) (0.1% FPR) of each model's unedited April benign scores, per model and seed; flagged = above. Detection = share of the April MALWARE
reports flagged after the edit; padded-benign FPR = share of the April BENIGN reports flagged after the same edit (all 17,402 April reports are edited). Mean ± std over the seeds present.
White-box: share of the 500 attacked malware reports still flagged after k steps; padded-benign FPR = share of the 500 benign reports padded with the call list chosen for malware report i after k steps.
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C, padtest
from baseline.twolevel_eval import april_meta

MODELS = [("m1", "M1 v2-PE"), ("m2", "M2 two-level, no padding"), ("m3", "M3 ATT+bal"), ("m4", "M4 ATT+bal-2L")]
COL = {"m1": "#6250d6", "m2": "#999999", "m3": "#1baf7a", "m4": "#eb6834"}


def md(rows, header):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def ms(v, d=1):
    v = 100 * np.asarray(v)
    return f"{v.mean():.{d}f} ± {v.std(ddof=1) if len(v) > 1 else 0:.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    fam, _, _ = april_meta()
    mal, ben = y == 1, y == 0
    S, R = {}, {}
    for f, _ in MODELS:
        p = os.path.join(a.scores, f"scores_{f}.npz")
        if not os.path.exists(p):
            continue
        d = np.load(p)
        names = [str(n) for n in d["names"]]
        seeds = sorted(int(k[4:]) for k in d.files if k.startswith("seed"))
        Z = {s: d[f"seed{s}"].astype(np.float64) for s in seeds}
        S[f] = {"names": names, "seeds": seeds, "Z": Z}
        t1 = {s: padtest.thresholds(Z[s][0], y, 0.01) for s in seeds}
        t01 = {s: padtest.thresholds(Z[s][0], y, 0.001) for s in seeds}
        R[f] = {"t1": t1, "t01": t01}
    names = S[next(iter(S))]["names"]
    L = [f"### Attacks on the four final models (April, all reports edited; seeds present: " + ", ".join(f"{f}: {len(S[f]['seeds'])}" for f in S) + ")", ""]
    out = {}
    for thr_key, thr_lab in (("t1", "1% FPR"), ("t01", "0.1% FPR")):
        det, fpr = [], []
        for j, nm in enumerate(names):
            rd, rf = [nm], [nm]
            for f, _ in MODELS:
                if f not in S:
                    rd.append("n/a"), rf.append("n/a")
                    continue
                dv = [(S[f]["Z"][s][j][mal] > R[f][thr_key][s]).mean() for s in S[f]["seeds"]]
                fv = [(S[f]["Z"][s][j][ben] > R[f][thr_key][s]).mean() for s in S[f]["seeds"]]
                out[f"{f}|{nm}|{thr_key}"] = {"detection": [float(x) for x in dv], "padded_benign_fpr": [float(x) for x in fv]}
                rd.append(ms(dv)), rf.append(ms(fv, 2))
            det.append(rd), fpr.append(rf)
        L += [f"**Detection of malware after the edit, threshold at {thr_lab} of the clean April benign scores (%)**", "", md(det, ["edit set"] + [m[1] for m in MODELS if m[0] in S]), "",
              f"**Padded-benign FPR after the same edit, threshold at {thr_lab} (%) (clean benign: {thr_lab.split()[0]} by construction)**", "", md(fpr, ["edit set"] + [m[1] for m in MODELS if m[0] in S]), ""]
    # per family under random 50 prepend (1% threshold)
    if "random_50_prepend" in names:
        j = names.index("random_50_prepend")
        rows = []
        for g in sorted(set(fam) - {"clean", "windows_syswow64"}):
            m = fam == g
            rows.append([g, int(m.sum())] + [ms([(S[f]["Z"][s][j][m] > R[f]["t1"][s]).mean() for s in S[f]["seeds"]]) + " (clean " + ms([(S[f]["Z"][s][0][m] > R[f]["t1"][s]).mean() for s in S[f]["seeds"]]) + ")" if f in S else "n/a" for f, _ in MODELS])
        L += ["**Detection per family under random padding k = 50 prepended (1% threshold; in brackets the unedited detection) (%)**", "", md(rows, ["family", "n"] + [m[1] for m in MODELS if m[0] in S]), ""]
    # white-box
    wrows, wb = [], {}
    for f, lab in MODELS:
        fs = sorted(glob.glob(os.path.join(a.scores, f"wb_{f}_seed*.npz")))
        if not fs:
            continue
        runs = [np.load(p) for p in fs]
        wb[f] = runs
        for key, tk in (("t1", "1%"), ("t01", "0.1%")):
            row = [lab, tk, len(runs)]
            for k in (0, 5, 10, 20, 50):
                kk = min(k, runs[0]["best"].shape[0] - 1)
                row.append(ms([(r["best"][kk] > float(r[key])).mean() for r in runs]))
            for k in (5, 10, 20, 50):
                row.append(ms([(r[f"ben_k{k}"] > float(r[key])).mean() for r in runs], 2) if f"ben_k{k}" in runs[0].files else "n/a")
            wrows.append(row)
    if wrows:
        L += ["**White-box greedy attack (500 April malware, 200 candidates per step, prepend, up to 50 steps): share still flagged after k steps (%) and padded-benign FPR after k steps (%)**", "",
              md(wrows, ["model", "threshold", "seeds", "k = 0", "k = 5", "k = 10", "k = 20", "k = 50", "FPR k = 5", "FPR k = 10", "FPR k = 20", "FPR k = 50"]), ""]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(L) + "\n")
    json.dump(out, open(os.path.join(a.out, "results.json"), "w"))
    # figure: detection and padded-benign FPR vs k (1% threshold)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    panels = [("random", "prepend", "random padding, prepend"), ("random", "insert", "random padding, insert"), ("lgbm", "prepend", "surrogate (LightGBM), prepend"), ("lgbm", "insert", "surrogate (LightGBM), insert")]
    fig, ax = plt.subplots(2, 5, figsize=(17, 6.6), dpi=200)
    for pi, (kind, mode, title) in enumerate(panels):
        ks = sorted({int(n.split("_")[1]) for n in names if n.startswith(kind + "_") and n.endswith("_" + mode)})
        for f, lab in MODELS:
            if f not in S or not ks:
                continue
            for row, sel in ((0, mal), (1, ben)):
                v = [[(S[f]["Z"][s][0][sel] > R[f]["t1"][s]).mean()] + [(S[f]["Z"][s][names.index(f"{kind}_{k}_{mode}")][sel] > R[f]["t1"][s]).mean() for k in ks] for s in S[f]["seeds"]]
                v = 100 * np.array(v)
                ax[row, pi].plot([0] + ks, v.mean(0), "-o", ms=3, color=COL[f], label=lab)
                ax[row, pi].fill_between([0] + ks, v.mean(0) - v.std(0, ddof=1), v.mean(0) + v.std(0, ddof=1), color=COL[f], alpha=0.15, lw=0)
        ax[0, pi].set_title(title, fontsize=8.5)
    for f, lab in MODELS:
        if f in wb:
            ks = list(range(wb[f][0]["best"].shape[0]))
            v = 100 * np.array([(r["best"] > float(r["t1"])).mean(1) for r in wb[f]])
            ax[0, 4].plot(ks, v.mean(0), color=COL[f], label=lab)
            ax[0, 4].fill_between(ks, v.mean(0) - v.std(0, ddof=1), v.mean(0) + v.std(0, ddof=1), color=COL[f], alpha=0.15, lw=0)
            kb = [0] + [k for k in (5, 10, 20, 50) if f"ben_k{k}" in wb[f][0].files]
            vb = 100 * np.array([[0.01] + [(r[f"ben_k{k}"] > float(r["t1"])).mean() for k in kb[1:]] for r in wb[f]])
            ax[1, 4].plot(kb, vb.mean(0), "-o", ms=3, color=COL[f])
    ax[0, 4].set_title("white-box greedy, prepend (500 reports)", fontsize=8.5)
    for i in range(2):
        for pi in range(5):
            ax[i, pi].set_xlabel("padded calls k" if pi < 4 else "greedy steps k")
            ax[i, pi].spines[["top", "right"]].set_visible(False)
    ax[0, 0].set_ylabel("malware still detected (%)\n(threshold 1% FPR)")
    ax[1, 0].set_ylabel("padded-benign FPR (%)")
    ax[0, 0].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_detection_vs_k_four_models.png"))
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
