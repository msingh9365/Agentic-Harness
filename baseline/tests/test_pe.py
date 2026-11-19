"""Tests of baseline/pe.py (v2-PE): (a) per-token and per-chunk positions, (b) "released" mode is bit-identical to the released code on 50 April reports,
(c) the vector at global position p equals Eq. 1-2 of the paper, plus: same state dict and same initial weights in both modes."""
import os

import numpy as np
import pytest
import torch

from baseline import common as C, cv, pe

NB = C.setup_nebula(require_patched=True)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APRIL = os.path.join(ROOT, "results", "_pe_tokens", "variants", "released_bpe50k", "x_test.npy")      # April tokens of the released tokenizer (not in git)
CKPT = os.path.join(NB["nebula_root"], "nebula", "objects", "bpe_50000_torch.model")                  # the released BPE checkpoint
V = 300


def added_vectors(model, token=7):
    """The vectors that embed() adds on top of sqrt(d) * Embedding(token): [512, d], model in eval mode (dropout off), one report with the same token everywhere."""
    model.eval()
    x = torch.full((1, 512), token, dtype=torch.long)
    with torch.no_grad():
        chunks = model.embed(model.split(x))
        base = model.encoder(torch.tensor([[token]])) * np.sqrt(model.d_model)
        return torch.cat(chunks, dim=1)[0] - base[0, 0]


def test_a_positions_inside_a_chunk_and_across_chunks_differ_in_paper_mode_only():
    torch.manual_seed(0)
    paper, released = pe.build_chunks(V, pe_mode="paper"), pe.build_chunks(V, pe_mode="released")
    p, r = added_vectors(paper), added_vectors(released)
    assert not torch.allclose(p[0], p[1])                      # two positions inside chunk 0
    assert not torch.allclose(p[5], p[5 + 64])                 # the same within-chunk position (5) in chunks 0 and 1
    assert not torch.allclose(p[0], p[64]) and not torch.allclose(p[63], p[64])
    assert len({tuple(np.round(v.numpy(), 6)) for v in p}) == 512      # all 512 positions get a different vector
    for t in range(1, 512):                                    # released: the position-0 vector everywhere (no position signal)
        assert torch.equal(r[0], r[t])


def test_c_vector_at_global_position_p_is_equation_1_2_of_the_paper():
    for offset in (0, 1):
        m = pe.build_chunks(V, pe_mode="paper", pos_offset=offset)
        got = added_vectors(m).numpy().astype(np.float64)
        want = pe.paper_pe_table(64, 512, offset)
        assert np.abs(got - want).max() < 5e-5                  # float32 arithmetic (embedding + PE - embedding): 1e-6 level
    # spot values by hand: PE(0) = [0, 1, 0, 1, ...]; PE(1, 0) = sin(1), PE(1, 1) = cos(1); PE(64c + j) uses 64c + j (chunk 3, offset 5 -> 197)
    t = pe.paper_pe_table(64, 512, 0)
    assert np.allclose(t[0, 0::2], 0) and np.allclose(t[0, 1::2], 1) and np.isclose(t[1, 0], np.sin(1.0)) and np.isclose(t[1, 1], np.cos(1.0))
    m = pe.build_chunks(V, pe_mode="paper")
    assert np.abs(added_vectors(m).numpy()[3 * 64 + 5] - t[197]).max() < 5e-5


def test_state_dict_and_initial_weights_are_the_same_in_both_modes():
    torch.manual_seed(3)
    a = pe.build_chunks(V, pe_mode="released")
    torch.manual_seed(3)
    b = pe.build_chunks(V, pe_mode="paper")
    sa, sb = a.state_dict(), b.state_dict()
    assert list(sa) == list(sb) and all(sa[k].shape == sb[k].shape and torch.equal(sa[k], sb[k]) for k in sa)
    from nebula.models.attention import TransformerEncoderChunks
    torch.manual_seed(3)
    base = TransformerEncoderChunks(**cv.model_config(V))
    assert list(base.state_dict()) == list(sa) and all(torch.equal(base.state_dict()[k], sa[k]) for k in sa)


def april_reports(n, vocab_size):
    if os.path.exists(APRIL):
        return np.load(APRIL, mmap_mode="r")[:n].astype(np.int64), "real April reports"
    return np.random.default_rng(0).integers(0, vocab_size, (n, 512)), "random token ids (April tokens not on this machine)"


def test_b_released_mode_is_bit_identical_to_the_released_code_on_50_april_reports():
    from nebula.models.attention import TransformerEncoderChunks
    if os.path.exists(CKPT):
        sd = torch.load(CKPT, weights_only=True)
        v = sd["encoder.weight"].shape[0]
    else:
        torch.manual_seed(0)
        sd, v = None, V
    base = TransformerEncoderChunks(**cv.model_config(v))
    mine = pe.build_chunks(v, pe_mode="released")
    if sd is not None:
        base.load_state_dict(sd); mine.load_state_dict(sd)
    else:
        mine.load_state_dict(base.state_dict())
    x, what = april_reports(50, v)
    x = torch.as_tensor(x)
    base.eval(); mine.eval()
    with torch.no_grad():
        zb, zm = base(x), mine(x)
        zb1, zm1 = torch.cat([base(x[i:i + 1]) for i in range(50)]), torch.cat([mine(x[i:i + 1]) for i in range(50)])      # batch of 50 and one by one
    assert torch.equal(zb, zm) and torch.equal(zb1, zm1), what
    paper = pe.build_chunks(v, pe_mode="paper")
    paper.load_state_dict(base.state_dict()); paper.eval()
    with torch.no_grad():
        assert not torch.equal(paper(x), zb)                  # the encoding really changes the output
    print(f"[test_b] {what}: 50 reports, released-mode logits identical to the released code (batch and single)")


def test_paper_mode_is_deterministic_in_eval_and_backpropagates_into_the_embedding():
    torch.manual_seed(1)
    m = pe.build_chunks(V, pe_mode="paper")
    x = torch.randint(0, V, (4, 512))
    m.eval()
    with torch.no_grad():
        assert torch.equal(m(x), m(x))
        assert torch.allclose(m(x)[:1], m(x[:1]), atol=1e-5)    # batch-size invariant up to float summation order: the positions are per token, not per batch slot
    m.train()
    m(x).sum().backward()
    assert m.encoder.weight.grad is not None and m.encoder.weight.grad.abs().sum() > 0
