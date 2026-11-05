#!/usr/bin/env python
"""
Train and evaluate the two-level Nebula (see model.py).

    prepare   tokenize reports with Nebula's preprocessing -> tokens/offsets/meta
    embed     run the (frozen, pretrained) level-1 Nebula on every chunk once and
              cache the chunk vectors; also stores Nebula's own score on chunk 0
              (= the original Nebula prediction, used as the baseline)
    train     --mode frozen   : train level 2 on the cached vectors (CPU friendly)
              --mode finetune : train both levels end to end from token ids (GPU)

Run from the repository root, e.g.
    python -m hier_nebula.train prepare --dataset speakeasy --data-dir ../hf-git --out ../hier_data/speakeasy
    python -m hier_nebula.train embed   --data ../hier_data/speakeasy
    python -m hier_nebula.train train   --data ../hier_data/speakeasy --mode frozen --max-chunks 8 --out results/hier/frozen_k8
"""
import argparse
import json
import os
import time

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader

from hier_nebula.data import prepare, ChunkDataset, collate, SEQ_LEN
from hier_nebula.model import HierNebula, build_level1


# --------------------------------------------------------------------------- metrics
def metrics(y, score, num_classes=1):
    from sklearn.metrics import roc_auc_score, roc_curve, f1_score, accuracy_score
    y = np.asarray(y)
    if num_classes == 1:
        fpr, tpr, _ = roc_curve(y, score)
        out = {"n": int(len(y)), "auc": float(roc_auc_score(y, score)),
               "f1@0.5": float(f1_score(y, score >= 0.5)), "acc@0.5": float(accuracy_score(y, score >= 0.5))}
        for f in (1e-3, 1e-2, 1e-1):
            out[f"tpr@fpr={f:g}"] = float(tpr[fpr <= f].max()) if (fpr <= f).any() else 0.0
        return out
    pred = score.argmax(1)
    return {"n": int(len(y)), "acc": float(accuracy_score(y, pred)),
            "f1_macro": float(f1_score(y, pred, average="macro")),
            "auc_ovr_macro": float(roc_auc_score(y, score, multi_class="ovr", average="macro",
                                                 labels=list(range(num_classes))))}


def splits(meta, val_frac=0.1, seed=0):
    rng = np.random.default_rng(seed)
    train = np.where(meta.split == "trainset")[0]
    test = np.where(meta.split == "testset")[0]
    perm = rng.permutation(train)
    n_val = int(len(perm) * val_frac)
    return perm[n_val:], perm[:n_val], test


# --------------------------------------------------------------------------- embed
def cmd_embed(a):
    meta = pd.read_csv(os.path.join(a.data, "meta.csv"))
    if meta.dataset.iloc[0] != "speakeasy":
        raise SystemExit("embed uses the released Speakeasy Nebula weights; only valid for --dataset speakeasy")
    torch.set_num_threads(a.threads)
    level1 = build_level1(a.nebula, vocab_size=a.vocab_size, pretrained=True)
    model = HierNebula(level1, max_chunks=a.max_chunks).eval()
    ds = ChunkDataset(a.data, np.arange(len(meta)), max_chunks=a.max_chunks)
    dl = DataLoader(ds, batch_size=a.batch_size, collate_fn=collate, num_workers=1)
    vecs = np.zeros((len(meta), a.max_chunks, 64), dtype=np.float16)
    nebula_score = np.zeros(len(meta), dtype=np.float32)
    t0 = time.time()
    with torch.no_grad():
        for i, (ids, mask, _, rows) in enumerate(dl):
            v = model.encode_chunks(ids, mask)                      # [B, K, 64]
            vecs[rows.numpy(), :v.shape[1]] = v.numpy().astype(np.float16)
            nebula_score[rows.numpy()] = torch.sigmoid(model.nebula_logit(v[:, 0])).squeeze(-1).numpy()
            if i % 100 == 0:
                print(f"{(i+1)*a.batch_size}/{len(meta)} embedded, {(time.time()-t0)/60:.1f} min", flush=True)
    np.save(os.path.join(a.data, "chunk_vecs_pretrained.npy"), vecs)
    np.save(os.path.join(a.data, "nebula_score_chunk0.npy"), nebula_score)
    print(f"done in {(time.time()-t0)/60:.1f} min")


