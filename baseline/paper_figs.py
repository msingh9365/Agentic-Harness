"""
All paper figures and tables from STORED logits, scores and results (no model, no GPU, no new April evaluation, no model choice).   (OURS; CPU only)

    python -m baseline.paper_figs --models results/paper/specs/A.json            # SET A: reproduction (paper's tokenizer)
    python -m baseline.paper_figs --models results/paper/specs/B.json            # SET B: corrected tokenizer (+ comparison A vs B)
    python -m baseline.paper_figs --models results/paper/specs/B.json --only F7,F8,T5     # regenerate a few items (e.g. after the M1 white-box results arrive: change `attack_results` in the spec)
    python -m baseline.paper_figs --models <spec> --prepare                       # (re)build the small caches in <data_dir> from the raw sources named in spec["raw"] (needs the stores / run folders / weights)
    python -m baseline.paper_figs --readme                                         # results/paper/README.md from the manifests of all sets

The spec is a JSON file: model set name, the four models with their stored logits, the attack results (`results.json` of baseline/gs_attack_report.py; M1 white-box missing = "pending"), the evaluation results (`results.json` of
gs_eval_g.py / gs_eval_i.py), the seen / unseen file (`gs_seen_unseen.py`), the cache folder and the raw sources for --prepare. Every item writes <set>/figs/<id>.pdf + .png (300 dpi) + _caption.txt or <set>/tables/<id>.md + .tex.
Anything that cannot be made is skipped with the reason in the manifest (and in the README); the others are still made. Error bars and bands = std over the 10 seeds unless stated.
"""
import argparse
import glob
import json
import math
import os
import re
import sys
import traceback

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SC, DC = 3.5, 7.16                                                  # single / double column width (inches, IEEE)
MODELS = ["M1", "M2", "M3", "M4"]
# Okabe-Ito colour-blind-safe palette, ONE fixed colour per model in every figure
COL = {"M1": "#0072B2", "M2": "#E69F00", "M3": "#009E73", "M4": "#D55E00"}
NAME = {"M1": "M1 Nebula", "M2": "M2 two-level", "M3": "M3 ATT+bal", "M4": "M4 ATT+bal-2L"}
LONG = {"M1": "M1 (Nebula, flatten pooling, no padding)", "M2": "M2 (two-level, attention pooling, no padding)", "M3": "M3 (ATT+bal, attention pooling, balanced padding)", "M4": "M4 (two-level, attention pooling, balanced padding)"}
SEEDS = list(range(10))
PAPER = {"tpr@1e-3": 0.5213, "f1": 0.9136}                          # Nebula paper, Table 7 (the only numbers we use from it; NOTES.md section 1)
ATTACK_COLS = [("unedited", "unedited"), ("random_20_prepend", "random 20\nprepend"), ("random_50_prepend", "random 50\nprepend"), ("random_100_prepend", "random 100\nprepend"),
               ("random_200_insert", "random 200\ninsert"), ("lgbm_50_prepend", "LightGBM 50\nprepend"), ("wb20", "white-box\n20 steps"), ("wb50", "white-box\n50 steps")]


def p(*a):
    return os.path.join(ROOT, *a)


def rel(path):
    return path if not os.path.isabs(path) else os.path.relpath(path, ROOT) if path.startswith(ROOT) else path


def style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "Nimbus Roman", "STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix", "font.size": 8,
                         "axes.labelsize": 8, "axes.titlesize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "legend.frameon": False, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "lines.linewidth": 1.0, "lines.markersize": 3, "pdf.fonttype": 42, "ps.fonttype": 42,
                         "savefig.dpi": 300, "figure.dpi": 100, "figure.constrained_layout.use": True})
    return plt


class Ctx:
    def __init__(self, spec_path):
        self.spec_path = spec_path
        self.spec = json.load(open(spec_path))
        self.set = self.spec["set"]
        self.out = p("results", "paper", self.set)
        self.figs, self.tabs = os.path.join(self.out, "figs"), os.path.join(self.out, "tables")
        self.data = p(self.spec["data_dir"])
        for d in (self.figs, self.tabs, self.data):
            os.makedirs(d, exist_ok=True)
        self.manifest = []
        self._cache = {}

    # ----- stored inputs
    def y(self):
        return np.load(p("results", "logits", "labels.npz"))["y_test"].astype(int)

    def meta(self):
        if "meta" not in self._cache:
            from baseline.twolevel_eval import april_meta
            self._cache["meta"] = april_meta()
        return self._cache["meta"]

    def Z(self):
        if "Z" not in self._cache:
            z = {}
            for m in MODELS:
                d = self.spec["models"][m]["logits"]
                z[m] = np.load(p(d["file"]))[d["key"]].astype(np.float64).reshape(10, -1)
            self._cache["Z"] = z
        return self._cache["Z"]

    def json(self, key):
        if key not in self._cache:
            self._cache[key] = json.load(open(p(self.spec[key])))
        return self._cache[key]

    def note(self, kind, id_, title, files, sources, status="made", reason=""):
        self.manifest.append({"kind": kind, "id": id_, "title": title, "set": self.set, "files": [rel(f) for f in files], "sources": sources, "status": status, "reason": reason})

    # ----- writers
    def save_fig(self, fig, id_, title, caption, sources):
        base = os.path.join(self.figs, id_)
        fig.savefig(base + ".pdf")
        fig.savefig(base + ".png", dpi=300)
        open(base + "_caption.txt", "w").write(caption.strip() + "\n")
        import matplotlib.pyplot as plt
        plt.close(fig)
        self.note("figure", id_, title, [base + ".pdf", base + ".png", base + "_caption.txt"], sources)

    def save_table(self, id_, title, header, rows, caption, sources, align=None):
        md = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
        base = os.path.join(self.tabs, id_)
        open(base + ".md", "w").write(f"**{caption}**\n\n" + "\n".join(md) + "\n")
        open(base + ".tex", "w").write(latex(header, rows, caption, id_, align))
        self.note("table", id_, title, [base + ".md", base + ".tex"], sources)


def tex_esc(s):
    s = str(s)
    bold = s.startswith("**") and s.endswith("**") and len(s) > 4
    s = s.strip("*") if bold else s
    s = s.replace("\\", "").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#").replace("±", r"$\pm$").replace("−", "-").replace("≥", r"$\geq$").replace("\n", " ")
    s = s.replace("<", r"$<$").replace(">", r"$>$")
    return r"\textbf{" + s + "}" if bold else s


def latex(header, rows, caption, label, align=None):
    align = align or "l" + "r" * (len(header) - 1)
    L = [r"\begin{table}[t]", r"\centering", r"\small", r"\caption{" + tex_esc(caption) + "}", r"\label{tab:" + label + "}", r"\begin{tabular}{" + align + "}", r"\toprule",
         " & ".join(tex_esc(h) for h in header) + r" \\", r"\midrule"]
    L += [" & ".join(tex_esc(c) for c in r) + r" \\" for r in rows]
    L += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    return "\n".join(L)


