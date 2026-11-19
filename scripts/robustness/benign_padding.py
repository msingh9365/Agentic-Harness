#!/usr/bin/env python
"""
Item 2 of results/robustness: robustness measurement "malware padded with benign calls".

    python scripts/robustness/benign_padding.py --src-j <regime J output>

A measurement of how much the detection rate of a model falls when API calls that occur in benign reports are added to
malware reports. It is not a search for evasions: the added calls are drawn at random, k is fixed (1, 5, 20, 50), and
nothing is optimised. The edits are applied in memory to the JSON behaviour reports of the dataset (the filtered reports
of Nebula's preprocessing); the edited reports/tokens are not written to disk, only aggregate numbers.

  insert k  : k calls at random places;   prepend k : k calls before the first call.
  Each added call: a random call of a random benign JANUARY report (pool of 2,000 randomly chosen benign January reports
  with at least one call, numpy Generator seed 5000).
  Only the 9,399 malware April reports are edited; benign April reports stay unchanged. Malware reports without any API
  call stay unchanged. Threshold: fixed at 1% FPR on the unedited April scores of each model (per seed), so the benign FPR
  stays 1% by construction. Reported: malware TPR (mean over seeds) before/after; group-bootstrap intervals (April hash_apis,
  1,000 resamples) and, for C (J) - A (J), a seed-paired bootstrap; and the restricted case "fits" = malware reports whose
  whole edited token sequence is at most 512 tokens (no original call leaves the window).
Models: released Nebula, A (J), C (J) (regime J: all of January; A 1 epoch, C 10 epochs; 10 seeds each).
Writes results/robustness/benign_padding.md and .json.
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
sys.path.insert(0, os.path.join(HERE, "..", "pooling_v2"))
import common as C  # noqa: E402
from hier_nebula.model import build_level1  # noqa: E402
from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL  # noqa: E402
from perturb_check import _init, _W, pad, logits  # noqa: E402

KS = [1, 5, 20, 50]
EDITS = [f"insert {k}" for k in KS] + [f"prepend {k}" for k in KS]
OUT = "results/robustness"
EPOCHS_J = {"A": 1, "C": 10}


def _init_pool(nebula, pool_rows):
    _init(nebula)
    pool = []
    for r in pool_rows:
        apis = list(_W["reps"].get(int(r)).get("apis") or [])
        if apis:
            pool.append(apis)
    _W["pool"] = pool


def _edit(apis, row, k, mode):
    rng = np.random.default_rng([6000, int(row), k, 0 if mode == "insert" else 1])
    pool = _W["pool"]
    add = []
    for _ in range(k):
        r = int(rng.integers(len(pool)))
        add.append(pool[r][int(rng.integers(len(pool[r])))])
    n = len(apis)
    if mode == "prepend":
        return add + list(apis)
    gaps = np.sort(rng.integers(0, n + 1, k))
    out, j = [], 0
    for i in range(n + 1):
        while j < k and gaps[j] == i:
            out.append(add[j]); j += 1
        if i < n:
            out.append(apis[i])
    return out


def _tok(row):
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    apis = list(rep.get("apis") or [])
    out, lens = [], []
    for mode in ("insert", "prepend"):
        for k in KS:
            if not apis:
                t = nb.ids(rep)
            else:
                r = dict(rep); r["apis"] = _edit(apis, row, k, mode); t = nb.ids(r)
            out.append(np.asarray(t[:512], dtype=np.int32)); lens.append(len(t))
    return int(row), out, lens, len(apis)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-j", required=True)
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="debug: only this many malware reports")
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    y = test.label.values
    N = len(test)
    mal_idx = np.flatnonzero(y == 1)
    if a.limit:
        mal_idx = mal_idx[:a.limit]
    jan_ben = meta.row.values[(meta.split == "trainset") & (meta.label == 0)]
    pool_rows = np.random.default_rng(5000).choice(jan_ben, 2000, replace=False)
    t0 = time.time()
    with Pool(a.workers, initializer=_init_pool, initargs=(a.nebula, pool_rows)) as pool:
        res = list(pool.imap(_tok, test.row.values[mal_idx], chunksize=32))
    X = np.stack([pad([r[1][j] for r in res]) for j in range(len(EDITS))]).astype(np.int64)       # [8, n_mal, 512]
    L = np.array([r[2] for r in res]).T
    ncalls = np.array([r[3] for r in res])
    print(f"tokenised {len(mal_idx):,} malware reports under {len(EDITS)} edits in {time.time() - t0:.0f}s; "
          f"{100 * float((ncalls == 0).mean()):.1f}% have no calls (unchanged)", flush=True)
    fits = L <= 512                                                    # [8, n_mal]

    plain = np.load(os.path.join("/Users/manish/Code/mtp/pooling_v2_work", f"perturbed_tokens_{N}.npz"))["plain"]
    names = ["released Nebula", "A (J)", "C (J)"]
    keys = {"released Nebula": ["released"], "A (J)": [f"A_s{s}" for s in range(10)], "C (J)": [f"C_s{s}" for s in range(10)]}
    z0, ze = {}, {}
    rel = build_level1(a.nebula, vocab_size=50001, pretrained=True).eval()
    z0["released"] = logits(rel, plain.astype(np.int64))
    ze["released"] = np.stack([logits(rel, X[j]) for j in range(len(EDITS))])
    for v in ("A", "C"):
        for s in range(10):
            run = f"{v}_all_s{s}"
            m = build_variant(a.nebula, V2_TO_INTERNAL[v]).eval()
            m.load_state_dict(torch.load(os.path.join(a.src_j, "ckpt", run, "final.pt"), map_location="cpu", weights_only=True))
            z0[f"{v}_s{s}"] = np.load(os.path.join(a.src_j, "scores", f"{run}_epochs.npz"))["april"][EPOCHS_J[v] - 1]
            ze[f"{v}_s{s}"] = np.stack([logits(m, X[j]) for j in range(len(EDITS))])
            print(run, f"{time.time() - t0:.0f}s", flush=True)

    # flags: [9, N] fraction of seeds that flag (mean over seeds); row 0 = unedited, benign rows never change
    flags = {}
    for n in names:
        fl = []
        for k in keys[n]:
            thr = C.thr_from(y, z0[k], 0.01)
            f0 = (z0[k] > thr).astype(float)
            fs = [f0]
            for j in range(len(EDITS)):
                f = f0.copy(); f[mal_idx] = (ze[k][j] > thr).astype(float); fs.append(f)
            fl.append(np.stack(fs))
        flags[n] = np.mean(fl, 0)
    labels = ["unedited"] + EDITS
    mal = np.zeros(N, bool); mal[mal_idx] = True
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))
    def fit_mask(e):
        m = np.zeros(N, bool); m[mal_idx] = fits[e - 1]; return m
    def wtpr(fl, mask):
        m = (mask & mal).astype(float); return (W @ (fl * m)) / (W @ m)
    ci = lambda v: f"[{100 * np.percentile(v, 2.5):+.1f}, {100 * np.percentile(v, 97.5):+.1f}]"
    point = lambda fl, mask: float(fl[mask & mal].mean())
    all_m = mal
    t1, t2, t3, t4 = [], [], [], []
    for e in range(1, 9):
        fm = fit_mask(e)
        r1, r2 = {"edit": labels[e]}, {"edit": labels[e], "malware reports that fit": f"{int(fm.sum()):,}"}
        for n in names:
            r1[f"{n}: TPR before → after"] = f"{100 * point(flags[n][0], all_m):.1f}% → {100 * point(flags[n][e], all_m):.1f}%"
            d = wtpr(flags[n][e], all_m) - wtpr(flags[n][0], all_m)
            r1[f"{n}: change, points [group 95%]"] = f"{100 * (point(flags[n][e], all_m) - point(flags[n][0], all_m)):+.1f} {ci(d)}"
            r2[f"{n}: TPR before → after"] = f"{100 * point(flags[n][0], fm):.1f}% → {100 * point(flags[n][e], fm):.1f}%"
            d2 = wtpr(flags[n][e], fm) - wtpr(flags[n][0], fm)
            r2[f"{n}: change, points [group 95%]"] = f"{100 * (point(flags[n][e], fm) - point(flags[n][0], fm)):+.1f} {ci(d2)}"
        t1.append(r1); t2.append(r2)
        for tag, mask, tab in (("all malware", all_m, t3), ("malware that fits", fm, t4)):
            r = {"edit": labels[e]}
            for x_, y_ in (("A (J)", "released Nebula"), ("C (J)", "released Nebula"), ("C (J)", "A (J)")):
                dd = (wtpr(flags[x_][e], mask) - wtpr(flags[x_][0], mask)) - (wtpr(flags[y_][e], mask) - wtpr(flags[y_][0], mask))
                pt = (point(flags[x_][e], mask) - point(flags[x_][0], mask)) - (point(flags[y_][e], mask) - point(flags[y_][0], mask))
                r[f"change {x_} − {y_}, points [group 95%]"] = f"{100 * pt:+.1f} {ci(dd)}"
            tab.append(r)
    rng = np.random.default_rng(0)
    # seed-paired C - A (recomputed per seed on the right subset)
    t5 = []
    def tpr_seed(v, e, mask_m):
        return np.array([((ze[f"{v}_s{s}"][e - 1][mask_m] > C.thr_from(y, z0[f"{v}_s{s}"], 0.01)).mean()
                          - (z0[f"{v}_s{s}"][mal_idx][mask_m] > C.thr_from(y, z0[f"{v}_s{s}"], 0.01)).mean()) for s in range(10)])
    for e in range(1, 9):
        for tag, mm in (("all malware", np.ones(len(mal_idx), bool)), ("malware that fits", fits[e - 1])):
            dA, dC = 100 * tpr_seed("A", e, mm), 100 * tpr_seed("C", e, mm)
            x = dC - dA; b = rng.choice(x, (20000, 10)).mean(1)
            t5.append({"edit": labels[e], "set": tag, "A (J) change": f"{dA.mean():+.1f}", "C (J) change": f"{dC.mean():+.1f}",
                       "C − A, seed-paired [95% over seeds]": f"{x.mean():+.1f} [{np.percentile(b, 2.5):+.1f}, {np.percentile(b, 97.5):+.1f}]"})
    json.dump({"labels": labels, "tpr_all_malware": {n: [point(flags[n][e], all_m) for e in range(9)] for n in names},
               "tpr_fits": {n: [point(flags[n][e], fit_mask(e)) if e else None for e in range(9)] for n in names},
               "n_malware": int(len(mal_idx)), "share_no_calls": float((ncalls == 0).mean())},
              open(f"{OUT}/benign_padding.json" if not a.limit else f"{OUT}/benign_padding_debug.json", "w"), indent=1)
    md = ["# Item 2: malware reports padded with calls from benign January reports (robustness measurement)\n",
          "Only the " + f"{len(mal_idx):,}" + " malware April reports are edited; benign April reports stay unchanged and the threshold stays fixed at 1% FPR "
          "on the unedited April scores of each model, so the benign FPR is 1% by construction. Each added call is a random call of a random benign January "
          "report (pool of 2,000), k = 1, 5, 20, 50, inserted at random places or prepended; nothing is optimised. "
          f"{100 * float((ncalls == 0).mean()):.1f}% of the malware reports have no API call and stay unchanged. A (J), C (J): mean over 10 seeds "
          "(regime J). \"Fits\": the whole edited token sequence is at most 512 tokens, so no original call leaves the window.\n",
          "## Malware TPR at the fixed threshold, all malware reports\n", C.md_table(pd.DataFrame(t1)),
          "\n## Only malware reports that fit in 512 tokens after the edit\n", C.md_table(pd.DataFrame(t2)),
          "\n## Differences between models in the change of TPR (group bootstrap), all malware\n", C.md_table(pd.DataFrame(t3)),
          "\n## The same on malware that fits\n", C.md_table(pd.DataFrame(t4)),
          "\n## C (J) versus A (J), seed-paired\n", "Bootstrap over the 10 seeds only.\n", C.md_table(pd.DataFrame(t5))]
    if not a.limit:
        open(f"{OUT}/benign_padding.md", "w").write("\n".join(md))
    print(C.md_table(pd.DataFrame(t1))); print(C.md_table(pd.DataFrame(t2)))


if __name__ == "__main__":
    main()
