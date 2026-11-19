"""Tests of the selection rule of NOTES 16.4 (baseline/tune_select.py) on synthetic validation numbers."""
import numpy as np

from baseline import tune_select as T


def cand(pauc, robust=0.7, loss=0.1, auc=0.99, n=10, sd=0.02, seed=0):
    r = np.random.default_rng(seed)
    z = r.normal(size=n); z = (z - z.mean()) / z.std(ddof=1)
    return {"pauc": pauc + sd * z, "auc": np.full(n, auc), "loss": np.full(n, loss), "robust": np.full(n, robust)}


def grid(over=None):
    base = {(lr, p, e): cand(0.80) for lr in (1e-3, 2e-3) for p in (0.25, 0.5) for e in (1, 2, 3, 4)}
    base.update(over or {})
    return base


def test_tag_names():
    assert T.tag_of(1e-3, 0.25) == "tune_lr1e-3_p0.25" and T.tag_of(2e-3, 0.5) == "tune_lr2e-3_p0.5"


def test_collapse_and_robustness_exclusions_and_best_wins_when_clear():
    g = grid({(1e-3, 0.25, 4): cand(0.95, robust=0.5),                     # best pAUC but R far below the reference: excluded
                (2e-3, 0.25, 3): cand(0.93, auc=0.5),                        # collapse: excluded
                (2e-3, 0.5, 4): cand(0.90, robust=0.69)})                    # clear winner among the eligible (R within 0.02 of 0.70)
    rows, chosen, best = T.select(g, ref_robust=0.70)
    assert rows[(1e-3, 0.25, 4)]["robust_excluded"] and rows[(2e-3, 0.25, 3)]["collapsed"]
    assert best == chosen == (2e-3, 0.5, 4)


def test_ties_fewest_epochs_then_p_half_then_loss():
    g = grid({(1e-3, 0.25, 3): cand(0.9005, loss=0.2), (1e-3, 0.5, 3): cand(0.9, loss=0.3), (2e-3, 0.5, 2): cand(0.8995, loss=0.5), (2e-3, 0.25, 2): cand(0.9, loss=0.1)})
    rows, chosen, best = T.select(g, ref_robust=0.70)
    assert rows[(2e-3, 0.5, 2)]["tied_with_best"] and rows[(2e-3, 0.25, 2)]["tied_with_best"]
    assert chosen == (2e-3, 0.5, 2)                     # epochs 2 beat 3; at epoch 2 p = 0.5 beats p = 0.25 even though its loss is higher
    g2 = grid({(2e-3, 0.5, 2): cand(0.9, loss=0.5), (1e-3, 0.5, 2): cand(0.9, loss=0.2)})
    assert T.select(g2, 0.70)[1] == (1e-3, 0.5, 2)       # same epochs, same p: the lower validation loss


def test_nothing_eligible_returns_none_and_a_2_point_margin_is_inclusive():
    g = grid()
    rows, chosen, best = T.select(g, ref_robust=0.95)
    assert chosen is None
    g = {k: cand(0.8, robust=0.68) for k in grid()}
    assert T.select(g, ref_robust=0.70)[1] is not None  # exactly 0.02 below is not "more than 2 points below"
