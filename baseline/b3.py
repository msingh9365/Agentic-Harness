"""
Experiment B3 (follow-up): the self-supervised experiment of the paper's Fig. 6 re-run with the baseline-v2 recipe.   (OURS: driver)

    python -m baseline.b3 --write-hashes --labels <tokens>/labels.npz              # once: writes baseline/b3_split_hashes.json
    python -m baseline.b3 --plan --units sup --seeds 0 1 2 3 4 --out /kaggle/working/out        # orchestrator (both GPUs)
    python -m baseline.b3 --unit ar --seed 0 --out out                                  # one unit

Data (assert-checked in every run)
  validation slice  follow-up F's held-out 10% of January (baseline/gap_split_hash.json): used for every choice, never for training
  the other 90%     split per seed (0..4) into an unlabeled 80% (pre-training) and a labeled 20% (fine-tuning), stratified by family;
                    indices hashed in baseline/b3_split_hashes.json
  tokens            BPE V = 8192 fit on the 90% only (variant bpe8k_v2; the old bpe8k was fit on all of January, validation slice included)

Run types (per seed; `lr` in {2e-3 (the v2 recipe), 1e-3 (the allowed fall-back)} for every type)
  upper            supervised on the whole 90%            (chunked Nebula)
  lower            supervised on the labeled 20% only     (chunked Nebula)
  lower_lasttoken  control: the causal last-token classifier on the 20%, no pre-training
  ar_lasttoken     AR pre-training on the unlabeled 80% (6 epochs, early stop on the validation-slice LM loss, patience 2, min delta 0.01),
                   then the last-token classifier fine-tuned on the 20%
  mlm_bert         per-position BERT MLM pre-training (same settings), then the chunked classifier fine-tuned on the 20%
Every fine-tuning uses the authors' ModelTrainer (AdamW, weight decay 1e-2, batch 96, dropout 0.3, gradient clipping 0.5) for up to 6 epochs and, after every
epoch, stores the validation metrics (used for every choice) and the validation and April test LOGITS (test: stored, not looked at until the settings are chosen).
The epoch count and the lr of each run type are chosen afterwards on the validation curves alone (baseline/b3_report.py: `choose`).
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

from baseline import common as C, cv, gap, lm, selfsup
from baseline import selfsup_long as SL

HERE = os.path.dirname(os.path.abspath(__file__))
HASHES = os.path.join(HERE, "b3_split_hashes.json")
LRS = [2e-3, 1e-3]
EPOCHS = 6
WD, CLIP, BATCH, DROPOUT = 1e-2, 0.5, 96, 0.3
RUNS = {"sup": ["upper", "lower", "lower_lasttoken"], "ar": ["ar_lasttoken"], "mlm": ["mlm_bert"], "mlm_theirs": ["mlm_theirs"], "arflat": ["ar_flatten"]}
# which pre-training a unit needs: "mlm_theirs" = the authors' multi-hot MLM, "arflat" = AR flatten (fine-tunes the AR weights of unit "ar" with the bidirectional flatten classifier; needs them in <out>)
UNIT_PRE = {"ar": "ar", "mlm": "mlm_bert", "mlm_theirs": "mlm_theirs", "arflat": "ar"}
COST_MIN = {"sup": 20, "ar": 27, "mlm": 19, "mlm_theirs": 12, "arflat": 6}           # estimated minutes on one T4 (both lrs); the longest units are scheduled first
DONE = "unit_done.json"


# ----------------------------------------------------------------------------- data and splits
def split_hash(unl, lab, val):
    h = hashlib.sha256()
    for a in (unl, lab, val):
        h.update(np.asarray(a, dtype=np.int64).tobytes())
    return h.hexdigest()[:32]


def b3_split(ym_train, seed, hashes=HASHES, check=True):
    """(unlabeled 80%, labeled 20%, validation slice) of seed `seed`; the validation slice is asserted against follow-up F's hash,
    the 80/20 split against baseline/b3_split_hashes.json."""
    from sklearn.model_selection import train_test_split
    trn, val = gap.val_slice(ym_train, hashes=os.path.join(HERE, "gap_split_hash.json") if check else None)
    unl, lab = train_test_split(trn, train_size=0.8, stratify=np.asarray(ym_train)[trn], random_state=seed)
    unl, lab = np.sort(unl), np.sort(lab)
    assert not (set(unl) & set(val)) and not (set(lab) & set(val)) and not (set(unl) & set(lab)) and len(unl) + len(lab) == len(trn)
    info = {"sha256": split_hash(unl, lab, val), "n_unlabeled": len(unl), "n_labeled": len(lab), "n_val": len(val)}
    if check and os.path.exists(hashes):
        ref = json.load(open(hashes)).get("seeds", {}).get(str(seed))
        if ref is not None:
            assert info == ref, f"seed {seed}: split differs from the stored one: {info} vs {ref}"
    return unl, lab, val, info


def write_hashes(labels):
    ym = np.load(labels)["ym_train"]
    seeds = {str(s): b3_split(ym, s, check=False)[3] for s in range(5)}
    gap.val_slice(ym)                                             # the validation slice itself is asserted
    json.dump({"note": "B3 splits: validation slice of follow-up F (gap_split_hash.json), the rest split 80/20 stratified by family, "
                       "train_test_split(train_size=0.8, stratify=ym, random_state=seed); sha256 over (unlabeled, labeled, validation) indices",
               "seeds": seeds}, open(HASHES, "w"), indent=1)
    print(json.dumps(seeds, indent=1))


def load(tokens, variant):
    vdir = os.path.join(tokens, "variants", variant)
    lab = np.load(os.path.join(tokens, "labels.npz"))
    return (np.load(os.path.join(vdir, "x_train.npy")), lab["y_train"], lab["ym_train"], np.load(os.path.join(vdir, "x_test.npy")), lab["y_test"],
            json.load(open(os.path.join(vdir, "vocab.json"))), json.load(open(os.path.join(vdir, "info.json"))) if os.path.exists(os.path.join(vdir, "info.json")) else {})


# ----------------------------------------------------------------------------- models
def downstream(run, V):
    if run in ("lower_lasttoken", "ar_lasttoken"):
        return lm.build_fullattn(V, DROPOUT, causal=True, last_token=True)
    if run == "ar_flatten":
        return lm.build_fullattn(V, DROPOUT, causal=False)
    return lm.build_chunked(V, DROPOUT)


def torch_device(device):
    return {"gpu": "cuda"}.get(device, device)


# ----------------------------------------------------------------------------- one fine-tuning / supervised run with per-epoch validation
def train_epochs(model, xt, yt, xv, yv, x_test, y_test, lr, epochs, device, run_dir, name, extra, save_model_epochs=()):
    """The authors' ModelTrainer for `epochs` epochs on (xt, yt); after every epoch: validation metrics + loss, and the validation and test logits (stored)."""
    import torch
    dev = torch_device(device)
    trainer = cv.make_trainer(model, dev, "binary", BATCH, lr, WD, clip_grad_norm=CLIP)
    bpe = int(np.ceil(len(xt) / BATCH))
    log, zvs, zts, t0 = [], [], [], time.time()

    def on_epoch_end(ep):
        zv, zt = cv.predict_logits(model, xv, dev, bs=512), cv.predict_logits(model, x_test, dev, bs=512)
        mv, mt = C.binary_metrics(yv, zv, decision=0.0), C.binary_metrics(y_test, zt, decision=0.0)
        rec = {"epoch": ep, "batches": ep * bpe, "seconds": round(time.time() - t0, 1), "val_loss": gap.bce_logits(yv, zv), "val": gap.compact(mv),
               "val_n_tied_at_top": mv["n_tied_at_top"], "test_NOT_FOR_SELECTION": gap.compact(mt),
               "test_p32_tpr@0.001": C.binary_metrics(y_test, C.sigmoid32(zt))["tpr@0.001"]}
        log.append(rec); zvs.append(zv.astype(np.float32)); zts.append(zt.astype(np.float32))
        print(f"  [{name}] epoch {ep}: val TPR@1e-3 {mv['tpr@0.001']:.3f} @1e-2 {mv['tpr@0.01']:.3f} AUC {mv['auc']:.4f} loss {rec['val_loss']:.4f} | {rec['seconds']:.0f}s", flush=True)
        if ep in save_model_epochs:
            torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, os.path.join(run_dir, f"{name}_epoch{ep}_model.pt"))

    hook = gap.EpochHook(model, bpe, on_epoch_end)
    trainer.model.forwardPass = hook
    trainer.fit(xt, yt, epochs=epochs)
    hook.finish()
    assert len(log) == epochs, (len(log), epochs)
    np.save(os.path.join(run_dir, f"{name}_val_logits.npy"), np.stack(zvs))
    np.save(os.path.join(run_dir, f"{name}_test_logits.npy"), np.stack(zts))
    res = {"lr": lr, "epochs": epochs, "batch_size": BATCH, "weight_decay": WD, "clip_grad_norm": CLIP, "dropout": DROPOUT, "batches_per_epoch": bpe,
           "n_train": int(len(xt)), "n_val": int(len(xv)), "train_seconds": round(time.time() - t0, 1), "per_epoch": log,
           "collapsed": bool(log[-1]["val"]["auc"] < 0.6), **extra}
    C.dump_json(res, os.path.join(run_dir, f"{name}.json"))
    return res


