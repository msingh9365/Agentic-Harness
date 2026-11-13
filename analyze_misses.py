#!/usr/bin/env python
"""
Why are April (testset) ransomware and coinminer reports missed?

    collect   one pass over all 92,700 raw reports with Nebula's own preprocessing:
              exact hashes of the filtered report and of the API-name sequence,
              emulator stop reasons per entry point, fields Nebula drops, and the
              API-name sequence of every report (stored outside the repo)
    analyze   checks the row mapping of the model scores, then tasks 1-6 of the brief;
              writes results/misses/tables.md and results/misses/plots/

Models compared: finetune_k8 (two-level, fine-tuned, 8 chunks) and frozen_k1
(released Nebula behaviour). Threshold = the score that flags 1% of April benign
reports (a report is flagged when its score is ABOVE the threshold), as in
hier_nebula/summarize.py.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np
import pandas as pd

from measure_lengths import Nebula, entry_points_of, list_files

R = "results/misses"
SEQ_DIR = "../hier_data/misses"          # API-name sequences (large; not committed)
MODELS = ["finetune_k8", "frozen_k1"]
FIELDS_DROPPED = ["process_events", "dropped_files", "dynamic_code_segments", "handled_exceptions"]
ENC_PATTERNS = [("CryptEncrypt", r"^CryptEncrypt$"), ("CryptAcquireContext*", r"^CryptAcquireContext"),
                ("BCrypt*", r"^BCrypt"), ("FindFirstFile*", r"^FindFirstFile"), ("FindNextFile*", r"^FindNextFile"),
                ("CreateFile*", r"^CreateFile"), ("WriteFile", r"^WriteFile$"), ("MoveFile*", r"^MoveFile"),
                ("DeleteFile*", r"^DeleteFile")]
ANTI_PATTERNS = [("IsDebuggerPresent", r"^IsDebuggerPresent$"), ("CheckRemoteDebuggerPresent", r"^CheckRemoteDebuggerPresent$"),
                 ("GetTickCount*", r"^GetTickCount"), ("QueryPerformanceCounter", r"^QueryPerformanceCounter$"),
                 ("Sleep*", r"^Sleep"), ("GetSystemMetrics", r"^GetSystemMetrics$"), ("GetCursorPos", r"^GetCursorPos$")]
# REPORT.md §7 reference values for finetune_k8
REF_AUC = 0.9639
REF_BUCKET_AUC = {"1": 0.9726, "2–3": 0.9817, "4–8": 0.9358}


def short(name):
    return str(name).split(".")[-1]


def stop_category(t):
    if t in (None, "", "none"):
        return "no error recorded"
    if t == "max_api_count":
        return "max_api_count (500-call cap)"
    if t == "unsupported_api":
        return "unsupported API"
    if t.startswith("Invalid ") or t.startswith("invalid_") or t == "unhandled_interrupt":
        return "invalid memory / CPU fault"
    return "emulator internal error"


# --------------------------------------------------------------------------- collect
_NB = None


def _init(nebula):
    global _NB
    _NB = Nebula(nebula)


def _collect(item):
    import orjson
    split, folder, name, path = item
    with open(path, "rb") as fh:
        eps = entry_points_of(orjson.loads(fh.read()))
    rep = _NB.report(eps)
    calls = rep["apis"] if rep else []
    names = [c["api_name"] for c in calls]
    errs = [((ep.get("error") or {}).get("type") or "none") for ep in eps]
    unsup = [str((ep.get("error") or {}).get("api_name")) for ep in eps
             if (ep.get("error") or {}).get("type") == "unsupported_api"]
    row = {
        "split": split, "family": folder.replace("report_", ""), "sample_id": os.path.splitext(name)[0],
        "label": int(folder not in ("report_clean", "report_windows_syswow64")),
        "n_calls": len(calls), "n_entry_points": len(eps),
        "ep_types": "|".join(str(ep.get("ep_type")) for ep in eps),
        "error_types": "|".join(errs), "main_error": errs[0] if errs else "none",
        "unsupported_apis": "|".join(unsup),
        "has_file_access": int(bool(rep and len(rep.get("file_access") or []) > 0)),
        "has_registry_access": int(bool(rep and len(rep.get("registry_access") or []) > 0)),
        "has_network_traffic": int(bool(rep and len(rep.get("network_events.traffic") or []) > 0)),
        "hash_report": hashlib.sha1(json.dumps(rep, sort_keys=True).encode()).hexdigest() if rep else "none",
        "hash_apis": hashlib.sha1("\n".join(names).encode()).hexdigest(),
    }
    for f in FIELDS_DROPPED:
        row[f"raw_{f}"] = int(any(len(ep.get(f) or []) > 0 for ep in eps))
    return row, names


def cmd_collect(a):
    files = [f for f in list_files(a.data_dir) if f[2].endswith(".json")]
    os.makedirs(R, exist_ok=True); os.makedirs(SEQ_DIR, exist_ok=True)
    vocab, codes, offsets, rows = {}, [], [0], []
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(a.nebula,)) as pool:
        for k, (row, names) in enumerate(pool.imap(_collect, files, chunksize=16), 1):   # ordered
            rows.append(row)
            codes.extend(vocab.setdefault(n, len(vocab)) for n in names)
            offsets.append(len(codes))
            if k % 10000 == 0 or k == len(files):
                print(f"{k}/{len(files)} collected, {(time.time()-t0)/60:.1f} min", flush=True)
    pd.DataFrame(rows).to_csv(os.path.join(R, "reports.csv"), index=False)
    np.save(os.path.join(SEQ_DIR, "codes.npy"), np.asarray(codes, dtype=np.int32))
    np.save(os.path.join(SEQ_DIR, "offsets.npy"), np.asarray(offsets, dtype=np.int64))
    with open(os.path.join(SEQ_DIR, "vocab.json"), "w") as fh:
        json.dump(list(vocab), fh)
    print(f"wrote {R}/reports.csv ({len(rows)} rows) and API sequences ({len(codes):,} calls, "
          f"{len(vocab):,} distinct names) to {SEQ_DIR}")


# --------------------------------------------------------------------------- helpers
def auc(y, s):
    from sklearn.metrics import roc_auc_score
    return roc_auc_score(y, s)


def threshold(y, s, fpr=0.01):
    neg = np.sort(s[y == 0])[::-1]
    k = int(np.floor(fpr * len(neg)))
    return neg[k] if k < len(neg) else -np.inf


def pct(a, b):
    return 100.0 * a / b if b else float("nan")


def c(a, b):
    return f"{pct(a, b):.1f}% ({int(a):,})"


def md_table(df):
    cols = list(df.columns)
    out = "| " + " | ".join(map(str, cols)) + " |\n|" + "---|" * len(cols) + "\n"
    for _, r in df.iterrows():
        out += "| " + " | ".join(str(r[x]) for x in cols) + " |\n"
    return out


class Seqs:
    def __init__(self):
        self.codes = np.load(os.path.join(SEQ_DIR, "codes.npy"))
        self.offsets = np.load(os.path.join(SEQ_DIR, "offsets.npy"))
        self.vocab = json.load(open(os.path.join(SEQ_DIR, "vocab.json")))
        self.short_lower = np.array([short(v).lower() for v in self.vocab])

    def names(self, i):
        return [self.vocab[x] for x in self.codes[self.offsets[i]:self.offsets[i + 1]]]

    def short_set(self, i):
        return set(self.short_lower[self.codes[self.offsets[i]:self.offsets[i + 1]]])

    def short_list(self, i):
        return list(self.short_lower[self.codes[self.offsets[i]:self.offsets[i + 1]]])


# --------------------------------------------------------------------------- analyze
def cmd_analyze(a):
    md, summary = [], {}
    log = lambda *x: print(*x, flush=True)
    meta = pd.read_csv(os.path.join(a.data, "meta.csv"))
    rep = pd.read_csv(os.path.join(R, "reports.csv"), keep_default_na=False)
    S = pd.read_csv("results/samples.csv")

    # ---- 0. row mapping checks
    files = [f for f in list_files(a.data_dir) if f[2].endswith(".json")]
    rebuilt = pd.DataFrame([(sp, fo.replace("report_", ""), os.path.splitext(n)[0]) for sp, fo, n, _ in files],
                           columns=["split", "family", "id"])
    assert (rebuilt.id.values == meta.id.values).all() and (rebuilt.split.values == meta.split.values).all()
    assert (rep.sample_id.values == meta.id.values).all() and (rep.split.values == meta.split.values).all()
    assert (rep.label.values == meta.label.values).all()
    rep["row"] = np.arange(len(rep))
    rep = rep.merge(S[["split", "sample_id", "tokens", "n_apis_raw", "tok_registry_access", "tok_network_events.traffic",
                       "tok_file_access", "tok_apis", "n_entry_points", "n_chunks" if "n_chunks" in S else "chunks_fixed"]]
                    .rename(columns={"n_entry_points": "n_entry_points_s", "chunks_fixed": "n_chunks_s"}),
                    on=["split", "sample_id"], how="left", validate="one_to_one")
    assert rep.tokens.notna().all()
    assert (rep.n_entry_points == rep.n_entry_points_s).all()
    scores = {}
    for m in MODELS + ["frozen_k8", "finetune_k1"]:
        t = pd.read_csv(f"results/hier/{m}/test_scores.csv")
        assert len(t) == 17402
        rebuilt_test = rebuilt.index[rebuilt.split == "testset"].values
        assert set(t.row) == set(rebuilt_test), m
        assert (meta.label.values[t.row.values] == t.label.values).all(), m        # labels match for all rows
        scores[m] = t.set_index("row").score
    test = rep[rep.split == "testset"].copy()
    for m in scores:
        test[m] = scores[m].loc[test.row].values
    y = test.label.values
    a8 = auc(y, test.finetune_k8.values)
    assert round(a8, 4) == REF_AUC, a8
    nch = meta.n_chunks.values[test.row.values]
    for b, (lo, hi) in {"1": (1, 1), "2–3": (2, 3), "4–8": (4, 8)}.items():
        sel = (nch >= lo) & (nch <= hi)
        v = auc(y[sel], test.finetune_k8.values[sel])
        assert round(v, 4) == REF_BUCKET_AUC[b], (b, v)
    log(f"row mapping OK: 17,402 test rows, labels match, finetune_k8 AUC {a8:.4f}, bucket AUCs match REPORT §7")
    md.append("# Why April ransomware and coinminer reports are missed (analyze_misses.py)\n\n")
    md.append("## 0. Checks\n\n")
    md.append(f"- Test rows joined to `meta.csv`; the order rebuilt independently from `list_files()` is identical "
              f"for all 92,700 reports, and labels match `test_scores.csv` for all 17,402 test rows.\n"
              f"- `finetune_k8` test AUC {a8:.4f} (REPORT §7: {REF_AUC}); per-chunk-bucket AUCs "
              f"{', '.join(f'{k}: {v}' for k, v in REF_BUCKET_AUC.items())} reproduced.\n")

    thr = {m: threshold(y, test[m].values) for m in scores}
    for m in scores:
        test[f"flag_{m}"] = (test[m].values > thr[m]).astype(int)
    mal = test[test.label == 1]
    md.append("- Threshold at 1% FPR on the 8,003 April benign reports: " +
              ", ".join(f"`{m}` {thr[m]:.5f} (flags {int(test[(test.label == 0)][f'flag_{m}'].sum())})" for m in MODELS) + ".\n")

    # exact groups over all 92,700
    for h in ["hash_report", "hash_apis"]:
        g = rep.groupby(h)
        rep[f"{h}_size"] = g[h].transform("size")
        rep[f"{h}_mal_share"] = g.label.transform("mean")
        rep[f"{h}_conflict"] = ((rep[f"{h}_mal_share"] > 0) & (rep[f"{h}_mal_share"] < 1)).astype(int)
        test[f"{h}_size"] = rep.set_index("row").loc[test.row, f"{h}_size"].values
        test[f"{h}_mal_share"] = rep.set_index("row").loc[test.row, f"{h}_mal_share"].values
        test[f"{h}_conflict"] = rep.set_index("row").loc[test.row, f"{h}_conflict"].values
    fp_cols = ["tokens", "n_apis_raw", "tok_registry_access", "tok_network_events.traffic", "tok_file_access",
               "tok_apis", "n_entry_points"]
    # absent field = empty cell in samples.csv; a present field always has > 0 tokens, so 0 is unambiguous
    rep["fp"] = rep[fp_cols].fillna(0).astype("int64").astype(str).agg("|".join, axis=1)
    g = rep.groupby("fp")
    rep["fp_size"] = g.fp.transform("size"); rep["fp_mal_share"] = g.label.transform("mean")
    rep["fp_conflict"] = ((rep.fp_mal_share > 0) & (rep.fp_mal_share < 1)).astype(int)
    for col in ["fp", "fp_size", "fp_mal_share", "fp_conflict"]:
        test[col] = rep.set_index("row").loc[test.row, col].values
    mal = test[test.label == 1]

    # ---- reproduce preliminary finding 1
    md.append("\n## 1. Detection per family (reproduces preliminary finding 1)\n\n")
    rows = []
    for fam, gg in test.groupby("family"):
        r = {"family": fam, "April reports": f"{len(gg):,}"}
        for m in MODELS:
            r[f"flagged by {m}"] = c(gg[f"flag_{m}"].sum(), len(gg))
        rows.append(r)
    md.append(md_table(pd.DataFrame(rows)))
    miss8 = mal[mal.flag_finetune_k8 == 0]
    rc = miss8.family.isin(["ransomware", "coinminer"]).sum()
    md.append(f"\n`finetune_k8` misses {len(miss8):,} of {len(mal):,} April malware reports; ransomware + coinminer "
              f"cause {c(rc, len(miss8))} of them (ransomware {int((miss8.family == 'ransomware').sum()):,}, "
              f"coinminer {int((miss8.family == 'coinminer').sum()):,}).\n")
    summary["f1"] = dict(misses=len(miss8), rc_share=pct(rc, len(miss8)),
                         ransom=[pct(mal[(mal.family == 'ransomware')][f'flag_{m}'].sum(), (mal.family == 'ransomware').sum()) for m in MODELS],
                         coin=[pct(mal[(mal.family == 'coinminer')][f'flag_{m}'].sum(), (mal.family == 'coinminer').sum()) for m in MODELS])

    # ---- the preliminary numbers, recomputed with the preliminary (CSV) definitions
    md.append("\n## 1b. Preliminary findings recomputed with the preliminary definitions\n\n")
    md.append("Same data and definitions as the first analysis (`results/samples.csv` columns and the coarse "
              "fingerprint); exact-hash versions follow in later sections.\n\n")
    P = []
    P.append(("1", "misses of finetune_k8", "2,381", f"{len(miss8):,}"))
    P.append(("1", "ransomware + coinminer share of misses", "59%", f"{pct(rc, len(miss8)):.1f}%"))
    for fam, pre in [("ransomware", "60.4% vs 66.5%"), ("coinminer", "66.3% vs 79.5%")]:
        gg = mal[mal.family == fam]
        P.append(("1", f"{fam} detection finetune_k8 vs frozen_k1", pre,
                  f"{pct(gg.flag_finetune_k8.sum(), len(gg)):.1f}% vs {pct(gg.flag_frozen_k1.sum(), len(gg)):.1f}%"))
    rw = mal[mal.family == "ransomware"]
    rm, rcg = rw[rw.flag_finetune_k8 == 0], rw[rw.flag_finetune_k8 == 1]
    P.append(("2", "ransomware file_access present, missed vs caught (tok_file_access > 0)", "1.4% vs 36.3%",
              f"{pct((rm['tok_file_access'] > 0).sum(), len(rm)):.1f}% vs {pct((rcg['tok_file_access'] > 0).sum(), len(rcg)):.1f}%"))
    P.append(("2", "ransomware >1 entry point, missed vs caught", "0.1% vs 33.6%",
              f"{pct((rm.n_entry_points > 1).sum(), len(rm)):.1f}% vs {pct((rcg.n_entry_points > 1).sum(), len(rcg)):.1f}%"))
    P.append(("2", "ransomware median API calls (n_apis_raw), missed vs caught", "about 140 both",
              f"{np.median(rm.n_apis_raw):.0f} vs {np.median(rcg.n_apis_raw):.0f}"))
    cmm = mal[(mal.family == "coinminer") & (mal.flag_finetune_k8 == 0)]
    fpv0 = cmm.fp.value_counts()
    gfp = cmm[cmm.fp == fpv0.index[0]]
    P.append(("3", "largest coarse fingerprint among coinminer misses", "265 of 568 (47%)",
              f"{len(gfp):,} of {len(cmm):,} ({pct(len(gfp), len(cmm)):.0f}%); fingerprint `{fpv0.index[0]}`"))
    P.append(("3", "that fingerprint in January", "none", f"{int(((rep.fp == fpv0.index[0]) & (rep.split == 'trainset')).sum()):,}"))
    P.append(("3", "mean finetune_k8 score (missed reports of that fingerprint)", "0.997", f"{gfp.finetune_k8.mean():.4f}"))
    P.append(("4", "1% FPR threshold finetune_k8 / frozen_k1", "0.99896 / 0.8745", f"{thr['finetune_k8']:.5f} / {thr['frozen_k1']:.4f}"))
    benp = test[test.label == 0]
    P.append(("4", "April benign scoring > 0.9, finetune_k8 / frozen_k1", "675 / 73",
              f"{int((benp.finetune_k8 > 0.9).sum()):,} / {int((benp.frozen_k1 > 0.9).sum()):,}"))
    top20 = benp.sort_values("finetune_k8", ascending=False).head(20)
    P.append(("4", "API calls of the 20 highest-scoring benign reports", "1 to 13",
              f"{int(top20.n_apis_raw.min())} to {int(top20.n_apis_raw.max())}"))
    fpc = rep[rep.fp_conflict == 1]
    P.append(("5", "fingerprints with both labels / reports / median API calls", "609 / 21,215 / 12",
              f"{fpc.fp.nunique():,} / {len(fpc):,} / {np.median(fpc.n_apis_raw):.0f}"))
    P.append(("5", "April malware in such groups", "26.5%", f"{pct(mal.fp_conflict.sum(), len(mal)):.1f}%"))
    P.append(("5", "finetune_k8 misses in such groups", "33.5%", f"{pct(miss8.fp_conflict.sum(), len(miss8)):.1f}%"))
    md.append("| finding | quantity | preliminary | recomputed |\n|---|---|---|---|\n")
    md.extend(f"| {a_} | {b_} | {c_} | {d_} |\n" for a_, b_, c_, d_ in P)
    summary["prelim"] = P

    # ---- task 1: exact duplicates and label conflicts
    md.append("\n## 2. Exact duplicates and label conflicts (task 1)\n\n")
    md.append("Exact hash = SHA-1 of Nebula's filtered report (`filter_and_normalize_report()` output) serialised "
              "with sorted keys. Second check: SHA-1 of the API-name sequence only. Groups are over all 92,700 reports.\n\n")
    rows = []
    for h, name in [("hash_report", "filtered report"), ("hash_apis", "API-name sequence"), ("fp", "coarse fingerprint (preliminary)")]:
        size = rep.groupby(h)[h].transform("size")
        same_split = rep.groupby([h, "split"])[h].transform("size") > 1
        jan_hashes = set(rep[rep.split == "trainset"][h])
        apr = rep[rep.split == "testset"]
        conf = rep[rep[f"{h}_conflict" if h != "fp" else "fp_conflict"] == 1]
        n_conf_groups = conf[h].nunique()
        tm = test[test.label == 1]
        conflict_col = f"{h}_conflict" if h != "fp" else "fp_conflict"
        rows.append({
            "grouping": name, "groups": f"{rep[h].nunique():,}",
            "reports with a duplicate in the same split": c(same_split.sum(), len(rep)),
            "April reports with a duplicate in January": c(apr[h].isin(jan_hashes).sum(), len(apr)),
            "groups with both labels": f"{n_conf_groups:,}",
            "reports in those groups": c(len(conf), len(rep)),
            "median API calls in those groups": f"{np.median(conf.n_calls):.0f}" if len(conf) else "–",
            "April malware in those groups": c(tm[conflict_col].sum(), len(tm)),
            "finetune_k8 misses in those groups": c(miss8[conflict_col].sum(), len(miss8)),
        })
        summary[f"conf_{h}"] = rows[-1]
    md.append(md_table(pd.DataFrame(rows)))
    conf = rep[rep.hash_report_conflict == 1]
    md.append("\nFamilies of the reports in exact-hash groups with both labels (all splits):\n\n")
    fam_tab = conf.groupby(["family", "split"]).size().unstack(fill_value=0)
    fam_tab["all"] = fam_tab.sum(axis=1)
    md.append(fam_tab.sort_values("all", ascending=False).to_markdown() + "\n")
    cg = conf.groupby("hash_report").agg(size=("label", "size"), malware=("label", "sum"), calls=("n_calls", "first"))
    md.append(f"\nExact-hash groups with both labels: {len(cg):,}; size median {cg['size'].median():.0f}, max {cg['size'].max():,}; "
              f"API calls per report in them: median {np.median(conf.n_calls):.0f}, p90 {np.percentile(conf.n_calls, 90):.0f}.\n")
    md.append("\nLargest exact-hash groups with both labels:\n\n")
    top = cg.sort_values("size", ascending=False).head(10).reset_index()
    top["benign"] = top["size"] - top.malware
    top["API names (first 6)"] = [", ".join(short(n) for n in rep_names[:6]) for rep_names in
                                   [Seqs_cache().names(int(rep[rep.hash_report == h].row.iloc[0])) for h in top.hash_report]]
    top["hash_report"] = top.hash_report.str[:10]
    md.append(md_table(top[["hash_report", "size", "malware", "benign", "calls", "API names (first 6)"]]))

    ga = rep.groupby("hash_apis").agg(size=("label", "size"), malware=("label", "sum"), calls=("n_calls", "first"),
                                      row=("row", "first"))
    ga = ga[(ga.malware > 0) & (ga.malware < ga["size"])].sort_values("size", ascending=False)
    lop = (ga.malware / ga["size"] >= 0.99) | (ga.malware / ga["size"] <= 0.01)
    md.append(f"\nLargest API-name-sequence groups with both labels ({len(ga):,} groups, {int(ga['size'].sum()):,} reports; "
              f"groups where one label is ≥ 99% of the reports: {int(lop.sum()):,}, holding "
              f"{c(ga[lop]['size'].sum(), ga['size'].sum())} of their reports):\n\n")
    ta = ga.head(12).reset_index()
    ta["benign"] = ta["size"] - ta.malware
    ta["families"] = [", ".join(f"{k} {v:,}" for k, v in rep[rep.hash_apis == h].family.value_counts().head(3).items())
                      for h in ta.hash_apis]
    ta["first API names"] = [", ".join(short(n) for n in Seqs_cache().names(int(r))[:6]) for r in ta.row]
    ta["hash_apis"] = ta.hash_apis.str[:10]
    md.append(md_table(ta[["hash_apis", "size", "malware", "benign", "calls", "families", "first API names"]]))

    # ---- task 2: why emulation stopped
    md.append("\n## 3. Why emulation stopped (task 2)\n\n")
    md.append("Stop reason of a report = `error.type` of its first entry point (the module entry), grouped into "
              "categories; raw types are in the second table. \"No error recorded\" means the entry point returned "
              "(or ended without an error record).\n\n")
    rep["stop"] = rep.main_error.map(stop_category)
    test["stop"] = rep.set_index("row").loc[test.row, "stop"].values
    test["main_error"] = rep.set_index("row").loc[test.row, "main_error"].values
    test["unsupported_apis"] = rep.set_index("row").loc[test.row, "unsupported_apis"].values
    cats = list(rep.stop.value_counts().index)
    rows = []
    for fam in ["ransomware", "coinminer"]:
        for st, nm in [(0, "missed"), (1, "caught")]:
            gg = test[(test.family == fam) & (test.flag_finetune_k8 == st)]
            r = {"April group (finetune_k8)": f"{fam} {nm}", "n": f"{len(gg):,}"}
            for k in cats:
                r[k] = c((gg.stop == k).sum(), len(gg))
            rows.append(r)
    md.append(md_table(pd.DataFrame(rows)))
    md.append("\nMost common raw error types (module entry), April ransomware and coinminer:\n\n")
    rows = []
    for fam in ["ransomware", "coinminer"]:
        for st, nm in [(0, "missed"), (1, "caught")]:
            gg = test[(test.family == fam) & (test.flag_finetune_k8 == st)]
            top_t = gg.main_error.value_counts().head(4)
            rows.append({"group": f"{fam} {nm}", "n": f"{len(gg):,}",
                         "top error types": "; ".join(f"`{k}` {c(v, len(gg))}" for k, v in top_t.items())})
    md.append(md_table(pd.DataFrame(rows)))
    md.append("\nUnsupported API names (any entry point), April ransomware and coinminer:\n\n")
    rows = []
    for fam in ["ransomware", "coinminer"]:
        for st, nm in [(0, "missed"), (1, "caught")]:
            gg = test[(test.family == fam) & (test.flag_finetune_k8 == st)]
            cnt = Counter(x for s in gg.unsupported_apis for x in s.split("|") if x)
            rows.append({"group": f"{fam} {nm}", "reports with an unsupported API": c((gg.unsupported_apis != "").sum(), len(gg)),
                         "top unsupported APIs": "; ".join(f"`{k}` ({v})" for k, v in cnt.most_common(5)) or "–"})
    md.append(md_table(pd.DataFrame(rows)))
    md.append("\nStop reason per family, January (trainset) vs April (testset):\n\n")
    rows = []
    for fam, gg in rep.groupby("family"):
        for sp, nm in [("trainset", "Jan"), ("testset", "Apr")]:
            g2 = gg[gg.split == sp]
            r = {"family": fam, "split": nm, "n": f"{len(g2):,}"}
            for k in cats:
                r[k] = c((g2.stop == k).sum(), len(g2))
            rows.append(r)
    md.append(md_table(pd.DataFrame(rows)))

    # ---- task 3: missed ransomware
    seqs = Seqs_cache()
    md.append("\n## 4. What the missed ransomware does (task 3)\n\n")
    groups = {
        "Apr missed": test[(test.family == "ransomware") & (test.flag_finetune_k8 == 0)].row.values,
        "Apr caught": test[(test.family == "ransomware") & (test.flag_finetune_k8 == 1)].row.values,
        "Jan (all)": rep[(rep.family == "ransomware") & (rep.split == "trainset")].row.values,
    }
    rr = rep.set_index("row")
    md.append("Missed/caught = `finetune_k8` at 1% FPR. Shares are of the reports in each group.\n\n")
    rows = []
    for k, idx in groups.items():
        g2 = rr.loc[idx]
        rows.append({"group": k, "n": f"{len(idx):,}",
                     "median API calls": f"{np.median(g2.n_calls):.0f}",
                     "file_access": c(g2.has_file_access.sum(), len(g2)),
                     "registry_access": c(g2.has_registry_access.sum(), len(g2)),
                     "network traffic": c(g2.has_network_traffic.sum(), len(g2)),
                     ">1 entry point": c((g2.n_entry_points > 1).sum(), len(g2)),
                     **{f"raw `{f}`": c(g2[f'raw_{f}'].sum(), len(g2)) for f in FIELDS_DROPPED}})
    md.append(md_table(pd.DataFrame(rows)))
    sets = {k: [seqs.short_set(i) for i in idx] for k, idx in groups.items()}
    md.append("\nFile-encryption related APIs (share of reports that call it at least once):\n\n")
    rows = []
    for nm, rx in ENC_PATTERNS + [("any FindFirst/FindNext + Write/Move", None)]:
        r = {"API": f"`{nm}`"}
        for k, ss in sets.items():
            if rx is None:
                hit = sum(any(x.startswith(("findfirstfile", "findnextfile")) for x in s) and
                          any(x == "writefile" or x.startswith("movefile") for x in s) for s in ss)
            else:
                rgx = re.compile(rx, re.I)
                hit = sum(any(rgx.match(x) for x in s) for s in ss)
            r[k] = c(hit, len(ss))
        rows.append(r)
    md.append(md_table(pd.DataFrame(rows)))
    md.append("\nAnti-analysis or delay APIs:\n\n")
    rows = []
    for nm, rx in ANTI_PATTERNS:
        rgx = re.compile(rx, re.I)
        r = {"API": f"`{nm}`"}
        for k, ss in sets.items():
            r[k] = c(sum(any(rgx.match(x) for x in s) for s in ss), len(ss))
        rows.append(r)
    md.append(md_table(pd.DataFrame(rows)))
    md.append("\nTop 15 API names by document frequency (lower-case, without DLL):\n\n")
    rows = []
    dfreq = {k: Counter(x for s in ss for x in s) for k, ss in sets.items()}
    for k in sets:
        rows.append({"group": k, "top APIs": "; ".join(f"`{x}` {pct(v, len(sets[k])):.0f}%" for x, v in dfreq[k].most_common(15))})
    md.append(md_table(pd.DataFrame(rows)))
    for (k1, k2) in [("Apr missed", "Apr caught"), ("Apr missed", "Jan (all)")]:
        n1, n2 = len(sets[k1]), len(sets[k2])
        lo = []
        for x in set(dfreq[k1]) | set(dfreq[k2]):
            a1, a2 = dfreq[k1][x], dfreq[k2][x]
            if a1 + a2 < 20:
                continue
            l = math.log((a1 + 0.5) / (n1 - a1 + 0.5)) - math.log((a2 + 0.5) / (n2 - a2 + 0.5))
            lo.append((l, x, a1, a2))
        lo.sort()
        md.append(f"\nAPIs whose document frequency differs most, {k1} (n={n1:,}) vs {k2} (n={n2:,}); "
                  "log-odds with +0.5 smoothing, APIs in ≥20 reports:\n\n")
        md.append("| direction | API | " + f"{k1} | {k2} | log-odds |\n|---|---|---|---|---|\n")
        for l, x, a1, a2 in lo[::-1][:10]:
            md.append(f"| more in {k1} | `{x}` | {c(a1, n1)} | {c(a2, n2)} | {l:+.2f} |\n")
        for l, x, a1, a2 in lo[:10]:
            md.append(f"| more in {k2} | `{x}` | {c(a1, n1)} | {c(a2, n2)} | {l:+.2f} |\n")
    md.append("\nMost common last 5 API calls (endings), per group:\n\n")
    rows = []
    for k, idx in groups.items():
        endings = Counter(" → ".join(seqs.short_list(i)[-5:]) for i in idx)
        for e, v in endings.most_common(4):
            rows.append({"group": k, "last 5 calls": f"`{e}`" if e else "(no calls)", "reports": c(v, len(idx))})
    md.append(md_table(pd.DataFrame(rows)))
    miss_r = rr.loc[groups["Apr missed"]]
    md.append("\nExact-hash structure of the missed ransomware: "
              f"{miss_r.hash_report.nunique():,} distinct filtered reports among {len(miss_r):,}; the largest exact group "
              f"holds {miss_r.hash_report.value_counts().iloc[0]:,}; {c(miss_r.hash_report_conflict.sum(), len(miss_r))} sit "
              "in a group that also has benign reports.\n")
    summary["ransom"] = {k: dict(n=len(idx)) for k, idx in groups.items()}

    # ---- task 4: big coinminer group
    md.append("\n## 5. The big coinminer group (task 4)\n\n")
    cm_miss = test[(test.family == "coinminer") & (test.flag_finetune_k8 == 0)]
    fpv = cm_miss.fp.value_counts()
    big_fp = fpv.index[0]
    grp = cm_miss[cm_miss.fp == big_fp]
    md.append(f"Coinminer misses (`finetune_k8`): {len(cm_miss):,}. Largest coarse fingerprint `{big_fp}` (tokens|API calls|"
              f"registry|network|file|apis tokens|entry points) holds {c(len(grp), len(cm_miss))} of them.\n\n")
    hv = grp.hash_report.value_counts()
    av = grp.hash_apis.value_counts()
    md.append(f"- Distinct exact filtered-report hashes in that group: {len(hv):,} (largest: {hv.iloc[0]:,} reports).\n"
              f"- Distinct API-name sequences: {len(av):,} (largest: {av.iloc[0]:,}).\n")
    allfp = test[test.fp == big_fp]
    md.append(f"- All April reports with that fingerprint: {len(allfp):,} ({dict(allfp.family.value_counts())}); "
              f"January reports with it: {int(((rep.fp == big_fp) & (rep.split == 'trainset')).sum()):,}; "
              f"January reports with the same exact filtered-report hash as the largest exact group: "
              f"{int(((rep.hash_report == hv.index[0]) & (rep.split == 'trainset')).sum()):,}.\n")
    for m in MODELS:
        md.append(f"- `{m}` on the whole fingerprint group: mean score {allfp[m].mean():.4f}, median {allfp[m].median():.4f}, "
                  f"flagged {c(allfp[f'flag_{m}'].sum(), len(allfp))} (threshold {thr[m]:.5f}).\n")
    rep_row = int(grp[grp.hash_report == hv.index[0]].row.iloc[0])
    target = seqs.names(rep_row)
    from rapidfuzz.distance import Levenshtein
    jan_cm = rep[(rep.family == "coinminer") & (rep.split == "trainset")]
    uniq = jan_cm.drop_duplicates("hash_apis")
    best = None
    tl = [x.lower() for x in target]
    for r in uniq.itertuples():
        s = [x.lower() for x in seqs.names(r.row)]
        if best is not None and abs(len(s) - len(tl)) >= best[0]:
            continue
        d = Levenshtein.distance(tl, s)
        if best is None or d < best[0]:
            best = (d, r.row, s)
    d, jrow, js = best
    jrr = rr.loc[jrow]
    md.append(f"\nClosest January coinminer by edit distance over API-name sequences (lower-case; {len(uniq):,} distinct "
              f"January coinminer sequences searched): `{jrr.sample_id}`, distance **{d}** "
              f"({len(tl)} vs {len(js)} calls; {int((rep.hash_apis == jrr.hash_apis).sum()):,} reports share that January sequence).\n\n")
    # minimal edit script (same alignment as the distance), consecutive edits merged into blocks
    ops = Levenshtein.editops(tl, js)
    blocks = []
    for op in ops:
        tag, i, j = op.tag, op.src_pos, op.dest_pos
        if blocks and blocks[-1]["tag"] == tag and i - blocks[-1]["i_end"] <= 1 and j - blocks[-1]["j_end"] <= 1:
            b_ = blocks[-1]
        else:
            b_ = {"tag": tag, "i0": i, "j0": j, "april": [], "jan": []}
            blocks.append(b_)
        if tag in ("replace", "delete"):
            b_["april"].append(tl[i])
        if tag in ("replace", "insert"):
            b_["jan"].append(js[j])
        b_["i_end"], b_["j_end"] = i, j
    md.append(f"Minimal edit script ({len(ops)} edits; `delete` = only in April, `insert` = only in January), "
              f"consecutive edits merged:\n\n| edit | at April call | April calls | January calls |\n|---|---|---|---|\n")
    for b_ in blocks:
        md.append(f"| {b_['tag']} | {b_['i0']} | {', '.join(short(x) for x in b_['april']) or '–'} | "
                  f"{', '.join(short(x) for x in b_['jan']) or '–'} |\n")
    md.append(f"\nLast 6 calls: April `{' → '.join(short(x) for x in tl[-6:])}`; January `{' → '.join(short(x) for x in js[-6:])}`.\n")

    with open(os.path.join(R, "coinminer_group_example.txt"), "w") as fh:
        fh.write(f"# One report of the big April coinminer group: {grp[grp.row == rep_row].sample_id.iloc[0]}\n"
                 f"# exact filtered-report hash {hv.index[0]}; {len(target)} API calls, one per line\n")
        fh.write("\n".join(target) + "\n")
    rep_rep = Nebula(a.nebula).report(entry_points_of(json.load(open(files[rep_row][3]))))
    with open(os.path.join(R, "coinminer_group_example_filtered.json"), "w") as fh:
        json.dump(rep_rep, fh, indent=1)
    md.append(f"\nThe full API-name list of the April report is in "
              f"[`coinminer_group_example.txt`](coinminer_group_example.txt); its whole filtered report is in "
              f"[`coinminer_group_example_filtered.json`](coinminer_group_example_filtered.json). "
              f"Its non-API fields: {json.dumps({k: v for k, v in rep_rep.items() if k != 'apis'})[:600]}\n")
    summary["coin"] = dict(miss=len(cm_miss), fp_size=len(grp), n_hash=len(hv), top_hash=int(hv.iloc[0]), dist=d,
                           mean8=float(allfp.finetune_k8.mean()))

    # ---- task 5: calibration
    md.append("\n## 6. Score calibration (task 5)\n\n")
    ben = test[test.label == 0]
    rows = []
    for m in MODELS:
        for t in [0.9, 0.99, 0.999]:
            hi = ben[ben[m] > t]
            rows.append({"model": m, "benign score >": t, "April benign reports": c(len(hi), len(ben)),
                         "median API calls": f"{np.median(hi.n_calls):.0f}" if len(hi) else "–",
                         "≤10 API calls": c((hi.n_calls <= 10).sum(), len(hi)) if len(hi) else "–",
                         "median exact-group size": f"{np.median(hi.hash_report_size):.0f}" if len(hi) else "–",
                         "in a group with malware": c((hi.hash_report_mal_share > 0).sum(), len(hi)) if len(hi) else "–",
                         "same API-name sequence as some malware": c((hi.hash_apis_mal_share > 0).sum(), len(hi)) if len(hi) else "–",
                         "median malware share of their group": f"{np.median(hi.hash_report_mal_share):.2f}" if len(hi) else "–"})
    md.append(md_table(pd.DataFrame(rows)))
    for m in MODELS:
        mx = test[m].max()
        near = test[test[m] >= mx - 0.0005]
        md.append(f"\n`{m}`: highest test score {mx:.5f}; {len(near):,} reports within 0.0005 of it "
                  f"({int((near.label == 0).sum()):,} benign, {int((near.label == 1).sum()):,} malware). "
                  f"The 1% FPR threshold {thr[m]:.5f} is {mx - thr[m]:.5f} below the highest score.\n")
    md.append("\nThe 10 highest-scoring April benign reports (`finetune_k8`):\n\n")
    top = ben.sort_values("finetune_k8", ascending=False).head(10)
    t2 = pd.DataFrame({"family": top.family, "finetune_k8": top.finetune_k8.map("{:.5f}".format),
                       "frozen_k1": top.frozen_k1.map("{:.4f}".format), "API calls": top.n_calls,
                       "exact group: malware / size": [f"{int(round(ms * sz)):,} / {int(sz):,}" for sz, ms in
                                                      zip(top.hash_report_size, top.hash_report_mal_share)],
                       "API-sequence group: malware / size": [f"{int(round(ms * sz)):,} / {int(sz):,}" for sz, ms in
                                                              zip(top.hash_apis_size, top.hash_apis_mal_share)],
                       "API names": [", ".join(short(x) for x in seqs.names(int(r))[:8]) for r in top.row]})
    md.append(md_table(t2))
    summary["calib"] = {m: [int((ben[m] > t).sum()) for t in [0.9, 0.99, 0.999]] for m in MODELS}
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from analyze import style, BLUE, ORANGE, INK, INK2, SURF
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 11, "axes.titleweight": "bold",
                         "axes.labelcolor": INK2, "text.color": INK, "figure.facecolor": SURF})
    os.makedirs(os.path.join(R, "plots"), exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    bins = np.linspace(0, 1, 51)
    for ax, m in zip(axes, MODELS):
        style(ax)
        ax.hist(test[test.label == 0][m], bins=bins, histtype="step", lw=2, color=BLUE, label=f"benign (n={int((y == 0).sum()):,})")
        ax.hist(test[test.label == 1][m], bins=bins, histtype="step", lw=2, color=ORANGE, label=f"malware (n={int((y == 1).sum()):,})")
        ax.axvline(thr[m], color=INK, ls="--", lw=1.2)
        ax.text(thr[m], ax.get_ylim()[1] if ax.get_ylim()[1] > 1 else 1, f" 1% FPR\n threshold\n {thr[m]:.4f}", fontsize=8,
                va="top", ha="right")
        ax.set_yscale("log"); ax.set_xlabel("score"); ax.set_title(m)
    axes[0].set_ylabel("April reports (log scale)"); axes[1].legend(frameon=False, loc="upper center", fontsize=8)
    fig.suptitle("Test-set score distributions", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(R, "plots", "score_hist.png"), dpi=150); plt.close(fig)

    # the top end, spread out: x = -log10(1 - score); 1 = 0.9, 2 = 0.99, 3 = 0.999
    big_rows = set(test[test.fp == big_fp].row)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, m in zip(axes, MODELS):
        style(ax)
        tx = lambda v: -np.log10(np.clip(1 - v, 1e-6, 1))
        bins = np.linspace(0, 5, 61)
        ax.hist(tx(test[test.label == 0][m]), bins=bins, histtype="step", lw=2, color=BLUE, label="benign")
        ax.hist(tx(test[(test.label == 1) & ~test.row.isin(big_rows)][m]), bins=bins, histtype="step", lw=2, color=ORANGE,
                label="malware (other)")
        ax.hist(tx(test[test.row.isin(big_rows)][m]), bins=bins, histtype="stepfilled", alpha=0.5, color=INK2,
                label="the 265-report coinminer group")
        ax.axvline(tx(np.array([thr[m]]))[0], color=INK, ls="--", lw=1.2)
        ax.text(tx(np.array([thr[m]]))[0], 3e3, f" threshold {thr[m]:.5f}", fontsize=8)
        ax.set_yscale("log"); ax.set_xticks([0, 1, 2, 3, 4, 5], ["0", "0.9", "0.99", "0.999", "0.9999", "0.99999"])
        ax.set_xlabel("score (axis spread out near 1)"); ax.set_title(m)
    axes[0].set_ylabel("April reports (log scale)"); axes[0].legend(frameon=False, loc="upper left", fontsize=8)
    fig.suptitle("The top end of the score range", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(R, "plots", "score_tail.png"), dpi=150); plt.close(fig)

    # ---- task 6: removing unlearnable reports
    md.append("\n## 7. Effect of removing unlearnable reports (task 6, analysis only)\n\n")
    md.append("TPR per family at 1% FPR, with the threshold recomputed on the April benign reports that remain. "
              "(a) removes every April report in an exact-hash group that contains both labels (groups over all splits); "
              "(b) removes reports with 10 or fewer API calls; (a+b) both.\n\n")
    variants = {"all": np.ones(len(test), bool), "(a) no label-conflict groups": test.hash_report_conflict.values == 0,
                "(b) > 10 API calls": test.n_calls.values > 10,
                "(a+b)": (test.hash_report_conflict.values == 0) & (test.n_calls.values > 10)}
    rows = []
    for vn, keep in variants.items():
        tt = test[keep]
        yy = tt.label.values
        r0 = {"subset": vn, "benign kept": f"{int((yy == 0).sum()):,}", "malware kept": f"{int((yy == 1).sum()):,}"}
        for m in MODELS:
            th = threshold(yy, tt[m].values)
            fl = tt[m].values > th
            r = dict(r0, model=m)
            r["all malware"] = c(fl[yy == 1].sum(), (yy == 1).sum())
            for fam in ["ransomware", "coinminer", "backdoor", "dropper", "keylogger", "rat", "trojan"]:
                sel = (tt.family.values == fam)
                r[fam] = f"{pct(fl[sel].sum(), sel.sum()):.1f}% ({int(fl[sel].sum()):,}/{int(sel.sum()):,})"
            rows.append(r)
    md.append(md_table(pd.DataFrame(rows)))

    with open(os.path.join(R, "tables.md"), "w") as fh:
        fh.write("".join(md))
    with open(os.path.join(R, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, default=str)
    log("wrote", os.path.join(R, "tables.md"))


_SEQS = None


def Seqs_cache():
    global _SEQS
    if _SEQS is None:
        _SEQS = Seqs()
    return _SEQS


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nebula", default=os.environ.get("NEBULA_ROOT", "../nebula"))
    ap.add_argument("--data-dir", default="../hf-git")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("collect")
    p.add_argument("--workers", type=int, default=os.cpu_count())
    p = sub.add_parser("analyze")
    p.add_argument("--data", default="../hier_data/speakeasy", help="folder with meta.csv from hier_nebula prepare")
    a = ap.parse_args()
    {"collect": cmd_collect, "analyze": cmd_analyze}[a.cmd](a)


if __name__ == "__main__":
    main()
