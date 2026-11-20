"""Tests of the plumbing of baseline/twolevel.py with a small stand-in for level 1 (any module with core(ids [M, 512]) -> [M, 64]); they run on CPU without the authors' package.
The checks that need the REAL level 1 (ATT+bal weights, position encoding, edits from the call store) are in `python -m baseline.twolevel --selftest` and run inside the pilot kernel (NOTES 19.8)."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from baseline import twolevel as T


class Stub(torch.nn.Module):
    """core(): embedding of the tokens, position-dependent weights, masked mean over the real tokens (id 0 = padding): different for different chunks, 0 for an all-padding chunk."""

    def __init__(self, v=300, d=64):
        super().__init__()
        self.e = torch.nn.Embedding(v, d)
        self.w = torch.nn.Parameter(torch.randn(T.CHUNK, d))

    def core(self, ids):
        keep = (ids != 0).float().unsqueeze(-1)
        x = (self.e(ids) * self.w[None]) * keep
        return x.sum(1) / keep.sum(1).clamp(min=1)


def model(seed=0):
    torch.manual_seed(seed)
    return T.build_model_class()(Stub()).eval()


def report(n_tokens, seed):
    r = np.random.default_rng(seed)
    x = np.zeros(T.CUT, dtype=np.int64)
    x[:min(n_tokens, T.CUT)] = r.integers(1, 300, min(n_tokens, T.CUT))
    return x


def test_number_of_real_chunks():
    f = T.n_real_chunks
    assert list(f(np.array([0, 1, 512, 513, 1024, 1025, 4095, 4096, 4097, 100000]))) == [1, 1, 1, 2, 2, 3, 8, 8, 8, 8]


def test_k1_reduces_to_one_chunk_and_masked_chunks_change_nothing():
    m = model()
    x = torch.from_numpy(np.stack([report(300, i) for i in range(8)]))
    nch = torch.ones(8, dtype=torch.long)
    with torch.no_grad():
        z = m(x, nch)
        vec, mask = m.chunk_vectors(x, nch)
        assert vec.shape == (8, 1, 64) and mask.all()
        assert torch.equal(vec[:, 0], m.level1.core(x[:, :T.CHUNK]))
        x2 = x.clone()
        x2[:, T.CHUNK:] = torch.randint(1, 300, x2[:, T.CHUNK:].shape)                       # garbage in the 7 padding chunks
        assert torch.equal(m(x2, nch), z)


def test_two_chunk_report_chunk_two_is_level1_alone_and_positions_restart():
    m = model()
    base = report(1000, 1)
    x = torch.from_numpy(base)[None]
    nch = torch.tensor([2])
    second = np.zeros(T.CUT, dtype=np.int64)
    second[:488] = base[512:1000]
    with torch.no_grad():
        v, _ = m.chunk_vectors(x, nch)
        v2, _ = m.chunk_vectors(torch.from_numpy(second)[None], torch.tensor([1]))
    assert torch.allclose(v[0, 1], v2[0, 0], atol=1e-6)
    assert not torch.allclose(v[0, 0], v[0, 1])


def test_logit_does_not_depend_on_the_other_reports_in_the_batch():
    m = model()
    toks = np.stack([report(n, i) for i, n in enumerate([100, 700, 1500, 5000, 4096, 513, 1, 2600])])
    nch = T.n_real_chunks(np.array([100, 700, 1500, 5000, 4096, 513, 1, 2600]))
    with torch.no_grad():
        z = m(torch.from_numpy(toks), torch.from_numpy(nch))
        for i in range(len(toks)):
            zi = m(torch.from_numpy(toks[i:i + 1]), torch.from_numpy(nch[i:i + 1]))
            assert torch.allclose(z[i], zi[0], atol=1e-5), i


def test_gradient_reaches_level1_and_level2_and_the_micro_batches_add_up_to_the_full_batch():
    toks = np.stack([report(n, i) for i, n in enumerate([100, 700, 1500, 5000, 900, 513, 40, 2600])])
    tot = np.array([100, 700, 1500, 5000, 900, 513, 40, 2600])
    nch, y = T.n_real_chunks(tot), np.array([0, 1, 1, 0, 1, 0, 0, 1])
    grads = {}
    for micro in (8, 3):
        m = model()
        m.eval()                                                                              # no dropout: the two accumulations must agree
        params = list(m.parameters())
        opt = torch.optim.SGD(params, lr=0.0)
        loss, used = T.train_step(m, opt, params, toks, nch, y, micro, "cpu", print)
        grads[micro] = (loss, [p.grad.clone() if p.grad is not None else None for p in params])
        assert used == micro
        assert m.level1.e.weight.grad is not None and m.cls.grad is not None and m.head.weight.grad is not None
    assert abs(grads[8][0] - grads[3][0]) < 1e-6
    # clip_grad_norm_ rescales the stored gradients in place: both runs clip the same total gradient to the same norm
    for g1, g2 in zip(grads[8][1], grads[3][1]):
        if g1 is not None:
            assert torch.allclose(g1, g2, atol=1e-6)


def test_parameter_counts_of_level2():
    m = model()
    c = T.param_counts(m)
    assert c["level2"] == 64 + 9 * 64 + 2 * 33472 + 128 + 65, c                              # CLS, chunk positions, 2 layers (attention 16,640 + FFN 16,576 + 2 LayerNorms 256), final LayerNorm, linear
    assert c["level1"] == sum(p.numel() for p in m.level1.parameters())
