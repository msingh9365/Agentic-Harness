"""
Kaggle job (NOTES 28, epoch study; January data only, no April): per (model or cell, fold, seed) one run of up to 5 epochs with the per-epoch validation measures of NOTES 28.5.   (OURS; training = baseline/v2pe.py and baseline/twolevel.py in study mode)

    python -m baseline.epoch_study --units m1:9 m1:4 m3:9 m3:4 fn:9 an:9 fb:9 --seeds 0 1 2 3 4 --epochs 5 --out /kaggle/working/out
    python -m baseline.epoch_study --units m2:9 m2:4 --dry-run                      # prints the commands

Units: m1 (flatten, no padding, lr 2e-3), m3 (attention, balanced padding, lr 1e-3), m2 (two-level, no padding, scratch, lr 1e-3), m4 (two-level, balanced padding, scratch, lr 1e-3);
2 x 2 cells at lr 1e-3 on fold 9: fn (flatten, none), an (attention, none), fb (flatten, balanced); the fourth cell, attention + balanced (ab), is IDENTICAL to m3 on fold 9 (same settings, seeds, pool) and is taken from the m3:9 runs.
Output: <out>/es_<unit>_f<fold>/seed<k>.json (+ validation logits per epoch) and <out>/loss_curves/... ; no April file is written (checked by the report script).
"""
import argparse
import os
import subprocess
import sys
import time

UNITS = {  # unit: (script, extra arguments)
    "m1": ("v2pe", ["--pooling", "flatten", "--lr", "0.002"]),
    "m3": ("v2pe", ["--pooling", "attn", "--lr", "0.001", "--pad-store", "all.npz", "--pad-mode", "replace", "--pad-labels", "all", "--pad-stream", "7000", "--pad-prob", "0.5"]),
    "fn": ("v2pe", ["--pooling", "flatten", "--lr", "0.001"]),
    "an": ("v2pe", ["--pooling", "attn", "--lr", "0.001"]),
    "fb": ("v2pe", ["--pooling", "flatten", "--lr", "0.001", "--pad-store", "all.npz", "--pad-mode", "replace", "--pad-labels", "all", "--pad-stream", "7000", "--pad-prob", "0.5"]),
    "m2": ("twolevel", ["--padding", "none", "--init", "scratch", "--lr", "1e-3"]),
    "m4": ("twolevel", ["--padding", "balanced", "--init", "scratch", "--lr", "1e-3"]),
}


def jobs_of(units, seeds, epochs):
    out = []
    for u in units:
        name, fold = u.split(":")
        script, extra = UNITS[name]
        tag = f"es_{name}_f{fold}"
        if script == "v2pe":
            args = ["--epochs", str(epochs), "--variant", "bpe50k_fix", "--tokens-find", "all.npz", "--study-fold", fold, "--study-store", "all.npz", "--loss-log", "--pe-mode", "paper", "--tag", tag] + extra
        else:
            args = ["--epochs", str(epochs), "--variant", "bpe50k_fix", "--tokens-find", "all.npz", "--study-fold", fold, "--no-april", "--tag", tag, "--device", "cuda"] + extra
        for s in seeds:
            out.append((tag, s, script, args + ["--seed", str(s)]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", nargs="+", required=True, help="unit:fold, e.g. m1:9")
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--out", default="/kaggle/working/out")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--limit", type=int, default=0, help="smoke test only")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    for u in a.units:
        assert u.split(":")[0] in UNITS, u
    jobs = jobs_of(a.units, a.seeds, a.epochs)
    extra = ["--out", a.out] + (["--limit", str(a.limit)] if a.limit else [])
    if a.dry_run:
        for tag, s, script, args in jobs:
            print(f"python -m baseline.{script} " + " ".join(args + extra + (["--device", a.device] if script == "v2pe" else [])))
        print(len(jobs), "runs")
        return
    import torch
    n_gpu = max(1, torch.cuda.device_count())
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    todo = [j for j in jobs if not os.path.exists(os.path.join(a.out, j[0], f"seed{j[1]}.json"))]
    running, t0, failed = {}, time.time(), []
    while todo or running:
        for g in range(n_gpu):
            if g not in running and todo:
                tag, s, script, args = todo.pop(0)
                log = open(os.path.join(a.out, "logs", f"{tag}_seed{s}.log"), "a")
                cmd = [sys.executable, "-m", f"baseline.{script}"] + args + extra + (["--device", a.device] if script == "v2pe" else [])
                if script == "twolevel" and a.device != "cuda":
                    cmd[cmd.index("--device") + 1] = a.device
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"{tag} seed{s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {tag} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                    print("".join(open(log.name).readlines()[-8:])[-1200:], flush=True)
                    for q, _, _ in running.values():                      # fail fast (NOTES 28.8: a failed unit stops the work)
                        if q.poll() is None:
                            q.terminate()
                    raise SystemExit(f"runs failed: {failed}")
                del running[g]
        time.sleep(5)
    print(f"all runs finished in {(time.time() - t0) / 60:.1f} min; failed: {failed}", flush=True)


if __name__ == "__main__":
    main()
