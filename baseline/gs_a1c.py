"""
ITEM A1c (NOTES 30.2 / 30.2a; CPU kernel; JANUARY ONLY, no April report is filtered or read): the path-invariant rule, counted and tested with a bag-of-words logistic regression on the January grouped fold 9.   (OURS; the
authors' functions do the filtering and the cleaning)

    python -m baseline.gs_a1c --out /kaggle/working/out [--limit N]

1. the filtered January reports (the train folder, 75,298; labels asserted equal to the published ones), fold 9 split (hash asserted: 66,580 training, 8,718 validation);
2. document frequencies of path components (stems and extensions) on the TRAINING part only; the rule of NOTES 30.2a (components with fewer than 50 training reports -> `zzrnd` (stem) / `zzext` (extension));
3. counts: reports with >= 1 replacement, replacements per report, words changed, vocabulary (words with document frequency >= 5 in the training part) with and without the rule, placeholder words that already occur in the text without the rule;
4. bag of cleaned whitespace words (CountVectorizer, min_df 5 on the training part, log1p) + logistic regression (liblinear, C 0.5, random_state 0), without and with the rule: validation pAUC@1e-2 (normalised), AUC, TPR@1e-2,
   difference (rule minus without) with a cluster 95% interval over the (group, class) cells of the split (1,000 resamples, numpy seed 0);
5. decision.json: GPU training with the rule is planned for later ONLY if the difference in pAUC@1e-2 is >= -0.02.
Output: counts.json, results.json, decision.json, tables.md. No report text is saved.
"""
import argparse
import collections
import json
import os
import pickle
import re
import time

import numpy as np

from baseline import common as C
from baseline import groupsplit as G
from baseline import preprocess as P

PATH = re.compile(r"(?:[a-z]:|%[a-z_]+%)(?:\\{1,4}[^\\\s'\",;)\]}]+)+|\\{2,4}[?.]\\{1,4}[^\\\s'\",;)\]}]+(?:\\{1,4}[^\\\s'\",;)\]}]+)*")
SEP = re.compile(r"(\\+)")
EXT = re.compile(r"[a-z0-9]{1,5}")
MIN_DF = 50
RAND, XEXT = "zzrnd", "zzext"


def components(m):
    """path match -> (parts, prefix_n): parts alternate component / separator, parts[0] is the first component"""
    parts = SEP.split(m)
    comps = parts[0::2]
    prefix_n = 2 if m[0] == "\\" else 1
    return parts, comps, prefix_n


def stem_ext(c):
    if "." in c:
        stem, ext = c.rsplit(".", 1)
        if EXT.fullmatch(ext) and stem:
            return stem, ext
    return c, None


def path_keys(txt):
    keys = set()
    for m in PATH.finditer(txt):
        _, comps, pn = components(m.group(0))
        for c in comps[pn:]:
            if not c:
                continue
            s, e = stem_ext(c)
            keys.add(("s", s))
            if e is not None:
                keys.add(("e", e))
    return keys


def apply_rule(txt, keep):
    """returns (new text, number of replaced components)"""
    n_rep = [0]

    def sub(mo):
        parts, comps, pn = components(mo.group(0))
        out = []
        for i, c in enumerate(comps):
            if i >= pn and c:
                s, e = stem_ext(c)
                s2 = s if ("s", s) in keep else RAND
                e2 = e if (e is None or ("e", e) in keep) else XEXT
                n_rep[0] += int(s2 != s) + int(e2 != e)
                c = s2 if e is None else f"{s2}.{e2}"
            out.append(c)
            if 2 * i + 1 < len(parts):
                out.append(parts[2 * i + 1])
        return "".join(out)
    return PATH.sub(sub, txt), n_rep[0]


def pauc_norm(y, z, f=1e-2):
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(y, z, drop_intermediate=False)
    i = int(np.searchsorted(fpr, f, side="left"))
    t_at = tpr[i] if fpr[i] == f else tpr[i - 1] + (tpr[i] - tpr[i - 1]) * (f - fpr[i - 1]) / (fpr[i] - fpr[i - 1])
    x, yv = np.append(fpr[:i], f), np.append(tpr[:i], t_at)
    return float(np.sum(np.diff(x) * (yv[1:] + yv[:-1]) / 2.0) / f)


