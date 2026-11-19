"""Tests of the call-token store and the in-memory padding (baseline/callstore.py, baseline/inmem_pad.py) on a small synthetic store.
(The real store is checked against full re-tokenisation and the REPORT 5.10 arrays by `python -m baseline.callstore --check`.)"""
import numpy as np

from baseline import callstore as CS, inmem_pad as IP


def synthetic_store(n_reports=60, seed=0):
    r = np.random.default_rng(seed)
    toks, lens, nseg, names = [], [], [], []
    for _ in range(n_reports):
        n = int(r.integers(0, 12))
        pieces = [r.integers(3, 500, int(r.integers(1, 4))).astype(np.uint16)] + [r.integers(3, 500, int(r.integers(2, 9))).astype(np.uint16) for _ in range(n)] + [r.integers(3, 500, 2).astype(np.uint16)]
        toks += pieces
        lens += [len(p) for p in pieces]
        nseg.append(len(pieces))
        names += [-1] + list(r.integers(0, 5, n)) + [-1]
    return CS.CallStore(np.concatenate(toks), np.concatenate([[0], np.cumsum(lens)]).astype(np.int64), np.concatenate([[0], np.cumsum(nseg)]).astype(np.int64), np.asarray(names, dtype=np.int32), list("abcde"))


def test_unedited_report_is_the_concatenation_of_its_pieces_and_cut_at_512():
    s = synthetic_store()
    for r in range(len(s)):
        t, total = CS.build_tokens(s, r, list(range(s.n_calls(r))))
        full = s.report_tokens(r)
        assert total == len(full) and np.array_equal(t[:min(512, len(full))], full[:512]) and (t[len(full):] == 0).all()


def test_prepend_and_extra_calls_land_in_the_right_place():
    s = synthetic_store()
    r = next(i for i in range(len(s)) if s.n_calls(i) >= 3)
    n = s.n_calls(r)
    t, total = CS.build_tokens(s, r, [(s, 0, 0) if s.n_calls(0) else np.array([7], np.uint16)] + list(range(n)), cut=10_000)
    extra = s.call(0, 0) if s.n_calls(0) else np.array([7], np.uint16)
    assert np.array_equal(t[:len(s.head(r))], s.head(r))
    assert np.array_equal(t[len(s.head(r)):len(s.head(r)) + len(extra)], extra)
    assert total == len(s.report_tokens(r)) + len(extra) and (t[total:] == 0).all()


def test_epoch_edits_are_deterministic_and_malware_only_equals_the_malware_part_of_all_labels():
    s = synthetic_store(80)
    y = (np.arange(len(s)) % 3 == 0).astype(int)
    trn = np.arange(60)
    pool = IP.pool_rows_of(s, y, trn)
    assert all(y[p] == 0 and s.n_calls(int(p)) > 0 for p in pool)
    a = IP.epoch_edits(s, y, trn, 2, 1, pool, stream=7000, labels="all")
    b = IP.epoch_edits(s, y, trn, 2, 1, pool, stream=7000, labels="all")
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])
    m = IP.epoch_edits(s, y, trn, 2, 1, pool, stream=7000, labels="malware")
    assert len(m[0]) > 0 and (y[m[0]] == 1).all()
    idx = [i for i, r in enumerate(a[0]) if y[r] == 1]
    assert np.array_equal(a[0][idx], m[0]) and np.array_equal(a[1][idx], m[1])         # the plan of a report does not depend on the others
    k = IP.epoch_edits(s, y, trn, 2, 1, pool, stream=7100, labels="all")
    assert not (len(k[0]) == len(a[0]) and np.array_equal(k[1], a[1]))               # a different stream gives different edits
    e2 = IP.epoch_edits(s, y, trn, 2, 2, pool, stream=7000, labels="all")
    assert not np.array_equal(e2[0], a[0]) or not np.array_equal(e2[1], a[1])        # a new draw every epoch


def test_build_fast_equals_build_tokens_for_prepend_and_insert():
    s = synthetic_store(80)
    rng = np.random.default_rng(5)
    for r in range(len(s)):
        n = s.n_calls(r)
        k = int(rng.integers(1, 9))
        added = [rng.integers(3, 500, int(rng.integers(2, 8))).astype(np.uint16) for _ in range(k)]
        gaps = np.sort(rng.integers(0, n + 1, k))
        for cut in (512, 20):
            fp = CS.build_fast(s, r, added, None, cut)
            bp = CS.build_tokens(s, r, added + list(range(n)), cut=cut)
            assert np.array_equal(fp[0], bp[0]) and fp[1] == bp[1]
            order, j = [], 0
            for i in range(n + 1):
                while j < k and gaps[j] == i:
                    order.append(added[j]); j += 1
                if i < n:
                    order.append(i)
            fi = CS.build_fast(s, r, added, gaps, cut)
            bi = CS.build_tokens(s, r, order, cut=cut)
            assert np.array_equal(fi[0], bi[0]) and fi[1] == bi[1]
