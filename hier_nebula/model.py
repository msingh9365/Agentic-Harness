"""
Two-level ("hierarchical") Nebula.

Level 1 is Nebula itself (nebula.models.attention.TransformerEncoderChunks with
the released configuration). It is applied separately to every 512-token chunk
of a report and returns the 64-d vector of Nebula's first classifier layer
(classifier_head[0], i.e. Nebula's own representation just before its logit).

Level 2 is a small Transformer over the sequence of chunk vectors:
    [CLS] + chunk vectors  ->  + learned chunk-position embedding
    -> TransformerEncoder (padding chunks masked)  ->  LayerNorm(CLS)  ->  Linear

With one chunk and level 2 removed this is exactly Nebula, so Nebula is the
natural baseline.
"""
import math
import os
from typing import Optional

import torch
from torch import nn, Tensor

SEQ_LEN = 512

# the configuration of the released bpe_50000_torch.model (nebula/__init__.py)
NEBULA_CONFIG = dict(maxlen=SEQ_LEN, chunk_size=64, dModel=64, nHeads=8, dHidden=256, nLayers=2,
                     numClasses=1, classifier_head=[64], layerNorm=False, dropout=0.3,
                     norm_first=True, pooling="flatten")


def build_level1(nebula_root: str, vocab_size: int, pretrained: bool = True) -> nn.Module:
    """Nebula's TransformerEncoderChunks, optionally with the released weights."""
    from measure_lengths import bootstrap_nebula
    bootstrap_nebula(nebula_root)
    from nebula.models.attention import TransformerEncoderChunks
    m = TransformerEncoderChunks(vocab_size=vocab_size, **NEBULA_CONFIG)
    if pretrained:
        path = os.path.join(nebula_root, "nebula", "objects", "bpe_50000_torch.model")
        m.load_state_dict(torch.load(path, weights_only=True))
    return m


class HierNebula(nn.Module):
    def __init__(self, level1: nn.Module, max_chunks: int = 8, d_model: int = 64, n_heads: int = 4,
                 n_layers: int = 2, d_hidden: int = 128, dropout: float = 0.1, num_classes: int = 1):
        super().__init__()
        self.level1 = level1
        self.max_chunks = max_chunks
        chunk_dim = level1.classifier_head[0][0].out_features      # 64 for the released Nebula
        self.proj = nn.Identity() if chunk_dim == d_model else nn.Linear(chunk_dim, d_model)
        self.cls = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        self.pos = nn.Embedding(max_chunks + 1, d_model)           # position 0 = CLS
        layer = nn.TransformerEncoderLayer(d_model, n_heads, d_hidden, dropout, batch_first=True, norm_first=True)
        self.level2 = nn.TransformerEncoder(layer, n_layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, num_classes)

    # ---- level 1
    def chunk_vector(self, ids: Tensor) -> Tensor:
        """ids [M, 512] -> [M, 64]: Nebula's representation of each chunk."""
        h = self.level1.core(ids)
        return self.level1.classifier_head[0](h)

    def nebula_logit(self, chunk_vec: Tensor) -> Tensor:
        """Nebula's own output for a chunk, from its chunk vector (the baseline)."""
        return self.level1.classifier_head[1](chunk_vec)

    def encode_chunks(self, ids: Tensor, mask: Tensor) -> Tensor:
        """ids [B, K, 512], mask [B, K] (True = real chunk) -> [B, K, 64].
        Only real chunks are run through level 1; padding chunks stay zero."""
        B, K, L = ids.shape
        vec = self.chunk_vector(ids[mask])
        out = vec.new_zeros(B, K, vec.shape[-1])
        out[mask] = vec
        return out

    # ---- level 2
    def classify(self, chunk_vecs: Tensor, mask: Tensor) -> Tensor:
        """chunk_vecs [B, K, D], mask [B, K] -> logits [B, num_classes]."""
        B, K, _ = chunk_vecs.shape
        assert K <= self.max_chunks, f"{K} chunks > max_chunks={self.max_chunks}"
        x = self.proj(chunk_vecs)
        x = torch.cat([self.cls.expand(B, -1, -1), x], dim=1)
        x = x + self.pos(torch.arange(K + 1, device=x.device))
        pad = torch.cat([torch.zeros(B, 1, dtype=torch.bool, device=mask.device), ~mask], dim=1)
        x = self.level2(x, src_key_padding_mask=pad)
        return self.head(self.norm(x[:, 0]))

    def forward(self, ids: Tensor, mask: Tensor) -> Tensor:
        return self.classify(self.encode_chunks(ids, mask), mask)

    def freeze_level1(self, frozen: bool = True):
        for p in self.level1.parameters():
            p.requires_grad = not frozen