def ms(v, d=1, scale=100.0):
    v = np.asarray(v, dtype=float) * scale
    return f"{v.mean():.{d}f} ± {v.std(ddof=1) if len(v) > 1 else 0:.{d}f}"


def thr(z, y, fpr):
    neg = np.sort(z[y == 0])[::-1]
    k = int(np.floor(fpr * len(neg)))
    return neg[k] if k < len(neg) else -np.inf


# --------------------------------------------------------------------------------------------- figures
def f2(C):
    plt = style()
    from baseline import groupsplit as G
    jt = G.january_table()
    fa, _, _ = C.meta()
    fj = jt["train"]["family"]
    order = [f for f, _ in sorted(((f, (fj == f).sum()) for f in set(fj)), key=lambda t: -t[1])]
    nj, na = [int((fj == f).sum()) for f in order], [int((fa == f).sum()) for f in order]
    fig, ax = plt.subplots(figsize=(DC, 2.3))
    x = np.arange(len(order))
    ax.bar(x - 0.2, nj, 0.4, color="#999999", label="January (training)")
    ax.bar(x + 0.2, na, 0.4, color="#333333", label="April (test)")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([o.replace("windows_", "") for o in order], rotation=20, ha="right")
    ax.set_ylabel("reports (log scale)")
    ax.legend()
    cap = "Number of emulation reports per family in the January 2022 training set (75,298 reports) and the April 2022 test set (17,402 reports) of the Speakeasy data; `clean` and `windows_syswow64` are benign. Log-scale y-axis."
    C.save_fig(fig, "F2_samples_per_family", "Samples per family, January vs April", cap, ["results/hier/data/meta.csv", "results/misses/reports.csv", "results/padding/row_map.npz"])


def f3(C):
    plt = style()
    d = np.load(os.path.join(C.data, "lengths.npz"))
    fig, ax = plt.subplots(figsize=(SC, 2.6))
    for pop, lab, ls in (("train", "January", "-"), ("test", "April", "--")):
        L, y = d[f"len_{pop}"], d[f"y_{pop}"]
        for cls, nm, col in ((1, "malware", "#CC3311"), (0, "benign", "#555555")):
            v = np.sort(L[y == cls])
            ax.plot(v, np.arange(1, len(v) + 1) / len(v), ls=ls, color=col, label=f"{nm}, {lab}")
    for xv in (512, 4096):
        ax.axvline(xv, color="k", lw=0.5, ls=":")
        ax.text(xv * 1.05, 0.04, f"{xv:,}", fontsize=6.5)
    ax.set_xscale("log")
    ax.set_xlabel("report length (tokens, whole report)")
    ax.set_ylabel("cumulative share of reports")
    ax.set_xlim(8, 2e5)
    ax.legend(loc="upper left")
    cap = f"Cumulative distribution of the report length in tokens ({C.spec['tokenizer']}), malware and benign, January (solid) and April (dashed). Dotted lines: the 512-token window of the one-chunk models and the 4,096-token window (8 chunks) of the two-level models."
    C.save_fig(fig, "F3_report_length_cdf", "Report length CDF", cap, [rel(os.path.join(C.data, "lengths.npz"))])


def f4(C):
    plt = style()
    L = json.load(open(os.path.join(C.data, "loss.json")))
    fig, ax = plt.subplots(2, 2, figsize=(DC, 3.6), sharey=True)
    for a, m in zip(ax.flat, MODELS):
        tr, va = np.array(L[m]["train"]), np.array(L[m]["val"])
        ep = np.arange(1, tr.shape[1] + 1)
        for arr, ls, lab in ((tr, "-", "training"), (va, "--", "validation slice (in-sample)")):
            mu, sd = arr.mean(0), arr.std(0, ddof=1) if len(arr) > 1 else np.zeros(arr.shape[1])
            a.errorbar(ep, mu, yerr=sd, color=COL[m], ls=ls, marker="o", capsize=2, label=lab)
        a.set_title(NAME[m])
        a.set_xticks(ep)
    for a in ax[1]:
        a.set_xlabel("epoch")
    for a in ax[:, 0]:
        a.set_ylabel("binary cross-entropy")
    ax[0, 0].legend()
    cap = "Training loss (mean over the epoch, solid) and loss on the 8,718-report validation slice (dashed) of the final models M1 to M4 after each epoch, mean ± std over 10 seeds, one shared y-axis. The final models are trained on ALL of January, so the validation slice is part of their training data and its loss is in-sample; the one-epoch models show a single point."
    C.save_fig(fig, "F4_loss_curves", "Training and validation loss M1-M4", cap, [rel(os.path.join(C.data, "loss.json"))])


def f5(C):
    plt = style()
    from sklearn.metrics import roc_curve
    y = C.y()
    grid = np.logspace(-4, 0, 400)
    fig, ax = plt.subplots(figsize=(SC, 3.0))
    for m in MODELS:
        T = []
        for s in SEEDS:
            fpr, tpr, _ = roc_curve(y, C.Z()[m][s])
            T.append(np.interp(grid, fpr, tpr))
        T = np.array(T)
        ax.plot(grid, T.mean(0), color=COL[m], label=NAME[m])
        ax.fill_between(grid, T.mean(0) - T.std(0, ddof=1), np.minimum(1, T.mean(0) + T.std(0, ddof=1)), color=COL[m], alpha=0.18, lw=0)
    ax.plot([1e-3], [PAPER["tpr@1e-3"]], marker="*", ms=9, color="k", ls="none", label="Nebula paper (TPR 0.5213 at 1e-3)")
    ax.set_xscale("log")
    ax.set_xlim(1e-4, 1)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("false-positive rate (log scale)")
    ax.set_ylabel("true-positive rate")
    ax.legend(loc="lower right")
    cap = "ROC curves of M1 to M4 on the April test set (17,402 reports) on a log false-positive-rate axis, mean over 10 seeds with a ± std band. The star marks the TPR of 0.5213 at an FPR of 1e-3 reported by the Nebula paper."
    C.save_fig(fig, "F5_roc_logfpr", "ROC on log-FPR axis", cap, [C.spec["models"][m]["logits"]["file"] for m in MODELS])


def f6(C):
    plt = style()
    y = C.y()
    fam, _, _ = C.meta()
    fams = [g for g in sorted(set(fam)) if g not in ("clean", "windows_syswow64")]
    M = np.zeros((4, len(fams)))
    for i, m in enumerate(MODELS):
        for s in SEEDS:
            t = thr(C.Z()[m][s], y, 0.01)
            M[i] += np.array([(C.Z()[m][s][fam == g] > t).mean() for g in fams]) / len(SEEDS)
    fig, ax = plt.subplots(figsize=(DC, 2.1))
    im = ax.imshow(100 * M, cmap="viridis", vmin=40, vmax=100, aspect="auto")
    for i in range(4):
        for j in range(len(fams)):
            ax.text(j, i, f"{100 * M[i, j]:.1f}", ha="center", va="center", fontsize=7, color="white" if 100 * M[i, j] < 75 else "black")
    ax.set_xticks(range(len(fams)))
    ax.set_xticklabels(fams)
    ax.set_yticks(range(4))
    ax.set_yticklabels([NAME[m] for m in MODELS])
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.colorbar(im, ax=ax, label="detection (%)", pad=0.01)
    cap = "Detection rate (%) at a 1% false-positive rate per malware family on the April test set; the threshold of each model and seed is set on the April benign reports (the 1% FPR on clean reports is true by construction), mean over 10 seeds."
    C.save_fig(fig, "F6_per_family_detection", "Per-family detection heatmap", cap, [C.spec["models"][m]["logits"]["file"] for m in MODELS] + ["results/hier/data/meta.csv"])


