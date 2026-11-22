"""
Kaggle job (NOTES 26, items 3 and 4): training of the cells of the 2 x 2 (head x padding) and of the malware-only padding models, corrected tokenizer `bpe50k_fix`.   (OURS; training = baseline/v2pe.py)

    python -m baseline.gs_2x2 --mode grid  --cells fn ab an fb --out /kaggle/working/out                         # item 3 budget grid: group-split training part, seeds 0-4, 3 epochs, lr 1e-3 and 2e-3, --loss-log, NO April logit
    python -m baseline.gs_2x2 --mode final --cells fn ab an fb --lr 1e-3 --epochs 2 --out /kaggle/working/out      # item 3 final: all 75,298 January reports, seeds 0-9, April logits and weights after the last epoch only
    python -m baseline.gs_2x2 --mode final --cells y_fm y_am --out /kaggle/working/out                             # item 4: malware-only padding with the final M1 and M3 settings (lr / epochs default per cell)
    python -m baseline.gs_2x2 --mode grid --cells fn ab an fb --dry-run                                            # prints the commands

Cells: fn = flatten head, no padding (M1 type); ab = attention head, balanced padding p 0.5 (M3 type); an = attention head, no padding; fb = flatten head, balanced padding p 0.5;
y_fm = flatten head, malware-only padding (M1 settings: lr 2e-3, 1 epoch); y_am = attention head, malware-only padding (M3 settings: lr 1e-3, 3 epochs).
Padding (cells with padding): the in-memory replace-padding of NOTES 21 (pool = the 21,507 benign group-split training reports, stream 7000, p 0.5, k U{1..50}, insert / prepend 50/50). All other settings are those of v2pe.py.
Output: <out>/<tag>/seed<k>.json (+ val logits in grid mode, test logits and weights after the last epoch in final mode) and <out>/loss_curves/<tag>/seed<k>.json; tags x2g_<cell>_lr<lr> (grid), x2f_<cell> (item 3 final), x2m_<cell> (item 4).
"""
import argparse
import os
import subprocess
import sys
import time

CELLS = {  # name: (pooling, padded labels or None, default lr, default epochs)
    "fn": ("flatten", None, 2e-3, 1), "ab": ("attn", "all", 1e-3, 3), "an": ("attn", None, 1e-3, 3), "fb": ("flatten", "all", 2e-3, 1),
    "y_fm": ("flatten", "malware", 2e-3, 1), "y_am": ("attn", "malware", 1e-3, 3)}
GRID_LRS, GRID_EPOCHS, GRID_SEEDS = [1e-3, 2e-3], 3, [0, 1, 2, 3, 4]


def tag_of(mode, cell, lr):
    return f"x2g_{cell}_lr{lr:.0e}".replace("e-0", "e-") if mode == "grid" else (f"x2m_{cell}" if cell.startswith("y_") else f"x2f_{cell}")


def jobs_of(mode, cells, seeds, lr, epochs, split_dir, store):
    out = []
    for cell in cells:
        pooling, pad, dlr, dep = CELLS[cell]
        lrs = GRID_LRS if mode == "grid" else [lr if (lr and not cell.startswith("y_")) else dlr]
        ep = GRID_EPOCHS if mode == "grid" else (epochs if (epochs and not cell.startswith("y_")) else dep)
        for l in lrs:
            tag = tag_of(mode, cell, l)
            args = ["--epochs", str(ep), "--variant", "bpe50k_fix", "--split-dir", split_dir, "--loss-log", "--pe-mode", "paper", "--tokens-find", "all.npz", "--pooling", pooling, "--lr", str(l)]
            if pad:
                args += ["--pad-store", store, "--pad-mode", "replace", "--pad-labels", pad, "--pad-stream", "7000", "--pad-prob", "0.5"]
            if mode == "final":
                args += ["--full-january", "--april-epoch", str(ep)]
            for s in seeds:
                out.append((tag, s, args + ["--tag", tag, "--seed", str(s)]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["grid", "final"])
    ap.add_argument("--cells", nargs="+", required=True, choices=list(CELLS))
    ap.add_argument("--out", default="/kaggle/working/out")
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--lr", type=float, default=None, help="final mode, item 3 cells: the chosen learning rate")
    ap.add_argument("--epochs", type=int, default=None, help="final mode, item 3 cells: the chosen number of epochs")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--pad-store", default="all.npz")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test only")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    seeds = a.seeds if a.seeds is not None else (GRID_SEEDS if a.mode == "grid" else list(range(10)))
    if a.mode == "final" and any(not c.startswith("y_") for c in a.cells):
        assert a.lr and a.epochs, "item 3 final needs --lr and --epochs (the budget chosen by baseline/gs_select_2x2.py)"
    jobs = jobs_of(a.mode, a.cells, seeds, a.lr, a.epochs, a.split_dir, a.pad_store)
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
                    for q, _, _ in running.values():                      # fail fast (NOTES 26: a failed run stops the work)
                        if q.poll() is None:
                            q.terminate()
                    raise SystemExit(f"runs failed: {failed}")
                del running[g]
        time.sleep(5)
    print(f"all runs finished in {(time.time() - t0) / 60:.1f} min; failed: {failed}", flush=True)


if __name__ == "__main__":
    main()
