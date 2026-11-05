"""
Turn reports into Nebula token ids and serve them as [K, 512] chunk tensors.

Stored format (in --out, outside the repo):
    tokens.npy   uint16, all samples' token ids concatenated (first max_chunks*512 per sample)
    offsets.npy  int64 [N+1], sample i is tokens[offsets[i]:offsets[i+1]]
    meta.csv     one row per sample: id, split, family, label columns, n_tokens_full
"""
import math
import os
import time
from multiprocessing import Pool

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset

SEQ_LEN = 512

# Nebula's multiclass map (nebula/constants.py SPEAKEASY_LABELMAP); syswow64 is benign like clean
SPEAKEASY_FAMILY_TO_ID = {"clean": 0, "windows_syswow64": 0, "backdoor": 1, "coinminer": 2, "dropper": 3,
                          "keylogger": 4, "ransomware": 5, "rat": 6, "trojan": 7}

_W = {}


def _init_speakeasy(nebula_root):
    from measure_lengths import Nebula
    _W["nb"] = Nebula(nebula_root)


def _tok_speakeasy(item):
    import orjson
    from measure_lengths import entry_points_of
    split, folder, name, path, keep = item
    nb = _W["nb"]
    with open(path, "rb") as fh:
        rep = nb.report(entry_points_of(orjson.loads(fh.read())))
    ids = np.asarray(nb.ids(rep) if rep else [], dtype=np.uint16)
    fam = folder.replace("report_", "")
    return dict(id=os.path.splitext(name)[0], split=split, family=fam,
                label=int(folder not in ("report_clean", "report_windows_syswow64")),
                label_family=SPEAKEASY_FAMILY_TO_ID[fam], n_tokens_full=len(ids)), ids[:keep]


def _init_avast(nebula_root, tok_dir):
    from measure_avast import bootstrap_nebula, make_tokenizer
    _W["tok"] = make_tokenizer(bootstrap_nebula(nebula_root), tok_dir, "A")


def _tok_avast(item):
    from measure_avast import record, read_summary
    sha, family, split, path, keep, fam_id = item
    ids = np.asarray(_W["tok"].encode(record(read_summary(path), "A"), pad=False)[0], dtype=np.uint16)
    return dict(id=sha, split=split, family=family, label=fam_id, label_family=fam_id,
                n_tokens_full=len(ids)), ids[:keep]


def prepare(dataset, data_dir, out, nebula_root, max_chunks=8, workers=4, limit=0, seed=0, tok_dir=None):
    keep = max_chunks * SEQ_LEN
    if dataset == "speakeasy":
        from measure_lengths import list_files
        items = [(*f, keep) for f in list_files(data_dir) if f[2].endswith(".json")]
        init, initargs, fn = _init_speakeasy, (nebula_root,), _tok_speakeasy
    elif dataset == "avast":
        from measure_avast import load_labels
        L = load_labels(data_dir)
        fams = {f: i for i, f in enumerate(sorted(L.classification_family.unique()))}
        items = [(r.sha256, r.classification_family, r.split,
                  os.path.join(data_dir, "public_small_reports", r.sha256 + ".json"), keep, fams[r.classification_family])
                 for r in L.itertuples()]
        init, initargs, fn = _init_avast, (nebula_root, tok_dir), _tok_avast
    else:
        raise ValueError(dataset)
    if limit:
        rng = np.random.default_rng(seed)
        items = [items[i] for i in rng.permutation(len(items))[:limit]]
    os.makedirs(out, exist_ok=True)
    metas, arrays = [], []
    t0 = time.time()
    with Pool(workers, initializer=init, initargs=initargs) as pool:
        for i, (m, a) in enumerate(pool.imap(fn, items, chunksize=16), 1):   # imap keeps the order
            metas.append(m); arrays.append(a)
            if i % 10000 == 0 or i == len(items):
                print(f"{i}/{len(items)} tokenized, {(time.time()-t0)/60:.1f} min", flush=True)
    offsets = np.zeros(len(arrays) + 1, dtype=np.int64)
    offsets[1:] = np.cumsum([len(a) for a in arrays])
    np.save(os.path.join(out, "tokens.npy"), np.concatenate(arrays) if arrays else np.zeros(0, np.uint16))
    np.save(os.path.join(out, "offsets.npy"), offsets)
    meta = pd.DataFrame(metas)
    meta["dataset"] = dataset
    meta["n_chunks"] = np.maximum(1, np.ceil(np.minimum(meta.n_tokens_full, keep) / SEQ_LEN)).astype(int)
    meta.to_csv(os.path.join(out, "meta.csv"), index=False)
    print(f"wrote {len(meta)} samples to {out}")
    return meta


class ChunkDataset(Dataset):
    """Serves (ids [n_chunks, 512] int64, label) for the given row indices."""

    def __init__(self, data_dir, indices, label_col="label", max_chunks=8):
        self.tokens = np.load(os.path.join(data_dir, "tokens.npy"), mmap_mode="r")
        self.offsets = np.load(os.path.join(data_dir, "offsets.npy"))
        self.meta = pd.read_csv(os.path.join(data_dir, "meta.csv"))
        self.indices = np.asarray(indices)
        self.labels = self.meta[label_col].values
        self.max_chunks = max_chunks

    def __len__(self):
        return len(self.indices)

    def chunks(self, i):
        t = np.asarray(self.tokens[self.offsets[i]:self.offsets[i + 1]], dtype=np.int64)
        t = t[:self.max_chunks * SEQ_LEN]
        k = max(1, math.ceil(len(t) / SEQ_LEN))
        out = np.zeros((k, SEQ_LEN), dtype=np.int64)          # pad id 0, as Nebula's pad_sequence
        out.reshape(-1)[:len(t)] = t
        return torch.from_numpy(out)

    def __getitem__(self, j):
        i = self.indices[j]
        return self.chunks(i), int(self.labels[i]), i


def collate(batch):
    """-> ids [B, K, 512], mask [B, K], labels [B], row indices [B]; K = most chunks in the batch."""
    K = max(x[0].shape[0] for x in batch)
    ids = torch.zeros(len(batch), K, SEQ_LEN, dtype=torch.long)
    mask = torch.zeros(len(batch), K, dtype=torch.bool)
    for b, (c, _, _) in enumerate(batch):
        ids[b, :c.shape[0]] = c
        mask[b, :c.shape[0]] = True
    labels = torch.tensor([x[1] for x in batch])
    rows = torch.tensor([x[2] for x in batch])
    return ids, mask, labels, rows
