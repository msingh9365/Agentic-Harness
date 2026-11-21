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


def test_stage_b_selection_rule():
    from baseline.gs_select import select

    def r(p, se=0.004, loss=0.07, auc=0.99, r20=0.95, r100=0.8):
        return {"mean_pauc": p, "se_pauc": se, "mean_loss": loss, "min_auc": auc, "mean_r20": r20, "mean_r100": r100}
    # v2-PE style (no robustness): the best is epoch 3, epoch 2 is within one SE and has fewer epochs, epoch 1 is not within one SE
    rows = {(1e-3, 1): r(0.90), (1e-3, 2): r(0.938), (1e-3, 3): r(0.94), (1e-3, 4): r(0.92)}
    _, chosen, best = select(rows, False)
    assert best == (1e-3, 3) and chosen == (1e-3, 2)
    # the same pAUC and the same epoch: the lower validation loss wins, then the lower learning rate
    rows = {(2e-3, 2): r(0.94, loss=0.08), (1e-3, 2): r(0.94, loss=0.07)}
    assert select(rows, False)[1] == (1e-3, 2)
    # collapse guard
    rows = {(1e-3, 1): r(0.99, auc=0.55), (1e-3, 2): r(0.90)}
    assert select(rows, False)[1] == (1e-3, 2)
    # ATT+bal, amended rule (NOTES 21.7): only R20 more than 0.02 below the best R20 excludes a candidate (before the tie rule, even if its pAUC is the highest); R100 takes no part
    rows = {(1e-3, 0.5, 1): r(0.96, r20=0.90), (1e-3, 0.5, 2): r(0.94, r20=0.95, r100=0.05), (2e-3, 0.25, 2): r(0.945, r20=0.945, r100=0.20), (2e-3, 0.5, 2): r(0.90, r20=0.95, r100=0.70)}
    rows, chosen, best = select(rows, True)
    assert rows[(1e-3, 0.5, 1)]["robust_excluded"] and not rows[(2e-3, 0.25, 2)]["robust_excluded"] and not rows[(1e-3, 0.5, 2)]["robust_excluded"]
    assert best == chosen == (2e-3, 0.25, 2)                           # the highest pAUC among the candidates that pass R20; its R100 (0.20) and the other (0.70) play no role
    # the first plan's rule (R20 and R100) is still available through robust_keys
    rows = {(1e-3, 0.5, 2): r(0.94, r20=0.95, r100=0.05), (2e-3, 0.25, 2): r(0.945, r20=0.945, r100=0.20)}
    assert select(rows, True, ("mean_r20", "mean_r100"))[0][(1e-3, 0.5, 2)]["robust_excluded"]
