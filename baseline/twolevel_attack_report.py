"""
Tables and figure of the attacks on ATT+bal-2L from SCORES only (scores_<family>.npz, wb_<family>_seed<s>.npz of baseline/twolevel_attack.py; no edited report is read or written).   (OURS)

    python -m baseline.twolevel_attack_report --src results/attbal_2l/attack_scores --out results/attbal_2l/attacks [--boot 1000]

Reuses baseline/review_attacks.py (tables and comparisons: malware TPR and padded-benign FPR at the 1% and 0.1% thresholds of each model and seed, stratified and cluster bootstrap, claim rule applied
descriptively) with the four models a2l (ATT+bal-2L), b2l (B, no padding), attbal, v2_pe.
White-box: share of the 500 malware reports still flagged after k prepended calls; padded-benign FPR (the chosen list of malware report i prepended to benign report ben[i]); paired differences by seed.
"""
import argparse
import json
import os

import numpy as np

from baseline import attack_stats as A, review_attacks as RA
from baseline import twolevel_attack as TA
from baseline.twolevel_eval import april_meta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAMS = ["v2_pe", "attbal", "b2l", "a2l", "a2r2"]          # a2r2 = A2 of round 2 (NOTES 20); a family without score files is skipped
LABEL = {"a2r2": "ATT+bal-2L, round 2 (A2)", "a2l": "ATT+bal-2L (A)", "b2l": "B (2L, no padding)", "attbal": "ATT+bal", "v2_pe": "v2-PE"}
PAIRS = [("a2l", "attbal"), ("a2l", "v2_pe"), ("a2l", "b2l"), ("b2l", "attbal"), ("a2r2", "attbal"), ("a2r2", "v2_pe"), ("a2r2", "a2l"), ("a2r2", "b2l")]
WB_KS = (1, 2, 5, 10, 20, 30, 40, 50)


def load_scores(src):
    Z, names, tot = {}, None, None
    for f in FAMS:
        p = os.path.join(src, f"scores_{f}.npz")
        if os.path.exists(p):
            d = np.load(p)
            Z[f] = np.stack([d[k] for k in sorted([k for k in d.files if k.startswith("seed")], key=lambda s: int(s[4:]))]).astype(np.float64)
            names, tot = [str(x) for x in d["names"]], d["tot"]
    return Z, names, tot


def subset(Z, names, tot, keep):
    idx = [names.index(n) for n in keep]
    return {f: z[:, idx] for f, z in Z.items()}, [names[i] for i in idx], tot[idx]


def md(rows, header):
    return RA.md(rows, header)


def whitebox(src):
    wb = {}
    for f in FAMS:
        runs = []
        for s in range(10):
            p = os.path.join(src, f"wb_{f}_seed{s}.npz")
            if os.path.exists(p):
                d = np.load(p)
                runs.append({"seed": s, **{k: d[k] for k in d.files}})
        if runs:
            wb[f] = runs
    return wb


