"""
ATT+bal-2L: ATT+bal as level 1 of the two-level Nebula (NOTES 19).   (OURS; third_party/nebula is not touched)

    level 1  the ATT+bal encoder (baseline/pe.py: pe_mode "paper", pool_mode "attn", BPE-50k, d 64, 8 heads, FFN 256, 2 layers, chunk-attention 64, dropout 0.3), shared weights, applied to
             every REAL chunk of 512 tokens; positions are 0..511 inside each chunk; the chunk vector is the 64-d attention-pooled vector (`core()`); the classifier head of ATT+bal is removed
    level 2  as hier_nebula/model.py: learned [CLS] + chunk vectors + learned chunk-position embedding, 2 pre-norm encoder layers (d 64, 4 heads, FFN 128, dropout 0.1), padded chunks masked,
             LayerNorm(CLS) -> Linear -> logit

Tokens: the first 8 x 512 = 4,096 tokens of the WHOLE (edited) report, from the call-token store (baseline/callstore.py, cut 4,096). Balanced padding (model A) is applied to the whole call list
BEFORE chunking, in memory, with the plan of ATT+bal (make_pad.plan_train_row, stream 7000: the same edits as ATT+bal for the same seed, epoch and row). Model B: the same code without padding.

    python -m baseline.twolevel --out out --seed 0 --epochs 3 --lr 2e-3 --padding balanced --init scratch --tag A_scratch_lr2e-3         one run (one GPU)
    python -m baseline.twolevel --pilot --out out                                                                                          Stage 1 (NOTES 19.8): self tests, then A and B for 1 epoch
    python -m baseline.twolevel --selftest --out out

Recipe (NOTES 19.5): AdamW, weight decay 1e-2, clip 0.5 (global norm), constant lr, effective batch 96 (micro-batches + gradient accumulation if 96 reports do not fit), fp32. After every epoch:
validation metrics and loss, training losses (the format of results/loss_curves), validation logits; April logits and weights are STORED (unless --no-april) and not evaluated here.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

from baseline import callstore as CS, common as C, gap, inmem_pad, make_pad, pe

CHUNK, MAXK = 512, 8
CUT = CHUNK * MAXK
VAL_HASH = "b18269395891ee1e51d69e4a7293f0af"                   # NOTES 19.2 = baseline/gap_split_hash.json["sha256"]
BATCH, WD, CLIP, DROP1, DROP2 = 96, 1e-2, 0.5, 0.3, 0.1
PAD_STREAM, EPOCH_STREAM = 7000, 9100                           # edit plan of ATT+bal (REPORT 5.10); order of the training reports: default_rng([9100, seed, epoch])


# ----------------------------------------------------------------------------- model
def n_real_chunks(total_tokens):
    """Real chunks of a report with `total_tokens` tokens (the whole edited report): ceil(min(total, 4096) / 512), at least 1 (an empty report is one all-padding chunk)."""
    t = np.minimum(np.asarray(total_tokens), CUT)
    return np.clip(-(-t // CHUNK), 1, MAXK).astype(np.int64)


def make_level1(vocab_size, dropout=DROP1):
    """The ATT+bal encoder built exactly as ATT+bal is (same random stream, so the same initial weights for the same seed), then its classifier head is removed (core() does not use it)."""
    m = pe.build_chunks(vocab_size, dropout=dropout, pe_mode="paper", pool_mode="attn")
    del m.classifier_head
    return m


def load_warm(level1, path):
    """ATT+bal weights of the same seed into level 1: every key except the classifier head must match (strict)."""
    import torch
    sd = torch.load(path, map_location="cpu", weights_only=True)
    head = [k for k in sd if k.startswith("classifier_head")]
    level1.load_state_dict({k: v for k, v in sd.items() if k not in head}, strict=True)
    return head


def build_model_class():
    import torch
    from torch import nn

    class TwoLevel(nn.Module):
        def __init__(self, level1, d=64, heads=4, layers=2, hidden=128, dropout=DROP2, max_chunks=MAXK):
            super().__init__()
            self.level1, self.max_chunks, self.d = level1, max_chunks, d
            self.cls = nn.Parameter(torch.randn(1, 1, d) * 0.02)
            self.pos = nn.Embedding(max_chunks + 1, d)                                 # position 0 = CLS
            layer = nn.TransformerEncoderLayer(d, heads, hidden, dropout, batch_first=True, norm_first=True)
            self.level2 = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
            self.norm = nn.LayerNorm(d)
            self.head = nn.Linear(d, 1)

        def chunk_vectors(self, tok, nch):
            """tok [B, 4096] long, nch [B] long -> ([B, K, d] chunk vectors, [B, K] real-chunk mask); K = the largest real chunk count in the batch. Only real chunks go through level 1."""
            B, K = tok.shape[0], int(nch.max())
            ids = tok[:, :K * CHUNK].reshape(B, K, CHUNK)
            mask = torch.arange(K, device=tok.device)[None, :] < nch[:, None]
            vec = self.level1.core(ids[mask])
            x = vec.new_zeros(B, K, vec.shape[-1])
            x[mask] = vec
            return x, mask

        def classify(self, x, mask):
            B, K, _ = x.shape
            x = torch.cat([self.cls.expand(B, -1, -1), x], dim=1) + self.pos(torch.arange(K + 1, device=x.device))
            pad = torch.cat([torch.zeros(B, 1, dtype=torch.bool, device=mask.device), ~mask], dim=1)
            x = self.level2(x, src_key_padding_mask=pad)
            return self.head(self.norm(x[:, 0])).squeeze(-1)

        def forward(self, tok, nch):
            return self.classify(*self.chunk_vectors(tok, nch))

    return TwoLevel


def make_model(vocab_size, seed, init="scratch", warm_path=None):
    """Level 1 built right after set_seed(seed) as in ATT+bal, level 2 next in the same random stream."""
    C.set_seed(seed)
    l1 = make_level1(vocab_size)
    if init == "warm":
        assert warm_path, "--init warm needs the ATT+bal weights of this seed"
        load_warm(l1, warm_path)
    return build_model_class()(l1)


def param_counts(model):
    n1 = sum(p.numel() for p in model.level1.parameters())
    n = sum(p.numel() for p in model.parameters())
    return {"level1": int(n1), "level2": int(n - n1), "total": int(n)}


# ----------------------------------------------------------------------------- data
def val_hash(trn, val):
    h = hashlib.sha256()
    h.update(trn.astype(np.int64).tobytes())
    h.update(val.astype(np.int64).tobytes())
    return h.hexdigest()[:32]


def load_data(a):
    """Everything in memory: X [n_reports, 4096] uint16 (first 4,096 tokens of the ORIGINAL reports: January rows 0.., then April), total token counts, labels, slices. Asserts the validation hash and that
    the first 512 tokens of every row equal the stored BPE-50k rows x_train / x_test."""
    tokens = a.tokens or C.find_dir_with("labels.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    y_all, y_test = lab["y_train"], lab["y_test"]
    ntr, nte = len(y_all), len(y_test)
    sp = a.store if a.store and os.path.exists(a.store) else os.path.join(C.find_dir_with("all.npz"), "all.npz")
    store = CS.CallStore.load(sp)
    assert len(store) == ntr + nte, (len(store), ntr, nte)
    trn, val = gap.val_slice(lab["ym_train"])
    assert val_hash(trn, val) == VAL_HASH and (len(trn), len(val)) == (67768, 7530), "validation slice differs from the one of NOTES 19.2"
    n = len(store)
    X = np.zeros((n, CUT), dtype=np.uint16)
    tot = np.zeros(n, dtype=np.int64)
    for r in range(n):
        t = store.report_tokens(r)
        m = min(len(t), CUT)
        X[r, :m] = t[:m]
        tot[r] = len(t)
    x_tr, x_te, vocab = gap.load(tokens, a.variant)
    assert np.array_equal(X[:ntr, :CHUNK], x_tr.astype(np.uint16)) and np.array_equal(X[ntr:, :CHUNK], x_te.astype(np.uint16)), "call store != stored BPE-50k rows"
    return {"store": store, "X": X, "tot": tot, "y_all": y_all, "y_test": y_test, "ntr": ntr, "nte": nte, "trn": trn, "val": val, "vocab_size": len(vocab), "tokens": tokens}


def train_pool_rows(D):
    return inmem_pad.pool_rows_of(D["store"], D["y_all"], D["trn"])


def epoch_edits(D, seed, epoch, pool_rows, p_pad=0.5):
    """(positions in `trn` [m], tokens uint16 [m, 4096], total token counts [m]) of the edited training reports of this (seed, epoch): the plan of ATT+bal (stream 7000), applied to the whole call list, then
    cut at 4,096 tokens (build_fast gives the same tokens as build_tokens; checked in the self test)."""
    store, trn = D["store"], D["trn"]
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    pos, toks, tots = [], [], []
    for i, r in enumerate(trn):
        r = int(r)
        plan = make_pad.plan_train_row(r, seed, epoch, store.n_calls(r), pool_n, PAD_STREAM, p_pad)
        if plan is None:
            continue
        added = [store.call(int(pool_rows[pr]), int(c)) for pr, c in plan["draws"]]
        t, total = CS.build_fast(store, r, added, plan["gaps"] if plan["mode"] == "insert" else None, cut=CUT)
        pos.append(i), toks.append(t), tots.append(total)
    if not pos:
        return np.zeros(0, np.int64), np.zeros((0, CUT), np.uint16), np.zeros(0, np.int64)
    return np.asarray(pos, dtype=np.int64), np.stack(toks), np.asarray(tots, dtype=np.int64)


# ----------------------------------------------------------------------------- scoring
def predict(model, X, tot, dev, bs=192):
    """Logits [n] float32 (eval mode, no dropout); X uint16 [n, 4096], tot = total token counts."""
    import torch
    model.eval()
    nch = n_real_chunks(tot)
    out = np.zeros(len(X), dtype=np.float32)
    with torch.no_grad():
        for i in range(0, len(X), bs):
            x = torch.from_numpy(np.asarray(X[i:i + bs]).astype(np.int64)).to(dev)
            out[i:i + bs] = model(x, torch.from_numpy(nch[i:i + bs]).to(dev)).float().cpu().numpy()
    return out


# ----------------------------------------------------------------------------- training
def bce_sum(logits, y):
    import torch
    return torch.nn.functional.binary_cross_entropy_with_logits(logits, y, reduction="sum")


def train_step(model, opt, params, X, nch, y, micro, dev, log):
    """One optimizer step on a batch of <= 96 reports: micro-batches of `micro` reports with gradient accumulation (loss = mean over the whole batch); on a CUDA OOM the micro-batch is halved and the batch retried."""
    import torch
    while True:
        try:
            opt.zero_grad(set_to_none=True)
            total = 0.0
            for s in range(0, len(X), micro):
                xb = torch.from_numpy(X[s:s + micro].astype(np.int64)).to(dev, non_blocking=True)
                nb = torch.from_numpy(nch[s:s + micro]).to(dev)
                yb = torch.from_numpy(y[s:s + micro].astype(np.float32)).to(dev)
                loss = bce_sum(model(xb, nb), yb) / len(X)
                loss.backward()
                total += float(loss.detach())
            torch.nn.utils.clip_grad_norm_(params, CLIP)
            opt.step()
            return total, micro
        except torch.cuda.OutOfMemoryError:
            opt.zero_grad(set_to_none=True)
            torch.cuda.empty_cache()
            if micro <= 1:
                raise
            micro = max(1, micro // 2)
            log(f"CUDA out of memory: micro-batch halved to {micro} (gradient accumulation to an effective batch of {BATCH})")


def run(a):
    import torch
    nb = C.setup_nebula(require_patched=True)
    out_dir = os.path.join(a.out, a.tag)
    os.makedirs(out_dir, exist_ok=True)
    res_path = os.path.join(out_dir, f"seed{a.seed}.json")
    if os.path.exists(res_path) and not a.force:
        print(f"[{a.tag} seed {a.seed}] already done", flush=True)
        return
    dev = a.device
    log = lambda s: print(f"[{a.tag} seed {a.seed}] {s}", flush=True)
    t_load = time.time()
    D = load_data(a)
    store, X, tot, y_all, trn, val, ntr = D["store"], D["X"], D["tot"], D["y_all"], D["trn"], D["val"], D["ntr"]
    if a.limit:                                                                          # smoke test only
        r = np.random.default_rng(0)
        trn, val = np.sort(r.permutation(trn)[:a.limit]), np.sort(r.permutation(val)[:max(40, a.limit // 4)])
        D["trn"] = trn
    Xtr, ttr, ytr = X[trn], tot[trn], y_all[trn]
    Xv, tv, yv = X[val], tot[val], y_all[val]
    Xte, tte, yte = X[ntr:], tot[ntr:], D["y_test"]
    pool_rows = train_pool_rows(D)
    log(f"data loaded in {time.time() - t_load:.0f}s: train {len(trn):,}, validation {len(val):,} (hash {VAL_HASH} asserted), April {len(Xte):,}; TRAIN pool {len(pool_rows):,} benign reports")
    warm_path = None
    if a.init == "warm":
        from baseline import padtest
        warm_path = padtest.find_weights("attbal", a.seed, None, a.search)
    model = make_model(D["vocab_size"], a.seed, a.init, warm_path).to(dev)
    counts = param_counts(model)
    log(f"parameters {counts}; init {a.init}" + (f" ({warm_path})" if warm_path else ""))
    params = [p for p in model.parameters() if p.requires_grad]
    l1_ids = {id(p) for p in model.level1.parameters()}
    p1 = [p for p in params if id(p) in l1_ids]
    p2 = [p for p in params if id(p) not in l1_ids]
    opt = torch.optim.AdamW([{"params": p1, "lr": a.lr * a.l1_mult, "base_mult": a.l1_mult}, {"params": p2, "lr": a.lr, "base_mult": 1.0}], lr=a.lr, weight_decay=WD)
    ema_model = None
    if a.ema:
        import copy
        ema_model = copy.deepcopy(model).to(dev)
        for q in ema_model.parameters():
            q.requires_grad_(False)
    gstep = 0
    sub_idx = np.random.default_rng(11).choice(len(Xtr), min(2000, len(Xtr)), replace=False)       # fixed subset of 2,000 training reports (positions in the 90% slice), UNEDITED tokens
    micro = a.micro or BATCH
    bpe = int(np.ceil(len(Xtr) / BATCH))
    total_steps = a.epochs * bpe
    batch_losses, per_epoch, timing = [], [], []
    if a.freeze1_steps:
        for q in p1:
            q.requires_grad_(False)
    for ep in range(1, a.epochs + 1):
        t0 = time.time()
        if a.padding == "balanced":
            pos, tk, tt = epoch_edits(D, a.seed, ep, pool_rows, p_pad=a.pad_prob)
            Xe, te_ = Xtr.copy(), ttr.copy()
            Xe[pos], te_[pos] = tk, tt
            n_edit = int(len(pos))
            del tk
        else:
            Xe, te_, n_edit = Xtr, ttr, 0
        t_edit = time.time() - t0
        nch_e = n_real_chunks(te_)
        perm = np.random.default_rng([EPOCH_STREAM, a.seed, ep]).permutation(len(Xe))
        model.train()
        if a.freeze1_steps and gstep < a.freeze1_steps:
            model.level1.eval()                                                          # frozen level 1 gives plain features (no dropout) until it is released
        if str(dev).startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()
        t1, new = time.time(), []
        for s in range(0, len(perm), BATCH):
            idx = perm[s:s + BATCH]
            if a.freeze1_steps and gstep == a.freeze1_steps:
                for q in p1:
                    q.requires_grad_(True)
                model.level1.train()
                log(f"level 1 released at step {gstep}")
            f = (1.0 - gstep / total_steps) if a.sched == "linear" else 1.0
            for g_ in opt.param_groups:
                g_["lr"] = a.lr * g_["base_mult"] * f
            l, micro = train_step(model, opt, [q for q in params if q.requires_grad], Xe[idx], nch_e[idx], ytr[idx], micro, dev, log)
            gstep += 1
            if ema_model is not None:
                d_ = min(a.ema, (1 + gstep) / (10 + gstep))
                with torch.no_grad():
                    for qe, qm in zip(ema_model.parameters(), model.parameters()):
                        qe.mul_(d_).add_(qm.detach(), alpha=1 - d_)
            new.append(l)
        if str(dev).startswith("cuda"):
            torch.cuda.synchronize()
        t_train = time.time() - t1
        peak = round(torch.cuda.max_memory_allocated() / 2**30, 2) if str(dev).startswith("cuda") else None
        reserved = round(torch.cuda.max_memory_reserved() / 2**30, 2) if str(dev).startswith("cuda") else None
        t2 = time.time()
        zv = predict(model, Xv, tv, dev)
        mv = C.binary_metrics(yv, zv, decision=0.0)
        zs = predict(model, Xtr[sub_idx], ttr[sub_idx], dev)
        t_eval_val = time.time() - t2
        batch_losses.extend(new)
        rec = {"epoch": ep, "step_end": len(batch_losses), "n_batches": len(new), "train_epoch_mean_loss": float(np.mean(new)), "val_loss": gap.bce_logits(yv, zv), "val_pauc@1e-2": mv["pauc@0.01"], "val_auc": mv["auc"],
               "train_subset_clean_loss": gap.bce_logits(ytr[sub_idx], zs), "val": gap.compact(mv), "val_n_tied_at_top": mv["n_tied_at_top"], "edited_reports": n_edit, "micro_batch": micro,
               "mean_chunks_train_epoch": float(nch_e.mean()), "mean_chunks_val": float(n_real_chunks(tv).mean()), "peak_gpu_mem_allocated_gb": peak, "peak_gpu_mem_reserved_gb": reserved,
               "seconds_edit": round(t_edit, 1), "seconds_train": round(t_train, 1), "seconds_val_eval": round(t_eval_val, 1)}
        np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_val_logits.npy"), zv.astype(np.float32))
        if ema_model is not None:
            zve = predict(ema_model, Xv, tv, dev)
            mve = C.binary_metrics(yv, zve, decision=0.0)
            rec["ema"] = {"val_pauc@1e-2": mve["pauc@0.01"], "val_auc": mve["auc"], "val_loss": gap.bce_logits(yv, zve), "val": gap.compact(mve), "decay": a.ema}
            np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_val_logits_ema.npy"), zve.astype(np.float32))
            log(f"epoch {ep} EMA: val pAUC@1e-2 {mve['pauc@0.01']:.4f} AUC {mve['auc']:.4f} val loss {rec['ema']['val_loss']:.4f}")
        if not a.no_april:                                                                   # stored, NOT evaluated here
            t3 = time.time()
            zt = predict(model, Xte, tte, dev)
            rec["seconds_april_score"] = round(time.time() - t3, 1)
            np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_test_logits.npy"), zt.astype(np.float32))
            torch.save({k: v.detach().cpu() for k, v in model.state_dict().items()}, os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_model.pt"))
            if ema_model is not None:
                np.save(os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_test_logits_ema.npy"), predict(ema_model, Xte, tte, dev).astype(np.float32))
                torch.save({k: v.detach().cpu() for k, v in ema_model.state_dict().items()}, os.path.join(out_dir, f"seed{a.seed}_epoch{ep}_model_ema.pt"))
        rec["seconds_epoch_total"] = round(time.time() - t0, 1)
        per_epoch.append(rec)
        log(f"epoch {ep}: val pAUC@1e-2 {mv['pauc@0.01']:.4f} TPR@1e-3 {mv['tpr@0.001']:.3f} @1e-2 {mv['tpr@0.01']:.3f} AUC {mv['auc']:.4f} val loss {rec['val_loss']:.4f} train loss {rec['train_epoch_mean_loss']:.4f} | "
            f"edit {t_edit:.0f}s train {t_train:.0f}s eval {t_eval_val:.0f}s | peak {peak} GB, micro {micro}, mean chunks {rec['mean_chunks_train_epoch']:.2f}")
        del Xe
    bl = np.array(batch_losses)
    steps = np.arange(10, len(bl) + 1, 10)
    res = {"model": a.tag, "seed": a.seed, "epochs": a.epochs, "steps_per_epoch": bpe, "recipe": {"lr": a.lr, "sched": a.sched, "level1_lr_mult": a.l1_mult, "freeze_level1_steps": a.freeze1_steps, "ema": a.ema, "wd": WD, "clip": CLIP, "dropout_level1": DROP1, "dropout_level2": DROP2, "batch": BATCH, "micro_batch_used": micro, "precision": "fp32"},
           "init": a.init, "padding": ({"mode": "replace", "p": a.pad_prob, "k": "U{1..50}", "insert_prepend": "50/50", "pool": "TRAIN pool only", "stream": PAD_STREAM, "applied": "whole call list before chunking, cut at 4,096 tokens"} if a.padding == "balanced" else None),
           "params": counts, "split_hash_asserted": VAL_HASH, "n_train": int(len(Xtr)), "n_val": int(len(Xv)), "n_val_benign": int((yv == 0).sum()), "tokenizer": a.variant,
           "train_loss_note": ("mean BCE of the last 10 training batches (dropout on) on the PADDED training mix of that epoch" if a.padding == "balanced" else "mean BCE of the last 10 training batches (dropout on); no padding"),
           "train_loss_every": 10, "train_loss_step": steps.tolist(), "train_loss_mean_last_10": [float(bl[g - 10:g].mean()) for g in steps], "per_epoch": per_epoch,
           "train_subset": {"numpy_seed": 11, "n": int(len(sub_idx)), "tokens": "unedited", "mode": "eval (no dropout)"}, "env": C.env_info(), "nebula": nb,
           "april": "not evaluated by this script" if not a.no_april else "not scored (--no-april)", "wall_seconds": round(time.time() - t_load, 1)}
    if a.throughput:
        res["throughput"] = throughput(model, D, pool_rows, dev)
        log(f"throughput {res['throughput']}")
    C.dump_json(res, res_path)


def throughput(model, D, pool_rows, dev):
    """Scoring speed of the final model on 1,000 VALIDATION malware reports edited in memory by prepending k TRAIN-pool calls (k = 0, 100, 200). Validation reports only (no April)."""
    import torch
    store, val, y_all = D["store"], D["val"], D["y_all"]
    rows = [int(r) for r in val if y_all[r] == 1][:1000]
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    out = {}
    for k in (0, 100, 200):
        X = np.zeros((len(rows), CUT), dtype=np.uint16)
        tt = np.zeros(len(rows), dtype=np.int64)
        for i, r in enumerate(rows):
            rng = np.random.default_rng([8300, r])
            added = []
            for _ in range(k):
                pr = int(rng.integers(len(pool_rows)))
                added.append(store.call(int(pool_rows[pr]), int(rng.integers(pool_n[pr]))))
            X[i], tt[i] = CS.build_fast(store, r, added, None, cut=CUT)
        if str(dev).startswith("cuda"):
            torch.cuda.synchronize()
        t = time.time()
        predict(model, X, tt, dev)
        if str(dev).startswith("cuda"):
            torch.cuda.synchronize()
        dt = time.time() - t
        out[f"prepend_{k}"] = {"reports_per_s": round(len(rows) / dt, 1), "mean_chunks": float(n_real_chunks(tt).mean()), "chunks_per_s": round(float(n_real_chunks(tt).sum()) / dt, 1), "n": len(rows)}
    return out


# ----------------------------------------------------------------------------- Stage 1: self test and pilot
def selftest(a):
    """Checks of NOTES 19.8 that need the real level 1, the call store and the stored ATT+bal weights (CPU). Writes <out>/selftest.json and raises on the first failure."""
    import torch
    from baseline import padtest
    nb = C.setup_nebula(require_patched=True)
    res = {"checks": {}}
    D = load_data(a)
    store, X, tot, ntr = D["store"], D["X"], D["tot"], D["ntr"]
    res["checks"]["e_validation_hash"] = f"{VAL_HASH} asserted in load_data; 67,768 / 7,530; first 512 tokens of all {len(X):,} rows equal the stored BPE-50k rows"
    wp = padtest.find_weights("attbal", 0, None, a.search)
    full = padtest.load_model("attbal", wp, "cpu")                                           # ATT+bal seed 0, eval mode
    TL = build_model_class()
    two = make_model(D["vocab_size"], 0, "warm", wp).eval()
    res["params"] = param_counts(two)
    res["params"]["attbal_full"] = int(sum(p.numel() for p in full.parameters()))
    res["params"]["attbal_head_removed"] = res["params"]["attbal_full"] - res["params"]["level1"]
    # (a) K = 1: a report of <= 512 tokens
    short = [int(r) for r in range(ntr) if tot[r] <= CHUNK][:64]
    assert len(short) == 64
    xs = torch.from_numpy(X[short].astype(np.int64))
    nch = torch.from_numpy(n_real_chunks(tot[short]))
    assert int(nch.max()) == 1
    with torch.no_grad():
        ref = full.core(xs[:, :CHUNK])
        vec, mask = two.chunk_vectors(xs, nch)
        d_a = float((vec[:, 0] - ref).abs().max())
        assert mask.shape == (64, 1) and bool(mask.all())
        # level 2 sees one real chunk; adding 7 masked padding chunks (garbage content) does not change the logit
        z1 = two(xs, nch)
        x7 = xs.clone()
        x7[:, CHUNK:] = torch.randint(1, 50000, x7[:, CHUNK:].shape)
        d_mask = float((two(x7, nch) - z1).abs().max())
    assert d_a == 0.0 or d_a < 1e-5, d_a
    assert d_mask == 0.0, d_mask
    res["checks"]["a_K1"] = {"max_abs_diff_chunk_vector_vs_ATTbal_core": d_a, "max_abs_diff_logit_when_masked_chunks_change": d_mask, "n_reports": 64}
    # (b) a 1,000-token report: chunk 2 is level 1 on its own; positions restart at 0; independence of the batch
    mid = [int(r) for r in range(ntr) if 900 <= tot[r] <= 1000][:32]
    xm = torch.from_numpy(X[mid].astype(np.int64))
    nm = torch.from_numpy(n_real_chunks(tot[mid]))
    assert int(nm.min()) == int(nm.max()) == 2
    with torch.no_grad():
        vm, _ = two.chunk_vectors(xm, nm)
        second = torch.zeros_like(xm)
        second[:, :CHUNK] = xm[:, CHUNK:2 * CHUNK]
        v2, _ = two.chunk_vectors(second, torch.ones(len(mid), dtype=torch.long))
        d_b1 = float((vm[:, 1] - v2[:, 0]).abs().max())
        z_all = two(xm, nm)
        z_one = torch.cat([two(xm[i:i + 1], nm[i:i + 1]) for i in range(len(mid))])
        d_b2 = float((z_all - z_one).abs().max())
        xg = xm.clone()
        xg[:, 2 * CHUNK:] = torch.randint(1, 50000, xg[:, 2 * CHUNK:].shape)                  # content beyond the real chunks
        d_b3 = float((two(xg, nm) - z_all).abs().max())
    assert d_b1 < 1e-5 and d_b2 < 1e-5 and d_b3 == 0.0, (d_b1, d_b2, d_b3)
    res["checks"]["b_chunk2"] = {"chunk2_vs_same_tokens_as_first_chunk_of_own_report": d_b1, "logit_alone_vs_in_batch": d_b2, "logit_when_masked_chunks_change": d_b3, "n_reports": len(mid)}
    # (c) an edited report keeps exactly 4,096 tokens and fills 8 chunks
    pool_rows = train_pool_rows(D)
    pos, tk, tt = epoch_edits(D, 0, 1, pool_rows)
    assert tk.shape[1] == CUT and (tt >= 1).all()
    long_ = np.where(tt >= CUT)[0]
    assert len(long_) and (tk[long_][:, -1] > 0).all() and (n_real_chunks(tt[long_]) == MAXK).all()
    res["checks"]["c_cut"] = {"edited_reports": int(len(pos)), "with >= 4096 tokens": int(len(long_)), "all fill 8 chunks": True}
    # (d) the plan of ATT+bal: first 512 tokens of 200 edited reports = inmem_pad edits of the same (seed, epoch, row); build_fast = build_tokens at 4,096
    trn = D["trn"]
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    bad_512 = bad_fast = 0
    for j in range(0, len(pos), max(1, len(pos) // 200)):
        r = int(trn[pos[j]])
        plan = make_pad.plan_train_row(r, 0, 1, store.n_calls(r), pool_n, PAD_STREAM, 0.5)
        t512, total512 = inmem_pad.edit_row(store, r, plan, pool_rows)
        added = [(store, int(pool_rows[pr]), int(c)) for pr, c in plan["draws"]]
        order = make_pad.apply_plan(list(range(store.n_calls(r))), plan, added)
        t4096, total4096 = CS.build_tokens(store, r, order, cut=CUT)
        bad_512 += int(not (np.array_equal(t512, tk[j][:CHUNK]) and total512 == tt[j]))
        bad_fast += int(not (np.array_equal(t4096, tk[j]) and total4096 == tt[j]))
    assert bad_512 == 0 and bad_fast == 0, (bad_512, bad_fast)
    res["checks"]["d_edits"] = {"compared": len(range(0, len(pos), max(1, len(pos) // 200))), "first_512_differs_from_ATTbal_edit": bad_512, "build_fast_differs_from_build_tokens": bad_fast}
    # (f) counts
    assert res["params"]["level1"] > 3_000_000 and res["params"]["level2"] < 100_000
    C.dump_json(res, os.path.join(a.out, "selftest.json"))
    print(json.dumps(res, indent=1), flush=True)
    return res


def pilot(a):
    """Stage 1: self test (CPU), then A (balanced padding) and B (none) for 1 epoch, seed 0, lr 2e-3, on the two GPUs in parallel; no April logits."""
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    selftest(argparse.Namespace(**{**vars(a), "device": "cpu"}))
    procs = []
    for g, (tag, pad) in enumerate([("pilot_A", "balanced"), ("pilot_B", "none")]):
        log = open(os.path.join(a.out, "logs", f"{tag}.log"), "a")
        cmd = [sys.executable, "-m", "baseline.twolevel", "--out", a.out, "--seed", "0", "--epochs", "1", "--lr", "2e-3", "--padding", pad, "--tag", tag, "--device", "cuda", "--no-april", "--throughput", "--force"]
        if a.search:
            cmd += ["--search", a.search]
        procs.append((tag, subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), log))
    bad = []
    for tag, p, log in procs:
        rc = p.wait()
        log.close()
        print(f"{tag} exited with {rc}", flush=True)
        print("".join(open(os.path.join(a.out, "logs", f"{tag}.log")).readlines()[-12:])[-2500:], flush=True)
        if rc:
            bad.append(tag)
    if bad:
        raise SystemExit(f"pilot runs failed: {bad}")


def orchestrate(a):
    """Stage 2: --cells tag:padding:init:lr ... x --seeds, one subprocess per (cell, seed), one per GPU at a time; finished units (seed<k>.json present) are skipped."""
    try:
        import torch
        n_gpu = max(1, torch.cuda.device_count())
    except Exception:
        n_gpu = 1
    jobs = []
    for c in a.cells:
        f_ = c.split(":")
        tag, pad, init, lr = f_[:4]
        extra = [x for kv in (f_[4].split(",") if len(f_) > 4 else []) for x in ("--" + kv.split("=")[0].replace("_", "-"), kv.split("=")[1])]          # e.g. sched=linear,l1_mult=0.25,freeze1_steps=706,ema=0.999
        for s in a.seeds:
            if not os.path.exists(os.path.join(a.out, tag, f"seed{s}.json")):
                jobs.append((tag, pad, init, lr, s, extra))
    os.makedirs(os.path.join(a.out, "logs"), exist_ok=True)
    running, failed, t0 = {}, [], time.time()
    while jobs or running:
        for g in range(n_gpu):
            if g not in running and jobs:
                tag, pad, init, lr, s, extra = jobs.pop(0)
                log = open(os.path.join(a.out, "logs", f"{tag}_seed{s}.log"), "a")
                cmd = [sys.executable, "-m", "baseline.twolevel", "--out", a.out, "--seed", str(s), "--epochs", str(a.epochs), "--lr", lr, "--padding", pad, "--init", init, "--tag", tag, "--device", "cuda", "--search", a.search] + extra
                running[g] = (subprocess.Popen(cmd, env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(g)), stdout=log, stderr=subprocess.STDOUT), f"{tag} seed {s}", log)
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: started {tag} seed {s}", flush=True)
        for g, (p, name, log) in list(running.items()):
            if p.poll() is not None:
                log.close()
                print(f"[{(time.time() - t0) / 60:.1f} min] GPU {g}: {name} exited with {p.returncode}", flush=True)
                if p.returncode:
                    failed.append(name)
                    print("".join(open(log.name).readlines()[-12:])[-1500:], flush=True)
                    for q, _, lg in running.values():                                    # fail fast: a broken unit means a broken recipe, do not burn the rest of the session
                        if q.poll() is None:
                            q.terminate()
                    raise SystemExit(f"run failed: {failed}")
                del running[g]
        time.sleep(5)
    if failed:
        raise SystemExit(f"runs failed: {failed}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", default=None)
    ap.add_argument("--store", default=None, help="call-token store all.npz (default: searched under /kaggle/input)")
    ap.add_argument("--search", default="/kaggle/input", help="where the stored ATT+bal weights (attbal/seed<k>.pt) are searched")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--plan", action="store_true", help="Stage 2: run --cells x --seeds on the available GPUs")
    ap.add_argument("--cells", nargs="*", default=[], help="tag:padding:init:lr, e.g. A_scratch_lr2e-3:balanced:scratch:2e-3")
    ap.add_argument("--seeds", type=int, nargs="*", default=list(range(10)))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--sched", default="const", choices=["const", "linear"], help="learning rate: constant, or linear decay to 0 over all steps of the run (NOTES 20)")
    ap.add_argument("--l1-mult", type=float, default=1.0, help="learning rate of level 1 = this x lr")
    ap.add_argument("--freeze1-steps", type=int, default=0, help="level 1 frozen (no gradient, no dropout) for this many first steps")
    ap.add_argument("--ema", type=float, default=0.0, help="exponential moving average of the weights with this decay (0 = off); evaluated next to the raw weights")
    ap.add_argument("--padding", default="balanced", choices=["balanced", "none"])
    ap.add_argument("--pad-prob", type=float, default=0.5)
    ap.add_argument("--init", default="scratch", choices=["scratch", "warm"])
    ap.add_argument("--tag", default="A_scratch")
    ap.add_argument("--variant", default="bpe50k")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--micro", type=int, default=0, help="reports per forward pass (default 96 = the whole batch; halved automatically on a CUDA OOM)")
    ap.add_argument("--no-april", action="store_true", help="do not score April and do not store weights (pilot)")
    ap.add_argument("--throughput", action="store_true", help="after training: scoring speed on 1,000 validation malware reports with k = 0, 100, 200 prepended calls")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a)
    if a.plan:
        return orchestrate(a)
    return pilot(a) if a.pilot else run(a)


if __name__ == "__main__":
    main()
