#!/usr/bin/env python
"""
Where is the useful signal in Speakeasy reports, and what does Nebula rely on?
(REPORT.md section 10.) CPU only; only small models (logistic regression, LightGBM)
are trained. Released Nebula is used for inference (and gradients) only.

Sub-commands, in the order they are run:
    split      grouped January validation split (by hash_apis)  -> results/signal/val_split.csv
    collect    one pass over the raw reports with Nebula's filter -> results/signal/reports.csv
               + filtered reports / API-name codes / link pairs in ../hier_data/signal/
    baselines  analysis 1: simple baselines vs Nebula
    drift      analysis 5: drift breakdown
    links      analysis 6: data-flow link features
    prefix     analysis 2: prefix curve (LightGBM + released Nebula)
    ablate     analysis 3: ablations of released Nebula
    attrib     analysis 4: integrated gradients on 1,000 April reports
    tables     join results/signal/parts/*.md into results/signal/tables.md

Rules (see REPORT.md §10.1): nothing is chosen on April. Choices use the January
validation split. TPR at a fixed FPR takes its threshold from the benign scores of the
set being reported (REPORT.md §7, §9).
"""
import argparse
import hashlib
import warnings
import json
import os
import platform
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd

from signal_lib import (R, WORK, SEQ_LEN, WINDOW, FAMILIES, short_lower, hex_value, evaluate, threshold, auc,
                        pct, cnt, mean_range, f4, md_table, write_part, save_scores, load_meta, load_features,
                        Seqs, Reps, load_nebula, nebula_scores, sigmoid32, forward_from_embedding)

SEEDS = [0, 1, 2]
warnings.filterwarnings("ignore", category=FutureWarning)     # sklearn 1.9: 'penalty' deprecation notice


def log_versions():
    import importlib
    v = {"python": platform.python_version()}
    for m in ["numpy", "pandas", "sklearn", "lightgbm", "scipy", "torch", "sentencepiece", "orjson"]:
        try:
            v[m] = importlib.import_module(m).__version__
        except Exception:
            v[m] = "not installed"
    print("versions:", json.dumps(v), flush=True)
    return v


# =========================================================================== split
def cmd_split(a):
    from sklearn.model_selection import GroupShuffleSplit
    meta = load_meta()
    jan = meta[meta.split == "trainset"]
    gss = GroupShuffleSplit(n_splits=1, test_size=0.1, random_state=0)
    tr, va = next(gss.split(jan, groups=jan.hash_apis))
    side = np.array(["test"] * len(meta), dtype=object)
    side[jan.index[tr]] = "train"
    side[jan.index[va]] = "val"
    out = pd.DataFrame({"row": meta.row, "id": meta.id, "split": meta.split, "label": meta.label,
                        "hash_apis": meta.hash_apis, "side": side})
    os.makedirs(R, exist_ok=True)
    out.to_csv(os.path.join(R, "val_split.csv"), index=False)
    assert not set(out[out.side == "train"].hash_apis) & set(out[out.side == "val"].hash_apis)
    rows = []
    for s in ["train", "val", "test"]:
        d = out[out.side == s]
        g = d.groupby("hash_apis").size()
        rows.append({"side": s, "groups (hash_apis)": f"{len(g):,}", "reports": f"{len(d):,}",
                     "malware": cnt(d.label.sum(), len(d)), "largest group": f"{g.max():,}",
                     "groups of 1 report": f"{(g == 1).sum():,}"})
        print(rows[-1], flush=True)
    seen = out[out.side == "test"].hash_apis.isin(set(out[out.split == "trainset"].hash_apis))
    txt = ("### 0. Validation split (January, grouped by API-name sequence)\n\n"
           "`GroupShuffleSplit(test_size=0.1, random_state=0)` over the distinct `hash_apis` values of the January "
           "reports: 10% of the groups go to validation. `test` is April.\n\n" + md_table(pd.DataFrame(rows)) +
           f"\nApril reports whose API-name sequence also occurs in January: {cnt(seen.sum(), len(seen))}.\n")
    write_part("a0_split", txt)


# =========================================================================== collect
_NB = None


def _init_collect(nebula):
    global _NB
    from measure_lengths import Nebula
    _NB = Nebula(nebula)


def _collect(item):
    import orjson
    from measure_lengths import entry_points_of
    from measure_links import call_positions, find_links
    i, path = item
    with open(path, "rb") as fh:
        eps = entry_points_of(orjson.loads(fh.read()))
    rep = _NB.report(eps)
    assert rep, path                                  # no report is dropped by Nebula's filter (REPORT.md §1.3)
    blob = orjson.dumps(rep)
    assert str(orjson.loads(blob)) == str(rep)        # the stored report gives the same tokenizer input
    calls = rep.get("apis") or []
    full = [c["api_name"] for c in calls]
    starts, lens, n_tok, fallback, head_len = call_positions(_NB, rep)
    chunk = starts // SEQ_LEN
    links = find_links(calls)
    cross = leave0 = 0
    maxcd = maxd = 0
    for p, u in links:
        maxd = max(maxd, u - p)
        if chunk[p] < WINDOW and chunk[u] < WINDOW and chunk[p] != chunk[u]:
            cross += 1
            maxcd = max(maxcd, int(chunk[u] - chunk[p]))
        if chunk[p] == 0 and chunk[u] != 0:
            leave0 += 1
    ends = starts + lens
    ev = Counter()
    for k, tag in [("file_access", "file"), ("registry_access", "reg")]:
        for r in rep.get(k) or []:
            ev[f"ev_{tag}_{r.get('event')}"] += 1
    row = {"row": i, "tokens": n_tok, "head_tokens": head_len, "n_calls": len(calls),
           "n_entry_points": len(eps) if isinstance(eps, list) else 0,
           "n_file": len(rep.get("file_access") or []), "n_reg": len(rep.get("registry_access") or []),
           "n_net": len(rep.get("network_events.traffic") or []),
           "calls_start_in_512": int((starts < SEQ_LEN).sum()) if len(calls) else 0,
           "calls_fit_in_512": int((ends <= SEQ_LEN).sum()) if len(calls) else 0,
           "n_links": len(links), "n_cross_chunk_links": cross, "n_links_leaving_chunk0": leave0,
           "max_link_distance_calls": maxd, "max_chunk_distance": maxcd, "fallback_used": int(fallback),
           "hash_apis": hashlib.sha1("\n".join(full).encode()).hexdigest(), **ev}
    names = [short_lower(n) for n in full]
    return row, blob, names, links


def cmd_collect(a):
    from multiprocessing import Pool
    from measure_lengths import list_files
    log_versions()
    meta = load_meta()
    files = [f for f in list_files(a.data_dir) if f[2].endswith(".json")]
    assert len(files) == len(meta)
    for (split, folder, name, _), (_, m) in zip(files, meta.iterrows()):
        assert split == m.split and os.path.splitext(name)[0] == m.id
    os.makedirs(WORK, exist_ok=True)
    items = [(i, f[3]) for i, f in enumerate(files)]
    vocab, codes, noff = {}, [], [0]
    rows, roff = [], [0]
    pair_rows, pair_p, pair_u, pair_i, pair_j = [], [], [], [], []
    t0 = time.time()
    with open(os.path.join(WORK, "reps.bin"), "wb") as fb, \
            Pool(a.workers, initializer=_init_collect, initargs=(a.nebula,)) as pool:
        for k, (row, blob, names, links) in enumerate(pool.imap(_collect, items, chunksize=8)):
            assert row["row"] == k
            rows.append(row)
            fb.write(blob)
            roff.append(roff[-1] + len(blob))
            c = [vocab.setdefault(n, len(vocab)) for n in names]
            codes.extend(c)
            noff.append(len(codes))
            for p, u in links:
                pair_rows.append(k); pair_p.append(c[p]); pair_u.append(c[u]); pair_i.append(p); pair_j.append(u)
            if (k + 1) % 5000 == 0 or k + 1 == len(items):
                el = time.time() - t0
                print(f"{k + 1}/{len(items)} collected, {el / 60:.1f} min, eta {(len(items) - k - 1) * el / (k + 1) / 60:.1f} min",
                      flush=True)
    np.save(os.path.join(WORK, "reps_off.npy"), np.asarray(roff, dtype=np.int64))
    np.save(os.path.join(WORK, "names_codes.npy"), np.asarray(codes, dtype=np.int32))
    np.save(os.path.join(WORK, "names_off.npy"), np.asarray(noff, dtype=np.int64))
    json.dump(list(vocab), open(os.path.join(WORK, "names_vocab.json"), "w"))
    np.save(os.path.join(WORK, "link_pairs.npy"),
            np.stack([pair_rows, pair_p, pair_u, pair_i, pair_j], 1).astype(np.int32) if pair_rows
            else np.zeros((0, 5), np.int32))
    f = pd.DataFrame(rows).fillna(0)
    evcols = sorted(c for c in f.columns if c.startswith("ev_"))
    f[evcols] = f[evcols].astype(int)
    f = f[[c for c in f.columns if not c.startswith("ev_")] + evcols]

    # ---- checks against the existing results files
    assert (f.hash_apis.values == meta.hash_apis.values).all(), "hash_apis differs from results/misses/reports.csv"
    print("check: hash_apis equals results/misses/reports.csv for all", len(f), "reports")
    assert (f.tokens.values == meta.n_tokens_full.values).all()
    print("check: token counts equal meta.csv n_tokens_full for all reports")
    lk = pd.read_csv("results/links/samples.csv", usecols=["split", "sample_id", "n_links", "n_cross_chunk_links",
                                                            "max_chunk_distance", "n_calls"])
    lk = meta[["split", "id"]].merge(lk, left_on=["split", "id"], right_on=["split", "sample_id"], how="left")
    for c in ["n_links", "n_cross_chunk_links", "max_chunk_distance", "n_calls"]:
        bad = int((lk[c].values != f[c].values).sum())
        print(f"check: {c} equal to results/links/samples.csv: {len(f) - bad}/{len(f)}")
        assert bad == 0
    f = f.drop(columns=["hash_apis"])
    f.to_csv(os.path.join(R, "reports.csv"), index=False)
    print(f"wrote {R}/reports.csv ({len(f)} rows), {len(vocab)} distinct API names, {len(pair_rows):,} links; "
          f"{(time.time() - t0) / 60:.1f} min")


