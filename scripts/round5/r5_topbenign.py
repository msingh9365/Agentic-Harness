#!/usr/bin/env python
"""
Round 5, item 2 (last bullet): the 20 highest-scoring April benign reports of ATT+bal, as in results/robustness item 3, compared with C (J) and the released Nebula.

    python scripts/round5/r5_topbenign.py

ATT+bal: mean logit of its 10 seeds (G1, epoch 2). C (J): mean logit of its 10 seeds (10 epochs). Released: published weights. Ranking by logit. For every
report: source (clean / windows_syswow64), 512-token chunks, calls, seen in January, whether an April or January malware report has the same API-name
sequence (hash_apis), the first 30 API names. Comparison: overlap of the lists, Spearman correlation of the scores over all April benign reports, ranks of each
list in the other models. Writes results/round5/top_benign.md/json.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import r5_common as R  # noqa: E402
from r5_common import C, V  # noqa: E402
from r5_accuracy import load_logit  # noqa: E402

TOP = 20


def main():
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    y = test.label.values
    ben = np.flatnonzero(y == 0)
    Z = {"ATT+bal": np.stack([load_logit("ATTbal", s) for s in range(10) if R.available("ATTbal", s)]),
         "C (J)": np.stack([load_logit("C", s) for s in range(10)])}
    z = {k: v.mean(0) for k, v in Z.items()}
    z["released Nebula"] = R.load_model("released", 0)[2]
    names = list(z)
    mal_apr = set(test.hash_apis[y == 1])
    jm = meta[(meta.split == "trainset") & (meta.label == 1)]
    mal_jan = set(jm.hash_apis)
    reps = C.Reps()
    tops = {n: ben[np.argsort(-z[n][ben])][:TOP] for n in names}
    out, md = {}, ["# The 20 highest-scoring April benign reports (round 5, item 2)\n",
                   "Ranking by logit. ATT+bal and C (J): mean logit of the 10 seeds; released: published weights. \"Shares sequence with malware\": the API-name sequence also occurs in a "
                   "malware report of April or January. Calls: the first 30 API names of the filtered report (dll prefix dropped).\n"]
    for n in names:
        rows = []
        for r, i in enumerate(tops[n], 1):
            row = test.iloc[i]
            apis = reps.get(int(row.row)).get("apis") or []
            nm = [str(c.get("api_name", "")).split(".")[-1].lower() for c in apis]
            h = row.hash_apis
            sh = ("April" if h in mal_apr else "") + ("+" if h in mal_apr and h in mal_jan else "") + ("January" if h in mal_jan else "")
            rows.append({"rank": r, "row": int(row.row), "logit": f"{z[n][i]:.2f}", "source": row.family, "chunks": int(row.n_chunks), "calls": len(nm),
                         "seen in January": "yes" if row.seen else "no", "shares sequence with malware": sh or "no",
                         "other benign April reports with the same sequence": int(((test.hash_apis == h) & (test.label == 0)).sum()) - 1,
                         "first 30 calls": " ".join(nm[:30]), "_hash": h})
        out[n] = rows
        thr = C.thr_from(y, z[n], 0.001)
        md += [f"\n## {n}\n", f"Threshold at 0.1% FPR on April: logit {thr:.2f}; the top-20 logits range from {rows[-1]['logit']} to {rows[0]['logit']}.\n",
               C.md_table(pd.DataFrame(rows).drop(columns=["_hash"]))]
    from scipy.stats import spearmanr
    rank_in = lambda v: {int(test.row.values[i]): int(r) + 1 for r, i in enumerate(ben[np.argsort(-v[ben])])}
    rk = {n: rank_in(z[n]) for n in names}
    summ = {"n_benign": int(len(ben))}
    cmp_md = ["\n## Comparison\n"]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            ra, rb = [r["row"] for r in out[a]], [r["row"] for r in out[b]]
            both = sorted(set(ra) & set(rb))
            rho = spearmanr(z[a][ben], z[b][ben]).correlation
            ha, hb = {r["_hash"] for r in out[a]}, {r["_hash"] for r in out[b]}
            cmp_md.append(f"- {a} and {b}: {len(both)} reports in both top-20 lists ({len(ha & hb)} shared sequences); Spearman correlation over the {len(ben):,} benign April reports {rho:.2f}; "
                          f"the top 20 of {a} sit at ranks {sorted(rk[b][r] for r in ra)[0]}–{sorted(rk[b][r] for r in ra)[-1]} in {b} (median {int(np.median([rk[b][r] for r in ra]))}); "
                          f"the top 20 of {b} sit at ranks {sorted(rk[a][r] for r in rb)[0]}–{sorted(rk[a][r] for r in rb)[-1]} in {a} (median {int(np.median([rk[a][r] for r in rb]))}).")
            summ[f"{a}|{b}"] = {"overlap": len(both), "spearman": float(rho)}
    for n in names:
        v = out[n]
        cmp_md.append(f"- {n}: {sum(r['shares sequence with malware'] != 'no' for r in v)}/20 share their sequence with a malware report; median calls {np.median([r['calls'] for r in v]):.0f}; "
                      f"distinct sequences {len({r['_hash'] for r in v})}; sources {pd.Series([r['source'] for r in v]).value_counts().to_dict()}; chunks {pd.Series([r['chunks'] for r in v]).value_counts().sort_index().to_dict()}; "
                      f"seen in January {sum(r['seen in January'] == 'yes' for r in v)}/20.")
    # per-seed variability of ATT+bal's own top 20
    ra = [r["row"] for r in out["ATT+bal"]]
    ov = [len(set(test.row.values[ben[np.argsort(-Z["ATT+bal"][s][ben])][:TOP]]) & set(ra)) for s in range(len(Z["ATT+bal"]))]
    cmp_md.append(f"- Overlap of each ATT+bal seed's own top 20 with the ensemble top 20: {ov}.")
    md += cmp_md
    open(f"{R.OUT}/top_benign.md", "w").write("\n".join(md))
    json.dump({"lists": {k: [{kk: vv for kk, vv in r.items() if kk != "_hash"} for r in v] for k, v in out.items()}, "summary": summ, "seed_overlap": ov},
              open(f"{R.OUT}/top_benign.json", "w"), indent=1, default=str)
    print("\n".join(cmp_md))


if __name__ == "__main__":
    main()
