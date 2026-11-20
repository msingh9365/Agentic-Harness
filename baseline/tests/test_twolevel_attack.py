"""Tests of baseline/twolevel_attack.py on a small synthetic call store and a stand-in scorer (CPU, no authors' package). The real-model checks run in the kernel (check_scores)."""
import numpy as np
import pytest

from baseline import callstore as CS, padtest
from baseline import twolevel_attack as TA


def make_store(n_reports=30, seed=0):
    rng = np.random.default_rng(seed)
    seg_tok, seg_off, rep_seg, seg_name = [], [0], [0], []
    for _ in range(n_reports):
        n = int(rng.integers(1, 40))
        pieces = [np.array([1, 2], dtype=np.uint16)] + [rng.integers(3, 300, int(rng.integers(3, 30))).astype(np.uint16) for _ in range(n)] + [np.array([9], dtype=np.uint16)]
        for p in pieces:
            seg_tok.append(p)
            seg_off.append(seg_off[-1] + len(p))
            seg_name.append(int(rng.integers(0, 20)))
        rep_seg.append(rep_seg[-1] + len(pieces))
    return CS.CallStore(np.concatenate(seg_tok), np.array(seg_off), np.array(rep_seg), np.array(seg_name), [str(i) for i in range(20)])


def scorer(tok, tot):
    """deterministic stand-in: logit from the tokens of the first 512 positions and the total length"""
    w = np.random.default_rng(5).normal(size=512)
    x = np.asarray(tok)[:, :512].astype(np.float64)
    return ((x * w).sum(1) / 5000.0 - 0.001 * np.asarray(tot)).astype(np.float32)


def setup():
    store = make_store()
    ntr = 10
    y_test = np.array([i % 2 for i in range(len(store) - ntr)])
    pool = np.arange(0, ntr)
    pool_n = np.array([store.n_calls(int(r)) for r in pool])
    return store, ntr, y_test, pool, pool_n


def test_set_list_names_and_counts():
    s = TA.set_list()
    assert s[0][0] == "unedited" and len(s) == 1 + 2 * len(TA.RANDOM_KS) + 2 * 2 * len(TA.SURR_KS)
    assert len({x[0] for x in s}) == len(s)


def test_4096_build_starts_with_the_512_build_and_totals_agree():
    store, ntr, y, pool, pool_n = setup()
    for spec in (("unedited", "none", 0, None), ("random_20_insert", "random", 20, "insert"), ("random_200_prepend", "random", 200, "prepend")):
        t1, n1 = TA.build_set(store, ntr, len(y), pool, pool_n, None, spec, 512)
        t2, n2 = TA.build_set(store, ntr, len(y), pool, pool_n, None, spec, 4096)
        assert np.array_equal(t1, t2[:, :512]) and np.array_equal(n1, n2)


def test_random_edit_adds_exactly_the_planned_tokens():
    store, ntr, y, pool, pool_n = setup()
    t0, n0 = TA.build_set(store, ntr, len(y), pool, pool_n, None, ("unedited", "none", 0, None), 4096)
    t, n = TA.build_set(store, ntr, len(y), pool, pool_n, None, ("random_5_prepend", "random", 5, "prepend"), 4096)
    from baseline import make_pad
    for i in range(len(y)):
        plan = make_pad.plan_test_row(i, 5, "prepend", store.n_calls(ntr + i), pool_n)
        added = sum(len(store.call(int(pool[p]), int(c))) for p, c in plan["draws"])
        assert n[i] == n0[i] + added


def test_greedy_matches_the_original_attack_for_the_first_steps(monkeypatch):
    """Steps of the new greedy = steps of baseline/attack_run.run_3b (same reports, same candidates), with the stand-in scorer."""
    from baseline import attack_run as AR
    store, ntr, y, pool, pool_n = setup()
    out = TA.greedy(store, ntr, y, pool, scorer, 512, n_wb=6, steps=3, n_cand=15, group=4, log=lambda s: None)
    # the original, with the same stand-ins
    class Ns:
        kind, seed, family, device, out = "attbal", 0, "x", "cpu", None
    monkeypatch.setattr(AR, "inputs", lambda a: (store, y, ntr, {}, pool))
    monkeypatch.setattr(padtest, "load_model", lambda *a_, **k: None)
    monkeypatch.setattr(padtest, "find_weights", lambda *a_, **k: None)
    monkeypatch.setattr(padtest, "score", lambda m, tok, dev, bs=256: np.stack([scorer(t, np.zeros(len(t))) for t in tok]))
    monkeypatch.setattr(AR, "N_WB", 6)
    monkeypatch.setattr(AR, "WB_STEPS", 3)
    monkeypatch.setattr(AR, "WB_CAND", 15)
    import tempfile
    ns = Ns()
    ns.out, ns.models_root, ns.search = tempfile.mkdtemp(), None, None
    AR.run_3b(ns)
    ref = np.load(f"{ns.out}/a3b_x_seed0.npz")
    # the original scorer ignores the total token count: compare with a scorer that does the same
    out2 = TA.greedy(store, ntr, y, pool, lambda tok, tot: scorer(tok, np.zeros(len(tok))), 512, n_wb=6, steps=3, n_cand=15, group=4, log=lambda s: None)
    assert np.allclose(out2["raw"], ref["raw"], atol=1e-5) and np.allclose(out2["best"], ref["best"], atol=1e-5)
    assert np.array_equal(out2["sel"], ref["sel"]) and out2["t1"] == ref["t1"]
    assert out["raw"].shape == (4, 6)


def test_greedy_stops_evaded_reports_and_padded_benign_uses_the_chosen_prefix():
    store, ntr, y, pool, pool_n = setup()
    out = TA.greedy(store, ntr, y, pool, scorer, 512, n_wb=7, steps=6, n_cand=20, group=3, log=lambda s: None)
    assert (np.diff(out["best"].astype(np.float64), axis=0) <= 1e-6).all()                       # the running minimum never rises
    stopped = out["best"][-1] <= out["t1"]
    assert (out["n_picked"][stopped] <= 6).all() and (out["n_picked"][out["best"][-1] > out["t1"]] == 6).all()      # a report that is still flagged used every step
    assert (out["n_picked"] <= 6).all() and len(set(out["ben_ids"])) == len(out["ben_ids"])
    assert "ben_k5" in out and "ben_k10" not in out and out["ben_k5"].shape == (7,)