# =========================================================================== features / models
def bag_matrix(seqs, rows, vocab_n, K=None, bigrams=True, keep=None, min_df=20, fit_rows=None):
    """Sparse count matrix of API names (+ consecutive bigrams) for `rows`, using the first K calls.
    Columns: names and bigrams seen in >= min_df reports of `fit_rows` (January train side).
    Returns (X [len(rows), n_cols] csr, keep) where keep = sorted feature codes."""
    import scipy.sparse as sp
    r_idx, f_idx = [], []
    for n, i in enumerate(rows):
        c = seqs.get(i)
        if K is not None:
            c = c[:K]
        c = c.astype(np.int64)
        feats = c
        if bigrams and len(c) > 1:
            feats = np.concatenate([c, vocab_n + c[:-1] * vocab_n + c[1:]])
        r_idx.append(np.full(len(feats), n, dtype=np.int64))
        f_idx.append(feats)
    r_idx = np.concatenate(r_idx) if r_idx else np.zeros(0, np.int64)
    f_idx = np.concatenate(f_idx) if f_idx else np.zeros(0, np.int64)
    if keep is None:
        fit = np.isin(r_idx, np.flatnonzero(np.isin(rows, fit_rows)))
        pairs = np.unique(np.stack([r_idx[fit], f_idx[fit]], 1), axis=0)
        u, df = np.unique(pairs[:, 1], return_counts=True)
        keep = u[df >= min_df]
    col = np.searchsorted(keep, f_idx)
    ok = (col < len(keep)) & (keep[np.minimum(col, len(keep) - 1)] == f_idx)
    X = sp.csr_matrix((np.ones(ok.sum(), dtype=np.float32), (r_idx[ok], col[ok])), shape=(len(rows), len(keep)))
    X.sum_duplicates()
    return X, keep


def feature_names(keep, vocab):
    V = len(vocab)
    return [vocab[k] if k < V else f"{vocab[(k - V) // V]}>{vocab[(k - V) % V]}" for k in keep]


def length_features(F):
    return pd.DataFrame({"log_tokens": np.log1p(F.tokens), "n_calls": F.n_calls, "n_entry_points": F.n_entry_points,
                         "has_file": (F.n_file > 0).astype(int), "has_reg": (F.n_reg > 0).astype(int),
                         "has_net": (F.n_net > 0).astype(int)})


def field_features(F):
    ev = [c for c in F.columns if c.startswith("ev_")]
    return F[["n_file", "n_reg", "n_net"] + ev].astype(np.float32)


def group_weights(meta):
    """Weights for the validation rows (meta.side == 'val', in row order): each API-name sequence
    (hash_apis group) adds up to 1, so one large group cannot dominate a validation metric.
    (The largest validation group holds 2,292 of 9,619 reports.)"""
    h = pd.Series(meta.hash_apis.values[meta.side.values == "val"])
    return (1.0 / h.map(h.value_counts())).values


def wauc(y, s, w):
    from sklearn.metrics import roc_auc_score
    return float(roc_auc_score(y, s, sample_weight=w))


def fit_lr(Xtr, ytr, Xva, yva, wva, Cs=(0.01, 0.1, 1, 10, 100)):
    from sklearn.linear_model import LogisticRegression
    best = None
    for C in Cs:
        m = LogisticRegression(C=C, penalty="l2", solver="liblinear", max_iter=2000)
        m.fit(Xtr, ytr)
        s = m.decision_function(Xva)
        e = {"auc": wauc(yva, s, wva), "plain_auc": auc(yva, s)}
        print(f"    LR C={C}: val AUC group-weighted {e['auc']:.4f} (plain {e['plain_auc']:.4f})", flush=True)
        if best is None or e["auc"] > best[0]:
            best = (e["auc"], C, m)
    print(f"    LR chosen C={best[1]} (val AUC {best[0]:.4f})", flush=True)
    return best[2], best[1]


LGB_PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=63, min_child_samples=20,
                  feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
                  metric="binary_logloss", verbose=-1, num_threads=4, deterministic=True, force_row_wise=True)


def fit_lgb(Xtr, ytr, Xva, yva, wva, seed, max_rounds=3000):
    import lightgbm as lgb
    p = dict(LGB_PARAMS, seed=seed, bagging_seed=seed, feature_fraction_seed=seed, data_random_seed=seed)
    dtr = lgb.Dataset(Xtr, ytr, free_raw_data=False)
    dva = lgb.Dataset(Xva, yva, weight=wva, reference=dtr)      # group-weighted validation log-loss
    m = lgb.train(p, dtr, max_rounds, valid_sets=[dva], callbacks=[lgb.early_stopping(100, verbose=False)])
    return m


def scale_dense(Xtr, *others):
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
    return [(Xtr - mu) / sd] + [(x - mu) / sd for x in others]


def build_sets(meta, F, seqs):
    """Feature matrices for train / val / test rows (all four feature sets of analysis 1)."""
    import scipy.sparse as sp
    from sklearn.feature_extraction.text import TfidfTransformer
    rows = {s: meta.row.values[meta.side == s] for s in ["train", "val", "test"]}
    allrows = np.concatenate([rows["train"], rows["val"], rows["test"]])
    V = len(seqs.vocab)
    Xb, keep = bag_matrix(seqs, allrows, V, bigrams=True, fit_rows=rows["train"])
    uni = keep < V
    n = {s: len(rows[s]) for s in rows}
    cut = np.cumsum([0, n["train"], n["val"], n["test"]])
    part = lambda X, k: X[cut[k]:cut[k + 1]]
    L = length_features(F).values.astype(np.float64)
    FF = np.log1p(field_features(F).values.astype(np.float64))
    sets = {}
    tf_uni = TfidfTransformer(sublinear_tf=True).fit(part(Xb[:, uni], 0))
    tf_big = TfidfTransformer(sublinear_tf=True).fit(part(Xb, 0))
    for name in ["length", "api", "api_bigram", "api_fields"]:
        if name == "length":
            lgbX = [L[r] for r in rows.values()]
            lrX = scale_dense(*lgbX)
        elif name == "api":
            lgbX = [part(Xb[:, uni], k) for k in range(3)]
            lrX = [tf_uni.transform(x) for x in lgbX]
        elif name == "api_bigram":
            lgbX = [part(Xb, k) for k in range(3)]
            lrX = [tf_big.transform(x) for x in lgbX]
        else:
            api = [part(Xb[:, uni], k) for k in range(3)]
            ffr = [FF[r] for r in rows.values()]
            ffs = scale_dense(*ffr)
            lgbX = [sp.hstack([x, sp.csr_matrix(f)]).tocsr() for x, f in zip(api, ffr)]
            lrX = [sp.hstack([tf_uni.transform(x), sp.csr_matrix(f)]).tocsr() for x, f in zip(api, ffs)]
        sets[name] = (lgbX, lrX)
    info = {"n_unigrams": int(uni.sum()), "n_bigrams": int((~uni).sum()), "n_field_features": FF.shape[1]}
    return rows, sets, keep, info


FEATURE_LABEL = {"length": "length only", "api": "bag of API names", "api_bigram": "API names + bigrams",
                 "api_fields": "API names + field counts"}
NEBULA_LIKE = [("released Nebula", "nebula"), ("finetune_k8", "finetune_k8"), ("frozen_k1", "frozen_k1")]


def existing_scores(meta):
    """April scores of released Nebula and the two-level runs, by meta.csv row."""
    test = meta[meta.split == "testset"]
    out = {"nebula": pd.Series(test.nebula.values, index=test.row.values)}
    for run in ["finetune_k8", "frozen_k1"]:
        d = pd.read_csv(f"results/hier/{run}/test_scores.csv")
        assert (meta.label.values[d.row.values] == d.label.values).all()
        out[run] = pd.Series(d.score.values, index=d.row.values)
    for k, s in out.items():
        assert set(s.index) == set(test.row), k
    return out


def result_row(name, evs, extra=None):
    """One table row from a list of evaluate() dicts (one per seed)."""
    e0 = evs[0]
    r = {"model": name, "AUC": mean_range([e["auc"] for e in evs], f4)}
    for tag, lab in [("1", "TPR @1% FPR"), ("01", "TPR @0.1% FPR")]:
        if len(evs) == 1:
            r[lab] = f"{pct(e0['tpr' + tag])} ({e0['tp' + tag]:,}/{e0['n_mal']:,}; FP {e0['fp' + tag]})"
        else:
            r[lab] = (mean_range([e["tpr" + tag] for e in evs], pct) +
                      f" ({np.mean([e['tp' + tag] for e in evs]):,.0f}/{e0['n_mal']:,}; "
                      f"FP {'/'.join(str(e['fp' + tag]) for e in evs)})")
    if extra:
        r.update(extra)
    return r


