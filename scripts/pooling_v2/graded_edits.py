#!/usr/bin/env python
"""
Graded edit test for the pooling_v2 models (results/pooling_v2/graded_edits.md): how fast does detection fall as
more API calls are added, and does it matter WHERE they are added?

    python scripts/pooling_v2/graded_edits.py --src <regime S output> --work <cache folder>

Edits of the filtered report of every April report (then Nebula's tokenizer, first 512 tokens):
  insert k  : k extra API calls at random places (k = 1, 5, 20, 50)
  prepend k : k extra API calls put before the first call (k = 1, 5, 20, 50); this shifts every later token
Every added call is a copy of a call of the SAME report (no new API names or arguments are introduced), chosen at
random (numpy Generator; seeds 2000 + row for insert, 3000 + row for prepend). Reports without API calls stay as is.

Reported per model (checkpoint chosen on validation AUC, 10 seeds):
  AUC                         all April reports edited
  TPR@1% fixed (a)            malware caught at the threshold that gave 1% FPR on the ORIGINAL April benign scores;
                              the threshold is not recomputed, as for a deployed model facing edited malware
  FPR fixed (a)               benign reports flagged at that same threshold after the same edit
  TPR@1% fixed (b), FPR (b)   the same with the January-validation threshold
  "fits" columns              only reports whose whole edited token sequence is at most 512 tokens (nothing is
                              pushed out of the window), before and after
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "go_no_go"))
import common as C  # noqa: E402

from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL  # noqa: E402
from perturb_check import insert_calls, pad, logits  # noqa: E402

KS = [1, 5, 20, 50]
EDITS = [f"insert {k}" for k in KS] + [f"prepend {k}" for k in KS]
_W = {}


def _init(nebula):
    from measure_lengths import Nebula
    _W["nb"] = Nebula(nebula)
    _W["reps"] = C.Reps()


def prepend_calls(apis, row, k):
    n = len(apis)
    if n == 0:
        return list(apis)
    rng = np.random.default_rng(3000 + int(row))
    return [apis[int(i)] for i in rng.integers(0, n, k)] + list(apis)


def _tok(row):
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    apis = list(rep.get("apis") or [])
    out, lens = [], []
    for k in KS:
        r = dict(rep); r["apis"] = insert_calls(apis, row, k)
        t = nb.ids(r); out.append(np.asarray(t[:512], dtype=np.int32)); lens.append(len(t))
    for k in KS:
        r = dict(rep); r["apis"] = prepend_calls(apis, row, k)
        t = nb.ids(r); out.append(np.asarray(t[:512], dtype=np.int32)); lens.append(len(t))
    return int(row), out, lens


def auc(y, s):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, s))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--variants", default="A,B,C")
    ap.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    rows = test.row.values[:a.limit] if a.limit else test.row.values
    y = test.label.values[:len(rows)]
    yv = val.label.values
    cache = os.path.join(a.work, f"graded_tokens_{len(rows)}.npz")
    if os.path.exists(cache):
        d = np.load(cache)
        X, L = d["X"], d["L"]
    else:
        t0 = time.time()
        with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
            res = list(pool.imap(_tok, rows, chunksize=32))
        assert [r[0] for r in res] == list(rows)
        X = np.stack([pad([r[1][j] for r in res]) for j in range(len(EDITS))]).astype(np.int32)     # [edits, N, 512]
        L = np.array([r[2] for r in res]).T                                                          # [edits, N]
        os.makedirs(a.work, exist_ok=True)
        np.savez(cache, X=X, L=L)
        print(f"tokenised {len(rows):,} reports under {len(EDITS)} edits in {time.time() - t0:.0f}s", flush=True)
    plain = np.load(os.path.join(a.work, f"perturbed_tokens_{len(test)}.npz"))["plain"][:len(rows)]
    # the 5-call insertion must be the same edit as in perturb_check.py
    chk = np.load(os.path.join(a.work, f"perturbed_tokens_{len(test)}.npz"))["ins"][:len(rows)]
    assert np.array_equal(chk, X[EDITS.index("insert 5")]), "insert 5 differs from perturb_check.py"
    fits = L <= 512
    info = {e: {"changed": float(np.mean((X[j] != plain).any(1))), "fits": int(fits[j].sum()), "fits_malware": int(y[fits[j]].sum())}
            for j, e in enumerate(EDITS)}
    print(json.dumps(info), flush=True)

    out = {"edits": info, "runs": {}}
    for v in a.variants.split(","):
        for s in [int(x) for x in a.seeds.split(",")]:
            run = f"{v}_s{s}"
            ep = json.load(open(os.path.join(a.src, "logs", f"{run}.json")))["epoch_by_val_auc"]
            npz = np.load(os.path.join(a.src, "scores", f"{run}_epochs.npz"))
            z0, zv = npz["april"][ep - 1][:len(rows)], npz["janval"][ep - 1]
            m = build_variant(a.nebula, V2_TO_INTERNAL[v]).eval()
            m.load_state_dict(torch.load(os.path.join(a.src, "ckpt", run, "best_auc.pt"), map_location="cpu", weights_only=True))
            ta, tb = C.thr_from(y, z0, 0.01), C.thr_from(yv, zv, 0.01)
            mal, ben = y == 1, y == 0
            r = {"epoch": ep, "original": {"auc": auc(y, z0), "tpr_fix_a": float((z0[mal] > ta).mean()), "fpr_fix_a": float((z0[ben] > ta).mean()),
                                           "tpr_fix_b": float((z0[mal] > tb).mean()), "fpr_fix_b": float((z0[ben] > tb).mean())}}
            for j, e in enumerate(EDITS):
                z = logits(m, X[j].astype(np.int64))
                f = fits[j]
                r[e] = {"auc": auc(y, z), "tpr_fix_a": float((z[mal] > ta).mean()), "fpr_fix_a": float((z[ben] > ta).mean()),
                        "tpr_fix_b": float((z[mal] > tb).mean()), "fpr_fix_b": float((z[ben] > tb).mean()),
                        "fits_auc_before": auc(y[f], z0[f]), "fits_auc_after": auc(y[f], z[f]),
                        "fits_tpr_fix_a_before": float((z0[f & mal] > ta).mean()), "fits_tpr_fix_a_after": float((z[f & mal] > ta).mean()),
                        "mean_logit_change_malware": float((z[mal] - z0[mal]).mean()), "mean_logit_change_benign": float((z[ben] - z0[ben]).mean())}
            out["runs"][run] = r
            print(f"{run}: TPR fixed (a) {100 * r['original']['tpr_fix_a']:.1f}% | " +
                  " | ".join(f"{e} {100 * r[e]['tpr_fix_a']:.1f}%" for e in EDITS), flush=True)
            json.dump(out, open("results/pooling_v2/graded_edits.json" if not a.limit else "results/pooling_v2/graded_edits_debug.json", "w"), indent=1)

    # ---- summary tables
    vs = a.variants.split(",")
    seeds = [int(x) for x in a.seeds.split(",")]
    g = lambda v, e, k: np.array([out["runs"][f"{v}_s{s}"][e][k] for s in seeds])
    rng = np.random.default_rng(0)

    def boot(x):
        b = rng.choice(x, (20000, len(x))).mean(1)
        return x.mean(), np.percentile(b, [2.5, 97.5])
    t1, t2, t3 = [], [], []
    for e in ["original"] + EDITS:
        r1 = {"edit": e}
        for v in vs:
            r1[f"{v} AUC"] = f"{g(v, e, 'auc').mean():.4f}"
        for v in vs:
            r1[f"{v} TPR fixed (a)"] = f"{100 * g(v, e, 'tpr_fix_a').mean():.1f}%"
        for v in vs:
            r1[f"{v} FPR fixed (a)"] = f"{100 * g(v, e, 'fpr_fix_a').mean():.2f}%"
        for v in vs:
            r1[f"{v} TPR fixed (b)"] = f"{100 * g(v, e, 'tpr_fix_b').mean():.1f}%"
        t1.append(r1)
        if e == "original":
            continue
        r2 = {"edit": e, "reports that fit (malware)": f"{info[e]['fits']:,} ({info[e]['fits_malware']:,})"}
        for v in vs:
            r2[f"{v} AUC before → after"] = f"{g(v, e, 'fits_auc_before').mean():.4f} → {g(v, e, 'fits_auc_after').mean():.4f}"
        for v in vs:
            r2[f"{v} TPR fixed (a) before → after"] = (f"{100 * g(v, e, 'fits_tpr_fix_a_before').mean():.1f}% → "
                                                        f"{100 * g(v, e, 'fits_tpr_fix_a_after').mean():.1f}%")
        t2.append(r2)
        if "A" in vs and "C" in vs:
            dA = 100 * (g("A", e, "tpr_fix_a") - g("A", "original", "tpr_fix_a"))
            dC = 100 * (g("C", e, "tpr_fix_a") - g("C", "original", "tpr_fix_a"))
            mu, ci = boot(dC - dA)
            fA = 100 * (g("A", e, "fits_tpr_fix_a_after") - g("A", e, "fits_tpr_fix_a_before"))
            fC = 100 * (g("C", e, "fits_tpr_fix_a_after") - g("C", e, "fits_tpr_fix_a_before"))
            mu2, ci2 = boot(fC - fA)
            t3.append({"edit": e, "A: change in TPR fixed (a), points": f"{dA.mean():+.1f}", "C": f"{dC.mean():+.1f}",
                       "C − A [95% over seeds]": f"{mu:+.1f} [{ci[0]:+.1f}, {ci[1]:+.1f}]",
                       "reports that fit: A": f"{fA.mean():+.1f}", "reports that fit: C": f"{fC.mean():+.1f}",
                       "reports that fit: C − A": f"{mu2:+.1f} [{ci2[0]:+.1f}, {ci2[1]:+.1f}]"})
    md = ["# Follow-up: graded edits (insert or prepend k API calls)\n", __doc__.split("Edits of the filtered report")[1].split("Reported per model")[0].strip().join(
          ["Edits of the filtered report ", "\n"]),
          "Regime S, 10 seeds, checkpoint chosen on validation AUC. \"TPR fixed (a)\": malware caught at the threshold that gave 1% FPR "
          "on the original April benign scores (not recomputed after the edit); \"FPR fixed (a)\": benign reports flagged at that "
          "threshold after the same edit; (b): the January-validation threshold. Means over seeds.\n",
          "## All April reports\n", C.md_table(pd.DataFrame(t1)),
          "\n## Only reports whose whole edited sequence fits in 512 tokens (nothing pushed out of the window)\n", C.md_table(pd.DataFrame(t2)),
          "\n## Change in malware TPR at the fixed threshold (a): C versus A, seed-paired\n",
          "Intervals from a bootstrap over the 10 seeds only.\n", C.md_table(pd.DataFrame(t3))]
    if not a.limit:
        open("results/pooling_v2/graded_edits.md", "w").write("\n".join(md))
    print("\n".join(md[3:]))


if __name__ == "__main__":
    main()
