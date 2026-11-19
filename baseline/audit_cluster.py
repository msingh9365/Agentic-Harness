"""
Duplicate-aware checks (audit item 1): cluster bootstrap over hash_apis groups for v2-PE vs released, ATT+bal vs released and ATT+bal vs v2-PE.   (OURS)

    python -m baseline.audit_cluster --out results/review [--boot 1000]

Table 1 (clean April): per-seed means of pAUC@1e-2 (primary), TPR@1e-2, TPR@1e-3, AUC; the cluster bootstrap resamples the cells (group, class) of the 2,509 groups (1,000 resamples, numpy seed 0), CI of the
difference of the means over seeds, seeds above 0 of 10 (the released checkpoint is one model: every seed of the other model is compared with it). The claim rule (CI excludes 0 and >= 7 of 10 seeds with the
same sign) is applied to the primary metric only; the other metrics are descriptive.
Table 2 (robustness): the same pairs on the random-padding test (REPORT 5.10 procedure), the surrogate-chosen padding and the white-box attack: malware TPR and padded-benign FPR at the 1% and 0.1% thresholds,
stratified and cluster bootstrap side by side (descriptive). White-box: 500 reports; the groups of those reports are resampled.
"""
import argparse
import json
import os

import numpy as np

from baseline import attack_run as AR_, attack_stats as A, common as C, review_attacks as RA

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAIRS = [("v2_pe", "released"), ("attbal", "released"), ("attbal", "v2_pe")]
LAB = {"released": "released checkpoint", "v2_pe": "v2-PE", "attbal": "ATT+bal"}
KEYS = [("pauc@0.01", "pAUC@1e-2"), ("tpr@0.01", "TPR@1e-2"), ("tpr@0.001", "TPR@1e-3"), ("auc", "AUC")]


