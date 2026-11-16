"""
Job 5 (GPU, lowest priority): ablations, paper Table 4 (vocabulary size), Fig. 3c (sequence length), Table 6 (tokenizer), experiment D.
(OURS: driver). Every configuration is a 3-fold CV with the time-matched regime (5 min per fold) and batch 96, like detection.

Needs the token arrays written by `preprocess --variants bpe5k,bpe10k,bpe30k,bpe70k,wp50k` and `--seq-lens 64,128,256,1024,2048`.
The raw-JSON ablation (Table 5, raw vs filtered) is not run here: see NOTES.md.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import common as C
from baseline import cv

CONFIGS = ([(f"bpe{k}k", 512) for k in (5, 10, 30, 70)] + [("bpe50k", n) for n in (64, 128, 256, 1024, 2048)] + [("wp50k", 512)])


def run_one(a):
    tokens = a.tokens or C.find_dir_with("labels.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    splits = json.load(open(os.path.join(tokens, "splits.json")))
    vdir = os.path.join(tokens, "variants", a.variant)
    sfx = "" if a.seq_len == 512 else f"_len{a.seq_len}"
    x, xt = np.load(os.path.join(vdir, f"x_train{sfx}.npy")), np.load(os.path.join(vdir, f"x_test{sfx}.npy"))
    vocab = json.load(open(os.path.join(vdir, "vocab.json")))
    tag = f"{a.variant}_len{a.seq_len}_seed{a.seed}"
    nb = C.setup_nebula(require_patched=True)
    res = cv.run_cv(x, lab["y_train"], xt, lab["y_test"], splits["kfold3"], len(vocab), os.path.join(a.out, "ablate", tag), task="binary",
                    regime="time", time_budget=a.time_budget, device=a.device, seed=a.seed, maxlen=a.seq_len, tag=tag)
    res["nebula"], res["variant"], res["seq_len"] = nb, a.variant, a.seq_len
    C.dump_json(res, os.path.join(a.out, "ablate", tag, "metrics.json"))


def orchestrate(a):
    import torch
    n_gpu = min(max(1, torch.cuda.device_count()), a.gpus or 99)
    queue = [["--variant", v, "--seq-len", str(n)] for v, n in CONFIGS]
    running, t0 = {}, time.time()
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while queue or running:
        for g in range(n_gpu):
            if g not in running and queue:
                j = queue.pop(0)
                name = "ablate_" + "_".join(x.strip("-") for x in j)
                log = open(os.path.join(a.out, "logs", name + ".log"), "w")
                running[g] = (subprocess.Popen([sys.executable, "-m", "baseline.ablate", "--out", a.out] + j,
                                               env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), name, log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {name}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                print("".join(open(os.path.join(a.out, "logs", name + ".log")).readlines()[-3:]), flush=True)
                del running[g]
        time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", default=None, choices=[None, "main"])
    ap.add_argument("--variant", default="bpe50k")
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--time-budget", type=int, default=cv.PAPER["time_budget"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    return orchestrate(a) if a.plan else run_one(a)


if __name__ == "__main__":
    main()
