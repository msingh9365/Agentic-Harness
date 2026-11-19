"""
Table 1 of RESULTS_FOR_REVIEW.md: clean April data for the released checkpoint, v2, v2-PE, ATT+bal, PE+bal, the two 'keep' models and the two malware-only models, following EVAL_PROTOCOL.md.   (OURS)

    python -m baseline.review_tables --out results/review [--boot 1000] [--reuse]

Inputs: results/logits/{released,v2,v2_pe}.npz and results/att_bal/<tag>/seed<k>_epoch2_{test,val}_logits.npy for tag in attbal, pebal, attkeep, pekeep, attaug, peaug (outputs of baseline/v2pe.py).
Per-seed mean +- std and 10-seed ensembles of pAUC@1e-2 (primary), TPR@1e-2, TPR@1e-3, AUC; stratified bootstrap over the April reports (1,000 resamples, numpy seed 0); the claim rule against v2-PE
(the CI of the per-seed means excludes 0 AND the same sign in >= 7 of the 10 seeds), also stated for the 10-seed ensembles. Only logits and aggregate numbers are read or written.
"""
import argparse
import json
import os

import numpy as np

from baseline import att_report as AR, common as C, gap_final
from baseline.v2pe_report import md, ms

ROOT = AR.ROOT
FAMS = ["released", "v2", "v2_pe", "attbal", "pebal", "attkeep", "pekeep", "attaug", "peaug"]
LABEL = dict(AR.LABEL, attkeep="ATT+bal-keep (attention, balanced padding, clean copies kept)", pekeep="PE+bal-keep (flatten, balanced padding, clean copies kept)",
             attaug="ATT+aug (attention, padding of malware only)", peaug="PE+aug (flatten, padding of malware only)")
KEYS = [("pauc@0.01", "pAUC@1e-2", 3), ("tpr@0.01", "TPR@1e-2", 3), ("tpr@0.001", "TPR@1e-3", 3), ("auc", "AUC", 4)]
PAIRS = [(f, "v2_pe") for f in FAMS[3:]] + [("attbal", "pebal"), ("attkeep", "pekeep"), ("attaug", "peaug"), ("attkeep", "attbal"), ("pekeep", "pebal"), ("attaug", "attbal"), ("peaug", "pebal")]


def verdict(e, d):
    pos, neg = int((d > 0).sum()), int((d < 0).sum())
    excl = e["lo"] > 0 or e["hi"] < 0
    if excl and e["point"] > 0 and pos >= 7:
        return "RESOLVED better"
    if excl and e["point"] < 0 and neg >= 7:
        return "RESOLVED worse"
    return "not resolved"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "review"))
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "att_bal"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--reuse", action="store_true")
    a = ap.parse_args()
    lab = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))
    y = lab["y_test"].astype(int)
    fams = [f for f in FAMS if AR.load_family(f, a.src) is not None]
    test = {f: AR.load_family(f, a.src)[0] for f in fams}
    T = {f: AR.metrics_of(y, test[f]) for f in fams}
    ens = {f: C.binary_metrics(y, test[f].mean(0), decision=0.0) for f in fams if len(test[f]) > 1}
    pairs = [p for p in PAIRS if p[0] in fams and p[1] in fams]
    os.makedirs(a.out, exist_ok=True)
    bpath = os.path.join(a.out, "bootstrap.json")
    if a.reuse and os.path.exists(bpath):
        bs = json.load(open(bpath))
    else:
        bs = gap_final.bootstrap(y, {f: test[f] for f in fams}, a.boot, pairs=pairs)
        json.dump(bs, open(bpath, "w"), indent=1)
    L = ["**Table 1. Clean April data (9,399 malware, 8,003 benign), logit-ranked; per-seed mean ± std (n = seeds) and 10-seed ensemble.**", ""]
    rows = []
    for f in fams:
        r = [LABEL[f], len(T[f]["auc"])] + [ms(T[f][k], d) for k, _, d in KEYS]
        r += [f"{ens[f][k]:.{d}f}" if f in ens else "—" for k, _, d in KEYS]
        rows.append(r)
    L.append(md(rows, ["model", "n"] + [c[1] for c in KEYS] + [c[1] + " (ens.)" for c in KEYS]))
    L += ["", "**Claim rule against v2-PE** (primary metric pAUC@1e-2; CI of the per-seed means excludes 0 and the same sign in ≥ 7 of 10 seeds; points × 100; ensembles: CI only):", ""]
    rows = []
    for (n, b) in pairs:
        e, ee = bs["ps"]["diffs"][f"{n} - {b}"]["pauc@0.01"], bs["ens"]["diffs"][f"{n} - {b}"]["pauc@0.01"]
        dd = T[n]["pauc@0.01"] - (T[b]["pauc@0.01"] if len(T[b]["pauc@0.01"]) == 10 else T[b]["pauc@0.01"][0])
        rows.append([f"{n} − {b}", f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]", f"{int((dd > 0).sum())}/10", verdict(e, dd),
                     f"{100 * ee['point']:+.2f} [{100 * ee['lo']:+.2f}, {100 * ee['hi']:+.2f}]" + (" (CI excludes 0; descriptive)" if ee["resolved"] else " (CI contains 0; descriptive)")])
    L.append(md(rows, ["difference", "per-seed means, pAUC@1e-2", "seeds > 0", "claim rule", "10-seed ensembles, pAUC@1e-2"]))
    L += ["", "**Other metrics, per-seed means, differences against v2-PE (points × 100, 95% CI):**", ""]
    rows = []
    for n in [f for f in fams if f in FAMS[3:]]:
        for k, lbl, _ in KEYS[1:]:
            e = bs["ps"]["diffs"][f"{n} - v2_pe"][k]
            rows.append([n, lbl, f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]", "CI excludes 0 (descriptive)" if e["resolved"] else "CI contains 0 (descriptive)"])
    L.append(md(rows, ["model − v2-PE", "metric", "difference", "CI"]))
    text = "\n".join(L)
    open(os.path.join(a.out, "table1.md"), "w").write(text + "\n")
    json.dump({"test": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in T.items()}, "ensemble_test": {f: {k: v for k, v in m.items() if k != "roc_on_grid"} for f, m in ens.items()}},
              open(os.path.join(a.out, "table1.json"), "w"), indent=1)
    print(text)


if __name__ == "__main__":
    main()