def family_row(name, evs):
    r = {"model": name}
    for f in FAMILIES:
        r[f"{f} (n={evs[0]['famn_' + f]:,})"] = mean_range([e["fam_" + f] for e in evs], pct)
    return r


def cmd_baselines(a):
    log_versions()
    meta, F, seqs = load_meta(), load_features(), Seqs()
    rows, sets, keep, info = build_sets(meta, F, seqs)
    W = group_weights(meta)
    print("features:", info, flush=True)
    y = {s: meta.label.values[rows[s]] for s in rows}
    fam = meta.family.values[rows["test"]]
    ex = existing_scores(meta)
    table, famtab, valtab = [], [], []
    for name, key in NEBULA_LIKE:
        e = evaluate(y["test"], ex[key].loc[rows["test"]].values, fam)
        table.append(result_row(name, [e], {"seeds": "1 (existing scores)", "val AUC (group-weighted)": "—"}))
        famtab.append(family_row(name, [e]))
    summary = {}
    for fs in ["length", "api", "api_bigram", "api_fields"]:
        lgbX, lrX = sets[fs]
        print(f"== {fs}: train {lgbX[0].shape}", flush=True)
        t0 = time.time()
        m, C = fit_lr(lrX[0], y["train"], lrX[1], y["val"], W)
        s = m.decision_function(lrX[2])
        sv = m.decision_function(lrX[1])
        e = evaluate(y["test"], s, fam)
        ev = {"auc": wauc(y["val"], sv, W)}
        mname = f"lr_{fs}"
        save_scores(mname, rows["test"], y["test"], s, np.zeros(len(s), int))
        save_scores(mname + "_janval", rows["val"], y["val"], sv, np.zeros(len(sv), int))
        table.append(result_row(f"LR, {FEATURE_LABEL[fs]}", [e],
                                {"seeds": f"deterministic (C={C})", "val AUC (group-weighted)": f4(ev["auc"])}))
        famtab.append(family_row(f"LR, {FEATURE_LABEL[fs]}", [e]))
        summary[mname] = {"test": [e], "val": [ev], "C": C}
        print(f"   LR test AUC {e['auc']:.4f} TPR1 {e['tpr1']:.4f} ({time.time() - t0:.0f}s)", flush=True)
        evs, evvs, allsc, allsv, iters = [], [], [], [], []
        for seed in SEEDS:
            t0 = time.time()
            m = fit_lgb(lgbX[0], y["train"], lgbX[1], y["val"], W, seed)
            s = m.predict(lgbX[2], num_iteration=m.best_iteration)
            sv = m.predict(lgbX[1], num_iteration=m.best_iteration)
            evs.append(evaluate(y["test"], s, fam)); evvs.append({"auc": wauc(y["val"], sv, W)})
            allsc.append(s); allsv.append(sv); iters.append(m.best_iteration)
            print(f"   LGBM seed {seed}: best iter {m.best_iteration}, val AUC {evvs[-1]['auc']:.4f}, "
                  f"test AUC {evs[-1]['auc']:.4f} TPR1 {evs[-1]['tpr1']:.4f} ({time.time() - t0:.0f}s)", flush=True)
            if fs == "api_bigram" and seed == 0:
                imp = pd.Series(m.feature_importance("gain"), index=feature_names(keep, seqs.vocab))
                imp.sort_values(ascending=False).head(40).to_csv(os.path.join(R, "lgbm_api_bigram_top_gain.csv"),
                                                                 header=["gain"])
        mname = f"lgbm_{fs}"
        save_scores(mname, np.tile(rows["test"], 3), np.tile(y["test"], 3), np.concatenate(allsc),
                    np.repeat(SEEDS, len(rows["test"])))
        save_scores(mname + "_janval", np.tile(rows["val"], 3), np.tile(y["val"], 3), np.concatenate(allsv),
                    np.repeat(SEEDS, len(rows["val"])))
        table.append(result_row(f"LightGBM, {FEATURE_LABEL[fs]}", evs,
                                {"seeds": f"3 (iters {', '.join(map(str, iters))})",
                                 "val AUC (group-weighted)": mean_range([e["auc"] for e in evvs], f4)}))
        famtab.append(family_row(f"LightGBM, {FEATURE_LABEL[fs]}", evs))
        summary[mname] = {"test": evs, "val": evvs}
    # best baseline of each kind, chosen on validation AUC (used by analyses 5 and 6)
    best = {}
    for kind in ["lr", "lgbm"]:
        cands = [k for k in summary if k.startswith(kind + "_")]
        best[kind] = max(cands, key=lambda k: np.mean([e["auc"] for e in summary[k]["val"]]))
    json.dump({"best": best, "info": info,
               "val_auc": {k: [e["auc"] for e in v["val"]] for k, v in summary.items()},
               "test": {k: v["test"] for k, v in summary.items()}},
              open(os.path.join(R, "baselines.json"), "w"), indent=1, default=float)
    print("best on validation:", best, flush=True)

    # paired bootstrap: released Nebula minus the best LightGBM (seed-mean score)
    s_best = pd.read_csv(os.path.join(R, "scores", f"{best['lgbm']}.csv")).groupby("row").score.mean()
    boot = paired_bootstrap(y["test"], ex["nebula"].loc[rows["test"]].values, s_best.loc[rows["test"]].values)
    imp = pd.read_csv(os.path.join(R, "lgbm_api_bigram_top_gain.csv"))
    txt = ("### 1. Simple baselines vs Nebula (April test set)\n\n"
           f"Features from Nebula's filtered reports. Bag of API names: {info['n_unigrams']:,} names, "
           f"bigrams: {info['n_bigrams']:,} (both kept if seen in ≥ 20 January-train reports); "
           f"field counts: {info['n_field_features']} columns (records per field and per event type). "
           "LR: L2, `liblinear`, TF-IDF (sublinear tf) on the bag features, standardised dense features; C from "
           "{0.01, 0.1, 1, 10, 100} by group-weighted validation AUC. LightGBM: raw counts, fixed parameters, early "
           "stopping (100 rounds) on group-weighted validation log-loss, seeds 0/1/2: mean [min–max]. "
           "*Group-weighted*: each API-name sequence of the validation side counts once in total (weight 1 / group "
           "size), because one sequence covers 2,292 of the 9,619 validation reports. TPR thresholds come from the 8,003 April "
           "benign scores of each model; the 0.1% FPR threshold rests on 8 benign reports. FP = benign reports above "
           "the threshold (one number per seed). Fewer than 80 / 8 means ties at the threshold: a bag model gives "
           "every report with the same API names the same score.\n\n"
           "Why group-weighted: with plain validation AUC, one run (API names + bigrams, seed 2) stopped after 1 tree "
           "(log `signal_baselines_auc_early_stop.log`). With plain validation log-loss, the prefix models of "
           "analysis 2 stopped after 16–48 trees: the 2,292-report group gets an uncertain score on short prefixes and "
           "its loss alone rises after ~20 trees, while the group-weighted loss keeps falling to ~500 trees (checked "
           "on January validation only; logs `signal_baselines_plain_logloss.log`, `signal_prefix_plain_logloss.log`). "
           "All LightGBM and LR choices in this study use the group-weighted validation metrics.\n\n" +
           md_table(pd.DataFrame(table)) +
           f"\nBest on group-weighted January validation AUC: LR = `{best['lr']}`, LightGBM = `{best['lgbm']}`.\n\n"
           "#### 1b. TPR at 1% FPR per family (April)\n\n" + md_table(pd.DataFrame(famtab)) +
           f"\n#### 1c. Released Nebula minus best LightGBM (`{best['lgbm']}`, mean of 3 seeds), paired bootstrap\n\n"
           + md_table(boot) +
           "\n#### 1d. Top 15 LightGBM features by gain (API names + bigrams, seed 0)\n\n" +
           md_table(pd.DataFrame({"feature": imp.iloc[:15, 0], "gain share": [pct(g / imp.gain.sum()) for g in imp.gain[:15]]})) +
           "\n(gain share is relative to the top 40 features.)\n")
    write_part("a1_baselines", txt)
    cmd_tables(a)


def paired_bootstrap(y, s1, s2, n=1000, seed=0):
    """Differences s1 - s2 in AUC and TPR at 1% / 0.1% FPR over resamples of the test set."""
    rng = np.random.default_rng(seed)
    base = [evaluate(y, s1), evaluate(y, s2)]
    d = {k: [] for k in ["auc", "tpr1", "tpr01"]}
    for _ in range(n):
        i = rng.integers(0, len(y), len(y))
        e1, e2 = evaluate(y[i], s1[i]), evaluate(y[i], s2[i])
        for k in d:
            d[k].append(e1[k] - e2[k])
    rows = []
    for k, lab in [("auc", "AUC"), ("tpr1", "TPR @1% FPR"), ("tpr01", "TPR @0.1% FPR")]:
        lo, hi = np.percentile(d[k], [2.5, 97.5])
        diff = base[0][k] - base[1][k]
        f = f4 if k == "auc" else (lambda x: f"{100 * x:+.1f} pp")
        f = (lambda x: f"{x:+.4f}") if k == "auc" else f
        rows.append({"metric": lab, "difference": f(diff), "95% interval": f"[{f(lo)}, {f(hi)}]"})
    return pd.DataFrame(rows)


# =========================================================================== drift (analysis 5)
MIN_CELL = 30


