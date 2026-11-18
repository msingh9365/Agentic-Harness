"""Tests of the partial AUC (baseline/common.py): perfect/random/tied rankings, the interpolation at max_fpr against a hand-computed example,
the McClish relation to sklearn, and that binary_metrics reports it."""
import numpy as np
import pytest

from baseline import common as C

# 4 benign, 4 malware; descending thresholds 5(m) 4.5(m) 4(b) 3.5(m) 3(b) 2.5(m) 2(b) 1(b): ROC points
# (0,0) (0,.25) (0,.5) (.25,.5) (.25,.75) (.5,.75) (.5,1) (.75,1) (1,1)
Y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
Z = np.array([1.0, 2.0, 3.0, 4.0, 2.5, 3.5, 4.5, 5.0])


def test_hand_computed_example_with_interpolation():
    # max_fpr .375: area [0,.25] at TPR .5 = .125, then TPR .75 on [.25,.375] = .09375 -> .21875 / .375
    assert C.pauc(Y, Z, 0.375) == pytest.approx(0.21875 / 0.375)
    # max_fpr .125: TPR .5 on [0,.125]
    assert C.pauc(Y, Z, 0.125) == pytest.approx(0.5)
    # max_fpr exactly at a vertical step (fpr .25: TPR .5 -> .75): the lower value counts, area .5 * .25
    assert C.pauc(Y, Z, 0.25) == pytest.approx(0.5)
    # max_fpr .5: .125 + .75 * .25 = .3125 -> / .5
    assert C.pauc(Y, Z, 0.5) == pytest.approx(0.625)
    # max_fpr 1 is the AUC
    from sklearn.metrics import roc_auc_score
    assert C.pauc(Y, Z, 1.0) == pytest.approx(roc_auc_score(Y, Z))


def test_perfect_and_worst_ranking():
    y = np.r_[np.zeros(500), np.ones(500)].astype(int)
    z = np.r_[np.linspace(-5, -1, 500), np.linspace(1, 5, 500)]
    assert C.pauc(y, z, 1e-2) == pytest.approx(1.0) and C.pauc(y, z, 1e-3) == pytest.approx(1.0)
    assert C.pauc(y, -z, 1e-2) == pytest.approx(0.0)


def test_random_ranking_is_max_fpr_over_two_by_simulation():
    rng = np.random.default_rng(0)
    y = (rng.random(20000) < 0.5).astype(int)
    vals = {f: [] for f in (1e-2, 1e-3)}
    for _ in range(60):
        z = rng.normal(size=len(y))
        for f in vals:
            vals[f].append(C.pauc(y, z, f))
    assert np.mean(vals[1e-2]) == pytest.approx(0.005, abs=0.0015)            # = mean TPR over FPR in [0, 1e-2] = FPR / 2
    assert np.mean(vals[1e-3]) == pytest.approx(0.0005, abs=0.0004)


def test_ties_are_handled_as_diagonal_segments():
    y = np.array([0, 0, 1, 1, 1])
    assert C.pauc(y, np.zeros(5), 0.2) == pytest.approx(0.1)                   # all scores tied: the diagonal, mean TPR = max_fpr / 2
    z = np.array([0.0, 1.0, 1.0, 2.0, 2.0])                                    # a tie between a benign and a malware report: they count half
    assert C.pauc(y, z, 1.0) == pytest.approx(__import__("sklearn.metrics", fromlist=["x"]).roc_auc_score(y, z))


def test_float32_probabilities_would_saturate_but_logits_do_not():
    y = np.r_[np.zeros(300), np.ones(300)].astype(int)
    rng = np.random.default_rng(1)
    z = np.r_[rng.normal(30, 8, 300), rng.normal(45, 8, 300)]                  # logits above 17 saturate in float32
    assert C.pauc(y, z, 1e-2) != C.pauc(y, C.sigmoid32(z), 1e-2)


def test_mcclish_equals_sklearn_and_relates_to_pauc():
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(2)
    y = (rng.random(3000) < 0.5).astype(int)
    z = rng.normal(size=3000) + 1.2 * y
    for f in (1e-2, 1e-3, 0.1):
        m = C.pauc_mcclish(y, z, f)
        assert m == pytest.approx(roc_auc_score(y, z, max_fpr=f))
        raw = C.pauc(y, z, f) * f
        assert m == pytest.approx(0.5 * (1 + (raw - f * f / 2) / (f - f * f / 2)), abs=1e-9)     # our area is sklearn's partial area


def test_binary_metrics_reports_pauc_and_roc_summary_agrees():
    C.setup_nebula(require_patched=True)
    rng = np.random.default_rng(3)
    y = (rng.random(4000) < 0.5).astype(int)
    z = rng.normal(size=4000) + 2.0 * y
    m = C.binary_metrics(y, z, decision=0.0)
    for f in (1e-2, 1e-3):
        assert m[f"pauc@{f:g}"] == pytest.approx(C.pauc(y, z, f)) and m[f"pauc_mcclish@{f:g}"] == pytest.approx(C.pauc_mcclish(y, z, f))
    s = C.roc_summary(y, z)
    assert [s[0], s[1], s[2], s[3], s[4]] == pytest.approx([m["tpr@0.001"], m["tpr@0.01"], m["auc"], m["pauc@0.01"], m["pauc@0.001"]], abs=1e-12)
