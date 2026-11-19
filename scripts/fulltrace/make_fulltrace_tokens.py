#!/usr/bin/env python
"""
Token data for results/fulltrace: up to 4,096 tokens (8 chunks of 512) per report, in the row order of
results/hier/data/meta.csv, stored raggedly (no padding).

    python scripts/fulltrace/make_fulltrace_tokens.py --full <prepare() output folder> --stage <folder>

--full is the folder written by `hier_nebula.train prepare` (tokens.npy uint16, offsets.npy, meta.csv in the order of the files on
disk); its rows are re-keyed to meta.csv order by (split, family, id), as scripts/kaggle/make_token_dataset.py does.
Writes into --stage:  tokens_full.npy (uint16, concatenated), offsets_full.npy (int64 [N+1]), full_manifest.json.
Checks: the first 512 tokens of every report equal tokens_512.npy (when --tokens512 is given), lengths equal
min(n_tokens_full, 4096) of meta.csv.
"""
import argparse
import hashlib
import json
import os

import numpy as np
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--tokens512", default=None, help="folder with tokens_512.npy")
    a = ap.parse_args()
    ref = pd.read_csv("results/hier/data/meta.csv")
    new = pd.read_csv(os.path.join(a.full, "meta.csv"))
    toks = np.load(os.path.join(a.full, "tokens.npy"), mmap_mode="r")
    off = np.load(os.path.join(a.full, "offsets.npy"))
    key = lambda d: list(zip(d.split, d.family, d.id))
    pos = {k: i for i, k in enumerate(key(new))}
    perm = np.array([pos[k] for k in key(ref)])
    assert len(set(perm.tolist())) == len(ref) == len(new)
    lens = (off[1:] - off[:-1])[perm]
    assert (lens == np.minimum(ref.n_tokens_full.values, 4096)).all(), "lengths differ from meta.csv n_tokens_full (capped at 4096)"
    os.makedirs(a.stage, exist_ok=True)
    out = np.zeros(int(lens.sum()), dtype=np.uint16)
    o2 = np.zeros(len(ref) + 1, dtype=np.int64)
    o2[1:] = np.cumsum(lens)
    for r in range(len(ref)):
        i = perm[r]
        out[o2[r]:o2[r + 1]] = toks[off[i]:off[i + 1]]
    if a.tokens512:
        X = np.load(os.path.join(a.tokens512, "tokens_512.npy"), mmap_mode="r")
        for r in range(0, len(ref), 7):
            t = out[o2[r]:o2[r + 1]][:512].astype(np.int32)
            assert np.array_equal(X[r][:len(t)], t) and not X[r][len(t):].any(), r
        print("ok: first 512 tokens equal tokens_512.npy (every 7th report)")
    np.save(os.path.join(a.stage, "tokens_full.npy"), out)
    np.save(os.path.join(a.stage, "offsets_full.npy"), o2)
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    json.dump({"n_reports": len(ref), "max_tokens": 4096, "total_tokens": int(o2[-1]), "dtype": "uint16",
               "mean_tokens": float(lens.mean()), "share_over_512": float((lens > 512).mean()), "share_at_4096_cap": float((lens == 4096).mean()),
               "sha256": {f: h(os.path.join(a.stage, f)) for f in ("tokens_full.npy", "offsets_full.npy")}},
              open(os.path.join(a.stage, "full_manifest.json"), "w"), indent=1)
    print(open(os.path.join(a.stage, "full_manifest.json")).read())


if __name__ == "__main__":
    main()
