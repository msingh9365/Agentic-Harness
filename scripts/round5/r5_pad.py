#!/usr/bin/env python
"""
Round 5, items 3a-3c and 5: padding the models with calls of the EVAL pool, several ways. Only the EVAL pool is used (never the TRAIN pool;
the TRAIN pool is used once, in prep_pools5.py, to define the "rarest 20% of API names"). Malware April reports (9,399) and 2,000 random benign
April reports (the same subset as round 4) are edited in memory, k = 1, 5, 20, 50, "insert k" (at random places) or "prepend k"; only scores are
cached, never edited reports.

Variants (--variant):
  random      random single calls of random EVAL reports (the round 4 test; item 5)
  block       a contiguous run of k calls, in order, from one random EVAL report that has at least k calls (3a)
  syswow      random single calls from the EVAL reports of the other benign source (windows_syswow64: 4 reports) (3b)
  clean       random single calls from the EVAL reports of source clean (3b, the source of almost all training padding)
  rare        random single calls whose API name is in the rarest 20% of the TRAIN pool (3b)
  sur_lgb     the k top-ranked EVAL calls of the surrogate LightGBM bag of API names (3c; ranking from surrogate_rank.py)
  sur_c       the k top-ranked EVAL calls of the surrogate C (J) seed 0 (3c)
Thresholds: fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed. "Fits in 512": no original call leaves the
512-token window after the edit. Intervals: group bootstrap over April hash_apis (1,000 resamples) and seed-paired.

    python scripts/round5/r5_pad.py --variant block --models released,A,C,ATTbal,MMbal,Cbal --seeds-old 5 --seeds-new 5
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

KS = V.KS
EDITS = V.EDITS
VARIANTS = ["random", "block", "syswow", "clean", "rare", "sur_lgb", "sur_c"]


def _init_pad(nebula, spec):
    _init(nebula)
    reps = _W["reps"]
    calls = lambda r: list(reps.get(int(r)).get("apis") or [])
    ev = spec["eval_rows"]
    _W["ev_rows"] = ev
    _W["ev"] = [calls(r) for r in ev]
    _W["syswow"] = [i for i, r in enumerate(ev) if int(r) in set(spec["syswow"])]
    _W["clean"] = [i for i, r in enumerate(ev) if int(r) in set(spec["clean"])]
    rare = set(spec["rare_names"])
    _W["rare_calls"] = [c for rep in _W["ev"] for c in rep if c["api_name"] in rare]
    _W["ranked"] = [reps.get(int(r)).get("apis")[i] for r, i in spec.get("ranked", [])]
    _W["variant"] = spec["variant"]


def _single(rng, idxs):
    ev = _W["ev"]
    r = ev[idxs[int(rng.integers(len(idxs)))]]
    while not r:
        r = ev[idxs[int(rng.integers(len(idxs)))]]
    return r[int(rng.integers(len(r)))]


def make_add(variant, rng, k):
    ev = _W["ev"]
    if variant == "random":
        return [_single(rng, range(len(ev))) for _ in range(k)]
    if variant == "syswow":
        return [_single(rng, _W["syswow"]) for _ in range(k)]
    if variant == "clean":
        return [_single(rng, _W["clean"]) for _ in range(k)]
    if variant == "rare":
        rc = _W["rare_calls"]
        return [rc[int(rng.integers(len(rc)))] for _ in range(k)]
    if variant == "block":
        ok = [i for i, r in enumerate(ev) if len(r) >= k]
        r = ev[ok[int(rng.integers(len(ok)))]]
        s = int(rng.integers(0, len(r) - k + 1))
        return list(r[s:s + k])
    if variant in ("sur_lgb", "sur_c"):
        return list(_W["ranked"][:k])
    raise ValueError(variant)


def edit(apis, row, k, mode, variant):
    rng = np.random.default_rng([8000 + VARIANTS.index(variant), int(row), k, 0 if mode == "insert" else 1])
    add = make_add(variant, rng, k)
    if mode == "prepend":
        return add + list(apis)
    n = len(apis)
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
                r = dict(rep); r["apis"] = edit(apis, row, k, mode, _W["variant"]); t = nb.ids(r)
            out.append(np.asarray(t[:4096], dtype=np.uint16)); lens.append(len(t))
    return int(row), out, lens


def spec_for(variant):
    p = json.load(open("results/pooling_v4/pools.json"))
    q = json.load(open(f"{R.OUT}/pools5.json"))
    s = {"eval_rows": p["eval_rows"], "syswow": q["eval_syswow64_rows"], "clean": q["eval_clean_rows"], "rare_names": q["rare_names"], "variant": variant}
    if variant.startswith("sur_"):
        s["ranked"] = json.load(open(f"{R.OUT}/surrogate_{variant[4:]}.json"))["ranked_calls"]
    return s


def padded_sets(variant, workers=4):
    test, y = V.april()
    mal = np.flatnonzero(y == 1)
    ben = np.flatnonzero(y == 0)
    ben = np.sort(np.random.default_rng(7).choice(ben, V.N_BEN_SUB, replace=False))     # the subset of round 4
    pos = np.concatenate([mal, ben])
    t0 = time.time()
    with Pool(workers, initializer=_init_pad, initargs=(R.NEBULA, spec_for(variant))) as pool:
        res = list(pool.imap(_tok, test.row.values[pos], chunksize=32))
    toks = [[r[1][j] for r in res] for j in range(len(EDITS))]
    lens = np.array([r[2] for r in res]).T
    print(f"[{variant}] tokenised {len(pos):,} reports x {len(EDITS)} edits in {time.time() - t0:.0f}s", flush=True)
    return {"pos": pos, "n_mal": len(mal), "toks": toks, "lens": lens}


def logits_for(P, variant, key, s, cache_name=None):
    """(z0 [N], ze [8, n]) of one model run, cached as scores only."""
    if variant == "random" and key in ("A", "C", "C2", "F", "released") and s < 5:
        # round 4 caches (same edits, same pool)
        legacy = os.path.join(V.WORK, f"v4_pad_logits_{'released' if key == 'released' else key + '_s' + str(s)}.npz")
        if os.path.exists(legacy):
            d = np.load(legacy)
            if d["ze"].shape == (len(EDITS), len(P["pos"])):
                return d["z0"], d["ze"]
    path = os.path.join(R.WORK5, f"pad_{variant}_{key}_s{s}.npz")
    if os.path.exists(path):
        d = np.load(path)
        return d["z0"], d["ze"]
    m, w, z0 = R.load_model(key, s)
    t0 = time.time()
    ze = np.stack([R.score_tokens(m, w, P["toks"][j]) for j in range(len(EDITS))])
    np.savez(path, z0=z0, ze=ze)
    print(f"  [{variant}] scored {key} s{s} in {time.time() - t0:.0f}s", flush=True)
    return z0, ze


def tables(P, variant, models, test, y, out_name, title_extra=""):
    pos, nm = P["pos"], P["n_mal"]
    mal_pos, ben_pos = pos[:nm], pos[nm:]
    lens = P["lens"]
    fit512 = lens[:, :nm] <= 512
    N = len(test)
    labels = ["unedited"] + EDITS
    fl = {f: {} for f in (0.01, 0.001)}
    seedflags = {f: {} for f in (0.01, 0.001)}
    for disp, (key, seeds) in models.items():
        acc = {f: ([], []) for f in fl}
        for s in seeds:
            z0, ze = logits_for(P, variant, key, s)
            for f in fl:
                thr = C.thr_from(y, z0, f)
                f0 = (z0 > thr).astype(float)
                acc[f][0].append(np.stack([f0[mal_pos]] + [(ze[j][:nm] > thr).astype(float) for j in range(8)]))
                acc[f][1].append(np.stack([f0[ben_pos]] + [(ze[j][nm:] > thr).astype(float) for j in range(8)]))
        for f in fl:
            fl[f][disp] = (np.mean(acc[f][0], 0), np.mean(acc[f][1], 0))
            seedflags[f][disp] = acc[f][0]
        print(f"  [{variant}] flags {disp} ({len(seeds)} seeds)", flush=True)
    W = np.stack(list(C.group_weights_boot(test.hash_apis.values, 1000, 0)))
    Wm, Wb = W[:, mal_pos], W[:, ben_pos]
    allm = np.ones(nm, bool)
    wmean = lambda Wx, v, mask: (Wx @ (v * mask)) / (Wx @ mask.astype(float))
    desc = {"random": "random single calls of random EVAL reports (the round 4 test)", "block": "a contiguous run of k calls, in order, from one EVAL report",
            "syswow": "random calls of the 4 EVAL reports of the other benign source (windows_syswow64)", "clean": "random calls of the EVAL reports of source clean",
            "rare": "random EVAL calls whose API name is in the rarest 20% of the TRAIN pool", "sur_lgb": "the k top-ranked EVAL calls of the surrogate LightGBM bag of API names",
            "sur_c": "the k top-ranked EVAL calls of the surrogate C (J) seed 0"}[variant]
    md = [f"# Padding variant `{variant}` {title_extra}\n", f"Padding: {desc}. k = 1, 5, 20, 50, inserted at random places or prepended. Malware: 9,399 April reports; benign: "
          "2,000 random April reports edited the same way. Thresholds fixed at 1% and 0.1% FPR on the unedited April benign scores of each model and seed; mean over "
          "seeds (seeds per model in the json). Edited reports exist in memory only.\n"]
    js = {"variant": variant, "labels": labels, "share_fit512": fit512.mean(1).tolist(), "tpr": {}, "tpr_fit512": {}, "fpr_benign": {}, "seeds": {d: len(s) for d, (k, s) in models.items()}}
    for f, ftag in ((0.01, "1%"), (0.001, "0.1%")):
        t_after, t_chg, t_fit, t_fitchg, t_fpr = [], [], [], [], []
        for disp in models:
            fm, fb = fl[f][disp]
            ra, rc, rf, rfc, rb = ({"model": disp} for _ in range(5))
            for e in range(9):
                ra[labels[e]] = f"{100 * fm[e].mean():.1f}%"
                rb[labels[e]] = f"{100 * fb[e].mean():.2f}%"
                if e:
                    mk = fit512[e - 1]
                    pt = fm[e].mean() - fm[0].mean()
                    rc[labels[e]] = f"{100 * pt:+.1f} {R.ci(wmean(Wm, fm[e], allm) - wmean(Wm, fm[0], allm))}"
                    rf[labels[e]] = f"{100 * fm[0][mk].mean():.1f}% → {100 * fm[e][mk].mean():.1f}%"
                    ptf = fm[e][mk].mean() - fm[0][mk].mean()
                    rfc[labels[e]] = f"{100 * ptf:+.1f} {R.ci(wmean(Wm, fm[e], mk) - wmean(Wm, fm[0], mk))}"
            for t, r in ((t_after, ra), (t_chg, rc), (t_fit, rf), (t_fitchg, rfc), (t_fpr, rb)):
                t.append(r)
            js["tpr"].setdefault(ftag, {})[disp] = [float(fm[e].mean()) for e in range(9)]
            js["tpr_fit512"].setdefault(ftag, {})[disp] = [float(fm[e][fit512[e - 1]].mean()) if e else None for e in range(9)]
            js["fpr_benign"].setdefault(ftag, {})[disp] = [float(fb[e].mean()) for e in range(9)]
        md += [f"\n## Threshold of {ftag} FPR: malware TPR after the edit, all 9,399 malware reports\n", C.md_table(pd.DataFrame(t_after)),
               f"\nChange in points [group 95%]\n", C.md_table(pd.DataFrame(t_chg)),
               f"\n## Threshold of {ftag} FPR: reports that fit in 512 tokens after the edit, TPR before → after\n", C.md_table(pd.DataFrame(t_fit)),
               f"\nChange in points [group 95%]\n", C.md_table(pd.DataFrame(t_fitchg)),
               f"\n## Threshold of {ftag} FPR: FPR of the 2,000 benign April reports padded the same way\n", C.md_table(pd.DataFrame(t_fpr))]
    # model differences in the change of TPR at 1% FPR, group bootstrap and seed-paired
    names = list(models)
    ref = "ATT+bal" if "ATT+bal" in names else None
    if ref:
        rows, rows_s = [], []
        rng = np.random.default_rng(0)
        for other in names:
            if other == ref:
                continue
            for tag, getm in (("all", lambda e: allm), ("fits", lambda e: fit512[e - 1])):
                r = {"difference": f"{ref} − {other} ({tag})"}
                rs = {"difference": f"{ref} − {other} ({tag})"}
                for e in range(1, 9):
                    mk = getm(e)
                    fx, fz = fl[0.01][ref][0], fl[0.01][other][0]
                    pt = (fx[e][mk].mean() - fx[0][mk].mean()) - (fz[e][mk].mean() - fz[0][mk].mean())
                    bs = (wmean(Wm, fx[e], mk) - wmean(Wm, fx[0], mk)) - (wmean(Wm, fz[e], mk) - wmean(Wm, fz[0], mk))
                    r[labels[e]] = f"{100 * pt:+.1f} {R.ci(bs)}"
                    sx, sz = seedflags[0.01][ref], seedflags[0.01][other]
                    if len(sx) > 1 and len(sz) > 1:
                        n = min(len(sx), len(sz))
                        d = 100 * (np.array([f[e][mk].mean() - f[0][mk].mean() for f in sx[:n]]) - np.array([f[e][mk].mean() - f[0][mk].mean() for f in sz[:n]]))
                        b = rng.choice(d, (20000, len(d))).mean(1)
                        rs[labels[e]] = f"{d.mean():+.1f} [{np.percentile(b, 2.5):+.1f}, {np.percentile(b, 97.5):+.1f}]"
                rows.append(r)
                if len(rs) > 1:
                    rows_s.append(rs)
        md += ["\n## ATT+bal against each model, difference in the change of malware TPR at 1% FPR, points [group 95%]\n", C.md_table(pd.DataFrame(rows))]
        if rows_s:
            md += ["\nSeed-paired (95% over the seeds)\n", C.md_table(pd.DataFrame(rows_s))]
    open(f"{R.OUT}/{out_name}.md", "w").write("\n".join(md))
    json.dump(js, open(f"{R.OUT}/{out_name}.json", "w"), indent=1)
    return md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=VARIANTS, required=True)
    ap.add_argument("--models", default="released,A,C,ATTbal,MMbal,Cbal")
    ap.add_argument("--seeds-old", type=int, default=5)
    ap.add_argument("--seeds-new", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    R.n_threads()
    test, y = V.april()
    keys = a.models.split(",")
    nseeds = {"A": a.seeds_old, "C": a.seeds_old, "C2": a.seeds_old, "F": 5, "released": 1}
    models = R.models_for(keys, {k: list(range(nseeds.get(k, a.seeds_new))) for k in keys})
    P = padded_sets(a.variant, a.workers)
    md = tables(P, a.variant, models, test, y, a.out or f"pad_{a.variant}")
    print("\n".join(md[:14]))


if __name__ == "__main__":
    main()
