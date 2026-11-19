"""Tests of the further edit families (baseline/extra_edits.py) on a synthetic store: rotation, injection, planners and the deduplication builder."""
import numpy as np

from baseline import callstore as CS, extra_edits as X


def piece(c):
    return np.array([c % 250 + 3, c // 250 + 3, c % 7 + 3], dtype=np.uint16)


def store_with_calls(report_calls):
    """report_calls: list of lists of call ids; call c has the token piece(c); head = [1, 2], tail = [9]."""
    toks, lens, nseg, names = [], [], [], []
    for calls in report_calls:
        parts = [np.array([1, 2], dtype=np.uint16)] + [piece(c) for c in calls] + [np.array([9], dtype=np.uint16)]
        toks += parts; lens += [len(p) for p in parts]; nseg.append(len(parts)); names += [-1] + [c % 11 for c in calls] + [-1]
    return CS.CallStore(np.concatenate(toks), np.concatenate([[0], np.cumsum(lens)]).astype(np.int64), np.concatenate([[0], np.cumsum(nseg)]).astype(np.int64), np.asarray(names, dtype=np.int32), list("abcdefghijk"))


def test_rotation_and_injection_equal_the_generic_builder():
    rng = np.random.default_rng(0)
    reports = [list(rng.integers(0, 400, int(rng.integers(1, 30)))) for _ in range(40)]
    s = store_with_calls(reports)
    for r in range(len(s)):
        n = s.n_calls(r)
        for shift in (0, n // 4, n // 2):
            for cut in (512, 12):
                a, ta = X.build_rotated(s, r, shift, cut)
                b, tb = CS.build_tokens(s, r, list(range(shift, n)) + list(range(0, shift)), cut=cut)
                assert np.array_equal(a, b) and ta == tb
        k = min(3, n)
        new = [np.array([200 + i, 201, 202, 203], dtype=np.uint16) for i in range(k)]
        a, ta = X.build_injected(s, r, new)
        b, tb = CS.build_tokens(s, r, new + list(range(k, n)))
        assert np.array_equal(a, b) and ta == tb


def test_planners_are_deterministic_and_unedited_for_empty_reports():
    rng = np.random.default_rng(1)
    reports = [list(rng.integers(0, 400, int(rng.integers(0, 20)))) for _ in range(60)]
    s = store_with_calls(reports)
    pool = np.array([r for r in range(30) if s.n_calls(r) > 0])
    P = X.Pools(s, pool, np.arange(30))
    assert P.rare and 0 < P.n_rare_names <= P.n_names
    for t in range(30, 60):
        n = s.n_calls(t)
        a, b = X.all_specs(t, n, P), X.all_specs(t, n, P)
        assert len(a) == len(X.SET_NAMES)
        if n == 0:
            assert all(x is None for x in a)
            continue
        for x, y in zip(a, b):
            if x is None:
                continue
            assert x["kind"] == y["kind"]
            if x["kind"] == "pad":
                assert x["added"] == y["added"] and (x["gaps"] is None) == (y["gaps"] is None)
        sp = X.plan("block", 5, "insert", t, n, P)
        assert len(set(sp["gaps"].tolist())) == 1                       # one block: all calls at one gap
        assert all(a[0] == "pool" for a in sp["added"]) and all(a[0] == "own" for a in X.plan("copy", 5, "prepend", t, n, P)["added"])


def test_dedup_removes_only_consecutive_identical_calls_and_stops_at_the_window():
    reports = [[5, 5, 5, 6, 5, 5, 7, 7, 8], [1, 2, 3], [4, 4]]
    s = store_with_calls(reports)
    ident = X.Ident(lambda row: {"apis": [{"c": c} for c in reports[int(row)]]})
    got = X.build_dedup(s, 0, None, ident, cut=512)
    want = np.concatenate([[1, 2]] + [piece(c) for c in [5, 6, 5, 7, 8]] + [[9]])
    assert np.array_equal(got[:len(want)], want) and (got[len(want):] == 0).all()
    assert np.array_equal(X.build_dedup(s, 1, None, ident)[:12], np.concatenate([[1, 2]] + [piece(c) for c in [1, 2, 3]] + [[9]]))
    spec = {"kind": "pad", "added": [("own", 0), ("own", 0)], "gaps": None}                   # copies of call 0 prepended: 4 identical calls in a row collapse to one
    got = X.build_dedup(s, 2, spec, ident)
    assert np.array_equal(got[:6], np.concatenate([[1, 2], piece(4), [9]])[:6]) and (got[6:] == 0).all()
    short = X.build_dedup(s, 0, None, ident, cut=7)
    assert np.array_equal(short, np.concatenate([[1, 2], piece(5), piece(6)])[:7])
