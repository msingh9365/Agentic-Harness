#!/usr/bin/env python
"""
v2 trainer for the pooling experiment (results/pooling_v2). v1 (train_pooling.py) is kept unchanged.

    python train_pooling_v2.py --variant A|B|C|B0|C0 --seed N --gpu K [--epochs 10] [--max-steps S] [--include-val]

  A   flatten pooling                         (retrained baseline)
  B   mean pooling, padding tokens excluded   (hier_nebula/pooling_variants.py: Bm)
  C   B + fixed position encoding             (Cm)
  B0  mean pooling over all 512 positions     (the unmasked B of results/pooling)
  C0  C without the padding mask              (the unmasked C of results/pooling)

Differences from v1:
  * no early stopping: all --epochs epochs (default 10) are trained, and a checkpoint is kept after EVERY epoch
    (ckpt/<run>/epochs/epoch_XX.pt, fp16 weights, for the record; last.pt = full training state for resuming,
    removed when the run has finished; best_auc.pt / best_tpr.pt = fp32 weights of the selected epochs;
    final.pt = fp32 weights after the last epoch, used when the epoch count is fixed in advance);
  * after every epoch the January-validation side AND the April set are scored (logits, fp32 eval mode) and written
    to scores/<run>_epochs.npz; the epoch is then selected on the validation side only:
        primary   : highest validation AUC               (ties -> earlier epoch)
        secondary : highest validation TPR at 1% FPR     (threshold convention of analyze_misses.threshold)
    April numbers in the log are for the record and are never used for selection;
  * --max-steps S stops after S optimiser steps (a "step budget" run); --include-val trains on January train+val
    (validation numbers are then in-sample and not used).
Settings otherwise as v1: AdamW lr 2.5e-4 wd 0.01, batch 64, LR x0.5 every 1000 steps, grad clip 0.5, BCE, fp16 autocast.
"""
import argparse
import json
import os
import platform
import subprocess
import sys
import time


def parse():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", choices=["A", "B", "C", "B0", "C0"], required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--max-steps", type=int, default=0, help="stop after this many optimiser steps (0 = no limit)")
    ap.add_argument("--include-val", action="store_true", help="train on the January validation side too")
    ap.add_argument("--tag", default="", help="suffix of the run name, e.g. _steps3000")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--lr", type=float, default=2.5e-4)
    ap.add_argument("--weight-decay", type=float, default=1e-2)
    ap.add_argument("--clip", type=float, default=0.5)
    ap.add_argument("--lr-step", type=int, default=1000)
    ap.add_argument("--no-amp", action="store_true")
    ap.add_argument("--data", default=None)
    ap.add_argument("--code", default=None)
    ap.add_argument("--out", default="/kaggle/working")
    ap.add_argument("--resume-dir", default=None)
    ap.add_argument("--limit", type=int, default=0, help="debug: use only this many training reports")
    ap.add_argument("--device", default="auto")
    return ap.parse_args()


def find_dir(explicit, marker, root="/kaggle/input"):
    if explicit:
        assert os.path.exists(os.path.join(explicit, marker)), f"{marker} not in {explicit}"
        return explicit
    for dp, dn, fn in os.walk(root):
        if os.path.exists(os.path.join(dp, marker)):
            return dp
        if dp.count(os.sep) - root.count(os.sep) > 5:
            dn[:] = []
    raise SystemExit(f"cannot find {marker} under {root}")


class Log:
    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.fh = open(path, "a")

    def __call__(self, *a):
        s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
        print(s, flush=True)
        self.fh.write(s + "\n"); self.fh.flush()


def tpr_at_fpr(np, y, s, fpr=0.01):
    """flagged = score > thr, thr = the (floor(fpr * n_benign) + 1)-th highest benign score."""
    neg = np.sort(s[y == 0])[::-1]
    k = int(np.floor(fpr * len(neg)))
    thr = neg[k] if k < len(neg) else -np.inf
    return float(((s > thr) & (y == 1)).sum() / max(1, (y == 1).sum()))


