"""
Sensitivity of the Table 1 primary comparisons to duplicate reports: the same pAUC@1e-2 differences as baseline/review_tables.py, but the bootstrap resamples the CELLS (duplicate group, class) instead of single reports.   (OURS)

    python -m baseline.review_cluster --out results/review [--boot 1000]

Group = the hash of the API sequence of the April report (results/misses/reports.csv; 2,509 groups for 17,402 reports; ids in results/review/april_hash_apis_group.npy). EVAL_PROTOCOL.md uses the
stratified bootstrap over reports (every report independent); a group bootstrap is the more conservative statement, because identical reports get identical scores. Only logits are read; the result
is an aggregate table (cluster_table1.md / .json).
"""
import argparse
import json
import os

import numpy as np

from baseline import att_report as AR, common as C

ROOT = AR.ROOT
PAIRS = [("attbal", "v2_pe"), ("pebal", "v2_pe"), ("attbal", "pebal"), ("peaug", "v2_pe"), ("peaug", "pebal"), ("attaug", "attbal"), ("attkeep", "pekeep"), ("attkeep", "attbal")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "review"))
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "att_bal"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    g = np.load(os.path.join(a.out, "april_hash_apis_group.npy"))
    fams = sorted({f for p in PAIRS for f in p})
    Z = {f: AR.load_family(f, a.src)[0] for f in fams}
    cells = {c: np.where(y == c)[0] for c in (0, 1)}
    members = {}
    for c, idx in cells.items():
        u, inv = np.unique(g[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    rng = np.random.default_rng(0)
    draws = {p: [] for p in PAIRS}
    for b in range(a.boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        pa = {f: np.mean([C.pauc(y[sel], z[sel]) for z in Z[f]]) for f in fams}
        for p in PAIRS:
            draws[p].append(pa[p[0]] - pa[p[1]])
    rows, out = [], {}
    for (n, m) in PAIRS:
        d = np.array(draws[(n, m)])
        pt = np.mean([C.pauc(y, z) for z in Z[n]]) - np.mean([C.pauc(y, z) for z in Z[m]])
        per = np.array([C.pauc(y, zn) - C.pauc(y, zm) for zn, zm in zip(Z[n], Z[m])])
        lo, hi = np.percentile(d, [2.5, 97.5])
        out[f"{n}-{m}"] = {"point": float(pt), "lo": float(lo), "hi": float(hi), "seeds_above_0": int((per > 0).sum()), "resolved": bool((lo > 0 or hi < 0) and max((per > 0).sum(), (per < 0).sum()) >= 7)}
        rows.append([f"{n} − {m}", f"{100 * pt:+.2f}", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{int((per > 0).sum())}/10", "RESOLVED" if out[f"{n}-{m}"]["resolved"] else "not resolved"])
    text = ("**Cluster-bootstrap sensitivity (Table 1 primary metric pAUC@1e-2, per-seed means; duplicate groups resampled together, 1,000 resamples; points × 100).**\n\n| difference | point | 95% CI | seeds > 0 | claim rule |\n|---|---|---|---|---|\n"
            + "\n".join("| " + " | ".join(r) + " |" for r in rows))
    open(os.path.join(a.out, "cluster_table1.md"), "w").write(text + "\n")
    json.dump(out, open(os.path.join(a.out, "cluster_table1.json"), "w"), indent=1)
    print(text)


if __name__ == "__main__":
    main()
