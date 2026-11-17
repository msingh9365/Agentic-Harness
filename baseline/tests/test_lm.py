"""Tests of the pre-training code: masking statistics (80/10/10 at ~15%), causal masking, initial LM loss ~ ln V,
weight transfer, and a tiny end-to-end run of the self-supervised pipeline on CPU."""
import json
import os

import numpy as np
import pytest
import torch

from baseline import common as C, lm

C.setup_nebula(require_patched=True)
V = 8193                                  # BPE 8,192 + the stray empty vocabulary key (see NOTES.md)


def tokens(n=64, L=512, seed=0, V=V):
    rng = np.random.default_rng(seed)
    x = np.zeros((n, L), dtype=np.int32)
    for i in range(n):
        k = int(rng.integers(100, L))
        x[i, :k] = rng.integers(3, V, k)
    return x


# ------------------------------------------------------------------ masking
def test_bert_mask_is_15_percent_with_80_10_10_and_never_touches_padding():
    x = tokens(400)
    xm, lab = lm.bert_mask(x, lm.MASK, V, np.random.default_rng(1))
    real = x != lm.PAD
    sel = lab != lm.IGNORE
    assert not sel[~real].any(), "padding was selected"
    assert (xm[~real] == lm.PAD).all()
    assert abs(sel[real].mean() - 0.15) < 0.005                                  # 15% of the real tokens are selected
    assert (lab[sel] == x[sel]).all()                                            # labels are the original ids
    n = sel.sum()
    to_mask = ((xm == lm.MASK) & sel).sum() / n
    kept = ((xm == x) & sel).sum() / n                                           # unchanged (also counts random draws that hit the same id)
    changed_random = ((xm != x) & (xm != lm.MASK) & sel).sum() / n
    assert abs(to_mask - 0.8) < 0.01 and abs(changed_random - 0.1) < 0.01 and abs(kept - 0.1) < 0.01
    assert xm[sel & (xm != lm.MASK)].min() >= 3                                  # random replacements are real tokens


def test_their_mlm_masking_has_the_same_statistics():
    """Their MaskedLanguageModelTrainer.mask_seq (used for the primary MLM run)."""
    from nebula.lit_pretraining import MaskedLanguageModelTrainer
    from nebula.models.attention import TransformerEncoderChunks
    from baseline import cv
    vocab = {"<pad>": 0, "<unk>": 1, "<mask>": 2, **{f"t{i}": i for i in range(3, V)}}
    tiny = TransformerEncoderChunks(**cv.model_config(V, pooling="mean", pretrain_layers=[8]))
    t = MaskedLanguageModelTrainer(vocab=vocab, pytorch_model=tiny, device="cpu", dataloader_workers=0, batch_size=8, name="t",
                                   log_folder="/tmp/nebula_lit/test_mask", verbose=False)
    np.random.seed(0)
    x = tokens(300)
    xm, target = t.mask_seq_arr(x)
    real = x != 0
    frac_mask_token = (xm == 2).sum() / real.sum()
    assert abs(frac_mask_token - 0.15 * 0.8) < 0.005                               # 15% selected, 80% of those -> <mask>
    assert target.shape == (300, V) and set(np.unique(target)) <= {0, 1}          # multi-hot "which ids were masked"
    assert (xm[~real] == 0).all()


# ------------------------------------------------------------------ causal masking and initial loss
@pytest.fixture(scope="module")
def ar_model():
    torch.manual_seed(0)
    return lm.build_fullattn(V, 0.0, causal=True, pretrain_layers=[]).eval()


def test_causal_model_cannot_see_later_tokens(ar_model):
    x = torch.from_numpy(tokens(2, seed=3)).long()
    x2 = x.clone()
    t = 100
    x2[:, t] = (x2[:, t] + 17) % (V - 3) + 3                                        # change one token
    with torch.no_grad():
        a, b = ar_model.pretrain(x), ar_model.pretrain(x2)
    assert torch.allclose(a[:, :t], b[:, :t], atol=1e-6), "an earlier position changed: the model looks into the future"
    assert (a[:, t:] - b[:, t:]).abs().max() > 1e-4                                  # positions from t on do change
    # control: without the causal mask the same change DOES reach earlier positions, so the test could fail
    bi = lm.build_fullattn(V, 0.0, causal=False, pretrain_layers=[]).eval()
    with torch.no_grad():
        ba, bb = bi.pretrain(x), bi.pretrain(x2)
    assert (ba[:, :t] - bb[:, :t]).abs().max() > 1e-5


def test_ar_targets_are_shifted_and_ignore_padding():
    x = torch.tensor([[5, 6, 7, 0, 0], [9, 8, 0, 0, 0]])
    xi, y = lm.ar_tensors(x.numpy())
    assert (xi == x).all()
    assert y.tolist() == [[6, 7, lm.IGNORE, lm.IGNORE, lm.IGNORE], [8, lm.IGNORE, lm.IGNORE, lm.IGNORE, lm.IGNORE]]


def test_initial_lm_loss_is_ln_vocab_for_ar_and_bert(ar_model):
    ce = torch.nn.CrossEntropyLoss()                                                 # ignore_index=-100, as their lit model
    x = tokens(8, seed=5)
    xi, y = lm.ar_tensors(x)
    with torch.no_grad():
        logits = ar_model.pretrain(xi)
        loss_ar = ce(logits.reshape(-1, V), y.reshape(-1)).item()
        bert = lm.build_chunked(V, 0.0, pooling=None, pretrain_layers=[]).eval()
        xm, lab = lm.bert_mask(x, lm.MASK, V, np.random.default_rng(0))
        lb = bert.pretrain(torch.from_numpy(xm).long())
        loss_bert = ce(lb.reshape(-1, V), torch.from_numpy(lab).reshape(-1)).item()
    assert abs(loss_ar - np.log(V)) < 0.3, (loss_ar, np.log(V))                    # ln(8193) = 9.01
    assert abs(loss_bert - np.log(V)) < 0.3, (loss_bert, np.log(V))


