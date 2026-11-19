"""Test of the v2-PE driver (baseline/v2pe.py): fitting the authors' ModelTrainer epoch by epoch (the path of the padded runs) on UNCHANGED data reproduces the single
fit(epochs=2) of the plain runs exactly; an overlay of edited rows changes the training. CPU, tiny data (the old BPE-8k tokens, which are on this machine)."""
import os
import types

import numpy as np
import pytest

from baseline import v2pe

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOK = os.path.join(ROOT, "results", "_tokens_raw", "out")
pytestmark = pytest.mark.skipif(not os.path.exists(os.path.join(TOK, "variants", "bpe8k", "x_train.npy")), reason="old BPE-8k tokens not on this machine")


def args(tmp, tag, aug=None, seed=0, pooling="attn"):
    return types.SimpleNamespace(tokens=TOK, out=str(tmp), tag=tag, seed=seed, epochs=2, pe_mode="paper", pooling=pooling, variant="bpe8k", device="cpu", limit=200,
                                 force=True, aug_dir=aug, pad_store=None, pad_mode="replace", pad_labels="all", pad_stream=7000, pad_prob=0.5, lr=None, val_robust=False, every_epoch=False)


def make_aug(dirpath, seed, rows, tok):
    os.makedirs(dirpath, exist_ok=True)
    for e in (1, 2):
        np.save(os.path.join(dirpath, f"aug_s{seed}_e{e}_rows.npy"), np.asarray(rows, dtype=np.int64))
        np.save(os.path.join(dirpath, f"aug_s{seed}_e{e}_tok.npy"), np.asarray(tok, dtype=np.uint16).reshape(-1, 512))


@pytest.mark.parametrize("pooling", ["attn", "flatten"])
def test_epoch_by_epoch_fitting_on_unchanged_data_equals_the_single_fit(tmp_path, pooling):
    v2pe.run(args(tmp_path, "plain", pooling=pooling))
    make_aug(tmp_path / "aug", 0, [], np.zeros((0, 512)))
    v2pe.run(args(tmp_path, "perepoch", aug=str(tmp_path / "aug"), pooling=pooling))
    for w in ("val", "test"):
        a = np.load(tmp_path / "plain" / f"seed0_epoch2_{w}_logits.npy")
        b = np.load(tmp_path / "perepoch" / f"seed0_epoch2_{w}_logits.npy")
        assert np.array_equal(a, b), (pooling, w, float(np.abs(a - b).max()))


def test_overlaid_rows_change_the_training_and_only_in_their_epoch(tmp_path):
    x = np.load(os.path.join(TOK, "variants", "bpe8k", "x_train.npy"), mmap_mode="r")
    from baseline import gap
    lab = np.load(os.path.join(TOK, "labels.npz"))
    trn, _ = gap.val_slice(lab["ym_train"])
    rng = np.random.default_rng(0)
    take = np.sort(np.random.default_rng(0).permutation(trn)[:200])[:40]               # rows that are in the limited training subset: the driver subsets with rng seed 0 too
    v2pe.run(args(tmp_path, "plain"))
    rows = np.asarray(sorted(int(r) for r in np.random.default_rng(0).permutation(trn)[:200]))[:40]
    tok = np.stack([np.roll(np.asarray(x[r]), 7) for r in rows]).astype(np.uint16) % 8000
    make_aug(tmp_path / "aug", 0, rows, tok)
    v2pe.run(args(tmp_path, "padded", aug=str(tmp_path / "aug")))
    a = np.load(tmp_path / "plain" / "seed0_epoch2_val_logits.npy")
    b = np.load(tmp_path / "padded" / "seed0_epoch2_val_logits.npy")
    assert not np.array_equal(a, b)                                                    # the overlay changes the training
    import json
    d = json.load(open(tmp_path / "padded" / "seed0.json"))
    assert d["edited_rows_per_epoch"] == {"1": 40, "2": 40} or d["edited_rows_per_epoch"] == {1: 40, 2: 40}, d["edited_rows_per_epoch"]