def model_scores(meta, best):
    """{display name: list of pd.Series (one per seed) of April scores by row}."""
    ex = existing_scores(meta)
    out = {"released Nebula": [ex["nebula"]], "finetune_k8": [ex["finetune_k8"]], "frozen_k1": [ex["frozen_k1"]]}
    for kind in ["lr", "lgbm"]:
        d = pd.read_csv(os.path.join(R, "scores", f"{best[kind]}.csv"))
        out[f"{'LR' if kind == 'lr' else 'LightGBM'} `{best[kind]}`"] = [g.set_index("row").score for _, g in d.groupby("seed")]
    return out


def cell_metrics(y, s, thr, m):
    """TPR (global threshold), FPR and AUC inside cell mask m."""
    yy, ss = y[m], s[m]
    nm, nb = int((yy == 1).sum()), int((yy == 0).sum())
    flag = ss > thr
    return {"n": int(m.sum()), "nm": nm, "nb": nb, "tpr": flag[yy == 1].mean() if nm else float("nan"),
            "tp": int(flag[yy == 1].sum()), "fpr": flag[yy == 0].mean() if nb else float("nan"),
            "auc": auc(yy, ss) if nm >= 10 and nb >= 10 else float("nan")}


def drift_table(test, groups, models, metric):
    """groups: list of (label, mask). One row per group, one column per model."""
    y = test.label.values
    rows = []
    for lab, m in groups:
        r = {"cell": lab, "reports (malware / benign)": f"{int(m.sum()):,} ({int(y[m].sum()):,} / {int((y[m] == 0).sum()):,})"}
        for name, series in models.items():
            if m.sum() < MIN_CELL:
                r[name] = "n<30"
                continue
            vals = []
            for s in series:
                sc = s.loc[test.row.values].values
                thr = threshold(y, sc, 0.01)
                vals.append(cell_metrics(y, sc, thr, m)[metric])
            fmt = f4 if metric == "auc" else pct
            r[name] = mean_range(vals, fmt)
        rows.append(r)
    return pd.DataFrame(rows)


def cmd_drift(a):
    from analyze_misses import stop_category
    meta = load_meta()
    best = json.load(open(os.path.join(R, "baselines.json")))["best"]
    models = model_scores(meta, best)
    meta["stop"] = meta.main_error.map(lambda t: stop_category(None if t == "none" else t))
    jan_hashes = set(meta.hash_apis[meta.split == "trainset"])
    meta["seen"] = np.where(meta.hash_apis.isin(jan_hashes), "seen in January", "unseen")
    test = meta[meta.split == "testset"].reset_index(drop=True)
    jan = meta[meta.split == "trainset"]
    stops = ["no error recorded", "max_api_count (500-call cap)", "unsupported API", "invalid memory / CPU fault",
             "emulator internal error"]
    # composition: January vs April
    comp = []
    for st in stops:
        r = {"stop reason": st}
        for nm, d in [("January", jan), ("April", test)]:
            for lab, l in [("malware", 1), ("benign", 0)]:
                dd = d[d.label == l]
                r[f"{nm} {lab}"] = cnt((dd.stop == st).sum(), len(dd))
        comp.append(r)
    seen_comp = []
    other = {1: set(test.hash_apis[test.label == 0]), 0: set(test.hash_apis[test.label == 1])}
    for lab, l in [("malware", 1), ("benign", 0)]:
        dd = test[test.label == l]
        seen_comp.append({"April": lab, "seen in January": cnt((dd.seen != "unseen").sum(), len(dd)),
                          "unseen": cnt((dd.seen == "unseen").sum(), len(dd)),
                          "same API-name sequence also occurs in April with the other label":
                              cnt(dd.hash_apis.isin(other[l]).sum(), len(dd))})
    txt = ("### 5. Drift breakdown (April)\n\n"
           "Thresholds: each model's global April 1% FPR threshold (LightGBM: per seed, then mean [min–max]). "
           "AUC inside a cell needs ≥ 10 reports of each class. Cells with fewer than 30 reports: `n<30`. "
           "Stop reason = `stop_category(main_error)` (REPORT.md §9.4). Seen = the report's API-name "
           "sequence (`hash_apis`) occurs in some January report (train or validation side).\n\n"
           "#### 5a. Composition: stop reasons in January and April\n\n" + md_table(pd.DataFrame(comp)) +
           "\n#### 5b. Composition: April reports whose API-name sequence occurs in January\n\n" +
           md_table(pd.DataFrame(seen_comp)))
    one_way = [("stop reason", [(st, (test.stop == st).values) for st in stops]),
               ("seen / unseen", [(v, (test.seen == v).values) for v in ["seen in January", "unseen"]])]
    k = "c"
    for title, groups in one_way:
        for metric, mlab in [("tpr", "TPR at 1% FPR (malware in the cell)"), ("fpr", "share of benign flagged (FPR)"),
                             ("auc", "AUC inside the cell")]:
            txt += f"\n#### 5{k}. By {title}: {mlab}\n\n" + md_table(drift_table(test, groups, models, metric))
            k = chr(ord(k) + 1)
    # family: TPR (global threshold) and AUC family vs all April benign
    fam_groups = [(f, (test.family == f).values) for f in FAMILIES]
    txt += f"\n#### 5{k}. By family: TPR at 1% FPR\n\n" + md_table(drift_table(test, fam_groups, models, "tpr"))
    k = chr(ord(k) + 1)
    ben = (test.label == 0).values
    fam_auc = drift_table(test, [(f, m | ben) for f, m in fam_groups], models, "auc")
    fam_auc["cell"] = [f"{f} vs all benign" for f in FAMILIES]
    txt += f"\n#### 5{k}. By family: AUC (family vs all 8,003 April benign)\n\n" + md_table(fam_auc)
    k = chr(ord(k) + 1)
    two = [(f"{st} / {sv}", ((test.stop == st) & (test.seen == sv)).values)
           for st in stops for sv in ["seen in January", "unseen"]]
    for metric, mlab in [("tpr", "TPR at 1% FPR"), ("fpr", "share of benign flagged"), ("auc", "AUC")]:
        txt += f"\n#### 5{k}. Stop reason × seen/unseen: {mlab}\n\n" + md_table(drift_table(test, two, models, metric))
        k = chr(ord(k) + 1)
    # in-distribution reference: the baselines on January validation, by stop reason
    ref = []
    va = meta[meta.side == "val"].reset_index(drop=True)
    for kind in ["lr", "lgbm"]:
        d = pd.read_csv(os.path.join(R, "scores", f"{best[kind]}_janval.csv"))
        for st in stops:
            m = (va.stop == st).values
            r = {"model": best[kind], "stop reason": st,
                 "reports (malware / benign)": f"{int(m.sum()):,} ({int(va.label[m].sum()):,} / {int((va.label[m] == 0).sum()):,})"}
            if m.sum() < MIN_CELL:
                r["TPR at 1% FPR"] = r["AUC"] = "n<30"
            else:
                tv, av = [], []
                for _, g in d.groupby("seed"):
                    sc = g.set_index("row").score.loc[va.row.values].values
                    cm = cell_metrics(va.label.values, sc, threshold(va.label.values, sc, 0.01), m)
                    tv.append(cm["tpr"]); av.append(cm["auc"])
                r["TPR at 1% FPR"], r["AUC"] = mean_range(tv, pct), mean_range(av, f4)
            ref.append(r)
    txt += (f"\n#### 5{k}. Reference: the same baselines on January validation, by stop reason\n\n"
            "Threshold from the January-validation benign scores. Released Nebula is not shown: it was "
            "probably trained on these January reports.\n\n" + md_table(pd.DataFrame(ref)))
    write_part("a5_drift", txt)
    cmd_tables(a)


# =========================================================================== links (analysis 6)
def link_features(F, meta, top_pairs=None):
    lp = np.load(os.path.join(WORK, "link_pairs.npy"))
    V = len(Seqs().vocab)
    vocab = json.load(open(os.path.join(WORK, "names_vocab.json")))
    code = lp[:, 1].astype(np.int64) * V + lp[:, 2]
    if top_pairs is None:
        tr = np.isin(lp[:, 0], meta.row.values[meta.side == "train"])
        u, c = np.unique(code[tr], return_counts=True)
        top_pairs = u[np.argsort(-c)][:20]
        top_n = c[np.argsort(-c)][:20]
    X = pd.DataFrame({"n_links": F.n_links, "links_per_call": F.n_links / np.maximum(1, F.n_calls),
                      "n_cross_chunk_links": F.n_cross_chunk_links, "n_links_leaving_chunk0": F.n_links_leaving_chunk0,
                      "max_link_distance_calls": F.max_link_distance_calls, "max_chunk_distance": F.max_chunk_distance})
    names = []
    for p in top_pairs:
        nm = f"{vocab[p // V]}>{vocab[p % V]}"
        names.append(nm)
        m = code == p
        X[f"pair:{nm}"] = np.bincount(lp[m, 0], minlength=len(F))
    return X.astype(np.float32), names, top_n


