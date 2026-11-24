"""
Implementation checks of NOTES_ROPE.md section 3 (run before any training):  python -m rope_test.test_rope --work <dir with in/>   (PYTHONPATH = <repo root>:<repo root>/results)
(a) RoPE relative property; (b) the new layer code with RoPE off and the input code restored reproduces the unmodified M3 (stored seed-0 weights, real tokens), and the full-attention path with a
block-diagonal mask does too; (c) parameter counts; (d) same initial weights as M3 per seed; (e) short CPU training (50 batches) of every variant: finite and falling loss.
Writes param_counts.json and tests_result.json next to this file. Any failure raises.
"""
import argparse
import json
import os

import numpy as np
import torch

from rope_test import rope_model as RM

HERE = os.path.dirname(os.path.abspath(__file__))


def test_a():
    torch.manual_seed(0)
    worst = 0.0
    for off in (1, 7, 64, 300):
        q, k = torch.randn(2, 8, 64, 8), torch.randn(2, 8, 64, 8)
        pos = torch.arange(64)
        c0, s0 = RM.rope_tables(pos, 8, q.dtype)
        c1, s1 = RM.rope_tables(pos + off, 8, q.dtype)
        a = torch.einsum("bhid,bhjd->bhij", RM.apply_rope(q, c0, s0), RM.apply_rope(k, c0, s0))
        b = torch.einsum("bhid,bhjd->bhij", RM.apply_rope(q, c1, s1), RM.apply_rope(k, c1, s1))
        worst = max(worst, float((a - b).abs().max()))
    assert worst < 1e-5, worst
    # the rotation itself: pair 0 (frequency 1) is rotated by exactly `pos` radians
    x = torch.zeros(1, 1, 3, 8)
    x[..., 0] = 1.0
    c, s = RM.rope_tables(torch.tensor([0, 1, 2]), 8, x.dtype)
    y = RM.apply_rope(x, c, s)
    assert torch.allclose(y[0, 0, 1, :2], torch.tensor([np.cos(1.0), np.sin(1.0)], dtype=torch.float32), atol=1e-6)
    return {"max_diff_shifted_scores": worst}


def load_m3(work, seed=0):
    from baseline import padtest
    return padtest.load_model("attbal", os.path.join(work, "in", "m3", "m3", f"seed{seed}.pt"), "cpu")


def test_b(work):
    x = torch.from_numpy(np.load(os.path.join(work, "in", "inputs", "variants", "bpe50k_fix", "x_test.npy"), mmap_mode="r")[:64].astype(np.int64))
    m3 = load_m3(work)
    sd = m3.state_dict()
    out = {}
    with torch.no_grad():
        ref = m3(x).reshape(-1)
        mc = RM.build(sd["encoder.weight"].shape[0], "m3_custom")
        mc.load_state_dict(sd)
        mc.eval()
        d1 = float((mc(x).reshape(-1) - ref).abs().max())
        out["m3_custom_vs_unmodified_max_diff"] = d1
        assert d1 < 1e-5, d1
        mf = RM.build(sd["encoder.weight"].shape[0], "sin_full")
        mf.load_state_dict(sd)
        mf.eval()
        blk = torch.full((512, 512), float("-inf"))
        for c in range(8):
            blk[c * 64:(c + 1) * 64, c * 64:(c + 1) * 64] = 0.0
        d2 = float((mf(x, blk).reshape(-1) - ref).abs().max())
        out["sin_full_with_block_mask_vs_unmodified_max_diff"] = d2
        assert d2 < 1e-5, d2
        d3 = float((mf(x).reshape(-1) - ref).abs().max())                      # without the mask the full attention must differ (not a vacuous test)
        out["sin_full_without_mask_vs_unmodified_max_diff"] = d3
        assert d3 > 1e-3, d3
        # RoPE blocks with the stored weights must differ too (RoPE is active) and be finite
        mr = RM.build(sd["encoder.weight"].shape[0], "rope_blocks")
        mr.load_state_dict(sd)
        mr.eval()
        zr = mr(x).reshape(-1)
        assert torch.isfinite(zr).all() and float((zr - ref).abs().max()) > 1e-3
    return out


def test_c_d(vocab=50001):
    from baseline import common as C, pe
    counts, same = {}, {}
    for seed in (0, 1):
        C.set_seed(seed)
        ref = pe.build_chunks(vocab, dropout=0.3, pe_mode="paper", pool_mode="attn")
        n_ref = sum(p.numel() for p in ref.parameters())
        for v in ("rope_blocks", "rope_full", "sin_full"):
            C.set_seed(seed)
            m = RM.build(vocab, v)
            n = sum(p.numel() for p in m.parameters())
            assert n == n_ref, (v, n, n_ref)
            assert list(m.state_dict()) == list(ref.state_dict())
            eq = all(torch.equal(a, b) for a, b in zip(m.state_dict().values(), ref.state_dict().values()))
            assert eq, f"initial weights of {v} differ from M3 for seed {seed}"
            counts[v], same[f"{v}_seed{seed}"] = n, True
        counts["m3"] = n_ref
    print("parameter counts:", counts, flush=True)
    return counts, same


def test_e(work, steps=50, bs=32):
    from baseline import common as C
    xt = np.load(os.path.join(work, "in", "inputs", "variants", "bpe50k_fix", "x_train.npy"), mmap_mode="r")
    y = np.load(os.path.join(work, "in", "inputs", "labels.npz"))["y_train"].astype(np.float32)
    rng = np.random.default_rng(0)
    idx = rng.choice(len(xt), steps * bs, replace=False)
    out = {}
    for v in ("rope_blocks", "rope_full", "sin_full"):
        C.set_seed(0)
        m = RM.build(50001, v)
        m.train()
        opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-2)
        ls = []
        for i in range(steps):
            b = np.sort(idx[i * bs:(i + 1) * bs])
            xb, yb = torch.from_numpy(xt[b].astype(np.int64)), torch.from_numpy(y[b])
            loss = torch.nn.functional.binary_cross_entropy_with_logits(m(xb).reshape(-1), yb)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(m.parameters(), 0.5)
            opt.step()
            ls.append(float(loss))
        first, last = float(np.mean(ls[:10])), float(np.mean(ls[-10:]))
        assert np.isfinite(ls).all() and last < first, (v, first, last)
        out[v] = {"first10": first, "last10": last}
        print(f"  (e) {v}: loss {first:.3f} -> {last:.3f}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--skip-e", action="store_true")
    a = ap.parse_args()
    torch.set_num_threads(4)
    res = {"a": test_a()}
    print("(a) ok", res["a"], flush=True)
    res["b"] = test_b(a.work)
    print("(b) ok", res["b"], flush=True)
    counts, same = test_c_d()
    res["c_param_counts"], res["d_same_initial_weights"] = counts, same
    json.dump(counts, open(os.path.join(HERE, "param_counts.json"), "w"), indent=1)
    print("(c), (d) ok", flush=True)
    if not a.skip_e:
        res["e"] = test_e(a.work)
        print("(e) ok", flush=True)
    json.dump(res, open(os.path.join(HERE, "tests_result.json"), "w"), indent=1)
    print("ALL TESTS PASSED", flush=True)


if __name__ == "__main__":
    main()
