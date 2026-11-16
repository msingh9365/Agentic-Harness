"""CPU tests of baseline/cv.py with synthetic tokens (no data needed)."""
import json
import os
import time

import numpy as np
import pytest

from baseline import common as C, cv

C.setup_nebula()
V, L = 120, 128


def synth(n=240, seed=0):
    """Token sequences where malware (y=1) over-uses a few tokens: a learnable but noisy signal."""
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < 0.5).astype(np.int8)
    x = np.zeros((n, L), dtype=np.int32)
    for i in range(n):
        k = int(rng.integers(40, L))
        x[i, :k] = rng.integers(3, V, k)
        if y[i]:
            x[i, rng.integers(0, k, 12)] = 7
    return x, y


def folds(n, k=3):
    idx = np.arange(n)
    return [{"train": np.setdiff1d(idx, idx[i::k]).tolist(), "val": idx[i::k].tolist()} for i in range(k)]


def test_released_config_has_expected_size():
    from nebula.models.attention import TransformerEncoderChunks
    m = TransformerEncoderChunks(**cv.model_config(50001))
    n = sum(p.numel() for p in m.parameters())
    assert abs(n / 1e6 - 5.397) < 0.01, n                    # NOTES.md: 5.397 M parameters (paper says about 5.6 M)


@pytest.mark.parametrize("n_batches", [1, 7, 13])
def test_batches_regime_stops_after_exactly_n_batches(tmp_path, n_batches):
    x, y = synth()
    xt, yt = synth(60, seed=1)
    res = cv.run_cv(x, y, xt, yt, folds(len(x)), V, str(tmp_path), regime="batches", max_batches=n_batches, batch_size=16,
                    device="cpu", maxlen=L, tag="t", save_models=False)
    assert [f["batches_seen"] for f in res["folds"]] == [n_batches] * 3
    assert "tpr@0.001" in res["test_mean_std"] and 0 <= res["test_mean_std"]["auc"]["mean"] <= 1


def test_time_regime_stops_near_the_budget(tmp_path):
    x, y = synth()
    xt, yt = synth(60, seed=1)
    t0 = time.time()
    res = cv.run_cv(x[:96], y[:96], xt, yt, folds(96)[:1], V, str(tmp_path), regime="time", time_budget=3, batch_size=16,
                    device="cpu", maxlen=L, tag="t", save_models=False)
    f = res["folds"][0]
    assert 2.5 < f["train_seconds"] < 12, f["train_seconds"]   # stopped by the time budget, not by running out of epochs
    assert f["epochs_seen"] > 1                                 # trained for several epochs in that time


def test_training_actually_learns(tmp_path):
    x, y = synth(600)
    xt, yt = synth(200, seed=3)
    res = cv.run_cv(x, y, xt, yt, folds(len(x)), V, str(tmp_path), regime="batches", max_batches=120, batch_size=32,
                    device="cpu", maxlen=L, tag="t", save_models=False)
    assert res["test_mean_std"]["auc"]["mean"] > 0.7           # far above chance on a separable toy signal


def test_metrics_follow_their_definition():
    """TPR at FPR: their get_tpr_at_fpr (last ROC point with FPR <= target)."""
    from nebula.misc import get_tpr_at_fpr
    rng = np.random.default_rng(0)
    y = np.r_[np.zeros(2000), np.ones(500)].astype(int)
    p = np.r_[rng.beta(2, 8, 2000), rng.beta(6, 3, 500)]
    m = C.binary_metrics(y, p)
    for f in C.FPRS:
        assert m[f"tpr@{f:g}"] == get_tpr_at_fpr(y, p, f)[0]
    assert m["n_malware"] == 500 and len(m["roc_on_grid"]) == len(C.ROC_GRID)
    pm = rng.dirichlet(np.ones(8), 400)
    ym = rng.integers(0, 8, 400)
    mm = C.multiclass_metrics(ym, pm)
    assert len(mm["f1_per_class"]) == 8 and 0 <= mm["acc"] <= 1
