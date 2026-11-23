"""
ITEM R1 (NOTES 30.3), attack scores of the windowed models (scores only; edited reports exist in memory only; April opening 32).   (OURS)

    python -m baseline.r1_attack --search <dir with r1/seed<k>.pt and r1/seed<k>_april.npy> --out out [--seeds 0 ... 9]

Windows as baseline/r1.py (stride 512, at most 64, report logit = max over windows). Sets (13, in this order): unedited; random prepend k = 20, 50, 60, 75, 100, 200; random insert k = 20, 50, 200; LightGBM 50 prepend and insert
(ranking_gs.json: the 50 top-ranked representative calls); `adaptive_50_every_window` (fixed in NOTES 30.3): 50 random pool calls (default_rng([6100, April row, window index]), per call a uniform pool report of the
3,161 held-out benign reports, then a uniform call of it) are inserted at the first call boundary at or after the start of EVERY window of the edited sequence (window starts 0, 512, 1,024, ..., at most 64 windows).
Random / LightGBM sets use the sampler of Stage J (make_pad.plan_test_row; insert gaps default_rng([8000, row, k, 0]); reports without calls stay unedited in the random sets, as in Stage J; the LightGBM sets apply to every report).
Check (assert): the unedited scores equal the stored April logits of every seed (tolerance 2e-3). Output: scores_r1.npz (names, tot = total tokens of the edited report, seed<k> = [sets, 17,402] float32), checks_r1.json.
"""
import argparse
import json
import os
import time

import numpy as np

from baseline import callstore as CS, common as C, groupsplit as G, make_pad, pe
from baseline.r1 import CHUNK, CUT, MAXW, report_max, score_windows, windows_from

SETS = [("unedited", "none", 0, None)] + [(f"random_{k}_prepend", "random", k, "prepend") for k in (20, 50, 60, 75, 100, 200)] + [(f"random_{k}_insert", "random", k, "insert") for k in (20, 50, 200)] + \
       [("lgbm_50_prepend", "lgbm", 50, "prepend"), ("lgbm_50_insert", "lgbm", 50, "insert"), ("adaptive_50_every_window", "adaptive", 50, None)]


def adaptive_sequence(store, r, t, pool, pool_n, n_ins=50):
    """token sequence (uint16) of April report r (row t) with n_ins pool calls inserted at the start of every window"""
    n = store.n_calls(r)
    h = store.head(r)
    parts, cur, wi, next_start, i = [h], len(h), 0, 0, 0
    while True:
        while wi < MAXW and cur >= next_start:
            rng = np.random.default_rng([6100, int(t), wi])
            for _ in range(n_ins):
                pr = int(rng.integers(len(pool)))
                a = store.call(int(pool[pr]), int(rng.integers(pool_n[pr])))
                parts.append(a)
                cur += len(a)
            wi += 1
            next_start = wi * CHUNK
        if i >= n:
            break
        c = store.call(r, i)
        parts.append(c)
        cur += len(c)
        i += 1
    parts.append(store.tail(r))
    seq = np.concatenate(parts)
    return seq


def build_row(store, ntr, t, spec, pool, pool_n, ranking_arr):
    name, kind, k, mode = spec
    r = ntr + t
    n = store.n_calls(r)
    if kind == "none" or (kind in ("random", "adaptive") and n == 0):
        tok = store.report_tokens(r)
        return windows_from(tok, len(tok)), len(tok)
    if kind == "adaptive":
        seq = adaptive_sequence(store, r, t, pool, pool_n)
        return windows_from(seq, len(seq)), len(seq)
    if kind == "random":
        plan = make_pad.plan_test_row(t, k, mode, n, pool_n)
        added = [store.call(int(pool[pr]), int(c)) for pr, c in plan["draws"]]
        gaps = plan["gaps"] if mode == "insert" else None
    else:
        added = ranking_arr
        gaps = np.sort(np.random.default_rng([8000, int(r), k, 0]).integers(0, n + 1, k)) if mode == "insert" else None
    tok, total = CS.build_fast(store, r, added, gaps, cut=CUT)
    return windows_from(tok, total), int(total)


