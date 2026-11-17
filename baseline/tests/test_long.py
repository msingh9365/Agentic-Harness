"""Tests for the long pre-training follow-up: early stopping with min_delta, per-epoch checkpoints, "fine-tune from epoch k loads exactly
checkpoint k" (checksum), split assertion, and a tiny end-to-end run of baseline.selfsup_long on CPU."""
import json
import os
import types

import numpy as np
import pytest
import torch

from baseline import common as C, lm, selfsup_long as SL

C.setup_nebula(require_patched=True)
V = 200


class FakeModule:
    """Stands in for the Lightning module: a model, eval()/train(), and a loss per call (_shared_step)."""
    device = "cpu"

    def __init__(self, losses):
        self.model = torch.nn.Linear(2, 2)
        self.training = True
        self.losses, self.i = list(losses), 0

    def eval(self): self.training = False
    def train(self, mode=True): self.training = mode

    def _shared_step(self, batch):
        return torch.tensor(self.losses[self.i])


class FakeTrainer:
    def __init__(self): self.current_epoch, self.should_stop = 0, False


def drive(cb, losses):
    """Run the callback over epochs with the given validation losses; each epoch changes the model weights so that checkpoints differ."""
    mod, tr = FakeModule(losses), FakeTrainer()
    sds = {}
    for e, _ in enumerate(losses):
        tr.current_epoch, mod.i = e, e
        with torch.no_grad():
            mod.model.weight.fill_(float(e + 1))
        sds[e + 1] = {k: v.clone() for k, v in mod.model.state_dict().items()}
        cb.on_train_epoch_start(tr, mod)
        cb.on_train_epoch_end(tr, mod)
        if tr.should_stop:
            break
    cb.on_train_end(tr, mod)
    return mod, tr, sds


def loader():
    return [(torch.zeros(3, 1),)]


def test_early_stop_uses_min_delta_and_patience():
    # improvements of 0.5, 0.005 (< min_delta), 0.004 (< min_delta): two non-significant epochs in a row -> stop after epoch 3
    cb = lm.ValLossCallback(loader(), patience=2, min_delta=0.01)
    mod, tr, _ = drive(cb, [2.0, 1.5, 1.495, 1.491, 1.0, 0.9])
    assert tr.should_stop and len(cb.history) == 4 and cb.stopped_early
    assert cb.best_epoch == 4                                    # the raw lowest loss is kept as best even if the gain is below min_delta
    # a real improvement resets the counter
    cb = lm.ValLossCallback(loader(), patience=2, min_delta=0.01)
    _, tr, _ = drive(cb, [2.0, 2.0, 1.9, 2.0, 1.8, 1.7])
    assert len(cb.history) == 6 and not cb.stopped_early


def test_defaults_are_the_first_runs_behavior():
    cb = lm.ValLossCallback(loader())
    assert cb.patience == 1 and cb.min_delta == 1e-6
    _, tr, _ = drive(cb, [3.0, 2.5, 2.0])                        # the 3-epoch run: strictly improving, never stops
    assert len(cb.history) == 3 and not cb.stopped_early and cb.best_epoch == 3


def test_best_weights_restored_and_checkpoints_saved_at_the_requested_epochs(tmp_path):
    cb = lm.ValLossCallback(loader(), patience=2, min_delta=0.01, save_epochs=(2, 4), ckpt_dir=str(tmp_path))
    mod, tr, sds = drive(cb, [3.0, 2.0, 2.5, 2.4, 2.45])         # best = epoch 2; stops after epoch 5 (two epochs without a real gain)
    assert cb.best_epoch == 2
    assert sorted(os.listdir(tmp_path)) == ["epoch2.pt", "epoch4.pt"]
    assert torch.equal(mod.model.weight, sds[2]["weight"])       # on_train_end restored the epoch-2 weights
    assert torch.equal(torch.load(tmp_path / "epoch4.pt")["weight"], sds[4]["weight"])
    assert not torch.equal(torch.load(tmp_path / "epoch2.pt")["weight"], torch.load(tmp_path / "epoch4.pt")["weight"])


def make_ckpt(path, seed):
    torch.manual_seed(seed)
    m = lm.build_fullattn(V, 0.0, causal=True, pretrain_layers=[])
    torch.save({k: v.detach().cpu() for k, v in m.state_dict().items()}, path)
    return lm.checksum(m)


def test_fine_tuning_from_epoch_k_loads_exactly_that_checkpoint(tmp_path):
    c3, c6 = make_ckpt(tmp_path / "epoch3.pt", 3), make_ckpt(tmp_path / "epoch6.pt", 6)
    assert c3["sha256"] != c6["sha256"]
    for k, want, other in [(3, c3, c6), (6, c6, c3)]:
        torch.manual_seed(0)
        model = lm.build_fullattn(V, 0.3, causal=True, last_token=True)
        proof = SL.init_from_checkpoint(model, str(tmp_path / f"epoch{k}.pt"))
        got = lm.checksum(model)
        assert got["sha256"] == want["sha256"] == proof["checksum_pretrained"]["sha256"] != other["sha256"]
        assert proof["after_loading"]["dist_to_pretrained"] < 1e-6 < proof["before_loading"]["dist_to_pretrained"]
        assert proof["checkpoint"] == f"epoch{k}.pt"