def cmd_links(a):
    import scipy.sparse as sp
    log_versions()
    meta, F, seqs = load_meta(), load_features(), Seqs()
    LX, pair_names, pair_n = link_features(F, meta)
    print("top 20 pairs (January train):", list(zip(pair_names, pair_n)), flush=True)
    rows, sets, keep, info = build_sets(meta, F, seqs)
    W = group_weights(meta)
    y = {s: meta.label.values[rows[s]] for s in rows}
    fam = meta.family.values[rows["test"]]
    LXs = [LX.values[rows[s]] for s in ["train", "val", "test"]]
    combos = {
        "links only": [LXs[k] for k in range(3)],
        "length only": sets["length"][0],
        "length + links": [np.hstack([sets["length"][0][k], LXs[k]]) for k in range(3)],
        "bag of API names": sets["api"][0],
        "API names + links": [sp.hstack([sets["api"][0][k], sp.csr_matrix(LXs[k])]).tocsr() for k in range(3)],
        "API names + bigrams": sets["api_bigram"][0],
        "API names + bigrams + links": [sp.hstack([sets["api_bigram"][0][k], sp.csr_matrix(LXs[k])]).tocsr() for k in range(3)],
    }
    fname = {"links only": "lgbm_links", "length only": "lgbm_length", "length + links": "lgbm_length_links",
             "bag of API names": "lgbm_api", "API names + links": "lgbm_api_links",
             "API names + bigrams": "lgbm_api_bigram", "API names + bigrams + links": "lgbm_api_bigram_links"}
    table, famtab, mean_scores = [], [], {}
    for name, X in combos.items():
        evs, evvs, allsc = [], [], []
        for seed in SEEDS:
            t0 = time.time()
            m = fit_lgb(X[0], y["train"], X[1], y["val"], W, seed)
            s = m.predict(X[2], num_iteration=m.best_iteration)
            sv = m.predict(X[1], num_iteration=m.best_iteration)
            evs.append(evaluate(y["test"], s, fam)); evvs.append({"auc": wauc(y["val"], sv, W)}); allsc.append(s)
            print(f"  {name} seed {seed}: iter {m.best_iteration} val AUC {evvs[-1]['auc']:.4f} test AUC "
                  f"{evs[-1]['auc']:.4f} TPR1 {evs[-1]['tpr1']:.4f} ({time.time() - t0:.0f}s)", flush=True)
        mean_scores[name] = np.mean(allsc, 0)
        if "links" in name:
            save_scores(fname[name], np.tile(rows["test"], 3), np.tile(y["test"], 3), np.concatenate(allsc),
                        np.repeat(SEEDS, len(rows["test"])))
        table.append(result_row(f"LightGBM, {name}", evs, {"val AUC (group-weighted)": mean_range([e["auc"] for e in evvs], f4)}))
        famtab.append(family_row(f"LightGBM, {name}", evs))
    boots = []
    for a_, b_ in [("links only", None), ("length + links", "length only"), ("API names + links", "bag of API names"),
                   ("API names + bigrams + links", "API names + bigrams")]:
        if b_ is None:
            continue
        bt = paired_bootstrap(y["test"], mean_scores[a_], mean_scores[b_])
        bt.insert(0, "comparison", f"{a_} − {b_}")
        boots.append(bt)
    # how the link features differ by class (January train)
    tr = meta.side.values == "train"
    desc = []
    for c in ["n_links", "links_per_call", "n_cross_chunk_links", "max_link_distance_calls"]:
        r = {"feature": c}
        for lab, l in [("malware", 1), ("benign", 0)]:
            v = LX[c].values[tr & (meta.label.values == l)]
            r[f"{lab} median [p25–p75]"] = f"{np.median(v):.2f} [{np.percentile(v, 25):.2f}–{np.percentile(v, 75):.2f}]"
        r["AUC of the feature alone (Jan train)"] = f4(auc(meta.label.values[tr], LX[c].values[tr]))
        desc.append(r)
    txt = ("### 6. Do data-flow links separate the classes?\n\n"
           "Link = REPORT.md §8 definition (merged API list, address-like return value ≥ 0x10000 reused as a later "
           "argument; producer = first call that returned it). Link features: number of links, links per call, "
           "cross-chunk links, links leaving chunk 0, maximum link distance (calls), maximum chunk distance, and counts "
           "of the 20 most common producer→user pairs (API names without DLL, lower-case) in the January training side. "
           "LightGBM as in analysis 1 (early stopping on group-weighted validation log-loss), seeds 0/1/2.\n\n"
           "#### 6a. Top 20 producer→user pairs (January train side)\n\n" +
           md_table(pd.DataFrame({"pair": pair_names, "links": [f"{n:,}" for n in pair_n]})) +
           "\n#### 6b. Link features by class (January train side)\n\n" + md_table(pd.DataFrame(desc)) +
           "\n#### 6c. Models (April test set)\n\n" + md_table(pd.DataFrame(table)) +
           "\n#### 6d. Paired bootstrap of the difference (mean score over the 3 seeds, 1,000 resamples)\n\n" +
           md_table(pd.concat(boots)) +
           "\n#### 6e. TPR at 1% FPR per family\n\n" + md_table(pd.DataFrame(famtab)))
    write_part("a6_links", txt)
    cmd_tables(a)


# =========================================================================== report variants + tokenization
PLACEHOLDER_CANDIDATES = ["addr", "value", "mem", "heap", "ptr", "handle", "buf", "data", "hex", "unk"]


def variant(rep, kind, seed=0, row=0, ph=None, K=None):
    """A modified copy of a Nebula-filtered report. The field order stays as Nebula wrote it."""
    rep = dict(rep)
    calls = list(rep.get("apis") or [])
    if kind == "orig":
        pass
    elif kind == "prefix":
        calls = calls[:K]
    elif kind == "shuffle":
        order = np.random.default_rng([seed, row]).permutation(len(calls))
        calls = [calls[i] for i in order]
    elif kind == "no_args":
        calls = [{k: v for k, v in c.items() if k != "args"} for c in calls]
    elif kind == "no_ret":
        calls = [{k: v for k, v in c.items() if k != "ret_val"} for c in calls]
    elif kind in ("addr_ph", "hex_ph"):
        lim = 0x10000 if kind == "addr_ph" else 0

        def sub(v):
            h = hex_value(v)
            return ph if h is not None and h >= lim else v
        new = []
        for c in calls:
            c = dict(c)
            if "args" in c and isinstance(c["args"], list):
                c["args"] = [sub(x) for x in c["args"]]
            if "ret_val" in c:
                c["ret_val"] = sub(c["ret_val"])
            new.append(c)
        calls = new
    elif kind == "no_fields":
        rep = {}
    elif kind == "names_only":
        rep = {}
        calls = [{"api_name": c["api_name"]} for c in calls]
    else:
        raise ValueError(kind)
    rep["apis"] = calls
    return rep


_W = {}


def _init_tok(nebula):
    from measure_lengths import Nebula
    _W["nb"] = Nebula(nebula)
    _W["reps"] = Reps()


def _tok(job):
    """job = (row, kind, seed, ph, K) -> (row, int32 ids [512])"""
    row, kind, seed, ph, K = job
    rep = variant(_W["reps"].get(row), kind, seed=seed, row=row, ph=ph, K=K)
    return row, np.asarray(_W["nb"].tokenizer.encode(rep, pad=True)[0], dtype=np.int32)


def tokenize_jobs(pool, jobs):
    ids = np.zeros((len(jobs), SEQ_LEN), dtype=np.int32)
    for k, (row, x) in enumerate(pool.imap(_tok, jobs, chunksize=32)):
        assert row == jobs[k][0]
        ids[k] = x
    return ids


# =========================================================================== prefix (analysis 2)
KS = [10, 25, 50, 100, 200, 500, None]


def klab(K):
    return "all" if K is None else str(K)


