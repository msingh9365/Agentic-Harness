"""Tests of baseline/groupsplit.py on small synthetic inputs (CPU)."""
import numpy as np
import pytest

from baseline import groupsplit as G


def test_union_find_joins_rows_that_agree_in_any_key():
    a = np.array(["x", "y", "z", "w", "v"])
    b = np.array(["1", "1", "2", "3", "3"])         # rows 0,1 share b; rows 3,4 share b
    c = np.array(["p", "q", "q", "r", "s"])         # rows 1,2 share c
    g = G.groups_of(a, b, c)
    assert g[0] == g[1] == g[2] and g[3] == g[4] and g[0] != g[3]
    assert G.groups_of(a).max() + 1 == 5


def test_split_has_no_shared_group_and_stable_hash():
    rng = np.random.default_rng(0)
    n = 3000
    groups = rng.integers(0, 400, n)
    fam = np.array(["a", "b", "c"])[rng.integers(0, 3, n)]
    trn, val = G.make_split(fam, groups)
    assert not (set(groups[trn]) & set(groups[val])) and len(trn) + len(val) == n
    assert abs(len(val) / n - 0.1) < 0.03
    assert G.split_hash(trn, val) == G.split_hash(*G.make_split(fam, groups))


def test_val_slice_asserts_the_hash(tmp_path):
    import json
    trn, val = np.arange(0, 90), np.arange(90, 100)
    np.savez(tmp_path / "s.npz", train=trn, val=val)
    json.dump({"sha256": G.split_hash(trn, val), "n_train": 90, "n_val": 10}, open(tmp_path / "h.json", "w"))
    assert len(G.val_slice(str(tmp_path / "s.npz"), str(tmp_path / "h.json"))[1]) == 10
    json.dump({"sha256": "0" * 32, "n_train": 90, "n_val": 10}, open(tmp_path / "h.json", "w"))
    with pytest.raises(AssertionError):
        G.val_slice(str(tmp_path / "s.npz"), str(tmp_path / "h.json"))


def test_near_duplicate_share_exact_distances():
    base = list(range(100))
    near = base[:97] + [200, 201, 202]                       # 3 substitutions in 100 -> 0.03
    far = list(range(500, 600))
    seq_a = [near, far]
    seq_b = [base]
    ha, hb = np.array(["n", "f"]), np.array(["b"])
    r, ua, ub = G.near_duplicate_share(seq_a, seq_b, ha, hb)
    assert r["0"] == 0.0 and r["0.01"] == 0.0 and r["0.05"] == 0.5 and r["0.1"] == 0.5
    r2, _, _ = G.near_duplicate_share([base, near], seq_b, np.array(["b", "n"]), hb)
    assert r2["0"] == 0.5 and r2["0.05"] == 1.0


def test_choose_fold_rule():
    from baseline.groupsplit import choose_fold, MALWARE_AND_CLEAN

    def fold(k, n, benign, groups, big, fam_min=400):
        return {"fold": k, "n": n, "benign": benign, "groups": groups, "largest_group_share": big, "families": {f: fam_min for f in MALWARE_AND_CLEAN} | {"windows_syswow64": 10}}
    folds = [fold(0, 1000, 190, 50, 0.5),                       # benign 19%: out
             fold(1, 1000, 330, 900, 0.10, fam_min=299),        # one family under 300: out
             fold(2, 1000, 330, 800, 0.20),                     # candidate
             fold(3, 1000, 330, 900, 0.10),                     # candidate, best share
             fold(4, 1000, 330, 900, 0.10)]                     # same share and groups as 3: lower fold number wins
    f, cands, _ = choose_fold(folds, 0.33)
    assert (f, cands) == (3, [2, 3, 4])
    folds[3]["groups"] = 800
    assert choose_fold(folds, 0.33)[0] == 4                      # tie on share -> more groups
    assert choose_fold(folds[:2], 0.33)[0] is None               # no candidate
