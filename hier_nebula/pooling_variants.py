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

v4 (results/pooling_v4) adds a third flag, `pool_mode`, for models that are C (fixed position encoding, 512 tokens) with a
different way of pooling the token vectors. All of them use the real tokens only (id != 0), as Cm:

    Mx   pool_mode="max"      masked max over the real tokens
    MMx  pool_mode="meanmax"  masked mean and masked max concatenated (the first layer of the head takes 2 x 64 inputs)
    ATTx pool_mode="attn"     attention pooling: one learned query vector q (64 values, initialised at 0 = the masked mean),
                              weights = softmax over the real tokens of (x . q) / sqrt(64), output = weighted sum of x

(the two "+aug" models of the round are Cm and ATTx trained on augmented data; the architecture is the same).
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
    "Mx": dict(pooling="mean", fixed_pe=True, pool_mode="max"),
    "MMx": dict(pooling="mean", fixed_pe=True, pool_mode="meanmax"),
    "ATTx": dict(pooling="mean", fixed_pe=True, pool_mode="attn"),
}

# names used in results/pooling_v2: B and C there are the masked ones; B0 and C0 are the old unmasked B and C.
# F (results/fulltrace) = C over the whole report: same model as C (Cm) but fed up to 4096 tokens (64 chunks of 64).
# v4 (results/pooling_v4): M = Mx, MM = MMx, ATT = ATTx; Caug = Cm and ATTaug = ATTx trained on augmented data.
V2_TO_INTERNAL = {"A": "A", "B": "Bm", "C": "Cm", "B0": "B", "C0": "C", "F": "Cm",
                  "M": "Mx", "MM": "MMx", "ATT": "ATTx", "Caug": "Cm", "ATTaug": "ATTx",
                  "Cbal": "Cm", "MMbal": "MMx", "ATTbal": "ATTx", "ATTbalW": "ATTx"}
V2_MAXLEN = {"F": 4096}


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
        def __init__(self, *args, fixed_pe: bool = False, masked_mean: bool = False, pool_mode: str = "mean", **kwargs):
            super().__init__(*args, **kwargs)
            self.fixed_pe = fixed_pe
            self.masked_mean = masked_mean
            self.pool_mode = pool_mode
            assert pool_mode in ("mean", "max", "meanmax", "attn"), pool_mode
            assert not masked_mean or self.pooling_type == "mean", "masked_mean needs pooling='mean'"
            if pool_mode != "mean":
                assert self.pooling_type == "mean"
                self.masked_mean = True                                            # all new poolings use the real tokens only
            if pool_mode == "meanmax":                                             # the head sees [mean, max]
                lin = nn.Linear(2 * self.d_model, self.classifier_head[0][0].out_features)
                nn.init.normal_(lin.weight, mean=0.0, std=0.02); nn.init.zeros_(lin.bias)
                self.classifier_head[0][0] = lin
            if pool_mode == "attn":
                self.att_query = nn.Parameter(torch.zeros(self.d_model))           # zero = uniform weights = masked mean at the start

        def _encode(self, src, src_mask=None):
            """token vectors [B, L, d] and the mask of real tokens [B, L, 1] (float32)."""
            x = torch.cat(self.transform(self.embed(self.split(src)), src_mask), dim=1)
            keep = (src != 0)                                                     # real tokens (id 0 = <pad>)
            if keep.size(1) < x.size(1):                                          # split() pads to a multiple of the chunk size
                keep = torch.nn.functional.pad(keep, (0, x.size(1) - keep.size(1)))
            return x.float(), keep.unsqueeze(-1).to(torch.float32)

        def attention_weights(self, src, src_mask=None):
            """[B, L] softmax weights of the attention pooling over the real tokens (0 on padding)."""
            x, keep = self._encode(src, src_mask)
            sc = (x @ self.att_query) / math.sqrt(self.d_model)                    # [B, L]
            sc = sc.masked_fill(keep.squeeze(-1) == 0, float("-inf"))
            w = torch.softmax(sc, dim=1)
            return torch.nan_to_num(w, nan=0.0)                                    # a report without any real token: all weights 0

        def core(self, src, src_mask=None):
            if not self.masked_mean:
                return super().core(src, src_mask)          # the original code path, unchanged
            x, keep = self._encode(src, src_mask)
            mean = (x * keep).sum(1) / keep.sum(1).clamp(min=1.0)
            if self.pool_mode == "mean":
                return mean
            if self.pool_mode in ("max", "meanmax"):
                mx = x.masked_fill(keep == 0, float("-inf")).max(1).values
                mx = torch.where(torch.isfinite(mx), mx, torch.zeros_like(mx))     # report without a real token
                return mx if self.pool_mode == "max" else torch.cat([mean, mx], dim=-1)
            sc = (x @ self.att_query) / math.sqrt(self.d_model)
            sc = sc.masked_fill(keep.squeeze(-1) == 0, float("-inf"))
            w = torch.nan_to_num(torch.softmax(sc, dim=1), nan=0.0)
            return (w.unsqueeze(-1) * x).sum(1)

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
    return {"fixed_pe": v["fixed_pe"], "masked_mean": v.get("masked_mean", False), "pool_mode": v.get("pool_mode", "mean")}


def build_variant(nebula_root: str, variant: str, vocab_size: int = 50001, maxlen: int = 512) -> nn.Module:
    """Untrained (random-init) model of variant A, B or C; same sizes as the released Nebula.
    maxlen = number of input tokens (a multiple of 64); only the mean-pooling variants work with maxlen > 512."""
    cfg = dict(NEBULA_CONFIG)
    cfg["maxlen"] = maxlen
    assert maxlen == 512 or VARIANTS[variant]["pooling"] == "mean", "flatten pooling is tied to 512 tokens"
    v = VARIANTS[variant]
    cfg["pooling"] = v["pooling"]
    return chunks_class(nebula_root)(vocab_size=vocab_size, **v_flags(v), **cfg)
