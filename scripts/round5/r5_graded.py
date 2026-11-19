#!/usr/bin/env python
"""
Round 5, item 5 (copied calls): the graded edits of results/robustness item 1 / results/pooling_v4 for the 10-seed models.

    python scripts/round5/r5_graded.py [--models released,A,C,C2,ATTbal,MMbal,Cbal]

Every April report (17,402) is edited in memory (nothing but scores is saved): insert k / prepend k calls (k = 1, 5, 20, 50), each a copy of a call of the SAME report
(the same edits and random seeds as scripts/pooling_v2/graded_edits.py), re-tokenised, first 512 tokens. Thresholds fixed at 1% and 0.1% FPR on the unedited April
benign scores of each model and seed. "Fits": the whole edited sequence is at most 512 tokens. Intervals: group bootstrap over April hash_apis (1,000 resamples) and
seed-paired. Writes results/round5/graded_edits.md/json.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "pooling_v2"))
import r5_common as R  # noqa: E402
from r5_common import C, V, _W, _init  # noqa: E402
from perturb_check import insert_calls  # noqa: E402
from graded_edits import prepend_calls  # noqa: E402

KS = V.KS
EDITS = V.EDITS


def _tok(row):
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    apis = list(rep.get("apis") or [])
    out, lens = [], []
    for k in KS:
        r = dict(rep); r["apis"] = insert_calls(apis, row, k); t = nb.ids(r)
        out.append(np.asarray(t[:512], dtype=np.uint16)); lens.append(len(t))
    for k in KS:
        r = dict(rep); r["apis"] = prepend_calls(apis, row, k); t = nb.ids(r)
        out.append(np.asarray(t[:512], dtype=np.uint16)); lens.append(len(t))
    return int(row), out, lens


def legacy(key, s):
    """scores of round 3/4 caches for the same models and edits ([9, N]) or None."""
    z = os.path.join(V.WORK, "robustness_item1_logits.npz")
    if key == "released" and os.path.exists(z):
        return np.load(z)["released"]
    if key in ("A", "C") and s < 5 and os.path.exists(z):
        d = np.load(z)
        return d[f"{key}_s{s}"] if f"{key}_s{s}" in d.files else None
    if key == "C2" and s < 5:
        p = os.path.join(V.WORK, f"v4_item1_logits_C_all_s{s}.npz".replace("C_all", "C2_all"))
        if os.path.exists(p):
            return np.load(p)["z"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="released,A,C,C2,ATTbal,MMbal,Cbal")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="graded_edits")
    a = ap.parse_args()
    R.n_threads()
    test, y = V.april()
    N = len(test)
    keys = a.models.split(",")
    models = R.models_for(keys, {k: list(range(1 if k == "released" else a.seeds)) for k in keys})
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(R.NEBULA,)) as pool:
        res = list(pool.imap(_tok, test.row.values, chunksize=32))
    toks = [[r[1][j] for r in res] for j in range(8)]
    L = np.array([r[2] for r in res]).T
    print(f"tokenised the copied-call edits of {N:,} reports in {time.time() - t0:.0f}s", flush=True)
    fits = L <= 512
    labels = ["unedited"] + EDITS
    Zs = {}
    for disp, (key, seeds) in models.items():
        for s in seeds:
            path = os.path.join(R.WORK5, f"graded_{key}_s{s}.npz")
            if os.path.exists(path):
                Zs[(disp, s)] = np.load(path)["z"]; continue
            lg = legacy(key, s)
            if lg is not None and lg.shape == (9, N):
                Zs[(disp, s)] = lg; np.savez(path, z=lg); continue
            m, w, z0 = R.load_model(key, s)
            z = np.stack([z0] + [R.score_tokens(m, w, toks[j]) for j in range(8)])
            np.savez(path, z=z); Zs[(disp, s)] = z
            print(f"  scored {disp} s{s} ({time.time() - t0:.0f}s)", flush=True)
    mal, ben = y == 1, y == 0
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))
    wt = lambda fl, mask: (W @ (fl * (mask & mal))) / (W @ (mask & mal).astype(float))
    wb = lambda fl: (W @ (fl * ben)) / (W @ ben.astype(float))
    ci = lambda v: f"[{100 * np.percentile(v, 2.5):+.1f}, {100 * np.percentile(v, 97.5):+.1f}]"
    from sklearn.metrics import roc_auc_score
    md = ["# Copied-call edits, 10-seed models (round 5, item 5)\n",
          "Insert k / prepend k calls (k = 1, 5, 20, 50), each a copy of a call of the same report, first 512 tokens (the edits of `results/robustness` item 1). Thresholds fixed at 1% and 0.1% "
          "FPR on the unedited April benign scores of each model and seed; mean over seeds (released: one model). Group-bootstrap 95% intervals over April `hash_apis`; edited reports exist in memory only.\n"]
    js = {"labels": labels, "seeds": {d: len(s) for d, (k, s) in models.items()}, "share_fit512": fits.mean(1).tolist()}
    seedflags = {}
    for f, ftag in ((0.01, "1%"), (0.001, "0.1%")):
        flags = {}
        for disp, (key, seeds) in models.items():
            fl = []
            for s in seeds:
                z = Zs[(disp, s)]; thr = C.thr_from(y, z[0], f)
                fl.append((z > thr).astype(float))                                  # [9, N]
            flags[disp] = np.mean(fl, 0); seedflags[(f, disp)] = fl
        t_tpr, t_fpr, t_all, t_fit = [], [], [], []
        for disp in models:
            fl = flags[disp]
            t_tpr.append({"model": disp, **{labels[e]: f"{100 * fl[e][mal].mean():.1f}%" for e in range(9)}})
            t_fpr.append({"model": disp, **{labels[e]: f"{100 * fl[e][ben].mean():.2f}%" for e in range(9)}})
            allm = np.ones(N, bool)
            t_all.append({"model": disp, **{labels[e]: f"{100 * (fl[e][mal].mean() - fl[0][mal].mean()):+.1f} {ci(wt(fl[e], allm) - wt(fl[0], allm))}" for e in range(1, 9)}})
            t_fit.append({"model": disp, **{labels[e]: f"{100 * fl[0][mal & fits[e - 1]].mean():.1f}% → {100 * fl[e][mal & fits[e - 1]].mean():.1f}%; "
                                                       f"{100 * (fl[e][mal & fits[e - 1]].mean() - fl[0][mal & fits[e - 1]].mean()):+.1f} {ci(wt(fl[e], fits[e - 1]) - wt(fl[0], fits[e - 1]))}" for e in range(1, 9)}})
            js.setdefault(f"tpr{ftag}", {})[disp] = [float(fl[e][mal].mean()) for e in range(9)]
            js.setdefault(f"fpr{ftag}", {})[disp] = [float(fl[e][ben].mean()) for e in range(9)]
        md += [f"\n## Threshold of {ftag} FPR: malware TPR after the edit (all April malware)\n", C.md_table(pd.DataFrame(t_tpr)),
               f"\nBenign FPR after the same edit of the benign reports (all April benign)\n", C.md_table(pd.DataFrame(t_fpr)),
               f"\nChange in malware TPR, points [group 95%], all reports\n", C.md_table(pd.DataFrame(t_all)),
               f"\nReports that fit in 512 tokens after the edit: TPR before → after; change in points [group 95%]\n", C.md_table(pd.DataFrame(t_fit))]
        ref = "ATT+bal"
        if ref in models:
            rows, rows_s = [], []
            rng = np.random.default_rng(0)
            for other in models:
                if other == ref:
                    continue
                r, rs = {"difference": f"{ref} − {other}"}, {"difference": f"{ref} − {other}"}
                for e in range(1, 9):
                    fx, fz = flags[ref], flags[other]
                    pt = (fx[e][mal].mean() - fx[0][mal].mean()) - (fz[e][mal].mean() - fz[0][mal].mean())
                    dd = (wt(fx[e], np.ones(N, bool)) - wt(fx[0], np.ones(N, bool))) - (wt(fz[e], np.ones(N, bool)) - wt(fz[0], np.ones(N, bool)))
                    r[labels[e]] = f"{100 * pt:+.1f} {ci(dd)}"
                    sx, sz = seedflags[(f, ref)], seedflags[(f, other)]
                    if len(sx) > 1 and len(sz) > 1:
                        n = min(len(sx), len(sz))
                        d = 100 * (np.array([x[e][mal].mean() - x[0][mal].mean() for x in sx[:n]]) - np.array([x[e][mal].mean() - x[0][mal].mean() for x in sz[:n]]))
                        b = rng.choice(d, (20000, len(d))).mean(1)
                        rs[labels[e]] = f"{d.mean():+.1f} [{np.percentile(b, 2.5):+.1f}, {np.percentile(b, 97.5):+.1f}]"
                rows.append(r)
                if len(rs) > 1:
                    rows_s.append(rs)
            md += [f"\n## Threshold of {ftag} FPR: ATT+bal against each model, difference in the change of malware TPR (points, group 95%)\n", C.md_table(pd.DataFrame(rows))]
            if rows_s:
                md += ["\nSeed-paired (95% over the seeds)\n", C.md_table(pd.DataFrame(rows_s))]
    auc = {d: np.mean([[roc_auc_score(y, Zs[(d, s)][e]) for e in range(9)] for s in seeds], 0) for d, (k, seeds) in models.items()}
    md += ["\n## AUC of the edited April set (threshold-free)\n", C.md_table(pd.DataFrame([{"model": d, **{labels[e]: f"{auc[d][e]:.4f}" for e in range(9)}} for d in models]))]
    js["auc"] = {d: v.tolist() for d, v in auc.items()}
    open(f"{R.OUT}/{a.out}.md", "w").write("\n".join(md))
    json.dump(js, open(f"{R.OUT}/{a.out}.json", "w"), indent=1)
    print(C.md_table(pd.DataFrame(t_tpr)))


if __name__ == "__main__":
    main()
