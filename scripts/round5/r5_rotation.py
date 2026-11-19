#!/usr/bin/env python
"""
Round 5, item 4: rotation check. Every April report (17,402; malware and benign) is rotated in memory (nothing is saved but scores):

  (a) inside the window: the real tokens of the model's window (first 512 tokens, or 4,096 for the whole-report models) are rotated at a
      call boundary (the call start nearest to the fraction), so the last calls of the window come first. A position test: the tokens
      are the same, only their order differs.
  (b) whole report: the full call list is rotated by the fraction (calls[r:] + calls[:r]), the report is re-tokenised and the first 512
      (or 4,096) tokens are taken. A "where is the signal" test: the window sees different calls.
Fractions 25%, 50%, 75%. Thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed.
Subsets: all reports, reports whose whole token sequence fits in 512 tokens (no call leaves the window: (a) and (b) only reorder),
reports longer than 512 tokens. Intervals: group bootstrap over April hash_apis (1,000 resamples); seed-paired differences.

    python scripts/round5/r5_rotation.py --models released,A,C,F,ATTbal [--seeds-old 5 --seeds-new 10 --seeds-f 3]
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
import r5_common as R  # noqa: E402
from r5_common import C, V, _W, _init  # noqa: E402

FR = [0.25, 0.5, 0.75]
LABELS = [f"{k} {int(100 * f)}%" for k in ("window", "whole") for f in FR]


def _rot(row):
    from measure_links import call_positions
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    full = np.asarray(nb.ids(rep), dtype=np.int32)
    try:
        starts, lens, n_tok, fallback, head = call_positions(nb, rep)
    except Exception:
        starts, fallback = np.zeros(0, dtype=np.int64), True
    a512, a4k, b4k = [], [], []
    for f in FR:
        for L, dst in ((512, a512), (4096, a4k)):
            win = full[:L]
            n = len(win)
            st = np.asarray(starts)[np.asarray(starts) < n] if (not fallback and len(starts)) else np.zeros(0, dtype=np.int64)
            if len(st) < 2:
                dst.append(win.astype(np.uint16))
                continue
            b = int(st[np.argmin(np.abs(st - f * n))])
            dst.append(np.concatenate([win[b:], win[:b]]).astype(np.uint16))
        apis = list(rep.get("apis") or [])
        if len(apis) < 2:
            b4k.append(full[:4096].astype(np.uint16))
        else:
            r = int(round(f * len(apis)))
            rr = dict(rep); rr["apis"] = apis[r:] + apis[:r]
            b4k.append(np.asarray(nb.ids(rr)[:4096], dtype=np.uint16))
    return int(row), a512, a4k, b4k, len(full), bool(fallback) or len(starts) < 2


def build(workers):
    test, y = V.april()
    t0 = time.time()
    with Pool(workers, initializer=_init, initargs=(R.NEBULA,)) as pool:
        res = list(pool.imap(_rot, test.row.values, chunksize=32))
    assert [r[0] for r in res] == list(test.row.values)
    print(f"rotated + tokenised {len(res):,} reports x 6 edits in {time.time() - t0:.0f}s", flush=True)
    return {"a512": [r[1] for r in res], "a4k": [r[2] for r in res], "b4k": [r[3] for r in res],
            "n_tok": np.array([r[4] for r in res]), "unrotatable": np.array([r[5] for r in res])}


def edit_tokens(T, win, e):
    f = e % 3
    if e < 3:
        src = T["a512"] if win == 512 else T["a4k"]
    else:
        src = T["b4k"]
    return [r[f] for r in src]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="released,A,C,F,ATTbal")
    ap.add_argument("--seeds-old", type=int, default=5)
    ap.add_argument("--seeds-new", type=int, default=10)
    ap.add_argument("--seeds-f", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="rotation")
    a = ap.parse_args()
    R.n_threads()
    test, y = V.april()
    N = len(test)
    keys = a.models.split(",")
    nseeds = {"A": a.seeds_old, "C": a.seeds_old, "C2": a.seeds_old, "F": a.seeds_f}
    models = R.models_for(keys, {k: list(range(nseeds.get(k, a.seeds_new if k != "released" else 1))) for k in keys})
    T = build(a.workers)
    if a.limit:
        raise SystemExit("--limit not supported")
    n_tok, unrot = T["n_tok"], T["unrotatable"]
    fit = n_tok <= 512
    flags = {}                                   # model -> per seed: dict(thr1, thr01, z0, ze[6])
    per = {}
    for disp, (key, seeds) in models.items():
        w = R.window(key)
        for s in seeds:
            path = os.path.join(R.WORK5, f"rot_{key}_s{s}.npz")
            def run():
                m, _, z0 = R.load_model(key, s)
                t0 = time.time()
                ze = np.stack([R.score_tokens(m, w, edit_tokens(T, w, e)) for e in range(6)])
                print(f"  scored {disp} s{s} in {time.time() - t0:.0f}s", flush=True)
                return {"z0": z0, "ze": ze}
            per.setdefault(disp, []).append(R.cached(path, run))
    from sklearn.metrics import roc_auc_score
    labels = ["unedited"] + LABELS
    mal, ben = y == 1, y == 0
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))
    subsets = {"all": np.ones(N, bool), "fits in 512 tokens": fit, "longer than 512 tokens": ~fit}
    res = {}
    for disp, lst in per.items():
        rows = []
        for d in lst:
            z = np.concatenate([d["z0"][None], d["ze"]])                     # [7, N]
            thr = {f: C.thr_from(y, d["z0"], f) for f in (0.01, 0.001)}
            rows.append({"auc": np.array([roc_auc_score(y, zz) for zz in z]),
                         "flag": {f: (z > thr[f]).astype(float) for f in thr}})
        res[disp] = rows

    def mean_flag(disp, f):
        return np.mean([r["flag"][f] for r in res[disp]], 0)                  # [7, N]

    md = ["# Rotation check (round 5, item 4)\n", __doc__.split("Fractions")[0].split("Round 5, item 4: rotation check.")[1].strip() + "\n",
          f"Reports: {N:,} April ({int(mal.sum()):,} malware); {int(fit.sum()):,} fit in 512 tokens; {int(unrot.sum()):,} have fewer than two call boundaries "
          "in the window or a per-call tokenisation that differs from the full one (their (a) rotation is the identity). Seeds per model: "
          + ", ".join(f"{d} {len(l)}" for d, l in res.items()) + ".\n"]
    js = {"labels": labels, "seeds": {d: len(l) for d, l in res.items()}, "n_fit512": int(fit.sum()), "n_unrotatable": int(unrot.sum()), "tables": {}}
    for sub, mk in subsets.items():
        for f, ftag in ((0.01, "1%"), (0.001, "0.1%")):
            rows, chg = [], []
            for disp in res:
                fl = mean_flag(disp, f)
                r = {"model": disp}; c = {"model": disp}
                for e in range(7):
                    r[labels[e]] = f"{100 * fl[e][mal & mk].mean():.1f}%"
                    if e:
                        pt = fl[e][mal & mk].mean() - fl[0][mal & mk].mean()
                        mm = (mal & mk).astype(float)
                        bs = (W @ (fl[e] * mm)) / (W @ mm) - (W @ (fl[0] * mm)) / (W @ mm)
                        c[labels[e]] = f"{100 * pt:+.1f} {R.ci(bs)}"
                rows.append(r); chg.append(c)
            md += [f"\n## Malware TPR at the threshold of {ftag} FPR, {sub}\n", C.md_table(pd.DataFrame(rows)),
                   f"\nChange in points [group 95%], {sub}\n", C.md_table(pd.DataFrame(chg))]
            js["tables"][f"tpr{ftag}_{sub}"] = {d: [float(mean_flag(d, f)[e][mal & mk].mean()) for e in range(7)] for d in res}
        rows = []
        for disp in res:
            fl = mean_flag(disp, 0.01)
            rows.append({"model": disp, **{labels[e]: f"{100 * fl[e][ben & mk].mean():.2f}%" for e in range(7)}})
        md += [f"\n## Benign FPR at the threshold of 1% FPR, {sub}\n", C.md_table(pd.DataFrame(rows))]
    rows = []
    for disp in res:
        au = np.mean([r["auc"] for r in res[disp]], 0)
        rows.append({"model": disp, **{labels[e]: f"{au[e]:.4f}" for e in range(7)}})
    md += ["\n## AUC (all reports)\n", C.md_table(pd.DataFrame(rows))]
    js["auc"] = {d: np.mean([r["auc"] for r in res[d]], 0).tolist() for d in res}
    # seed-paired differences of the change in TPR at 1% FPR, all reports, ATT+bal (or the first listed new model) against the others
    ref = "ATT+bal"
    if ref in res:
        rng = np.random.default_rng(0)
        rows = []
        for other in res:
            if other == ref or len(res[other]) < 2:
                continue
            r = {"difference": f"{ref} − {other}"}
            n = min(len(res[ref]), len(res[other]))
            for e in range(1, 7):
                dx = np.array([x["flag"][0.01][e][mal].mean() - x["flag"][0.01][0][mal].mean() for x in res[ref][:n]])
                dz = np.array([x["flag"][0.01][e][mal].mean() - x["flag"][0.01][0][mal].mean() for x in res[other][:n]])
                d = 100 * (dx - dz); b = rng.choice(d, (20000, len(d))).mean(1)
                r[labels[e]] = f"{d.mean():+.1f} [{np.percentile(b, 2.5):+.1f}, {np.percentile(b, 97.5):+.1f}]"
            rows.append(r)
        md += ["\n## Seed-paired difference in the change of TPR at 1% FPR, all malware (points, [95% over seeds])\n", C.md_table(pd.DataFrame(rows))]
    open(f"{R.OUT}/{a.out}.md", "w").write("\n".join(md))
    json.dump(js, open(f"{R.OUT}/{a.out}.json", "w"), indent=1)
    print("\n".join(md[:12]))


if __name__ == "__main__":
    main()
