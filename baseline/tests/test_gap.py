"""Tests for the gap follow-up: the validation slice, the per-epoch hook (evaluation exactly at epoch boundaries), and a tiny end-to-end run."""
import json
import os
import types

import numpy as np
import pytest

from baseline import common as C, cv, gap

C.setup_nebula(require_patched=True)


def test_validation_slice_is_stratified_disjoint_and_deterministic():
    ym = np.repeat(np.arange(8), [4000, 3000, 1000, 800, 500, 300, 200, 100])
    trn, val = gap.val_slice(ym, hashes=None)
    trn2, val2 = gap.val_slice(ym, hashes=None)
    assert (trn == trn2).all() and (val == val2).all()
    assert len(set(trn) & set(val)) == 0 and len(trn) + len(val) == len(ym)
    assert abs(len(val) / len(ym) - 0.1) < 0.002
    for c in range(8):                                                   # every family has 10% in the slice
        assert abs((ym[val] == c).mean() * len(val) / (ym == c).sum() - 0.1) < 0.01


def test_epoch_hook_evaluates_once_per_epoch_at_the_boundaries():
    from nebula.models.attention import TransformerEncoderChunks
    rng = np.random.default_rng(0)
    n, V = 250, 60                                                          # 3 batches per epoch at batch 96 (96 + 96 + 58)
    x = np.zeros((n, 512), dtype=np.int32)
    y = (rng.random(n) < 0.5).astype(np.int64)
    for i in range(n):
        k = int(rng.integers(30, 120))
        x[i, :k] = rng.integers(3, V - 5, k) + 5 * y[i]
    C.set_seed(0)
    model = TransformerEncoderChunks(**cv.model_config(V))
    trainer = cv.make_trainer(model, "cpu", "binary", 96, 2.5e-4, 1e-2, clip_grad_norm=1.0)
    assert trainer.clip_grad_norm == 1.0
    calls, forwards = [], []

    def on_epoch_end(ep):
        calls.append((ep, hook.total, model.training))
        cv.predict_logits(model, x[:8], "cpu")                                 # leaves the model in eval mode; the hook must restore train mode

    hook = gap.EpochHook(model, int(np.ceil(n / 96)), on_epoch_end)
    hook.total = 0
    orig = hook.forward
    hook.forward = lambda z: (setattr(hook, "total", hook.total + 1), orig(z))[1]
    trainer.model.forwardPass = hook
    trainer.fit(x, y, epochs=3)
    hook.finish()
    assert [c[0] for c in calls] == [1, 2, 3]
    assert [c[1] for c in calls] == [3, 6, 9]                                 # 3 training batches before each evaluation
    assert model.training                                                      # restored after the last callback inside fit; the final one was called after fit


def test_bce_helper_matches_torch():
    import torch
    z = np.random.default_rng(1).normal(size=200) * 5
    y = (np.random.default_rng(2).random(200) < 0.5).astype(float)
    ref = torch.nn.functional.binary_cross_entropy_with_logits(torch.tensor(z), torch.tensor(y)).item()
    assert abs(gap.bce_logits(y, z) - ref) < 1e-9