# --------------------------------------------------------------------------- train
def run_epoch(model, batches, num_classes, opt=None):
    loss_fn = nn.BCEWithLogitsLoss() if num_classes == 1 else nn.CrossEntropyLoss()
    train = opt is not None
    model.train(train)
    ys, ss, losses = [], [], []
    for x, mask, y in batches:
        with torch.set_grad_enabled(train):
            logits = model(x, mask) if x.dtype == torch.long else model.classify(x, mask)
            loss = loss_fn(logits.squeeze(-1), y.float()) if num_classes == 1 else loss_fn(logits, y)
        if train:
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        losses.append(loss.item())
        ys.append(y.numpy())
        s = torch.sigmoid(logits.squeeze(-1)) if num_classes == 1 else torch.softmax(logits, -1)
        ss.append(s.detach().numpy())
    return float(np.mean(losses)), np.concatenate(ys), np.concatenate(ss)


def cached_batches(vecs, n_chunks, labels, idx, bs, max_chunks, shuffle, rng):
    idx = rng.permutation(idx) if shuffle else idx
    for s in range(0, len(idx), bs):
        b = idx[s:s + bs]
        k = int(min(max_chunks, n_chunks[b].max()))
        x = torch.from_numpy(vecs[b, :k].astype(np.float32))
        mask = torch.from_numpy(np.arange(k)[None, :] < np.minimum(n_chunks[b], max_chunks)[:, None])
        x[~mask] = 0
        yield x, mask, torch.from_numpy(labels[b])


def token_batches(ds, idx_map, bs, shuffle, rng, workers):
    sub = torch.utils.data.Subset(ds, rng.permutation(idx_map) if shuffle else idx_map)
    for ids, mask, y, _ in DataLoader(sub, batch_size=bs, collate_fn=collate, num_workers=workers):
        yield ids, mask, y


