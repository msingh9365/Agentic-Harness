"""
Shared helpers for analyze_signal.py (REPORT.md section 10).

Everything that touches a report goes through Nebula's own preprocessing
(measure_lengths.Nebula: filter_and_normalize_report() + the released BPE
tokenizer). Released Nebula is hier_nebula.model.build_level1(..., pretrained=True).
"""
import json
import os
import re

import numpy as np
import pandas as pd

R = "results/signal"
WORK = "../hier_data/signal"          # large intermediate files (not committed)
SEQ_LEN = 512
WINDOW = 8
FAMILIES = ["backdoor", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan"]
HEX = re.compile(r"^0x[0-9a-fA-F]+$")


def short_lower(name):
    """API name without its DLL, lower-case (kernel32.GetProcAddress -> getprocaddress)."""
    return str(name).split(".")[-1].lower()


def hex_value(v):
    """int value of a '0x..' string, else None."""
    if isinstance(v, str) and HEX.match(v):
        return int(v, 16)
    return None


# --------------------------------------------------------------------------- metrics
def threshold(y, s, fpr):
    """Same convention as analyze_misses.threshold(): flagged = score > thr, thr = the
    (floor(fpr * n_benign) + 1)-th highest benign score."""
    neg = np.sort(np.asarray(s)[np.asarray(y) == 0])[::-1]
    k = int(np.floor(fpr * len(neg)))
    return neg[k] if k < len(neg) else -np.inf


def auc(y, s):
    from sklearn.metrics import roc_auc_score
    y = np.asarray(y)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def evaluate(y, s, fam=None, thr=None):
    """AUC, TPR at 1% and 0.1% FPR (thresholds from the benign scores of this set unless
    thr={0.01: t1, 0.001: t01} is given), with raw counts, and per-family TPR at 1% FPR."""
    y, s = np.asarray(y), np.asarray(s, dtype=np.float64)
    out = {"n": len(y), "n_mal": int((y == 1).sum()), "n_ben": int((y == 0).sum()), "auc": auc(y, s)}
    for f, tag in [(0.01, "1"), (0.001, "01")]:
        t = thr[f] if thr is not None else threshold(y, s, f)
        flag = s > t
        out[f"thr{tag}"] = float(t)
        out[f"tp{tag}"] = int((flag & (y == 1)).sum())
        out[f"fp{tag}"] = int((flag & (y == 0)).sum())
        out[f"tpr{tag}"] = out[f"tp{tag}"] / max(1, out["n_mal"])
    if fam is not None:
        fam = np.asarray(fam)
        flag = s > out["thr1"]
        for f in FAMILIES:
            m = fam == f
            out[f"fam_{f}"] = flag[m].mean() if m.any() else float("nan")
            out[f"famn_{f}"] = int(m.sum())
    return out


# --------------------------------------------------------------------------- formatting
def pct(x, d=1):
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100 * x:.{d}f}%"


def cnt(a, b, d=1):
    return f"{pct(a / b if b else float('nan'), d)} ({int(a):,}/{int(b):,})"


def mean_range(vals, fmt):
    vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
    if not vals:
        return "—"
    if len(vals) == 1:
        return fmt(vals[0])
    return f"{fmt(np.mean(vals))} [{fmt(min(vals))}–{fmt(max(vals))}]"


def f4(x):
    return "—" if isinstance(x, float) and np.isnan(x) else f"{x:.4f}"


def md_table(df):
    cols = list(df.columns)
    out = "| " + " | ".join(map(str, cols)) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows():
        out += "| " + " | ".join(str(r[x]) for x in cols) + " |\n"
    return out


def write_part(name, text):
    """Each analysis writes results/signal/parts/<name>.md; `tables` joins them."""
    os.makedirs(os.path.join(R, "parts"), exist_ok=True)
    with open(os.path.join(R, "parts", f"{name}.md"), "w") as fh:
        fh.write(text)