def main():
    import torch
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", required=True)
    ap.add_argument("--family", default="r1", choices=["r1", "m3"], help="weights folder: r1 (the windowed models, report logit = max over windows) or m3 (the final M3: writes scores_m3_first.npz = first window only = the plain M3, and scores_m3_mw.npz = max over windows = the test-time multi-window baseline)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--ranking", default="ranking_gs.json")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--chunk", type=int, default=256)
    ap.add_argument("--limit-test", type=int, default=0, help="smoke test only: the first N April reports")
    a = ap.parse_args()
    nb = C.setup_nebula(require_patched=True)
    tokens = C.find_dir_with("all.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    y_all = lab["y_train"]
    ntr = len(y_all)
    vocab = json.load(open(os.path.join(tokens, "variants", "bpe50k_fix", "vocab.json")))
    store = CS.CallStore.load(a.store if os.path.exists(a.store) else os.path.join(tokens, a.store))
    sd = a.split_dir if os.path.exists(os.path.join(a.split_dir, "split.npz")) else C.find_dir_with("split.npz")
    trn, val = G.val_slice(os.path.join(sd, "split.npz"), os.path.join(sd, "split_hash.json"))
    pool = np.array([int(r) for r in val if y_all[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    pool_n = np.array([store.n_calls(int(r)) for r in pool], dtype=np.int64)
    rk = json.load(open(a.ranking if os.path.exists(a.ranking) else os.path.join(C.find_dir_with(os.path.basename(a.ranking)), os.path.basename(a.ranking))))
    assert len(pool) == rk["eval_pool_n"] == 3161
    rep_call = {int(i): v for i, v in rk["rep_call"].items()}
    ranking_arr = [store.call(rep_call[int(nm)][0], rep_call[int(nm)][1]) for nm in rk["rank_lgbm"][:50]]
    n_test = a.limit_test or 17402
    models = {}
    for s in a.seeds:
        p = os.path.join(a.search, a.family, f"seed{s}.pt")
        if not os.path.exists(p):
            for dp, dn, fn in os.walk(a.search):
                if os.path.basename(dp) == a.family and f"seed{s}.pt" in fn:
                    p = os.path.join(dp, f"seed{s}.pt")
        m = pe.build_chunks(len(vocab), pe_mode="paper", pool_mode="attn")
        m.load_state_dict(torch.load(p, map_location="cpu", weights_only=True))
        models[s] = m.to(a.device).eval()
    res = {s: np.zeros((len(SETS), n_test), dtype=np.float32) for s in a.seeds}
    first = {s: np.zeros((len(SETS), n_test), dtype=np.float32) for s in a.seeds}
    tot = np.zeros((len(SETS), n_test), dtype=np.int64)
    t0 = time.time()
    for j, spec in enumerate(SETS):
        for c0 in range(0, n_test, a.chunk):
            Ws, counts = [], []
            for t in range(c0, min(c0 + a.chunk, n_test)):
                w, total = build_row(store, ntr, t, spec, pool, pool_n, ranking_arr)
                Ws.append(w)
                counts.append(len(w))
                tot[j, t] = total
            W, counts = np.concatenate(Ws), np.asarray(counts)
            for s in a.seeds:
                z = score_windows(models[s], W, a.device, bs=2048)
                res[s][j, c0:c0 + len(counts)] = report_max(z, counts)
                first[s][j, c0:c0 + len(counts)] = z[np.concatenate([[0], np.cumsum(counts)[:-1]])]
        print(f"set {j} {spec[0]} scored for {len(a.seeds)} seeds ({time.time() - t0:.0f}s)", flush=True)
    chk = {}
    for s in a.seeds:
        pth = os.path.join(a.search, a.family, f"seed{s}_april.npy")
        if not os.path.exists(pth):
            for dp, dn, fn in os.walk(a.search):
                if os.path.basename(dp) == a.family and f"seed{s}_april.npy" in fn:
                    pth = os.path.join(dp, f"seed{s}_april.npy")
        ref = np.load(pth).astype(np.float64).reshape(-1)[:n_test]
        d = float(np.abs(ref - (first if a.family == "m3" else res)[s][0].astype(np.float64)).max())      # r1: the report logit (max); m3: the plain first-window logit
        chk[f"seed{s}"] = d
        assert d < 2e-3, f"seed {s}: unedited scores differ from the stored April logits by {d}"
    os.makedirs(a.out, exist_ok=True)
    names = np.array([s[0] for s in SETS])
    if a.family == "m3":
        np.savez_compressed(os.path.join(a.out, "scores_m3_first.npz"), names=names, tot=tot, **{f"seed{s}": first[s] for s in a.seeds})
        np.savez_compressed(os.path.join(a.out, "scores_m3_mw64.npz"), names=names, tot=tot, **{f"seed{s}": res[s] for s in a.seeds})
    else:
        np.savez_compressed(os.path.join(a.out, "scores_r1.npz"), names=names, tot=tot, **{f"seed{s}": res[s] for s in a.seeds})
    json.dump({"family": a.family, "unedited_vs_stored_april_logits_max_abs_diff": chk, "n_sets": len(SETS)}, open(os.path.join(a.out, f"checks_{a.family}.json"), "w"), indent=1)
    print("done", json.dumps(chk), flush=True)


if __name__ == "__main__":
    main()