def wb_tables(wb, groups):
    rows, rows_b, out = [], [], {}
    for f in [x for x in FAMS if x in wb]:
        runs = wb[f]
        for t, key in (("1e-2", "t1"), ("1e-3", "t01")):
            c = np.stack([(r["best"] > float(r[key])).mean(1) for r in runs])
            out.setdefault(f, {})[t] = c.tolist()
            rows.append([LABEL[f], RA.THR_LABEL[t], len(runs)] + [f"{100 * c[:, k].mean():.1f}" + (f" ({100 * c[:, k].min():.0f}–{100 * c[:, k].max():.0f})" if len(runs) > 1 else "") for k in (0,) + WB_KS])
            fb = {k: np.mean([(r[f"ben_k{k}"] > float(r[key])).mean() for r in runs]) for k in TA.WB_BEN_K if f"ben_k{k}" in runs[0]}
            rows_b.append([LABEL[f], RA.THR_LABEL[t]] + [f"{100 * fb[k]:.1f}" for k in TA.WB_BEN_K if k in fb])
            out[f].setdefault("padded_benign", {})[t] = {str(k): v for k, v in fb.items()}
    t1 = "**White-box greedy attack: share of the 500 malware reports still flagged after k prepended calls (mean over seeds 0-2; range in brackets).**\n\n" + md(rows, ["model", "threshold", "seeds"] + [f"k={k}" for k in (0,) + WB_KS])
    t2 = ("**White-box: padded-benign FPR. The call list that the attack chose for malware report i after k steps (the final list if it stopped earlier) is prepended to one random benign April report (numpy seed 32, the same 500 "
          "benign reports for every model); share of those 500 flagged (mean over seeds).**\n\n" + md(rows_b, ["model", "threshold"] + [f"k={k}" for k in TA.WB_BEN_K]))
    # paired differences by seed
    rows_c, cmp_ = [], {}
    rng = np.random.default_rng(0)
    for a_, b_ in PAIRS:
        if a_ not in wb or b_ not in wb:
            continue
        ra, rb = {r["seed"]: r for r in wb[a_]}, {r["seed"]: r for r in wb[b_]}
        seeds = sorted(set(ra) & set(rb))
        sel = ra[seeds[0]]["sel"]
        n = len(sel)
        W = np.stack([np.bincount(rng.integers(0, n, n), minlength=n) for _ in range(1000)]).astype(np.float64) / n
        u, inv = np.unique(groups[sel], return_inverse=True)
        Wc = np.stack([np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u))[inv] for _ in range(1000)]).astype(np.float64)
        Wc = Wc / Wc.sum(1, keepdims=True)
        for t, key in (("1e-2", "t1"), ("1e-3", "t01")):
            for k in (5, 10, 20, 50):
                fa = np.stack([ra[s]["best"][k] > float(ra[s][key]) for s in seeds]).astype(float)
                fb = np.stack([rb[s]["best"][k] > float(rb[s][key]) for s in seeds]).astype(float)
                d = (fa - fb).mean(1)
                lo, hi = np.percentile(((fa - fb) @ W.T).mean(0), [2.5, 97.5])
                clo, chi = np.percentile(((fa - fb) @ Wc.T).mean(0), [2.5, 97.5])
                cmp_[f"{a_}-{b_}|{t}|k{k}"] = {"per_seed": d.tolist(), "mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "cluster_lo": float(clo), "cluster_hi": float(chi), "seeds_above_0": int((d > 0).sum()), "n_seeds": len(seeds)}
                rows_c.append([f"{LABEL[a_]} − {LABEL[b_]}", RA.THR_LABEL[t], k, f"{100 * d.mean():+.1f}", f"[{100 * lo:+.1f}, {100 * hi:+.1f}]", f"[{100 * clo:+.1f}, {100 * chi:+.1f}]", f"{int((d > 0).sum())}/{len(seeds)}"])
    t3 = ("**White-box comparisons (points; share of the same 500 malware reports still flagged after k steps; seeds paired; CI = bootstrap over the 500 reports, and over their hash_apis groups).** A positive "
          "difference means that the first model is flagged MORE often (is harder to evade).\n\n" + md(rows_c, ["comparison", "threshold", "k", "mean difference", "95% CI (stratified)", "95% CI (cluster)", "seeds > 0"]))
    return [t1, t2, t3], out, cmp_


def figure(path, Zr, names_r, Zs, names_s, wb, y, boot):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"v2_pe": "#eb6834", "attbal": "#eda100", "b2l": "#6250d6", "a2l": "#1baf7a", "a2r2": "#0b6b4a"}
    mk = {"v2_pe": "s", "attbal": "D", "b2l": "v", "a2l": "o", "a2r2": "^"}
    ls = {"v2_pe": "--", "attbal": ":", "b2l": "-.", "a2l": "-", "a2r2": "-"}
    ink, mute, bg = "#0b0b0b", "#52514e", "#fcfcfb"
    plt.rcParams.update({"font.size": 9.5, "axes.edgecolor": mute, "axes.labelcolor": ink, "text.color": ink, "xtick.color": mute, "ytick.color": mute, "figure.facecolor": bg, "axes.facecolor": bg})
    panels = [("Random calls, prepended", "random", "prepend", TA.RANDOM_KS), ("Random calls, inserted", "random", "insert", TA.RANDOM_KS), ("LightGBM-chosen calls, prepended", "lgbm", "prepend", TA.SURR_KS),
              ("v2-PE-chosen calls, prepended", "v2pe", "prepend", TA.SURR_KS), ("White-box greedy (500 malware)", "wb", None, None)]
    fig, axes = plt.subplots(2, 5, figsize=(20, 7.4), dpi=200, sharey="row")
    for c, (title, kind, mode, ks) in enumerate(panels):
        for r in (0, 1):
            ax = axes[r, c]
            if r == 0:
                ax.set_title(title, fontsize=10.5, loc="left")
            ax.grid(axis="y", color="#d8d7d2", lw=0.6)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for f in FAMS:
                if kind == "wb":
                    if f not in wb:
                        continue
                    if r == 0:
                        yv = 100 * np.stack([(q["best"] > float(q["t1"])).mean(1) for q in wb[f]]).mean(0)
                        x = np.arange(len(yv))
                    else:
                        ks_ = [k for k in TA.WB_BEN_K if f"ben_k{k}" in wb[f][0]]
                        x = [0] + ks_
                        yv = [1.0] + [100 * np.mean([(q[f"ben_k{k}"] > float(q["t1"])).mean() for q in wb[f]]) for k in ks_]
                else:
                    Z = {"random": Zr, "lgbm": Zs, "v2pe": Zs}[kind].get(f)
                    names = names_r if kind == "random" else names_s
                    if Z is None:
                        continue
                    F = A.flags_of(Z, y, "1e-2")
                    x, yv = [0], [100 * boot.rate(F[:, 0], "mal" if r == 0 else "ben")[0].mean()]
                    for k in ks:
                        nm = f"{kind}_{k}_{mode}"
                        x.append(k)
                        yv.append(100 * boot.rate(F[:, names.index(nm)], "mal" if r == 0 else "ben")[0].mean())
                ax.plot(x, yv, color=col[f], ls=ls[f], marker=mk[f], ms=4.5, lw=1.7, mfc=bg, mew=1.4, label=LABEL[f])
            ax.set_xlabel("calls added (k)")
            if r == 0:
                ax.set_ylim(0, 102)
            else:
                ax.set_ylim(0, None)
    axes[0, 0].set_ylabel("malware flagged at 1% FPR (%)")
    axes[1, 0].set_ylabel("padded benign flagged (%)")
    axes[0, 4].legend(loc="upper right", fontsize=8.5, frameon=False)
    top = max(float(np.nanmax(l.get_ydata())) for ax in axes[1] for l in ax.get_lines() if len(l.get_ydata()))
    axes[1, 0].set_ylim(0, top * 1.08)          # shared row: show the largest padded-benign FPR (white-box lists) in every panel
    fig.suptitle("Detection of April malware when calls are added (thresholds fixed at 1% FPR of each model's unedited April benign scores; mean over 10 seeds, white-box over seeds 0-2)", fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "attbal_2l", "attack_scores"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "attbal_2l", "attacks"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    _, _, groups = april_meta()
    boot, cboot = A.Boot(y, a.boot), A.Boot(y, a.boot, groups)
    RA.LABEL.update(LABEL)
    RA.ORDER = FAMS
    Z, names, tot = load_scores(a.src)
    L, agg = [], {}
    if Z:
        rnames = ["unedited"] + [n for n in names if n.startswith("random_")]
        Zr, nr, tr = subset(Z, names, tot, rnames)
        snames = ["unedited"] + [n for n in names if not n.startswith("random_") and n != "unedited"]
        Zs, ns, ts = subset(Z, names, tot, snames)
        for title, ZZ, nn, tt, key in (("Random padding with calls of the EVAL pool, all April reports", Zr, nr, tr, "random"), ("Surrogate-chosen padding (ranks 1..k of the LightGBM or v2-PE ranking)", Zs, ns, ts, "surrogate")):
            RA.store_of = lambda f: "ours"
            t, o, F = RA.table_set(title, ZZ, {"ours": tt}, y, boot, nn, "Thresholds: 1% and 0.1% FPR of each model's and seed's unedited April benign scores. Seeds 0-9, mean ± std.")
            c, oc = RA.comparisons(title, F, {"ours": tt}, y, boot, nn, PAIRS, cboot)
            L += [t, "", c, ""]
            agg[key], agg[key + "_cmp"] = o, oc
    else:
        Zr = Zs = {}
        nr = ns = []
    wb = whitebox(a.src)
    if wb:
        texts, o, cmp_ = wb_tables(wb, groups)
        L += [t + "\n" for t in texts]
        agg["whitebox"], agg["whitebox_cmp"] = o, cmp_
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "attack_tables.md"), "w").write("\n".join(L) + "\n")
    json.dump(agg, open(os.path.join(a.out, "attack_aggregates.json"), "w"), indent=1)
    if Z:
        figure(os.path.join(a.out, "fig_detection_vs_k.png"), Zr, nr, Zs, ns, wb, y, boot)
    print("\n".join(L))


if __name__ == "__main__":
    main()