def save_scores(name, rows, labels, scores, seeds):
    os.makedirs(os.path.join(R, "scores"), exist_ok=True)
    pd.DataFrame({"row": np.asarray(rows), "label": np.asarray(labels),
                  "score": np.asarray(scores, dtype=np.float64), "seed": np.asarray(seeds)}).to_csv(
        os.path.join(R, "scores", f"{name}.csv"), index=False, float_format="%.8g")


# --------------------------------------------------------------------------- data
def load_meta():
    """meta.csv + reports.csv (same order, checked) + the val split."""
    meta = pd.read_csv("results/hier/data/meta.csv")
    rep = pd.read_csv("results/misses/reports.csv", usecols=["split", "sample_id", "label", "main_error", "hash_report",
                                                              "hash_apis", "n_calls"])
    assert len(meta) == len(rep) == 92700
    assert (meta.id.values == rep.sample_id.values).all() and (meta.split.values == rep.split.values).all()
    assert (meta.label.values == rep.label.values).all()
    meta["main_error"] = rep.main_error.fillna("none").values
    meta["hash_apis"] = rep.hash_apis.values
    meta["hash_report"] = rep.hash_report.values
    meta["row"] = np.arange(len(meta))
    p = os.path.join(R, "val_split.csv")
    if os.path.exists(p):
        vs = pd.read_csv(p)
        assert (vs.row.values == meta.row.values).all()
        meta["side"] = vs.side.values
    meta["nebula"] = np.load("results/hier/data/nebula_score_chunk0.npy").astype(np.float64)
    return meta


def load_features():
    f = pd.read_csv(os.path.join(R, "reports.csv"))
    assert len(f) == 92700 and (f.row.values == np.arange(92700)).all()
    return f


class Seqs:
    """API-name sequences (short, lower-case) as int codes, from `collect`."""

    def __init__(self):
        self.codes = np.load(os.path.join(WORK, "names_codes.npy"))
        self.off = np.load(os.path.join(WORK, "names_off.npy"))
        self.vocab = json.load(open(os.path.join(WORK, "names_vocab.json")))

    def get(self, i):
        return self.codes[self.off[i]:self.off[i + 1]]


class Reps:
    """Nebula-filtered reports (orjson), from `collect`."""

    def __init__(self):
        self.off = np.load(os.path.join(WORK, "reps_off.npy"))
        self.fh = None

    def get(self, i):
        import orjson
        if self.fh is None:
            self.fh = open(os.path.join(WORK, "reps.bin"), "rb")
        self.fh.seek(self.off[i])
        return orjson.loads(self.fh.read(self.off[i + 1] - self.off[i]))


# --------------------------------------------------------------------------- released Nebula
def load_nebula(nebula_root="../nebula"):
    import torch
    from hier_nebula.model import build_level1
    m = build_level1(nebula_root, vocab_size=50001, pretrained=True).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    return m


def nebula_scores(model, ids, bs=512):
    """ids: int array [N, 512] -> sigmoid(level1(ids)) (released Nebula's prediction)."""
    import torch
    out = np.zeros(len(ids), dtype=np.float64)
    with torch.no_grad():
        for a in range(0, len(ids), bs):
            x = torch.from_numpy(np.asarray(ids[a:a + bs], dtype=np.int64))
            out[a:a + bs] = torch.sigmoid(model(x)).squeeze(-1).double().numpy()
    return out


def forward_from_embedding(model, emb):
    """Released Nebula from the output of its embedding layer (model.encoder(x), before the
    * sqrt(d_model) scaling and the positional encoding). Same ops as
    TransformerEncoderChunks.core() + classifier_head; checked against model(x)."""
    import math
    import torch
    chunks = torch.split(emb, model.chunk_size, dim=1)
    outs = []
    for c in chunks:
        c = model.pos_encoder(c * math.sqrt(model.d_model))
        outs.append(model.transformer_encoder(c))
    x = torch.cat(outs, dim=1)
    x = model.pooling(x)
    return model.classifier_head(x)
