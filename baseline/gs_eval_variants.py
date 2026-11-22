"""
NOTES 27 Part 3 (CPU, stored scores): clean April comparison of the test-time variants (dedupe exact, dedupe name, multi-window max) with the final M1 and M3, and the combined scores directory for the attack tables.   (OURS)

    python -m baseline.gs_eval_variants --dirs <kernel output dirs of gs_variants> --fixj <Stage J scores dir> --ref stage_i/logits_fixed_models.npz --out <dir>

 * merges the seeds of the kernel outputs (scores_<m>_<variant>.npz) into <out>/combined/scores_<key>.npz, keys m1, m1_dx, m1_dn, m1_mw, m3, m3_dx, m3_dn, m3_mw (set order as gs_variants.SETS);
   the keys m1 and m3 are the plain scores of the Stage J files restricted to these sets (asserted equal to the plain scores of this run, <= 2e-3, and the unedited row to the stored April logits);
 * clean April metrics of every variant (unedited row), per-seed mean +- std, 10-seed ensembles, and the paired differences variant - final model with both bootstraps (descriptive; resolved = cluster interval of pAUC@1e-2 excludes 0);
 * removed-call and window statistics (April, per class).
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C, gap_final
from baseline.gs_variants import SETS
from baseline.twolevel_eval import april_meta, cluster_bootstrap
from baseline.v2pe_report import BOOT, COLS, md, metrics_of, ms

SEEDS = list(range(10))
VARS = [("dx", "dedupe_exact", "dedupe (exact repeats)"), ("dn", "dedupe_name", "dedupe (same API name)"), ("mw", "multiwin", "multi-window max")]
BASE = {"m1": "M1 Nebula", "m3": "M3 ATT+bal"}


def merge(dirs, fam, variant):
    out = {}
    for d in dirs:
        p = os.path.join(d, f"scores_{fam}_{variant}.npz")
        if not os.path.exists(p):
            continue
        z = np.load(p)
        assert [str(n) for n in z["names"]] == [s[0] for s in SETS]
        for k in z.files:
            if k.startswith("seed"):
                assert k not in out, (fam, variant, k, "seed present twice")
                out[k] = z[k]
            elif k.startswith("first_"):
                out[k] = z[k]
    assert sorted(int(k[4:]) for k in out if k.startswith("seed") and k[4:].isdigit()) == SEEDS, (fam, variant, "not all 10 seeds present")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--fixj", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "logits", "labels.npz"))["y_test"].astype(int)
    _, _, groups = april_meta()
    ref = np.load(a.ref)
    stored = {"m1": ref["f1_test"].astype(np.float64), "m3": ref["f3_test"].astype(np.float64)}
    comb = os.path.join(a.out, "combined")
    os.makedirs(comb, exist_ok=True)
    names = [s[0] for s in SETS]
    Z, lab, stats = {}, {}, []
    for fam in ("m1", "m3"):
        d = np.load(os.path.join(a.fixj, f"scores_{fam}.npz"))
        jn = [str(n) for n in d["names"]]
        sel = [jn.index(n) for n in names]
        plain = merge(a.dirs, fam, "plain")
        for s in SEEDS:                                                    # plain of this run = Stage J plain scores = stored April logits
            assert np.abs(plain[f"seed{s}"] - d[f"seed{s}"][sel]).max() < 2e-3, (fam, s, "plain scores differ from Stage J")
            assert np.abs(plain[f"seed{s}"][0] - stored[fam][s]).max() < 2e-3, (fam, s, "unedited differs from the stored logits")
        np.savez_compressed(os.path.join(comb, f"scores_{fam}.npz"), names=np.array(names), tot=d["tot"][sel], **{f"seed{s}": d[f"seed{s}"][sel] for s in SEEDS})
        Z[fam], lab[fam] = stored[fam], BASE[fam] + " (final)"
        for key, variant, label in VARS:
            m = merge(a.dirs, fam, variant)
            np.savez_compressed(os.path.join(comb, f"scores_{fam}_{key}.npz"), names=np.array(names), tot=np.zeros((len(names), len(y)), dtype=np.int32), **{f"seed{s}": m[f"seed{s}"] for s in SEEDS})
            Z[f"{fam}_{key}"], lab[f"{fam}_{key}"] = np.stack([m[f"seed{s}"][0].astype(np.float64) for s in SEEDS]), f"{BASE[fam]} + {label}"
            ex = {}
            for dd in a.dirs:                                              # removed / windows statistics of the first seed file present
                p = os.path.join(dd, f"scores_{fam}_{variant}.npz")
                if os.path.exists(p):
                    z = np.load(p)
                    ex = {q: z[q] for q in ("tot", "removed", "nwin", "argwin") if q in z.files}
                    break
            for j, nm in enumerate(names):
                row = [lab[f"{fam}_{key}"], nm]
                for cls, mk in (("malware", y == 1), ("benign", y == 0)):
                    if variant != "multiwin":
                        row += [f"{np.median(ex['removed'][j][mk]):g} [{ex['removed'][j][mk].mean():.1f}]", f"{np.median(ex['tot'][j][mk]):g}"]
                    else:
                        row += [f"{np.median(ex['nwin'][j][mk]):g} [{ex['nwin'][j][mk].mean():.2f}]", f"{100 * (ex['tot'][j][mk] > 512 * 64).mean():.2f}% > 64 windows; arg-max window 0 in {100 * (ex['argwin'][j][mk] == 0).mean():.1f}%"]
                stats.append(row)
    from sklearn.metrics import roc_auc_score
    T = {k: metrics_of(y, z) for k, z in Z.items()}
    ens = {k: C.binary_metrics(y, z.mean(0), decision=0.0) for k, z in Z.items()}
    pairs = [(f"{f}_{k}", f) for f in ("m1", "m3") for k, _, _ in VARS]
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    cd = cluster_bootstrap(y, groups, Z, pairs, a.boot)
    idx_of = {"pauc@0.01": 3, "tpr@0.01": 1, "tpr@0.001": 0, "auc": 2}
    L = ["### Part 3: clean April results of the test-time variants next to the final M1 and M3 (corrected tokenizer, 10 seeds; descriptive; F1 = fixed threshold 0 on the logit)", "",
         md([[lab[k], len(T[k]["auc"])] + [ms(T[k][c], d) for c, _, d in COLS] for k in Z], ["model", "n"] + [c[1] for c in COLS]), "", "10-seed ensembles:", "",
         md([[lab[k], f"{ens[k]['tpr@0.001']:.3f}", f"{ens[k]['tpr@0.01']:.3f}", f"{ens[k]['auc']:.4f}", f"{ens[k]['f1@0.5']:.3f}", f"**{ens[k]['pauc@0.01']:.3f}**", f"{ens[k]['pauc@0.001']:.3f}"] for k in Z], ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1 (threshold 0)", "**pAUC@1e-2**", "pAUC@1e-3"]), "",
         "### Paired differences variant - final model (points ×100; stratified and cluster 95% CI; seeds paired by index)", ""]
    rows = []
    for (n, b) in pairs:
        for c, lbl, d in BOOT:
            if c not in idx_of:
                continue
            dd = T[n][c] - T[b][c]
            ps = bs["ps"]["diffs"][f"{n} - {b}"][c]
            lo, hi = np.percentile(cd[(n, b)][:, idx_of[c]], [2.5, 97.5])
            rows.append([f"{lab[n]} − {lab[b]}", lbl, f"{100 * dd.mean():+.2f}", f"[{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"[{100 * lo:+.2f}, {100 * hi:+.2f}]", f"{int((dd > 0).sum())} up / {int((dd < 0).sum())} down",
                         ("**resolved**" if (lo > 0 or hi < 0) else "not resolved") if c == "pauc@0.01" else ""])
    L += [md(rows, ["difference", "metric", "mean difference", "stratified 95% CI", "cluster 95% CI", "seeds", "outcome (pAUC only)"]), "",
          "### Calls removed (dedupe) or windows (multi-window), April reports, median [mean] per report; first-512 total / token count of the edited report", "",
          md(stats, ["variant", "edit set", "malware: removed calls / windows", "malware: total tokens / note", "benign: removed calls / windows", "benign: total tokens / note"]), ""]
    open(os.path.join(a.out, "clean_tables.md"), "w").write("\n".join(L) + "\n")
    json.dump({"test": {k: {c: v.round(6).tolist() for c, v in m_.items()} for k, m_ in T.items()}}, open(os.path.join(a.out, "clean_results.json"), "w"))
    print("\n".join(L))


if __name__ == "__main__":
    main()
