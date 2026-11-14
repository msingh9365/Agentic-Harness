#!/usr/bin/env python
"""
Score released Nebula and the two-level 8-chunk model (results/hier/finetune_k8/best.pt) on the April
test set and on the grouped January validation side. Inference only, model.eval(), fixed batch size.

  released Nebula: sigmoid(level1(x)), x = first 512 tokens (tokenizer.encode(report, pad=True)).
                   Must reproduce results/hier/data/nebula_score_chunk0.npy.
  two-level:       HierNebula(K=8) with the finetune_k8 checkpoint, built with the arguments in its
                   result.json. Must reproduce results/hier/finetune_k8/test_scores.csv on April before
                   it is used on January.
Writes results/go_no_go/scores/{nebula,twolevel_k8}_{april,janval}.parquet.
"""
import argparse
import json
import subprocess
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
import torch

import common as C

BATCH = 256
_W = {}


def _init(nebula):
    from measure_lengths import Nebula
    _W["nb"] = Nebula(nebula)
    _W["reps"] = C.Reps()


def _tok(row):
    """-> first 8 * 512 token ids of Nebula's tokenized report (no padding)."""
    ids = _W["nb"].ids(_W["reps"].get(int(row)))
    return row, np.asarray(ids[:8 * 512], dtype=np.int64)


def tokens(pool, rows):
    out = {}
    for r, ids in pool.imap(_tok, rows, chunksize=32):
        out[r] = ids
    return [out[r] for r in rows]


def chunk_batch(ids_list, K=8, L=512):
    k = max(1, max(-(-len(x) // L) for x in ids_list))
    k = min(k, K)
    x = torch.zeros(len(ids_list), k, L, dtype=torch.long)
    mask = torch.zeros(len(ids_list), k, dtype=torch.bool)
    for b, ids in enumerate(ids_list):
        n = max(1, -(-len(ids) // L))
        flat = torch.zeros(n * L, dtype=torch.long)
        flat[:len(ids)] = torch.from_numpy(ids)
        x[b, :n] = flat.view(n, L)
        mask[b, :n] = True
    return x, mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    torch.set_num_threads(4)
    torch.manual_seed(0)
    commit = subprocess.check_output(["git", "-C", a.nebula, "rev-parse", "HEAD"], text=True).strip()
    print(f"Nebula commit: {commit}; batch size {BATCH}; torch {torch.__version__}", flush=True)
    meta = C.meta_full()
    parts = {"april": meta.row.values[meta.split == "testset"], "janval": meta.row.values[meta.side == "val"]}

    from hier_nebula.model import build_level1, HierNebula
    neb = build_level1(a.nebula, vocab_size=50001, pretrained=True).eval()
    args = json.load(open("results/hier/finetune_k8/result.json"))["args"]
    two = HierNebula(build_level1(a.nebula, vocab_size=50001, pretrained=True), max_chunks=args["max_chunks"],
                     num_classes=1, n_layers=args["layers"], dropout=args["dropout"], pool=args.get("pool", "cls"))
    two.load_state_dict(torch.load("results/hier/finetune_k8/best.pt", weights_only=True))
    two.eval()
    print("model.eval(): nebula.training =", neb.training, "; two-level.training =", two.training, flush=True)

    with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
        for part, rows in parts.items():
            t0 = time.time()
            ids = tokens(pool, rows)
            s_neb = np.zeros(len(rows)); s_two = np.zeros(len(rows))
            with torch.no_grad():
                for i in range(0, len(rows), BATCH):
                    b = ids[i:i + BATCH]
                    x0 = torch.zeros(len(b), 512, dtype=torch.long)
                    for j, t in enumerate(b):
                        x0[j, :min(512, len(t))] = torch.from_numpy(t[:512])
                    s_neb[i:i + BATCH] = torch.sigmoid(neb(x0)).squeeze(-1).double().numpy()
                    x, mask = chunk_batch(b)
                    s_two[i:i + BATCH] = torch.sigmoid(two(x, mask)).squeeze(-1).float().double().numpy()
            d = np.abs(s_neb - meta.nebula.values[rows]).max()
            print(f"{part}: {len(rows):,} reports, {time.time() - t0:.0f}s; released Nebula vs "
                  f"nebula_score_chunk0.npy max |diff| = {d:.2e}", flush=True)
            assert d < 1e-4
            if part == "april":
                ref = pd.read_csv("results/hier/finetune_k8/test_scores.csv").set_index("row").score
                d2 = np.abs(s_two - ref.loc[rows].values).max()
                print(f"april: two-level K=8 vs results/hier/finetune_k8/test_scores.csv max |diff| = {d2:.2e}", flush=True)
                if d2 > 1e-4:
                    raise SystemExit("two-level checkpoint does NOT reproduce test_scores.csv: stop and ask")
            C.save_scores("nebula", rows, {0: s_neb}, part)
            C.save_scores("twolevel_k8", rows, {0: s_two}, part)
    json.dump({"nebula_commit": commit, "batch_size": BATCH, "torch": torch.__version__,
               "two_level_args": args}, open(f"{C.OUT}/scoring.json", "w"), indent=1)
    print("wrote", C.SCORES)


if __name__ == "__main__":
    main()