def attack_value(A, m, key, thr_key="t1"):
    """list of per-seed detection (fraction) for an edit set or 'wb<k>' (k greedy steps); None if pending"""
    mk = C_ATTACK[m]
    if key.startswith("wb"):
        w = A.get(f"wb|{mk}|{thr_key}")
        if w is None or w == "pending" or A.get(f"wb|{mk}") == "pending":
            return None
        return [row[int(key[2:])] for row in w["flagged_share_by_step_per_seed"]]
    v = A.get(f"{mk}|{key}|{thr_key}")
    return None if v is None else v["detection"]


C_ATTACK = {"M1": "m1", "M2": "m2", "M3": "m3", "M4": "m4"}


def f7(C):
    plt = style()
    A = C.json("attack_results")
    M = np.full((4, len(ATTACK_COLS)), np.nan)
    pend = np.zeros_like(M, dtype=bool)
    for i, m in enumerate(MODELS):
        for j, (k, _) in enumerate(ATTACK_COLS):
            v = attack_value(A, m, k)
            if v is None:
                pend[i, j] = True
            else:
                M[i, j] = 100 * np.mean(v)
    fig, ax = plt.subplots(figsize=(DC, 2.3))
    cm = plt.get_cmap("viridis").copy()
    cm.set_bad("#DDDDDD")
    im = ax.imshow(np.ma.masked_invalid(M), cmap=cm, vmin=0, vmax=100, aspect="auto")
    for i in range(4):
        for j in range(len(ATTACK_COLS)):
            ax.text(j, i, "pending" if pend[i, j] else f"{M[i, j]:.1f}", ha="center", va="center", fontsize=7, color="black" if pend[i, j] or M[i, j] > 55 else "white")
    ax.set_xticks(range(len(ATTACK_COLS)))
    ax.set_xticklabels([c for _, c in ATTACK_COLS])
    ax.set_yticks(range(4))
    ax.set_yticklabels([NAME[m] for m in MODELS])
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.colorbar(im, ax=ax, label="malware detected (%)", pad=0.01)
    cap = "Robustness to API-call padding: share of April malware still detected at a 1% false-positive rate (threshold on the unedited April benign reports) after the edit, mean over 10 seeds. Random padding takes calls from benign reports (EVAL pool), the LightGBM edit uses calls ranked by a LightGBM surrogate, the white-box attack is a greedy search with 200 candidates per step on 500 malware reports." + (" Grey cells marked pending: not computed yet." if pend.any() else "")
    C.save_fig(fig, "F7_robustness_heatmap", "Robustness heatmap", cap, [C.spec["attack_results"]])


def f8(C):
    plt = style()
    A = dict(C.json("attack_results"))
    extra = C.spec.get("attack_results_extra")                      # NOTES 26 item 2 (stage_k): random padding k = 60 and 75 (held-out pool), only the keys the main file does not have
    if extra:
        A.update({k: v for k, v in json.load(open(p(extra))).items() if k not in A})
    fig, ax = plt.subplots(1, 4, figsize=(DC, 2.2), sharey=True)
    ksr = [5, 20, 50] + ([60, 75] if extra else []) + [100, 200]
    panels = [("random", ["prepend"], "random, prepend", ksr), ("random", ["insert"], "random, insert", ksr),
              ("lgbm", ["prepend", "insert"], "LightGBM (solid: prepend, dashed: insert)", [20, 50, 100])]
    for a, (kind, modes, title, ks) in zip(ax[:3], panels):
        for m in MODELS:
            for mode, ls in zip(modes, ("-", "--")):
                kk = [k for k in ks if attack_value(A, m, f"{kind}_{k}_{mode}") is not None]
                v = [attack_value(A, m, "unedited")] + [attack_value(A, m, f"{kind}_{k}_{mode}") for k in kk]
                if any(x is None for x in v):
                    continue
                v = 100 * np.array(v).T
                a.plot([0] + kk, v.mean(0), ls=ls, marker="o", ms=3, color=COL[m], label=NAME[m] if mode == modes[0] else None)
                a.fill_between([0] + kk, v.mean(0) - v.std(0, ddof=1), v.mean(0) + v.std(0, ddof=1), color=COL[m], alpha=0.15, lw=0)
        a.set_title(title, fontsize=7.5)
        a.set_xlabel("added calls k")
        if kind == "random":
            a.axvline(50, color="0.5", lw=0.7, ls=":")                  # the padded training of M3 and M4 drew k from 1 to 50
    a = ax[3]
    pend = []
    for m in MODELS:
        w = A.get(f"wb|{C_ATTACK[m]}|t1")
        if w is None or w == "pending":
            pend.append(NAME[m])
            continue
        v = 100 * np.array(w["flagged_share_by_step_per_seed"])
        a.plot(range(v.shape[1]), v.mean(0), color=COL[m])
        a.fill_between(range(v.shape[1]), v.mean(0) - v.std(0, ddof=1), v.mean(0) + v.std(0, ddof=1), color=COL[m], alpha=0.15, lw=0)
    a.set_title("white-box greedy (prepend)", fontsize=7.5)
    a.set_xlabel("greedy steps")
    if pend:
        a.text(0.97, 0.97, "pending: " + ", ".join(pend), transform=a.transAxes, fontsize=6.5, va="top", ha="right")
    ax[0].set_ylabel("malware detected (%)")
    ax[0].legend(fontsize=6.5)
    cap = "Detection of April malware at a 1% false-positive rate against the number of calls added by the attacker (random padding prepended and inserted, LightGBM-ranked padding, and the white-box greedy search), mean over 10 seeds with ± std bands. The dotted vertical line marks k = 50, the largest padding size seen in the training of M3 and M4 (M1 and M2 were trained without padding)." + (" A model whose white-box result is pending is named in the last panel." if pend else "")
    C.save_fig(fig, "F8_detection_vs_added_calls", "Detection vs number of added calls", cap, [C.spec["attack_results"]])


def p2_name(C, m):
    """key of model m in the seen/unseen file: '<m> ...(<p2_suffix>)' (the spec stores only the suffix, e.g. 'final' or 'fixed tokenizer')"""
    P = C.json("p2")
    suf = f"({C.spec['p2_suffix']})"
    hit = sorted({k.rsplit("|", 1)[0] for k in P["models"] if k.startswith(m + " ") and k.rsplit("|", 1)[0].endswith(suf)})
    assert len(hit) == 1, (m, hit)
    return hit[0]


