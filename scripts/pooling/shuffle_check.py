#!/usr/bin/env python
"""
Sanity check: score the trained A, B, C models on the April reports with the ORDER OF THE API CALLS shuffled.

    python scripts/pooling/shuffle_check.py --src <Kaggle output folder> [--nebula ../nebula]

For every April report: Nebula's filtered report (analyze_signal.py collect, reps.bin) with its list of API
calls ("apis") put in a random order (numpy Generator seeded with 1000 + row), then Nebula's own tokenisation,
first 512 tokens. Each call keeps its own fields; only the order changes. A model that uses call order loses
accuracy; a bag-of-calls model would not.

Also checks the pipeline: with the UNshuffled order the CPU scores of the downloaded checkpoints must equal the
logits written by the Kaggle run (max |difference| < 0.05), and the unshuffled tokens must equal the first 512
tokens of the token dataset when it is given with --tokens.

Writes results/pooling/shuffle_check.json (AUC, TPR at 1% FPR with the April threshold (a) of the same score
vector, and TPR / FPR at the January-validation threshold (b) taken from the unshuffled model).
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

from hier_nebula.pooling_variants import build_variant  # noqa: E402

_W = {}


def _init(nebula):
    from measure_lengths import Nebula
    _W["nb"] = Nebula(nebula)
    _W["reps"] = C.Reps()


def _tok(row):
    rep = _W["reps"].get(int(row))
    plain = _W["nb"].ids(rep)[:512]
    apis = list(rep.get("apis") or [])
    perm = np.random.default_rng(1000 + int(row)).permutation(len(apis))
    rep2 = dict(rep)
    rep2["apis"] = [apis[i] for i in perm]
    shuf = _W["nb"].ids(rep2)[:512]
    return int(row), np.asarray(plain, dtype=np.int32), np.asarray(shuf, dtype=np.int32)


def pad(lst):
    x = np.zeros((len(lst), 512), dtype=np.int64)
    for i, t in enumerate(lst):
        x[i, :len(t)] = t
    return x


@torch.no_grad()
def logits(model, x, bs=256):
    out = np.zeros(len(x))
    for i in range(0, len(x), bs):
        out[i:i + bs] = model(torch.from_numpy(x[i:i + bs])).squeeze(-1).double().numpy()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--tokens", default=None, help="folder of tokens_512.npy, to check the unshuffled tokens")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--variants", default="ABC")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--limit", type=int, default=0, help="debug: first N April reports")
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    rows = test.row.values[:a.limit] if a.limit else test.row.values
    y = test.label.values[:len(rows)]
    seeds = [int(s) for s in a.seeds.split(",")]

    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
        res = list(pool.imap(_tok, rows, chunksize=32))
    assert [r[0] for r in res] == list(rows)
    plain, shuf = pad([r[1] for r in res]), pad([r[2] for r in res])
    moved = float(np.mean([(p != s).any() for p, s in zip(plain, shuf)]))
    print(f"tokenised {len(rows):,} April reports twice in {time.time() - t0:.0f}s; "
          f"{100 * moved:.1f}% of the shuffled token sequences differ from the original", flush=True)
    if a.tokens:
        ref = np.load(os.path.join(a.tokens, "tokens_512.npy"), mmap_mode="r")[rows]
        assert np.array_equal(ref.astype(np.int64), plain), "unshuffled tokens differ from tokens_512.npy"
        print("ok: unshuffled tokens equal tokens_512.npy for all April reports", flush=True)

    out = {"n_reports": int(len(rows)), "share_sequences_changed": moved, "runs": {}}
    for v in a.variants:
        for s in seeds:
            ck = os.path.join(a.src, "ckpt", f"{v}_s{s}", "best.pt")
            if not os.path.exists(ck):
                print("missing", ck)
                continue
            m = build_variant(os.path.join(a.nebula), v).eval()
            m.load_state_dict(torch.load(ck, map_location="cpu", weights_only=True))
            z_plain, z_shuf = logits(m, plain), logits(m, shuf)
            kg = pd.read_parquet(os.path.join(a.src, "scores", f"pool_{v}_seed{s}_april.parquet")).set_index("row").logit
            d = float(np.abs(z_plain - kg.loc[rows].values).max())
            kv = pd.read_parquet(os.path.join(a.src, "scores", f"pool_{v}_seed{s}_janval.parquet")).set_index("row").logit
            thr_b = {f: C.thr_from(val.label.values, kv.loc[val.row.values].values, f) for f, _ in C.FPRS}
            r = {"max_abs_logit_diff_vs_kaggle": d}
            for tag, z in (("original", z_plain), ("shuffled", z_shuf)):
                sc = C.Scorer(y, z, thr_b)
                mt = sc.metrics(np.ones(len(y)), [("all", np.ones(len(y), bool))])["all"]
                r[tag] = {"auc": mt["auc"], "tpr1_a": mt["tpr1%_a"], "tpr1_b": mt["tpr1%_b"], "fpr1_b": mt["fpr1%_b"],
                          "tpr01_a": mt["tpr0.1%_a"]}
            out["runs"][f"{v}_s{s}"] = r
            print(f"{v} seed {s}: |logit - Kaggle| max {d:.4f} | AUC {r['original']['auc']:.4f} -> {r['shuffled']['auc']:.4f} | "
                  f"TPR@1% (a) {100 * r['original']['tpr1_a']:.1f}% -> {100 * r['shuffled']['tpr1_a']:.1f}%", flush=True)
            if not a.limit:
                assert d < 0.05, f"CPU logits differ from the Kaggle run for {v} seed {s}: {d}"
    os.makedirs("results/pooling", exist_ok=True)
    json.dump(out, open("results/pooling/shuffle_check.json" if not a.limit else "results/pooling/shuffle_check_debug.json", "w"),
              indent=1)


if __name__ == "__main__":
    main()
