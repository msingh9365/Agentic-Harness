"""
GPU smoke test: every GPU code path of the study with tiny budgets, on the real token arrays, before spending real quota.   (OURS)
Prints the GPU, the memory each step needed, and how long it took. Short budgets only; the numbers are NOT results.
"""
import argparse
import os
import subprocess
import sys
import time


def sh(cmd, env=None):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-12:])
    print(f"$ {' '.join(cmd[2:6])} ...  [exit {r.returncode}, {time.time() - t:.0f}s]\n{tail}\n", flush=True)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import torch
    print("torch", torch.__version__, "| cuda", torch.cuda.is_available(), "| devices", torch.cuda.device_count(),
          [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())], flush=True)
    py = sys.executable
    steps = [
        # detection: 20 s per fold instead of 300 s
        [py, "-m", "baseline.detect", "--out", a.out, "--variant", "bpe50k", "--regime", "time", "--time-budget", "20"],
        [py, "-m", "baseline.detect", "--out", a.out, "--variant", "ws50k", "--regime", "time", "--time-budget", "20"],
        [py, "-m", "baseline.detect", "--out", a.out, "--released"],
        [py, "-m", "baseline.classify", "--out", a.out, "--variant", "bpe50k", "--regime", "time", "--time-budget", "20"],
        # self-supervised: 3,000 unlabeled reports, one epoch each
        [py, "-m", "baseline.selfsup", "--out", a.out, "--unit", "mlm_theirs", "--limit", "3000", "--ft-epochs", "1", "--pt-epochs", "1"],
        [py, "-m", "baseline.selfsup", "--out", a.out, "--unit", "mlm_bert", "--limit", "3000", "--ft-epochs", "1", "--pt-epochs", "1"],
        [py, "-m", "baseline.selfsup", "--out", a.out, "--unit", "ar", "--limit", "3000", "--ft-epochs", "1", "--pt-epochs", "1"],
        [py, "-m", "baseline.selfsup", "--out", a.out, "--unit", "baselines", "--limit", "1500", "--ft-epochs", "1", "--pt-epochs", "1"],
    ]
    bad = 0
    for s in steps:
        bad += sh(s) != 0
        subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader"], check=False)
    print("smoke steps failed:", bad, flush=True)
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