def f9(C):
    plt = style()
    P = C.json("p2")
    fig, ax = plt.subplots(figsize=(SC, 2.6))
    for i, m in enumerate(MODELS):
        nm = p2_name(C, m)
        for j, sname in enumerate(("seen", "unseen")):
            r = P["models"][f"{nm}|{sname}"]
            mu = float(np.mean(r["pauc_per_seed"]))
            lo, hi = r["ci_cluster"]["pauc"]
            ax.bar(i + (j - 0.5) * 0.38, mu, 0.36, color=COL[m], hatch="" if sname == "seen" else "///", edgecolor="k" if sname == "unseen" else COL[m], lw=0.5, label=None)
            ax.errorbar(i + (j - 0.5) * 0.38, mu, yerr=[[mu - lo], [hi - mu]], color="k", capsize=2, lw=0.8)
    ax.set_xticks(range(4))
    ax.set_xticklabels([NAME[m].replace(" ", "\n", 1) for m in MODELS])
    ax.set_ylabel("pAUC at 1% FPR (April subset)")
    ax.set_ylim(0, 1)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor="#999999", label="seen"), Patch(facecolor="white", edgecolor="k", hatch="///", label="unseen")], loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    cap = "pAUC at 1% FPR on the April reports whose API sequence was seen (solid) or not seen (hatched) in the model's own training set, mean over 10 seeds; error bars: 95% cluster-bootstrap interval of the seed mean (reports with the same API sequence resampled together). The subsets differ in families and size."
    C.save_fig(fig, "F9_seen_vs_unseen", "Seen vs unseen pAUC", cap, [C.spec["p2"]])


def f10(C):
    plt = style()
    y = C.y()
    fig, ax = plt.subplots(1, 2, figsize=(DC, 2.4), sharex=True)
    for a, m in zip(ax, ("M1", "M3")):
        z = C.Z()[m][0]
        bins = np.linspace(np.percentile(z, 0.1), np.percentile(z, 99.9), 90)
        a.hist(z[y == 0], bins=bins, color="#999999", alpha=0.8, label="benign", log=True)
        a.hist(z[y == 1], bins=bins, color=COL[m], alpha=0.7, label="malware", log=True)
        for f, ls in ((0.01, "--"), (0.001, ":")):
            a.axvline(thr(z, y, f), color="k", ls=ls, lw=0.8, label=f"threshold at {f * 100:g}% FPR")
        a.set_title(NAME[m] + " (seed 0)")
        a.set_xlabel("logit")
    ax[0].set_ylabel("reports (log scale)")
    ax[0].legend(fontsize=6.5)
    cap = "Distribution of the model output (logit) on the April benign (grey) and malware (colour) reports for M1 and M3, seed 0; vertical lines: the thresholds at 1% (dashed) and 0.1% (dotted) false-positive rate on the benign reports. Log-scale counts."
    C.save_fig(fig, "F10_logit_distributions", "Logit distributions M1 and M3", cap, [C.spec["models"][m]["logits"]["file"] for m in ("M1", "M3")])


def f11(C):
    plt = style()
    E = C.json("eval_results")
    fig, ax = plt.subplots(figsize=(SC, 2.6))
    rng = np.random.default_rng(0)
    for i, m in enumerate(MODELS):
        v = np.array(E["test"][C.spec["models"][m]["eval_key"]]["pauc@0.01"])
        ax.boxplot([v], positions=[i], widths=0.5, showfliers=False, medianprops={"color": "k", "lw": 0.8}, boxprops={"color": COL[m]}, whiskerprops={"color": COL[m]}, capprops={"color": COL[m]})
        ax.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, s=9, color=COL[m], zorder=3, edgecolor="k", lw=0.3)
    ax.set_xticks(range(4))
    ax.set_xticklabels([NAME[m].replace(" ", "\n", 1) for m in MODELS])
    ax.set_ylabel("pAUC at 1% FPR (April)")
    cap = "pAUC at 1% FPR on the April test set for each of the 10 seeds (dots) and their box plot (median, quartiles, range) per model."
    C.save_fig(fig, "F11_pauc_per_seed", "pAUC per seed", cap, [C.spec["eval_results"]])


def f12(C):
    plt = style()
    d = json.load(open(os.path.join(C.data, "attn_m3_seed0.json")))
    fig, ax = plt.subplots(2, 1, figsize=(DC, 3.4), sharex=True, sharey=True)
    for a, which, ttl in zip(ax, ("detected", "missed"), ("a report detected by M3 (seed 0)", "a report missed by M3 (seed 0)")):
        r = d[which]
        w = np.array(r["weights"])
        a.bar(range(512), w, width=1.0, color=COL["M3"])
        top = np.argsort(-w)[:5]
        for n, k in enumerate(top):
            a.annotate(r["pieces"][k].replace("\u2581", "") or "(space)", (k, w[k]), xytext=(0, 3 + 7 * (n % 2)), textcoords="offset points", fontsize=6, ha="center", rotation=60)
        a.set_title(f"{ttl}: April row {r['april_row']}, logit {r['logit']:.2f}", fontsize=7.5)
        a.set_ylabel("pooling weight")
    ax[1].set_xlabel("token position (first 512 tokens)")
    cap = "Attention-pooling weights of M3 (ATT+bal, seed 0) over the 512 input tokens of two April malware reports, one detected and one missed at a 1% false-positive rate (rule: the lowest-index April malware report with at least 512 tokens in each class). The five highest-weight tokens are labelled with their SentencePiece pieces (the leading word-boundary mark is dropped). A uniform pooling would give every token the weight 1/512 = 0.00195: the learned weights stay close to uniform. Forward pass on CPU with the stored weights."
    C.save_fig(fig, "F12_attention_weights_M3", "Attention-pooling weights of M3", cap, [rel(os.path.join(C.data, "attn_m3_seed0.json"))])


def f13(C):
    plt = style()
    R = json.load(open(p("results", "review", "attack_aggregates.json")))["random"]
    sets = ["random_5_insert", "random_20_insert", "random_50_insert", "random_5_prepend", "random_20_prepend", "random_50_prepend"]
    models = [("attaug", "ATT, malware-only padding", "#CC79A7", ""), ("attbal", "ATT, balanced padding", "#009E73", ""), ("peaug", "PE, malware-only padding", "#CC79A7", "///"), ("pebal", "PE, balanced padding", "#009E73", "///")]
    fig, ax = plt.subplots(figsize=(SC, 3.1))                         # single column: 3.5 in wide
    for i, (k, lab, col, h) in enumerate(models):
        mu = [100 * R[f"{k}|{s}"]["1e-2"]["fpr"][0] for s in sets]
        sd = [100 * R[f"{k}|{s}"]["1e-2"]["fpr"][1] for s in sets]
        ax.bar(np.arange(len(sets)) + (i - 1.5) * 0.2, mu, 0.19, yerr=sd, color=col, hatch=h, edgecolor="k", lw=0.4, capsize=1, error_kw={"lw": 0.6}, label=lab)
    ax.axhline(1.0, color="k", ls=":", lw=0.6)
    ax.set_xticks(range(len(sets)))
    ax.set_xticklabels([f"{s.split('_')[2]}\n{s.split('_')[1]}" for s in sets], fontsize=7)      # e.g. "insert / 20"
    ax.tick_params(axis="y", labelsize=7)
    ax.set_xlabel("padding: mode and number of added calls k", fontsize=8)
    ax.set_ylabel("padded-benign false alarms (%)\nat 1% FPR", fontsize=8)
    ax.legend(ncol=2, fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), columnspacing=0.8, handlelength=1.4)
    cap = "EARLIER models (REPORT 5.10 and 5.11, old random validation split, 10 seeds each; not M1 to M4): false-positive rate on padded April benign reports at the 1% threshold of the unedited benign reports, for models trained with padding of malware reports only (pink) and with balanced padding of malware and benign reports (green); attention pooling (ATT, solid) and flatten pooling (PE, hatched). Bars: mean ± std over seeds; the dotted line is the clean 1%."
    C.save_fig(fig, "F13_padded_benign_false_alarms_earlier_models", "Padded-benign false alarms: malware-only vs balanced padding (earlier models)", cap, ["results/review/attack_aggregates.json"])