def test_their_mlm_loss_starts_at_k_times_ln_vocab():
    """Their MLM target is multi-hot (k masked token ids per sequence): the soft-target cross-entropy starts near k * ln V."""
    m = lm.build_chunked(V, 0.0, pretrain_layers=[64]).eval()
    x = tokens(4, seed=7)
    rng = np.random.default_rng(0)
    xm, lab = lm.bert_mask(x, lm.MASK, V, rng)
    target = np.zeros((4, V), dtype=np.float32)
    for i in range(4):
        target[i, np.unique(lab[i][lab[i] != lm.IGNORE])] = 1
    with torch.no_grad():
        loss = torch.nn.CrossEntropyLoss()(m.pretrain(torch.from_numpy(xm).long()), torch.from_numpy(target)).item()
    k = target.sum(1).mean()
    assert abs(loss / k - np.log(V)) < 0.3, (loss, k)


# ------------------------------------------------------------------ weight transfer
def test_transfer_copies_encoder_only_and_checksums_prove_it():
    torch.manual_seed(1)
    pre = lm.build_fullattn(V, 0.0, causal=True, pretrain_layers=[])
    ds = lm.build_fullattn(V, 0.3, causal=False)
    sd = {k: v.clone() for k, v in pre.state_dict().items()}
    assert lm.checksum(ds)["sha256"] != lm.checksum(sd)["sha256"]
    d0 = lm.distance(ds.state_dict(), sd)
    head_before = ds.classifier_head[0][0].weight.clone()
    copied = lm.transfer(sd, ds)
    assert len(copied) > 10 and all(k.startswith(lm.ENCODER_PREFIXES) for k in copied)
    assert lm.checksum(ds)["sha256"] == lm.checksum(sd)["sha256"]
    assert d0 > 1 and lm.distance(ds.state_dict(), sd) < 1e-9
    assert torch.equal(ds.classifier_head[0][0].weight, head_before)                 # the classifier head is NOT overwritten


def test_last_token_classifier_reads_the_last_real_token():
    m = lm.build_fullattn(300, 0.0, causal=True, last_token=True).eval()
    x = torch.from_numpy(tokens(3, V=300, seed=9)).long()
    with torch.no_grad():
        out = m(x)
        h = m.core(x)
        last = (x != 0).sum(1) - 1
        ref = m.classifier_head(h[torch.arange(3), last])
    assert out.shape == (3, 1) and torch.allclose(out, ref)
    x_more_pad = x.clone()
    x_more_pad[0, int(last[0]) + 1:] = 0
    with torch.no_grad():                                                           # tokens after the last real one do not matter
        assert torch.allclose(m(x_more_pad)[0], out[0], atol=1e-6)


# ------------------------------------------------------------------ end to end on CPU
@pytest.mark.slow
def test_selfsup_pipeline_end_to_end_on_cpu(tmp_path):
    from baseline import preprocess as P, selfsup
    v = 120
    rng = np.random.default_rng(0)
    n = 160
    ym = rng.integers(0, 8, n).astype(np.int8)
    y = (ym > 0).astype(np.int8)

    def mk(n, y):
        x = tokens(n, V=v, seed=int(rng.integers(1e6)))
        for i in range(n):
            if y[i]:
                x[i, rng.integers(0, 100, 15)] = 7                                    # learnable signal
        return x
    tok = tmp_path / "tokens"
    (tok / "variants" / "bpe8k").mkdir(parents=True)
    np.savez(tok / "labels.npz", y_train=y, y_test=y[:60], ym_train=ym, ym_test=ym[:60])
    np.save(tok / "variants" / "bpe8k" / "x_train.npy", mk(n, y)); np.save(tok / "variants" / "bpe8k" / "x_test.npy", mk(60, y[:60]))
    json.dump({"<pad>": 0, "<unk>": 1, "<mask>": 2, **{f"t{i}": i for i in range(3, v)}}, open(tok / "variants" / "bpe8k" / "vocab.json", "w"))
    json.dump(P.make_splits(y, ym, seeds=(0,)), open(tok / "splits.json", "w"))
    import argparse
    a = argparse.Namespace(tokens=str(tok), out=str(tmp_path / "out"), seed=0, ft_epochs=1, pt_epochs=2, batch_size=16, lr=2.5e-4,
                           device="cpu", workers=0, limit=0)
    for unit in ["mlm_theirs", "mlm_bert", "ar", "baselines"]:
        a.unit = unit
        selfsup.run_unit(a)
    base = tmp_path / "out" / "ssl" / "seed0"
    for run in ["upper", "lower", "mlm_theirs", "mlm_bert", "ar_flatten", "ar_lasttoken", "lower_fullattn", "upper_fullattn"]:
        m = json.load(open(base / run / "metrics.json"))
        assert 0 <= m["test"]["auc"] <= 1 and (base / run / "test_logits.npy").exists()
        if run in ("mlm_theirs", "mlm_bert", "ar_flatten", "ar_lasttoken"):
            wp = m["weight_proof"]
            assert wp["after_loading"]["dist_to_pretrained"] < 1e-6 < wp["before_loading"]["dist_to_pretrained"]
            assert len(m["pretraining"]["epochs"]) >= 1