# ----------------------------------------------------------------------------- pre-training (validation LM loss on the 10% slice)
def pretrain_cached(kind, x_unl, x_val, vocab, a, seed, out):
    """Pre-train (or load the cache): returns (best state dict, history). The validation LM loss uses the 10% validation slice (evaluation only);
    a checkpoint is written after every epoch: <out>/ckpt_<kind>/epoch<k>.pt. The full state dict of the best epoch is <out>/pretrained_<kind>_v2.pt."""
    import torch
    cache, hist_path = os.path.join(out, f"pretrained_{kind}_v2.pt"), os.path.join(out, f"pretrain_{kind}_v2.json")
    if os.path.exists(cache) and os.path.exists(hist_path):
        return torch.load(cache, weights_only=True), json.load(open(hist_path))
    a.val_x = x_val                                                   # selfsup.pretrain: LM validation on the slice, all of x_unl is trained on
    a.ckpt_dir = os.path.join(out, f"ckpt_{kind}")
    a.save_epochs = tuple(range(1, a.pt_epochs + 1))
    C.set_seed(seed)
    pre, hist = selfsup.pretrain(kind, x_unl, vocab, a, seed, f"b3_pre_{kind}_seed{seed}")
    shutil.rmtree(os.path.join(selfsup.LIT_DIR, f"b3_pre_{kind}_seed{seed}"), ignore_errors=True)
    os.makedirs(out, exist_ok=True)
    torch.save(lm.encoder_state(pre) if kind == "mlm_theirs" else pre, cache)      # their MLM head is huge: keep the encoder only (as in B and B2)
    C.dump_json(hist, hist_path)
    return pre, hist


