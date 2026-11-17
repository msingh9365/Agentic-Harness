"""
Job 3 (GPU): self-supervised pre-training experiments, paper Sec. 4.5 / Fig. 6 (experiment B).   (OURS: driver)

Per seed: stratified 80/20 split of the January training set (splits.json), BPE vocabulary 8,192.
  upper            supervised, 100% of train, no pre-training
  lower            supervised, the 20% labeled part only, no pre-training
  mlm_theirs       their MaskedLanguageModelTrainer on the 80% (labels ignored), then fine-tune on the 20%
  mlm_bert         per-position BERT MLM (loss on masked positions only) on the 80%, then fine-tune on the 20%   [our variant]
  ar_flatten       causal full-attention next-token pre-training on the 80%, fine-tuned with the flatten classifier (bidirectional)
  ar_lasttoken     same pre-trained weights, fine-tuned causal with the last non-pad token as the classifier input
  lower_fullattn / upper_fullattn   controls: the AR architecture (full attention) without pre-training
All runs use the same fine-tuning budget (--ft-epochs), AdamW lr 2.5e-4, batch 96. Nothing is selected on the April test set.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import common as C
from baseline import lm

LIT_DIR = "/tmp/nebula_lit"
UNITS = {"baselines": ["upper", "lower", "lower_fullattn", "upper_fullattn"], "mlm_theirs": ["mlm_theirs"],
         "mlm_bert": ["mlm_bert"], "ar": ["ar_flatten", "ar_lasttoken"]}
RUN_COST = {"baselines": 32, "ar": 15, "mlm_theirs": 9, "mlm_bert": 9}      # rough minutes on a T4, to schedule the long ones first


def load(tokens, variant="bpe8k"):
    lab = np.load(os.path.join(tokens, "labels.npz"))
    vdir = os.path.join(tokens, "variants", variant)
    return (np.load(os.path.join(vdir, "x_train.npy")), lab["y_train"], np.load(os.path.join(vdir, "x_test.npy")), lab["y_test"],
            json.load(open(os.path.join(vdir, "vocab.json"))), json.load(open(os.path.join(tokens, "splits.json"))))


def finetune(model, x, y, tag, a, seed):
    """Their LitTrainerWrapper (Lightning) on (x, y): AdamW lr 2.5e-4, batch 96, ft_epochs, gradient clipping 1.0, final weights."""
    from torch.nn import BCEWithLogitsLoss
    from nebula.lit_utils import LitTrainerWrapper
    w = LitTrainerWrapper(pytorch_model=model, name=tag, log_folder=os.path.join(LIT_DIR, tag), epochs=a.ft_epochs,
                          learning_rate=a.lr, device=a.device, batch_size=a.batch_size, gradient_clip_val=1.0,
                          monitor_metric="train_loss", monitor_mode="min", dataloader_workers=a.workers, random_state=seed,
                          loss=BCEWithLogitsLoss(), out_classes=1, verbose=False)
    loader = w.create_dataloader(x, y, shuffle=True)
    t0 = time.time()
    w.train_lit_model(loader, None)
    return w, time.time() - t0, int(np.ceil(len(x) / a.batch_size)) * a.ft_epochs


def predict_logits(w, x):
    loader = w.create_dataloader(x, None, shuffle=False)
    return w.predict_lit_model(loader, return_logits=True).reshape(-1).float().numpy()


def evaluate_and_save(w, model, x_test, y_test, run_dir, extra, save_model=True):
    import torch
    os.makedirs(run_dir, exist_ok=True)
    z = predict_logits(w, x_test)                                  # logits: tie-free ranking (see common.binary_metrics)
    m = C.binary_metrics(y_test, z, decision=0.0)
    np.save(os.path.join(run_dir, "test_logits.npy"), z.astype(np.float32))
    if save_model:
        torch.save(model.state_dict(), os.path.join(run_dir, "model.pt"))
    C.dump_json({"test": m, "test_p32": C.binary_metrics(y_test, C.sigmoid32(z)), **extra}, os.path.join(run_dir, "metrics.json"))
    print(f"  [{extra['run']}] TEST TPR@1e-3 {m['tpr@0.001']:.4f} | TPR@1e-2 {m['tpr@0.01']:.4f} | AUC {m['auc']:.4f} | F1@0.5 "
          f"{m['f1@0.5']:.4f} | {extra['train_seconds']:.0f}s", flush=True)
    return m


def pretrain(kind, x_unl, vocab, a, seed, tag):
    """Pre-train on the unlabeled 80% (2% of it held out for the LM validation loss). Returns (pretrained state dict, history)."""
    import torch
    V = len(vocab)
    T = lm.make_lm_trainers()
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(x_unl))
    n_val = max(1, int(0.02 * len(x_unl)))
    xv, xp = x_unl[perm[:n_val]], x_unl[perm[n_val:]]
    common = dict(vocab=vocab, pretrain_epochs=a.pt_epochs, name=tag, log_folder=os.path.join(LIT_DIR, tag), device=a.device,
                  batch_size=a.batch_size, learning_rate=a.lr, gradient_clip_val=1.0, dataloader_workers=a.workers,
                  random_state=seed, verbose=False)
    np.random.seed(seed)
    if kind == "mlm_theirs":
        model = lm.build_chunked(V, dropout=0.0, pretrain_layers=[1024])                  # as in their train_example_lit_mlm_eval.py
        trainer = lm.with_val_callback(T["theirs_mlm"])(pytorch_model=model, mask_probability=0.15, **common)
        xm, ym = trainer.mask_seq_arr(xv)
        val_loader = trainer.create_dataloader(xm, ym, shuffle=False)
    elif kind == "mlm_bert":
        model = lm.build_chunked(V, dropout=0.0, pooling=None, pretrain_layers=[])        # per-position logits [B, 512, V]
        trainer = lm.with_val_callback(T["bert_mlm"])(vocab_size=V, seed=seed, pytorch_model=model, **common)
        import torch.utils.data as D
        val_loader = D.DataLoader(lm.DynamicMaskDataset(xv, V, seed + 1, fixed=True), batch_size=a.batch_size, shuffle=False)
    elif kind == "ar":
        model = lm.build_fullattn(V, dropout=0.0, causal=True, pretrain_layers=[])        # their causal_attention model, per-position logits
        trainer = lm.with_val_callback(T["ar"])(pytorch_model=model, context_len=512, **common)
        val_loader = trainer.create_dataloader(*lm.ar_tensors(xv), shuffle=False)
    else:
        raise ValueError(kind)
    cb = lm.ValLossCallback(val_loader, patience=getattr(a, "pt_patience", 1), min_delta=getattr(a, "min_delta", 1e-6),
                            save_epochs=getattr(a, "save_epochs", ()), ckpt_dir=getattr(a, "ckpt_dir", None))
    trainer.val_callback = cb
    t0 = time.time()
    trainer.pretrain(xp)
    hist = {"epochs": cb.history, "seconds": time.time() - t0, "n_pretrain": int(len(xp)), "n_val": int(len(xv)),
            "initial_loss_expected_ln_V": float(np.log(V)), "max_epochs": a.pt_epochs, "patience": cb.patience, "min_delta": cb.min_delta,
            "best_epoch": cb.best_epoch, "stopped_early": cb.stopped_early}
    return {k: v.detach().cpu() for k, v in model.state_dict().items()}, hist


def downstream_model(run, V):
    if run.startswith("mlm"):
        return lm.build_chunked(V, 0.3)
    if run == "ar_flatten":
        return lm.build_fullattn(V, 0.3, causal=False)
    if run == "ar_lasttoken":
        return lm.build_fullattn(V, 0.3, causal=True, last_token=True)
    if run.endswith("fullattn"):
        return lm.build_fullattn(V, 0.3, causal=False)
    return lm.build_chunked(V, 0.3)


def run_unit(a):
    import torch
    nb = C.setup_nebula(require_patched=True)
    tokens = a.tokens or C.find_dir_with("labels.npz")
    x, y, xt, yt, vocab, splits = load(tokens)
    V = len(vocab)
    sp = splits["ssl_80_20_stratified_by_family"][str(a.seed)]
    unl, lab = np.asarray(sp["unlabeled"]), np.asarray(sp["labeled"])
    if a.limit:
        r = np.random.default_rng(0)
        unl, lab = r.permutation(unl)[:a.limit], r.permutation(lab)[:max(8, a.limit // 4)]
        x_all_idx = np.concatenate([unl, lab])
    else:
        x_all_idx = np.arange(len(x))
    out = os.path.join(a.out, "ssl", f"seed{a.seed}")
    print(f"[seed {a.seed}/{a.unit}] vocab {V} | unlabeled {len(unl)} labeled {len(lab)} test {len(xt)} | {C.env_info()}", flush=True)
    for run in UNITS[a.unit]:
        C.set_seed(a.seed)
        tag = f"{run}_seed{a.seed}"
        run_dir = os.path.join(out, run)
        extra = {"run": run, "seed": a.seed, "ft_epochs": a.ft_epochs, "pt_epochs": a.pt_epochs, "batch_size": a.batch_size, "lr": a.lr,
                 "n_labeled": int(len(lab)), "n_unlabeled": int(len(unl)), "nebula": nb, "env": C.env_info()}
        model = downstream_model(run, V)
        if run in ("upper", "upper_fullattn"):
            xf, yf = x[x_all_idx], y[x_all_idx]
        else:
            xf, yf = x[lab], y[lab]
        proof = {}
        if run in ("mlm_theirs", "mlm_bert", "ar_flatten", "ar_lasttoken"):
            kind = "ar" if run.startswith("ar") else run
            cache = os.path.join(out, f"pretrained_{kind}.pt")
            if os.path.exists(cache):                                   # ar_flatten and ar_lasttoken share one pre-training
                pre = torch.load(cache, weights_only=True)
                hist = json.load(open(os.path.join(out, f"pretrain_{kind}.json")))
            else:
                pre, hist = pretrain(kind, x[unl], vocab, a, a.seed, f"pre_{kind}_seed{a.seed}")
                os.makedirs(out, exist_ok=True)
                torch.save(lm.encoder_state(pre) if kind != "ar" else pre, cache)     # MLM head is huge: keep the encoder only
                C.dump_json(hist, os.path.join(out, f"pretrain_{kind}.json"))
            before = {"abs_sum": lm.checksum(model)["abs_sum"], "dist_to_pretrained": lm.distance(model.state_dict(), pre)}
            copied = lm.transfer(pre, model)
            after = {"abs_sum": lm.checksum(model)["abs_sum"], "dist_to_pretrained": lm.distance(model.state_dict(), pre)}
            proof = {"tensors_copied": len(copied), "checksum_pretrained": lm.checksum(pre), "checksum_downstream_after": lm.checksum(model),
                     "before_loading": before, "after_loading": after}
            assert lm.checksum(pre)["sha256"] == lm.checksum(model)["sha256"], "downstream encoder is not the pre-trained one"
            assert after["dist_to_pretrained"] < 1e-6 < before["dist_to_pretrained"]
            print(f"  [{run}] fine-tuning starts from the pre-trained weights: encoder checksum {proof['checksum_downstream_after']['sha256']} "
                  f"(abs-sum {before['abs_sum']:.2f} -> {after['abs_sum']:.2f}; distance to pre-trained {before['dist_to_pretrained']:.3f} -> "
                  f"{after['dist_to_pretrained']:.1e}); pre-training val loss per epoch {[round(e['val_loss'], 3) for e in hist['epochs']]}", flush=True)
            extra["pretraining"] = hist
        w, secs, steps = finetune(model, xf, yf, tag, a, a.seed)
        extra.update({"train_seconds": secs, "finetune_steps": steps, "n_finetune": int(len(xf)), "weight_proof": proof})
        evaluate_and_save(w, model, xt, yt, run_dir, extra)
        del w, model
        if a.device != "cpu":
            torch.cuda.empty_cache()


def orchestrate(a):
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    n_gpu = min(n_gpu, a.gpus) if a.gpus else n_gpu
    queue = sorted([(s, u) for s in a.seeds for u in a.units], key=lambda su: -RUN_COST[su[1]])
    running, t0 = {}, time.time()
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while queue or running:
        for g in range(n_gpu):
            if g not in running and queue:
                s, u = queue.pop(0)
                name = f"seed{s}_{u}"
                log = open(os.path.join(a.out, "logs", f"ssl_{name}.log"), "w")
                cmd = [sys.executable, "-m", "baseline.selfsup", "--out", a.out, "--seed", str(s), "--unit", u, "--device", a.device,
                       "--ft-epochs", str(a.ft_epochs), "--pt-epochs", str(a.pt_epochs), "--workers", str(a.workers)]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), name, log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {name}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                print("".join(l for l in open(os.path.join(a.out, "logs", f"ssl_{name}.log")).readlines() if "TEST" in l or "Error" in l)[-1500:], flush=True)
                del running[g]
        time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", default=None, choices=[None, "main"])
    ap.add_argument("--unit", default="baselines", choices=list(UNITS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2])
    ap.add_argument("--units", nargs="*", default=list(UNITS), choices=list(UNITS), help="resume aid: run only these units")
    ap.add_argument("--ft-epochs", type=int, default=10)
    ap.add_argument("--pt-epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=96)
    ap.add_argument("--lr", type=float, default=2.5e-4)
    ap.add_argument("--device", default="gpu")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: use only this many unlabeled reports")
    a = ap.parse_args()
    return orchestrate(a) if a.plan else run_unit(a)


if __name__ == "__main__":
    main()
