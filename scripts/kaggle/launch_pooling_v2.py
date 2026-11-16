#!/usr/bin/env python
"""
Run several train_pooling_v2.py jobs on a "GPU T4 x2" Kaggle session: one run per GPU at a time.

    python launch_pooling_v2.py --jobs A:0,B:0,A:0:tag=_steps3000:steps=3000 [--gpus 0,1] [-- <extra train args>]

Job = VARIANT:SEED[:key=value...] with VARIANT in A, B, C, B0, C0 and keys
    tag=<suffix of the run name>   steps=<max optimiser steps>   epochs=<n>   all=1 (train on all of January)

Each GPU has a worker that takes the next job from a shared queue, so two runs are always active
(CUDA_VISIBLE_DEVICES=0 and =1, plus --gpu K). A failed job does not stop the others; the exit code is
non-zero if any failed. GPU memory (nvidia-smi, whole process incl. CUDA context) is sampled every 15 s
into <out>/logs/gpu_mem.json. Extra arguments after "--" go to train_pooling_v2.py.

If a previous kernel's output is attached as an input (--resume-dir, or found under /kaggle/input),
finished jobs are copied over and skipped, and unfinished ones resume from their last checkpoint.
"""
import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def finished(out, run):
    return (os.path.exists(os.path.join(out, "logs", f"{run}.json"))
            and os.path.exists(os.path.join(out, "scores", f"{run}_epochs.npz")))


def adopt_previous(prev, out, run):
    """Copy a finished job's files from a previous kernel's output into this one."""
    if not prev or not finished(prev, run):
        return False
    for sub in ("logs", "scores", "ckpt"):
        src = os.path.join(prev, sub)
        if not os.path.isdir(src):
            continue
        os.makedirs(os.path.join(out, sub), exist_ok=True)
        for f in os.listdir(src):
            if f.startswith(run):
                s, d = os.path.join(src, f), os.path.join(out, sub, f)
                shutil.copytree(s, d, dirs_exist_ok=True) if os.path.isdir(s) else shutil.copy2(s, d)
    return True


def gpu_monitor(out, stop, gpus):
    peak = {g: 0 for g in gpus}
    path = os.path.join(out, "logs", "gpu_mem.json")
    while not stop.is_set():
        try:
            txt = subprocess.check_output(["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu",
                                           "--format=csv,noheader,nounits"], text=True, timeout=20)
            for line in txt.strip().splitlines():
                i, used, total, util = [int(x) for x in line.split(",")]
                peak[i] = max(peak.get(i, 0), used)
                peak[f"total_{i}"] = total
                peak[f"util_last_{i}"] = util
            with open(path, "w") as fh:
                json.dump({"peak_used_mib": peak, "t": time.strftime("%H:%M:%S")}, fh)
        except Exception:
            pass
        stop.wait(15)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", required=True, help="comma list VARIANT:SEED, e.g. A:0,B:0")
    ap.add_argument("--gpus", default="0,1")
    ap.add_argument("--out", default="/kaggle/working")
    ap.add_argument("--resume-dir", default=None)
    ap.add_argument("rest", nargs="*", help="arguments for train_pooling_v2.py (put them after --)")
    a, extra = ap.parse_known_args()
    extra = extra + a.rest
    extra = [x for x in extra if x != "--"]
    gpus = [int(g) for g in a.gpus.split(",")]
    jobs = []
    for j in a.jobs.split(","):
        p = j.split(":")
        kv = dict(x.split("=", 1) for x in p[2:])
        run = f"{p[0]}{kv.get('tag', '')}_s{int(p[1])}"
        jobs.append((p[0], int(p[1]), kv, run))
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)

    prev = a.resume_dir
    if prev is None and os.path.isdir("/kaggle/input"):
        for dp, dn, _ in os.walk("/kaggle/input"):
            if "ckpt" in dn and "scores" in dn:
                prev = dp
                break
            if dp.count(os.sep) > 6:
                dn[:] = []
    print(f"launcher: jobs {jobs} on GPUs {gpus}; out {a.out}; previous output {prev}; extra args {extra}", flush=True)
    try:
        print(subprocess.check_output(["nvidia-smi"], text=True), flush=True)
    except Exception as e:
        print("nvidia-smi unavailable:", e, flush=True)

    q = queue.Queue()
    for j in jobs:
        q.put(j)
    print("jobs:", [j[3] for j in jobs], flush=True)
    results, lock = {}, threading.Lock()
    stop = threading.Event()
    threading.Thread(target=gpu_monitor, args=(a.out, stop, gpus), daemon=True).start()
    t_start = time.time()

    def worker(gpu):
        while True:
            try:
                variant, seed, kv, tag = q.get_nowait()
            except queue.Empty:
                return
            if finished(a.out, tag) or adopt_previous(prev, a.out, tag):
                print(f"[{tag}] already finished, skipping", flush=True)
                with lock:
                    results[tag] = 0
                continue
            cmd = [sys.executable, os.path.join(HERE, "train_pooling_v2.py"), "--variant", variant, "--seed", str(seed),
                   "--gpu", str(gpu), "--out", a.out] + extra
            if "tag" in kv: cmd += ["--tag", kv["tag"]]
            if "steps" in kv: cmd += ["--max-steps", kv["steps"]]
            if "epochs" in kv: cmd += ["--epochs", kv["epochs"]]
            if kv.get("all") == "1": cmd += ["--include-val"]
            if prev:
                cmd += ["--resume-dir", prev]
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), PYTHONUNBUFFERED="1")
            t0 = time.time()
            print(f"[{tag}] start on GPU {gpu}: {' '.join(cmd[2:])}", flush=True)
            p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in p.stdout:
                print(f"[{tag} gpu{gpu}] {line.rstrip()}", flush=True)
            rc = p.wait()
            print(f"[{tag}] exit {rc} after {(time.time() - t0) / 60:.1f} min", flush=True)
            with lock:
                results[tag] = rc

    threads = [threading.Thread(target=worker, args=(g,)) for g in gpus]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stop.set()
    mem = {}
    try:
        mem = json.load(open(os.path.join(a.out, "logs", "gpu_mem.json")))
    except Exception:
        pass
    summary = {"jobs": {r: results.get(r) for _, _, _, r in jobs},
               "wall_min": round((time.time() - t_start) / 60, 1), "gpu_mem": mem}
    for _, _, _, r in jobs:
        p = os.path.join(a.out, "logs", f"{r}.json")
        if os.path.exists(p):
            j = json.load(open(p))
            summary[r] = {k: j.get(k) for k in ("gpu", "epoch_by_val_auc", "epoch_by_val_tpr1", "steps", "mean_epoch_s",
                                                "peak_gpu_mem_gb")}
    json.dump(summary, open(os.path.join(a.out, "logs", "summary.json"), "w"), indent=1)
    print("SUMMARY", json.dumps(summary, indent=1), flush=True)
    sys.exit(1 if any(rc != 0 for rc in results.values()) else 0)


if __name__ == "__main__":
    main()