def f14(C):
    """SET B only (NOTES 26 item 4): padded-benign false alarms of the final-settings models trained with malware-only padding, next to the balanced-padding M3 and the no-padding M1"""
    plt = style()
    R = json.load(open(p(C.spec["item4_results"])))
    sets = ["random_5_insert", "random_20_insert", "random_50_insert", "random_5_prepend", "random_20_prepend", "random_50_prepend"]
    models = [("y_am", "attention, malware-only padding", "#CC79A7", ""), ("m3", "M3 ATT+bal (balanced padding)", "#009E73", ""), ("y_fm", "flatten, malware-only padding", "#CC79A7", "///"), ("m1", "M1 Nebula (no padding)", "#0072B2", "///")]
    fig, ax = plt.subplots(figsize=(SC, 3.1))
    for i, (k, lab, col, h) in enumerate(models):
        v = [100 * np.array(R[f"{k}|{s}|t1"]["padded_benign_fpr"]) for s in sets]
        ax.bar(np.arange(len(sets)) + (i - 1.5) * 0.2, [x.mean() for x in v], 0.19, yerr=[x.std(ddof=1) for x in v], color=col, hatch=h, edgecolor="k", lw=0.4, capsize=1, error_kw={"lw": 0.6}, label=lab)
    ax.axhline(1.0, color="k", ls=":", lw=0.6)
    ax.set_xticks(range(len(sets)))
    ax.set_xticklabels([f"{s.split('_')[2]}\n{s.split('_')[1]}" for s in sets], fontsize=7)
    ax.tick_params(axis="y", labelsize=7)
    ax.set_xlabel("padding: mode and number of added calls k", fontsize=8)
    ax.set_ylabel("padded-benign false alarms (%)\nat 1% FPR", fontsize=8)
    ax.legend(ncol=2, fontsize=6.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), columnspacing=0.8, handlelength=1.4)
    cap = "Corrected-tokenizer models with the final M1 (flatten) and M3 (attention) settings (10 seeds): false-positive rate on padded April benign reports at the 1% threshold of the unedited benign reports, for models trained with padding of malware reports only (pink; solid = attention head, hatched = flatten head), the balanced-padding M3 (green) and the no-padding M1 (blue, hatched). Bars: mean ± std over seeds; the dotted line is the clean 1%."
    C.save_fig(fig, "F14_padded_benign_false_alarms_final_settings", "Padded-benign false alarms: malware-only vs balanced padding (final settings)", cap, [C.spec["item4_results"]])


def f_ab(C):
    """SET B only: per-seed pAUC of the current (SET A) and the corrected tokenizer per model, paired side by side"""
    plt = style()
    E = C.json("eval_results")
    fig, ax = plt.subplots(figsize=(DC, 2.6))
    rng = np.random.default_rng(0)
    for i, m in enumerate(MODELS):
        ck, fk = C.spec["compare"][m]
        for j, (key, lab, h) in enumerate(((ck, "current tokenizer", ""), (fk, "corrected tokenizer", "///"))):
            v = np.array(E["test"][key]["pauc@0.01"])
            x = i + (j - 0.5) * 0.36
            ax.boxplot([v], positions=[x], widths=0.3, showfliers=False, medianprops={"color": "k", "lw": 0.8}, boxprops={"color": COL[m]}, whiskerprops={"color": COL[m]}, capprops={"color": COL[m]})
            ax.scatter(x + rng.uniform(-0.07, 0.07, len(v)), v, s=8, color=COL[m], edgecolor="k", lw=0.3, zorder=3, marker="o" if j == 0 else "s")
    ax.set_xticks(range(4))
    ax.set_xticklabels([NAME[m] for m in MODELS])
    ax.set_ylabel("pAUC at 1% FPR (April)")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", color="k", ls="none", label="current tokenizer (left of each pair)"), Line2D([], [], marker="s", color="k", ls="none", label="corrected tokenizer (right)")])
    cap = "pAUC at 1% FPR on the April test set for each seed (dots) and box plots per model: the current tokenizer (left of each pair, circles) against the corrected tokenizer with byte fallback and full character coverage (right, squares). Same settings, same 10 seeds; pairs are matched by seed index only."
    C.save_fig(fig, "F_AB_tokenizer_comparison", "Current vs corrected tokenizer per model", cap, [C.spec["eval_results"]])


# --------------------------------------------------------------------------------------------- tables
def t1(C):
    from baseline import groupsplit as G
    jt = G.january_table()
    fa, _, _ = C.meta()
    fj = jt["train"]["family"]
    fams = [f for f, _ in sorted(((f, (fj == f).sum()) for f in set(fj)), key=lambda t: -t[1])]
    rows = [[f.replace("windows_", ""), "benign" if f in ("clean", "windows_syswow64") else "malware", f"{int((fj == f).sum()):,}", f"{int((fa == f).sum()):,}"] for f in fams]
    rows.append(["**total**", "", f"**{len(fj):,}**", f"**{len(fa):,}**"])
    C.save_table("T1_dataset", "Dataset per family and split", ["family", "class", "January (training)", "April (test)"], rows, "Emulation reports per family in the training (January 2022) and test (April 2022) sets.",
                 ["results/hier/data/meta.csv", "results/misses/reports.csv"], "llrr")


