"""
Job 2 (GPU): malware detection, paper Table 7 (experiment A) and the sanity check on the released models (E).   (OURS: driver)

  python -m baseline.detect --plan main --out /kaggle/working/out          # all runs, one subprocess per GPU
  python -m baseline.detect --variant bpe50k --regime batches --out DIR    # one run
  python -m baseline.detect --released --out DIR                           # released models on our April test set

Training and the model are the authors' (ModelTrainer, TransformerEncoderChunks); see baseline/cv.py.
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

RELEASED = {"released_bpe50k": "bpe_50000_torch.model", "released_ws50k": "whitespace_50000_torch.model"}
MAIN_PLAN = [("bpe50k", "time"), ("ws50k", "time"), ("bpe50k", "batches"), ("ws50k", "batches")]


def load_data(tokens, variant):
    lab = np.load(os.path.join(tokens, "labels.npz"))
    splits = json.load(open(os.path.join(tokens, "splits.json")))
    vdir = os.path.join(tokens, "variants", variant)
    x, xt = np.load(os.path.join(vdir, "x_train.npy")), np.load(os.path.join(vdir, "x_test.npy"))
    vocab = json.load(open(os.path.join(vdir, "vocab.json")))
    return x, lab["y_train"], xt, lab["y_test"], splits, vocab


def run_one(a):
    tokens = a.tokens or C.find_dir_with("labels.npz")
    x, y, xt, yt, splits, vocab = load_data(tokens, a.variant)
    tag = f"{a.variant}_{a.regime}_seed{a.seed}"
    out = os.path.join(a.out, "detect", tag)
    nb = C.setup_nebula(require_patched=True)
    print(f"[{tag}] x {x.shape} test {xt.shape} vocab {len(vocab)} malware share train {y.mean():.3f} test {yt.mean():.3f} | {C.env_info()}", flush=True)
    res = cv.run_cv(x, y, xt, yt, splits["kfold3"], len(vocab), out, task="binary", regime=a.regime,
                    time_budget=a.time_budget, max_batches=cv.PAPER_BATCHES[a.variant] if a.regime == "batches" else None,
                    device=a.device, seed=a.seed, tag=tag)
    res["nebula"] = nb
    C.dump_json(res, os.path.join(out, "metrics.json"))
    t = res["test_mean_std"]
    print(f"[{tag}] TEST mean over folds: TPR@1e-3 {t['tpr@0.001']['mean']:.4f} | AUC {t['auc']['mean']:.4f} | F1@0.5 "
          f"{t['f1@0.5']['mean']:.4f} | Acc {t['acc@0.5']['mean']:.4f}", flush=True)


def run_released(a):
    """E: evaluate the authors' released weights on OUR April test set (and on our January set, which they may have seen)."""
    import torch
    from nebula.models.attention import TransformerEncoderChunks
    nb = C.setup_nebula(require_patched=True)
    tokens = a.tokens or C.find_dir_with("labels.npz")
    out = os.path.join(a.out, "released")
    os.makedirs(out, exist_ok=True)
    allres = {"nebula": nb, "env": C.env_info()}
    for variant, fname in RELEASED.items():
        x, y, xt, yt, splits, vocab = load_data(tokens, variant)
        model = TransformerEncoderChunks(**cv.model_config(len(vocab)))
        model.load_state_dict(torch.load(os.path.join(nb["nebula_root"], "nebula", "objects", fname), weights_only=True))
        trainer = cv.make_trainer(model, a.device, "binary", 96, 2.5e-4, 1e-2)
        pt = cv.predict(trainer, xt)
        ptr = cv.predict(trainer, x)
        allres[variant] = {"test": C.binary_metrics(yt, pt), "train_in_sample": C.binary_metrics(y, ptr)}
        np.save(os.path.join(out, f"{variant}_test_probs.npy"), pt.astype(np.float32))
        t = allres[variant]["test"]
        print(f"[{variant}] released weights on our April test set: TPR@1e-3 {t['tpr@0.001']:.4f} AUC {t['auc']:.4f} "
              f"F1@0.5 {t['f1@0.5']:.4f} Acc {t['acc@0.5']:.4f} | on January train: AUC {allres[variant]['train_in_sample']['auc']:.4f}", flush=True)
    C.dump_json(allres, os.path.join(out, "metrics.json"))


def orchestrate(a):
    """Run the plan with one subprocess per GPU (a T4 x2 session has two)."""
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    n_gpu = min(n_gpu, a.gpus) if a.gpus else n_gpu
    jobs = [["--variant", v, "--regime", r, "--seed", str(s)] for s in a.seeds for v, r in MAIN_PLAN] + [["--released"]]
    running, queue, t0 = {}, list(jobs), time.time()
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while queue or running:
        for g in range(n_gpu):
            if g not in running and queue:
                j = queue.pop(0)
                name = "_".join(x.strip("-") for x in j)
                log = open(os.path.join(a.out, "logs", f"{name}.log"), "w")
                env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))
                cmd = [sys.executable, "-m", "baseline.detect", "--out", a.out, "--device", "cuda"] + j
                running[g] = (subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT), name, log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {name}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                print("".join(open(os.path.join(a.out, "logs", f"{name}.log")).readlines()[-6:]), flush=True)
                del running[g]
        time.sleep(5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", default=None, choices=[None, "main"])
    ap.add_argument("--variant", default="bpe50k", choices=["bpe50k", "ws50k"])
    ap.add_argument("--regime", default="time", choices=["time", "batches"])
    ap.add_argument("--released", action="store_true")
    ap.add_argument("--time-budget", type=int, default=cv.PAPER["time_budget"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0])
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    if a.plan:
        return orchestrate(a)
    return run_released(a) if a.released else run_one(a)


if __name__ == "__main__":
    main()
