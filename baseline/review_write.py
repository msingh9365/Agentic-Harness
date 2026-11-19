"""
Headline tables of RESULTS_FOR_REVIEW.md / REPORT 5.11, generated from the saved aggregate numbers (no number is typed by hand).   (OURS)

    python -m baseline.review_write [--dir results/review]

Reads table1.json, cluster_table1.json, attack_aggregates.json; writes headline_tables.md with: Table 2 (robustness: malware TPR / padded-benign FPR), the ATT − PE counts, Table 3 (the shortcut: malware-only
padding against the balanced versions, with the probe AUCs) and the 'Nebula paper vs ours' table.
"""
import argparse
import json
import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = {"released": "released checkpoint", "v2_pe": "v2-PE", "pebal": "PE+bal", "attbal": "ATT+bal", "attkeep": "ATT+bal-keep", "pekeep": "PE+bal-keep", "attaug": "ATT+aug", "peaug": "PE+aug"}


def md(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"] + ["| " + " | ".join(map(str, r)) + " |" for r in rows])


def cell(rec, t):
    tp, fp = rec[t]["tpr"], rec[t]["fpr"]
    return f"{100 * tp[0]:.1f} / {100 * fp[0]:.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "results", "review"))
    a = ap.parse_args()
    A = json.load(open(os.path.join(a.dir, "attack_aggregates.json")))
    T = json.load(open(os.path.join(a.dir, "table1.json")))
    out = []
    cols = [("random", "random_20_prepend"), ("random", "random_50_prepend"), ("random", "random_50_insert"), ("surrogate", "lgbm_20_prepend"), ("surrogate", "lgbm_50_prepend"), ("surrogate", "lgbm_50_insert"),
            ("surrogate", "v2pe_20_prepend"), ("surrogate", "v2pe_50_prepend"), ("surrogate", "v2pe_50_insert")]
    for t, tl in (("1e-2", "1% FPR"), ("1e-3", "0.1% FPR")):
        rows = []
        for f in ["released", "v2_pe", "pebal", "attbal", "attkeep", "pekeep"]:
            rows.append([L[f]] + [cell(A[src][f"{f}|{nm}"], t) for src, nm in cols])
        out += [f"**Table 2 ({tl} threshold). Malware flagged / padded benign flagged, in % (mean over the 10 seeds; the released checkpoint is one model). Calls prepended or inserted into every April report (9,399 malware, 8,003 benign).**", "",
                md(rows, ["model"] + [("random " if s == "random" else "LightGBM " if nm.startswith("lgbm") else "v2-PE ") + nm.split("_", 1)[1].replace("_", " ") for s, nm in cols]), ""]
    # white-box
    W = A["whitebox"]
    rows = []
    for f in ["released", "v2_pe", "pebal", "attbal", "attkeep", "pekeep"]:
        if f in W:
            c1, c3 = np.array(W[f]["1e-2"]), np.array(W[f]["1e-3"])
            rows.append([L[f], len(c1)] + [f"{100 * c1[:, k].mean():.1f} / {100 * c3[:, k].mean():.1f}" for k in (0, 5, 10, 20)])
    out += ["**Table 2 (white-box greedy attack, 500 April malware, seeds 0-2). Share still flagged at the 1% / 0.1% FPR thresholds after k prepended calls, in %.**", "", md(rows, ["model", "seeds", "k = 0", "k = 5", "k = 10", "k = 20"]), ""]
    # ATT - PE counts
    for nm, cmp_key in (("random padding", "random_cmp"), ("surrogate padding", "surrogate_cmp")):
        rows = []
        for pair, lab in (("attbal-pebal", "ATT+bal − PE+bal"), ("attkeep-pekeep", "ATT+bal-keep − PE+bal-keep")):
            for rate in ("malware TPR", "malware TPR, fit subset", "padded-benign FPR"):
                better = worse = both_b = both_w = n = 0
                for key, d in A[cmp_key].items():
                    p, setn, t, r = key.split("|")
                    if p != pair or r != rate:
                        continue
                    n += 1
                    if d["resolved"]:
                        pos = d["mean"] > 0
                        better += pos; worse += (not pos)
                        if d.get("cluster", {}).get("resolved"):
                            both_b += pos; both_w += (not pos)
                rows.append([lab, rate, n, f"{better} ({both_b})", f"{worse} ({both_w})", n - better - worse])
        out += [f"**Count of tests ({nm}; edit sets × the two thresholds) in which the first model is higher / lower than the second by the descriptive rule (CI excludes 0 and ≥ 7 of 10 seeds with the same sign). In brackets: the same under the cluster bootstrap over duplicate groups. For the padded-benign FPR a higher value is worse.**", "",
                md(rows, ["comparison", "rate", "tests", "first higher (cluster)", "first lower (cluster)", "neither"]), ""]
    # Table 3: shortcut
    rows = []
    P = A["probe"]
    for f in ["v2_pe", "pebal", "peaug", "attbal", "attaug"]:
        r5 = A["random"][f"{f}|random_5_prepend"]["1e-2"]
        r20 = A["random"][f"{f}|random_20_prepend"]["1e-2"]
        r50 = A["random"][f"{f}|random_50_prepend"]["1e-2"]
        tm = T["test"][f]
        pr = P.get(f)
        rows.append([L[f], f"{100 * np.mean(tm['tpr@0.01']):.1f}", f"{100 * r20['tpr'][0]:.1f} / {100 * r20['fpr'][0]:.1f}", f"{100 * r50['tpr'][0]:.1f} / {100 * r50['fpr'][0]:.1f}",
                     f"{pr['pooled'][0]:.3f}" if pr else "—", f"{pr['hidden'][0]:.3f}" if pr else "—"])
    out += ["**Table 3. The label shortcut: padding applied to malware training reports only (aug) against padding of all reports (bal). Clean TPR@1% FPR, then padded malware / padded benign flagged at the 1% threshold (random calls, prepend), and the probe AUC for \"padding present\" (pooled vector, 64-d hidden vector).**", "",
            md(rows, ["model", "clean TPR@1% (April)", "k=20 prepend: malware / benign flagged", "k=50 prepend: malware / benign flagged", "probe AUC, pooled", "probe AUC, hidden"]), ""]
    # paper vs ours
    rows = [["Nebula paper (Table 7, BPE, 2,116 batches, their test set)", "0.5213", "0.9657", "0.9136"]]
    for f in ["released", "v2_pe", "attbal", "pebal", "peaug"]:
        tm = T["test"][f]
        rows.append([f"ours: {L[f]} (published April set)", f"{np.mean(tm['tpr@0.001']):.3f}", f"{np.mean(tm['auc']):.4f}", f"{np.mean(tm['f1@0.5']):.4f}"])
    out += ["**Nebula paper vs ours. Different data (the paper's test set is not the published one; §6.1 of the report); for reference only.**", "", md(rows, ["model", "TPR@1e-3", "AUC", "F1 (threshold 0.5)"]), ""]
    open(os.path.join(a.dir, "headline_tables.md"), "w").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
