#!/usr/bin/env python
"""
Build the Kaggle dataset "nebula-speakeasy-tokens": every Speakeasy report tokenised once with the
released Nebula BPE tokenizer (nebula/objects/bpe_50000_*), first 512 tokens, as Nebula's own input.

    python scripts/kaggle/make_token_dataset.py --stage <empty folder> [--nebula ../nebula] [--data-dir ../hf-git]

Runs hier_nebula.data.prepare (the repository's tokenisation: Nebula's filter_and_normalize_report +
BPE, order of measure_lengths.list_files), then writes into --stage:
    tokens_512.npy   int32 [92700, 512], pad id 0 (what tokenizer.encode(report, pad=True) gives)
    labels.npy       int8  [92700]
    rows.csv         row, id, split, family, label, n_tokens_full, n_chunks, hash_apis, side
                     (side = train / val / test from results/signal/val_split.csv: January grouped train,
                      January validation, April test)
    meta.csv         copy of results/hier/data/meta.csv
    val_split.csv    copy of results/signal/val_split.csv
    manifest.json    counts, sha256 of the files and of the tokenizer files, Nebula commit
    dataset-metadata.json
Checks before it finishes: rows match results/hier/data/meta.csv exactly (id, split, label, n_chunks,
n_tokens_full); and the released Nebula, run on tokens_512.npy, reproduces results/hier/data/
nebula_score_chunk0.npy (max |diff| < 1e-4) on a sample of reports including all shorter than 512 tokens.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO)
os.chdir(REPO)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--data-dir", default="../hf-git")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--owner", default="msingh9365")
    a = ap.parse_args()
    stage = os.path.abspath(a.stage)
    assert not os.path.exists(stage) or not os.listdir(stage), f"{stage} must be empty"
    os.makedirs(stage, exist_ok=True)
    full = stage + "_full_tokens"                       # prepare() output (up to 8 x 512 tokens), not uploaded

    from hier_nebula.data import prepare
    ref = pd.read_csv("results/hier/data/meta.csv")
    if os.path.exists(os.path.join(full, "meta.csv")):                 # --reuse: keep an earlier tokenisation
        new = pd.read_csv(os.path.join(full, "meta.csv"))
    else:
        new = prepare("speakeasy", a.data_dir, full, a.nebula, max_chunks=8, workers=a.workers)
    # The order of files on disk (measure_lengths.list_files) differs between machines, so match every
    # report to its row in results/hier/data/meta.csv by (split, family, id); the committed row order is
    # what the rest of the repository is joined on.
    key = lambda d: list(zip(d.split, d.family, d.id))
    pos = {k: i for i, k in enumerate(key(new))}
    assert len(pos) == len(new), "(split, family, id) is not unique"
    perm = np.array([pos[k] for k in key(ref)])                         # perm[r] = index in `new` of meta row r
    assert len(set(perm.tolist())) == len(ref) == len(new)
    new = new.iloc[perm].reset_index(drop=True)
    for c in ["id", "split", "family", "label", "n_tokens_full", "n_chunks"]:
        assert (new[c].values == ref[c].values).all(), f"column {c} differs from results/hier/data/meta.csv"
    print(f"ok: {len(new):,} reports re-ordered to results/hier/data/meta.csv ({int((perm != np.arange(len(perm))).sum()):,} "
          f"rows moved); labels, token counts and chunk counts equal meta.csv", flush=True)

    toks = np.load(os.path.join(full, "tokens.npy"), mmap_mode="r")
    off = np.load(os.path.join(full, "offsets.npy"))
    N = len(new)
    X = np.zeros((N, 512), dtype=np.int32)
    for r in range(N):
        i = perm[r]
        t = toks[off[i]:min(off[i + 1], off[i] + 512)]
        X[r, :len(t)] = t
    assert X.max() < 50001 and X.min() >= 0
    np.save(os.path.join(stage, "tokens_512.npy"), X)
    np.save(os.path.join(stage, "labels.npy"), ref.label.values.astype(np.int8))

    from signal_lib import load_meta, load_nebula, nebula_scores
    meta = load_meta()
    assert len(meta) == N and (meta.id.values == ref.id.values).all()
    rows = meta[["row", "id", "split", "family", "label", "n_tokens_full", "n_chunks", "hash_apis"]].copy()
    rows["side"] = meta.side.values
    rows.to_csv(os.path.join(stage, "rows.csv"), index=False)
    shutil.copy("results/hier/data/meta.csv", os.path.join(stage, "meta.csv"))
    shutil.copy("results/signal/val_split.csv", os.path.join(stage, "val_split.csv"))
    print("sides:", rows.side.value_counts().to_dict(), flush=True)

    # the released Nebula on these arrays must give its stored scores
    rng = np.random.default_rng(0)
    short = np.flatnonzero(ref.n_tokens_full.values < 512)
    sample = np.unique(np.concatenate([rng.choice(N, 4000, replace=False), short[:1500]]))
    z = nebula_scores(load_nebula(a.nebula).eval(), X[sample])
    d = float(np.abs(z - meta.nebula.values[sample]).max())
    print(f"released Nebula on tokens_512.npy vs nebula_score_chunk0.npy: {len(sample)} reports "
          f"({int((ref.n_tokens_full.values[sample] < 512).sum())} shorter than 512 tokens), max |diff| = {d:.2e}", flush=True)
    assert d < 1e-4, "tokens_512.npy does not reproduce the released Nebula scores"

    commit = subprocess.check_output(["git", "-C", a.nebula, "rev-parse", "HEAD"], text=True).strip()
    obj = os.path.join(a.nebula, "nebula", "objects")
    files = ["tokens_512.npy", "labels.npy", "rows.csv", "meta.csv", "val_split.csv"]
    man = {"n_reports": N, "seq_len": 512, "dtype": "int32", "pad_id": 0, "vocab_size": 50001,
           "nebula_commit": commit, "tokenizer": "bpe_50000 (released)",
           "tokenizer_sha256": {f: sha(os.path.join(obj, f)) for f in
                                ("bpe_50000_sentencepiece.model", "bpe_50000_vocab.json", "bpe_50000_torch.model")},
           "sides": rows.side.value_counts().to_dict(), "check_max_abs_diff_vs_released_nebula": d,
           "check_n_reports": int(len(sample)), "sha256": {f: sha(os.path.join(stage, f)) for f in files}}
    json.dump(man, open(os.path.join(stage, "manifest.json"), "w"), indent=1)
    json.dump({"title": "nebula-speakeasy-tokens", "id": f"{a.owner}/nebula-speakeasy-tokens",
               "licenses": [{"name": "other"}],
               "description": "Speakeasy reports tokenised with the released Nebula BPE tokenizer (first 512 tokens)."},
              open(os.path.join(stage, "dataset-metadata.json"), "w"), indent=1)
    size = sum(os.path.getsize(os.path.join(stage, f)) for f in os.listdir(stage))
    print(f"staged {len(os.listdir(stage))} files, {size / 2**20:.1f} MiB in {stage}")


if __name__ == "__main__":
    main()
