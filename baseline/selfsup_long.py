"""
Follow-up to experiment B: LONGER self-supervised pre-training (up to 15 epochs, early stopping).   (OURS: driver)

Same data, same stratified 80/20 split per seed (asserted against baseline/ssl_split_hashes.json), same fine-tuning
(10 epochs on the labeled 20%, AdamW lr 2.5e-4, batch 96, final weights, nothing selected on the April test set) as baseline/selfsup.py,
whose functions it calls. Only the pre-training length changes. Upper bound, lower bound and the full-attention controls are NOT
re-run: results/B_selfsup/ has them for the same seeds, splits and fine-tuning budget.

Units (per seed), outputs in <out>/ssl_long/seed<k>/:
  ar_long          AR pre-training (full 512 attention, causal) up to --pt-epochs, early stop (patience --pt-patience, min delta --min-delta),
                   encoder checkpoints at epochs 3, 6, 10 (--save-epochs) and the best epoch; the last-non-pad-token classifier is
                   fine-tuned from each of them -> runs ar_lasttoken_ep<k>
  mlm_bert_long    per-position BERT MLM (ours), fine-tuned from the best epoch -> mlm_bert_best
  mlm_theirs_long  the authors' multi-hot MLM, fine-tuned from the best epoch -> mlm_theirs_best
  lasttoken_control  EXTRA control, no pre-training: the same causal last-non-pad-token classifier fine-tuned on the labeled 20% from scratch
                   -> lower_lasttoken (the architecture-matched lower bound of ar_lasttoken_*)
  ar_flatten_long  AR flatten classifier, fine-tuned from the best AR checkpoint of ar_long (run ar_long first) -> ar_flatten_best

The RNG order of the first run is kept (set_seed, build the downstream model, pre-train; set_seed, build, transfer, fine-tune), so epoch 3
of a long run is the same procedure as the 3-epoch run.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

from baseline import common as C
from baseline import lm, selfsup

HERE = os.path.dirname(os.path.abspath(__file__))
UNITS = {"lasttoken_control": 5, "ar_long": 4, "mlm_bert_long": 2, "mlm_theirs_long": 1, "ar_flatten_long": 0}      # value = scheduling priority (higher first)
RUN_COST_MIN = {"lasttoken_control": 4, "ar_long": 45, "mlm_bert_long": 27, "mlm_theirs_long": 16, "ar_flatten_long": 5}
DONE = "unit_done.json"


def split_hash(sp):
    h = hashlib.sha256()
    for part in ("unlabeled", "labeled"):
        h.update(np.asarray(sp[part], dtype=np.int64).tobytes())
    return h.hexdigest()[:32]


def assert_same_split(sp, seed, hashes_path=os.path.join(HERE, "ssl_split_hashes.json")):
    """The split of this follow-up must be the split of the first run: compare with the hashes recorded from the published splits.json."""
    ref = json.load(open(hashes_path))["seeds"][str(seed)]
    got = {"sha256": split_hash(sp), "n_unlabeled": len(sp["unlabeled"]), "n_labeled": len(sp["labeled"])}
    assert got == ref, f"seed {seed}: split differs from the first run: {got} vs {ref}"
    return got


def init_from_checkpoint(model, ckpt_path):
    """Load a pre-training checkpoint (a state dict) into a downstream model and PROVE it: the encoder checksum of the
    downstream model must equal the checkpoint's, and must have differed before. Returns the proof dict."""
    import torch
    pre = torch.load(ckpt_path, map_location="cpu", weights_only=True)
    before = {"abs_sum": lm.checksum(model)["abs_sum"], "dist_to_pretrained": lm.distance(model.state_dict(), pre)}
    copied = lm.transfer(pre, model)
    after = {"abs_sum": lm.checksum(model)["abs_sum"], "dist_to_pretrained": lm.distance(model.state_dict(), pre)}
    proof = {"checkpoint": os.path.basename(ckpt_path), "tensors_copied": len(copied), "checksum_pretrained": lm.checksum(pre),
             "checksum_downstream_after": lm.checksum(model), "before_loading": before, "after_loading": after}
    assert proof["checksum_pretrained"]["sha256"] == proof["checksum_downstream_after"]["sha256"], "downstream encoder is not the checkpoint"
    assert after["dist_to_pretrained"] < 1e-6 < before["dist_to_pretrained"]
    return proof


