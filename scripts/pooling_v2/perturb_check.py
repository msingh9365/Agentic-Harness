#!/usr/bin/env python
"""
Robustness checks for the pooling_v2 models on the April reports.

    python scripts/pooling_v2/perturb_check.py --src <Kaggle output folder> --work <folder for the token cache>

For every April report (Nebula's filtered report, reps.bin from analyze_signal.py collect), three inputs:
  original : as is
  shuffled : the order of the API calls randomly permuted (numpy Generator seeded 1000 + row); as results/pooling
  inserted : 5 extra API calls inserted at random places. Each inserted call is a copy of a call of the SAME report
             taken from elsewhere (not one of the two neighbours of the insertion point); positions are drawn uniformly
             over the gaps of the call list, seed 2000 + row. Reports without API calls are left unchanged.
Each input is tokenised with Nebula's own tokenizer and cut to the first 512 tokens.

"Without changing which calls fit": inserting calls before the 512-token cut pushes later calls out of the window.
Two views are reported:
  all reports         : the model input is the first 512 tokens of the edited report, whatever is pushed out
  unaffected reports  : only reports whose whole edited token sequence is at most 512 tokens, so that every original
                        call is still inside the window (the edit adds calls and removes none); "before" and "after"
                        are computed on exactly these reports.
Models: the checkpoint chosen by validation AUC (ckpt/<V>_s<N>/best_auc.pt) of the variants given (v2 names A, B, C).
CPU logits of the unperturbed input must equal the Kaggle logits of the same epoch (checked for seed 0 of each variant).
Output: results/pooling_v2/perturb_check.json
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "go_no_go"))
import common as C  # noqa: E402

from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL  # noqa: E402

_W = {}
N_INSERT = 5


def _init(nebula):
    from measure_lengths import Nebula
    _W["nb"] = Nebula(nebula)
    _W["reps"] = C.Reps()


def insert_calls(apis, row, k=N_INSERT):
    n = len(apis)
    if n == 0:
        return list(apis)
    rng = np.random.default_rng(2000 + int(row))
    gaps = np.sort(rng.integers(0, n + 1, k))
    picks = []
    for g in gaps:
        cand = [i for i in range(n) if i not in (g - 1, g)] or list(range(n))     # not a neighbour of the insertion point
        picks.append(int(rng.choice(cand)))
    out, j = [], 0
    for i in range(n + 1):
        while j < k and gaps[j] == i:
            out.append(apis[picks[j]]); j += 1
        if i < n:
            out.append(apis[i])
    assert len(out) == n + k
    return out


def _tok(row):
    nb, rep = _W["nb"], _W["reps"].get(int(row))
    apis = list(rep.get("apis") or [])
    plain = nb.ids(rep)
    r1 = dict(rep); r1["apis"] = [apis[i] for i in np.random.default_rng(1000 + int(row)).permutation(len(apis))]
    r2 = dict(rep); r2["apis"] = insert_calls(apis, row)
    shuf, ins = nb.ids(r1), nb.ids(r2)
    cut = lambda t: np.asarray(t[:512], dtype=np.int32)
    return int(row), cut(plain), cut(shuf), cut(ins), len(plain), len(ins)


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


def metrics(y, z, thr_b):
    sc = C.Scorer(y, z, thr_b)
    m = sc.metrics(np.ones(len(y)), [("all", np.ones(len(y), bool))])["all"]
    return {"auc": float(m["auc"]), "tpr1_a": float(m["tpr1%_a"]), "tpr1_b": float(m["tpr1%_b"]), "fpr1_b": float(m["fpr1%_b"])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--work", required=True, help="folder for the cached token arrays")
    ap.add_argument("--nebula", default="../nebula")
    ap.add_argument("--tokens", default=None, help="folder with tokens_512.npy, to check the unperturbed tokens")
    ap.add_argument("--variants", default="A,B,C")
    ap.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    ap.add_argument("--select", default="auc", choices=["auc", "tpr", "final"])
    ap.add_argument("--tag", default="", help="run-name suffix, e.g. _all")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    val = meta[meta.side == "val"].reset_index(drop=True)
    rows = test.row.values[:a.limit] if a.limit else test.row.values
    y = test.label.values[:len(rows)]
    os.makedirs(a.work, exist_ok=True)
    cache = os.path.join(a.work, f"perturbed_tokens_{len(rows)}.npz")
    if os.path.exists(cache):
        d = np.load(cache)
        plain, shuf, ins, n_plain, n_ins = d["plain"], d["shuf"], d["ins"], d["n_plain"], d["n_ins"]
    else:
        t0 = time.time()
        with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
            res = list(pool.imap(_tok, rows, chunksize=32))
        assert [r[0] for r in res] == list(rows)
        plain, shuf, ins = (pad([r[i] for r in res]) for i in (1, 2, 3))
        n_plain, n_ins = np.array([r[4] for r in res]), np.array([r[5] for r in res])
        np.savez(cache, plain=plain, shuf=shuf, ins=ins, n_plain=n_plain, n_ins=n_ins)
        print(f"tokenised {len(rows):,} reports three ways in {time.time() - t0:.0f}s", flush=True)
    unaffected = n_ins <= 512
    print(f"shuffled sequences that differ from the original: {100 * np.mean((plain != shuf).any(1)):.1f}%; "
          f"inserted: {100 * np.mean((plain != ins).any(1)):.1f}%; reports whose whole edited sequence fits in 512 tokens "
          f"(no original call pushed out): {int(unaffected.sum()):,} ({100 * unaffected.mean():.1f}%), "
          f"of which malware {int(y[unaffected].sum()):,}", flush=True)
    if a.tokens:
        ref = np.load(os.path.join(a.tokens, "tokens_512.npy"), mmap_mode="r")[rows]
        assert np.array_equal(ref.astype(np.int64), plain), "unperturbed tokens differ from tokens_512.npy"
        print("ok: unperturbed tokens equal tokens_512.npy for all April reports", flush=True)

    yv = val.label.values
    out = {"n_reports": int(len(rows)), "n_unaffected": int(unaffected.sum()), "n_unaffected_malware": int(y[unaffected].sum()),
           "share_shuffled_changed": float(np.mean((plain != shuf).any(1))), "share_inserted_changed": float(np.mean((plain != ins).any(1))),
           "select": a.select, "runs": {}}
    for v in a.variants.split(","):
        for s in [int(x) for x in a.seeds.split(",")]:
            run = f"{v}{a.tag}_s{s}"
            lj = os.path.join(a.src, "logs", f"{run}.json")
            ck = os.path.join(a.src, "ckpt", run, "final.pt" if a.select == "final" else f"best_{a.select}.pt")
            if not (os.path.exists(lj) and os.path.exists(ck)):
                print("missing", run); continue
            info = json.load(open(lj))
            npz = np.load(os.path.join(a.src, "scores", f"{run}_epochs.npz"))
            ep = len(npz["april"]) if a.select == "final" else info["epoch_by_val_auc" if a.select == "auc" else "epoch_by_val_tpr1"]
            za_k, zv_k = npz["april"][ep - 1][:len(rows)], npz["janval"][ep - 1]
            m = build_variant(a.nebula, V2_TO_INTERNAL[v]).eval()
            m.load_state_dict(torch.load(ck, map_location="cpu", weights_only=True))
            thr_b = {f: C.thr_from(yv, zv_k, f) for f, _ in C.FPRS}
            r = {"epoch": ep}
            if s == 0 or a.limit:                                   # pipeline check, once per variant
                z0 = logits(m, plain)
                r["max_abs_logit_diff_vs_kaggle"] = float(np.abs(z0 - za_k).max())
                assert r["max_abs_logit_diff_vs_kaggle"] < 0.05, (run, r["max_abs_logit_diff_vs_kaggle"])
            zs, zi = logits(m, shuf), logits(m, ins)
            r["original"] = metrics(y, za_k, thr_b)
            r["shuffled"] = metrics(y, zs, thr_b)
            r["inserted"] = metrics(y, zi, thr_b)
            u = unaffected
            r["unaffected_original"] = metrics(y[u], za_k[u], thr_b)
            r["unaffected_inserted"] = metrics(y[u], zi[u], thr_b)
            # share of April reports whose predicted class at the January threshold (b, 1% FPR) flips
            r["flip_b_inserted"] = float(np.mean((za_k > thr_b[0.01]) != (zi > thr_b[0.01])))
            r["mean_abs_logit_change_inserted"] = float(np.mean(np.abs(zi - za_k)))
            out["runs"][f"{v}_s{s}"] = r
            print(f"{run} (epoch {ep}): AUC {r['original']['auc']:.4f} -> shuffled {r['shuffled']['auc']:.4f}, inserted "
                  f"{r['inserted']['auc']:.4f} | unaffected subset AUC {r['unaffected_original']['auc']:.4f} -> "
                  f"{r['unaffected_inserted']['auc']:.4f}", flush=True)
    os.makedirs("results/pooling_v2", exist_ok=True)
    json.dump(out, open(f"results/pooling_v2/perturb_check{a.tag}.json" if not a.limit else "results/pooling_v2/perturb_check_debug.json", "w"),
              indent=1)


if __name__ == "__main__":
    main()
