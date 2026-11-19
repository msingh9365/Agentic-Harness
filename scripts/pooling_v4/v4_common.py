"""
Shared code of round 4 (results/pooling_v4): benign-call padding with the EVAL pool, model loading and scoring, tables.

Padding test (a robustness measurement, as results/robustness item 2): k = 1, 5, 20, 50 calls, each a random call of a random
report of the EVAL pool (benign January reports, results/pooling_v4/pools.json), inserted at random places ("insert k") or in
front of the first call ("prepend k"); the edited report is re-tokenised. The edits are made in memory; only scores are cached.
Applied to every April malware report (9,399) and to 2,000 random benign April reports (to measure the false-positive rate of
padded benign reports). Random padding, fixed k, nothing optimised.
"""
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
from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL, V2_MAXLEN  # noqa: E402
from perturb_check import _init, _W  # noqa: E402

KS = [1, 5, 20, 50]
EDITS = [f"insert {k}" for k in KS] + [f"prepend {k}" for k in KS]
WORK = "/Users/manish/Code/mtp/pooling_v2_work"
NEBULA = "../nebula"
OUT = "results/pooling_v4"
N_BEN_SUB = 2000

# where each model family lives: (output folder, run-name template, epoch whose April logits are the unedited ones, maxlen)
SRC = {
    "A": ("/Users/manish/Code/mtp/pooling_v2_all_output", "A_all_s{s}", 1, 512),
    "C": ("/Users/manish/Code/mtp/pooling_v2_all_output", "C_all_s{s}", 10, 512),
    "F": ("/Users/manish/Code/mtp/fulltrace_output", "F_all_s{s}", 10, 4096),
    # control: C of the 10-epoch run of regime J after its epoch 2 (same data order and LR schedule as a 2-epoch run; weights from the fp16 epoch checkpoint)
    "C2": ("/Users/manish/Code/mtp/pooling_v2_all_output", "C_all_s{s}", 2, 512),
}


def pools():
    p = json.load(open(f"{OUT}/pools.json"))
    return p["eval_rows"], p["train_rows"]


def _init_pool(nebula, pool_rows):
    _init(nebula)
    _W["pool"] = [list(_W["reps"].get(int(r)).get("apis") or []) for r in pool_rows]


def pad_edit(apis, row, k, mode, pool):
    """k calls from the pool added to apis. Deterministic given (row, k, mode)."""
    rng = np.random.default_rng([6000, int(row), k, 0 if mode == "insert" else 1])
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
    nb, rep, pool = _W["nb"], _W["reps"].get(int(row)), _W["pool"]
    apis = list(rep.get("apis") or [])
    out, lens = [], []
    for mode in ("insert", "prepend"):
        for k in KS:
            if not apis:
                t = nb.ids(rep)
            else:
                r = dict(rep); r["apis"] = pad_edit(apis, row, k, mode, pool); t = nb.ids(r)
            out.append(np.asarray(t[:4096], dtype=np.uint16)); lens.append(len(t))
    return int(row), out, lens


def april():
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    return test, test.label.values


def padded_sets(workers=4, limit=0):
    """Tokenise the padded April reports. Returns dict: rows (report rows), idx (positions in the April table), edits
    tokens [8][n] (uint16, up to 4096 tokens), lens [8, n]."""
    test, y = april()
    mal = np.flatnonzero(y == 1)
    ben = np.flatnonzero(y == 0)
    ben = np.sort(np.random.default_rng(7).choice(ben, N_BEN_SUB, replace=False))
    pos = np.concatenate([mal, ben])
    if limit:
        pos = np.concatenate([mal[:limit], ben[:limit]])
    ev, _ = pools()
    t0 = time.time()
    with Pool(workers, initializer=_init_pool, initargs=(NEBULA, ev)) as pool:
        res = list(pool.imap(_tok, test.row.values[pos], chunksize=32))
    toks = [[r[1][j] for r in res] for j in range(len(EDITS))]
    lens = np.array([r[2] for r in res]).T
    print(f"tokenised {len(pos):,} padded reports x {len(EDITS)} edits in {time.time() - t0:.0f}s", flush=True)
    return {"pos": pos, "n_mal": int(len(pos) - len(ben) if not limit else limit), "toks": toks, "lens": lens}


def to512(toks):
    x = np.zeros((len(toks), 512), dtype=np.int64)
    for i, t in enumerate(toks):
        t = t[:512]; x[i, :len(t)] = t
    return x


@torch.no_grad()
def score512(model, x, bs=128):
    out = np.zeros(len(x))
    for i in range(0, len(x), bs):
        out[i:i + bs] = model(torch.from_numpy(x[i:i + bs])).squeeze(-1).double().numpy()
    return out


@torch.no_grad()
def score_ragged(model, toks, bs=64):
    """logits of a list of token arrays of different lengths (sorted by length, padded per batch to a multiple of 64)."""
    order = np.argsort([-len(t) for t in toks], kind="stable")
    out = np.zeros(len(toks))
    for i in range(0, len(toks), bs):
        sel = order[i:i + bs]
        L = max(64, int(-(-max(len(toks[j]) for j in sel) // 64) * 64))
        x = np.zeros((len(sel), L), dtype=np.int64)
        for r, j in enumerate(sel):
            x[r, :len(toks[j])] = toks[j]
        out[sel] = model(torch.from_numpy(x)).squeeze(-1).double().numpy()
    return out


def load_model(fam, s, src=None):
    """(model, maxlen, unedited April logits) of family fam ('released', 'A', 'C', 'F', or a v4 family in `src`)."""
    if fam == "released":
        m = build_level1(NEBULA, vocab_size=50001, pretrained=True).eval()
        plain = np.load(os.path.join(WORK, "perturbed_tokens_17402.npz"))["plain"].astype(np.int64)
        return m, 512, score512(m, plain)
    out, tmpl, ep, maxlen = (src or SRC)[fam]
    run = tmpl.format(s=s)
    m = build_variant(NEBULA, V2_TO_INTERNAL["C" if fam == "C2" else fam], maxlen=maxlen).eval()
    ck = os.path.join(out, "ckpt", run, "epochs", "epoch_02.pt") if fam == "C2" else os.path.join(out, "ckpt", run, "final.pt")
    sd = torch.load(ck, map_location="cpu", weights_only=True)
    m.load_state_dict({k: (v.float() if v.is_floating_point() else v) for k, v in sd.items()})
    z0 = np.load(os.path.join(out, "scores", f"{run}_epochs.npz"))["april"][ep - 1]
    return m, maxlen, z0


def padded_logits(P, fam, s, src=None, cache=True):
    """(z0 [N_april], ze [8, n_reports]) of one model. Cached as scores only."""
    key = f"{fam}_s{s}" if fam != "released" else "released"
    path = os.path.join(WORK, f"v4_pad_logits_{key}.npz")
    if cache and os.path.exists(path):
        d = np.load(path)
        if d["ze"].shape == (len(EDITS), len(P["pos"])):
            return d["z0"], d["ze"]
    t0 = time.time()
    m, maxlen, z0 = load_model(fam, s, src)
    if maxlen == 512:
        ze = np.stack([score512(m, to512(P["toks"][j])) for j in range(len(EDITS))])
    else:
        ze = np.stack([score_ragged(m, P["toks"][j]) for j in range(len(EDITS))])
    if cache:
        np.savez(path, z0=z0, ze=ze)
    print(f"  scored {key} in {time.time() - t0:.0f}s", flush=True)
    return z0, ze