def pretrain_cached(kind, x_unl, vocab, a, seed, out):
    """Pre-train (or load the cache). Returns (best state dict, history). AR keeps the full state (with its LM head); the MLM heads are
    huge, so only the encoder is kept for them (as in the first run). Per-epoch checkpoints for AR: <out>/ckpt_ar/epoch<k>.pt."""
    import torch
    cache, hist_path = os.path.join(out, f"pretrained_{kind}_long.pt"), os.path.join(out, f"pretrain_{kind}_long.json")
    if os.path.exists(cache) and os.path.exists(hist_path):
        return torch.load(cache, weights_only=True), json.load(open(hist_path))
    a.ckpt_dir = os.path.join(out, "ckpt_ar") if kind == "ar" else None
    a.save_epochs = tuple(a.save_epochs_list) if kind == "ar" else ()
    C.set_seed(seed)
    selfsup.downstream_model("ar_flatten" if kind == "ar" else f"{kind}", len(vocab))      # the first run built this model first (RNG order)
    pre, hist = selfsup.pretrain(kind, x_unl, vocab, a, seed, f"pre_{kind}_long_seed{seed}")
    shutil.rmtree(os.path.join(selfsup.LIT_DIR, f"pre_{kind}_long_seed{seed}"), ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    torch.save(lm.encoder_state(pre) if kind != "ar" else pre, cache)
    C.dump_json(hist, hist_path)
    return (lm.encoder_state(pre) if kind != "ar" else pre), hist


def finetune_from(run, ckpt_path, x, y, xt, yt, V, a, seed, out, extra_info):
    """Fine-tune `run`'s downstream model from a checkpoint and evaluate it once on the April test set."""
    import torch
    run_dir = os.path.join(out, run)
    if os.path.exists(os.path.join(run_dir, "metrics.json")):
        print(f"  [{run}] already done", flush=True)
        return
    C.set_seed(seed)
    model = selfsup.downstream_model(run.split("_ep")[0].split("_best")[0], V)
    proof = init_from_checkpoint(model, ckpt_path)
    print(f"  [{run}] fine-tuning starts from {proof['checkpoint']}: encoder checksum {proof['checksum_downstream_after']['sha256']} "
          f"(distance to the checkpoint {proof['before_loading']['dist_to_pretrained']:.3f} -> {proof['after_loading']['dist_to_pretrained']:.1e})", flush=True)
    w, secs, steps = selfsup.finetune(model, x, y, f"{run}_seed{seed}", a, seed)
    extra = {"run": run, "seed": seed, "ft_epochs": a.ft_epochs, "batch_size": a.batch_size, "lr": a.lr, "env": C.env_info(),
             "train_seconds": secs, "finetune_steps": steps, "n_finetune": int(len(x)), "weight_proof": proof, **extra_info}
    selfsup.evaluate_and_save(w, model, xt, yt, run_dir, extra, save_model=False)
    del w, model
    shutil.rmtree(os.path.join(selfsup.LIT_DIR, f"{run}_seed{seed}"), ignore_errors=True)       # Lightning scratch (checkpoints, logs)
    if a.device != "cpu":
        torch.cuda.empty_cache()


def checkpoint_epochs(hist, ckpt_dir, wanted):
    """Epochs to fine-tune from: those of `wanted` that were reached (and saved), plus the best epoch. {epoch: path}, best flagged."""
    run = len(hist["epochs"])
    eps = sorted({e for e in wanted if e <= run} | {hist["best_epoch"]})
    return eps


def run_unit(a):
    import torch
    nb = C.setup_nebula(require_patched=True)
    tokens = a.tokens or C.find_dir_with("labels.npz")
    x, y, xt, yt, vocab, splits = selfsup.load(tokens)
    V = len(vocab)
    sp = splits["ssl_80_20_stratified_by_family"][str(a.seed)]
    split_info = None if a.limit else assert_same_split(sp, a.seed)
    unl, lab = np.asarray(sp["unlabeled"]), np.asarray(sp["labeled"])
    if a.limit:
        r = np.random.default_rng(0)
        unl, lab = r.permutation(unl)[:a.limit], r.permutation(lab)[:max(8, a.limit // 4)]
        keep = r.permutation(len(xt))[:300]                          # smoke tests only: a small test subset
        xt, yt = xt[keep], yt[keep]
    out = os.path.join(a.out, "ssl_long", f"seed{a.seed}")
    os.makedirs(out, exist_ok=True)
    a.save_epochs_list = [int(e) for e in str(a.save_epochs).split(",") if e]
    print(f"[seed {a.seed}/{a.unit}] vocab {V} | unlabeled {len(unl)} labeled {len(lab)} test {len(xt)} | split hash {split_info} | {C.env_info()}", flush=True)
    base = {"pt_max_epochs": a.pt_epochs, "pt_patience": a.pt_patience, "min_delta": a.min_delta, "n_labeled": int(len(lab)),
            "n_unlabeled": int(len(unl)), "split": split_info, "nebula": nb}
    xl, yl = x[lab], y[lab]
    ckpt_dir = os.path.join(out, "ckpt_ar")
    if a.unit == "ar_long":
        pre, hist = pretrain_cached("ar", x[unl], vocab, a, a.seed, out)
        best = hist["best_epoch"]
        print(f"  [ar] pre-training ran {len(hist['epochs'])} epochs, best epoch {best}, stopped early: {hist['stopped_early']}", flush=True)
        best_path = os.path.join(out, "pretrained_ar_long.pt")
        for k in checkpoint_epochs(hist, ckpt_dir, a.save_epochs_list):
            path = os.path.join(ckpt_dir, f"epoch{k}.pt") if k in a.save_epochs_list else best_path
            if k == best:
                path = best_path                                   # best weights (equal to epoch<k>.pt when k was saved)
            finetune_from(f"ar_lasttoken_ep{k}", path, xl, yl, xt, yt, V, a, a.seed, out,
                          {**base, "pretrain_kind": "ar", "pretrain_epoch": k, "is_best": k == best, "pretraining": hist})
    elif a.unit in ("mlm_bert_long", "mlm_theirs_long"):
        kind = a.unit.replace("_long", "")
        pre, hist = pretrain_cached(kind, x[unl], vocab, a, a.seed, out)
        print(f"  [{kind}] pre-training ran {len(hist['epochs'])} epochs, best epoch {hist['best_epoch']}, stopped early: {hist['stopped_early']}", flush=True)
        finetune_from(f"{kind}_best", os.path.join(out, f"pretrained_{kind}_long.pt"), xl, yl, xt, yt, V, a, a.seed, out,
                      {**base, "pretrain_kind": kind, "pretrain_epoch": hist["best_epoch"], "is_best": True, "pretraining": hist})
    elif a.unit == "lasttoken_control":
        run_dir = os.path.join(out, "lower_lasttoken")
        if not os.path.exists(os.path.join(run_dir, "metrics.json")):
            C.set_seed(a.seed)
            model = selfsup.downstream_model("ar_lasttoken", V)               # same constructor and RNG order as ar_lasttoken_*, no checkpoint
            w, secs, steps = selfsup.finetune(model, xl, yl, f"lower_lasttoken_seed{a.seed}", a, a.seed)
            extra = {"run": "lower_lasttoken", "seed": a.seed, "ft_epochs": a.ft_epochs, "batch_size": a.batch_size, "lr": a.lr, "env": C.env_info(),
                     "train_seconds": secs, "finetune_steps": steps, "n_finetune": int(len(xl)), "weight_proof": {}, **base}
            selfsup.evaluate_and_save(w, model, xt, yt, run_dir, extra, save_model=False)
            shutil.rmtree(os.path.join(selfsup.LIT_DIR, f"lower_lasttoken_seed{a.seed}"), ignore_errors=True)
    elif a.unit == "ar_flatten_long":
        hist = json.load(open(os.path.join(out, "pretrain_ar_long.json")))
        finetune_from("ar_flatten_best", os.path.join(out, "pretrained_ar_long.pt"), xl, yl, xt, yt, V, a, a.seed, out,
                      {**base, "pretrain_kind": "ar", "pretrain_epoch": hist["best_epoch"], "is_best": True, "pretraining": hist})
    C.dump_json({"unit": a.unit, "seed": a.seed, "finished": time.strftime("%Y-%m-%d %H:%M:%S")}, os.path.join(out, f"{a.unit}_{DONE}"))


def import_from(root, out):
    """Copy the AR pre-training results (best encoder + history) of an earlier kernel (attached with kernel_sources) into <out>,
    so that ar_flatten_long can start from the same best AR checkpoint. Returns the number of files copied."""
    n = 0
    for dp, dn, fn in os.walk(root):
        if os.path.basename(dp).startswith("seed") and os.path.basename(os.path.dirname(dp)) == "ssl_long":
            for f in ("pretrained_ar_long.pt", "pretrain_ar_long.json"):
                if f in fn:
                    dst = os.path.join(out, "ssl_long", os.path.basename(dp), f)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    if not os.path.exists(dst):
                        shutil.copy(os.path.join(dp, f), dst)
                        n += 1
    return n


def orchestrate(a):
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    n_gpu = min(n_gpu, a.gpus) if a.gpus else n_gpu
    queue = sorted([(s, u) for s in a.seeds for u in a.units], key=lambda su: -UNITS[su[1]])
    queue = [su for su in queue if not os.path.exists(os.path.join(a.out, "ssl_long", f"seed{su[0]}", f"{su[1]}_{DONE}"))]      # resume
    running, t0, failed = {}, time.time(), []
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while queue or running:
        for g in range(n_gpu):
            if g not in running and queue:
                s, u = queue.pop(0)
                name = f"seed{s}_{u}"
                log = open(os.path.join(a.out, "logs", f"long_{name}.log"), "a")
                cmd = [sys.executable, "-m", "baseline.selfsup_long", "--out", a.out, "--seed", str(s), "--unit", u, "--device", a.device,
                       "--ft-epochs", str(a.ft_epochs), "--pt-epochs", str(a.pt_epochs), "--pt-patience", str(a.pt_patience),
                       "--min-delta", str(a.min_delta), "--save-epochs", a.save_epochs, "--workers", str(a.workers)]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), name, log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {name}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                print("".join(l for l in open(os.path.join(a.out, "logs", f"long_{name}.log")).readlines()
                              if "TEST" in l or "Error" in l or "[ar]" in l or "pre-training ran" in l)[-1800:], flush=True)
                del running[g]
        time.sleep(5)
    if failed:
        raise SystemExit(f"units failed: {failed}")                  # do not let a failed run look like a COMPLETE kernel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--plan", default=None, choices=[None, "long"])
    ap.add_argument("--unit", default="ar_long", choices=list(UNITS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    ap.add_argument("--units", nargs="*", default=list(UNITS), choices=list(UNITS))
    ap.add_argument("--ft-epochs", type=int, default=10)
    ap.add_argument("--pt-epochs", type=int, default=15)
    ap.add_argument("--pt-patience", type=int, default=2)
    ap.add_argument("--min-delta", type=float, default=0.01)
    ap.add_argument("--save-epochs", default="3,6,10")
    ap.add_argument("--import-from", default=None, help="folder of an earlier kernel's output to take the AR best checkpoints from")
    ap.add_argument("--batch-size", type=int, default=96)
    ap.add_argument("--lr", type=float, default=2.5e-4)
    ap.add_argument("--device", default="gpu")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: use only this many unlabeled reports")
    a = ap.parse_args()
    if a.import_from:
        print(f"imported {import_from(a.import_from, a.out)} AR files from {a.import_from}", flush=True)
    return orchestrate(a) if a.plan else run_unit(a)


if __name__ == "__main__":
    main()
