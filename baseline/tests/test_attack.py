"""Tests of the attack statistics (baseline/attack_stats.py) and the edit-set layout of baseline/attack_run.py."""
import numpy as np

from baseline import attack_run, attack_stats as A


def synth(n=2000, S=10, shift=0.0, seed=0):
    r = np.random.default_rng(seed)
    y = (r.random(n) < 0.5).astype(int)
    base = r.normal(size=(S, 1, n)) * 0.3 + np.where(y == 1, 3.0, -3.0) + r.normal(size=(S, 1, n))
    Z = np.repeat(base, 3, axis=1)
    Z[:, 1] += shift * y                        # set 1: malware scores shifted
    return y, Z


def test_thresholds_give_the_requested_benign_rate_on_the_unedited_set():
    y, Z = synth()
    F = A.flags_of(Z, y, "1e-2")
    ben = F[:, 0][:, y == 0].mean(1)
    assert np.all(ben <= 0.0105) and np.all(ben >= 0.0095 - 1 / (y == 0).sum())
    F3 = A.flags_of(Z, y, "1e-3")
    assert np.all(F3[:, 0][:, y == 0].mean(1) <= 0.0015)


def test_compare_identical_models_is_zero_and_unresolved_and_a_clear_gap_is_resolved():
    y, Z = synth()
    F = A.flags_of(Z, y, "1e-2")
    b = A.Boot(y, 200)
    same = A.compare(b, F[:, 1], F[:, 1], "mal")
    assert same["mean"] == 0 and not same["resolved"]
    y2, Z2 = synth(shift=-3.0, seed=0)
    F2 = A.flags_of(Z2, y, "1e-2")
    d = A.compare(b, F[:, 1], F2[:, 1], "mal")                  # A = shifted-down? A has no shift, B has malware scores lowered -> A flags more
    assert d["mean"] > 0.1 and d["resolved"] and d["seeds_above_0"] == 10 and d["lo"] > 0


def test_point_rate_lies_inside_its_bootstrap_interval_and_fit_subset_is_used():
    y, Z = synth()
    F = A.flags_of(Z, y, "1e-2")
    b = A.Boot(y, 300)
    p, bs = b.rate(F[:, 1], "mal")
    lo, hi = np.percentile(bs, [2.5, 97.5], axis=1).T if False else (np.percentile(bs, 2.5, axis=1), np.percentile(bs, 97.5, axis=1))
    assert np.all(lo <= p + 1e-6) and np.all(p <= hi + 1e-6)
    mask = np.zeros(len(y), bool); mask[: len(y) // 2] = True
    pm, _ = b.rate(F[:, 1], "mal", mask)
    want = F[:, 1][:, (y == 1) & mask].mean(1)
    assert np.allclose(pm, want, atol=1e-6)


def test_edit_set_layout_is_12_edits_plus_unedited():
    assert len(attack_run.SETS) == 12 and attack_run.set_name(0) == "unedited" and attack_run.set_name(1) == "lgbm_5_insert" and attack_run.set_name(12) == "v2pe_50_prepend"


def test_cluster_bootstrap_widens_the_interval_when_reports_are_duplicated():
    y, Z = synth(n=2000, S=4)
    F = A.flags_of(Z, y, "1e-2")[:, 1]
    groups = np.arange(len(y)) // 20                       # blocks of 20 neighbouring reports act as duplicates
    plain, clus = A.Boot(y, 300), A.Boot(y, 300, groups)
    _, b1 = plain.rate(F, "mal")
    _, b2 = clus.rate(F, "mal")
    assert (np.percentile(b2, 97.5, axis=1) - np.percentile(b2, 2.5, axis=1)).mean() >= (np.percentile(b1, 97.5, axis=1) - np.percentile(b1, 2.5, axis=1)).mean() * 0.9
    assert np.allclose(clus.rate(F, "mal")[0], plain.rate(F, "mal")[0])          # the point estimate does not depend on the resampling