def main():
    a = parse()
    os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    import numpy as np
    import pandas as pd
    import torch
    from sklearn.metrics import roc_auc_score
    from torch import nn

    run = f"{a.variant}{a.tag}_s{a.seed}"
    log = Log(os.path.join(a.out, "logs", f"{run}.log"))
    data = find_dir(a.data, "tokens_512.npy")
    code = find_dir(a.code, os.path.join("hier_nebula", "pooling_variants.py"))
    sys.path.insert(0, code)
    from hier_nebula.pooling_variants import build_variant, V2_TO_INTERNAL

    use_cuda = torch.cuda.is_available() and a.device in ("auto", "cuda")
    if a.device == "auto" and not use_cuda and os.path.isdir("/kaggle/input"):
        raise SystemExit("NO GPU in this Kaggle session: refusing to train on CPU")
    dev = torch.device("cuda" if use_cuda else "cpu")
    amp = use_cuda and not a.no_amp
    info = {"run": run, "variant": a.variant, "internal_variant": V2_TO_INTERNAL[a.variant], "seed": a.seed,
            "args": vars(a), "host": platform.node(), "python": sys.version.split()[0], "torch": torch.__version__,
            "numpy": np.__version__, "pandas": pd.__version__, "cuda": torch.version.cuda, "amp_fp16": amp,
            "gpu": torch.cuda.get_device_name(0) if use_cuda else "none"}
    log(f"== {run} | variant {a.variant} (internal {V2_TO_INTERNAL[a.variant]}) | gpu {a.gpu}: {info['gpu']} | torch "
        f"{torch.__version__} cuda {torch.version.cuda} | amp {amp} | python {info['python']} numpy {np.__version__}")

    # ---------------------------------------------------------------- data
    X = np.load(os.path.join(data, "tokens_512.npy"), mmap_mode="r")
    y = np.load(os.path.join(data, "labels.npy"))
    rows = pd.read_csv(os.path.join(data, "rows.csv"))
    assert X.shape == (len(rows), 512) and X.dtype == np.int32 and len(y) == len(rows)
    assert (rows.row.values == np.arange(len(rows))).all() and (rows.label.values == y).all()
    idx = {s: np.flatnonzero(rows.side.values == s) for s in ("train", "val", "test")}
    if a.limit:
        idx["train"] = np.random.default_rng(0).permutation(idx["train"])[:a.limit]
        idx["val"] = idx["val"][:max(256, a.limit // 4)]
        idx["test"] = idx["test"][:max(256, a.limit // 4)]
    train_idx = np.sort(np.concatenate([idx["train"], idx["val"]])) if a.include_val else idx["train"]
    log("reports: " + ", ".join(f"{s}={len(v):,}" for s, v in idx.items()) + f" | training on {len(train_idx):,}"
        + (" (January train + validation)" if a.include_val else ""))
    Xg = torch.from_numpy(np.array(X)).to(dev)
    yg = torch.from_numpy(y.astype(np.float32)).to(dev)

    def batch(ix):
        t = torch.from_numpy(ix).to(dev)
        return Xg[t].long(), yg[t]

    # ---------------------------------------------------------------- model
    torch.manual_seed(a.seed)
    if use_cuda:
        torch.cuda.manual_seed_all(a.seed)
    model = build_variant(os.path.join(code, "nebula"), V2_TO_INTERNAL[a.variant]).to(dev)
    n_par = sum(p.numel() for p in model.parameters())
    log(f"model: {n_par:,} parameters; pooling={model.pooling_type}; fixed_pe={model.fixed_pe}; masked_mean={model.masked_mean}")
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.weight_decay)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=a.lr_step, gamma=0.5)
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    loss_fn = nn.BCEWithLogitsLoss()

    ck = os.path.join(a.out, "ckpt", run)
    os.makedirs(os.path.join(ck, "epochs"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "scores"), exist_ok=True)
    state = {"epoch": 0, "step": 0, "history": [], "april": [], "janval": [], "best_auc": (-1.0, 0), "best_tpr": (-1.0, 0),
             "done": False}

    def save(path, obj):
        torch.save(obj, path + ".tmp"); os.replace(path + ".tmp", path)

    for d in (ck, os.path.join(a.resume_dir, "ckpt", run) if a.resume_dir else None):
        p = os.path.join(d, "last.pt") if d else None
        if p and os.path.exists(p):
            c = torch.load(p, map_location=dev, weights_only=False)
            model.load_state_dict(c["model"]); opt.load_state_dict(c["opt"]); sched.load_state_dict(c["sched"])
            scaler.load_state_dict(c["scaler"]); state = c["state"]
            torch.set_rng_state(c["rng_cpu"].cpu())
            if use_cuda and c.get("rng_cuda") is not None:
                torch.cuda.set_rng_state(c["rng_cuda"].cpu())
            log(f"RESUMED from {p}: {state['epoch']} epochs, {state['step']} steps done")
            break

    @torch.no_grad()
    def logits(ix, bs=256):
        model.eval()
        out = np.zeros(len(ix))
        for i in range(0, len(ix), bs):
            xb, _ = batch(ix[i:i + bs])
            out[i:i + bs] = model(xb).squeeze(-1).float().double().cpu().numpy()
        return out

    yv, yt = y[idx["val"]], y[idx["test"]]
    steps_per_epoch = int(np.ceil(len(train_idx) / a.batch_size))
    log(f"batch {a.batch_size}, {steps_per_epoch} steps/epoch, lr {a.lr}, x0.5 every {a.lr_step} steps, clip {a.clip}, "
        f"{a.epochs} epochs" + (f", stop after {a.max_steps} steps" if a.max_steps else "") + "; no early stopping")
    if use_cuda:
        torch.cuda.reset_peak_memory_stats()

    # ---------------------------------------------------------------- training
    while state["epoch"] < a.epochs and not state["done"]:
        ep = state["epoch"] + 1
        t0 = time.time()
        model.train()
        order = np.random.RandomState(a.seed * 1000 + ep).permutation(train_idx)       # same order for every variant
        tot, n = 0.0, 0
        for i in range(0, len(order), a.batch_size):
            xb, yb = batch(order[i:i + a.batch_size])
            with torch.autocast("cuda", dtype=torch.float16, enabled=amp):
                z = model(xb).squeeze(-1)
            loss = loss_fn(z.float(), yb)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            nn.utils.clip_grad_norm_(model.parameters(), a.clip)
            scaler.step(opt); scaler.update(); sched.step()
            tot += loss.item() * len(yb); n += len(yb)
            state["step"] += 1
            if a.max_steps and state["step"] >= a.max_steps:
                state["done"] = True
                break
        if use_cuda:
            torch.cuda.synchronize()
        t_train = time.time() - t0
        zv, zt = logits(idx["val"]), logits(idx["test"])
        vl = float(loss_fn(torch.from_numpy(zv), torch.from_numpy(yv.astype(np.float64))))
        vauc, vtpr = float(roc_auc_score(yv, zv)), tpr_at_fpr(np, yv, zv)
        tauc, ttpr = float(roc_auc_score(yt, zt)), tpr_at_fpr(np, yt, zt)           # for the record only
        rec = {"epoch": ep, "steps": state["step"], "train_loss": tot / n, "val_loss": vl, "val_auc": vauc,
               "val_tpr1": vtpr, "april_auc": tauc, "april_tpr1": ttpr, "train_s": round(t_train, 1),
               "epoch_s": round(time.time() - t0, 1), "lr_end": sched.get_last_lr()[0],
               "peak_gpu_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 3) if use_cuda else 0}
        state["history"].append(rec); state["april"].append(zt); state["janval"].append(zv); state["epoch"] = ep
        sd = {k: v.detach().cpu() for k, v in model.state_dict().items()}
        save(os.path.join(ck, "epochs", f"epoch_{ep:02d}.pt"), {k: v.half() if v.is_floating_point() else v for k, v in sd.items()})
        if vauc > state["best_auc"][0]:
            state["best_auc"] = (vauc, ep); save(os.path.join(ck, "best_auc.pt"), sd)
        if vtpr > state["best_tpr"][0]:
            state["best_tpr"] = (vtpr, ep); save(os.path.join(ck, "best_tpr.pt"), sd)
        np.savez(os.path.join(a.out, "scores", f"{run}_epochs.npz.tmp.npz"), april=np.stack(state["april"]),
                 janval=np.stack(state["janval"]), epochs=np.arange(1, ep + 1))
        os.replace(os.path.join(a.out, "scores", f"{run}_epochs.npz.tmp.npz"), os.path.join(a.out, "scores", f"{run}_epochs.npz"))
        save(os.path.join(ck, "last.pt"), {"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
                                           "scaler": scaler.state_dict(), "state": state, "rng_cpu": torch.get_rng_state(),
                                           "rng_cuda": torch.cuda.get_rng_state() if use_cuda else None})
        log(f"epoch {ep} ({state['step']} steps): train loss {rec['train_loss']:.4f} | val loss {vl:.4f} AUC {vauc:.4f} "
            f"TPR@1% {vtpr:.3f} | [April AUC {tauc:.4f} TPR@1% {ttpr:.3f}, not used] | {rec['epoch_s']:.0f}s | "
            f"peak GPU {rec['peak_gpu_mem_gb']} GB | best val AUC epoch {state['best_auc'][1]}, best val TPR epoch {state['best_tpr'][1]}")

    log(f"finished: {state['epoch']} epochs, {state['step']} steps; selected epoch by validation AUC = {state['best_auc'][1]}, "
        f"by validation TPR@1% = {state['best_tpr'][1]}")
    info.update(history=state["history"], epoch_by_val_auc=state["best_auc"][1], epoch_by_val_tpr1=state["best_tpr"][1],
                steps=state["step"], params=n_par, mean_epoch_s=float(np.mean([h["epoch_s"] for h in state["history"]])),
                peak_gpu_mem_gb=max([h["peak_gpu_mem_gb"] for h in state["history"]] or [0]))
    try:
        info["nvidia_smi"] = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used",
                                                      "--format=csv,noheader"], text=True, timeout=20).strip()
    except Exception:
        pass
    with open(os.path.join(a.out, "logs", f"{run}.json"), "w") as fh:
        json.dump(info, fh, indent=1, default=str)
    save(os.path.join(ck, "final.pt"), {k: v.detach().cpu() for k, v in model.state_dict().items()})   # fp32 weights after the last epoch
    try:
        os.remove(os.path.join(ck, "last.pt"))                  # resume state is not needed once the run is complete
    except OSError:
        pass
    log("done")


if __name__ == "__main__":
    main()
