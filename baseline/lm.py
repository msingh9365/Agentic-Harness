"""
Language-model pre-training pieces for the self-supervised experiments (paper Sec. 4.5).   (OURS, built on the authors' classes)

Theirs (called, not rewritten): nebula.lit_pretraining.{LanguageModelTrainer, MaskedLanguageModelTrainer, AutoRegressiveModelTrainer},
        nebula.lit_utils.{LitTrainerWrapper, PyTorchLightningModelLM}, nebula.models.attention.{TransformerEncoderChunks,
        TransformerEncoderModel} (incl. their `causal_attention` and `pretrain_layers` options).
Ours:   - ValLossCallback: per-epoch validation LM loss, early stopping, best-weights restore (their LM trainers only log train loss)
        - PerPositionMaskedLM: BERT-style MLM with loss only on the masked positions and dynamic masking (a SECOND MLM variant;
          the authors' own MLM predicts a multi-hot "which token ids were masked" vector, see NOTES.md section 4)
        - FullContextAutoRegressive: next-token pre-training on the full 512 tokens with the padding ignored (their AutoRegressiveModelTrainer
          is unfinished: random 256-token windows, loss on padding too)
        - CausalLastTokenClassifier: causal classifier that reads the last non-pad token (the task's second pooling for AR)
        - transfer / checksum helpers that prove the fine-tuning really starts from the pre-trained weights
"""
import copy
import hashlib
import os

import numpy as np
import torch
from torch import nn

PAD, UNK, MASK = 0, 1, 2
IGNORE = -100                      # CrossEntropyLoss ignore_index
ENCODER_PREFIXES = ("encoder.", "transformer_encoder.", "pos_encoder.")


# ----------------------------------------------------------------------------- masking (BERT)
def bert_mask(x, mask_id, vocab_size, rng, p=0.15, p_mask=0.8, p_random=0.1):
    """BERT masking of one batch of token ids x [B, L] (numpy int). Of the real (non-pad) tokens, each is selected with
    probability p; a selected token becomes <mask> with prob p_mask, a random token with prob p_random, stays with the rest.
    Returns (x_masked, labels) where labels hold the original id at selected positions and IGNORE elsewhere."""
    x = np.asarray(x)
    real = x != PAD
    selected = (rng.random(x.shape) < p) & real
    u = rng.random(x.shape)
    xm = x.copy()
    xm[selected & (u < p_mask)] = mask_id
    rnd = selected & (u >= p_mask) & (u < p_mask + p_random)
    xm[rnd] = rng.integers(3, vocab_size, int(rnd.sum()))        # random real token (not pad/unk/mask)
    labels = np.where(selected, x, IGNORE).astype(np.int64)
    return xm, labels


class DynamicMaskDataset(torch.utils.data.Dataset):
    """Masks a fresh random subset of tokens every time a sequence is read (dynamic masking, as in RoBERTa)."""

    def __init__(self, x, vocab_size, seed=0, p=0.15, fixed=False):
        self.x, self.V, self.p, self.fixed = x, vocab_size, p, fixed
        self.rng = np.random.default_rng(seed)
        self.cache = {}

    def __len__(self):
        return len(self.x)

    def __getitem__(self, i):
        if self.fixed and i in self.cache:                       # validation: same masking every epoch
            return self.cache[i]
        xm, lab = bert_mask(self.x[i][None], MASK, self.V, self.rng, self.p)
        out = (torch.from_numpy(xm[0].astype(np.int64)), torch.from_numpy(lab[0]))
        if self.fixed:
            self.cache[i] = out
        return out


def ar_tensors(x):
    """Next-token inputs/targets on the FULL sequence: input = x (512 tokens), target at position t = x[t+1] if that is a real
    token, else IGNORE (padding and the last position are not predicted)."""
    x = torch.as_tensor(np.asarray(x), dtype=torch.long)
    y = torch.full_like(x, IGNORE)
    nxt = x[:, 1:]
    y[:, :-1] = torch.where(nxt != PAD, nxt, torch.full_like(nxt, IGNORE))
    return x, y


# ----------------------------------------------------------------------------- callbacks
def _callback_base():
    import lightning as L
    return L.Callback


