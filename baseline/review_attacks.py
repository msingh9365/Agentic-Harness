"""
Tables 2 and 3 and the figure of RESULTS_FOR_REVIEW.md from the SCORES written by baseline/review_gpu.py (edited reports were never written; nothing here reads or writes one).   (OURS)

    python -m baseline.review_attacks --src results/review/attack --out results/review [--boot 1000]

Reads a3_<family>.npz (surrogate-chosen padding, 12 edit sets + unedited), a3pad_<family>.npz (random padding of REPORT 5.10, 6 edit sets + unedited, all April reports), a3_meta_*.npz /
a3pad_meta_*.npz (token totals of the edited reports), a3b_<family>_seed<k>.npz (white-box greedy), probe_<family>.npz (shortcut probe). Statistics: baseline/attack_stats.py.
Writes attack_tables.md, attack_aggregates.json (numbers only) and fig_detection_vs_k.png.
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import attack_run as AR, attack_stats as A

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABEL = {"released": "released checkpoint", "v2_pe": "v2-PE", "pebal": "PE+bal", "attbal": "ATT+bal", "attkeep": "ATT+bal-keep", "pekeep": "PE+bal-keep", "attaug": "ATT+aug", "peaug": "PE+aug"}
ORDER = ["released", "v2_pe", "pebal", "attbal", "attkeep", "pekeep"]
PAIRS = [("attbal", "pebal"), ("attkeep", "pekeep")]
THR = ("1e-2", "1e-3")
THR_LABEL = {"1e-2": "1% FPR", "1e-3": "0.1% FPR"}
KS = AR.KS
FIG_FAMS = ("released", "v2_pe", "pebal", "attbal")


def md(rows, header):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def pm(v):
    return f"{100 * v[0]:.1f} ± {100 * v[1]:.1f}" if v[1] else f"{100 * v[0]:.1f}"


def load(src, prefix, fams):
    """fam -> Z [S, nsets, N]; totals per store ('ours' / 'released') [nsets, N]."""
    Z, tot = {}, {}
    for f in fams:
        p = os.path.join(src, f"{prefix}_{f}.npz")
        if os.path.exists(p):
            d = np.load(p)
            Z[f] = np.stack([d[k] for k in sorted(d.files, key=lambda s: int(s[4:]))]).astype(np.float64)
    for st in ("ours", "released"):
        p = os.path.join(src, f"{prefix}_meta_{st}.npz")
        if os.path.exists(p):
            tot[st] = np.load(p)["totals"]
    return Z, tot


def store_of(f):
    return "released" if f == "released" else "ours"


def table_set(name, Z, tot, y, boot, names, header_note):
    """Per model and edit set: malware TPR and padded-benign FPR at 1% and 0.1% (mean ± std over seeds), and the same on the 'fits in 512 tokens' subset."""
    out, rows = {}, []
    F = {t: {f: A.flags_of(Z[f], y, t) for f in Z} for t in THR}
    for f in [x for x in ORDER + ["attaug", "peaug"] if x in Z]:
        for j in range(1, Z[f].shape[1]):
            fit = tot[store_of(f)][j] <= 512
            r = [LABEL[f], names[j].replace("_", " ")]
            rec = {}
            for t in THR:
                pm_, _ = boot.rate(F[t][f][:, j], "mal")
                pb_, _ = boot.rate(F[t][f][:, j], "ben")
                rec[t] = {"tpr": [float(pm_.mean()), float(pm_.std(ddof=1)) if len(pm_) > 1 else 0.0], "fpr": [float(pb_.mean()), float(pb_.std(ddof=1)) if len(pb_) > 1 else 0.0]}
                pf, _ = boot.rate(F[t][f][:, j], "mal", fit) if fit[boot.pos].any() else (np.array([np.nan]), None)
                rec[t]["tpr_fit"] = float(np.nanmean(pf)) if not np.all(np.isnan(pf)) else None
                r += [pm(rec[t]["tpr"]), pm(rec[t]["fpr"])]
            rec["share_fit_mal"] = float(fit[boot.pos].mean())
            rec["share_fit_ben"] = float(fit[boot.neg].mean())
            r += [f"{100 * rec['share_fit_mal']:.1f}%", "n/a" if rec["1e-2"]["tpr_fit"] is None else f"{100 * rec['1e-2']['tpr_fit']:.1f}", "n/a" if rec["1e-3"]["tpr_fit"] is None else f"{100 * rec['1e-3']['tpr_fit']:.1f}"]
            rows.append(r)
            out[f"{f}|{names[j]}"] = rec
    text = f"**{name}** {header_note}\n\n" + md(rows, ["model", "edit", "malware TPR @1%", "padded-benign FPR @1%", "malware TPR @0.1%", "padded-benign FPR @0.1%", "malware that fit in 512", "TPR @1%, fit subset", "TPR @0.1%, fit subset"])
    return text, out, F


def comparisons(name, F, tot, y, boot, names, fams_pairs, cboot=None):
    """A - B per edit set, threshold and rate. Columns: mean of the per-seed differences, their std over the seeds, the 95% CI of the stratified bootstrap (the protocol), seeds above / below 0, the claim
    rule, and the same CI from the cluster bootstrap over duplicate groups (sensitivity; a result that is resolved under both is the safe one)."""
    rows, out = [], {}
    for a_, b_ in fams_pairs:
        if a_ not in F["1e-2"] or b_ not in F["1e-2"]:
            continue
        for j in range(1, F["1e-2"][a_].shape[1]):
            fit = tot[store_of(a_)][j] <= 512
            for t in THR:
                cases = [("mal", "malware TPR", None), ("ben", "padded-benign FPR", None)] + ([("mal", "malware TPR, fit subset", fit)] if fit[boot.pos].sum() > 50 else [])
                for cls, key, mask in cases:
                    d = A.compare(boot, F[t][a_][:, j], F[t][b_][:, j], cls, mask)
                    dc = A.compare(cboot, F[t][a_][:, j], F[t][b_][:, j], cls, mask) if cboot is not None else None
                    sd = float(np.std(d["per_seed"], ddof=1))
                    d["sd_over_seeds"] = sd
                    if dc is not None:
                        d["cluster"] = {"lo": dc["lo"], "hi": dc["hi"], "resolved": dc["resolved"]}
                    rows.append([f"{LABEL[a_]} − {LABEL[b_]}", names[j].replace("_", " "), THR_LABEL[t], key, f"{100 * d['mean']:+.2f}", f"{100 * sd:.2f}", f"[{100 * d['lo']:+.2f}, {100 * d['hi']:+.2f}]",
                                 f"{d['seeds_above_0']}/{d['seeds_below_0']}", "**yes**" if d["resolved"] else "no"] + ([f"[{100 * dc['lo']:+.2f}, {100 * dc['hi']:+.2f}]", "yes" if dc["resolved"] else "no"] if dc else []))
                    out[f"{a_}-{b_}|{names[j]}|{t}|{key}"] = d
    head = ["comparison", "edit", "threshold", "rate", "mean difference", "std over seeds", "CI (stratified bootstrap)", "seeds >0 / <0", "meets rule (descriptive)"] + (["CI (cluster bootstrap)", "meets rule, cluster (descriptive)"] if cboot is not None else [])
    return (f"**{name}: A − B, points (× 100). Mean of the per-seed differences (seed i of A against seed i of B), their standard deviation over the seeds, 95% CI of the stratified bootstrap over the April reports "
            "(1,000 resamples, numpy seed 0; it covers the test-set sampling only, not the seed-to-seed spread), seeds above 0 / below 0; meets rule = CI excludes 0 and ≥ 7 of 10 seeds with the same sign (descriptive: none of these robustness comparisons is a pre-registered claim).**\n\n" + md(rows, head)), out


def whitebox(src):
    res = {}
    for p in sorted(glob.glob(os.path.join(src, "a3b_*_seed*.npz"))):
        f = os.path.basename(p)[4:].rsplit("_seed", 1)
        d = np.load(p)
        res.setdefault(f[0], []).append({"seed": int(f[1][:-4]), "best": d["best"], "t1": float(d["t1"]), "t01": float(d["t01"]), "sel": d["sel"]})
    return res


def whitebox_table(wb):
    ks = [0, 1, 2, 5, 10, 20]
    rows, curves = [], {}
    for f in [x for x in ORDER if x in wb]:
        runs = sorted(wb[f], key=lambda r: r["seed"])
        c1 = np.stack([(r["best"] > r["t1"]).mean(1) for r in runs])         # [seeds, 21]
        c01 = np.stack([(r["best"] > r["t01"]).mean(1) for r in runs])
        curves[f] = {"1e-2": c1.tolist(), "1e-3": c01.tolist(), "seeds": [r["seed"] for r in runs]}
        for t, c in (("1e-2", c1), ("1e-3", c01)):
            rows.append([LABEL[f], THR_LABEL[t], len(runs)] + [(f"{100 * c[:, k].mean():.1f}" + (f" ({100 * c[:, k].min():.1f}–{100 * c[:, k].max():.1f})" if len(runs) > 1 else "")) for k in ks])
    text = "**White-box greedy attack: share of the 500 malware reports still flagged after k prepended calls (mean over seeds; range of seeds in brackets).**\n\n" + md(rows, ["model", "threshold", "seeds"] + [f"k={k}" for k in ks])
    return text, curves


def whitebox_compare(wb, n_boot=A.N_BOOT):
    """ATT+bal - PE+bal and ATT+bal-keep - PE+bal-keep on the white-box attack (seeds 0-2, the same 500 reports for every model): per-seed difference of the share still flagged after k calls, the CI
    from a bootstrap over the 500 reports (the same resamples for both models, numpy seed 0), and the number of seeds with a positive difference (of 3)."""
    rows, out = [], {}
    rng = np.random.default_rng(0)
    for a_, b_ in PAIRS:
        if a_ not in wb or b_ not in wb:
            continue
        ra = {r["seed"]: r for r in wb[a_]}
        rb = {r["seed"]: r for r in wb[b_]}
        seeds = sorted(set(ra) & set(rb))
        n = len(ra[seeds[0]]["best"][0])
        W = np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(n_boot)]).astype(np.float64) / n
        for t, key in (("1e-2", "t1"), ("1e-3", "t01")):
            for k in (5, 10, 20):
                fa = np.stack([ra[s_]["best"][k] > ra[s_][key] for s_ in seeds]).astype(float)       # [seeds, n]
                fb = np.stack([rb[s_]["best"][k] > rb[s_][key] for s_ in seeds]).astype(float)
                d = (fa - fb).mean(1)
                dist = ((fa - fb) @ W.T).mean(0)
                lo, hi = np.percentile(dist, [2.5, 97.5])
                out[f"{a_}-{b_}|{t}|k{k}"] = {"per_seed": d.tolist(), "mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "seeds_above_0": int((d > 0).sum()), "n_seeds": len(seeds)}
                rows.append([f"{LABEL[a_]} − {LABEL[b_]}", THR_LABEL[t], k, f"{100 * d.mean():+.1f}", f"[{100 * lo:+.1f}, {100 * hi:+.1f}]", f"{int((d > 0).sum())}/{len(seeds)}"])
    return "**White-box comparisons (points; seeds 0-2 paired; CI = bootstrap over the 500 reports).**\n\n" + md(rows, ["comparison", "threshold", "k", "mean difference", "95% CI", "seeds > 0"]), out


def probe_table(src):
    rows, out = [], {}
    for f in ["v2_pe", "pebal", "attbal", "peaug", "attaug"]:
        p = os.path.join(src, f"probe_{f}.npz")
        if not os.path.exists(p):
            continue
        d = np.load(p)
        a1, a2, a3 = d["auc_pooled"].mean(1), d["auc_hidden"].mean(1), d["auc_shuffled"].mean(1)
        out[f] = {"pooled": [float(a1.mean()), float(a1.std(ddof=1))], "hidden": [float(a2.mean()), float(a2.std(ddof=1))], "shuffled": [float(a3.mean()), float(a3.std(ddof=1))], "n_seeds": int(len(a1))}
        rows.append([LABEL[f], len(a1), f"{a1.mean():.4f} ± {a1.std(ddof=1):.4f}", f"{a2.mean():.4f} ± {a2.std(ddof=1):.4f}", f"{a3.mean():.3f}"])
    return "**Table 3b. Shortcut probe: AUC of a logistic regression predicting \"padding present\" on April reports (padded with probability 0.5), mean ± std over the seeds.**\n\n" + md(rows, ["model", "n seeds", "AUC, pooled vector", "AUC, 64-d hidden vector", "shuffled-label control"]), out


def figure(path, Zr, Za, wb, y, boot, fams, tot_r, tot_a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"released": "#2a78d6", "v2_pe": "#eb6834", "pebal": "#1baf7a", "attbal": "#eda100", "tuned": "#6250d6"}
    mk = {"released": "o", "v2_pe": "s", "pebal": "^", "attbal": "D", "tuned": "v"}
    ls = {"released": "-", "v2_pe": "--", "pebal": "-.", "attbal": ":", "tuned": (0, (5, 1))}
    ink, mute, bg = "#0b0b0b", "#52514e", "#fcfcfb"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": mute, "axes.labelcolor": ink, "text.color": ink, "xtick.color": mute, "ytick.color": mute, "figure.facecolor": bg, "axes.facecolor": bg})
    panels = [("Random benign calls (REPORT 5.10)", "random"), ("Calls chosen with a LightGBM surrogate", "lgbm"), ("Calls chosen with a v2-PE (seed 0) surrogate", "v2pe"), ("White-box greedy (500 malware, seeds 0-2)", "wb")]
    fig, axes = plt.subplots(1, 4, figsize=(17, 4.3), dpi=200, sharey=True)
    for ax, (title, kind) in zip(axes, panels):
        ax.set_title(title, fontsize=10.5, loc="left")
        ax.grid(axis="y", color="#d8d7d2", lw=0.6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ends = []
        for f in [x for x in FIG_FAMS if x in fams]:
            if kind == "wb":
                if f not in wb:
                    continue
                runs = sorted(wb[f], key=lambda r: r["seed"])
                c = np.stack([(r["best"] > r["t1"]).mean(1) for r in runs]).mean(0)
                x, yv = np.arange(len(c)), 100 * c
            else:
                Z = (Zr if kind == "random" else Za).get(f)
                if Z is None:
                    continue
                F = A.flags_of(Z, y, "1e-2")
                names = [AR.pad_set_name(j) for j in range(Z.shape[1])] if kind == "random" else [AR.set_name(j) for j in range(Z.shape[1])]
                x, yv = [0], [100 * boot.rate(F[:, 0], "mal")[0].mean()]
                for k in KS:
                    nm = f"random_{k}_prepend" if kind == "random" else f"{kind}_{k}_prepend"
                    x.append(k)
                    yv.append(100 * boot.rate(F[:, names.index(nm)], "mal")[0].mean())
            ax.plot(x, yv, color=col[f], ls=ls[f], marker=mk[f], ms=5, lw=1.8, mfc=bg, mew=1.6, label=LABEL[f])
            ends.append((f, x[-1], yv[-1]))
        placed = []                                                       # direct labels at the line ends, pushed apart so that they do not overlap (at least 6 points of the y axis)
        for f, xe, ye in sorted(ends, key=lambda t: t[2]):
            ypos = ye if not placed else max(ye, placed[-1] + 6.0)
            placed.append(ypos)
            ax.annotate(LABEL[f], (xe, ye), xytext=(xe + 0.03 * (21 if kind == "wb" else 50) + 1, ypos), textcoords="data", fontsize=8.5, color=ink, va="center")
        ax.set_xlabel("calls prepended (k)")
        ax.set_xlim(-1, (21 if kind == "wb" else 50) * 1.45)
        ax.set_ylim(0, 102)
    axes[0].set_ylabel("malware flagged at 1% FPR (%)")
    axes[3].legend(loc="upper right", fontsize=8.5, frameon=False)
    fig.text(0.01, 0.005, "Released checkpoint, v2-PE surrogate, k = 50 (middle right panel): the model flags every report, malware and benign alike (padded-benign FPR 100%), so 100% there is not detection. "
             "Thresholds are fixed at 1% FPR of each model's unedited April benign scores.", fontsize=8, color=mute, ha="left", va="bottom")
    fig.suptitle("Detection of April malware when benign calls are prepended (thresholds fixed on the unedited April benign scores of each model)", fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(path)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "review", "attack"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "review"))
    ap.add_argument("--boot", type=int, default=A.N_BOOT)
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    boot = A.Boot(y, a.boot)
    gp = os.path.join(a.out, "april_hash_apis_group.npy")
    cboot = A.Boot(y, a.boot, np.load(gp)) if os.path.exists(gp) else None
    fams = ORDER + ["attaug", "peaug"]
    Zs, tot_s = load(a.src, "a3", fams)
    Zr, tot_r = load(a.src, "a3pad", fams)
    names_s = [AR.set_name(j) for j in range(13)]
    names_r = [AR.pad_set_name(j) for j in range(7)]
    L, agg = [], {}
    if Zr:
        t, o, Fr = table_set("Table 2a. Random padding (the procedure of REPORT 5.10, calls from the EVAL pool), all April reports.", Zr, tot_r, y, boot, names_r, "Thresholds: 1% and 0.1% FPR of each model's unedited April benign scores.")
        c, oc = comparisons("Table 2a comparisons", Fr, tot_r, y, boot, names_r, PAIRS, cboot)
        L += [t, "", c, ""]; agg["random"], agg["random_cmp"] = o, oc
    if Zs:
        t, o, Fs = table_set("Table 2b. Surrogate-chosen padding: calls of rank 1..k from the LightGBM or the v2-PE surrogate (insert and prepend).", {f: Zs[f] for f in Zs}, tot_s, y, boot, names_s, "")
        c, oc = comparisons("Table 2b comparisons", Fs, tot_s, y, boot, names_s, PAIRS, cboot)
        L += [t, "", c, ""]; agg["surrogate"], agg["surrogate_cmp"] = o, oc
    wb = whitebox(a.src)
    if wb:
        t, curves = whitebox_table(wb)
        L += [t, ""]; agg["whitebox"] = curves
        tw, ow = whitebox_compare(wb)
        L += [tw, ""]; agg["whitebox_cmp"] = ow
    t, o = probe_table(a.src)
    if o:
        L += [t, ""]; agg["probe"] = o
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "attack_tables.md"), "w").write("\n".join(L) + "\n")
    json.dump(agg, open(os.path.join(a.out, "attack_aggregates.json"), "w"), indent=1)
    if Zr and Zs:
        figure(os.path.join(a.out, "fig_detection_vs_k.png"), Zr, Zs, wb, y, boot, [f for f in ORDER if f in Zs], tot_r, tot_s)
    print("\n".join(L))


if __name__ == "__main__":
    main()