def cmd_train(a):
    torch.manual_seed(a.seed); rng = np.random.default_rng(a.seed)
    torch.set_num_threads(a.threads)
    meta = pd.read_csv(os.path.join(a.data, "meta.csv"))
    label_col = "label" if a.task == "binary" else "label_family"
    labels = meta[label_col].values.astype(np.int64)
    num_classes = 1 if a.task == "binary" else int(labels.max()) + 1
    if meta.dataset.iloc[0] != "speakeasy" and not a.scratch:
        raise SystemExit("The released Nebula weights were trained on Speakeasy with the Speakeasy tokenizer; "
                         "for other datasets use --scratch --mode finetune.")
    tr, va, te = splits(meta, seed=a.seed)
    if a.limit:
        # random subsets (the rows are stored folder by folder, so a plain slice would be one class)
        tr = tr[:a.limit]
        va = rng.permutation(va)[:max(1, a.limit // 10)]
        te = rng.permutation(te)[:max(1, a.limit // 5)]
    level1 = build_level1(a.nebula, vocab_size=a.vocab_size, pretrained=not a.scratch)
    model = HierNebula(level1, max_chunks=a.max_chunks, num_classes=num_classes, n_layers=a.layers,
                       dropout=a.dropout)
    n_chunks = meta.n_chunks.values

    if a.mode == "frozen":
        model.freeze_level1(True)
        vecs = np.load(os.path.join(a.data, "chunk_vecs_pretrained.npy"), mmap_mode="r")
        vecs = np.asarray(vecs)
        make = lambda idx, shuffle: cached_batches(vecs, n_chunks, labels, idx, a.batch_size, a.max_chunks, shuffle, rng)
    else:
        ds = ChunkDataset(a.data, np.arange(len(meta)), label_col=label_col, max_chunks=a.max_chunks)
        make = lambda idx, shuffle: token_batches(ds, idx, a.batch_size, shuffle, rng, a.workers)

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=a.weight_decay)
    print(f"mode={a.mode} task={a.task} K={a.max_chunks} train={len(tr)} val={len(va)} test={len(te)} "
          f"trainable params={sum(p.numel() for p in params):,}", flush=True)
    os.makedirs(a.out, exist_ok=True)
    key = "auc" if num_classes == 1 else "f1_macro"
    best, history = -1, []
    for ep in range(1, a.epochs + 1):
        t0 = time.time()
        tl, _, _ = run_epoch(model, make(tr, True), num_classes, opt)
        vl, vy, vs = run_epoch(model, make(va, False), num_classes)
        vm = metrics(vy, vs, num_classes)
        history.append({"epoch": ep, "train_loss": tl, "val_loss": vl, **{f"val_{k}": v for k, v in vm.items()}})
        print(f"epoch {ep}: train loss {tl:.4f} val loss {vl:.4f} val {key} {vm[key]:.4f} ({time.time()-t0:.0f}s)", flush=True)
        if vm[key] > best:
            best = vm[key]
            torch.save(model.state_dict(), os.path.join(a.out, "best.pt"))
    model.load_state_dict(torch.load(os.path.join(a.out, "best.pt"), weights_only=True))
    _, ty, ts = run_epoch(model, make(te, False), num_classes)
    result = {"args": vars(a), "test": metrics(ty, ts, num_classes), "history": history}
    if a.mode == "frozen" and num_classes == 1 and os.path.exists(os.path.join(a.data, "nebula_score_chunk0.npy")):
        base = np.load(os.path.join(a.data, "nebula_score_chunk0.npy"))
        result["test_nebula_baseline"] = metrics(labels[te], base[te], 1)
    pd.DataFrame({"row": te, "label": ty, **({"score": ts} if num_classes == 1 else
                                              {f"p{c}": ts[:, c] for c in range(num_classes)})}
                 ).to_csv(os.path.join(a.out, "test_scores.csv"), index=False)
    with open(os.path.join(a.out, "result.json"), "w") as fh:
        json.dump(result, fh, indent=2, default=str)
    print("TEST", json.dumps(result["test"]))
    if "test_nebula_baseline" in result:
        print("NEBULA BASELINE (first 512 tokens)", json.dumps(result["test_nebula_baseline"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"))
    ap.add_argument("--threads", type=int, default=os.cpu_count())
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--dataset", choices=["speakeasy", "avast"], required=True)
    p.add_argument("--data-dir", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--tok-dir", default="results/avast/tokenizer")
    p.add_argument("--max-chunks", type=int, default=8)
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p.add_argument("--limit", type=int, default=0)
    p = sub.add_parser("embed")
    p.add_argument("--data", required=True)
    p.add_argument("--max-chunks", type=int, default=8)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--vocab-size", type=int, default=50001)
    p = sub.add_parser("train")
    p.add_argument("--data", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--mode", choices=["frozen", "finetune"], default="frozen")
    p.add_argument("--task", choices=["binary", "multiclass"], default="binary")
    p.add_argument("--max-chunks", type=int, default=8)
    p.add_argument("--layers", type=int, default=2)
    p.add_argument("--dropout", type=float, default=0.1)
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=256)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--weight-decay", type=float, default=1e-2)
    p.add_argument("--vocab-size", type=int, default=50001)
    p.add_argument("--scratch", action="store_true", help="random level-1 init (required for Avast: no released Avast model)")
    p.add_argument("--workers", type=int, default=2)
    p.add_argument("--limit", type=int, default=0, help="small subset for a smoke test")
    p.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "prepare":
        prepare(a.dataset, a.data_dir, a.out, a.nebula, a.max_chunks, a.workers, a.limit, tok_dir=a.tok_dir)
    elif a.cmd == "embed":
        cmd_embed(a)
    else:
        cmd_train(a)


if __name__ == "__main__":
    main()
