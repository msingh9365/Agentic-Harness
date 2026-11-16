"""
3-fold cross-validated training with the authors' ModelTrainer, plus evaluation on the April test set.   (OURS: the loop)

Theirs: TransformerEncoderChunks (model), ModelTrainer (training loop: AdamW, BCE / cross-entropy, time budget, gradient clipping),
        get_tpr_at_fpr (metric). Ours: the loop around them, which their CrossValidation class does not offer because it
        throws the fold models away and never evaluates on the test set (paper Sec. 4.2: "the mean of the three models
        evaluated on the validation subsets and a single test set").

Two training regimes, both with the paper's settings (batch 96, AdamW lr 2.5e-4, weight decay 1e-2, static lr):
  time      time_budget = 300 s per fold (their mechanism). A T4 is faster than the paper's Quadro T2000, so it sees more batches.
  batches   exactly N batches per fold (paper Table 7: BPE 2116, Whitespace 2159). Implemented by raising KeyboardInterrupt
            from the forward pass at batch N+1, which is exactly how their time budget stops training.
"""
import os
import time

import numpy as np

from baseline import common as C

PAPER = dict(batch_size=96, lr=2.5e-4, weight_decay=1e-2, time_budget=300, folds=3)
PAPER_BATCHES = {"bpe50k": 2116, "ws50k": 2159, "ws50k_legacy": 2159}


def model_config(vocab_size, maxlen=512, n_classes=1, chunk_size=64, dropout=0.3, pooling="flatten", **extra):
    """The released Nebula configuration (nebula/__init__.py Nebula.__init__), numClasses=1 for detection."""
    cfg = {"vocab_size": vocab_size, "maxlen": maxlen, "chunk_size": chunk_size, "dModel": 64, "nHeads": 8, "dHidden": 256,
           "nLayers": 2, "numClasses": n_classes, "classifier_head": [64], "layerNorm": False, "dropout": dropout,
           "norm_first": True, "pooling": pooling}
    cfg.update(extra)
    return cfg


class BatchLimit:
    """modelForwardPass that stops training after `max_batches` training batches (eval-mode calls are not counted)."""

    def __init__(self, model, max_batches):
        self.model, self.forward, self.max, self.n = model, model.forward, max_batches, 0

    def __call__(self, x):
        if self.model.training:
            if self.n >= self.max:
                raise KeyboardInterrupt        # caught by ModelTrainer.fit(), the same way as their time budget
            self.n += 1
        return self.forward(x)


def make_trainer(model, device, task, batch_size, lr, weight_decay, time_budget=None, max_batches=None):
    from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss
    from torch.optim import AdamW
    from nebula import ModelTrainer
    kw = {}
    if max_batches is not None:
        kw["modelForwardPass"] = BatchLimit(model, max_batches)
    return ModelTrainer(model=model, device=device, loss_function=BCEWithLogitsLoss() if task == "binary" else CrossEntropyLoss(),
                        optimizer_class=AdamW, optimizer_config={"lr": lr, "weight_decay": weight_decay}, optim_scheduler=None,
                        batchSize=batch_size, verbosity_n_batches=100000, outputFolder=None, falsePositiveRates=C.FPRS,
                        time_budget=time_budget, **kw)


def predict(trainer, x):
    p = trainer.predict_proba(x)
    return p.reshape(-1) if p.shape[1] == 1 else p


def predict_logits(model, x, device, bs=256):
    """Pre-sigmoid scores of a binary model (same forward pass as their predict_proba, without the float32 sigmoid)."""
    import torch
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(x), bs):
            out.append(model(torch.from_numpy(np.asarray(x[i:i + bs])).long().to(device)).float().cpu())
    return torch.cat(out).numpy().reshape(-1)


