#!/usr/bin/env python
"""
Train one pooling variant of Nebula from scratch on one GPU (Kaggle or local) and write its scores.

    python train_pooling.py --variant A|B|C --seed N --gpu K

  A  pooling="flatten", positional encoding as released   (retrained baseline)
  B  pooling="mean",    positional encoding as released
  C  pooling="mean",    fixed positional encoding          (hier_nebula/pooling_variants.py)

Data (dataset "nebula-speakeasy-tokens", built by scripts/kaggle/make_token_dataset.py):
  tokens_512.npy int32 [92700, 512]  first 512 Nebula tokens per report, pad id 0
  labels.npy     int8  [92700]
  rows.csv       row, id, split, family, label, n_tokens_full, n_chunks, hash_apis, side
Training uses side == "train" (January, grouped), early stopping uses side == "val" (January
validation, disjoint hash_apis groups), scoring covers side == "test" (April) and "val".

Settings = Nebula's own from-scratch settings in nebula/scripts/cross_validation/_speakeasy_model_loop.py
(same model sizes, dropout 0.3, BCEWithLogitsLoss, AdamW lr 2.5e-4, StepLR gamma 0.5 every 1000
steps (3000-step budget / 3), grad-norm clip 0.5, batch size 64), plus fp16 autocast, early stopping on
the January validation loss, and a per-epoch checkpoint that a restarted run resumes from.

Outputs, in --out (default /kaggle/working):
  scores/pool_<V>_seed<N>_{april,janval}.parquet   columns row, seed, score (+ logit); same layout as
                                                   results/go_no_go/scores (score = sigmoid(logit), float64)
  ckpt/<V>_s<N>/last.pt (resume) and best.pt (best validation loss)
  logs/<V>_s<N>.log, logs/<V>_s<N>.json            epoch times, GPU name, package versions, peak GPU memory
"""
import argparse
import glob
import json
import os
import platform
import subprocess
import sys
import time


def parse():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", choices=["A", "B", "C"], required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--gpu", type=int, default=0, help="physical GPU index (sets CUDA_VISIBLE_DEVICES)")
    ap.add_argument("--epochs", type=int, default=10, help="maximum number of epochs")
    ap.add_argument("--patience", type=int, default=2, help="stop after this many epochs without a better validation loss")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--lr", type=float, default=2.5e-4)
    ap.add_argument("--weight-decay", type=float, default=1e-2)
    ap.add_argument("--clip", type=float, default=0.5)
    ap.add_argument("--lr-step", type=int, default=1000, help="StepLR step size in optimiser steps")
    ap.add_argument("--no-amp", action="store_true", help="fp32 instead of fp16 autocast")
    ap.add_argument("--data", default=None, help="folder with tokens_512.npy (default: search /kaggle/input)")
    ap.add_argument("--code", default=None, help="folder with hier_nebula/ and nebula/ (default: search /kaggle/input)")
    ap.add_argument("--out", default="/kaggle/working")
    ap.add_argument("--resume-dir", default=None, help="extra folder to look for ckpt/<V>_s<N>/last.pt in")
    ap.add_argument("--limit", type=int, default=0, help="debug: use only this many training reports")
    ap.add_argument("--device", default="auto", help="auto | cuda | cpu")
    return ap.parse_args()


def find_dir(explicit, marker, roots=("/kaggle/input",)):
    if explicit:
        assert os.path.exists(os.path.join(explicit, marker)), f"{marker} not in {explicit}"
        return explicit
    for r in roots:
        for dp, _, fns in os.walk(r):
            if os.path.exists(os.path.join(dp, marker)):
                return dp
            if dp.count(os.sep) - r.count(os.sep) > 5:
                _[:] = []
    raise SystemExit(f"cannot find {marker} under {roots}; pass the folder explicitly")