def t2(C):
    tok = C.spec["tokenizer"]
    H = ["setting"] + [NAME[m] for m in MODELS]
    rows = [["tokenizer", tok, tok, tok, tok], ["input window", "first 512 tokens", "first 4,096 tokens (up to 8 chunks of 512)", "first 512 tokens", "first 4,096 tokens (up to 8 chunks of 512)"],
            ["encoder (level 1)", "2 layers, 8 heads, d 64, hidden 256, chunks of 64 tokens", "same (from scratch)", "same", "same (from scratch)"],
            ["level 2", "-", "2 layers, 4 heads, hidden 128, dropout 0.1, chunk-position embedding", "-", "same as M2"], ["pooling", "flatten", "attention pooling per chunk, level 2 over chunks", "attention pooling", "attention pooling per chunk, level 2 over chunks"],
            ["positional encoding", "sinusoidal (paper Eq. 1-2)", "sinusoidal", "sinusoidal", "sinusoidal"], ["optimiser", "AdamW, weight decay 1e-2", "same", "same", "same"], ["learning rate", "2e-3", "1e-3", "1e-3", "1e-3"],
            ["batch size, gradient clip, dropout", "96, 0.5, 0.3", "96, 0.5, 0.3", "96, 0.5, 0.3", "96, 0.5, 0.3"], ["epochs", "1", "1", "3", "1"],
            ["padding augmentation", "none", "none", "balanced, p = 0.5 (malware and benign)", "balanced, p = 0.5, before chunking"], ["training reports", "75,298 (all of January)", "75,298", "75,298", "75,298"],
            ["seeds", "10 (0-9)", "10", "10", "10"], ["selection of the settings", "validation slice (group split), NOTES 21.10", "validation slice, NOTES 23.1", "validation slice, NOTES 21.10", "validation slice, NOTES 23.1"]]
    C.save_table("T2_hyperparameters", "Hyper-parameters per model", H, rows, "Training settings of the four final models (all trained on the 75,298 January reports; settings chosen on a held-out validation slice, never on April).",
                 ["baseline/v2pe.py", "baseline/twolevel.py", "NOTES.md sections 21-23"], "lllll")


def t3(C):
    pr = json.load(open(os.path.join(C.data, "params.json")))
    rows = []
    for m in MODELS:
        r = pr[m]
        rows.append([NAME[m], f"{r['level1']:,}" if r.get("level2") is not None else f"{r['total']:,}", f"{r['level2']:,}" if r.get("level2") is not None else "-", f"{r['total']:,}"])
    C.save_table("T3_parameter_counts", "Parameter counts", ["model", "level 1 (encoder)", "level 2", "total"], rows,
                 "Trainable parameters (sum of p.numel() over the model parameters read from the stored weights; the fixed sinusoidal table is a buffer, not a parameter).", [rel(os.path.join(C.data, "params.json"))], "lrrr")


def t4(C):
    E = C.json("eval_results")
    H = ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1 (threshold 0.5)", "pAUC@1e-2"]
    rows = [["Nebula paper (Table 7)", f"{PAPER['tpr@1e-3']:.3f}", "-", "-", f"{PAPER['f1']:.3f}", "-"]]
    for m in MODELS:
        t = E["test"][C.spec["models"][m]["eval_key"]]
        rows.append([NAME[m], ms(t["tpr@0.001"], 3, 1), ms(t["tpr@0.01"], 3, 1), ms(t["auc"], 4, 1), ms(t["f1@0.5"], 3, 1), ms(t["pauc@0.01"], 3, 1)])
    rows.append(["10-seed ensemble (mean logit)", "", "", "", "", ""])
    for m in MODELS:
        e = E["ensemble"][C.spec["models"][m]["eval_key"]]
        rows.append([NAME[m] + " (ensemble)", f"{e['tpr@0.001']:.3f}", f"{e['tpr@0.01']:.3f}", f"{e['auc']:.4f}", f"{e['f1@0.5']:.3f}", f"{e['pauc@0.01']:.3f}"])
    C.save_table("T4_clean_results", "Clean April results with the Nebula paper row", H, rows, "Clean April test results (17,402 reports), mean ± std over 10 seeds and 10-seed ensembles. TPR@x: true-positive rate at a threshold giving false-positive rate x on the April benign reports; the paper row gives the two numbers we take from the Nebula paper.",
                 [C.spec["eval_results"]])


def t5(C):
    A = C.json("attack_results")
    names = [k.split("|")[1] for k in A if k.startswith("m1|") and k.endswith("|t1")]
    for thr_key, lab, tid in (("t1", "1%", "T5a"), ("t01", "0.1%", "T5b")):
        rows = []
        for nm in names:
            rows.append([nm.replace("_", " ")] + [ms(attack_value(A, m, nm, thr_key)) if attack_value(A, m, nm, thr_key) is not None else "pending" for m in MODELS])
        for k in (5, 10, 20, 50):
            r = [f"white-box {k} steps"]
            for m in MODELS:
                v = attack_value(A, m, f"wb{k}", thr_key)
                r.append(ms(v) if v is not None else "pending")
            rows.append(r)
        C.save_table(f"{tid}_attack_detection_{lab.replace('%', 'pct')}", f"Attack results: detection at {lab} FPR", ["edit"] + [NAME[m] for m in MODELS], rows,
                     f"Detection (%) of April malware after each edit at the {lab} false-positive-rate threshold of the unedited April benign scores, mean ± std over 10 seeds (white-box: 500 malware reports)." + (" Pending = not computed yet." if any("pending" in str(c) for r in rows for c in r) else ""), [C.spec["attack_results"]])
    rows = []
    for nm in names:
        rows.append([nm.replace("_", " ")] + [ms(A[f"{C_ATTACK[m]}|{nm}|t1"]["padded_benign_fpr"], 2) if f"{C_ATTACK[m]}|{nm}|t1" in A else "pending" for m in MODELS])
    C.save_table("T5c_attack_padded_benign_fpr_1pct", "Attack results: padded-benign FPR", ["edit"] + [NAME[m] for m in MODELS], rows,
                 "False-positive rate (%) on the same edit applied to the April benign reports, 1% threshold, mean ± std over 10 seeds (unedited: 1% by construction).", [C.spec["attack_results"]])


def t6(C):
    P = C.json("p2")
    rows = []
    for m in MODELS:
        nm = p2_name(C, m)
        r = [NAME[m]]
        for sname in ("seen", "unseen"):
            x = P["models"][f"{nm}|{sname}"]
            r += [ms(x["pauc_per_seed"], 3, 1), f"[{x['ci_cluster']['pauc'][0]:.3f}, {x['ci_cluster']['pauc'][1]:.3f}]", ms(x["tpr01_per_seed"], 3, 1)]
        rows.append(r)
    sub = P["subsets"]
    key = [k for k in sub if k.startswith("jan|")]
    desc = "; ".join(f"{k.split('|')[1]}: {sub[k]['reports']:,} reports ({sub[k]['malware']:,} malware, {sub[k]['groups']:,} groups)" for k in key)
    C.save_table("T6_seen_unseen", "Seen vs unseen April reports", ["model", "pAUC@1e-2 seen", "cluster 95% CI", "TPR@1e-2 seen", "pAUC@1e-2 unseen", "cluster 95% CI", "TPR@1e-2 unseen"], rows,
                 f"April reports whose API sequence is seen / unseen in the model's own training set ({desc}); metrics computed inside each subset, mean ± std over 10 seeds; CI = cluster bootstrap of the seed mean.", [C.spec["p2"]])