class ValLossCallback(_callback_base()):
    """After every training epoch: validation LM loss on a held-out part of the unlabeled data. Early stopping when it has not
    improved by at least `min_delta` for `patience` epochs; the best weights (lowest validation loss) are restored at the end of
    training (before their trainer saves them). The defaults (patience 1, min_delta 1e-6) are what the 3-epoch run used.
    Long pre-training: `save_epochs` + `ckpt_dir` save the model state dict at the end of those epochs (epoch<k>.pt)."""

    def __init__(self, val_loader, patience=1, min_delta=1e-6, save_epochs=(), ckpt_dir=None):
        super().__init__()
        self.val_loader, self.patience, self.min_delta = val_loader, patience, min_delta
        self.save_epochs, self.ckpt_dir = set(save_epochs or ()), ckpt_dir
        self.history, self.best, self.best_epoch, self.best_state, self.bad = [], float("inf"), None, None, 0
        self.ref = float("inf")              # last loss that counted as a real improvement (>= min_delta better than the one before)
        self.stopped_early = False
        self._sum, self._n = 0.0, 0

    def on_train_epoch_start(self, trainer, pl_module):
        self._sum, self._n = 0.0, 0

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        loss = outputs["loss"] if isinstance(outputs, dict) else outputs
        self._sum += float(loss.detach()); self._n += 1

    @torch.no_grad()
    def on_train_epoch_end(self, trainer, pl_module):
        was = pl_module.training
        pl_module.eval()
        losses, n = 0.0, 0
        for batch in self.val_loader:
            batch = [b.to(pl_module.device) for b in batch]
            loss = pl_module._shared_step(batch)
            losses += loss.item() * len(batch[0]); n += len(batch[0])
        pl_module.train(was)
        val = losses / max(1, n)
        epoch = trainer.current_epoch + 1
        self.history.append({"epoch": epoch, "train_loss": self._sum / max(1, self._n), "val_loss": val})
        print(f"  [LM] epoch {epoch}: train loss {self.history[-1]['train_loss']:.4f} | val loss {val:.4f}", flush=True)
        if epoch in self.save_epochs and self.ckpt_dir:
            os.makedirs(self.ckpt_dir, exist_ok=True)
            torch.save({k: v.detach().cpu() for k, v in pl_module.model.state_dict().items()}, os.path.join(self.ckpt_dir, f"epoch{epoch}.pt"))
        if val < self.best - 1e-6:
            self.best, self.best_epoch = val, epoch
            self.best_state = copy.deepcopy({k: v.detach().cpu() for k, v in pl_module.model.state_dict().items()})
        if val < self.ref - self.min_delta:
            self.ref, self.bad = val, 0
        else:
            self.bad += 1
            if self.bad >= self.patience:
                print(f"  [LM] validation loss did not improve by {self.min_delta:g} for {self.patience} epoch(s): stopping early", flush=True)
                self.stopped_early = True
                trainer.should_stop = True

    def on_train_end(self, trainer, pl_module):
        if self.best_state is not None:
            pl_module.model.load_state_dict(self.best_state)


def with_val_callback(trainer_cls):
    """Subclass a trainer class of theirs so that setup_trainer() also installs a ValLossCallback."""
    class Wrapped(trainer_cls):
        val_callback = None

        def setup_trainer(self):
            super().setup_trainer()
            if self.val_callback is not None:
                self.trainer.callbacks.append(self.val_callback)
    Wrapped.__name__ = trainer_cls.__name__ + "WithVal"
    return Wrapped


