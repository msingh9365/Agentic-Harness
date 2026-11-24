"""
Kernel job queue of the RoPE test (NOTES_ROPE.md): every job is the UNCHANGED command of an existing module run through `rope_test.launcher` with the variant model; the two GPUs of a kernel work off the queue.

    python -m rope_test.run_jobs --mode guard  --variants rope_blocks rope_full sin_full [--seeds 0 1 2] [--lr 0.001] --out /kaggle/working/out
    python -m rope_test.run_jobs --mode final  --variants rope_blocks --out ...      [--lr 0.001]       (10 seeds, all of January, April logits + weights after epoch 3: gs_grid.final_jobs(attbal, fix, 3 epochs))
    python -m rope_test.run_jobs --mode scores --out ...                              (Stage J padding-attack scores of V0 (m3) and V1..V3: baseline.gs_attack --mode scores)
    python -m rope_test.run_jobs --mode wb     --wb-jobs v1:0 v1:1 v1:2 v2:0 v2:1 v2:2 --out ...
Families of the attack modes: m3 = V0 (stored weights, `m3/seed<k>.pt`), v1 = rope_blocks, v2 = rope_full, v3 = sin_full (`v1/seed<k>.pt`, `seed<k>_april.npy`).
"""
import argparse
import os
import subprocess
import sys
import time

FAMKIND = {"v1": "rope_blocks", "v2": "rope_full", "v3": "sin_full"}
V2FAM = {v: k for k, v in FAMKIND.items()}


def guard_jobs(variants, seeds, lr, out):
    jobs = []
    for v in variants:
        tag = f"rg_{v}" + ("" if abs(lr - 1e-3) < 1e-12 else f"_lr{lr:g}")
        for s in seeds:
            args = ["--epochs", "3", "--variant", "bpe50k_fix", "--tokens-find", "all.npz", "--study-fold", "9", "--study-store", "all.npz", "--loss-log", "--pe-mode", "paper", "--tag", tag,
                    "--pooling", "attn", "--lr", str(lr), "--pad-store", "all.npz", "--pad-mode", "replace", "--pad-labels", "all", "--pad-stream", "7000", "--pad-prob", "0.5",
                    "--seed", str(s), "--out", out, "--device", "cuda"]
            jobs.append((tag, s, v, "baseline.v2pe", args))
    return jobs


def final_jobs(variants, seeds, lr, out):
    from baseline import gs_grid
    jobs = []
    for v in variants:
        tag = f"rf_{v}" + ("" if abs(lr - 1e-3) < 1e-12 else f"_lr{lr:g}")
        for s in seeds:
            t0, _, args = gs_grid.final_jobs("attbal", [s], "split", "bpe50k_gs", "all_gs.npz", fix=True, ep=3)[0]
            args = list(args)
            args[args.index("--tag") + 1] = tag
            args[args.index("--lr") + 1] = str(lr)
            assert "--april-epoch" in args and args[args.index("--april-epoch") + 1] == "3" and args[args.index("--epochs") + 1] == "3"
            jobs.append((tag, s, v, "baseline.v2pe", args + ["--out", out, "--device", "cuda"]))
    return jobs


def attack_jobs(mode, wb_jobs, out, search):
    extra = ["--extra-families"] + [f"{f}:{k}" for f, k in FAMKIND.items()]
    common = ["--out", out, "--device", "cuda", "--store", "all.npz", "--ranking", "ranking_gs.json", "--split-dir", "split", "--search", search]
    jobs = []
    if mode == "scores":
        for f in ["m3", "v1", "v2", "v3"]:
            jobs.append((f"scores_{f}", 0, FAMKIND.get(f), "baseline.gs_attack", ["--mode", "scores", "--family", f] + common + extra, os.path.join(out, f"scores_{f}.npz")))
    else:
        for j in wb_jobs:
            f, s = j.split(":")
            jobs.append((f"wb_{f}", int(s), FAMKIND.get(f), "baseline.gs_attack", ["--mode", "wb", "--family", f, "--seed", s, "--steps", "50", "--n-wb", "500"] + common + extra,
                         os.path.join(out, f"wb_{f}_seed{s}.npz")))
    return jobs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["guard", "final", "scores", "wb"])
    ap.add_argument("--variants", nargs="*", default=["rope_blocks", "rope_full", "sin_full"])
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--wb-jobs", nargs="*", default=[])
    ap.add_argument("--out", default="/kaggle/working/out")
    ap.add_argument("--search", default=os.environ.get("NEBULA_INPUT", "/kaggle/input"))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.mode == "guard":
        jobs = guard_jobs(a.variants, a.seeds or [0, 1, 2], a.lr, a.out)
    elif a.mode == "final":
        jobs = final_jobs(a.variants, a.seeds or list(range(10)), a.lr, a.out)
    else:
        jobs = attack_jobs(a.mode, a.wb_jobs, a.out, a.search)
    cmds = []
    for j in jobs:
        tag, s, v, module, args = j[:5]
        done = j[5] if len(j) > 5 else os.path.join(a.out, tag, f"seed{s}.json")
        cmds.append((tag, s, done, [sys.executable, "-m", "rope_test.launcher"] + (["--rope-variant", v] if (v and a.mode in ("guard", "final")) else []) + [module] + args))
    if a.dry_run:
        for tag, s, done, cmd in cmds:
            print(" ".join(cmd[2:]))
        print(len(cmds), "jobs")
        return
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    todo = [c for c in cmds if not os.path.exists(c[2])]
    running, t0, failed = {}, time.time(), []
    while todo or running:
        for g in range(n_gpu):
            if g not in running and todo:
                tag, s, done, cmd = todo.pop(0)
                log = open(os.path.join(a.out, "logs", f"{tag}_seed{s}.log"), "a")
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"{tag} seed{s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {tag} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                    print("".join(open(log.name).readlines()[-8:])[-1500:], flush=True)
                    for q, _, _ in running.values():                       # fail fast
                        if q.poll() is None:
                            q.terminate()
                    raise SystemExit(f"runs failed: {failed}")
                del running[g]
        time.sleep(5)
    print(f"all jobs finished in {(time.time() - t0) / 60:.1f} min; failed: {failed}", flush=True)


if __name__ == "__main__":
    main()
