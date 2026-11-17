"""
Tables and plots for REPRODUCTION_REPORT.md from the metrics files of the Kaggle jobs.   (OURS)

    python -m baseline.report --results results/baseline_raw --out results/baseline

Reads  <results>/detect/<variant>_<regime>_seed0/metrics.json, <results>/released/metrics.json, <results>/ssl/seed*/<run>/metrics.json,
       <results>/classify/*/metrics.json, <results>/ablate/*/metrics.json
Writes <out>/tables.md and <out>/plots/*.png. The paper's numbers are the constants below (arXiv 2310.10664v2).
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C

# ----------------------------------------------------------------------------- the paper (arXiv v2)
PAPER = {
    "table7": {"bpe50k": {"batches": 2116, "tpr": 0.5213, "auc": 0.9657, "f1": 0.9136, "acc": 0.9104},
               "ws50k": {"batches": 2159, "tpr": 0.5703, "auc": 0.9664, "f1": 0.9058, "acc": 0.9053}},
    "val_f1": {"bpe50k": 0.9847, "ws50k": 0.9870},                                       # Table 5, filtered
    "table9_f1": {"bpe50k": [0.8526, 0.8548, 0.6303, 0.2850, 0.1295, 0.7421, 0.3683, 0.6827],
                  "ws50k": [0.8240, 0.8324, 0.6214, 0.4615, 0.1179, 0.6523, 0.1854, 0.6486]},
    "table4_val": {5000: (0.8078, 0.9965, 0.9817, 0.9753), 10000: (0.7834, 0.9969, 0.9839, 0.9782), 30000: (0.8576, 0.9977, 0.9861, 0.9811),
                   50000: (0.8383, 0.9976, 0.9856, 0.9806), 70000: (0.8407, 0.9977, 0.9862, 0.9814)},   # TPR@1e-3, AUC, F1, Acc (validation)
    "table6_test": {"wp50k": (0.5540, 0.9630, 0.9049, 0.9041), "ws50k": (0.5703, 0.9664, 0.9068, 0.9053), "bpe50k": (0.5213, 0.9657, 0.9136, 0.9104)},
}
# categorical palette validated with the dataviz validator (CVD-safe; contrast < 3:1 on white, so lines also differ in style)
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]
STYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1))]


def jl(p):
    return json.load(open(p))


def pm(ms, key, d=4):
    v = ms[key]
    return f"{v['mean']:.{d}f} ± {v['std']:.{d}f}"


def md(rows, header):
    out = "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n"
    for r in rows:
        out += "| " + " | ".join(str(c) for c in r) + " |\n"
    return out


# ----------------------------------------------------------------------------- A and E: detection
def detection(res, out):
    txt = "## A. Detection (paper Table 7)\n\n"
    rows = []
    for variant in ["bpe50k", "ws50k", "ws50k_legacy"]:
        pk = variant.replace("_legacy", "")                                  # the paper has one Whitespace row
        p = PAPER["table7"][pk]
        if variant != "ws50k_legacy":
            rows.append([f"**paper**, Nebula {'BPE' if variant == 'bpe50k' else 'Whitespace'}", 3, p["batches"], p["tpr"], "", p["auc"], p["f1"], p["acc"],
                         PAPER["val_f1"][pk], "Quadro T2000"])
        for regime in ["time", "batches"]:
            f = os.path.join(res, "detect", f"{variant}_{regime}_seed0", "metrics.json")
            if not os.path.exists(f):
                continue
            m = jl(f)
            t, v = m["test_mean_std"], m["val_mean_std"]
            b = [r["batches_seen"] for r in m["folds"]]
            name = {"bpe50k": "BPE", "ws50k": "WS (pinned-repo cleaning)", "ws50k_legacy": "WS (legacy cleaning)"}[variant]
            p32 = m.get("test_p32_mean_std")
            rows.append([f"ours, {name} {'time-matched (5 min/fold)' if regime == 'time' else 'batch-matched'}", len(m["folds"]),
                         f"{np.mean(b):.0f} ({min(b)}–{max(b)})", pm(t, "tpr@0.001"), pm(p32, "tpr@0.001") if p32 else "", pm(t, "auc"),
                         pm(t, "f1@0.5"), pm(t, "acc@0.5"), pm(v, "f1@0.5"), m["env"].get("gpu", "?")])
    txt += md(rows, ["run", "fold models", "batches / fold", "test TPR @ FPR 1e-3 (logit-ranked)", "same, literal float32 probabilities", "test AUC",
                     "test F1 (thr 0.5)", "test Acc (thr 0.5)", "val F1 (thr 0.5)", "GPU"])
    txt += "\nMean ± std (population std, as the authors' CV code) over the fold models (3 per seed; seeds pooled). The TPR threshold comes from " \
           "the test set itself (`get_tpr_at_fpr`, the authors' function). **Logit-ranked** is the headline number: after the float32 sigmoid, " \
           "tens of benign reports tie with the top malware scores at exactly 1.0 (more than the 8 that FPR 1e-3 allows), so the literal " \
           "procedure returns 0 for those models (an output-precision artifact, see NOTES.md §4).\n\n"
    # secondary table: TPR at other FPRs
    rows = []
    for variant in ["bpe50k", "ws50k", "ws50k_legacy"]:
        for regime in ["time", "batches"]:
            f = os.path.join(res, "detect", f"{variant}_{regime}_seed0", "metrics.json")
            if os.path.exists(f):
                t = jl(f)["test_mean_std"]
                rows.append([f"{variant} {regime}"] + [f"{t[f'tpr@{x:g}']['mean']:.4f}" for x in C.FPRS] + [f"{t['f1@fpr0.001']['mean']:.4f}"])
    if rows:
        txt += md(rows, ["run"] + [f"TPR@{x:g}" for x in C.FPRS] + ["F1 at the FPR-1e-3 threshold"]) + "\n"
    # E: released models
    f = os.path.join(res, "released", "metrics.json")
    if os.path.exists(f):
        r = jl(f)
        rows = []
        for variant, name in [("released_bpe50k", "released Nebula BPE"), ("released_ws50k", "released Nebula Whitespace, pinned-repo tokenizer"),
                              ("released_ws50k_legacy", "released Nebula Whitespace, legacy cleaning (ours, inferred)")]:
            if variant not in r:
                continue
            t = r[variant]["test"]
            rows.append([name, f"{t['tpr@0.001']:.4f}", f"{t['auc']:.4f}", f"{t['f1@0.5']:.4f}", f"{t['acc@0.5']:.4f}",
                         f"{r[variant]['train_in_sample']['auc']:.4f}"])
        txt += "### E. The authors' released models on our April test set\n\n" + md(rows, ["model", "TPR@1e-3", "AUC", "F1 (0.5)", "Acc (0.5)", "AUC on January (they trained on ~70k of it)"])
        txt += "\n"
    roc_plot(res, out, "detect")
    return txt


def roc_plot(res, out, kind):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(os.path.join(out, "plots"), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    i = 0
    for variant in ["bpe50k", "ws50k", "ws50k_legacy"]:
        for regime in ["time", "batches"]:
            f = os.path.join(res, "detect", f"{variant}_{regime}_seed0", "metrics.json")
            if os.path.exists(f):
                m = jl(f)
                ax.plot(C.ROC_GRID, m["test_roc_mean"], color=COLORS[i], ls=STYLES[i], lw=2,
                        label=f"{ {'bpe50k': 'BPE', 'ws50k': 'WS', 'ws50k_legacy': 'WS legacy cleaning'}[variant] } {'time' if regime == 'time' else 'batches'}-matched")
                i += 1
    ax.axvline(1e-3, color="#898782", lw=1, ls=":")
    ax.set_xscale("log"); ax.set_xlim(1e-4, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("Mean ROC of the three CV models, April test set", loc="left", fontsize=11)
    ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(out, "plots", "roc_detection.png"), dpi=160); plt.close(fig)


# ----------------------------------------------------------------------------- B: self-supervised
SSL_LABEL = {"upper": "upper bound (100% supervised)", "lower": "lower bound (20% supervised)", "mlm_theirs": "MLM (authors' multi-hot target)",
             "mlm_bert": "MLM (per-position BERT, ours)", "ar_flatten": "AR, flatten classifier", "ar_lasttoken": "AR, last-token classifier",
             "lower_fullattn": "control: full attention, 20%, no pre-training", "upper_fullattn": "control: full attention, 100%, no pre-training"}


def ssl_section(res, out):
    runs = {}
    for f in glob.glob(os.path.join(res, "ssl", "seed*", "*", "metrics.json")):
        run = f.split(os.sep)[-2]
        runs.setdefault(run, []).append(jl(f))
    if not runs:
        return ""
    txt = "## B. Self-supervised pre-training (paper Sec. 4.5, Fig. 6)\n\n"
    order = [r for r in SSL_LABEL if r in runs]
    ref = {}
    rows = []
    for r in order:
        ms = runs[r]
        tp = np.array([m["test"]["tpr@0.001"] for m in ms])
        ref[r] = tp.mean()
        rows.append([SSL_LABEL[r], len(ms), f"{tp.mean():.4f} ± {tp.std():.4f} ({tp.min():.3f}–{tp.max():.3f})",
                     f"{np.mean([m['test']['tpr@0.01'] for m in ms]):.4f}", f"{np.mean([m['test']['tpr@0.1'] for m in ms]):.4f}",
                     f"{np.mean([m['test']['auc'] for m in ms]):.4f}", f"{np.mean([m['test']['f1@0.5'] for m in ms]):.4f}"])
    txt += md(rows, ["run", "seeds", "TPR @ FPR 1e-3 (mean ± std (min–max))", "TPR @ 1e-2", "TPR @ 1e-1", "AUC", "F1 (0.5)"])
    if "upper" in ref and "lower" in ref:
        txt += f"\nUpper − lower at FPR 1e-3: {100 * (ref['upper'] - ref['lower']):.1f} points (paper: about 15).\n"
        for r in ("ar_flatten", "ar_lasttoken", "mlm_theirs", "mlm_bert"):
            if r in ref:
                txt += f"- {SSL_LABEL[r]}: {100 * (ref['upper'] - ref[r]):.1f} points below the upper bound, {100 * (ref[r] - ref['lower']):+.1f} against the lower bound.\n"
    # ROC (Fig 6 replica)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(os.path.join(out, "plots"), exist_ok=True)
    fig, ax = plt.subplots(figsize=(6.8, 5.0))
    for i, r in enumerate([x for x in ["upper", "ar_flatten", "ar_lasttoken", "lower", "mlm_theirs", "mlm_bert"] if x in runs]):
        roc = np.mean([m["test"]["roc_on_grid"] for m in runs[r]], axis=0)
        ax.plot(C.ROC_GRID, roc, color=COLORS[i], ls=STYLES[i], lw=2, label=SSL_LABEL[r])
    ax.axvline(1e-3, color="#898782", lw=1, ls=":")
    ax.set_xscale("log"); ax.set_xlim(1e-4, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate")
    ax.set_title("Self-supervised pre-training, April test set (mean ROC over seeds)", loc="left", fontsize=10.5)
    ax.grid(alpha=0.3); [ax.spines[s].set_visible(False) for s in ("top", "right")]
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout(); fig.savefig(os.path.join(out, "plots", "fig6_replica.png"), dpi=160); plt.close(fig)
    txt += "\n![Fig 6 replica](plots/fig6_replica.png)\n\n"
    # pre-training losses
    rows = []
    for r in ("mlm_theirs", "mlm_bert", "ar_flatten"):
        for m in runs.get(r, []):
            h = m.get("pretraining", {}).get("epochs", [])
            rows.append([r.replace("ar_flatten", "ar"), m["seed"], " → ".join(f"{e['val_loss']:.3f}" for e in h),
                         f"{m['pretraining']['initial_loss_expected_ln_V']:.2f}"])
    if rows:
        txt += "Validation LM loss per pre-training epoch (a model that guesses uniformly starts at ln V):\n\n" + md(rows, ["pre-training", "seed", "val loss by epoch", "ln V"]) + "\n"
    return txt


# ----------------------------------------------------------------------------- C: classification
def classify_section(res, out):
    rows = []
    for variant in ["bpe50k", "ws50k", "ws50k_legacy"]:
        if variant != "ws50k_legacy":
            rows.append([f"**paper**, {'BPE' if variant == 'bpe50k' else 'Whitespace'}"] + [f"{v:.3f}" for v in PAPER["table9_f1"][variant]] + ["", ""])
        for regime in ["time", "batches"]:
            f = os.path.join(res, "classify", f"classify_{variant}_{regime}_seed0", "metrics.json")
            if os.path.exists(f):
                m = jl(f)
                rows.append([f"ours, {variant.replace('50k', '')} {regime}-matched"] + [f"{v:.3f}" for v in m["test_f1_per_class_mean"]] +
                            [pm(m["test_mean_std"], "f1_macro", 3), pm(m["test_mean_std"], "acc", 3)])
    if len(rows) <= 2:
        return ""
    return "## C. Type classification (paper Table 9; \"Table 12b\" in the journal numbering)\n\n" + \
        md(rows, ["run"] + C.SPEAKEASY_CLASSES + ["macro F1", "accuracy"]) + "\nPer-class F1 on the April test set, mean over the three fold models.\n\n"


# ----------------------------------------------------------------------------- D: ablations
def ablate_section(res, out):
    fs = sorted(glob.glob(os.path.join(res, "ablate", "*", "metrics.json")))
    if not fs:
        return ""
    got = {}
    for f in fs:
        m = jl(f)
        got[(m["variant"], m["seq_len"])] = m
    base = os.path.join(res, "detect", "bpe50k_time_seed0", "metrics.json")
    if os.path.exists(base):
        got[("bpe50k", 512)] = jl(base)
    base = os.path.join(res, "detect", "ws50k_time_seed0", "metrics.json")
    if os.path.exists(base):
        got[("ws50k", 512)] = jl(base)
    base = os.path.join(res, "detect", "ws50k_legacy_time_seed0", "metrics.json")
    if os.path.exists(base):
        got[("ws50k_legacy", 512)] = jl(base)
    txt = "## D. Ablations\n\n"
    rows = []
    for k, name in [(5000, "5k"), (10000, "10k"), (30000, "30k"), (50000, "50k"), (70000, "70k")]:
        m = got.get((f"bpe{name}", 512))
        p = PAPER["table4_val"][k]
        rows.append([f"paper {name}", p[0], p[1], p[2], p[3], "", "", ""])
        if m:
            v, t = m["val_mean_std"], m["test_mean_std"]
            rows.append([f"ours {name}", pm(v, "tpr@0.001", 3), pm(v, "auc", 4), pm(v, "f1@0.5", 4), pm(v, "acc@0.5", 4),
                         pm(t, "tpr@0.001", 3), pm(t, "auc", 4), pm(t, "f1@0.5", 4)])
    txt += "### Vocabulary size (paper Table 4, validation metrics)\n\n" + md(rows, ["BPE vocabulary", "val TPR@1e-3", "val AUC", "val F1", "val Acc", "test TPR@1e-3", "test AUC", "test F1"]) + "\n"
    rows = []
    for n in (64, 128, 256, 512, 1024, 2048):
        m = got.get(("bpe50k", n))
        if m:
            v, t = m["val_mean_std"], m["test_mean_std"]
            rows.append([n, pm(v, "f1@0.5", 4), pm(t, "f1@0.5", 4), pm(t, "tpr@0.001", 3), pm(t, "auc", 4), f"{np.mean([r['batches_seen'] for r in m['folds']]):.0f}"])
    if rows:
        txt += "### Sequence length (paper Fig. 3c: F1 peaks at 512 under a fixed time budget)\n\n" + md(rows, ["N", "val F1", "test F1", "test TPR@1e-3", "test AUC", "batches / fold"]) + "\n"
    rows = []
    for key, name in [("wp50k", "Wordpunct"), ("ws50k", "Whitespace"), ("bpe50k", "BPE")]:
        p = PAPER["table6_test"][key]
        rows.append([f"paper {name}", p[0], p[1], p[2], p[3]])
        for k2, name2 in ([(key, name + (" (pinned-repo cleaning)" if key == "ws50k" else "")), ("ws50k_legacy", "Whitespace (legacy cleaning)")]
                          if key == "ws50k" else [(key, name)]):
            m = got.get((k2, 512))
            if m:
                t = m["test_mean_std"]
                rows.append([f"ours {name2}", pm(t, "tpr@0.001", 4), pm(t, "auc", 4), pm(t, "f1@0.5", 4), pm(t, "acc@0.5", 4)])
    txt += "### Tokenizer (paper Table 6, test metrics)\n\n" + md(rows, ["", "TPR@1e-3", "AUC", "F1", "Acc"]) + "\n"
    return txt


def pool_seeds(res, out):
    """Merge the fold models of every seed of a configuration (detect/, classify/, ablate/) into one metrics file named
    <stem>_seed0, in <out>/_pooled, so that the sections below read one record per configuration."""
    import re
    import shutil
    from baseline import cv
    root = os.path.join(out, "_pooled")
    shutil.rmtree(root, ignore_errors=True)
    for kind in ["detect", "classify", "ablate"]:
        groups = {}
        for f in glob.glob(os.path.join(res, kind, "*", "metrics.json")):
            stem = re.sub(r"_seed\d+$", "", os.path.basename(os.path.dirname(f)))
            groups.setdefault(stem, []).append(f)
        for stem, fs in groups.items():
            ms = [jl(f) for f in sorted(fs)]
            merged = ms[0]
            merged["folds"] = sum([m["folds"] for m in ms], [])
            merged["seeds"] = sorted(m["seed"] for m in ms)
            cv.aggregate(merged, merged["task"])
            C.dump_json(merged, os.path.join(root, kind, f"{stem}_seed0", "metrics.json"))
    if os.path.exists(os.path.join(res, "released", "metrics.json")):
        os.makedirs(os.path.join(root, "released"), exist_ok=True)
        shutil.copy(os.path.join(res, "released", "metrics.json"), os.path.join(root, "released", "metrics.json"))
    return root


def long_section(a):
    """B2: longer pre-training (needs results/B_selfsup_long/bootstrap.json from baseline.long_stats)."""
    first, long = os.path.join(a.published, "B_selfsup"), os.path.join(a.published, "B_selfsup_long")
    if not os.path.exists(os.path.join(long, "bootstrap.json")):
        return ""
    from baseline import report_long
    return report_long.section(first, long, a.out)


def gap_section(a):
    """F: closing the gap to the released model (results/F_gap/final_table.md written by baseline.gap_final)."""
    p = os.path.join(a.published, "F_gap", "final_table.md")
    if not os.path.exists(p):
        return ""
    return ("## F. Closing the gap to the released model: baseline v2 (follow-up; REPRODUCTION_REPORT.md 5.7)\n\n" + open(p).read() +
            "\n\n![logit histograms](plots/gap_logit_hist.png)\n\n![validation curves](plots/gap_val_curves.png)\n\n![ROC](plots/gap_roc.png)\n")


def b3_section(a):
    """B3: Fig. 6 with the v2 recipe (results/B3_selfsup_v2/tables.md written by baseline.b3_report)."""
    p = os.path.join(a.published, "B3_selfsup_v2", "tables.md")
    if not os.path.exists(p):
        return ""
    return ("## B3. Self-supervised pre-training with the baseline-v2 recipe (follow-up; REPRODUCTION_REPORT.md 5.2c)\n\n" + open(p).read() +
            "\n\n![Fig 6 v2](plots/fig6_v2.png)\n\n![validation curves](plots/b3_val_curves.png)\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--published", default="results", help="folder with B_selfsup/ and B_selfsup_long/ (the committed results)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pooled = pool_seeds(a.results, a.out)
    parts = [detection(pooled, a.out), ssl_section(a.results, a.out), long_section(a), b3_section(a), gap_section(a), classify_section(pooled, a.out), ablate_section(pooled, a.out)]
    with open(os.path.join(a.out, "tables.md"), "w") as f:
        f.write("# Baseline reproduction: tables (generated by baseline/report.py)\n\n" + "\n".join(p for p in parts if p))
    print("wrote", os.path.join(a.out, "tables.md"))


if __name__ == "__main__":
    main()