# ----------------------------------------------------------------------------- trainers (subclasses of theirs)
def make_lm_trainers():
    """Defined lazily: they need nebula (and lightning) to be importable."""
    from nebula.lit_pretraining import AutoRegressiveModelTrainer, LanguageModelTrainer, MaskedLanguageModelTrainer

    class PerPositionMaskedLM(LanguageModelTrainer):
        """BERT-style MLM: loss only on the masked positions, dynamic masking. Model must give per-position logits
        (TransformerEncoderChunks(pooling=None, pretrain_layers=[]))."""

        def __init__(self, vocab_size, seed=0, mask_probability=0.15, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__name__ = "PerPositionMaskedLM"
            self.vocab_size, self.seed, self.mask_probability = vocab_size, seed, mask_probability

        def create_lm_dataloader(self, x_unlabeled, shuffle=True):
            ds = DynamicMaskDataset(x_unlabeled, self.vocab_size, self.seed, self.mask_probability)
            return torch.utils.data.DataLoader(ds, batch_size=self.batch_size, shuffle=shuffle, num_workers=0)

    class FullContextAutoRegressive(AutoRegressiveModelTrainer):
        """Next-token prediction on the full 512 tokens (their trainer samples 256-token windows). Pads are ignored in the loss."""

        def create_lm_dataloader(self, x_unlabeled, shuffle=True):
            x, y = ar_tensors(x_unlabeled)
            return self.create_dataloader(x, y, shuffle=shuffle)      # torch tensors stay int64 (their loader casts numpy y to float)

    return {"theirs_mlm": MaskedLanguageModelTrainer, "bert_mlm": PerPositionMaskedLM, "ar": FullContextAutoRegressive,
            "LanguageModelTrainer": LanguageModelTrainer}


# ----------------------------------------------------------------------------- models
def build_chunked(vocab_size, dropout, pooling="flatten", pretrain_layers=None):
    """Nebula (chunked attention, S = 64): the released architecture."""
    from baseline import cv
    from nebula.models.attention import TransformerEncoderChunks
    return TransformerEncoderChunks(**cv.model_config(vocab_size, dropout=dropout, pooling=pooling, pretrain_layers=pretrain_layers))


def build_fullattn(vocab_size, dropout, causal=False, pretrain_layers=None, last_token=False):
    """Same sizes, but ordinary attention over all 512 tokens (paper: "discards attention chunking"). `causal` switches on their
    causal mask. last_token: causal classifier reading the last non-pad token."""
    from nebula.models.attention import TransformerEncoderModel
    cls = last_token_class() if last_token else TransformerEncoderModel
    return cls(vocab_size=vocab_size, maxlen=512, dModel=64, nHeads=8, dHidden=256, nLayers=2, numClasses=1, classifier_head=[64],
               layerNorm=False, dropout=dropout, norm_first=True, pooling="flatten", pretrain_layers=pretrain_layers,
               causal_attention=causal)


def _last_token_cls():
    from nebula.models.attention import TransformerEncoderModel

    class CausalLastTokenClassifier(TransformerEncoderModel):
        def forward(self, x, src_mask=None):
            h = self.core(x)                                              # [B, L, d] causal hidden states
            last = (x != PAD).sum(1).clamp(min=1) - 1                     # index of the last real token
            return self.classifier_head(h[torch.arange(x.size(0), device=x.device), last])
    return CausalLastTokenClassifier


_LAST = None


def last_token_class():
    global _LAST
    if _LAST is None:
        _LAST = _last_token_cls()
    return _LAST


# ----------------------------------------------------------------------------- weight transfer and proof
def encoder_state(model_or_sd, prefixes=ENCODER_PREFIXES):
    sd = model_or_sd.state_dict() if hasattr(model_or_sd, "state_dict") else model_or_sd
    return {k: v for k, v in sd.items() if k.startswith(prefixes)}


def transfer(pretrained_sd, model, prefixes=ENCODER_PREFIXES):
    """Copy every pre-trained tensor that the downstream model also has with the same shape (embedding, Transformer layers,
    positional buffer). Heads are NOT copied: shapes differ (LM head, classifier on flattened output)."""
    own = model.state_dict()
    copied = []
    for k, v in pretrained_sd.items():
        if k.startswith(prefixes) and k in own and own[k].shape == v.shape:
            own[k] = v.detach().clone()
            copied.append(k)
    model.load_state_dict(own)
    return copied


def checksum(sd_or_model, prefixes=ENCODER_PREFIXES):
    """sum of |w| and sha256 of the encoder tensors (a short, comparable fingerprint of the weights)."""
    sd = encoder_state(sd_or_model, prefixes)
    h = hashlib.sha256()
    total = 0.0
    for k in sorted(sd):
        t = sd[k].detach().cpu().double()
        total += float(t.abs().sum())
        h.update(k.encode()); h.update(t.numpy().tobytes())
    return {"abs_sum": total, "sha256": h.hexdigest()[:16], "n_tensors": len(sd)}


def distance(sd_a, sd_b, prefixes=ENCODER_PREFIXES):
    a, b = encoder_state(sd_a, prefixes), encoder_state(sd_b, prefixes)
    return float(sum(((a[k].double() - b[k].double()) ** 2).sum() for k in a if k in b) ** 0.5)
