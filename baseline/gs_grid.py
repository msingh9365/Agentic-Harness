"""
Kaggle job: the grid of Stage B (NOTES 21) on the group-split validation slice, 5 seeds, 4 epochs, every run in --loss-log mode (no April logit and no weights are produced).   (OURS; training = baseline/v2pe.py)

    python -m baseline.gs_grid --family v2pe   --out /kaggle/working/out      # 3 learning rates x seeds 0-4                     = 15 runs, flatten pooling, paper PE, no padding
    python -m baseline.gs_grid --family attbal --out /kaggle/working/out      # 2 learning rates x 2 padding probabilities x seeds 0-4 = 20 runs of 6 epochs, attention pooling, balanced padding
    python -m baseline.gs_grid --family attbal --dry-run                      # prints the 20 commands

All runs of the family go into one queue that the two GPUs of the kernel work off (the epochs 1 to 4 (v2-PE) or 1 to 6 (ATT+bal) of a cell are the epochs of ONE run: constant learning rate, no scheduler, so
epoch k of a 4-epoch run is the state of a k-epoch run). The commands are those of NOTES 21 Stage B. Output: <out>/<tag>/seed<k>.json (+ per-epoch validation logits) and <out>/loss_curves/<tag>/seed<k>.json.
"""
import argparse
import os
import subprocess
import sys
import time

from baseline.gs_select import AB_LRS, AB_PS, V2_LRS, tag_ab, tag_v2


def jobs_of(family, seeds, epochs, split_dir, variant, store):
    epochs = epochs or (6 if family == "attbal" else 4)          # owner's instruction (NOTES 21.5.1): ATT+bal 6 epochs, v2-PE 4
    base = ["--epochs", str(epochs), "--variant", variant, "--split-dir", split_dir, "--loss-log", "--pe-mode", "paper"]
    out = []
    for lr, p in ([(lr, None) for lr in V2_LRS] if family == "v2pe" else [(lr, p) for lr in AB_LRS for p in AB_PS]):
        tag = tag_v2(lr) if family == "v2pe" else tag_ab(lr, p)
        extra = ["--pooling", "flatten"] if family == "v2pe" else ["--pooling", "attn", "--pad-store", store, "--pad-mode", "replace", "--pad-labels", "all", "--pad-stream", "7000", "--pad-prob", str(p),
                                                                     "--val-robust", "--val-robust-k", "20", "100"]
        for s in seeds:
            out.append((tag, s, base + extra + ["--lr", str(lr), "--tag", tag, "--seed", str(s)]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True, choices=["v2pe", "attbal"])
    ap.add_argument("--out", default="/kaggle/working/out")
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    ap.add_argument("--epochs", type=int, default=0, help="default: 6 for attbal, 4 for v2pe")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--variant", default="bpe50k_gs")
    ap.add_argument("--pad-store", default="all_gs.npz")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test only")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    jobs = jobs_of(a.family, a.seeds, a.epochs, a.split_dir, a.variant, a.pad_store)
    extra = ["--device", a.device, "--out", a.out] + (["--limit", str(a.limit)] if a.limit else [])
    if a.dry_run:
        for tag, s, args in jobs:
            print("python -m baseline.v2pe " + " ".join(args + extra))
        print(len(jobs), "runs")
        return
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    n_gpu = min(n_gpu, a.gpus) if a.gpus else n_gpu
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    todo = [j for j in jobs if not os.path.exists(os.path.join(a.out, j[0], f"seed{j[1]}.json"))]
    running, t0, failed = {}, time.time(), []
    while todo or running:
        for g in range(n_gpu):
            if g not in running and todo:
                tag, s, args = todo.pop(0)
                log = open(os.path.join(a.out, "logs", f"{tag}_seed{s}.log"), "a")
                running[g] = (subprocess.Popen([sys.executable, "-m", "baseline.v2pe"] + args + extra, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"{tag} seed{s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {tag} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                    print("".join(open(log.name).readlines()[-6:])[-900:], flush=True)
                del running[g]
        time.sleep(5)
    print(f"all runs finished in {(time.time() - t0) / 60:.1f} min; failed: {failed}", flush=True)
    if failed:
        raise SystemExit(f"runs failed: {failed}")


if __name__ == "__main__":
    main()
