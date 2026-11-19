"""Checks of the call-token store (baseline/callstore.py): (1) the pieces of an unedited report concatenate to the stored x_train / x_test rows, (2) edits built by concatenation equal the full
re-tokenisation of the edited report, (3) the in-memory edits reproduce, token for token, the balanced-padding arrays of REPORT 5.10 (which were made by full re-tokenisation)."""
import json
import os
import time

import numpy as np

from baseline import callstore as CS, common as C, gap, inmem_pad, make_pad

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PE = os.path.join(ROOT, "results", "_pe_tokens", "variants", "bpe50k")
PAD = os.path.join(ROOT, "results", "_pad_train")


def run(store_dir, n_unedited=3000, n_edited=1500, arrays=((0, 1), (3, 2))):
    store = CS.CallStore.load(os.path.join(store_dir, "all.npz"))
    tr, te = make_pad.load_row_map()
    NTR = len(tr)
    lab = np.load(os.path.join(make_pad.TOKENS, "labels.npz"))
    y = lab["y_train"]
    xtr, xte = np.load(os.path.join(PE, "x_train.npy"), mmap_mode="r"), np.load(os.path.join(PE, "x_test.npy"), mmap_mode="r")
    rng = np.random.default_rng(0)
    # (1) unedited reports
    bad = 0
    idx = rng.choice(NTR + len(te), n_unedited, replace=False)
    for r in idx:
        t, total = CS.build_tokens(store, int(r), list(range(store.n_calls(int(r)))))
        want = xtr[r] if r < NTR else xte[r - NTR]
        bad += int(not np.array_equal(t, np.asarray(want, dtype=np.uint16)))
    print(f"(1) unedited reports rebuilt from the pieces: {bad} of {n_unedited} differ from the stored tokens", flush=True)
    assert bad == 0
    # (2) edits against full re-tokenisation
    tok = make_pad.make_tokenizer()
    reps = make_pad.Reps()
    trn, val = gap.val_slice(lab["ym_train"])
    pool_rows = inmem_pad.pool_rows_of(store, y, trn)
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows])
    bad = n = 0
    for r in rng.choice(trn, n_edited, replace=False):
        r = int(r)
        plan = make_pad.plan_train_row(r, int(rng.integers(10)), int(rng.integers(1, 3)), store.n_calls(r), pool_n, 7100)
        if plan is None:
            plan = make_pad.plan_test_row(r, int(rng.integers(1, 51)), "insert" if rng.random() < 0.5 else "prepend", store.n_calls(r), pool_n) if store.n_calls(r) else None
        if plan is None:
            continue
        mine, total = inmem_pad.edit_row(store, r, plan, pool_rows)
        rep = reps.get(int(tr[r]))
        added = [reps.get(int(tr[int(pool_rows[pr])]))["apis"][c] for pr, c in plan["draws"]]
        r2 = dict(rep)
        r2["apis"] = make_pad.apply_plan(list(rep.get("apis") or []), plan, added)
        full = tok.encode([r2], pad=False)[0]
        n += 1
        bad += int(not (np.array_equal(mine, make_pad.to512(full)) and total == len(full)))
    print(f"(2) edits built by concatenation against full re-tokenisation (tokens and total length): {bad} of {n} differ", flush=True)
    assert bad == 0
    # (3) the arrays of REPORT 5.10
    for s, e in arrays:
        rows_a, tok_a = np.load(os.path.join(PAD, f"aug_s{s}_e{e}_rows.npy")), np.load(os.path.join(PAD, f"aug_s{s}_e{e}_tok.npy"))
        t0 = time.time()
        rows_m, tok_m = inmem_pad.epoch_edits(store, y, trn, s, e, pool_rows, stream=7000, labels="all")
        same_rows = np.array_equal(rows_a, rows_m)
        same_tok = same_rows and np.array_equal(tok_a, tok_m)
        print(f"(3) seed {s} epoch {e}: the §5.10 array has {len(rows_a):,} edited reports; in memory {len(rows_m):,}; rows identical: {same_rows}; tokens identical: {same_tok} ({time.time() - t0:.0f}s)", flush=True)
        assert same_rows and same_tok
    print("store checks passed", flush=True)


def run_released(store_dir, n_unedited=3000, n_edited=1000):
    """The store made with the tokenizer of the released checkpoint: (1) unedited April reports against the stored released-tokenizer x_test, (2) edits against full re-tokenisation with that tokenizer."""
    store = CS.CallStore.load(os.path.join(store_dir, "all_released.npz"))
    tr, te = make_pad.load_row_map()
    NTR = len(tr)
    xte = np.load(os.path.join(ROOT, "results", "_pe_tokens", "variants", "released_bpe50k", "x_test.npy"), mmap_mode="r")
    rng = np.random.default_rng(1)
    bad = 0
    idx = rng.choice(len(te), n_unedited, replace=False)
    for t_ in idx:
        t, total = CS.build_tokens(store, NTR + int(t_), list(range(store.n_calls(NTR + int(t_)))))
        bad += int(not np.array_equal(t, np.asarray(xte[t_], dtype=np.uint16)))
    print(f"(1) released tokenizer: unedited April reports rebuilt from the pieces: {bad} of {n_unedited} differ from the stored tokens", flush=True)
    assert bad == 0
    tok = make_pad.make_tokenizer(released=True)
    reps = make_pad.Reps()
    lab = np.load(os.path.join(make_pad.TOKENS, "labels.npz"))
    y = lab["y_train"]
    trn, val = gap.val_slice(lab["ym_train"])
    pool_rows = np.array([int(r) for r in val if y[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows])
    bad = n = 0
    for t_ in rng.choice(len(te), n_edited, replace=False):
        r = NTR + int(t_)
        if store.n_calls(r) == 0:
            continue
        plan = make_pad.plan_test_row(r, int(rng.choice([5, 20, 50])), "insert" if rng.random() < 0.5 else "prepend", store.n_calls(r), pool_n)
        mine, total = inmem_pad.edit_row(store, r, plan, pool_rows)
        rep = reps.get(int(te[int(t_)]))
        added = [reps.get(int(tr[int(pool_rows[pr])]))["apis"][c] for pr, c in plan["draws"]]
        r2 = dict(rep)
        r2["apis"] = make_pad.apply_plan(list(rep.get("apis") or []), plan, added)
        full = tok.encode([r2], pad=False)[0]
        n += 1
        bad += int(not (np.array_equal(mine, make_pad.to512(full)) and total == len(full)))
    print(f"(2) released tokenizer: edits by concatenation against full re-tokenisation: {bad} of {n} differ", flush=True)
    assert bad == 0
    print("released store checks passed", flush=True)