# ----------------------------------------------------------------------------- one unit (all run types of one seed that share work)
def execute(unit, a, seed, x, y, xt, yt, vocab, unl, lab, val, split_info, out):
    import torch
    V = len(vocab)
    os.makedirs(out, exist_ok=True)
    base = {"seed": seed, "split": split_info, "n_unlabeled": int(len(unl)), "n_labeled": int(len(lab)), "n_val": int(len(val)), "env": C.env_info(),
            "tokenizer": a.variant, "tokens_info": a.tokens_info}
    pre_path, pre_hist = None, None
    if unit in UNIT_PRE:
        kind = UNIT_PRE[unit]
        if unit == "arflat":
            assert os.path.exists(os.path.join(out, "pretrained_ar_v2.pt")), "arflat needs the AR pre-training of unit ar (use --import-from)"
        pre, pre_hist = pretrain_cached(kind, x[unl], x[val], vocab, a, seed, out)
        pre_path = os.path.join(out, f"pretrained_{kind}_v2.pt")
        print(f"  [{kind}] pre-training ran {len(pre_hist['epochs'])} epochs, best epoch {pre_hist['best_epoch']}, stopped early {pre_hist['stopped_early']}, "
              f"val LM loss {[round(e['val_loss'], 3) for e in pre_hist['epochs']]}", flush=True)
    for run in RUNS[unit]:
        for lr in a.lrs:
            name = f"{run}_lr{lr:g}"
            if os.path.exists(os.path.join(out, f"{name}.json")):
                print(f"  [{name}] already done", flush=True)
                continue
            C.set_seed(seed)
            model = downstream(run, V)
            proof = {}
            if pre_path:
                proof = SL.init_from_checkpoint(model, pre_path)
                print(f"  [{name}] fine-tuning starts from the epoch-{pre_hist['best_epoch']} pre-trained weights: encoder checksum "
                      f"{proof['checksum_downstream_after']['sha256']} (distance {proof['before_loading']['dist_to_pretrained']:.3f} -> "
                      f"{proof['after_loading']['dist_to_pretrained']:.1e})", flush=True)
            idx = lab if run != "upper" else np.sort(np.concatenate([unl, lab]))
            dev = torch_device(a.device)
            model.to(dev) if dev != "cpu" else None
            res = train_epochs(model, x[idx], y[idx], x[val], y[val], xt, yt, lr, a.epochs, a.device, out, name,
                               {"run": run, "weight_proof": proof, "pretraining": pre_hist, **base})
            del model
            if dev != "cpu":
                torch.cuda.empty_cache()
    C.dump_json({"unit": unit, "seed": seed, "finished": time.strftime("%Y-%m-%d %H:%M:%S")}, os.path.join(out, f"{unit}_{DONE}"))


