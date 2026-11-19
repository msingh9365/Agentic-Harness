"""
v2-PE: Nebula with the positional encoding that the paper describes.   (OURS; third_party/nebula is not touched)

Paper section 3.3, Eq. (1)-(2): PE(pos, 2i) = sin(pos / 10000^(2i/d)), PE(pos, 2i+1) = cos(pos / 10000^(2i/d)), "the positional encoding of the token
at position pos in the sequence", added to the embedded vectors, sequence length N = 512 (attention spans of S = 64).

The pinned code (nebula/models/attention.py, PositionalEncoding.forward, batch-first) adds `self.pe[:1]` to the whole batch: the vector of position 0 at EVERY token
(commit 8bb17bd; before it `self.pe[:x.size(0)]`, one vector per batch slot). TransformerEncoderChunks.embed then calls it separately for each 64-token chunk.
So the released model has no per-token position signal.

TransformerEncoderChunksPE(pe_mode=...):
  "released"  exactly the released behaviour (the parent's embed is called)
  "paper"     e'_t = sqrt(d) * Embedding(x_t) + PE(g_t), then the same dropout, with g_t = chunk_size * c + j the GLOBAL position of offset j in chunk c
              (the chunk at index c gets positions 64c .. 64c+63, not 0..63). Padding tokens get their position too (the paper's equation is per position
              in the sequence). The table is the model's own `pos_encoder.pe` buffer (Eq. 1-2 with d = 64). Positions are 0-based like that buffer;
              `pos_offset` = 1 gives the 1-based reading of the paper's e = [e_1, ..., e_N].
The state dict has the same keys and shapes in both modes (the table is a buffer, not a parameter), and for the same seed the same initial weights.

Pooling option `pool_mode` (ATT+bal follow-up; ported from nebula-length-study, hier_nebula/pooling_variants.py, variant ATTx):
  "flatten"  the released pooling (the default; unchanged)
  "attn"     attention pooling: ONE learned query q (d values, initialised at 0), scores (x . q) / sqrt(d) over the token vectors after the Transformer, softmax over the
             REAL tokens only (token id != 0, 0 = <pad>), output = the weighted sum of the token vectors, then the same head (whose first layer takes d inputs instead of
             512 * d). q = 0 gives uniform weights, i.e. the masked mean. The attention itself still sees the padding positions (as in the released model); only the pooling
             ignores them. A report without any real token gets weights 0 (output 0).
"""
import math

import numpy as np
import torch
from torch import nn

_CLS = None


def chunks_pe_class():
    """Defined lazily: it needs nebula to be importable."""
    global _CLS
    if _CLS is None:
        from nebula.models.attention import TransformerEncoderChunks

        class TransformerEncoderChunksPE(TransformerEncoderChunks):
            def __init__(self, *args, pe_mode="released", pos_offset=0, pool_mode="flatten", **kwargs):
                assert pool_mode in ("flatten", "attn"), pool_mode
                if pool_mode == "attn":
                    kwargs["pooling"] = "mean"          # the head takes d_model inputs (the base class sizes it from `pooling`); core() below pools by attention
                super().__init__(*args, **kwargs)
                assert pe_mode in ("released", "paper"), pe_mode
                self.__name__ = "TransformerEncoderChunksPE"
                self.pe_mode, self.pos_offset, self.pool_mode = pe_mode, pos_offset, pool_mode
                if pool_mode == "attn":
                    self.att_query = nn.Parameter(torch.zeros(self.d_model))        # zero = uniform weights = the masked mean at the start

            def _encode(self, src, src_mask=None):
                """token vectors [B, L, d] after the Transformer and the mask of the real tokens [B, L, 1] (float32)."""
                x = torch.cat(self.transform(self.embed(self.split(src)), src_mask), dim=1)
                keep = (src != 0)
                if keep.size(1) < x.size(1):                                        # split() pads to a multiple of the chunk size
                    keep = torch.nn.functional.pad(keep, (0, x.size(1) - keep.size(1)))
                return x.float(), keep.unsqueeze(-1).to(torch.float32)

            def attention_weights(self, src, src_mask=None):
                """[B, L] softmax weights of the attention pooling over the real tokens (exactly 0 on padding; all 0 for a report without a real token)."""
                x, keep = self._encode(src, src_mask)
                sc = (x @ self.att_query) / math.sqrt(self.d_model)
                sc = sc.masked_fill(keep.squeeze(-1) == 0, float("-inf"))
                return torch.nan_to_num(torch.softmax(sc, dim=1), nan=0.0)

            def core(self, src, src_mask=None):
                if self.pool_mode != "attn":
                    return super().core(src, src_mask)
                x, keep = self._encode(src, src_mask)
                sc = (x @ self.att_query) / math.sqrt(self.d_model)
                sc = sc.masked_fill(keep.squeeze(-1) == 0, float("-inf"))
                w = torch.nan_to_num(torch.softmax(sc, dim=1), nan=0.0)
                return (w.unsqueeze(-1) * x).sum(1)

            def embed(self, chunks):
                if self.pe_mode == "released":
                    return super().embed(chunks)
                out = []
                for c, chunk in enumerate(chunks):                           # chunk: [batch, chunk_size] token ids
                    e = self.encoder(chunk) * math.sqrt(self.d_model)
                    g = torch.arange(c * self.chunk_size, c * self.chunk_size + chunk.shape[1], device=chunk.device) + self.pos_offset
                    e = e + self.pos_encoder.pe[g, 0, :].to(e.dtype)         # [chunk_size, d] broadcast over the batch
                    out.append(self.pos_encoder.dropout(e))
                return out
        _CLS = TransformerEncoderChunksPE
    return _CLS


def build_chunks(vocab_size, dropout=0.3, pe_mode="released", pos_offset=0, pool_mode="flatten", **extra):
    """The released Nebula configuration (baseline.cv.model_config) as TransformerEncoderChunksPE."""
    from baseline import cv
    return chunks_pe_class()(pe_mode=pe_mode, pos_offset=pos_offset, pool_mode=pool_mode, **cv.model_config(vocab_size, dropout=dropout, **extra))


def paper_pe_table(d_model=64, n_pos=512, offset=0):
    """Eq. (1)-(2) of the paper evaluated independently of the model's buffer (float64): [n_pos, d_model], row p = PE(p + offset, .)."""
    pos = np.arange(n_pos, dtype=np.float64)[:, None] + offset
    i = np.arange(d_model // 2, dtype=np.float64)[None, :]
    angle = pos / (10000.0 ** (2 * i / d_model))
    pe = np.zeros((n_pos, d_model))
    pe[:, 0::2], pe[:, 1::2] = np.sin(angle), np.cos(angle)
    return pe