def md(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def table1(y, groups, n_boot):
    from baseline import att_report as AR
    Z = {"released": AR.load_family("released", os.path.join(ROOT, "results", "att_bal"))[0], "v2_pe": AR.load_family("v2_pe", os.path.join(ROOT, "results", "att_bal"))[0], "attbal": AR.load_family("attbal", os.path.join(ROOT, "results", "att_bal"))[0]}
    cells = {c: np.where(y == c)[0] for c in (0, 1)}
    members = {}
    for c, idx in cells.items():
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    rng = np.random.default_rng(0)
    draws = {p: [] for p in PAIRS}
    for b in range(n_boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        m = {f: np.mean([C.roc_summary(y[sel], z[sel]) for z in Z[f]], axis=0) for f in Z}          # [TPR@1e-3, TPR@1e-2, AUC, pAUC@1e-2, pAUC@1e-3]
        for p in PAIRS:
            draws[p].append(m[p[0]] - m[p[1]])
        if b % 100 == 0:
            print(f"  table 1 cluster bootstrap {b}/{n_boot}", flush=True)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    per = {f: np.array([C.roc_summary(y, z) for z in Z[f]]) for f in Z}                              # [seeds, 5]
    out, rows = {}, []
    for (a_, b_) in PAIRS:
        D = np.array(draws[(a_, b_)])
        for key, lbl in KEYS:
            j = idx_of[key]
            d = per[a_][:, j] - (per[b_][:, j] if len(per[b_]) == len(per[a_]) else per[b_][0, j])
            lo, hi = np.percentile(D[:, j], [2.5, 97.5])
            pos, neg = int((d > 0).sum()), int((d < 0).sum())
            rule = ("RESOLVED " + ("better" if d.mean() > 0 else "worse") if (lo > 0 or hi < 0) and max(pos, neg) >= 7 else "not resolved") if key == "pauc@0.01" else ("CI excludes 0" if (lo > 0 or hi < 0) else "CI contains 0") + " (descriptive)"
            out[f"{a_}-{b_}|{key}"] = {"mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "seeds_above_0": pos, "rule": rule}
            rows.append([f"{LAB[a_]} − {LAB[b_]}", lbl + (" (primary)" if key == "pauc@0.01" else ""), f"{100 * d.mean():+.2f}", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{pos}/10", rule])
    text = ("**Table 1, duplicate-aware (cluster bootstrap over hash_apis groups; 1,000 resamples). Difference of the per-seed means in points; the released checkpoint is one model. The claim rule applies to the primary metric only; "
            "the other rows are descriptive.**\n\n" + md(rows, ["difference", "metric", "mean difference", "95% CI (cluster)", "seeds > 0", "outcome"]))
    return text, out


def whitebox_cluster(src, groups, n_boot):
    wb = RA.whitebox(src)
    out, rows = {}, []
    rng = np.random.default_rng(0)
    for a_, b_ in PAIRS:
        if a_ not in wb or b_ not in wb:
            continue
        ra, rb = {r["seed"]: r for r in wb[a_]}, {r["seed"]: r for r in wb[b_]}
        seeds = sorted(ra)
        sel = ra[seeds[0]]["sel"] if "sel" in ra[seeds[0]] else None
        grp = groups[sel]
        u, inv = np.unique(grp, return_inverse=True)
        W = np.stack([np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u))[inv] for _ in range(n_boot)]).astype(np.float64)
        for t, key in (("1e-2", "t1"), ("1e-3", "t01")):
            for k in (5, 10, 20):
                fa = np.stack([ra[s]["best"][k] > ra[s][key] for s in seeds]).astype(float)
                fb = np.stack([(rb[s] if s in rb else rb[min(rb)])["best"][k] > (rb[s] if s in rb else rb[min(rb)])[key] for s in seeds]).astype(float)
                d = (fa - fb).mean(1)
                dist = (((fa - fb) @ W.T) / W.sum(1)).mean(0)
                lo, hi = np.percentile(dist, [2.5, 97.5])
                out[f"{a_}-{b_}|{t}|k{k}"] = {"mean": float(d.mean()), "lo": float(lo), "hi": float(hi), "seeds_above_0": int((d > 0).sum()), "n_seeds": len(seeds)}
                rows.append([f"{LAB[a_]} − {LAB[b_]}", "1% FPR" if t == "1e-2" else "0.1% FPR", k, f"{100 * d.mean():+.1f}", f"[{100 * lo:+.1f}, {100 * hi:+.1f}]", f"{int((d > 0).sum())}/{len(seeds)}"])
    text = ("**White-box greedy, 500 reports, seeds 0-2 (the released checkpoint: its one run against every seed); share still flagged after k prepended calls; cluster bootstrap over the hash_apis groups of the 500 reports. Descriptive.**\n\n"
            + md(rows, ["difference", "threshold", "k", "mean difference (points)", "95% CI (cluster)", "seeds > 0"]))
    return text, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "review"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    groups = np.load(os.path.join(a.out, "april_hash_apis_group.npy"))
    src = os.path.join(a.out, "attack")
    boot, cboot = A.Boot(y, a.boot), A.Boot(y, a.boot, groups)
    L, agg = [], {}
    t1, o1 = table1(y, groups, a.boot)
    L.append(t1); agg["table1"] = o1
    RA.PAIRS = PAIRS
    for nm, prefix, names in (("random padding (REPORT 5.10 procedure, all April reports)", "a3pad", [AR_.pad_set_name(j) for j in range(7)]), ("surrogate-chosen padding (LightGBM and v2-PE-seed-0 rankings)", "a3", [AR_.set_name(j) for j in range(13)])):
        Z, tot = RA.load(src, prefix, ["released", "v2_pe", "attbal"])
        F = {t: {f: A.flags_of(Z[f], y, t) for f in Z} for t in RA.THR}
        text, out = RA.comparisons(nm, F, tot, y, boot, names, PAIRS, cboot)
        agg[prefix] = out
        L.append(text)
    t3, o3 = whitebox_cluster(src, groups, a.boot)
    L.append(t3); agg["whitebox"] = o3
    open(os.path.join(a.out, "audit_cluster.md"), "w").write("\n\n".join(L) + "\n")
    json.dump(agg, open(os.path.join(a.out, "audit_cluster.json"), "w"), indent=1)
    print("written audit_cluster.md")


if __name__ == "__main__":
    main()
