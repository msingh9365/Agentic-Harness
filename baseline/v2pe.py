"""
Baseline v2-PE: the baseline-v2 recipe with the positional encoding that the paper describes (baseline/pe.py).   (OURS: driver; training = their ModelTrainer)

    python -m baseline.v2pe --plan --seeds 0 1 2 3 4 5 6 7 8 9 --epochs 2 --out /kaggle/working/out
    python -m baseline.v2pe --seed 0 --epochs 2 --pe-mode paper --out out [--tag v2_pe] [--variant bpe50k]            one run (one GPU)

The recipe is that of baseline v2 (baseline/gap.py recipe R8_lr2e-3), unchanged: AdamW lr 2e-3, weight decay 1e-2, batch 96, clip 0.5, dropout 0.3, the authors' ModelTrainer,
BPE-50k, the 90% January slice (hash of baseline/gap_split_hash.json asserted), flatten pooling, 2 epochs, seeds 0 to 9. Same seed = same initial weights and data order as v2.
Nothing is selected on the April set: after every epoch the VALIDATION metrics are stored; the April logits are stored once, after the last epoch, and no April metric
is computed or printed here (they are computed by the evaluation script after all seeds have finished). `--pe-mode released` runs the same driver with the released behaviour
(used once to check that the subclass reproduces the existing v2 seed-0 logits).
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import callstore as CS, common as C, cv, gap, inmem_pad, padtest, pe

RECIPE = dict(lr=2e-3, clip=0.5, dropout=0.3, batch=96, wd=1e-2, tok="bpe50k")        # = gap.RECIPES["R8_lr2e-3"]


def run(a):
    import torch
    nb = C.setup_nebula(require_patched=True)
    recipe = dict(RECIPE, lr=a.lr) if getattr(a, "lr", None) else RECIPE
    out_dir = os.path.join(a.out, a.tag)
    os.makedirs(out_dir, exist_ok=True)
    res_path = os.path.join(out_dir, f"seed{a.seed}.json")
    if os.path.exists(res_path) and not a.force:
        print(f"[{a.tag} seed {a.seed}] already done", flush=True)
        return
    tokens = a.tokens or C.find_dir_with("labels.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    x_all, x_test, vocab = gap.load(tokens, a.variant)
    y_all, y_test = lab["y_train"], lab["y_test"]
    trn, val = gap.val_slice(lab["ym_train"])                       # asserts the stored hash (67,768 / 7,530)
    if a.limit:                                                     # smoke test on CPU only
        r = np.random.default_rng(0)
        trn, val = r.permutation(trn)[:a.limit], r.permutation(val)[:max(40, a.limit // 4)]
        keep = r.permutation(len(x_test))[:300]
        x_test, y_test = x_test[keep], y_test[keep]
    xt, yt, xv, yv = x_all[trn], y_all[trn], x_all[val], y_all[val]
    dev = a.device
    C.set_seed(a.seed)
    model = pe.build_chunks(len(vocab), dropout=RECIPE["dropout"], pe_mode=a.pe_mode, pool_mode=a.pooling)
    trainer = cv.make_trainer(model, dev, "binary", RECIPE["batch"], recipe["lr"], recipe["wd"], clip_grad_norm=recipe["clip"])
    bpe = int(np.ceil(len(xt) / RECIPE["batch"]))
    log, t0, seen = [], time.time(), {"batches": 0}
    rob = {"tok": None}                                             # fixed padded validation set (NOTES 16.3), filled in the in-memory padding branch

    def on_epoch_end(ep):
        zv = cv.predict_logits(model, xv, dev, bs=512)
        mv = C.binary_metrics(yv, zv, decision=0.0)
        rec = {"epoch": ep, "batches": seen["batches"] or ep * bpe, "seconds": round(time.time() - t0, 1), "val_loss": gap.bce_logits(yv, zv), "val": gap.compact(mv), "val_n_tied_at_top": mv["n_tied_at_top"]}
        if rob["tok"] is not None:
            thr = padtest.thresholds(zv, yv, 0.01)
            zr = cv.predict_logits(model, rob["tok"], dev, bs=512)
            rec["val_robust_tpr"], rec["val_robust_thr"], rec["val_robust_n"] = float((zr > thr).mean()), float(thr), int(len(zr))
        log.append(rec)
        print(f"[{a.tag} seed {a.seed}] epoch {ep}: val TPR@1e-3 {mv['tpr@0.001']:.3f} @1e-2 {mv['tpr@0.01']:.3f} pAUC@1e-2 {mv['pauc@0.01']:.3f} AUC {mv['auc']:.4f} loss {rec['val_loss']:.4f} | {rec['seconds']:.0f}s", flush=True)
        np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_val_logits.npy"), zv.astype(np.float32))
        if ep == a.epochs or getattr(a, "every_epoch", False):                         # the April logits: stored, NOT evaluated here
            zt = cv.predict_logits(model, x_test, dev, bs=512)
            np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_test_logits.npy"), zt.astype(np.float32))
            torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_model.pt"))

    edited, epoch_sizes = {}, {}
    aug_dir = a.aug_dir
    if aug_dir and not os.path.exists(os.path.join(aug_dir, f"aug_s{a.seed}_e1_rows.npy")):
        aug_dir = C.find_dir_with(f"aug_s{a.seed}_e1_rows.npy")      # Kaggle mounts private datasets under a path that is not the slug: search /kaggle/input
        print(f"[{a.tag} seed {a.seed}] padding arrays found in {aug_dir}", flush=True)
    if a.pad_store:
        # padding built IN MEMORY from the store of the ORIGINAL reports (baseline/callstore.py, inmem_pad.py); nothing edited is written anywhere. pad_mode "replace": the padded report replaces the
        # original (REPORT 5.10); "keep": a padded COPY is added to all the clean reports. pad_labels "malware": only malware training reports are eligible. One fit() per epoch (as below).
        sp = a.pad_store if os.path.exists(a.pad_store) else os.path.join(C.find_dir_with("all.npz"), "all.npz")
        store = CS.CallStore.load(sp)
        pool_rows = inmem_pad.pool_rows_of(store, y_all, trn)
        print(f"[{a.tag} seed {a.seed}] call store {sp}: {len(store):,} reports; TRAIN pool {len(pool_rows):,} benign reports of the training slice", flush=True)
        where = {int(r): i for i, r in enumerate(trn)}
        if getattr(a, "val_robust", False):
            _, rob["tok"] = inmem_pad.val_robust_set(store, y_all, val, pool_rows)
            print(f"[{a.tag} seed {a.seed}] validation robustness set: {len(rob['tok']):,} malware reports, 20 TRAIN-pool calls prepended", flush=True)
        for ep in range(1, a.epochs + 1):
            rows, tok = inmem_pad.epoch_edits(store, y_all, trn, a.seed, ep, pool_rows, stream=a.pad_stream, labels=a.pad_labels, p_pad=getattr(a, "pad_prob", 0.5))
            if a.pad_mode == "replace":
                pos = np.array([where[int(r)] for r in rows], dtype=np.int64)
                xe, ye = xt.copy(), yt
                xe[pos] = tok.astype(xe.dtype)
            else:
                xe, ye = np.concatenate([xt, tok.astype(xt.dtype)]), np.concatenate([yt, y_all[rows]])
            edited[ep], epoch_sizes[ep] = int(len(rows)), int(len(xe))
            seen["batches"] += int(np.ceil(len(xe) / RECIPE["batch"]))
            trainer.fit(xe, ye, epochs=1)
            on_epoch_end(ep)
            del xe, ye, tok
    elif aug_dir:
        # balanced padding (REPORT 5.10): one array per (seed, epoch) of edited reports, overlaid over the original rows of that epoch only; the authors' ModelTrainer is called
        # once per epoch (checked: epoch-by-epoch fitting on unchanged data reproduces the single fit(epochs=2) exactly, tests/test_v2pe.py)
        where = {int(r): i for i, r in enumerate(trn)}
        for ep in range(1, a.epochs + 1):
            rows = np.load(os.path.join(aug_dir, f"aug_s{a.seed}_e{ep}_rows.npy"))
            tok = np.load(os.path.join(aug_dir, f"aug_s{a.seed}_e{ep}_tok.npy"))
            pos = np.array([where[int(r)] for r in rows if int(r) in where], dtype=np.int64)
            keep = np.array([int(r) in where for r in rows], dtype=bool)
            assert keep.all() or a.limit, "an augmented row is outside the training slice"
            xe = xt.copy()
            xe[pos] = tok[keep].astype(xe.dtype)
            edited[ep] = int(len(pos))
            trainer.fit(xe, yt, epochs=1)
            on_epoch_end(ep)
    else:
        hook = gap.EpochHook(model, bpe, on_epoch_end)
        trainer.model.forwardPass = hook
        trainer.fit(xt, yt, epochs=a.epochs)
        hook.finish()
    assert len(log) == a.epochs, (len(log), a.epochs)
    C.dump_json({"tag": a.tag, "pe_mode": a.pe_mode, "pooling": a.pooling, "aug_dir": a.aug_dir, "pad_store": bool(a.pad_store), "pad_mode": a.pad_mode, "pad_labels": a.pad_labels, "pad_stream": a.pad_stream, "edited_rows_per_epoch": edited, "reports_per_epoch": epoch_sizes, "pos_offset": 0, "recipe": recipe, "pad_prob": getattr(a, "pad_prob", 0.5), "seed": a.seed, "epochs": a.epochs, "batches_per_epoch": bpe, "n_train": int(len(xt)),
                 "n_val": int(len(xv)), "n_val_benign": int((yv == 0).sum()), "tokenizer": a.variant, "split_hash_asserted": True, "env": C.env_info(), "nebula": nb,
                 "train_seconds": round(time.time() - t0, 1), "per_epoch": log, "april": "logits of the last epoch stored in seed<k>_epoch<e>_test_logits.npy; not evaluated by this script"},
                res_path)


def orchestrate(a):
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    n_gpu = min(n_gpu, a.gpus) if a.gpus else n_gpu
    jobs = [s for s in a.seeds if not os.path.exists(os.path.join(a.out, a.tag, f"seed{s}.json"))]
    running, t0, failed = {}, time.time(), []
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                s = jobs.pop(0)
                log = open(os.path.join(a.out, "logs", f"{a.tag}_seed{s}.log"), "a")
                cmd = [sys.executable, "-m", "baseline.v2pe", "--out", a.out, "--seed", str(s), "--epochs", str(a.epochs), "--device", a.device, "--pe-mode", a.pe_mode,
                       "--tag", a.tag, "--variant", a.variant, "--pooling", a.pooling] + (["--aug-dir", a.aug_dir] if a.aug_dir else []) + (
                    ["--pad-store", a.pad_store, "--pad-mode", a.pad_mode, "--pad-labels", a.pad_labels, "--pad-stream", str(a.pad_stream), "--pad-prob", str(a.pad_prob)] if a.pad_store else []) + (
                    ["--lr", str(a.lr)] if a.lr else []) + (["--val-robust"] if a.val_robust else []) + (["--every-epoch"] if a.every_epoch else []) + (["--limit", str(a.limit)] if a.limit else [])
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"seed{s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {a.tag} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {a.tag} {name} exited with {p.returncode}", flush=True)
                lines = [l for l in open(os.path.join(a.out, "logs", f"{a.tag}_{name}.log")).readlines() if "epoch" in l or "Error" in l]
                print("".join(lines[-3:])[-700:], flush=True)
                if p.returncode:
                    failed.append(name)
                del running[g]
        time.sleep(5)
    if failed:
        raise SystemExit(f"runs failed: {failed}")


def smoke(a):
    """Kaggle smoke kernel: (1) seed 0, 1 epoch, paper mode (does it train?); (2) seed 0, 2 epochs, released mode with the subclass (does it reproduce the existing v2 seed-0
    logits?), the two on the two GPUs in parallel. No April metric is computed."""
    jobs = [("smoke_paper", "paper", 1), ("smoke_released", "released", 2)]
    procs = []
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    for g, (tag, mode, ep) in enumerate(jobs):
        log = open(os.path.join(a.out, "logs", f"{tag}_seed0.log"), "a")
        cmd = [sys.executable, "-m", "baseline.v2pe", "--out", a.out, "--seed", "0", "--epochs", str(ep), "--device", a.device, "--pe-mode", mode, "--tag", tag, "--variant", a.variant]
        procs.append((tag, subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g % max(1, a.gpus or 2))), stdout=log, stderr=subprocess.STDOUT), log))
    bad = []
    for tag, p, log in procs:
        rc = p.wait()
        log.close()
        print(f"{tag} exited with {rc}", flush=True)
        print("".join(l for l in open(os.path.join(a.out, "logs", f"{tag}_seed0.log")).readlines() if "epoch" in l or "Error" in l)[-600:], flush=True)
        if rc:
            bad.append(tag)
    if bad:
        raise SystemExit(f"smoke runs failed: {bad}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--pe-mode", default="paper", choices=["paper", "released"])
    ap.add_argument("--tag", default="v2_pe")
    ap.add_argument("--pooling", default="flatten", choices=["flatten", "attn"], help="flatten = the released pooling, attn = attention pooling (baseline/pe.py)")
    ap.add_argument("--pad-store", default=None, help="call-token store of the ORIGINAL reports (baseline/callstore.py all.npz): padding is built in memory per epoch (nothing edited is written)")
    ap.add_argument("--pad-mode", default="replace", choices=["replace", "keep"], help="replace: the padded report replaces the original (REPORT 5.10); keep: a padded copy is added to all clean reports")
    ap.add_argument("--pad-labels", default="all", choices=["all", "malware"], help="which training reports can be padded")
    ap.add_argument("--pad-stream", type=int, default=7000, help="random stream of the padding plan (7000 = REPORT 5.10, 7100 = the keep runs)")
    ap.add_argument("--lr", type=float, default=None, help="learning rate (default: the v2 recipe, 2e-3)")
    ap.add_argument("--pad-prob", type=float, default=0.5, help="share of the training reports edited per epoch (0.5 = REPORT 5.10)")
    ap.add_argument("--val-robust", action="store_true", help="after every epoch: share of validation malware still flagged at the validation 1%% FPR threshold after 20 TRAIN-pool calls are prepended (NOTES 16.3)")
    ap.add_argument("--every-epoch", action="store_true", help="store the April logits and the weights after EVERY epoch (the April logits are not evaluated by this script)")
    ap.add_argument("--aug-dir", default=None, help="folder with aug_s<seed>_e<epoch>_{rows,tok}.npy (balanced padding arrays of baseline/make_pad.py)")
    ap.add_argument("--variant", default="bpe50k")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: use only this many training reports")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        return smoke(a)
    return orchestrate(a) if a.plan else run(a)


if __name__ == "__main__":
    main()
