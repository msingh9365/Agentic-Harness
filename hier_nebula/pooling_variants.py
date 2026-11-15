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
}


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
        def __init__(self, *args, fixed_pe: bool = False, **kwargs):
            super().__init__(*args, **kwargs)
            self.fixed_pe = fixed_pe

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


def build_variant(nebula_root: str, variant: str, vocab_size: int = 50001) -> nn.Module:
    """Untrained (random-init) model of variant A, B or C; same sizes as the released Nebula."""
    cfg = dict(NEBULA_CONFIG)
    v = VARIANTS[variant]
    cfg["pooling"] = v["pooling"]
    return chunks_class(nebula_root)(vocab_size=vocab_size, fixed_pe=v["fixed_pe"], **cfg)
