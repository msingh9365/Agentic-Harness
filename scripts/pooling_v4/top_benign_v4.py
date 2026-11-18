#!/usr/bin/env python
"""
Round 4, step 3: do M and ATT change the low-FPR weakness of C? The 20 highest-scoring April benign reports of the 5-seed
ensembles of C (J), M and ATT and of the released Nebula (as results/robustness item 3).

    python scripts/pooling_v4/top_benign_v4.py --src-v4 <Kaggle output of the round-4 runs>

Ensemble = mean logit of seeds 0-4 (Kaggle logits of the last epoch). Per list: first 30 API names, source, chunks, calls, whether the
API-name sequence also occurs in a malware report (April / January), overlap with the other lists, and the TPR at 0.1% FPR of the model
(threshold from all April benign scores; 1 benign report = 0.0125% of the 8,003).
Writes results/pooling_v4/top_benign.md and top_benign.json.
"""
import argparse
import json
import os
import sys

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_common as V  # noqa: E402
from v4_common import C, score512  # noqa: E402

TOP = 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-v4", default="/Users/manish/Code/mtp/pooling_v4_output")
    ap.add_argument("--epochs-new", type=int, default=2)
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("NTHREADS", os.cpu_count() or 4)))
    meta = C.meta_full()
    test = meta[meta.split == "testset"].reset_index(drop=True)
    N = len(test)
    y = test.label.values
    ben = np.flatnonzero(y == 0)
    z = {}
    for disp, (src, tmpl, ep) in {"C (J, 2 epochs)": (V.SRC["C"][0], "C_all_s{s}", 2), "C (J)": (V.SRC["C"][0], "C_all_s{s}", 10), "M (max)": (a.src_v4, "M_all_s{s}", a.epochs_new),
                                  "ATT (attention)": (a.src_v4, "ATT_all_s{s}", a.epochs_new)}.items():
        z[disp] = np.mean([np.load(os.path.join(src, "scores", tmpl.format(s=s) + "_epochs.npz"))["april"][ep - 1] for s in range(5)], 0)
    rel, _, z0 = V.load_model("released", 0)
    z["released Nebula"] = z0
    mal_apr, mal_jan = set(test.hash_apis[y == 1]), set(meta.hash_apis[(meta.split == "trainset") & (meta.label == 1)])
    reps = C.Reps()
    lists, md = {}, ["# The 20 highest-scoring April benign reports (round 4)\n",
                     "Ranking by logit among the 8,003 April benign reports; ensemble = mean logit of seeds 0–4. \"Shares sequence with malware\": the API-name sequence "
                     "also occurs in a malware report of April (A) or January (J). First 30 API names (dll prefix dropped, lower case).\n"]
    for name, zz in z.items():
        o = ben[np.argsort(-zz[ben])][:TOP]
        rows = []
        for r, i in enumerate(o, 1):
            row = test.iloc[i]
            apis = reps.get(int(row.row)).get("apis") or []
            names = [str(c.get("api_name", "")).split(".")[-1].lower() for c in apis]
            h = row.hash_apis
            sh = ("April" if h in mal_apr else "") + ("+" if (h in mal_apr and h in mal_jan) else "") + ("January" if h in mal_jan else "")
            rows.append({"rank": r, "row": int(row.row), "logit": f"{zz[i]:.2f}", "source": row.family, "chunks": int(row.n_chunks), "calls": len(names),
                         "shares sequence with malware": sh or "no", "first 30 calls": " ".join(names[:30]), "_hash": h})
        lists[name] = rows
        md += [f"\n## {name}\n", C.md_table(pd.DataFrame(rows).drop(columns=["_hash"]))]
    names_ = list(lists)
    summ = []
    for n in names_:
        L = lists[n]
        thr = C.thr_from(y, z[n], 0.001)
        tpr01 = float(((z[n] > thr) & (y == 1)).sum() / (y == 1).sum())
        r = {"model": n, "TPR at 0.1% FPR (of the ensemble)": f"{100 * tpr01:.1f}%", "median calls": f"{np.median([x['calls'] for x in L]):.0f}",
             "max calls": max(x["calls"] for x in L), "distinct sequences": len({x["_hash"] for x in L}),
             "one chunk": sum(x["chunks"] == 1 for x in L), "share sequence with malware": sum(x["shares sequence with malware"] != "no" for x in L),
             "source clean/syswow64": f"{sum(x['source'] == 'clean' for x in L)}/{sum(x['source'] != 'clean' for x in L)}"}
        for m in names_:
            r[f"in common with {m}"] = len({x["row"] for x in L} & {x["row"] for x in lists[m]}) if m != n else "–"
        summ.append(r)
    md += ["\n## Summary of the four lists\n", C.md_table(pd.DataFrame(summ))]
    from scipy.stats import spearmanr
    rho = {f"{x} vs {y_}": float(spearmanr(z[x][ben], z[y_][ben]).correlation) for i, x in enumerate(names_) for y_ in names_[i + 1:]}
    md += ["\nSpearman correlation of the benign scores (8,003 reports): " + "; ".join(f"{k} {v:.2f}" for k, v in rho.items()) + ".\n"]
    json.dump({"lists": {k: [{kk: vv for kk, vv in r.items() if kk != "_hash"} for r in v] for k, v in lists.items()}, "summary": summ, "spearman": rho},
              open(f"{V.OUT}/top_benign.json", "w"), indent=1, default=str)
    open(f"{V.OUT}/top_benign.md", "w").write("\n".join(md))
    print(C.md_table(pd.DataFrame(summ)))


if __name__ == "__main__":
    main()
