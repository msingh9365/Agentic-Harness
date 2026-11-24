"""
M3 variants with relative position (RoPE) and/or full attention (NOTES_ROPE.md section 1).   (OURS; no existing module is changed)

    variant       input sinusoidal code   RoPE in q and k   attention
    m3_custom     yes (global position)   no                64-token blocks   (= M3; used only to test the new layer code against the unmodified model)
    rope_blocks   no                      yes               64-token blocks   (V1)
    rope_full     no                      yes               full 512          (V2)
    sin_full      yes (global position)   no                full 512          (V3)

The model is `baseline.pe.chunks_pe_class()` (M3: paper PE, attention pooling) built exactly as M3 is built (same modules, same creation order, so the same seed gives the same initial weights);
only the forward pass of the two Transformer layers and of the embedding / block loop is replaced. The layers keep the parameters of torch.nn.TransformerEncoderLayer (same names, shapes);
RoPE has no parameter. RoPE: head dimension d_h = 8 = 4 frequency pairs, adjacent pairing (x_2i, x_2i+1), inverse frequencies base^(-2i/d_h) with base 10000, position = token index in the 512 window.
"""
import math
import types

import torch
import torch.nn.functional as F

VARIANTS = {  # name: (input_pe, rope, full_attention)
    "m3_custom": (True, False, False),
    "rope_blocks": (False, True, False),
    "rope_full": (False, True, True),
    "sin_full": (True, False, True),
}
BASE = 10000.0


def rope_tables(pos, d_h, dtype, base=BASE):
    """cos, sin [L, d_h] for the integer positions `pos` [L]; each frequency is repeated for its adjacent pair."""
    inv = base ** (-torch.arange(0, d_h, 2, device=pos.device, dtype=torch.float64) / d_h)          # [d_h/2]  (angles in float64, cast at the end: float32 angles lose ~1e-5 at position 300)
    ang = pos.to(torch.float64)[:, None] * inv[None, :]                                           # [L, d_h/2]
    return ang.cos().repeat_interleave(2, dim=-1).to(dtype), ang.sin().repeat_interleave(2, dim=-1).to(dtype)


def apply_rope(x, cos, sin):
    """x [..., L, d_h]; rotates every adjacent pair (x_2i, x_2i+1) by the angle of its position."""
    rot = torch.stack((-x[..., 1::2], x[..., 0::2]), dim=-1).flatten(-2)
    return x * cos + rot * sin


def _layer_forward(layer, ctx, src, src_mask=None, is_causal=False, src_key_padding_mask=None):
    """Pre-norm TransformerEncoderLayer (relu, dropout as in torch) with optional RoPE on q and k. Attention-probability dropout = the layer's dropout in training, as in nn.MultiheadAttention."""
    sa = layer.self_attn
    h = layer.norm1(src)
    B, L, D = h.shape
    H = sa.num_heads
    dh = D // H
    q, k, v = F.linear(h, sa.in_proj_weight, sa.in_proj_bias).chunk(3, dim=-1)
    q, k, v = (t.reshape(B, L, H, dh).transpose(1, 2) for t in (q, k, v))
    if ctx["rope"]:
        cos, sin = rope_tables(ctx["pos"], dh, q.dtype)
        q, k = apply_rope(q, cos, sin), apply_rope(k, cos, sin)
    a = F.scaled_dot_product_attention(q, k, v, attn_mask=src_mask, dropout_p=sa.dropout if layer.training else 0.0)
    a = sa.out_proj(a.transpose(1, 2).reshape(B, L, D))
    x = src + layer.dropout1(a)
    return x + layer._ff_block(layer.norm2(x))


_CLS = None


def model_class():
    global _CLS
    if _CLS is None:
        from baseline import pe
        base = pe.chunks_pe_class()

        class RopeNet(base):
            def __init__(self, *args, variant="rope_blocks", **kwargs):
                super().__init__(*args, pe_mode="paper", pool_mode="attn", **kwargs)
                assert variant in VARIANTS, variant
                self.variant = variant
                self.input_pe, self.rope, self.full_attention = VARIANTS[variant]
                self._ctx = {"rope": self.rope, "pos": None}                     # plain dict: not a module, not in the state dict
                for layer in self.transformer_encoder.layers:
                    layer.forward = types.MethodType(lambda l, *a, _c=self._ctx, **kw: _layer_forward(l, _c, *a, **kw), layer)

            def _run(self, e, pos, src_mask):
                self._ctx["pos"] = pos
                return self.transformer_encoder(e, src_mask)

            def _encode(self, src, src_mask=None):
                """token vectors [B, L, d] after the Transformer and the mask of the real tokens [B, L, 1] (as the parent)."""
                d = self.d_model
                if self.full_attention:
                    L = src.shape[1]
                    pos = torch.arange(L, device=src.device)
                    e = self.encoder(src) * math.sqrt(d)
                    if self.input_pe:
                        e = e + self.pos_encoder.pe[pos, 0, :].to(e.dtype)
                    x = self._run(self.pos_encoder.dropout(e), pos, src_mask)
                else:
                    outs = []
                    for c, chunk in enumerate(self.split(src)):
                        pos = torch.arange(c * self.chunk_size, c * self.chunk_size + chunk.shape[1], device=src.device)
                        e = self.encoder(chunk) * math.sqrt(d)
                        if self.input_pe:
                            e = e + self.pos_encoder.pe[pos, 0, :].to(e.dtype)
                        outs.append(self._run(self.pos_encoder.dropout(e), pos, src_mask))
                    x = torch.cat(outs, dim=1)
                keep = (src != 0)
                if keep.size(1) < x.size(1):
                    keep = F.pad(keep, (0, x.size(1) - keep.size(1)))
                return x.float(), keep.unsqueeze(-1).to(torch.float32)

        _CLS = RopeNet
    return _CLS


def build(vocab_size, variant, dropout=0.3, **extra):
    """The M3 configuration (baseline.cv.model_config, attention pooling) as the variant."""
    from baseline import cv
    return model_class()(variant=variant, **cv.model_config(vocab_size, dropout=dropout, **extra))


def load_model(variant, path, device):
    sd = torch.load(path, map_location="cpu", weights_only=True)
    m = build(sd["encoder.weight"].shape[0], variant)
    m.load_state_dict(sd)
    return m.to(device).eval()
