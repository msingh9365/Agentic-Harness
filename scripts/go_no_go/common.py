"""
Shared code for the go/no-go tests of the two-level Nebula (results/go_no_go.md).

Reuses the existing repository code (nothing is re-implemented):
  - reports / API-name sequences / row index: signal_lib.load_meta, Seqs, Reps   (analyze_signal.py collect)
  - grouped January split:                     results/signal/val_split.csv     (analyze_signal.py split)
  - bag-of-API LightGBM:                       analyze_signal.bag_matrix, fit_lgb, group_weights
  - released Nebula:                           signal_lib.load_nebula / nebula_scores (hier_nebula.model.build_level1)
  - seen / unseen:                             hash_apis of an April report occurs in January (as analyze_signal drift)

Metrics. Threshold (a): from the April benign scores. Threshold (b): from the January-validation benign
scores, applied to April (its real April FPR is reported). Both use the convention of
analyze_misses.threshold(): flagged = score > thr, thr = (floor(fpr * n_benign) + 1)-th highest benign score.
Intervals: bootstrap over April groups (hash_apis), 1,000 resamples, seed 0, paired across models.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from signal_lib import load_meta, Seqs, Reps, load_nebula, nebula_scores  # noqa: E402,F401

OUT = "results/go_no_go"
SCORES = os.path.join(OUT, "scores")
SEEDS = [0, 1, 2]
N_BOOT = 1000
FPRS = [(0.01, "1%"), (0.001, "0.1%")]


def meta_full():
    """meta.csv rows + side (train/val/test) + seen + chunk bucket."""
    meta = load_meta()
    jan = set(meta.hash_apis[meta.split == "trainset"])
    meta["seen"] = meta.hash_apis.isin(jan)
    meta["chunks"] = pd.cut(meta.n_chunks, [0, 1, 3, 8], labels=["1", "2-3", "4-8"]).astype(str)
    return meta


def subsets(test):
    """(name, mask) over the April rows, in report order."""
    return [("all", np.ones(len(test), bool)),
            ("seen", test.seen.values), ("unseen", ~test.seen.values),
            ("1 chunk", (test.chunks == "1").values), ("2-3 chunks", (test.chunks == "2-3").values),
            ("4-8 chunks", (test.chunks == "4-8").values)]


def thr_from(y, s, fpr):
    neg = np.sort(np.asarray(s)[np.asarray(y) == 0])[::-1]
    k = int(np.floor(fpr * len(neg)))
    return neg[k] if k < len(neg) else -np.inf


def save_scores(name, rows, scores_by_seed, part="april"):
    """Long parquet: row, seed, score (one file per model and part)."""
    os.makedirs(SCORES, exist_ok=True)
    df = pd.concat([pd.DataFrame({"row": rows, "seed": sd, "score": np.asarray(s, dtype=np.float64)})
                    for sd, s in scores_by_seed.items()])
    df.to_parquet(os.path.join(SCORES, f"{name}_{part}.parquet"), index=False)


def load_scores(name, part="april"):
    df = pd.read_parquet(os.path.join(SCORES, f"{name}_{part}.parquet"))
    return {sd: g.set_index("row").score for sd, g in df.groupby("seed")}


class Scorer:
    """Weighted metrics for one score vector on the April rows. Weights = group-bootstrap counts."""

    def __init__(self, y, s, thr_b):
        self.y = np.asarray(y).astype(float)
        self.s = np.asarray(s, dtype=np.float64)
        self.u, self.inv = np.unique(self.s, return_inverse=True)       # ascending unique scores
        self.thr_b = thr_b                                                # {fpr: threshold from January val}

    def metrics(self, w, masks):
        """w: per-report weights. Thresholds (a) come from the weighted April benign (all reports).
        Returns {subset: {metric: value}}."""
        U = len(self.u)
        negall = np.bincount(self.inv, w * (1 - self.y), minlength=U)
        N = negall.sum()
        thr_a = {}
        for f, _ in FPRS:
            k = np.floor(f * N)
            cn = np.cumsum(negall[::-1])                                  # benign weight from the top
            j = U - 1 - int(np.argmax(cn > k))                            # bin holding the (k+1)-th benign
            thr_a[f] = self.u[j]
        out = {}
        for name, m in masks:
            wm = w * m
            pos = np.bincount(self.inv, wm * self.y, minlength=U)
            neg = np.bincount(self.inv, wm * (1 - self.y), minlength=U)
            P, Nn = pos.sum(), neg.sum()
            r = {"n": wm.sum(), "n_mal": P}
            r["auc"] = ((pos * (np.cumsum(neg) - neg)).sum() + 0.5 * (pos * neg).sum()) / (P * Nn) if P and Nn else np.nan
            for f, tag in FPRS:
                for kind, t in (("a", thr_a[f]), ("b", self.thr_b[f])):
                    above = self.u > t
                    r[f"tpr{tag}_{kind}"] = pos[above].sum() / P if P else np.nan
                    r[f"fpr{tag}_{kind}"] = neg[above].sum() / Nn if Nn else np.nan
            out[name] = r
        return out


def group_weights_boot(groups, n_boot=N_BOOT, seed=0):
    """Yields per-report weights: groups (hash_apis) drawn with replacement."""
    codes, uniq = pd.factorize(groups)
    G = len(uniq)
    rng = np.random.default_rng(seed)
    for _ in range(n_boot):
        cnt = np.bincount(rng.integers(0, G, G), minlength=G)
        yield cnt[codes].astype(float)


METRIC_COLS = ["auc"] + [f"{m}{tag}_{k}" for _, tag in FPRS for k in "ab" for m in ("tpr", "fpr")]


def evaluate_models(test, models, thr_b, n_boot=N_BOOT, diffs=(), masks=None):
    """models: {name: {seed: April score array in test order}}; thr_b: {name: {seed: {fpr: thr}}}.
    Metric of a model = mean over its seeds. Returns (point table, per-seed table, bootstrap
    percentiles), plus paired differences for (name1, name2) in diffs."""
    y = test.label.values
    masks = subsets(test) if masks is None else masks
    scorers = {m: {sd: Scorer(y, s, thr_b[m][sd]) for sd, s in d.items()} for m, d in models.items()}

    def all_metrics(w):
        res = {}
        for m, d in scorers.items():
            per = [sc.metrics(w, masks) for sc in d.values()]
            res[m] = {sub: {k: np.mean([p[sub][k] for p in per]) for k in per[0][sub]} for sub, _ in masks}
            res[m]["_seeds"] = per
        return res

    point = all_metrics(np.ones(len(test)))
    boots = {(m, sub, k): [] for m in models for sub, _ in masks for k in METRIC_COLS}
    dboots = {(a, b, sub, k): [] for a, b in diffs for sub, _ in masks for k in METRIC_COLS}
    for w in group_weights_boot(test.hash_apis.values, n_boot):
        r = all_metrics(w)
        for m in models:
            for sub, _ in masks:
                for k in METRIC_COLS:
                    boots[(m, sub, k)].append(r[m][sub][k])
        for a, b in diffs:
            for sub, _ in masks:
                for k in METRIC_COLS:
                    dboots[(a, b, sub, k)].append(r[a][sub][k] - r[b][sub][k])
    ci = {key: np.nanpercentile(v, [2.5, 97.5]) for key, v in boots.items()}
    dci = {key: np.nanpercentile(v, [2.5, 97.5]) for key, v in dboots.items()}
    return point, ci, dci, masks


def fmt(k, v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:.4f}" if k == "auc" else f"{100 * v:.1f}%"


def fmt_d(k, v):
    return f"{v:+.4f}" if k == "auc" else f"{100 * v:+.1f}"


def md_table(df):
    esc = lambda v: str(v).replace("|", "\\|")
    cols = list(df.columns)
    out = "| " + " | ".join(map(esc, cols)) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows():
        out += "| " + " | ".join(esc(r[c]) for c in cols) + " |\n"
    return out


HEAD = {"auc": "AUC", "tpr1%_a": "TPR@1% (a)", "fpr1%_a": "FPR (a)", "tpr1%_b": "TPR@1% (b)", "fpr1%_b": "April FPR (b)",
        "tpr0.1%_a": "TPR@0.1% (a)", "fpr0.1%_a": "FPR (a) ", "tpr0.1%_b": "TPR@0.1% (b)", "fpr0.1%_b": "April FPR (b) "}


def diff_table(point, dci, masks, diffs):
    rows = []
    for a_, b_ in diffs:
        for sub, _ in masks:
            r = {"difference": f"{a_} − {b_}", "subset": sub}
            for k in METRIC_COLS:
                if k.startswith("fpr"):
                    continue
                lo, hi = dci[(a_, b_, sub, k)]
                r[HEAD[k]] = f"{fmt_d(k, point[a_][sub][k] - point[b_][sub][k])} [{fmt_d(k, lo)}, {fmt_d(k, hi)}]"
            rows.append(r)
    return pd.DataFrame(rows)


def result_tables(point, ci, masks, order, sub_filter=None):
    """Rows = model × subset. Cell = value [95% CI]."""
    rows = []
    for sub, _ in masks:
        if sub_filter and sub not in sub_filter:
            continue
        for m in order:
            r = {"subset": sub, "model": m, "n (malware)": f"{point[m][sub]['n']:,.0f} ({point[m][sub]['n_mal']:,.0f})"}
            for k in METRIC_COLS:
                lo, hi = ci[(m, sub, k)]
                r[HEAD[k]] = f"{fmt(k, point[m][sub][k])} [{fmt(k, lo)}, {fmt(k, hi)}]"
            rows.append(r)
    return pd.DataFrame(rows)


def seed_spread(point, masks, models, sub="all"):
    rows = []
    for m in models:
        per = point[m]["_seeds"]
        if len(per) < 2:
            continue
        r = {"model": m}
        for k in METRIC_COLS:
            v = [p[sub][k] for p in per]
            r[HEAD[k]] = " / ".join(fmt(k, x) for x in v)
        rows.append(r)
    return pd.DataFrame(rows)
