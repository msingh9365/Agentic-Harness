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


def final_jobs(family, seeds, split_dir, variant, store, stage_d=False, tok_old=False, full=False, full_loss=False, fix=False, p3=None):
    """Stage C (NOTES 21.10): the approved settings, seeds 0-9. ATT+bal lr 1e-3, p 0.5, epoch 3; v2-PE lr 2e-3, epoch 1. The runs continue past the chosen epoch (ATT+bal to 6, v2-PE to 4) only so that the
    loss curves can be shown; the April logits and the weights are stored ONLY after the chosen epoch (--april-epoch), so no April logit of another epoch exists. Epoch k of a run = a k-epoch run (constant lr)."""
    full_loss = full_loss or fix or bool(p3)                             # NOTES 25 (Stage I): the Step-5 loss-log runs (gsy_*) with the corrected tokenizer, tags gsz_*
    if family == "v2pe":
        tag, extra, epochs, ae = "gsf_v2pe", ["--pooling", "flatten", "--lr", "0.002"], 4, 1
    else:
        tag, extra, epochs, ae = "gsf_attbal", ["--pooling", "attn", "--pad-store", store, "--pad-mode", "replace", "--pad-labels", "all", "--pad-stream", "7000", "--pad-prob", "0.5", "--val-robust", "--val-robust-k", "20", "100", "--lr", "0.001"], 6, 3
    base = ["--epochs", str(epochs), "--variant", variant, "--split-dir", split_dir, "--loss-log", "--pe-mode", "paper"] + (["--april-every"] if stage_d else ["--april-epoch", str(ae)])
    if tok_old or full or full_loss:                         # Step 3b / Step 5 / Stage G loss-curve re-runs (NOTES 22.7): the OLD tokenizer (fit on all of January): its tokens and call store (nebula-tune-inputs) and the split (nebula-groupsplit); exactly the chosen number of epochs
        tag = tag.replace("gsf_", "gstk_" if tok_old else ("gsy_" if full_loss else "gsx_"))
        i = base.index("--variant")
        base[i + 1] = "bpe50k"
        base = [x for x in base if x != "--loss-log"] if (full and not full_loss) else base
        base = [x for x in base if x not in ("--epochs", str(epochs))] if False else base
        base[base.index("--epochs") + 1] = str(ae)
        base += ["--tokens-find", "all.npz"] + (["--full-january"] if (full or full_loss) else [])
        extra = [("all.npz" if x == "all_gs.npz" else x) for x in extra]
        if (full or full_loss) and "--val-robust" in extra:
            j = extra.index("--val-robust")
            extra = extra[:j] + extra[j + 4:]                # no validation measures in Step 5 (in-sample): drop "--val-robust --val-robust-k 20 100"
    if stage_d:                                              # Stage D (NOTES 21.13): the same runs as Stage C (same seeds, settings, epochs) in new tags; the April logits of every epoch are stored
        tag = tag.replace("gsf_", "gsd_")
        extra = [x for x in extra]
    if fix:
        tag = tag.replace("gsy_", "gsz_")
        base[base.index("--variant") + 1] = "bpe50k_fix"
    if p3:                                                   # NOTES 27 Part 2 (P3): the Step-5 settings with the role-normalised (gsr_) or control (gsa_) tokenizer, unknown pieces -> id 50,000
        tag = tag.replace("gsy_", "gsr_" if p3 == "role" else "gsa_")
        base[base.index("--variant") + 1] = "bpe50k_" + p3
    return [(tag, s, base + extra + ["--tag", tag, "--seed", str(s)]) for s in seeds]


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
    ap.add_argument("--tok-old", action="store_true", help="Step 3b: the Stage C runs with the OLD tokenizer (tags gstk_*), exactly the chosen epochs")
    ap.add_argument("--full-january", action="store_true", help="Step 5: train on all 75,298 January reports with the old tokenizer (tags gsx_*), exactly the chosen epochs; the padding pool stays the group-split training part")
    ap.add_argument("--full-loss", action="store_true", help="Stage G: the Step-5 runs again with --loss-log (tags gsy_*), exactly the chosen epochs, April logits after the last epoch (determinism check against Step 5)")
    ap.add_argument("--fix", action="store_true", help="NOTES 25 Stage I: the Step-5 settings with the corrected tokenizer bpe50k_fix (tags gsz_*), all of January, loss logs, April logits after the last epoch")
    ap.add_argument("--p3", choices=["role", "addr"], default=None, help="NOTES 27 P3: the Step-5 settings with the role-normalised (bpe50k_role, tags gsr_*) or control (bpe50k_addr, tags gsa_*) tokenizer, all of January, loss logs, April logits after the last epoch")
    ap.add_argument("--stage-d", action="store_true", help="Stage D: the Stage C runs again (tags gsd_*) with the April logits of every epoch stored (logits only)")
    ap.add_argument("--final", action="store_true", help="Stage C: the approved settings with seeds 0-9 (default seeds then 0-9), April logits after the chosen epoch only")
    a = ap.parse_args()
    if a.final or a.stage_d or a.tok_old or a.full_january or a.full_loss or a.fix or a.p3:
        jobs = final_jobs(a.family, a.seeds if a.seeds != [0, 1, 2, 3, 4] else list(range(10)), a.split_dir, a.variant, a.pad_store, stage_d=a.stage_d, tok_old=a.tok_old, full=a.full_january, full_loss=a.full_loss, fix=a.fix, p3=a.p3)
    else:
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