def fit_eval(docs_tr, y_tr, docs_va, label):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    t = time.time()
    cvz = CountVectorizer(token_pattern=r"\S+", lowercase=False, min_df=5, dtype=np.float32)
    Xtr = cvz.fit_transform(docs_tr)
    Xva = cvz.transform(docs_va)
    Xtr.data = np.log1p(Xtr.data)
    Xva.data = np.log1p(Xva.data)
    print(f"[{label}] vocabulary {Xtr.shape[1]:,}, train nnz {Xtr.nnz:,} ({(time.time() - t) / 60:.1f} min)", flush=True)
    clf = LogisticRegression(solver="liblinear", C=0.5, max_iter=300, random_state=0).fit(Xtr, y_tr)
    z = clf.decision_function(Xva)
    print(f"[{label}] fitted ({(time.time() - t) / 60:.1f} min)", flush=True)
    return z, Xtr.shape[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--limit", type=int, default=None, help="files per folder (smoke test only)")
    ap.add_argument("--work", default="/tmp/nebula_events")
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    t0 = time.time()
    info = C.setup_nebula(None, require_patched=False)
    data = C.find_data_root()
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(a.work, exist_ok=True)
    cache = os.path.join(a.work, f"train_{a.limit}.pkl")
    if os.path.exists(cache):
        events, ym, _ = pickle.load(open(cache, "rb"))
    else:
        events, ym, _ = P.filter_split(os.path.join(data, "windows_emulation_trainset"), info["nebula_root"], a.workers, a.limit)       # JANUARY only
        pickle.dump((events, ym, None), open(cache, "wb"), protocol=4)
    print(f"{len(events)} January reports filtered ({(time.time() - t0) / 60:.1f} min)", flush=True)
    tokens = C.find_dir_with("labels.npz")
    lab = np.load(os.path.join(tokens, "labels.npz"))
    y_all = lab["y_train"].astype(int)
    sd = C.find_dir_with("split.npz")
    trn, val = G.val_slice(os.path.join(sd, "split.npz"), os.path.join(sd, "split_hash.json"))
    group = np.load(os.path.join(sd, "split.npz"))["group"]
    if a.limit is None:
        assert np.array_equal(lab["ym_train"], ym) and len(events) == 75298 and (len(trn), len(val)) == (66580, 8718)
    else:                                                                       # smoke test: a subsample, placeholder labels
        keep = np.arange(len(events))
        trn, val = trn[trn < len(events)], val[val < len(events)]
        y_all = (np.asarray(ym) != 0).astype(int)
    tok = P.build_tokenizer(P.VARIANTS["bpe50k"], info["nebula_root"])
    low = [str(ev).lower() for ev in events]
    # document frequencies of path components on the training part
    df = collections.Counter()
    for i in trn:
        df.update(path_keys(low[int(i)]))
    keep_set = {k for k, v in df.items() if v >= MIN_DF}
    print(f"components: {len(df):,} distinct, {len(keep_set):,} kept (document frequency >= {MIN_DF}) ({(time.time() - t0) / 60:.1f} min)", flush=True)
    ruled, n_rep = [], np.zeros(len(low), dtype=np.int64)
    for i, txt in enumerate(low):
        new, n = apply_rule(txt, keep_set)
        ruled.append(new)
        n_rep[i] = n
    placeholder_in_orig = int(sum((RAND in t) or (XEXT in t) for t in low))
    clean = lambda texts: [tok.clear_json_event(t) for t in texts]
    docs_orig, docs_rule = clean(low), clean(ruled)
    w_orig, w_rule = np.array([len(d.split()) for d in docs_orig]), np.array([len(d.split()) for d in docs_rule])
    n_ph = np.array([sum(1 for w in d.split() if w in (RAND, XEXT)) for d in docs_rule])
    counts = {"reports": len(events), "reports_with_replacement": int((n_rep > 0).sum()), "share_reports_with_replacement": float((n_rep > 0).mean()), "replacements_total": int(n_rep.sum()), "replacements_per_report_mean": float(n_rep.mean()),
              "replacements_per_report_median": float(np.median(n_rep)), "placeholder_words_in_rule_text": int(n_ph.sum()), "words_total_without_rule": int(w_orig.sum()), "words_total_with_rule": int(w_rule.sum()),
              "words_removed_by_the_rule": int(w_orig.sum() - w_rule.sum()), "share_words_removed": float(1 - w_rule.sum() / w_orig.sum()), "reports_where_placeholder_words_already_occur_without_rule": placeholder_in_orig,
              "distinct_components": len(df), "components_kept": len(keep_set), "min_df": MIN_DF}
    ytr, yva = y_all[trn], y_all[val]
    z0, v0 = fit_eval([docs_orig[int(i)] for i in trn], ytr, [docs_orig[int(i)] for i in val], "without rule")
    z1, v1 = fit_eval([docs_rule[int(i)] for i in trn], ytr, [docs_rule[int(i)] for i in val], "with rule")
    counts["vocabulary_min_df5_without_rule"], counts["vocabulary_min_df5_with_rule"] = int(v0), int(v1)
    from sklearn.metrics import roc_auc_score
    m = {}
    for name, z in (("without_rule", z0), ("with_rule", z1)):
        neg = np.sort(z[yva == 0])[::-1]
        thr = neg[int(np.floor(0.01 * len(neg)))]
        m[name] = {"pauc@1e-2": pauc_norm(yva, z), "pauc@1e-3": pauc_norm(yva, z, 1e-3), "auc": float(roc_auc_score(yva, z)), "tpr@1e-2": float((z[yva == 1] > thr).mean())}
    gv = group[val] if a.limit is None else np.arange(len(val))
    members = {}
    for c in (0, 1):
        idx = np.where(yva == c)[0]
        u, inv = np.unique(gv[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    rng = np.random.default_rng(0)
    dl = []
    for b in range(a.boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        dl.append(pauc_norm(yva[sel], z1[sel]) - pauc_norm(yva[sel], z0[sel]))
    delta = m["with_rule"]["pauc@1e-2"] - m["without_rule"]["pauc@1e-2"]
    lo, hi = np.percentile(dl, [2.5, 97.5])
    dec = {"delta_pauc_rule_minus_without": delta, "cluster_ci95": [float(lo), float(hi)], "threshold": -0.02, "gpu_training_planned_later": bool(delta >= -0.02),
           "rule": "GPU training of a Transformer with the rule is planned for later ONLY if the rule loses at most 2 validation pAUC points (delta >= -0.02); nothing is trained tonight"}
    json.dump(counts, open(os.path.join(a.out, "counts.json"), "w"), indent=1)
    json.dump({"fold": 9, "metrics": m, "n_val": int(len(val)), "n_train": int(len(trn))}, open(os.path.join(a.out, "results.json"), "w"), indent=1)
    json.dump(dec, open(os.path.join(a.out, "decision.json"), "w"), indent=1)
    md = ["### A1c: path-invariant rule, January fold 9 (bag of words + logistic regression; validation only)", "", "| | validation pAUC@1e-2 | pAUC@1e-3 | AUC | TPR@1e-2 |", "|---|---|---|---|---|"]
    for name in ("without_rule", "with_rule"):
        r = m[name]
        md.append(f"| {name.replace('_', ' ')} | {r['pauc@1e-2']:.4f} | {r['pauc@1e-3']:.4f} | {r['auc']:.4f} | {r['tpr@1e-2']:.4f} |")
    md += ["", f"Difference (with rule - without) in pAUC@1e-2: **{100 * delta:+.2f} points**, cluster 95% interval [{100 * lo:+.2f}, {100 * hi:+.2f}]. Decision (planned later only if >= -2 points): **{'GO' if dec['gpu_training_planned_later'] else 'NO GO'}**.", "",
           "Counts: " + json.dumps(counts)]
    open(os.path.join(a.out, "tables.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md), flush=True)
    print(f"done in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
