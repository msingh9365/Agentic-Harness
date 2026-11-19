"""Tests of the balanced padding builder (baseline/make_pad.py): the plans, the edits, and (if the cached reports are on this machine) the row map."""
import os

import numpy as np
import pytest

from baseline import make_pad as P


def test_plan_is_deterministic_and_has_the_specified_distribution():
    pool_n = np.full(40, 7)
    plans = [P.plan_train_row(r, 0, 1, 30, pool_n) for r in range(4000)]
    assert plans[10] is None or plans[10]["k"] == P.plan_train_row(10, 0, 1, 30, pool_n)["k"]
    assert [p is None for p in plans] == [p is None for p in [P.plan_train_row(r, 0, 1, 30, pool_n) for r in range(4000)]]
    edited = [p for p in plans if p is not None]
    assert abs(len(edited) / 4000 - 0.5) < 0.03                                   # probability 0.5
    assert abs(np.mean([p["mode"] == "prepend" for p in edited]) - 0.5) < 0.04    # 50/50 insert and prepend
    ks = np.array([p["k"] for p in edited])
    assert ks.min() == 1 and ks.max() == 50 and abs(ks.mean() - 25.5) < 1.0        # k ~ U{1..50}
    assert all(len(p["draws"]) == p["k"] and all(0 <= r < 40 and 0 <= c < 7 for r, c in p["draws"]) for p in edited)
    assert all((p["gaps"] is None) == (p["mode"] == "prepend") for p in edited)
    # no call, no edit; another seed or epoch changes the plan
    assert P.plan_train_row(5, 0, 1, 0, pool_n) is None
    assert any((P.plan_train_row(r, 1, 1, 30, pool_n) is None) != (P.plan_train_row(r, 0, 1, 30, pool_n) is None) for r in range(50))
    assert any((P.plan_train_row(r, 0, 2, 30, pool_n) is None) != (P.plan_train_row(r, 0, 1, 30, pool_n) is None) for r in range(50))


def test_apply_plan_prepend_and_insert_keep_the_original_order():
    apis = [f"a{i}" for i in range(10)]
    plan = {"mode": "prepend", "k": 3, "draws": [], "gaps": None}
    assert P.apply_plan(apis, plan, ["x", "y", "z"]) == ["x", "y", "z"] + apis
    plan = {"mode": "insert", "k": 4, "draws": [], "gaps": np.array([0, 3, 3, 10])}
    out = P.apply_plan(apis, plan, ["w", "x", "y", "z"])
    assert len(out) == 14 and [c for c in out if c.startswith("a")] == apis                         # the original calls keep their order
    assert out[0] == "w" and out[1:4] == ["a0", "a1", "a2"] and out[4:6] == ["x", "y"] and out[-1] == "z"
    # inserted calls are the ones that were drawn
    assert sorted(c for c in out if not c.startswith("a")) == ["w", "x", "y", "z"]


def test_test_plan_uses_fixed_k_and_mode_and_is_deterministic():
    pool_n = np.full(10, 5)
    for mode in ("insert", "prepend"):
        for k in (5, 20, 50):
            a, b = P.plan_test_row(123, k, mode, 40, pool_n), P.plan_test_row(123, k, mode, 40, pool_n)
            assert a["k"] == k and a["mode"] == mode and a["draws"] == b["draws"]
    assert P.plan_test_row(123, 5, "insert", 40, pool_n)["draws"] != P.plan_test_row(124, 5, "insert", 40, pool_n)["draws"]


def test_to512_pads_with_zero_and_cuts():
    assert P.to512([5, 6, 7])[:4].tolist() == [5, 6, 7, 0] and P.to512(list(range(1, 1000)))[511] == 512 and P.to512([]).sum() == 0


@pytest.mark.skipif(not os.path.exists(os.path.join(P.REPS, "reps.bin")) or not os.path.exists(os.path.join(P.TOKENS, "labels.npz")), reason="reps.bin / token labels not on this machine")
def test_row_map_is_one_to_one_and_agrees_with_the_labels():
    tr, te = P.build_row_map()
    assert len(tr) == 75298 and len(te) == 17402 and len(set(tr)) == len(tr) and len(set(te)) == len(te) and not set(tr.tolist()) & set(te.tolist())