def cmd_prefix(a):
    from multiprocessing import Pool
    log_versions()
    meta, F, seqs = load_meta(), load_features(), Seqs()
    test = meta.split.values == "testset"
    # ---- how many calls fit in Nebula's first 512 tokens
    meas = []
    for lab, m in [("all reports", np.ones(len(F), bool)), ("reports > 512 tokens", F.tokens.values > SEQ_LEN),
                   ("reports > 512 tokens, January", (F.tokens.values > SEQ_LEN) & ~test),
                   ("reports > 512 tokens, April", (F.tokens.values > SEQ_LEN) & test)]:
        r = {"reports": f"{lab} (n={m.sum():,})"}
        for c, cl in [("calls_fit_in_512", "calls fully inside 512"), ("calls_start_in_512", "calls starting inside 512"),
                      ("head_tokens", "tokens before the API list")]:
            v = F[c].values[m]
            r[f"{cl}: median [p25–p75]"] = f"{np.median(v):.0f} [{np.percentile(v, 25):.0f}–{np.percentile(v, 75):.0f}]"
        v = (F.tokens.values[m] - F.head_tokens.values[m]) / np.maximum(1, F.n_calls.values[m])
        r["tokens per call (median)"] = f"{np.median(v[F.n_calls.values[m] > 0]):.2f}"
        meas.append(r)
    print(pd.DataFrame(meas).to_string(), flush=True)

    rows = {s: meta.row.values[meta.side == s] for s in ["train", "val", "test"]}
    y = {s: meta.label.values[rows[s]] for s in rows}
    long_ = F.n_calls.values[rows["test"]] > 200
    V = len(seqs.vocab)
    W = group_weights(meta)
    curve = []
    # ---- (a) LightGBM on prefixes
    for K in KS:
        allrows = np.concatenate([rows["train"], rows["val"], rows["test"]])
        X, keep = bag_matrix(seqs, allrows, V, K=K, bigrams=True, fit_rows=rows["train"])
        cut = np.cumsum([0, len(rows["train"]), len(rows["val"]), len(rows["test"])])
        Xs = [X[cut[k]:cut[k + 1]] for k in range(3)]
        allsc = []
        for seed in SEEDS:
            t0 = time.time()
            m = fit_lgb(Xs[0], y["train"], Xs[1], y["val"], W, seed)
            s = m.predict(Xs[2], num_iteration=m.best_iteration)
            va = wauc(y["val"], m.predict(Xs[1], num_iteration=m.best_iteration), W)
            allsc.append(s)
            e, el = evaluate(y["test"], s), None
            thr = {0.01: e["thr1"], 0.001: e["thr01"]}
            el = evaluate(y["test"][long_], s[long_], thr=thr)
            curve.append({"model": "LightGBM API names + bigrams", "K": klab(K), "seed": seed, "subset": "all April",
                          "val_auc": va, **{k: e[k] for k in ["auc", "tpr1", "tpr01", "tp1", "n_mal"]}})
            curve.append({"model": "LightGBM API names + bigrams", "K": klab(K), "seed": seed, "subset": "> 200 calls",
                          **{k: el[k] for k in ["auc", "tpr1", "tpr01", "tp1", "n_mal"]}})
            print(f"  LGBM K={klab(K)} seed {seed}: {X.shape[1]} features, iter {m.best_iteration}, AUC {e['auc']:.4f} "
                  f"TPR1 {e['tpr1']:.4f}; >200 calls AUC {el['auc']:.4f} TPR1 {el['tpr1']:.4f} ({time.time() - t0:.0f}s)",
                  flush=True)
        save_scores(f"lgbm_prefix_{klab(K)}", np.tile(rows["test"], 3), np.tile(y["test"], 3), np.concatenate(allsc),
                    np.repeat(SEEDS, len(rows["test"])))
    # ---- (b) released Nebula on the same prefixes (April)
    import torch
    torch.set_num_threads(4)
    model = load_nebula(a.nebula)
    trow = rows["test"]
    start512 = F.calls_start_in_512.values[trow]
    ncalls = F.n_calls.values[trow]
    with Pool(a.workers, initializer=_init_tok, initargs=(a.nebula,)) as pool:
        # Nebula's logits on the unchanged reports (metrics use logits: same ranking, no float32 ties at 1.0)
        base = nebula_scores(model, tokenize_jobs(pool, [(int(r), "orig", 0, None, None) for r in trow]), logit=True)
        d = np.abs(sigmoid32(base) - meta.nebula.values[trow]).max()
        print(f"check: sigmoid(logit) of unchanged April reports vs nebula_score_chunk0.npy: max |diff| {d:.2e}", flush=True)
        assert d < 1e-4
        # check: when the prefix keeps every call that starts inside the window, the first 512 tokens do not change
        rng = np.random.default_rng(0)
        cand = np.flatnonzero((ncalls > start512 + 1))
        chk = rng.choice(cand, min(300, len(cand)), replace=False)
        jobs = [(int(trow[i]), "prefix", 0, None, int(start512[i]) + int(rng.integers(0, ncalls[i] - start512[i])))
                for i in chk]
        ids = tokenize_jobs(pool, jobs)
        jobs0 = [(int(trow[i]), "orig", 0, None, None) for i in chk]
        ids0 = tokenize_jobs(pool, jobs0)
        same = int((ids == ids0).all(1).sum())
        print(f"check: prefix with K >= calls starting in 512 keeps the first 512 tokens: {same}/{len(chk)}", flush=True)
        assert same == len(chk)
        for K in KS:
            s = base.copy()
            need = np.flatnonzero(start512 > K) if K is not None else np.zeros(0, int)
            if len(need):
                ids = tokenize_jobs(pool, [(int(trow[i]), "prefix", 0, None, K) for i in need])
                s[need] = nebula_scores(model, ids, logit=True)
            save_scores(f"nebula_prefix_{klab(K)}", trow, y["test"], s, np.zeros(len(s), int))   # score = logit
            e = evaluate(y["test"], s)
            el = evaluate(y["test"][long_], s[long_], thr={0.01: e["thr1"], 0.001: e["thr01"]})
            for sub_, ee in [("all April", e), ("> 200 calls", el)]:
                curve.append({"model": "released Nebula", "K": klab(K), "seed": 0, "subset": sub_,
                              **{k: ee[k] for k in ["auc", "tpr1", "tpr01", "tp1", "n_mal"]}})
            print(f"  Nebula K={klab(K)}: {len(need):,} reports re-scored, AUC {e['auc']:.4f} TPR1 {e['tpr1']:.4f}; "
                  f">200 calls AUC {el['auc']:.4f} TPR1 {el['tpr1']:.4f}", flush=True)
    cv = pd.DataFrame(curve)
    cv.to_csv(os.path.join(R, "prefix_curve.csv"), index=False)
    # ---- tables
    tab = []
    for (mod, sub_), g in cv.groupby(["model", "subset"], sort=False):
        for K in KS:
            gg = g[g.K == klab(K)]
            tab.append({"model": mod, "subset": f"{sub_} (malware n={gg.n_mal.iloc[0]:,})", "K (calls)": klab(K),
                        "AUC": mean_range(list(gg.auc), f4), "TPR @1% FPR": mean_range(list(gg.tpr1), pct),
                        "TPR @0.1% FPR": mean_range(list(gg.tpr01), pct),
                        "malware caught @1%": f"{gg.tp1.mean():,.0f}",
                        "Jan val AUC (group-weighted)": mean_range(list(gg.val_auc), f4)
                        if "val_auc" in gg and gg.val_auc.notna().all() else "—"})
    n_long = int(long_.sum())
    txt = ("### 2. Prefix curve: how many API calls are needed?\n\n"
           "#### 2a. How many API calls fit in Nebula's first 512 tokens (measured on the tokenized reports)\n\n"
           "`calls fully inside 512` counts calls whose last token is at position < 512; `calls starting inside 512` "
           "counts calls whose first token is. For reports ≤ 512 tokens every call fits.\n\n" +
           md_table(pd.DataFrame(meas)) +
           f"\n#### 2b. Detection against the number of API calls kept (April; {n_long:,} reports have > 200 calls)\n\n"
           "Only the `apis` list is cut to its first K calls; file, registry and network fields are kept. LightGBM is "
           "trained on January prefixes of the same length and early-stopped on the group-weighted validation log-loss "
           "(seeds 0/1/2). Released Nebula is only "
           "re-scored. Thresholds: from the April benign scores of all April reports at the same K (also for the "
           "> 200-call subset). Nebula is ranked by its logit (scores files hold logits). The last column is the same LightGBM on the January validation side (all reports): "
           "there, more calls always help.\n\n" + md_table(pd.DataFrame(tab)) +
           "\n![prefix curve](plots/prefix_curve.png)\n")
    write_part("a2_prefix", txt)
    plot_prefix(cv)
    cmd_tables(a)


def plot_prefix(cv):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(os.path.join(R, "plots"), exist_ok=True)
    xs = {klab(K): i for i, K in enumerate(KS)}
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
    styles = {("released Nebula", "all April"): ("#2a78d6", "-"), ("released Nebula", "> 200 calls"): ("#2a78d6", "--"),
              ("LightGBM API names + bigrams", "all April"): ("#eb6834", "-"),
              ("LightGBM API names + bigrams", "> 200 calls"): ("#eb6834", "--")}
    for ax, met, lab in [(axes[0], "tpr1", "TPR at 1% FPR"), (axes[1], "auc", "AUC")]:
        for (mod, sub_), g in cv.groupby(["model", "subset"], sort=False):
            col, ls = styles[(mod, sub_)]
            gg = g.groupby("K", sort=False)[met].agg(["mean", "min", "max"])
            x = [xs[k] for k in gg.index]
            ax.plot(x, gg["mean"], ls, color=col, marker="o", ms=4, lw=2, label=f"{mod}, {sub_}")
            ax.fill_between(x, gg["min"], gg["max"], color=col, alpha=0.15, lw=0)
        ax.set_xticks(range(len(KS)), [klab(K) for K in KS])
        ax.set_xlabel("API calls kept (K)")
        ax.set_title(lab, loc="left", fontsize=11)
        ax.grid(axis="y", alpha=0.3)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=9, frameon=False, loc="lower center", ncol=2)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    fig.savefig(os.path.join(R, "plots", "prefix_curve.png"), dpi=150)
    print("wrote", os.path.join(R, "plots", "prefix_curve.png"))


# =========================================================================== ablations (analysis 3)
ABLATIONS = [("shuffle", "shuffle API call order"), ("no_args", "remove all arguments"),
             ("no_ret", "remove return values"), ("addr_ph", "address-like hex (≥ 0x10000) → placeholder"),
             ("hex_ph", "all hex values → placeholder"), ("no_fields", "remove file, registry, network fields"),
             ("names_only", "API names only")]


