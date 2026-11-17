#!/usr/bin/env python
"""
Unit tests for the pooling variants. Run from the repo root:
    python -m hier_nebula.test_pooling --nebula ../nebula
"""
import argparse

import torch

from hier_nebula.model import NEBULA_CONFIG, build_level1
from hier_nebula.pooling_variants import build_variant, chunks_class


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nebula", default="../nebula")
    a = ap.parse_args()
    torch.manual_seed(0)

    # 1. the problem: in the original model two different positions get the SAME encoding
    orig = build_variant(a.nebula, "A").eval()
    ids = torch.full((1, 64), 7, dtype=torch.long)                        # the same token at every position
    emb = orig.embed([ids])[0][0]                                         # [64, d_model]
    assert torch.equal(emb[0], emb[1]) and torch.equal(emb[0], emb[63]), "original encoding is not constant?"
    print("ok: original model, positions 0, 1 and 63 of one chunk get identical vectors")

    # 2. the fix: with fixed_pe, different positions get different vectors
    fixed = build_variant(a.nebula, "C").eval()
    fixed.load_state_dict(build_variant(a.nebula, "B").state_dict())      # same weights, only the flag differs
    emb = fixed.embed([ids])[0][0]
    assert not torch.equal(emb[0], emb[1]), "positions 0 and 1 still identical"
    assert not torch.equal(emb[1], emb[63]), "positions 1 and 63 still identical"
    d = (emb[0] - emb[1]).abs().max().item()
    assert d > 1e-3, d
    print(f"ok: fixed_pe, positions 0 and 1 differ (max abs difference {d:.3f})")

    # 3. the fix adds exactly pe[position] to the embedding, and the same code runs for every chunk
    tok = fixed.encoder(ids) * (fixed.d_model ** 0.5)
    want = tok[0] + fixed.pos_encoder.pe[:64, 0]
    assert torch.allclose(emb, want, atol=1e-6)
    ids2 = torch.randint(1, 1000, (3, 192))
    e = fixed.embed(fixed.split(ids2))
    assert len(e) == 3 and all(x.shape == (3, 64, 64) for x in e)
    print("ok: fixed_pe adds pe[:64, 0] to every chunk")

    # 4. the same token at the same position of two different chunks gets the same encoding
    same = torch.full((1, 128), 9, dtype=torch.long)
    c0, c1 = fixed.embed(fixed.split(same))
    assert torch.equal(c0, c1)
    print("ok: the encoding depends on the position inside the chunk, not on the chunk")

    # 5. fixed_pe=False is the original class: same logits as the released-architecture TransformerEncoderChunks
    base = build_level1(a.nebula, vocab_size=50001, pretrained=True).eval()
    flag = chunks_class(a.nebula)(vocab_size=50001, fixed_pe=False, **NEBULA_CONFIG).eval()
    flag.load_state_dict(base.state_dict())
    x = torch.randint(1, 50000, (4, 512))
    with torch.no_grad():
        assert torch.equal(base(x), flag(x))
    print("ok: fixed_pe=False reproduces the released model bit for bit")

    # 6. shapes of the three variants
    for v in "ABC":
        m = build_variant(a.nebula, v).eval()
        with torch.no_grad():
            assert m(x).shape == (4, 1), v
    n = {v: sum(p.numel() for p in build_variant(a.nebula, v).parameters()) for v in "ABC"}
    assert n["B"] == n["C"] and n["A"] > n["B"]
    print(f"ok: variants build and run; parameters A={n['A']:,} B={n['B']:,} C={n['C']:,}")

    # 7. masked mean pooling (v2): the average runs over real tokens only (id != 0), padding is excluded
    for vm, vu in (("Bm", "B"), ("Cm", "C")):
        mm = build_variant(a.nebula, vm).eval()
        mu = build_variant(a.nebula, vu).eval()
        mu.load_state_dict(mm.state_dict())                                  # same weights, only the pooling differs
        full = torch.randint(1, 50000, (3, 512))                             # no padding: masked == unmasked
        padded = full.clone()
        padded[0, 100:] = 0                                                  # report 0 has 100 real tokens
        padded[1, 400:] = 0
        with torch.no_grad():
            assert torch.allclose(mm(full), mu(full), atol=1e-6), vm
            assert not torch.allclose(mm(padded), mu(padded), atol=1e-4), f"{vm}: padding should change the unmasked mean"
            # by hand: transformer outputs, then the mean over real tokens
            xs = torch.cat(mm.transform(mm.embed(mm.split(padded))), dim=1)
            keep = (padded != 0).unsqueeze(-1).float()
            want = (xs * keep).sum(1) / keep.sum(1)
            assert torch.allclose(mm.core(padded), want, atol=1e-5)
            # the pooled vector ignores what sits at padding positions: replace those outputs by huge numbers
            xs2 = xs.clone(); xs2[0, 100:] = 1e6
            assert torch.allclose((xs2 * keep).sum(1) / keep.sum(1), want, atol=1e-3)
            # an all-padding input does not divide by zero
            assert torch.isfinite(mm(torch.zeros(1, 512, dtype=torch.long))).all()
    assert sum(p.numel() for p in build_variant(a.nebula, "Bm").parameters()) == n["B"]
    print("ok: masked mean (Bm, Cm) equals the plain mean without padding, ignores padding positions, same parameters")

    # 8. full-trace C (results/fulltrace): same model as Cm, fed up to 4096 tokens; chunks are independent, so a report
    #    padded to 4096 gives the same output as the same report padded to 512, and chunks beyond 512 add information
    m512 = build_variant(a.nebula, "Cm").eval()
    m4k = build_variant(a.nebula, "Cm", maxlen=4096).eval()
    m4k.load_state_dict(m512.state_dict())
    short = torch.randint(1, 50000, (3, 512)); short[0, 90:] = 0; short[1, 300:] = 0
    long_ = torch.cat([short, torch.zeros(3, 3584, dtype=torch.long)], 1)
    with torch.no_grad():
        assert torch.allclose(m512(short), m4k(long_), atol=1e-5), "padding a report to 4096 tokens changed the output"
        two = torch.randint(1, 50000, (2, 1024))
        p2 = m4k.core(torch.cat([two, torch.zeros(2, 3072, dtype=torch.long)], 1))          # pooled vectors (random-init logits are ~constant)
        assert not torch.allclose(p2, m512.core(two[:, :512]), atol=1e-3), "the second 512 tokens should change the pooled vector"
        # by hand: mean over the real tokens of the chunk outputs of all 16 chunks
        xs = torch.cat(m4k.transform(m4k.embed(m4k.split(two))), dim=1)
        assert torch.allclose(m4k.core(two), xs.mean(1), atol=1e-5)
    assert sum(p.numel() for p in m4k.parameters()) == sum(p.numel() for p in m512.parameters())
    print("ok: full-trace C (maxlen 4096) equals C on short reports, uses chunks beyond 512 tokens, same parameters")
    print("ALL POOLING TESTS PASSED")


if __name__ == "__main__":
    main()
