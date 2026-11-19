#!/usr/bin/env python
"""
Item 1 of results/robustness: the graded edits of results/pooling_v2/graded_edits.md on the RELEASED Nebula weights,
next to A and C of regime J (all of January; A 1 epoch, C 10 epochs; 10 seeds each).

    python scripts/robustness/graded_edits_released.py --src-j <regime J output> --work <token cache folder>

Edits (same tokens as pooling_v2, read from the cache graded_tokens_17402.npz written by scripts/pooling_v2/graded_edits.py):
insert k / prepend k (k = 1, 5, 20, 50) API calls, each a copy of a call of the SAME report; first 512 tokens.
TPR fixed (a): malware caught at the threshold that gave 1% FPR on the ORIGINAL (unedited) April benign scores of that model;
the threshold is not recomputed after the edit. FPR fixed (a): benign reports flagged at that threshold after the same edit.
"Fits": only reports whose whole edited token sequence is at most 512 tokens, so no original call leaves the window.
Intervals: group bootstrap over April hash_apis (1,000 resamples, seed 0, paired across models) for the TPR change;
seed-paired bootstrap over the 10 seeds for C - A.
Writes results/robustness/graded_edits.md and graded_edits.json; model logits are cached in --work.
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
sys.path.insert(0, os.path.join(HERE, "..", "pooling_v2"))
import common as C  # noqa: E402
from hier_nebula.model import build_level1  # noqa: E402
from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL  # noqa: E402
from perturb_check import logits  # noqa: E402

KS = [1, 5, 20, 50]
EDITS = [f"insert {k}" for k in KS] + [f"prepend {k}" for k in KS]
OUT = "results/robustness"
SEEDS = list(range(10))
EPOCHS_J = {"A": 1, "C": 10}


def auc(y, s):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, s))


def score_all(model, X, plain):
    """logits of the unedited and the 8 edited versions: [9, N]."""
    return np.stack([logits(model, plain.astype(np.int64))] + [logits(model, X[j].astype(np.int64)) for j in range(len(EDITS))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-j", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--nebula", default="../nebula")
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    y = test.label.values
    N = len(test)
    d = np.load(os.path.join(a.work, f"graded_tokens_{N}.npz")); X, L = d["X"], d["L"]
    plain = np.load(os.path.join(a.work, f"perturbed_tokens_{N}.npz"))["plain"]
    fits = L <= 512                                                   # [8, N]
    cache = os.path.join(a.work, "robustness_item1_logits.npz")
    Z = {}
    if os.path.exists(cache):
        z = np.load(cache)
        Z = {k: z[k] for k in z.files}
    else:
        t0 = time.time()
        rel = build_level1(a.nebula, vocab_size=50001, pretrained=True).eval()
        Z["released"] = score_all(rel, X, plain)
        ref = C.load_scores("nebula", "april")[0].loc[test.row.values].values
        sig = 1 / (1 + np.exp(-Z["released"][0]))
        print(f"released: max |sigmoid(CPU logit) - stored score| = {np.abs(sig - ref).max():.2e} ({time.time() - t0:.0f}s)", flush=True)
        for v in ("A", "C"):
            for s in SEEDS:
                run = f"{v}_all_s{s}"
                m = build_variant(a.nebula, V2_TO_INTERNAL[v]).eval()
                m.load_state_dict(torch.load(os.path.join(a.src_j, "ckpt", run, "final.pt"), map_location="cpu", weights_only=True))
                Z[f"{v}_s{s}"] = score_all(m, X, plain)
                kg = np.load(os.path.join(a.src_j, "scores", f"{run}_epochs.npz"))["april"][EPOCHS_J[v] - 1]
                assert np.abs(Z[f"{v}_s{s}"][0] - kg).max() < 0.05, run
                print(run, f"{time.time() - t0:.0f}s", flush=True)
        np.savez(cache, **Z)

    mal, ben = y == 1, y == 0
    names = ["released Nebula", "A (J)", "C (J)"]
    keys = {"released Nebula": ["released"], "A (J)": [f"A_s{s}" for s in SEEDS], "C (J)": [f"C_s{s}" for s in SEEDS]}
    rows_all, rows_fit, det = [], [], {}
    # per model: [seeds, 9, N] logits; thresholds from the unedited scores of each seed
    per = {n: np.stack([Z[k] for k in keys[n]]) for n in names}
    flags, fpr_flags = {}, {}
    for n in names:
        thr = np.array([C.thr_from(y, per[n][i, 0], 0.01) for i in range(len(keys[n]))])
        f = per[n] > thr[:, None, None]                              # [seeds, 9, N] flagged
        flags[n] = f.mean(0)                                         # mean over seeds, [9, N]
    res = {}
    for n in names:
        res[n] = {"auc": np.array([[auc(y, per[n][i, e]) for e in range(9)] for i in range(len(keys[n]))]),
                  "tpr": np.array([[flags[n][e][mal].mean()] for e in range(9)]).ravel(),
                  "fpr": np.array([flags[n][e][ben].mean() for e in range(9)])}
    labels = ["original"] + EDITS
    for e, lab in enumerate(labels):
        r = {"edit": lab}
        for n in names:
            r[f"{n} AUC"] = f"{res[n]['auc'][:, e].mean():.4f}"
        for n in names:
            r[f"{n} TPR fixed (a)"] = f"{100 * res[n]['tpr'][e]:.1f}%"
        for n in names:
            r[f"{n} FPR fixed (a)"] = f"{100 * res[n]['fpr'][e]:.2f}%"
        rows_all.append(r)
        if e == 0:
            continue
        f = fits[e - 1]
        r2 = {"edit": lab, "reports that fit (malware)": f"{int(f.sum()):,} ({int(y[f].sum()):,})"}
        for n in names:
            b, aft = flags[n][0][mal & f].mean(), flags[n][e][mal & f].mean()
            r2[f"{n} TPR fixed (a) before → after"] = f"{100 * b:.1f}% → {100 * aft:.1f}%"
        for n in names:
            aucs_b = np.mean([auc(y[f], per[n][i, 0][f]) for i in range(len(keys[n]))])
            aucs_a = np.mean([auc(y[f], per[n][i, e][f]) for i in range(len(keys[n]))])
            r2[f"{n} AUC before → after"] = f"{aucs_b:.4f} → {aucs_a:.4f}"
        rows_fit.append(r2)

    # group bootstrap of the TPR change (after - before), all reports and the restricted case
    wi = list(C.group_weights_boot(test.hash_apis.values, 1000, 0))
    W = np.stack(wi)                                                 # [1000, N]
    def wtpr(fl, mask):
        m = (mask & mal).astype(float)
        return (W @ (fl * m)) / (W @ m)
    chg = {}
    for n in names:
        for e in range(1, 9):
            chg[(n, e, "all")] = wtpr(flags[n][e], np.ones(N, bool)) - wtpr(flags[n][0], np.ones(N, bool))
            chg[(n, e, "fit")] = wtpr(flags[n][e], fits[e - 1]) - wtpr(flags[n][0], fits[e - 1])
    ci = lambda v: f"[{100 * np.percentile(v, 2.5):+.1f}, {100 * np.percentile(v, 97.5):+.1f}]"
    rows_chg = []
    for e in range(1, 9):
        r = {"edit": labels[e]}
        for n in names:
            r[f"{n}: change in TPR, points [group 95%]"] = f"{100 * (flags[n][e][mal].mean() - flags[n][0][mal].mean()):+.1f} {ci(chg[(n, e, 'all')])}"
        for a_, b_ in (("A (J)", "released Nebula"), ("C (J)", "released Nebula"), ("C (J)", "A (J)")):
            v = chg[(a_, e, "all")] - chg[(b_, e, "all")]
            r[f"{a_} − {b_}"] = f"{100 * (flags[a_][e][mal].mean() - flags[a_][0][mal].mean() - flags[b_][e][mal].mean() + flags[b_][0][mal].mean()):+.1f} {ci(v)}"
        rows_chg.append(r)
    rows_chg_fit = []
    for e in range(1, 9):
        f = fits[e - 1]
        r = {"edit": labels[e]}
        for n in names:
            r[f"{n}: change in TPR, points [group 95%]"] = f"{100 * (flags[n][e][mal & f].mean() - flags[n][0][mal & f].mean()):+.1f} {ci(chg[(n, e, 'fit')])}"
        for a_, b_ in (("A (J)", "released Nebula"), ("C (J)", "released Nebula"), ("C (J)", "A (J)")):
            v = chg[(a_, e, "fit")] - chg[(b_, e, "fit")]
            r[f"{a_} − {b_}"] = f"{100 * (flags[a_][e][mal & f].mean() - flags[a_][0][mal & f].mean() - flags[b_][e][mal & f].mean() + flags[b_][0][mal & f].mean()):+.1f} {ci(v)}"
        rows_chg_fit.append(r)
    # seed-paired C - A
    rng = np.random.default_rng(0)
    seedrows = []
    for e in range(1, 9):
        def tprs(v, e_, sel):
            return np.array([((per[v][i, e_] > C.thr_from(y, per[v][i, 0], 0.01))[mal & sel]).mean() for i in range(10)])
        for tag, sel in (("all reports", np.ones(N, bool)), ("reports that fit", fits[e - 1])):
            dA = 100 * (tprs("A (J)", e, sel) - tprs("A (J)", 0, sel)); dC = 100 * (tprs("C (J)", e, sel) - tprs("C (J)", 0, sel))
            x = dC - dA; b = rng.choice(x, (20000, 10)).mean(1)
            seedrows.append({"edit": labels[e], "set": tag, "A (J) change, points": f"{dA.mean():+.1f}", "C (J) change": f"{dC.mean():+.1f}",
                             "C − A, seed-paired [95% over seeds]": f"{x.mean():+.1f} [{np.percentile(b, 2.5):+.1f}, {np.percentile(b, 97.5):+.1f}]"})
    json.dump({"tpr": {n: res[n]["tpr"].tolist() for n in names}, "fpr": {n: res[n]["fpr"].tolist() for n in names},
               "auc": {n: res[n]["auc"].mean(0).tolist() for n in names}, "labels": labels}, open(f"{OUT}/graded_edits.json", "w"), indent=1)
    md = ["# Item 1: graded edits on the released Nebula weights, next to A and C of regime J\n",
          __doc__.split("Edits (same tokens")[0].strip().split("\n", 1)[1] if False else "",
          "Edits: insert k / prepend k calls (k = 1, 5, 20, 50), each a copy of a call of the same report, first 512 tokens (the tokens of "
          "`results/pooling_v2/graded_edits.md`). TPR fixed (a): malware caught at the threshold that gave 1% FPR on the unedited April "
          "benign scores of that model, not recomputed after the edit; FPR fixed (a): benign reports flagged at that threshold after the "
          "same edit. A (J) and C (J): mean over 10 seeds. Released Nebula: the published weights.\n",
          "## All April reports\n", C.md_table(pd.DataFrame(rows_all)),
          "\n## Only reports whose whole edited sequence fits in 512 tokens (no original call leaves the window)\n", C.md_table(pd.DataFrame(rows_fit)),
          "\n## Change in malware TPR at the fixed threshold, with group-bootstrap intervals (all reports)\n", C.md_table(pd.DataFrame(rows_chg)),
          "\n## The same change on the reports that fit in 512 tokens\n", C.md_table(pd.DataFrame(rows_chg_fit)),
          "\n## C (J) versus A (J), seed-paired\n", "Bootstrap over the 10 seeds only.\n", C.md_table(pd.DataFrame(seedrows))]
    open(f"{OUT}/graded_edits.md", "w").write("\n".join(m for m in md if m != ""))
    print(C.md_table(pd.DataFrame(rows_all))); print(C.md_table(pd.DataFrame(rows_fit)))


if __name__ == "__main__":
    main()