def cmd_ablate(a):
    from multiprocessing import Pool
    import torch
    log_versions()
    torch.set_num_threads(4)
    meta = load_meta()
    model = load_nebula(a.nebula)
    from measure_lengths import Nebula
    sp_ = Nebula(a.nebula).tokenizer.tokenizer
    sets = {"April test": meta.row.values[meta.split == "testset"], "January validation": meta.row.values[meta.side == "val"]}
    scores = {}
    with Pool(a.workers, initializer=_init_tok, initargs=(a.nebula,)) as pool:
        # ---- unmodified: must reproduce nebula_score_chunk0.npy
        for sn, rows in sets.items():
            t0 = time.time()
            s = nebula_scores(model, tokenize_jobs(pool, [(int(r), "orig", 0, None, None) for r in rows]), logit=True)
            d = np.abs(sigmoid32(s) - meta.nebula.values[rows])
            print(f"check ({sn}): unmodified vs nebula_score_chunk0.npy max |diff| = {d.max():.2e} "
                  f"({len(rows):,} reports, {time.time() - t0:.0f}s)", flush=True)
            assert d.max() < 1e-4
            scores[(sn, "orig", 0)] = s
        # ---- placeholder: single known token, chosen on January validation only
        ph_log = []
        for c in PLACEHOLDER_CANDIDATES:
            ids = sp_.encode_as_ids(c)
            single = len(ids) == 1 and ids[0] != 1 and hex_value(c) is None
            r = {"candidate": c, "pieces": " ".join(sp_.encode_as_pieces(c)), "ids": str(ids), "single known token": single}
            if single:
                rows = sets["January validation"]
                s = nebula_scores(model, tokenize_jobs(pool, [(int(x), "addr_ph", 0, c, None) for x in rows]), logit=True)
                r["mean |Δscore| on Jan val (addr_ph)"] = float(np.abs(sigmoid32(s) - sigmoid32(scores[("January validation", "orig", 0)])).mean())
                r["Jan val AUC"] = auc(meta.label.values[rows], s)
            ph_log.append(r)
            print("placeholder candidate:", r, flush=True)
        ok = [r for r in ph_log if r["single known token"]]
        ph = min(ok, key=lambda r: r["mean |Δscore| on Jan val (addr_ph)"])["candidate"]
        print(f"chosen placeholder: {ph!r} (smallest mean |Δscore| on January validation)", flush=True)
        # ---- ablations
        for kind, _ in ABLATIONS:
            seeds = SEEDS if kind == "shuffle" else [0]
            for sn, rows in sets.items():
                for seed in seeds:
                    t0 = time.time()
                    s = nebula_scores(model, tokenize_jobs(pool, [(int(r), kind, seed, ph, None) for r in rows]), logit=True)
                    scores[(sn, kind, seed)] = s
                    print(f"  {kind} seed {seed} on {sn}: AUC {auc(meta.label.values[rows], s):.4f} "
                          f"({time.time() - t0:.0f}s)", flush=True)
                save_scores(f"nebula_ablate_{kind}" + ("_janval" if sn != "April test" else ""),
                            np.tile(rows, len(seeds)), np.tile(meta.label.values[rows], len(seeds)),
                            np.concatenate([scores[(sn, kind, sd)] for sd in seeds]), np.repeat(seeds, len(rows)))
    # ---- tables
    out = []
    for sn, rows in sets.items():
        y = meta.label.values[rows]
        fam = meta.family.values[rows]
        e0 = evaluate(y, scores[(sn, "orig", 0)], fam)
        flag0 = scores[(sn, "orig", 0)] > e0["thr1"]
        out.append({"set": sn, "change": "none (unmodified)", "AUC": f4(e0["auc"]),
                    "TPR @1% FPR": f"{pct(e0['tpr1'])} ({e0['tp1']:,}/{e0['n_mal']:,})",
                    "TPR @0.1% FPR": f"{pct(e0['tpr01'])} ({e0['tp01']:,})", "ΔAUC": "", "ΔTPR @1%": "",
                    "ΔTPR @0.1%": "", "crossed the 1% threshold": "", "mean |Δscore|": "",
                    "benign at p = 1.0 (float32)": f"{((sigmoid32(scores[(sn, 'orig', 0)]) == 1.0) & (y == 0)).sum():,}"})
        for kind, lab in ABLATIONS:
            seeds = SEEDS if kind == "shuffle" else [0]
            evs = [evaluate(y, scores[(sn, kind, sd)], fam) for sd in seeds]
            cr, down, up, md, sat = [], [], [], [], []
            for sd in seeds:
                f1 = scores[(sn, kind, sd)] > e0["thr1"]
                cr.append((f1 != flag0).mean()); down.append(int((flag0 & ~f1 & (y == 1)).sum()))
                up.append(int((~flag0 & f1 & (y == 0)).sum()))
                md.append(np.abs(sigmoid32(scores[(sn, kind, sd)]) - sigmoid32(scores[(sn, "orig", 0)])).mean())
                sat.append(((sigmoid32(scores[(sn, kind, sd)]) == 1.0) & (y == 0)).sum())
            pp = lambda x: f"{100 * x:+.1f} pp"
            out.append({"set": sn, "change": lab + (" (3 seeds)" if len(seeds) > 1 else ""),
                        "AUC": mean_range([e["auc"] for e in evs], f4),
                        "TPR @1% FPR": mean_range([e["tpr1"] for e in evs], pct) + f" ({np.mean([e['tp1'] for e in evs]):,.0f})",
                        "TPR @0.1% FPR": mean_range([e["tpr01"] for e in evs], pct) + f" ({np.mean([e['tp01'] for e in evs]):,.0f})",
                        "ΔAUC": mean_range([e["auc"] - e0["auc"] for e in evs], lambda x: f"{x:+.4f}"),
                        "ΔTPR @1%": mean_range([e["tpr1"] - e0["tpr1"] for e in evs], pp),
                        "ΔTPR @0.1%": mean_range([e["tpr01"] - e0["tpr01"] for e in evs], pp),
                        "crossed the 1% threshold": mean_range(cr, pct) +
                        f" ({np.mean(down):,.0f} malware lost, {np.mean(up):,.0f} benign gained)",
                        "mean |Δscore|": mean_range(md, lambda x: f"{x:.3f}"),
                        "benign at p = 1.0 (float32)": mean_range(sat, lambda x: f"{x:,.0f}")})
    famtab = []
    rows = sets["April test"]
    y, fam = meta.label.values[rows], meta.family.values[rows]
    for kind, lab in [("orig", "none (unmodified)")] + ABLATIONS:
        seeds = SEEDS if kind == "shuffle" else [0]
        evs = [evaluate(y, scores[("April test", kind, sd)], fam) for sd in seeds]
        famtab.append(family_row(lab, evs))
    phdf = pd.DataFrame(ph_log)
    for c in ["mean |Δscore| on Jan val (addr_ph)", "Jan val AUC"]:
        if c in phdf:
            phdf[c] = phdf[c].map(lambda x: "—" if pd.isna(x) else f"{x:.4f}")
    txt = ("### 3. Ablations of released Nebula (inference only)\n\n"
           "Each change is applied to Nebula's filtered report, which is then tokenized and cut to 512 tokens as "
           "usual. Thresholds come from the benign scores of the changed reports; `crossed` uses the unmodified "
           "model's 1% FPR threshold and counts reports on the other side after the change (either direction). "
           "Metrics rank reports by Nebula's logit: the changed reports push hundreds of benign scores to exactly "
           "1.0 in float32 (last column), and with the probability the 1% threshold would sit on that tie. Scores files "
           "hold logits; `mean |Δscore|` is on the probability scale. sigmoid(logit) of the unmodified reports "
           "reproduces `nebula_score_chunk0.npy` (max |diff| in the log). Removing arguments or "
           "return values deletes the key from every call (the key names are stopwords, so they produce no tokens "
           "either way).\n\n"
           "#### 3a. Placeholder for hex values (chosen on January validation)\n\n"
           "Candidates must be one known token (not `<unk>`, id 1) and not a hex value. Among them, the one that "
           f"changes January-validation scores least under the address replacement is used: **`{ph}`**.\n\n" +
           md_table(phdf) + "\n#### 3b. Results\n\n" + md_table(pd.DataFrame(out)) +
           "\n#### 3c. TPR at 1% FPR per family (April)\n\n" + md_table(pd.DataFrame(famtab)))
    write_part("a3_ablate", txt)
    cmd_tables(a)


# =========================================================================== attribution (analysis 4)
CATS = ["API name", "address-like hex (≥ 0x10000)", "small hex", "string argument", "field key",
        "file/registry/network value", "padding", "other"]


def role_pieces(rep):
    """str(rep) as a list of (text, category) whose texts join to exactly str(rep)."""
    out = []

    def val_cat(v, field, key):
        if field == "apis":
            if key == "api_name":
                return "API name"
            h = hex_value(v)
            if h is not None:
                return "address-like hex (≥ 0x10000)" if h >= 0x10000 else "small hex"
            if v is None:
                return "other"
            return "string argument"
        return "file/registry/network value"

    def emit(o, field, key, top=False):
        if isinstance(o, dict):
            out.append(("{", "other"))
            for i, (k, v) in enumerate(o.items()):
                if i:
                    out.append((", ", "other"))
                out.append((repr(k) + ": ", "field key"))
                emit(v, k if top else field, None if top else k)
            out.append(("}", "other"))
        elif isinstance(o, list):
            out.append(("[", "other"))
            for i, v in enumerate(o):
                if i:
                    out.append((", ", "other"))
                emit(v, field, key)
            out.append(("]", "other"))
        else:
            out.append((repr(o), val_cat(o, field, key)))

    emit(rep, None, None, top=True)
    assert "".join(t for t, _ in out) == str(rep)
    return out


def token_roles(nb, rep, full_ids):
    """Category of each of the first 512 token positions, by tokenizing the pieces of role_pieces()
    separately. Returns None if the joined piece ids differ from the report's own ids."""
    roles, ids = [], []
    for text, cat in role_pieces(rep):
        t = nb.ids(text) if text.strip("{}[], ") else []
        ids.extend(t)
        roles.extend([cat] * len(t))
        if len(ids) >= SEQ_LEN + 64:
            break
    n = min(len(full_ids), SEQ_LEN)
    if ids[:n] != list(full_ids[:n]):
        return None
    return roles[:n] + ["padding"] * (SEQ_LEN - n)