def run_unit(a):
    nb = C.setup_nebula(require_patched=True)
    tokens = a.tokens or C.find_dir_with("labels.npz")
    x, y, ym, xt, yt, vocab, info = load(tokens, a.variant)
    a.tokens_info = {k: info.get(k) for k in ("vocab_entries", "trained_on_train", "tokenizer_fit_reports", "kind")}
    unl, lab, val, split_info = b3_split(ym, a.seed)
    if a.variant == "bpe8k_v2":
        assert info.get("tokenizer_fit_reports") == 67768, f"the tokenizer must be fit on the 90% only: {info}"
    if a.limit:                                                      # smoke test only
        r = np.random.default_rng(0)
        unl, lab, val = r.permutation(unl)[:a.limit], r.permutation(lab)[:max(8, a.limit // 4)], r.permutation(val)[:max(40, a.limit // 4)]
        keep = r.permutation(len(xt))[:300]
        xt, yt = xt[keep], yt[keep]
    out = os.path.join(a.out, "b3", f"seed{a.seed}")
    print(f"[seed {a.seed}/{a.unit}] vocab {len(vocab)} | unlabeled {len(unl)} labeled {len(lab)} val {len(val)} test {len(xt)} | split {split_info} | "
          f"tokens {a.tokens_info} | {C.env_info()} | {nb}", flush=True)
    execute(a.unit, a, a.seed, x, y, xt, yt, vocab, unl, lab, val, split_info, out)


def import_from(root, out):
    """Copy the AR pre-training results (best weights + history) of an earlier kernel (attached with kernel_sources) into <out>/b3/seed*, so that unit
    arflat fine-tunes exactly the AR weights of the main run. Returns the number of files copied."""
    n = 0
    for dp, dn, fn in os.walk(root):
        if os.path.basename(dp).startswith("seed") and os.path.basename(os.path.dirname(dp)) == "b3":
            for f in ("pretrained_ar_v2.pt", "pretrain_ar_v2.json"):
                if f in fn:
                    dst = os.path.join(out, "b3", os.path.basename(dp), f)
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
    queue = sorted([(s, u) for s in a.seeds for u in a.units], key=lambda su: -COST_MIN[su[1]])
    queue = [su for su in queue if not os.path.exists(os.path.join(a.out, "b3", f"seed{su[0]}", f"{su[1]}_{DONE}"))]
    running, t0, failed = {}, time.time(), []
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while queue or running:
        for g in range(n_gpu):
            if g not in running and queue:
                s, u = queue.pop(0)
                name = f"seed{s}_{u}"
                log = open(os.path.join(a.out, "logs", f"b3_{name}.log"), "a")
                cmd = [sys.executable, "-m", "baseline.b3", "--out", a.out, "--seed", str(s), "--unit", u, "--device", a.device, "--variant", a.variant,
                       "--epochs", str(a.epochs), "--pt-epochs", str(a.pt_epochs), "--pt-patience", str(a.pt_patience), "--min-delta", str(a.min_delta),
                       "--workers", str(a.workers), "--lrs"] + [str(l) for l in a.lrs]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), name, log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {name}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                print("".join(l for l in open(os.path.join(a.out, "logs", f"b3_{name}.log")).readlines()
                              if "pre-training ran" in l or "Error" in l or "epoch 6" in l)[-1500:], flush=True)
                del running[g]
        time.sleep(5)
    if failed:
        raise SystemExit(f"units failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--out", default="out")
    ap.add_argument("--variant", default="bpe8k_v2")
    ap.add_argument("--write-hashes", action="store_true")
    ap.add_argument("--labels", default=None)
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--import-from", default=None, help="folder of an earlier kernel's output to take the AR best weights from (unit arflat)")
    ap.add_argument("--unit", default="sup", choices=list(RUNS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    ap.add_argument("--units", nargs="*", default=list(RUNS), choices=list(RUNS))
    ap.add_argument("--lrs", type=float, nargs="*", default=LRS)
    ap.add_argument("--epochs", type=int, default=EPOCHS)
    ap.add_argument("--pt-epochs", type=int, default=6)
    ap.add_argument("--pt-patience", type=int, default=2)
    ap.add_argument("--min-delta", type=float, default=0.01)
    ap.add_argument("--batch-size", type=int, default=96)
    ap.add_argument("--lr", type=float, default=2.5e-4, help="LM pre-training lr (as in B and B2)")
    ap.add_argument("--device", default="gpu")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--gpus", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: use only this many unlabeled reports")
    a = ap.parse_args()
    if a.write_hashes:
        return write_hashes(a.labels)
    if a.import_from:
        print(f"imported {import_from(a.import_from, a.out)} AR files from {a.import_from}", flush=True)
    return orchestrate(a) if a.plan else run_unit(a)


if __name__ == "__main__":
    main()
