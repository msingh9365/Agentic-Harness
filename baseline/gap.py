"""
Supervised-recipe grid for "why is the released BPE model better than our retrained ones" (Step 2).   (OURS: driver; training = their ModelTrainer)

Everything is selected on a held-out 10% validation slice of January (stratified by family, fixed seed, saved hash); the April test set is evaluated
after every epoch and STORED, but only the final chosen recipes are looked at (the full grid is an appendix, marked "not used for selection").

    python -m baseline.gap --plan --recipes R0 R1_lr1e-3 --seeds 0 1 2 3 4 --epochs 12 --out /kaggle/working/out
    python -m baseline.gap --recipe R0 --seed 0 --epochs 12 --out out [--save-epochs 5]       one run (one GPU)

A run trains with their ModelTrainer (AdamW, BCE, gradient clipping, batch size as in the recipe) on 90% of January for `epochs` epochs and, at every
epoch boundary, scores the validation slice and the April test set (logits, eval mode) and stores the metrics. Early stopping and the epoch count are
chosen afterwards from the stored validation curves (`select_epoch`), which is equivalent to stopping on the validation loss / TPR without retraining.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import common as C, cv

HERE = os.path.dirname(os.path.abspath(__file__))
# one change at a time against R0 = the recipe of the first reproduction (A): lr 2.5e-4, clip 0.5 (their default), dropout 0.3, batch 96, wd 1e-2, our BPE-50k
BASE = dict(lr=2.5e-4, clip=0.5, dropout=0.3, batch=96, wd=1e-2, tok="bpe50k")
RECIPES = {
    "R0": dict(BASE),                                                        # H1 + H2: 90% of January instead of 2/3, trained by epochs
    "R1_lr1e-3": dict(BASE, lr=1e-3),                                        # H5: weight norms say the authors' training moved the weights about 5x further
    "R2_lr3e-4_clip1": dict(BASE, lr=3e-4, clip=1.0),                        # H4: the settings of the authors' research-branch CV script (run_tokenizer.py, Jan 2024)
    "R3_released_tok": dict(BASE, tok="released_bpe50k"),                    # H3: the released tokenizer
    "R4_lr3e-3": dict(BASE, lr=3e-3),                                        # H5, further along the lr axis (R1 helped)
    "R5_data_2of3": dict(BASE, n_train=50199),                               # H1 isolated: R0 on a random 2/3 of January (the size of one of our CV training folds)
    "R6_lr1e-2": dict(BASE, lr=1e-2),                                        # where does the lr axis peak?
    "R7_lr3e-3_clip1": dict(BASE, lr=3e-3, clip=1.0),                        # R4 with the authors' clipping value
    "R8_lr2e-3": dict(BASE, lr=2e-3),                                        # how close is lr 3e-3 to the collapse at 1e-2? (margin check)
    "R9_lr5e-3": dict(BASE, lr=5e-3),
}
FPRS = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]
KEEP = ["auc", "f1@0.5", "acc@0.5"] + [f"tpr@{f:g}" for f in FPRS]


def val_slice(ym_train, seed=2025, hashes=os.path.join(HERE, "gap_split_hash.json")):
    """Stratified (by family) 10% validation slice of the January training set; asserted against the stored hash."""
    from sklearn.model_selection import train_test_split
    n = len(ym_train)
    trn, val = train_test_split(np.arange(n), test_size=0.1, stratify=ym_train, random_state=seed)
    trn, val = np.sort(trn), np.sort(val)
    h = hashlib.sha256()
    h.update(trn.astype(np.int64).tobytes()); h.update(val.astype(np.int64).tobytes())
    if hashes and os.path.exists(hashes):
        ref = json.load(open(hashes))
        assert (h.hexdigest()[:32], len(trn), len(val)) == (ref["sha256"], ref["n_train"], ref["n_val"]), "validation slice differs from the stored one"
    return trn, val


def compact(m):
    return {k: m[k] for k in KEEP}


class EpochHook:
    """modelForwardPass wrapper: when training reaches the first batch of epoch k+1, run `on_epoch_end(k)` (evaluation), then continue."""

    def __init__(self, model, batches_per_epoch, on_epoch_end):
        self.model, self.forward, self.bpe, self.cb = model, model.forward, batches_per_epoch, on_epoch_end
        self.n, self.epoch = 0, 0

    def __call__(self, x):
        if self.model.training:
            if self.n == self.bpe:                      # an epoch is complete
                self.finish()
            self.n += 1
        return self.forward(x)

    def finish(self):
        self.epoch += 1
        self.n = 0
        was = self.model.training
        self.cb(self.epoch)
        self.model.train(was)


def bce_logits(y, z):
    z = np.asarray(z, dtype=np.float64)
    return float(np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z)))))


def load(tokens, variant):
    d = os.path.join(tokens, "variants", variant)
    return np.load(os.path.join(d, "x_train.npy")), np.load(os.path.join(d, "x_test.npy")), json.load(open(os.path.join(d, "vocab.json")))


def run(a, recipe, seed):
    import torch
    from nebula.models.attention import TransformerEncoderChunks
    nb = C.setup_nebula(require_patched=True)
    cfg = RECIPES[recipe]
    out_dir = os.path.join(a.out, "gap", recipe)
    os.makedirs(out_dir, exist_ok=True)
    res_path = os.path.join(out_dir, f"seed{seed}.json")
    if os.path.exists(res_path) and not a.force:
        print(f"[{recipe} seed {seed}] already done", flush=True)
        return
    tokens = a.tokens or C.find_dir_with("labels.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    x_all, x_test, vocab = load(tokens, cfg["tok"])
    y_all, y_test = lab["y_train"], lab["y_test"]
    trn, val = val_slice(lab["ym_train"])
    if a.limit:
        r = np.random.default_rng(0)
        trn, val = r.permutation(trn)[:a.limit], r.permutation(val)[:max(40, a.limit // 4)]
        keep = r.permutation(len(x_test))[:300]
        x_test, y_test = x_test[keep], y_test[keep]
    if cfg.get("n_train"):                                           # H1: train on fewer reports (random subset, seed-dependent, validation slice untouched)
        trn = np.sort(np.random.default_rng(1000 + seed).permutation(trn)[:cfg["n_train"]])
    xt, yt, xv, yv = x_all[trn], y_all[trn], x_all[val], y_all[val]
    C.set_seed(seed)
    model = TransformerEncoderChunks(**cv.model_config(len(vocab), dropout=cfg["dropout"]))
    trainer = cv.make_trainer(model, a.device, "binary", cfg["batch"], cfg["lr"], cfg["wd"], clip_grad_norm=cfg["clip"])
    bpe = int(np.ceil(len(xt) / cfg["batch"]))
    epochs_log, t0 = [], time.time()
    save = set(a.save_epochs or [])

    def on_epoch_end(ep):
        zv, zt = cv.predict_logits(model, xv, a.device, bs=512), cv.predict_logits(model, x_test, a.device, bs=512)
        mv, mt = C.binary_metrics(yv, zv, decision=0.0), C.binary_metrics(y_test, zt, decision=0.0)
        rec = {"epoch": ep, "batches": ep * bpe, "seconds": round(time.time() - t0, 1), "val_loss": bce_logits(yv, zv), "val": compact(mv),
               "test_NOT_FOR_SELECTION": compact(mt), "val_n_tied_at_top": mv["n_tied_at_top"], "test_p32_tpr@0.001": C.binary_metrics(y_test, C.sigmoid32(zt))["tpr@0.001"]}
        epochs_log.append(rec)
        print(f"[{recipe} seed {seed}] epoch {ep}: val TPR@1e-3 {mv['tpr@0.001']:.3f} @1e-2 {mv['tpr@0.01']:.3f} AUC {mv['auc']:.4f} loss {rec['val_loss']:.4f} "
              f"| {rec['seconds']:.0f}s", flush=True)
        if ep in save:
            torch.save(model.state_dict(), os.path.join(out_dir, f"seed{seed}_epoch{ep}_model.pt"))
            np.save(os.path.join(out_dir, f"seed{seed}_epoch{ep}_test_logits.npy"), zt.astype(np.float32))
            np.save(os.path.join(out_dir, f"seed{seed}_epoch{ep}_val_logits.npy"), zv.astype(np.float32))

    hook = EpochHook(model, bpe, on_epoch_end)
    trainer.model.forwardPass = hook                                 # their loop calls model.forwardPass(data) for every batch
    trainer.fit(xt, yt, epochs=a.epochs)
    hook.finish()                                                    # the last epoch
    assert len(epochs_log) == a.epochs, (len(epochs_log), a.epochs)
    C.dump_json({"recipe": recipe, "config": cfg, "seed": seed, "epochs": a.epochs, "batches_per_epoch": bpe, "n_train": int(len(xt)), "n_val": int(len(xv)),
                 "n_val_benign": int((yv == 0).sum()), "tokenizer": cfg["tok"], "env": C.env_info(), "nebula": nb, "train_seconds": round(time.time() - t0, 1),
                 "per_epoch": epochs_log}, res_path)


def orchestrate(a):
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    n_gpu = min(n_gpu, a.gpus) if a.gpus else n_gpu
    jobs = [(r, s) for r in a.recipes for s in a.seeds if not os.path.exists(os.path.join(a.out, "gap", r, f"seed{s}.json"))]
    running, t0, failed = {}, time.time(), []
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                r, s = jobs.pop(0)
                log = open(os.path.join(a.out, "logs", f"gap_{r}_seed{s}.log"), "a")
                cmd = [sys.executable, "-m", "baseline.gap", "--out", a.out, "--recipe", r, "--seed", str(s), "--epochs", str(a.epochs), "--device", a.device]
                if a.save_epochs:
                    cmd += ["--save-epochs"] + [str(e) for e in a.save_epochs]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"{r}_seed{s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {r} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                lines = [l for l in open(os.path.join(a.out, "logs", f"gap_{name.replace('_seed', '_seed')}.log")).readlines() if "epoch" in l or "Error" in l]
                print("".join(lines[-3:])[-600:], flush=True)
                if p.returncode:
                    failed.append(name)
                del running[g]
        time.sleep(5)
    if failed:
        raise SystemExit(f"runs failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--recipes", nargs="*", default=["R0"])
    ap.add_argument("--recipe", default="R0")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--save-epochs", type=int, nargs="*", default=None, help="also save the model and the test/validation logits at these epochs")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: use only this many training reports")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.plan:
        return orchestrate(a)
    return run(a, a.recipe, a.seed)


if __name__ == "__main__":
    main()
