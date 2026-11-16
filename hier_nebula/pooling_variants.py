"""
The three Nebula variants of the pooling experiment (results/pooling/README.md).

    A  pooling="flatten", positional encoding as released   (retrained baseline)
    B  pooling="mean",    positional encoding as released
    C  pooling="mean",    fixed positional encoding

Why C exists: nebula.models.attention.PositionalEncoding.forward(), in batch_first mode, adds
`self.pe[:1]`, i.e. the position-0 vector to EVERY token, so the released model has no
position information inside a 64-token chunk. C adds the encoding of each token's position in
its chunk instead:  x + self.pe[:x.size(1), 0].unsqueeze(0).

The original class is not edited. `ChunksFlagPE` is a subclass whose `fixed_pe` flag switches the
change on; with fixed_pe=False it is the original model (checked in test_pooling.py).

v2 (results/pooling_v2) adds a second flag, `masked_mean`: with pooling="mean" the average is taken over the
real tokens only (token id != 0, 0 = <pad>), not over all 512 positions. Padding positions are still seen by
the attention (as in the original model); only the pooling ignores them.

    Bm = B + masked_mean      Cm = C + masked_mean       (A, B, C are unchanged: v1 results stay reproducible)
"""
import functools
import importlib.util
import math
import os

import torch
from torch import nn, Tensor

from hier_nebula.model import NEBULA_CONFIG

VARIANTS = {
    "A": dict(pooling="flatten", fixed_pe=False),
    "B": dict(pooling="mean", fixed_pe=False),
    "C": dict(pooling="mean", fixed_pe=True),
    "Bm": dict(pooling="mean", fixed_pe=False, masked_mean=True),
    "Cm": dict(pooling="mean", fixed_pe=True, masked_mean=True),
}

# names used in results/pooling_v2: B and C there are the masked ones; B0 and C0 are the old unmasked B and C
V2_TO_INTERNAL = {"A": "A", "B": "Bm", "C": "Cm", "B0": "B", "C0": "C"}


@functools.lru_cache(maxsize=None)
def chunks_class(nebula_root: str):
    """TransformerEncoderChunks with the fixed_pe flag.

    attention.py is loaded straight from its file (it needs only torch), so this works where the
    nebula package itself cannot be imported (Kaggle: no internet, no speakeasy-emulator/unicorn)."""
    path = os.path.join(nebula_root, "nebula", "models", "attention.py")
    spec = importlib.util.spec_from_file_location("nebula_attention_file", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    TransformerEncoderChunks = mod.TransformerEncoderChunks

    class ChunksFlagPE(TransformerEncoderChunks):
        def __init__(self, *args, fixed_pe: bool = False, masked_mean: bool = False, **kwargs):
            super().__init__(*args, **kwargs)
            self.fixed_pe = fixed_pe
            self.masked_mean = masked_mean
            assert not masked_mean or self.pooling_type == "mean", "masked_mean needs pooling='mean'"

        def core(self, src, src_mask=None):
            if not self.masked_mean:
                return super().core(src, src_mask)          # the original code path, unchanged
            x = torch.cat(self.transform(self.embed(self.split(src)), src_mask), dim=1)   # [B, L, d]
            keep = (src != 0)                                                     # real tokens (id 0 = <pad>)
            if keep.size(1) < x.size(1):                                          # split() pads to a multiple of the chunk size
                keep = torch.nn.functional.pad(keep, (0, x.size(1) - keep.size(1)))
            keep = keep.unsqueeze(-1).to(torch.float32)
            return (x.float() * keep).sum(1) / keep.sum(1).clamp(min=1.0)

        def embed(self, chunks):
            if not self.fixed_pe:
                return super().embed(chunks)                  # the original code path, unchanged
            out = []
            for chunk in chunks:
                x = self.encoder(chunk) * math.sqrt(self.d_model)
                pe = self.pos_encoder
                x = x + pe.pe[:x.size(1), 0].unsqueeze(0)     # position inside the 64-token chunk
                out.append(pe.dropout(x))
            return out

    return ChunksFlagPE


def v_flags(v):
    return {"fixed_pe": v["fixed_pe"], "masked_mean": v.get("masked_mean", False)}


def build_variant(nebula_root: str, variant: str, vocab_size: int = 50001) -> nn.Module:
    """Untrained (random-init) model of variant A, B or C; same sizes as the released Nebula."""
    cfg = dict(NEBULA_CONFIG)
    v = VARIANTS[variant]
    cfg["pooling"] = v["pooling"]
    return chunks_class(nebula_root)(vocab_size=vocab_size, **v_flags(v), **cfg)
