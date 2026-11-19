#!/usr/bin/env python
"""
Item 3 of results/robustness: which April benign reports score highest for C (regime J) and for the released Nebula?

    python scripts/robustness/top_benign.py --src-j <regime J output>

Scores: C (J) = mean of the logits of its 10 seeds (weights after 10 epochs on all of January; the Kaggle logits of
scores/C_all_s<N>_epochs.npz); released Nebula = logit of the published weights (CPU). Ranking by logit, so scores
that saturate at probability 1.0 are not tied. For each of the 20 highest-scoring April benign reports: the first 30
API names (Nebula's filtered report), benign source (family: clean or windows_syswow64), number of 512-token chunks
(capped at 8), number of calls, and whether any malware report (April, or January) has the same API-name sequence
(hash_apis). Also: overlap of the two lists, the share of reports in each list whose sequence also occurs in malware,
and how the lists differ. Writes results/robustness/top_benign.md and top_benign.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "go_no_go"))
import common as C  # noqa: E402
from hier_nebula.model import build_level1  # noqa: E402

TOP = 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-j", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--nebula", default="../nebula")
    a = ap.parse_args()
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    N = len(test)
    plain = np.load(os.path.join(a.work, f"perturbed_tokens_{N}.npz"))["plain"]
    Zc = np.stack([np.load(os.path.join(a.src_j, "scores", f"C_all_s{s}_epochs.npz"))["april"][9] for s in range(10)])   # [10, N]
    zc = Zc.mean(0)
    torch.set_num_threads(4)
    rel = build_level1(a.nebula, vocab_size=50001, pretrained=True).eval()
    zr = np.zeros(N)
    with torch.no_grad():
        for i in range(0, N, 256):
            zr[i:i + 256] = rel(torch.from_numpy(plain[i:i + 256].astype(np.int64))).squeeze(-1).double().numpy()
    ref = C.load_scores("nebula", "april")[0].loc[test.row.values].values
    print("released: max |sigmoid(logit) - stored| =", float(np.abs(1 / (1 + np.exp(-zr)) - ref).max()), flush=True)
    y = test.label.values
    ben = np.flatnonzero(y == 0)
    mal_hash_apr = set(test.hash_apis[y == 1])
    allm = meta[meta.label == 1]
    mal_hash_jan = set(allm.hash_apis[allm.split == "trainset"])
    jan_ben = set(meta.hash_apis[(meta.split == "trainset") & (meta.label == 0)])
    reps = C.Reps()

    def top(z):
        o = ben[np.argsort(-z[ben])][:TOP]
        return o
    tops = {"C (J) ensemble": top(zc), "released Nebula": top(zr)}
    # benign April FPR threshold at 1% for each, to show where the list sits
    thr = {"C (J) ensemble": C.thr_from(y, zc, 0.01), "released Nebula": C.thr_from(y, zr, 0.01)}
    out, md = {}, ["# Item 3: the highest-scoring April benign reports for C (J) and for the released Nebula\n",
                   "Ranking by logit. C (J): mean logit of the 10 seeds trained on all of January (10 epochs). \"Shares sequence with malware\": "
                   "the report's API-name sequence (hash_apis) also occurs in a malware report of April (A) or January (J). Calls: the first 30 "
                   "API names of Nebula's filtered report (dll prefix dropped, lower-case).\n"]
    for name, o in tops.items():
        rows = []
        for r, i in enumerate(o, 1):
            row = test.iloc[i]
            apis = (reps.get(int(row.row)).get("apis") or [])
            names = [str(c.get("api_name", "")).split(".")[-1].lower() for c in apis]
            h = row.hash_apis
            rows.append({"rank": r, "row": int(row.row), "logit": f"{(zc if name.startswith('C') else zr)[i]:.2f}",
                         "source": row.family, "chunks": int(row.n_chunks), "calls": len(names),
                         "seen in January": "yes" if row.seen else "no",
                         "shares sequence with malware": ("April" if h in mal_hash_apr else "") + ("+" if (h in mal_hash_apr and h in mal_hash_jan) else "") + ("January" if h in mal_hash_jan else "") or "no",
                         "other benign April reports with the same sequence": int(((test.hash_apis == h) & (test.label == 0)).sum()) - 1,
                         "first 30 calls": " ".join(names[:30]), "_hash": h})
        out[name] = rows
        df = pd.DataFrame(rows)
        md.append(f"\n## {name}\n")
        md.append(f"Threshold at 1% FPR on April: logit {thr[name]:.2f}. The top-20 logits range from {rows[-1]['logit']} to {rows[0]['logit']}.\n")
        md.append(C.md_table(df.drop(columns=["_hash"])))
    ra, rb = [r["row"] for r in out["C (J) ensemble"]], [r["row"] for r in out["released Nebula"]]
    ha, hb = {r["_hash"] for r in out["C (J) ensemble"]}, {r["_hash"] for r in out["released Nebula"]}
    both = sorted(set(ra) & set(rb))
    # rank correlation among all April benign reports, and where each list's reports sit in the other model's ranking
    from scipy.stats import spearmanr
    rho = spearmanr(zc[ben], zr[ben]).correlation
    rank_in = lambda z: {int(test.row.values[i]): int(r) + 1 for r, i in enumerate(ben[np.argsort(-z[ben])])}
    rk_c, rk_r = rank_in(zc), rank_in(zr)
    share = lambda L: sum(1 for r in L if r["shares sequence with malware"] != "no")
    summary = {"overlap_reports": both, "n_overlap": len(both), "n_overlap_sequences": len(ha & hb), "spearman_all_benign": float(rho),
               "share_with_malware": {k: share(v) for k, v in out.items()},
               "median_calls": {k: float(np.median([r["calls"] for r in v])) for k, v in out.items()},
               "sources": {k: pd.Series([r["source"] for r in v]).value_counts().to_dict() for k, v in out.items()},
               "chunks": {k: pd.Series([r["chunks"] for r in v]).value_counts().sort_index().to_dict() for k, v in out.items()},
               "rank_of_released_top20_in_C": sorted(rk_c[r] for r in rb), "rank_of_C_top20_in_released": sorted(rk_r[r] for r in ra),
               "n_benign": int(len(ben)), "per_seed_C_top20_overlap_with_ensemble_top20": [
                   len(set(test.row.values[ben[np.argsort(-Zc[s][ben])][:TOP]]) & set(ra)) for s in range(10)]}
    json.dump({"lists": {k: [{kk: vv for kk, vv in r.items() if kk != "_hash"} for r in v] for k, v in out.items()}, "summary": summary},
              open("results/robustness/top_benign.json", "w"), indent=1, default=str)
    md.append("\n## Comparison\n")
    md.append(f"- Reports in both top-20 lists: {len(both)} ({len(ha & hb)} shared API-name sequences). Spearman correlation of the two scores over all "
              f"{len(ben):,} April benign reports: {rho:.2f}.\n- Where the other model ranks them (1 = highest benign score): the released model's top 20 sit at ranks "
              f"{summary['rank_of_released_top20_in_C']} in C; C's top 20 sit at ranks {summary['rank_of_C_top20_in_released']} in the released model.\n"
              f"- Top-20 reports whose sequence also occurs in a malware report: C {summary['share_with_malware']['C (J) ensemble']}/20, released "
              f"{summary['share_with_malware']['released Nebula']}/20. Median calls: C {summary['median_calls']['C (J) ensemble']:.0f}, released "
              f"{summary['median_calls']['released Nebula']:.0f}. Sources: C {summary['sources']['C (J) ensemble']}, released {summary['sources']['released Nebula']}. "
              f"Chunks: C {summary['chunks']['C (J) ensemble']}, released {summary['chunks']['released Nebula']}.\n"
              f"- Overlap of each C seed's own top 20 with the ensemble top 20: {summary['per_seed_C_top20_overlap_with_ensemble_top20']}.\n")
    open("results/robustness/top_benign.md", "w").write("\n".join(md))
    print("\n".join(md[-2:]))
    for name, v in out.items():
        print(name); [print(" ", r["rank"], r["row"], r["source"], r["chunks"], r["calls"], r["seen in January"], r["shares sequence with malware"], r["first 30 calls"][:90]) for r in v]


if __name__ == "__main__":
    main()
