"""
ITEM R1 of NOTES 30.3: an M3-style model (attention pooling + balanced padding p 0.5) trained on EVERY 512-token window of each report; the report logit = the MAXIMUM window logit.   (OURS; model = baseline/pe.py,
trainer of variant (a) = the authors' ModelTrainer as in baseline/v2pe.py)

    python -m baseline.r1 --mode select --variant a --seed 0 --epochs 3 --out out --tag r1sel_a        # January fold 9 only (66,580 train / 8,718 validation), NO April
    python -m baseline.r1 --mode final  --variant b --seed 0 --epochs 2 --out out --tag r1fin_b        # all January, April logits and weights after the LAST epoch only
    python -m baseline.r1 --plan --mode select --variant a --seeds 0 1 2 3 4 --epochs 3 --out out --tag r1sel_a

Windows: the whole token sequence of the (padded) report, window j = tokens [512 j, 512 j + 512), the last one zero-padded, at most 64 windows (32,768 tokens).
Variants: (a) every window is a training example carrying the report label (batch 96 windows, shuffled over the whole epoch, the authors' trainer); (b) multiple-instance loss: BCE of the report logit = max over
the report's windows (batch 96 reports; micro-batches of 24 reports with gradient accumulation, halved on a CUDA out-of-memory error).
Recipe (as the final M3): AdamW lr 1e-3, weight decay 1e-2, clip 0.5, dropout 0.3, constant lr, corrected tokenizer (50,001-row embedding), balanced padding p 0.5, k ~ U{1..50}, insert / prepend 50/50, replace,
stream 7000, applied to the call list of the whole report BEFORE windowing; padding pool = the benign reports with >= 1 call of the fold-9 TRAINING part (21,507 in final mode, as the final M3).
Per epoch (select mode): training loss, validation pAUC@1e-2 / AUC / TPR@1e-2 / BCE of the report logit (max over windows), R20 and R100 (share of validation malware above the validation 1% threshold after 20 / 100
pool calls are prepended; the same fixed draw as baseline/inmem_pad.py val_robust_set). Select mode computes NO April number and stores no April logit; final mode stores the April logits and the weights after the last epoch.
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

CHUNK, MAXW = 512, 64
CUT = CHUNK * MAXW
RECIPE = dict(lr=1e-3, clip=0.5, dropout=0.3, batch=96, wd=1e-2)
NTR = 75298


def n_windows(total):
    return int(np.clip(-(-int(total) // CHUNK), 1, MAXW))


def windows_from(tokens, total):
    """uint16 [nw, 512] copy of the windows of a token sequence (zero padded at the end); tokens may be longer than the cap"""
    nw = n_windows(total)
    out = np.zeros(nw * CHUNK, dtype=np.uint16)
    m = min(len(tokens), nw * CHUNK, int(total))
    out[:m] = tokens[:m]
    return out.reshape(nw, CHUNK)


def report_windows(store, r):
    t = store.report_tokens(int(r))
    return windows_from(t, len(t))


def edited_windows(store, r, added, gaps=None):
    from baseline import callstore as CS
    tok, total = CS.build_fast(store, int(r), added, gaps, cut=CUT)
    return windows_from(tok, total), int(total)


def build_epoch(store, trn, seed, epoch, pool_rows, pool_n, p_pad=0.5):
    """windows [N, 512] uint16 and owner [N] (position in `trn`) of one epoch: balanced padding of the whole call list, then windowing"""
    from baseline import make_pad
    Ws, owner = [], []
    for i, r in enumerate(trn):
        r = int(r)
        plan = make_pad.plan_train_row(r, seed, epoch, store.n_calls(r), pool_n, 7000, p_pad)
        if plan is None:
            w = report_windows(store, r)
        else:
            added = [store.call(int(pool_rows[pr]), int(c)) for pr, c in plan["draws"]]
            w, _ = edited_windows(store, r, added, plan["gaps"] if plan["mode"] == "insert" else None)
        Ws.append(w)
        owner.append(np.full(len(w), i, dtype=np.int32))
    return np.concatenate(Ws), np.concatenate(owner)


def val_robust_windows(store, y_all, val, pool_rows, k):
    """validation malware reports with k pool calls prepended (the draw of inmem_pad.val_robust_set: default_rng([8200, row]), per call a uniform pool report, then a uniform call of it): windows and starts"""
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    Ws, counts = [], []
    for r in val:
        r = int(r)
        if y_all[r] != 1:
            continue
        rng = np.random.default_rng([8200, r])
        added = []
        for _ in range(k):
            pr = int(rng.integers(len(pool_rows)))
            added.append(store.call(int(pool_rows[pr]), int(rng.integers(pool_n[pr]))))
        w, _ = edited_windows(store, r, added, None)
        Ws.append(w)
        counts.append(len(w))
    return np.concatenate(Ws), np.asarray(counts)


def score_windows(model, W, dev, bs=1024):
    import torch
    model.eval()
    out = np.zeros(len(W), dtype=np.float32)
    with torch.no_grad():
        for i in range(0, len(W), bs):
            out[i:i + bs] = model(torch.from_numpy(W[i:i + bs].astype(np.int64)).to(dev)).float().cpu().numpy().reshape(-1)
    return out


def report_max(z, counts):
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
    return np.maximum.reduceat(z, starts)


def windows_of_rows(store, rows):
    Ws, counts = [], []
    for r in rows:
        w = report_windows(store, int(r))
        Ws.append(w)
        counts.append(len(w))
    return np.concatenate(Ws), np.asarray(counts)


def run(a):
    import torch
    from baseline import callstore as CS, common as C, cv, gap, groupsplit, inmem_pad, padtest, pe
    nb = C.setup_nebula(require_patched=True)
    out_dir = os.path.join(a.out, a.tag)
    os.makedirs(out_dir, exist_ok=True)
    res_path = os.path.join(out_dir, f"seed{a.seed}.json")
    if os.path.exists(res_path) and not a.force:
        print(f"[{a.tag} seed {a.seed}] already done", flush=True)
        return
    tokens = a.tokens or C.find_dir_with("all.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    y_all = lab["y_train"]
    vocab = json.load(open(os.path.join(tokens, "variants", "bpe50k_fix", "vocab.json")))
    sp = a.store if os.path.exists(a.store) else os.path.join(C.find_dir_with(os.path.basename(a.store)), os.path.basename(a.store))
    store = CS.CallStore.load(sp)
    ntr = len(y_all)
    assert ntr == NTR and len(store) == ntr + 17402
    sd = a.split_dir if os.path.exists(os.path.join(a.split_dir, "split.npz")) else C.find_dir_with("split.npz")
    trn, val = groupsplit.val_slice(os.path.join(sd, "split.npz"), os.path.join(sd, "split_hash.json"))               # asserts the fold-9 hash
    assert (len(trn), len(val)) == (66580, 8718)
    pool_trn = trn
    final = a.mode == "final"
    if final:
        trn = np.arange(ntr)
        assert len(trn) == len(pool_trn) + len(val) and not (set(pool_trn.tolist()) & set(val.tolist()))
    pool_rows = inmem_pad.pool_rows_of(store, y_all, pool_trn)
    if not a.limit:
        assert len(pool_rows) == 21507, len(pool_rows)
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    if a.limit:                                                                         # smoke test only
        rg = np.random.default_rng(0)
        trn, val = np.sort(rg.permutation(trn)[:a.limit]), np.sort(rg.permutation(val)[:max(60, a.limit // 4)])
    yt, yv = y_all[trn], y_all[val]
    dev = a.device
    C.set_seed(a.seed)
    model = pe.build_chunks(len(vocab), dropout=RECIPE["dropout"], pe_mode="paper", pool_mode="attn")
    Wv, cv_counts = windows_of_rows(store, val)
    rob = {}
    if not final:
        for k in (20, 100):
            rob[k] = val_robust_windows(store, y_all, val, pool_rows, k)
    log = []
    t0 = time.time()
    if a.variant == "a":
        trainer = cv.make_trainer(model, dev, "binary", RECIPE["batch"], RECIPE["lr"], RECIPE["wd"], clip_grad_norm=RECIPE["clip"])
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=RECIPE["lr"], weight_decay=RECIPE["wd"])
        model.to(dev)
        micro_state = {"micro": 24}
    for ep in range(1, a.epochs + 1):
        te = time.time()
        W, owner = build_epoch(store, trn, a.seed, ep, pool_rows, pool_n)
        counts = np.bincount(owner, minlength=len(trn))
        t_build = time.time() - te
        if a.variant == "a":
            ye = yt[owner]
            trainer.fit(W.astype(np.int32), ye, epochs=1)
            train_loss = float(np.mean([float(v) for v in trainer.train_losses]))
        else:
            train_loss = train_epoch_b(model, opt, W, owner, counts, yt, a.seed, ep, dev, micro_state)
        n_win = int(len(W))
        del W, owner
        z = score_windows(model, Wv, dev)
        zv = report_max(z, cv_counts)
        mv = C.binary_metrics(yv, zv, decision=0.0)
        rec = {"epoch": ep, "train_loss": train_loss, "train_windows": n_win, "val_loss": gap.bce_logits(yv, zv), "val": gap.compact(mv), "seconds_build": round(t_build, 1), "seconds_epoch": round(time.time() - te, 1)}
        if rob:
            thr = padtest.thresholds(zv, yv, 0.01)
            for k, (Wr, cr) in rob.items():
                rec[f"R{k}"] = float((report_max(score_windows(model, Wr, dev), cr) > thr).mean())
            rec["val_thr"] = float(thr)
        np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_val_logits.npy"), zv.astype(np.float32))
        if final and ep == a.epochs:                                                    # April: ONE scoring, after the last epoch; stored, not evaluated here
            Wt, ct = windows_of_rows(store, np.arange(ntr, len(store)))
            zt = report_max(score_windows(model, Wt, dev), ct)
            np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_test_logits.npy"), zt.astype(np.float32))
            torch.save({k_: v_.detach().cpu() for k_, v_ in model.state_dict().items()}, os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_model.pt"))
        log.append(rec)
        print(f"[{a.tag} seed {a.seed}] epoch {ep}: windows {n_win:,} train loss {train_loss:.4f} | val pAUC@1e-2 {mv['pauc@0.01']:.3f} AUC {mv['auc']:.4f} val loss {rec['val_loss']:.4f}"
              + (f" R20 {rec['R20']:.3f} R100 {rec['R100']:.3f}" if rob else "") + f" | build {t_build:.0f}s epoch {rec['seconds_epoch']:.0f}s", flush=True)
    C.dump_json({"tag": a.tag, "mode": a.mode, "variant": a.variant, "seed": a.seed, "epochs": a.epochs, "recipe": RECIPE, "n_train": int(len(trn)), "n_val": int(len(val)), "tokenizer": "bpe50k_fix", "split_hash_asserted": True,
                 "pool_reports": int(len(pool_rows)), "max_windows": MAXW, "per_epoch": log, "env": C.env_info(), "nebula": nb, "train_seconds": round(time.time() - t0, 1),
                 "april": "logits after the last epoch stored (final mode); not evaluated here" if final else "no April number computed or stored (select mode)"}, res_path)


def train_epoch_b(model, opt, W, owner, counts, yt, seed, epoch, dev, state):
    """variant (b): one epoch of the multiple-instance loss; returns the mean report-level BCE"""
    import torch
    starts = np.concatenate([[0], np.cumsum(counts)[:-1]])
    perm = np.random.default_rng([9300, seed, epoch]).permutation(len(counts))
    model.train()
    params = [p for p in model.parameters() if p.requires_grad]
    losses = []
    for s in range(0, len(perm), RECIPE["batch"]):
        batch = perm[s:s + RECIPE["batch"]]
        while True:
            try:
                opt.zero_grad(set_to_none=True)
                total = 0.0
                micro = state["micro"]
                for m0 in range(0, len(batch), micro):
                    mb = batch[m0:m0 + micro]
                    idx = np.concatenate([np.arange(starts[i], starts[i] + counts[i]) for i in mb])
                    seg = torch.from_numpy(np.repeat(np.arange(len(mb)), counts[mb])).to(dev)
                    x = torch.from_numpy(W[idx].astype(np.int64)).to(dev)
                    y = torch.from_numpy(yt[mb].astype(np.float32)).to(dev)
                    z = model(x).reshape(-1)
                    zr = torch.full((len(mb),), -1e30, device=dev, dtype=z.dtype).scatter_reduce(0, seg, z, reduce="amax", include_self=True)
                    loss = torch.nn.functional.binary_cross_entropy_with_logits(zr, y, reduction="sum") / len(batch)
                    loss.backward()
                    total += float(loss.detach())
                torch.nn.utils.clip_grad_norm_(params, RECIPE["clip"])
                opt.step()
                break
            except torch.cuda.OutOfMemoryError:
                opt.zero_grad(set_to_none=True)
                torch.cuda.empty_cache()
                if state["micro"] <= 1:
                    raise
                state["micro"] = max(1, state["micro"] // 2)
                print(f"CUDA out of memory: micro-batch of reports halved to {state['micro']}", flush=True)
        losses.append(total)
    return float(np.mean(losses))


def plan(a):
    import torch
    n_gpu = max(1, torch.cuda.device_count())
    jobs = [s for s in a.seeds if not os.path.exists(os.path.join(a.out, a.tag, f"seed{s}.json"))]
    running, failed, t0 = {}, [], time.time()
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                s = jobs.pop(0)
                log = open(os.path.join(a.out, "logs", f"{a.tag}_seed{s}.log"), "a")
                cmd = [sys.executable, "-m", "baseline.r1", "--mode", a.mode, "--variant", a.variant, "--seed", str(s), "--epochs", str(a.epochs), "--out", a.out, "--tag", a.tag, "--device", a.device, "--split-dir", a.split_dir, "--store", a.store]
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"seed{s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {a.tag} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {a.tag} {name} exited with {p.returncode}", flush=True)
                lines = [l for l in open(os.path.join(a.out, "logs", f"{a.tag}_{name}.log")).readlines() if "epoch" in l or "Error" in l]
                print("".join(lines[-4:])[-900:], flush=True)
                if p.returncode:
                    failed.append(name)
                    for q, _, _ in running.values():
                        if q.poll() is None:
                            q.terminate()
                    raise SystemExit(f"runs failed: {failed}")
                del running[g]
        time.sleep(5)
    print(f"all runs finished in {(time.time() - t0) / 60:.1f} min; failed: {failed}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["select", "final"])
    ap.add_argument("--variant", required=True, choices=["a", "b"])
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3, 4])
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--store", default="all.npz")
    ap.add_argument("--split-dir", default="split")
    ap.add_argument("--limit", type=int, default=0, help="smoke test only")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    return plan(a) if a.plan else run(a)


if __name__ == "__main__":
    main()