def t7(C):
    E = C.json("eval_results")
    extra_path = os.path.join(C.data, "pairs_extra.json")
    extra = json.load(open(extra_path)) if os.path.exists(extra_path) else {}
    pairs = [("M3", "M1"), ("M4", "M3"), ("M4", "M2"), ("M2", "M1")]
    rows = []
    for a, b in pairs:
        ka, kb = C.spec["models"][a]["eval_key"], C.spec["models"][b]["eval_key"]
        r = E["pairs"].get(f"{ka}-{kb}|pauc@0.01") or extra.get(f"{ka}-{kb}")
        if r is None:
            rows.append([f"{NAME[a]} − {NAME[b]}", "n/a", "n/a", "n/a", "n/a", "not computed"])
            continue
        res = r["cluster_lo"] > 0 or r["cluster_hi"] < 0
        cells = [f"{100 * r['mean']:+.2f}", f"[{100 * r['strat_lo']:+.2f}, {100 * r['strat_hi']:+.2f}]", f"[{100 * r['cluster_lo']:+.2f}, {100 * r['cluster_hi']:+.2f}]", f"{r['seeds_up']} up / {r['seeds_down']} down", "resolved" if res else "not resolved"]
        rows.append([f"{NAME[a]} − {NAME[b]}"] + [f"**{c}**" if res else c for c in cells])
    C.save_table("T7_pairwise_differences", "Pairwise differences", ["difference", "pAUC@1e-2 (points)", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome"], rows,
                 "Pairwise differences of the April pAUC@1e-2 (points x100; mean of the 10 per-seed differences; seeds paired by index only). Bold = resolved: the cluster-bootstrap interval excludes 0.", [C.spec["eval_results"], rel(extra_path)])


def t8(C):
    E = C.json("eval_results")
    rows = []
    for m in MODELS:
        ck, fk = C.spec["compare"][m]
        r = E["pairs"][f"{fk}-{ck}|pauc@0.01"]
        res = r["cluster_lo"] > 0 or r["cluster_hi"] < 0
        cells = [f"{100 * r['mean']:+.2f}", f"[{100 * r['strat_lo']:+.2f}, {100 * r['strat_hi']:+.2f}]", f"[{100 * r['cluster_lo']:+.2f}, {100 * r['cluster_hi']:+.2f}]", f"{r['seeds_up']} up / {r['seeds_down']} down", "resolved" if res else "not resolved"]
        rows.append([NAME[m], ms(E["test"][ck]["pauc@0.01"], 3, 1), ms(E["test"][fk]["pauc@0.01"], 3, 1)] + [f"**{c}**" if res else c for c in cells])
    C.save_table("T8_current_vs_corrected_tokenizer", "Current vs corrected tokenizer per model", ["model", "pAUC@1e-2 current", "pAUC@1e-2 corrected", "difference (points)", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome"], rows,
                 "April pAUC@1e-2 with the current tokenizer and with the corrected tokenizer (byte fallback, full character coverage, id 0 = padding only), mean ± std over 10 seeds and the paired difference corrected − current (points x100). Bold = resolved (cluster interval excludes 0).", [C.spec["eval_results"]])


# --------------------------------------------------------------------------------------------- caches (--prepare)
def prepare(C):
    raw = C.spec["raw"]
    done = []
    if raw.get("stores"):                                           # report length per report (tokens), January rows then April rows
        from baseline import callstore as CS
        st = CS.CallStore.load(raw["stores"]["file"])
        ntr = 75298
        L = np.diff(st.seg_off[st.rep_seg]).astype(np.int64)
        lab = np.load(raw["stores"]["labels"])
        np.savez_compressed(os.path.join(C.data, "lengths.npz"), len_train=L[:ntr], len_test=L[ntr:], y_train=lab["y_train"].astype(int), y_test=lab["y_test"].astype(int))
        done.append("lengths.npz")
    if raw.get("loss"):
        out = {}
        for m, globs in raw["loss"].items():
            files = sorted(glob.glob(globs), key=lambda f: int(re.search(r"seed(\d+)\.json", f).group(1)))
            assert len(files) == 10, (m, len(files))
            recs = [json.load(open(f))["per_epoch"] for f in files]
            out[m] = {"train": [[e["train_epoch_mean_loss"] for e in r] for r in recs], "val": [[e["val_loss"] for e in r] for r in recs]}
        json.dump(out, open(os.path.join(C.data, "loss.json"), "w"))
        done.append("loss.json")
    if raw.get("weights"):
        import torch
        out = {}
        for m, path in raw["weights"].items():
            sd = torch.load(path, map_location="cpu", weights_only=True)
            par = {k: v.numel() for k, v in sd.items() if not k.endswith("pos_encoder.pe")}            # the sinusoidal table is a buffer
            if any(k.startswith("level1.") for k in par):
                l1 = sum(v for k, v in par.items() if k.startswith("level1."))
                out[m] = {"level1": l1, "level2": sum(par.values()) - l1, "total": sum(par.values())}
            else:
                out[m] = {"level1": sum(par.values()), "level2": None, "total": sum(par.values())}
        json.dump(out, open(os.path.join(C.data, "params.json"), "w"), indent=1)
        done.append("params.json")
    if raw.get("attn_raw"):                                         # output of baseline/paper_attn.py (CPU kernel) + the tokenizer for the piece strings
        import sentencepiece as spm
        a = json.load(open(raw["attn_raw"]))[C.set]
        sp = spm.SentencePieceProcessor(model_file=raw["tokenizer_model"])
        for which, r in a.items():
            assert abs(r["logit"] - r["stored_logit"]) < 1e-3, (which, r["logit"], r["stored_logit"])
            r["pieces"] = [("" if t == 0 else sp.id_to_piece(int(t))) for t in r["ids"]]
        json.dump(a, open(os.path.join(C.data, "attn_m3_seed0.json"), "w"))
        done.append("attn_m3_seed0.json")
    if raw.get("attack_scores"):                                    # results.json of gs_attack_report.py rebuilt from the stored attack scores (adds the white-box curves)
        import subprocess
        tmp = os.path.join(C.data, "_attack_tmp")
        subprocess.check_call([sys.executable, "-m", "baseline.gs_attack_report", "--scores", raw["attack_scores"], "--out", tmp, "--suffix", ""], env=dict(os.environ, MPLBACKEND="Agg"))
        os.replace(os.path.join(tmp, "results.json"), os.path.join(C.data, "attack_results.json"))
        import shutil
        shutil.rmtree(tmp)
        done.append("attack_results.json")
    print("prepared:", done)


def pairs_extra(C):
    """pairs of T7 that the evaluation file does not hold (e.g. M2 - M1 of SET B): bootstrap on the stored logits with the same functions and seed as gs_eval_g.py / gs_eval_i.py (needs the nebula shim on PYTHONPATH)"""
    E = C.json("eval_results")
    need = []
    for a, b in (("M3", "M1"), ("M4", "M3"), ("M4", "M2"), ("M2", "M1")):
        ka, kb = C.spec["models"][a]["eval_key"], C.spec["models"][b]["eval_key"]
        if f"{ka}-{kb}|pauc@0.01" not in E["pairs"]:
            need.append((ka, kb, a, b))
    if not need:
        return
    cache = os.path.join(C.data, "pairs_extra.json")
    if os.path.exists(cache) and all(f"{ka}-{kb}" in json.load(open(cache)) for ka, kb, _, _ in need):
        return                                                    # already bootstrapped (same stored logits, same seed): reuse
    from baseline import gap_final
    from baseline.twolevel_eval import cluster_bootstrap
    from baseline.v2pe_report import metrics_of
    y = C.y()
    _, _, groups = C.meta()
    Z = {C.spec["models"][m]["eval_key"]: C.Z()[m] for m in MODELS}
    pairs = [(ka, kb) for ka, kb, _, _ in need]
    bs = gap_final.bootstrap(y, Z, 1000, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, 1000)
    T = {k: metrics_of(y, Z[k]) for k in Z}
    out = {}
    for ka, kb, a, b in need:
        dd = T[ka]["pauc@0.01"] - T[kb]["pauc@0.01"]
        ps = bs["ps"]["diffs"][f"{ka} - {kb}"]["pauc@0.01"]
        lo, hi = np.percentile(cd[(ka, kb)][:, 3], [2.5, 97.5])
        out[f"{ka}-{kb}"] = {"mean": float(dd.mean()), "strat_lo": float(ps["lo"]), "strat_hi": float(ps["hi"]), "cluster_lo": float(lo), "cluster_hi": float(hi), "seeds_up": int((dd > 0).sum()), "seeds_down": int((dd < 0).sum())}
    json.dump(out, open(os.path.join(C.data, "pairs_extra.json"), "w"), indent=1)


# --------------------------------------------------------------------------------------------- driver and README
ITEMS = [("F2", f2), ("F3", f3), ("F4", f4), ("F5", f5), ("F6", f6), ("F7", f7), ("F8", f8), ("F9", f9), ("F10", f10), ("F11", f11), ("F12", f12), ("F13", f13), ("F14", f14), ("F_AB", f_ab),
         ("T1", t1), ("T2", t2), ("T3", t3), ("T4", t4), ("T5", t5), ("T6", t6), ("T7", t7), ("T8", t8)]


def run_items(C, only):
    sel = set(only.split(",")) if only else None
    for id_, fn in ITEMS:
        if sel and id_ not in sel:
            continue
        if id_ == "F13" and C.set != "A":
            C.note("figure", id_, "Padded-benign false alarms, malware-only vs balanced padding (earlier models)", [], [], "skipped", "SET A only (earlier models of REPORT 5.10/5.11, old tokenizer)")
            continue
        if id_ == "F14" and "item4_results" not in C.spec:
            C.note("figure", id_, "Padded-benign false alarms, malware-only vs balanced padding (final settings)", [], [], "skipped", "SET B only (item 4 of NOTES 26, corrected tokenizer)")
            continue
        if id_ in ("F_AB", "T8") and "compare" not in C.spec:
            C.note("figure" if id_.startswith("F") else "table", id_, "Current vs corrected tokenizer", [], [], "skipped", "only for SET B (needs the corrected-tokenizer models)")
            continue
        try:
            if id_ == "T7":
                pairs_extra(C)
            fn(C)
            print("made", id_, flush=True)
        except Exception as e:                                       # skip, note the reason, continue
            traceback.print_exc()
            C.note("figure" if id_.startswith("F") else "table", id_, fn.__name__, [], [], "skipped", f"{type(e).__name__}: {e}")
    prev = os.path.join(C.out, "manifest.json")
    old = json.load(open(prev)) if (sel and os.path.exists(prev)) else []
    match = lambda mid, i: re.match(re.escape(i) + r"(?![0-9])", mid) is not None
    keep = [m for m in old if not any(match(m["id"], i) for i in (sel or []))] if sel else []
    done_ids = {m["id"] for m in C.manifest}
    json.dump([m for m in keep if m["id"] not in done_ids] + C.manifest, open(prev, "w"), indent=1)


def write_readme():
    root = p("results", "paper")
    L = ["# Paper figures and tables", "", "Generated by `python -m baseline.paper_figs --models results/paper/specs/<set>.json` from STORED logits, scores and results only (no training, no GPU, no new April evaluation, no model choice).",
         "Style: matplotlib, vector PDF + PNG at 300 dpi, 3.5 in (single column) and 7.16 in (double column), serif 8 pt, Okabe-Ito colour-blind-safe palette with one fixed colour per model (M1 blue, M2 orange, M3 green, M4 vermillion), std over 10 seeds unless stated.",
         "Regenerate one item: `--only F7,T5`; rebuild the caches: `--prepare`; this file: `--readme`. A later run fills the cells marked *pending* once the input file named in the spec (`attack_results`) is replaced by the complete one.", "",
         "Sets: **A** = reproduction (the paper's tokenizer): final M1, M3 (Step 5), M2, M4 (Stage G), attacks of Stage H. **B** = corrected tokenizer (`bpe50k_fix`, NOTES 25): the same four models retrained, attacks of Stage J.", ""]
    for s in sorted(d for d in os.listdir(root) if os.path.exists(os.path.join(root, d, "manifest.json"))):
        man = json.load(open(os.path.join(root, s, "manifest.json")))
        L += [f"## SET {s}", "", "| item | title | status | files | sources |", "|---|---|---|---|---|"]
        for m in man:
            files = "<br>".join(f"`{f}`" for f in m["files"]) or "-"
            src = "<br>".join(f"`{x}`" for x in m["sources"]) or "-"
            L.append(f"| {m['id']} | {m['title']} | {m['status']}{': ' + m['reason'] if m['reason'] else ''} | {files} | {src} |")
        L.append("")
    L += ["## Notes", "", "- F12 needs the authors' model code, so the attention weights were produced by a CPU-only Kaggle kernel (`baseline/paper_attn.py`, owner msingh9365, no GPU) from the stored M3 seed-0 weights; the logit it computed equals the stored logit (asserted).",
          "- Display names: M1 is labelled \"M1 Nebula\" in every figure and table (the spec files look results up by the model's internal key, not by its display label). F13 is drawn at single-column width (3.5 in).",
          "- F12, SET A: the thin white gaps (weight exactly 0) in the detected report are tokens with id 0, i.e. letters the old tokenizer cannot encode (the letter `j`, NOTES 24.1), which attention pooling treats as padding; SET B has none.",
          "- F13 shows the EARLIER models of REPORT 5.10/5.11 (old split, old tokenizer), labelled as such; it exists for SET A only.",
          "- Nebula paper numbers used: TPR 0.5213 at FPR 1e-3 and F1 0.9136 (Table 7) only."]
    open(os.path.join(root, "README.md"), "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=None, help="JSON spec of a model set")
    ap.add_argument("--only", default=None, help="comma-separated item ids, e.g. F5,T4")
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--readme", action="store_true")
    a = ap.parse_args()
    if a.models:
        C = Ctx(a.models if os.path.isabs(a.models) else p(a.models))
        if a.prepare:
            prepare(C)
        else:
            run_items(C, a.only)
    if a.readme or (a.models and not a.prepare):
        write_readme()


if __name__ == "__main__":
    main()
