#!/usr/bin/env python
"""
Test 3: how far is "unseen"? Works on unique API-name sequences (exactly the sequences hashed in
hash_apis: full API names in Nebula's filtered report, in order).

For each unique April sequence that does not occur in January:
  nearest January sequence: shortlist the 20 January sequences with the highest Jaccard similarity of
    call 3-grams (sequence padded with start/end markers, so every sequence has at least one 3-gram),
    then the Levenshtein distance in calls (rapidfuzz) divided by the longer length; keep the minimum.
  window share: share of its 16-call windows (stride 1) that occur in any January sequence
    (sequences shorter than 16 calls: not defined, counted separately).
Distribution per label uses (sequence, label) pairs. Detection per quartile uses the April reports.
"""
import hashlib
import json
import time

import numpy as np
import pandas as pd
import scipy.sparse as sp
from rapidfuzz.distance import Levenshtein

import common as C

TOP = 20
WIN = 16


def main():
    meta = C.meta_full()
    reps = C.Reps()
    jan = meta[meta.split == "trainset"]
    test = meta[meta.split == "testset"].reset_index(drop=True)
    unseen_rows = test[~test.seen]
    rep_jan = jan.groupby("hash_apis").row.first()
    rep_apr = unseen_rows.groupby("hash_apis").row.first()
    print(f"unique January sequences: {len(rep_jan):,}; unique unseen April sequences: {len(rep_apr):,} "
          f"({len(unseen_rows):,} April reports)", flush=True)
    t0 = time.time()
    vocab = {}

    def seq(row, h):
        names = [c["api_name"] for c in (reps.get(int(row)).get("apis") or [])]
        assert hashlib.sha1("\n".join(names).encode()).hexdigest() == h
        return np.array([vocab.setdefault(n, len(vocab)) for n in names], dtype=np.int64)
    J = [seq(r, h) for h, r in rep_jan.items()]
    A = [seq(r, h) for h, r in rep_apr.items()]
    print(f"sequences read and hash-checked in {time.time() - t0:.0f}s; {len(vocab)} distinct API names", flush=True)

    # ---- 3-gram Jaccard shortlist
    V = len(vocab) + 2
    gram_id = {}

    def grams(s):
        p = np.concatenate([[V - 2], s, [V - 1]])
        g = set(zip(p[:-2], p[1:-1], p[2:]))
        return [gram_id.setdefault(x, len(gram_id)) for x in g]

    def matrix(seqs):
        r, c = [], []
        for i, s in enumerate(seqs):
            g = grams(s)
            r += [i] * len(g); c += g
        return r, c
    rj, cj = matrix(J); ra, ca = matrix(A)
    G = len(gram_id)
    MJ = sp.csr_matrix((np.ones(len(rj), np.float32), (rj, cj)), shape=(len(J), G))
    MA = sp.csr_matrix((np.ones(len(ra), np.float32), (ra, ca)), shape=(len(A), G))
    inter = (MA @ MJ.T).toarray()
    sa, sj = np.asarray(MA.sum(1)).ravel(), np.asarray(MJ.sum(1)).ravel()
    jac = inter / (sa[:, None] + sj[None, :] - inter)
    short = np.argsort(-jac, axis=1)[:, :TOP]
    # ---- edit distance on the shortlist
    t0 = time.time()
    dist, nearest = np.zeros(len(A)), np.zeros(len(A), int)
    Jl = [s.tolist() for s in J]
    for i, s in enumerate(A):
        sl = s.tolist()
        best = (np.inf, -1)
        for j in short[i]:
            L = max(len(sl), len(Jl[j]))
            d = Levenshtein.distance(sl, Jl[j]) / L if L else 0.0
            if d < best[0]:
                best = (d, j)
        dist[i], nearest[i] = best
    print(f"edit distances: {len(A) * TOP:,} pairs in {time.time() - t0:.0f}s (all unseen sequences, no sampling)", flush=True)
    # ---- 16-call windows
    jw = set()
    for s in J:
        for k in range(len(s) - WIN + 1):
            jw.add(s[k:k + WIN].tobytes())
    wshare = np.full(len(A), np.nan)
    for i, s in enumerate(A):
        n = len(s) - WIN + 1
        if n > 0:
            wshare[i] = np.mean([s[k:k + WIN].tobytes() in jw for k in range(n)])
    seqdf = pd.DataFrame({"hash_apis": rep_apr.index, "n_calls": [len(s) for s in A], "nearest_dist": dist,
                          "max_jaccard": jac.max(1), "window_share": wshare,
                          "nearest_jan_hash": rep_jan.index.values[nearest]})
    seqdf.to_parquet(f"{C.OUT}/scores/test3_unseen_sequences.parquet", index=False)

    # ---- distributions by label ((sequence, label) pairs)
    lab = unseen_rows.groupby(["hash_apis", "label"]).size().reset_index(name="reports")
    lab = lab.merge(seqdf, on="hash_apis")
    def describe(v):
        v = v[~np.isnan(v)]
        q = np.percentile(v, [25, 50, 75])
        return f"{q[1]:.3f} [{q[0]:.3f}–{q[2]:.3f}]", len(v)
    rows = []
    for name, col in [("nearest January distance", "nearest_dist"), (f"share of {WIN}-call windows in January", "window_share")]:
        for lname, l in [("all unseen sequences", None), ("benign", 0), ("malware", 1)]:
            v = (seqdf[col].values if l is None else lab[lab.label == l][col].values).astype(float)
            d, n = describe(v)
            rows.append({"measure": name, "sequences": lname, "n": f"{n:,}", "median [quartiles]": d})
    dist_t = pd.DataFrame(rows)
    bins = np.linspace(0, 1, 11)
    hist = {"bin": [f"{bins[i]:.1f}–{bins[i + 1]:.1f}" for i in range(10)]}
    for name, col in [("distance", "nearest_dist"), ("window share", "window_share")]:
        for lname, l in [("benign", 0), ("malware", 1)]:
            v = lab[lab.label == l][col].values.astype(float)
            v = v[~np.isnan(v)]
            hist[f"{name}, {lname}"] = np.histogram(np.clip(v, 0, 1 - 1e-9), bins)[0]
    hist_t = pd.DataFrame(hist)
    n_short = int(np.isnan(wshare).sum())
    exact = int((dist == 0).sum())

    # ---- detection per quartile (April reports of unseen sequences)
    yv = meta[meta.side == "val"].label.values
    val_rows = meta.row.values[meta.side == "val"]
    models, thr_b = {}, {}
    for name, f in [("released Nebula", "nebula"), ("two-level K=8", "twolevel_k8"), ("LightGBM bag of API names", "lgbm_bag_full")]:
        a, v = C.load_scores(f, "april"), C.load_scores(f, "janval")
        models[name] = {s: a[s].loc[test.row.values].values for s in a}
        thr_b[name] = {s: {fp: C.thr_from(yv, v[s].loc[val_rows].values, fp) for fp, _ in C.FPRS} for s in v}
    rep_d = test.hash_apis.map(seqdf.set_index("hash_apis").nearest_dist).values
    rep_w = test.hash_apis.map(seqdf.set_index("hash_apis").window_share).values
    qd = np.nanpercentile(seqdf.nearest_dist, [25, 50, 75])
    qw = np.nanpercentile(seqdf.window_share, [25, 50, 75])
    def qmasks(v, q, tag):
        edges = [-np.inf, *q, np.inf]
        return [(f"{tag} Q{i + 1} ({'≤' if i < 3 else '>'} {q[min(i, 2)]:.3f})", (v > edges[i]) & (v <= edges[i + 1]) & ~np.isnan(v))
                for i in range(4)]
    unseen = ~test.seen.values
    wmasks = [("window share = 100%", unseen & (rep_w == 1)),
              (f"window share {qw[0]:.3f}–<100%", unseen & (rep_w > qw[0]) & (rep_w < 1)),
              (f"window share ≤ {qw[0]:.3f} (lowest quartile)", unseen & (rep_w <= qw[0])),
              (f"shorter than {WIN} calls (no window)", unseen & np.isnan(rep_w))]
    masks = [("seen in January", test.seen.values), ("unseen, all", unseen)] + qmasks(rep_d, qd, "distance") + wmasks
    point, ci, dci, masks = C.evaluate_models(test, models, thr_b, masks=masks)
    det = []
    for sub, m in masks:
        for mod in models:
            r = {"April reports": sub, "model": mod, "n (malware)": f"{point[mod][sub]['n']:,.0f} ({point[mod][sub]['n_mal']:,.0f})"}
            for k in ["auc", "tpr1%_a", "fpr1%_a", "tpr1%_b", "fpr1%_b"]:
                lo, hi = ci[(mod, sub, k)]
                r[C.HEAD[k]] = f"{C.fmt(k, point[mod][sub][k])} [{C.fmt(k, lo)}, {C.fmt(k, hi)}]"
            det.append(r)
    # per chunk bucket: distance of unseen reports
    ch = []
    for b in ["1", "2-3", "4-8"]:
        m = (~test.seen.values) & (test.chunks.values == b)
        v = rep_d[m]
        ch.append({"chunks": b, "unseen April reports": f"{m.sum():,}",
                   "nearest distance, median [quartiles]": describe(v)[0],
                   "window share, median [quartiles]": describe(rep_w[m])[0]})
    neb_q = {sub: point["released Nebula"][sub]["tpr1%_a"] for sub, _ in masks}
    qs = [k for k in neb_q if k.startswith("distance Q")]
    rest = [100 * neb_q[q] for q in qs[1:]]
    decision = (f"\"Unseen\" is mostly near January: the median unseen sequence differs from its nearest January sequence "
                f"in {100 * np.median(dist):.1f}% of its calls, and the median share of its {WIN}-call windows already seen in "
                f"January is {100 * np.nanmedian(wshare):.0f}%; released Nebula catches {100 * neb_q[qs[0]]:.1f}% of malware in "
                f"the nearest quartile but only {min(rest):.1f}%–{max(rest):.1f}% in the other three (not monotone, wide intervals).")
    json.dump({"median_dist": float(np.median(dist)), "quartiles_dist": qd.tolist(), "quartiles_window": qw.tolist(),
               "nebula_tpr1_a_by_quartile": neb_q, "n_short": n_short, "decision": decision},
              open(f"{C.OUT}/test3.json", "w"), indent=1, default=float)
    txt = ("## Test 3: how far is \"unseen\"?\n\n"
           f"{len(seqdf):,} unique April API-name sequences do not occur in January ({len(unseen_rows):,} reports); "
           f"{len(rep_jan):,} unique January sequences. All of them were compared (no sampling): Jaccard shortlist of "
           f"{TOP} on call 3-grams, then Levenshtein distance in calls / longer length (rapidfuzz). "
           f"{exact} unseen sequences have distance 0 (expected: an exact match would make them seen). Window share is undefined for {n_short} sequences shorter than "
           f"{WIN} calls. Label rows count (sequence, label) pairs.\n\n"
           + C.md_table(dist_t) + "\n**Histogram (number of (sequence, label) pairs):**\n\n" + C.md_table(hist_t) +
           "\n**Unseen April reports by number of chunks:**\n\n" + C.md_table(pd.DataFrame(ch)) +
           "\n**Detection by distance quartile and by window share** (quartiles over unique unseen sequences; the window "
           "share has its median at 100%, so it is split into 100%, the rest above its lowest quartile, the lowest "
           "quartile, and sequences too short for a window; global April thresholds (a) and January thresholds (b); "
           "95% intervals from the group bootstrap):\n\n" + C.md_table(pd.DataFrame(det)) +
           f"\n**Decision.** {decision}\n")
    open(f"{C.OUT}/parts_test3.md", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