def run_cv(x, y, x_test, y_test, folds, vocab_size, out, *, task="binary", regime="time", time_budget=PAPER["time_budget"],
           max_batches=None, batch_size=PAPER["batch_size"], lr=PAPER["lr"], weight_decay=PAPER["weight_decay"],
           device="cuda", seed=0, maxlen=512, chunk_size=64, tag="", save_models=True, model_extra=None):
    """folds: list of {"train": idx, "val": idx}. Returns a dict with per-fold and mean/std metrics (validation and test)."""
    import torch
    from nebula.models.attention import TransformerEncoderChunks
    os.makedirs(out, exist_ok=True)
    n_classes = 1 if task == "binary" else 8
    cfg = model_config(vocab_size, maxlen, n_classes, chunk_size, **(model_extra or {}))
    res = {"task": task, "regime": regime, "config": cfg, "batch_size": batch_size, "lr": lr, "weight_decay": weight_decay,
           "time_budget": time_budget if regime == "time" else None, "max_batches": max_batches if regime == "batches" else None,
           "seed": seed, "folds": [], "env": C.env_info()}
    metric = C.binary_metrics if task == "binary" else C.multiclass_metrics
    for i, f in enumerate(folds):
        C.set_seed(seed * 1000 + i)
        tr, va = np.asarray(f["train"]), np.asarray(f["val"])
        model = TransformerEncoderChunks(**cfg)
        n_params = sum(p.numel() for p in model.parameters())
        trainer = make_trainer(model, device, task, batch_size, lr, weight_decay,
                               time_budget=time_budget if regime == "time" else None,
                               max_batches=max_batches if regime == "batches" else None)
        t0 = time.time()
        if regime == "time":
            trainer.fit(x[tr], y[tr], epochs=int(1e4))
        else:
            trainer.fit(x[tr], y[tr], epochs=10 ** 4)
        train_seconds = time.time() - t0
        batches = int(trainer.global_batch_idx)
        per_epoch = int(np.ceil(len(tr) / batch_size))
        if regime == "batches":
            assert batches == max_batches, f"stopped after {batches} batches, expected {max_batches}"
        losses = np.asarray(trainer.train_losses, dtype=np.float64)
        if task == "binary":
            pv, pt = predict_logits(model, x[va], device), predict_logits(model, x_test, device)     # logits: tie-free ranking
            m_val, m_test = metric(y[va], pv, decision=0.0), metric(y_test, pt, decision=0.0)
            m_test_p32 = metric(y_test, C.sigmoid32(pt))        # the literal procedure on float32 probabilities (saturates)
        else:
            pv, pt = predict(trainer, x[va]), predict(trainer, x_test)
            m_val, m_test, m_test_p32 = metric(y[va], pv), metric(y_test, pt), None
        rec = {"fold": i, "n_train": int(len(tr)), "n_val": int(len(va)), "params": int(n_params), "batches_seen": batches,
               "epochs_seen": round(batches / per_epoch, 2), "train_seconds": round(train_seconds, 1),
               "loss_first100": float(losses[:100].mean()), "loss_last100": float(losses[-100:].mean()),
               "loss_curve_every50": losses[::50].round(4).tolist(),
               "val": m_val, "test": m_test, "test_p32": m_test_p32}
        res["folds"].append(rec)
        key = "tpr@0.001" if task == "binary" else "f1_macro"
        print(f"[{tag}] fold {i + 1}/{len(folds)}: {batches} batches ({rec['epochs_seen']} epochs, {train_seconds:.0f}s) | "
              f"val {key} {rec['val'][key]:.4f} | test {key} {rec['test'][key]:.4f} | test auc "
              f"{rec['test'].get('auc', rec['test'].get('auc_ovr_macro')):.4f}", flush=True)
        if save_models:
            torch.save(model.state_dict(), os.path.join(out, f"fold{i}_model.pt"))
            suffix = "logits" if task == "binary" else "probs"
            np.save(os.path.join(out, f"fold{i}_test_{suffix}.npy"), pt.astype(np.float32))
            np.save(os.path.join(out, f"fold{i}_val_{suffix}.npy"), pv.astype(np.float32))
        del trainer, model
        if device != "cpu":
            torch.cuda.empty_cache()
    aggregate(res, task)
    C.dump_json(res, os.path.join(out, "metrics.json"))
    return res


def aggregate(res, task):
    """Mean and std over the fold models (the authors' CV reports np.nanstd of the folds), mean ROC, per-class F1."""
    for split in ["val", "test"]:
        keys = [k for k, v in res["folds"][0][split].items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
        res[f"{split}_mean_std"] = C.mean_std([r[split] for r in res["folds"]], keys)
        if task == "binary":
            res[f"{split}_roc_mean"] = np.mean([r[split]["roc_on_grid"] for r in res["folds"]], axis=0).round(5).tolist()
            if split == "test":
                keys32 = [k for k, v in res["folds"][0]["test_p32"].items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
                res["test_p32_mean_std"] = C.mean_std([r["test_p32"] for r in res["folds"]], keys32)
        else:
            res[f"{split}_f1_per_class_mean"] = np.mean([r[split]["f1_per_class"] for r in res["folds"]], axis=0).round(4).tolist()
    return res
