"""
Job 4 (GPU): malware type classification, paper Table 9 (arXiv v2; "Table 12b" in the journal numbering), experiment C.   (OURS: driver)

Eight classes (clean, backdoor, coinminer, dropper, keylogger, ransomware, rat, trojan), cross-entropy, the authors' ModelTrainer.
Reported: per-class F1 on the April test set, mean over the 3 fold models (time-matched 5 min per fold, and the batch-matched
detection counts), plus accuracy, macro-F1 and macro one-vs-rest AUC.
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
from baseline.detect import load_data


def run_one(a):
    tokens = a.tokens or C.find_dir_with("labels.npz")
    x, _, xt, _, splits, vocab = load_data(tokens, a.variant)
    lab = np.load(os.path.join(tokens, "labels.npz"))
    ym, ymt = lab["ym_train"].astype(np.int64), lab["ym_test"].astype(np.int64)
    tag = f"classify_{a.variant}_{a.regime}_seed{a.seed}"
    out = os.path.join(a.out, "classify", tag)
    nb = C.setup_nebula(require_patched=True)
    print(f"[{tag}] x {x.shape} classes {np.bincount(ym).tolist()} test {np.bincount(ymt).tolist()}", flush=True)
    res = cv.run_cv(x, ym, xt, ymt, splits["kfold3"], len(vocab), out, task="multiclass", regime=a.regime, time_budget=a.time_budget,
                    max_batches=cv.PAPER_BATCHES[a.variant] if a.regime == "batches" else None, device=a.device, seed=a.seed, tag=tag)
    res["nebula"], res["classes"] = nb, C.SPEAKEASY_CLASSES
    C.dump_json(res, os.path.join(out, "metrics.json"))
    f1 = res["test_f1_per_class_mean"]
    print(f"[{tag}] test per-class F1 (mean of folds): " + ", ".join(f"{c} {v:.3f}" for c, v in zip(C.SPEAKEASY_CLASSES, f1)), flush=True)


def orchestrate(a):
    import torch
    n_gpu = min(max(1, torch.cuda.device_count()), a.gpus or 99)
    queue = [["--variant", v, "--regime", r] for v in ["bpe50k", "ws50k"] for r in ["time", "batches"]]
    running, t0 = {}, time.time()
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while queue or running:
        for g in range(n_gpu):
            if g not in running and queue:
                j = queue.pop(0)
                name = "classify_" + "_".join(x.strip("-") for x in j)
                log = open(os.path.join(a.out, "logs", name + ".log"), "w")
                running[g] = (subprocess.Popen([sys.executable, "-m", "baseline.classify", "--out", a.out] + j,
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
    ap.add_argument("--variant", default="bpe50k", choices=["bpe50k", "ws50k"])
    ap.add_argument("--regime", default="time", choices=["time", "batches"])
    ap.add_argument("--time-budget", type=int, default=cv.PAPER["time_budget"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    return orchestrate(a) if a.plan else run_one(a)


if __name__ == "__main__":
    main()