class Log:
    def __init__(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.fh = open(path, "a")

    def __call__(self, *a):
        s = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
        print(s, flush=True)
        self.fh.write(s + "\n"); self.fh.flush()


def main():
    a = parse()
    # which physical GPU this process uses; must be set before torch initialises CUDA
    os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    import numpy as np
    import pandas as pd
    import torch
    from torch import nn

    tag = f"{a.variant}_s{a.seed}"
    log = Log(os.path.join(a.out, "logs", f"{tag}.log"))
    data = find_dir(a.data, "tokens_512.npy")
    code = find_dir(a.code, os.path.join("hier_nebula", "pooling_variants.py"))
    sys.path.insert(0, code)
    from hier_nebula.pooling_variants import build_variant

    use_cuda = torch.cuda.is_available() and a.device in ("auto", "cuda")
    dev = torch.device("cuda" if use_cuda else "cpu")
    amp = use_cuda and not a.no_amp
    info = {"variant": a.variant, "seed": a.seed, "args": vars(a), "host": platform.node(),
            "python": sys.version.split()[0], "torch": torch.__version__, "numpy": np.__version__,
            "pandas": pd.__version__, "cuda": torch.version.cuda, "device": str(dev), "amp_fp16": amp,
            "gpu": torch.cuda.get_device_name(0) if use_cuda else "none",
            "gpu_total_mem_gb": round(torch.cuda.get_device_properties(0).total_memory / 2**30, 2) if use_cuda else 0}
    try:
        info["nebula_commit_file"] = open(os.path.join(code, "nebula", "COMMIT")).read().strip()
    except OSError:
        pass
    log(f"== variant {a.variant} seed {a.seed} | gpu {a.gpu}: {info['gpu']} | torch {torch.__version__} "
        f"cuda {torch.version.cuda} | amp {amp} | python {info['python']} numpy {np.__version__} pandas {pd.__version__}")
    log(f"data {data} | code {code}")

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
    log("reports: " + ", ".join(f"{s}={len(v):,}" for s, v in idx.items()))
    Xg = torch.from_numpy(np.ascontiguousarray(X)).to(dev)          # int32, ~190 MB: whole array lives on the GPU
    yg = torch.from_numpy(y.astype(np.float32)).to(dev)

    def batch(ix):
        t = torch.from_numpy(ix).to(dev)
        return Xg[t].long(), yg[t]

    # ---------------------------------------------------------------- model, optimiser
    torch.manual_seed(a.seed)
    if use_cuda:
        torch.cuda.manual_seed_all(a.seed)
    model = build_variant(os.path.join(code, "nebula"), a.variant).to(dev)
    n_par = sum(p.numel() for p in model.parameters())
    log(f"model {a.variant}: {n_par:,} parameters; pooling={model.pooling_type}; fixed_pe={model.fixed_pe}")
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=a.weight_decay)
    sched = torch.optim.lr_scheduler.StepLR(opt, step_size=a.lr_step, gamma=0.5)       # stepped every batch
    scaler = torch.amp.GradScaler("cuda", enabled=amp)
    loss_fn = nn.BCEWithLogitsLoss()

    ck_dir = os.path.join(a.out, "ckpt", tag)
    os.makedirs(ck_dir, exist_ok=True)
    state = {"epoch": 0, "best": float("inf"), "best_epoch": 0, "bad": 0, "history": [], "done": False}
    for d in (ck_dir, os.path.join(a.resume_dir, "ckpt", tag) if a.resume_dir else None):
        p = os.path.join(d, "last.pt") if d else None
        if p and os.path.exists(p):
            ck = torch.load(p, map_location=dev, weights_only=False)
            model.load_state_dict(ck["model"]); opt.load_state_dict(ck["opt"])
            sched.load_state_dict(ck["sched"]); scaler.load_state_dict(ck["scaler"])
            state = ck["state"]
            torch.set_rng_state(ck["rng_cpu"].cpu())
            if use_cuda and ck.get("rng_cuda") is not None:
                torch.cuda.set_rng_state(ck["rng_cuda"].cpu())
            if d != ck_dir:                       # keep the resumed files where this run writes
                os.makedirs(ck_dir, exist_ok=True)
                if os.path.exists(os.path.join(d, "best.pt")):
                    torch.save(torch.load(os.path.join(d, "best.pt"), map_location="cpu"), os.path.join(ck_dir, "best.pt"))
            log(f"RESUMED from {p}: epoch {state['epoch']} done, best val loss {state['best']:.5f} (epoch {state['best_epoch']})")
            break

    def save(path, obj):
        torch.save(obj, path + ".tmp"); os.replace(path + ".tmp", path)

    @torch.no_grad()
    def predict(ix, bs=256):
        """fp32 inference, eval mode -> logits (float64)."""
        model.eval()
        out = np.zeros(len(ix))
        for i in range(0, len(ix), bs):
            xb, _ = batch(ix[i:i + bs])
            out[i:i + bs] = model(xb).squeeze(-1).float().double().cpu().numpy()
        return out

    def val_metrics():
        from sklearn.metrics import roc_auc_score
        z = predict(idx["val"])
        yy = y[idx["val"]]
        loss = float(loss_fn(torch.from_numpy(z), torch.from_numpy(yy.astype(np.float64))))
        return loss, float(roc_auc_score(yy, z))

    # ---------------------------------------------------------------- training
    steps_per_epoch = int(np.ceil(len(idx["train"]) / a.batch_size))
    log(f"batch {a.batch_size}, {steps_per_epoch} steps/epoch, lr {a.lr}, StepLR x0.5 every {a.lr_step} steps, "
        f"clip {a.clip}, max {a.epochs} epochs, patience {a.patience}")
    if use_cuda:
        torch.cuda.reset_peak_memory_stats()
    while state["epoch"] < a.epochs and state["bad"] < a.patience and not state["done"]:
        ep = state["epoch"] + 1
        t0 = time.time()
        model.train()
        order = np.random.RandomState(a.seed * 1000 + ep).permutation(idx["train"])     # same order for A, B and C
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
        if use_cuda:
            torch.cuda.synchronize()
        t_train = time.time() - t0
        t1 = time.time()
        vl, vauc = val_metrics()
        t_val = time.time() - t1
        better = vl < state["best"]
        if better:
            state.update(best=vl, best_epoch=ep, bad=0)
            save(os.path.join(ck_dir, "best.pt"), {k: v.detach().cpu() for k, v in model.state_dict().items()})
        else:
            state["bad"] += 1
        rec = {"epoch": ep, "train_loss": tot / n, "val_loss": vl, "val_auc": vauc, "train_s": round(t_train, 1),
               "val_s": round(t_val, 1), "epoch_s": round(time.time() - t0, 1), "lr_end": sched.get_last_lr()[0],
               "peak_gpu_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 3) if use_cuda else 0}
        state["history"].append(rec); state["epoch"] = ep
        log(f"epoch {ep}: train loss {rec['train_loss']:.5f} | val loss {vl:.5f} auc {vauc:.5f} | "
            f"train {t_train:.0f}s val {t_val:.1f}s | peak GPU mem {rec['peak_gpu_mem_gb']} GB"
            + (" | best" if better else f" | no improvement ({state['bad']}/{a.patience})"))
        save(os.path.join(ck_dir, "last.pt"),
             {"model": model.state_dict(), "opt": opt.state_dict(), "sched": sched.state_dict(),
              "scaler": scaler.state_dict(), "state": state, "rng_cpu": torch.get_rng_state(),
              "rng_cuda": torch.cuda.get_rng_state() if use_cuda else None})
        log(f"checkpoint saved: {ck_dir}/last.pt")

    stop = "early stop" if state["bad"] >= a.patience else ("max epochs" if state["epoch"] >= a.epochs else "done")
    log(f"training finished ({stop}); best epoch {state['best_epoch']} val loss {state['best']:.5f}")

    # ---------------------------------------------------------------- scores
    model.load_state_dict(torch.load(os.path.join(ck_dir, "best.pt"), map_location=dev))
    sc_dir = os.path.join(a.out, "scores")
    os.makedirs(sc_dir, exist_ok=True)
    for part, side in (("april", "test"), ("janval", "val")):
        ix = idx[side]
        z = predict(ix)
        df = pd.DataFrame({"row": ix, "seed": a.seed, "score": 1.0 / (1.0 + np.exp(-z)), "logit": z})
        df.to_parquet(os.path.join(sc_dir, f"pool_{a.variant}_seed{a.seed}_{part}.parquet"), index=False)
        from sklearn.metrics import roc_auc_score
        log(f"scored {part}: {len(ix):,} reports, AUC {roc_auc_score(y[ix], z):.5f}")

    info.update(history=state["history"], best_epoch=state["best_epoch"], best_val_loss=state["best"],
                stopped_by=stop, params=n_par,
                peak_gpu_mem_gb=max([h["peak_gpu_mem_gb"] for h in state["history"]] or [0]),
                mean_epoch_s=float(np.mean([h["epoch_s"] for h in state["history"]])) if state["history"] else None)
    try:
        info["nvidia_smi"] = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used", "--format=csv,noheader"],
            text=True, timeout=20).strip()
    except Exception:
        pass
    with open(os.path.join(a.out, "logs", f"{tag}.json"), "w") as fh:
        json.dump(info, fh, indent=1, default=str)
    log("done")


if __name__ == "__main__":
    main()