def cmd_attrib(a):
    import torch
    from measure_lengths import Nebula
    log_versions()
    torch.set_num_threads(4)
    torch.manual_seed(0)
    meta = load_meta()
    nb = Nebula(a.nebula)
    model = load_nebula(a.nebula)
    reps = Reps()
    test = meta[meta.split == "testset"]
    rng = np.random.default_rng(0)
    per = [a.n // 2 // len(FAMILIES) + (1 if i < (a.n // 2) % len(FAMILIES) else 0) for i in range(len(FAMILIES))]
    pick = []
    for f, k in zip(FAMILIES, per):
        pick += list(rng.choice(test.row.values[test.family == f], k, replace=False))
    pick += list(rng.choice(test.row.values[test.label == 0], a.n - sum(per), replace=False))
    pick = np.array(pick)
    base_ids = np.asarray(nb.tokenizer.encode({"apis": []}, pad=True)[0], dtype=np.int64)
    print(f"sample: {len(pick)} April reports ({sum(per)} malware: {dict(zip(FAMILIES, per))}; "
          f"{a.n - sum(per)} benign), seed 0", flush=True)
    print(f"method: integrated gradients on the embedding-layer output (model.encoder), {a.steps} steps, "
          f"midpoint Riemann sum, target = Nebula's logit. Baseline = embedding of {{'apis': []}} tokenized and padded: "
          f"ids {base_ids[:5].tolist()}... ({int((base_ids != 0).sum())} non-pad tokens)", flush=True)
    E0 = model.encoder(torch.from_numpy(base_ids)[None])                      # [1, 512, 64]
    with torch.no_grad():
        x = torch.from_numpy(base_ids)[None]
        assert torch.allclose(forward_from_embedding(model, model.encoder(x)), model(x), atol=1e-5)
        base_logit = model(x).item()
    alphas = ((torch.arange(a.steps) + 0.5) / a.steps).view(-1, 1, 1)
    attr = np.zeros((len(pick), SEQ_LEN), dtype=np.float32)
    ids_all = np.zeros((len(pick), SEQ_LEN), dtype=np.int64)
    roles_all, logit, comp_err, fallback = [], [], [], 0
    t0 = time.time()
    for n, row in enumerate(pick):
        rep = reps.get(int(row))
        ids = np.asarray(nb.tokenizer.encode(rep, pad=True)[0], dtype=np.int64)
        ids_all[n] = ids
        roles = token_roles(nb, rep, nb.ids(rep))
        if roles is None:
            fallback += 1
        roles_all.append(roles)
        xi = torch.from_numpy(ids)[None]
        with torch.no_grad():
            E = model.encoder(xi)
            lg = model(xi).item()
        path = (E0 + alphas * (E - E0)).detach().requires_grad_(True)
        out = forward_from_embedding(model, path).sum()
        g, = torch.autograd.grad(out, path)
        at = ((E - E0) * g.mean(0, keepdim=True)).sum(-1)[0].detach().numpy()
        attr[n] = at
        logit.append(lg)
        comp_err.append(abs(at.sum() - (lg - base_logit)))
        if (n + 1) % 100 == 0:
            print(f"  {n + 1}/{len(pick)} done, {(time.time() - t0) / 60:.1f} min; median completeness error "
                  f"{np.median(comp_err):.4f} (logit units)", flush=True)
    logit = np.array(logit)
    sc = 1 / (1 + np.exp(-logit))
    assert np.abs(sc - meta.nebula.values[pick]).max() < 1e-4
    y = meta.label.values[pick]
    ok = np.array([r is not None for r in roles_all])
    print(f"token roles exact for {ok.sum()}/{len(pick)} reports; completeness |sum(attr) - (logit - base)|: median "
          f"{np.median(comp_err):.4f}, p95 {np.percentile(comp_err, 95):.4f}; mean |logit - base| "
          f"{np.mean(np.abs(logit - base_logit)):.2f}; {(time.time() - t0) / 60:.1f} min", flush=True)
    np.savez_compressed(os.path.join(WORK, "attrib.npz"), rows=pick, attr=attr, ids=ids_all, logit=logit)
    roles = np.array([r if r is not None else ["other"] * SEQ_LEN for r in roles_all])
    # ---- category shares
    cat_rows = []
    for lab, m in [("malware", (y == 1) & ok), ("benign", (y == 0) & ok)]:
        A, Rl = np.abs(attr[m]), roles[m]
        tot = A.sum()
        r = {"class": f"{lab} (n={m.sum()})"}
        for c in CATS:
            r[c] = pct(A[Rl == c].sum() / tot)
        cat_rows.append(r)
        r2 = {"class": f"{lab}: share of the 512 positions"}
        for c in CATS:
            r2[c] = pct((Rl == c).mean())
        cat_rows.append(r2)
        r3 = {"class": f"{lab}: mean signed attribution per report (logit)"}
        for c in CATS:
            r3[c] = f"{attr[m][Rl == c].sum() / m.sum():+.2f}"
        cat_rows.append(r3)
    blk = []
    for lab, m in [("malware", y == 1), ("benign", y == 0)]:
        A = np.abs(attr[m])
        r = {"class": lab}
        for b in range(8):
            r[f"tokens {b * 64}–{b * 64 + 63}"] = pct(A[:, b * 64:(b + 1) * 64].sum() / A.sum())
        blk.append(r)
    # ---- top tokens
    flat_ids, flat_a, flat_r = ids_all[ok].ravel(), attr[ok].ravel(), roles[ok].ravel()
    nz = flat_r != "padding"
    df = pd.DataFrame({"id": flat_ids[nz], "a": flat_a[nz], "role": flat_r[nz]})
    g = df.groupby("id").agg(n=("a", "size"), mean=("a", "mean"), mabs=("a", lambda v: np.abs(v).mean()),
                             role=("role", lambda v: v.value_counts().index[0]))
    g = g[g.n >= 50]
    g["token"] = [sp_piece(nb, i) for i in g.index]
    top = []
    for lab, gg in [("towards malware (highest mean)", g.sort_values("mean", ascending=False).head(30)),
                    ("towards benign (lowest mean)", g.sort_values("mean").head(30))]:
        for i, r in gg.iterrows():
            top.append({"direction": lab, "token": f"`{r.token}`", "category": r.role, "occurrences": f"{r.n:,}",
                        "mean attribution": f"{r['mean']:+.4f}", "mean |attribution|": f"{r.mabs:.4f}"})
    txt = ("### 4. Attribution: integrated gradients on 1,000 April reports\n\n"
           f"Stratified sample (seed 0): {sum(per)} malware ({', '.join(f'{f} {k}' for f, k in zip(FAMILIES, per))}) and "
           f"{a.n - sum(per)} benign. Method: integrated gradients on the output of Nebula's embedding layer, "
           f"{a.steps} steps (midpoint rule), target = Nebula's logit, attribution of a token = sum over the 64 "
           "embedding dimensions. Baseline = the embedding of the empty report `{'apis': []}` tokenized and padded. "
           f"Completeness error |Σ attribution − (logit − baseline logit)|: median {np.median(comp_err):.4f}, "
           f"p95 {np.percentile(comp_err, 95):.4f} (mean |logit − baseline logit| = "
           f"{np.mean(np.abs(logit - base_logit)):.2f}). Token categories come from tokenizing the report in pieces "
           f"(exact for {ok.sum()}/{len(pick)} reports; the rest are left out of 4a and 4c). Padding positions "
           "match the baseline's padding, so their attribution is zero by construction.\n\n"
           "#### 4a. Share of total absolute attribution per category\n\n" + md_table(pd.DataFrame(cat_rows)) +
           "\n#### 4b. Share of absolute attribution per 64-token block (Nebula attends only inside these blocks)\n\n" +
           md_table(pd.DataFrame(blk)) +
           "\n#### 4c. Top 30 tokens by mean attribution (tokens with ≥ 50 occurrences in the sample)\n\n" +
           md_table(pd.DataFrame(top)))
    write_part("a4_attrib", txt)
    cmd_tables(a)


def sp_piece(nb, i):
    return nb.tokenizer.tokenizer.id_to_piece(int(i)).replace("|", "\\|")


# =========================================================================== tables
def cmd_tables(a=None):
    parts = sorted(os.listdir(os.path.join(R, "parts")))
    txt = ("# Where the signal is: tables (generated by analyze_signal.py)\n\n" +
           "\n".join(open(os.path.join(R, "parts", p)).read() for p in parts))
    open(os.path.join(R, "tables.md"), "w").write(txt)
    print(f"wrote {R}/tables.md from {parts}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nebula", default="../nebula")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("split")
    p = sub.add_parser("collect")
    p.add_argument("--data-dir", default="../hf-git")
    p.add_argument("--workers", type=int, default=os.cpu_count())
    for c in ["baselines", "drift", "links", "tables"]:
        sub.add_parser(c)
    p = sub.add_parser("prefix")
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p = sub.add_parser("ablate")
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p = sub.add_parser("attrib")
    p.add_argument("--n", type=int, default=1000)
    p.add_argument("--steps", type=int, default=50)
    a = ap.parse_args()
    os.makedirs(R, exist_ok=True)
    fn = globals()[f"cmd_{a.cmd}"]
    return fn(a)


if __name__ == "__main__":
    sys.exit(main() or 0)