def test_checkpoint_epochs_lists_reached_epochs_and_the_best():
    h = lambda n, best: {"epochs": [{}] * n, "best_epoch": best}
    assert SL.checkpoint_epochs(h(15, 14), None, [3, 6, 10]) == [3, 6, 10, 14]
    assert SL.checkpoint_epochs(h(8, 6), None, [3, 6, 10]) == [3, 6]                 # best = 6 is already in the list
    assert SL.checkpoint_epochs(h(5, 3), None, [3, 6, 10]) == [3]
    assert SL.checkpoint_epochs(h(12, 12), None, [3, 6, 10]) == [3, 6, 10, 12]


def test_split_assertion_detects_a_different_split(tmp_path):
    sp = {"unlabeled": [3, 4, 5, 9], "labeled": [0, 1, 2]}
    info = {"sha256": SL.split_hash(sp), "n_unlabeled": 4, "n_labeled": 3}
    p = tmp_path / "h.json"
    json.dump({"seeds": {"0": info}}, open(p, "w"))
    assert SL.assert_same_split(sp, 0, str(p)) == info
    with pytest.raises(AssertionError):
        SL.assert_same_split({"unlabeled": [3, 4, 5, 8], "labeled": [0, 1, 2]}, 0, str(p))


def test_tiny_end_to_end_run_of_the_long_pipeline(tmp_path):
    """Pre-train a few epochs with early stopping on 150 random reports (CPU), fine-tune from epochs 1, 2 and best, check outputs."""
    rng = np.random.default_rng(0)
    n = 400
    x = np.zeros((n, 512), dtype=np.int32)
    y = (rng.random(n) < 0.5).astype(np.int64)
    for i in range(n):
        k = int(rng.integers(60, 200))
        x[i, :k] = rng.integers(3, V - 5, k) + (y[i] * 5)
    vocab = {"<pad>": 0, "<unk>": 1, "<mask>": 2, **{f"t{i}": i for i in range(3, V)}}
    a = types.SimpleNamespace(pt_epochs=4, pt_patience=1, min_delta=1e9, save_epochs=(1, 2), ckpt_dir=str(tmp_path / "ckpt"), device="cpu",
                              batch_size=32, lr=2.5e-4, workers=0, ft_epochs=1)
    pre, hist = selfsup_pretrain(x[:200], vocab, a)
    assert hist["stopped_early"] and len(hist["epochs"]) == 2                                   # min_delta 1e9: no epoch counts as an improvement
    assert sorted(os.listdir(tmp_path / "ckpt")) == ["epoch1.pt", "epoch2.pt"]
    assert hist["max_epochs"] == 4 and hist["patience"] == 1
    # the returned weights are those of the epoch with the lowest validation loss, which is what the history says
    best = min(hist["epochs"], key=lambda e: e["val_loss"])["epoch"]
    assert hist["best_epoch"] == best
    other = 1 if best == 2 else 2
    assert lm.checksum(pre)["sha256"] == lm.checksum(torch.load(tmp_path / "ckpt" / f"epoch{best}.pt"))["sha256"]
    assert lm.checksum(pre)["sha256"] != lm.checksum(torch.load(tmp_path / "ckpt" / f"epoch{other}.pt"))["sha256"]


def selfsup_pretrain(x, vocab, a):
    from baseline import selfsup
    C.set_seed(0)
    return selfsup.pretrain("ar", x, vocab, a, 0, "pre_ar_test")


def test_bootstrap_helpers_agree_with_the_authors_tpr_function():
    from baseline import long_stats as LS
    rng = np.random.default_rng(0)
    y = (rng.random(4000) < 0.5).astype(int)
    z = rng.normal(size=4000) + 1.5 * y
    m = C.binary_metrics(y, z, decision=0.0)
    t3, t2 = LS.tprs_at(y, z)
    assert abs(t3 - m["tpr@0.001"]) < 1e-12 and abs(t2 - m["tpr@0.01"]) < 1e-12
    # a tiny bootstrap runs, the seed-average ensemble is used, and "resolved" is false for identical runs
    runs = {n: {s: ({}, z + 0.0, {}) for s in LS.SEEDS} for n in ("upper", "lower", "x")}
    res = LS.bootstrap(runs, y, ["upper", "lower", "x"], n_boot=20)
    assert res["x"]["tpr@0.01"]["ens"]["vs_lower"]["resolved"] is False
    assert res["x"]["tpr@0.01"]["ps"]["point"] == pytest.approx(t2)
