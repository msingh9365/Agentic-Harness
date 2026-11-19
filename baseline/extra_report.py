"""
Tables of the further robustness tests (audit item 4) from the scores of baseline/extra_run.py: rare-API-name, block and copied-call padding (insert / prepend, k = 5, 20, 50), rotation of the 512 window, argument injection (k = 5, 20, 50)
and the test-time deduplication defence on v2-PE, for the released checkpoint, v2-PE, PE+bal and ATT+bal.   (OURS)

    python -m baseline.extra_report --src results/review/extra --out results/review

Same thresholds and statistics as §5.11: thresholds = 1% and 0.1% FPR of each model's unedited April benign scores (for the deduplication family: of its own deduplicated unedited reports), every April report is edited,
malware TPR and padded-benign FPR (mean ± std over the seeds that were scored; the number of seeds is in the table), the 'fits in 512 tokens' share, ATT+bal - PE+bal and the other pairs with the stratified and the cluster
bootstrap (descriptive). Only scores are read.
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import attack_stats as A, extra_edits as X, review_attacks as RA

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = {"released": "released checkpoint", "v2_pe": "v2-PE", "pebal": "PE+bal", "attbal": "ATT+bal", "v2_pe_dedup": "v2-PE + test-time deduplication"}
RA.LABEL.update(LAB)
NAMES = ["unedited"] + X.SET_NAMES
HEAD = ["rare_20_prepend", "rare_50_insert", "block_50_prepend", "block_50_insert", "copy_50_prepend", "copy_50_insert", "rot_50", "inj_50"]
PAIRS = [("attbal", "pebal"), ("attbal", "v2_pe"), ("pebal", "v2_pe"), ("v2_pe_dedup", "v2_pe")]


def md(rows, head):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def _stack(src, prefix_main, prefix_inj, fam):
    """scores [seeds, 24, N] of the seeds for which both the main file (GPU, all sets but injection) and the injection file (CPU) exist; NaN rows of one are filled from the other."""
    out = []
    for p in sorted(glob.glob(os.path.join(src, f"{prefix_main}_{fam}_seed*.npz")), key=lambda q: int(q.split("seed")[1][:-4])):
        sd = p.split("seed")[1][:-4]
        pi = os.path.join(src, f"{prefix_inj}_{fam}_seed{sd}.npz")
        if not os.path.exists(pi):
            continue
        zx, zi = np.load(p)["z"].astype(np.float64), np.load(pi)["z"].astype(np.float64)
        out.append(np.where(np.isnan(zx), zi, zx))
    return np.stack(out) if out else None


def load(src):
    Z, tot = {}, {}
    for f in ("released", "v2_pe", "pebal", "attbal"):
        z = _stack(src, "x", "xi", f)
        if z is not None:
            Z[f] = z
    z = _stack(src, "d", "di", "v2_pe")
    if z is not None:
        Z["v2_pe_dedup"] = z
    for st in ("ours", "released"):
        p = os.path.join(src, f"x_meta_{st}.npz")
        if os.path.exists(p):
            tot[st] = np.load(p)["totals"]
    return Z, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "results", "review", "extra"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "review"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    Z, tot = load(a.src)
    boot = A.Boot(y, a.boot)
    gp = os.path.join(a.out, "april_hash_apis_group.npy")
    cboot = A.Boot(y, a.boot, np.load(gp)) if os.path.exists(gp) else None
    seeds = {f: len(Z[f]) for f in Z}
    # paired comparisons use the seeds that exist for both models
    F = {t: {f: A.flags_of(Z[f], y, t) for f in Z} for t in RA.THR}
    L, agg = [], {}
    full_rows, head_rows = [], {t: [] for t in RA.THR}
    for f in [x for x in ("released", "v2_pe", "pebal", "attbal", "v2_pe_dedup") if x in Z]:
        fit_tot = tot["released" if f == "released" else "ours"]
        for j in range(1, len(NAMES)):
            fit = fit_tot[j] <= 512
            row = [LAB[f], len(Z[f]), NAMES[j].replace("_", " ")]
            rec = {}
            for t in RA.THR:
                pm_, _ = boot.rate(F[t][f][:, j], "mal")
                pb_, _ = boot.rate(F[t][f][:, j], "ben")
                rec[t] = {"tpr": [float(pm_.mean()), float(pm_.std(ddof=1)) if len(pm_) > 1 else 0.0], "fpr": [float(pb_.mean()), float(pb_.std(ddof=1)) if len(pb_) > 1 else 0.0]}
                row += [RA.pm(rec[t]["tpr"]), RA.pm(rec[t]["fpr"])]
            rec["share_fit_mal"] = None if (f == "v2_pe_dedup" or fit_tot[j].max() == 0) else float(fit[boot.pos].mean())     # injection rows: totals not computed on the GPU: n/a
            row.append("n/a" if rec["share_fit_mal"] is None else f"{100 * rec['share_fit_mal']:.1f}%")
            full_rows.append(row)
            agg[f"{f}|{NAMES[j]}"] = rec
    for t in RA.THR:
        for f in [x for x in ("released", "v2_pe", "pebal", "attbal", "v2_pe_dedup") if x in Z]:
            head_rows[t].append([LAB[f], len(Z[f])] + [f"{100 * agg[f'{f}|{n}'][t]['tpr'][0]:.1f} / {100 * agg[f'{f}|{n}'][t]['fpr'][0]:.1f}" for n in HEAD])
    for t, tl in (("1e-2", "1% FPR"), ("1e-3", "0.1% FPR")):
        unedited = []
        for f in [x for x in ("released", "v2_pe", "pebal", "attbal", "v2_pe_dedup") if x in Z]:
            pm_, _ = boot.rate(F[t][f][:, 0], "mal")
            pb_, _ = boot.rate(F[t][f][:, 0], "ben")
            unedited.append(f"{LAB[f]}: {100 * pm_.mean():.1f} / {100 * pb_.mean():.2f}")
        L += [f"**Table X ({tl} threshold). Further edits: malware flagged / padded benign flagged, in % (mean over the seeds scored; every April report is edited). Unedited malware flagged / benign flagged: " + "; ".join(unedited) + ".**", "",
              md(head_rows[t], ["model", "seeds"] + [n.replace("_", " ") for n in HEAD]), ""]
    cmp_text, cmp_out = [], {}
    for pair in PAIRS:
        if pair[0] not in Z or pair[1] not in Z:
            continue
        n = min(len(Z[pair[0]]), len(Z[pair[1]]))
        Fp = {t: {pair[0]: F[t][pair[0]][:n], pair[1]: F[t][pair[1]][:n]} for t in RA.THR}
        tot_use = {k: np.where(v.max(1, keepdims=True) == 0, 10 ** 6, v) for k, v in tot.items()}                    # rows without totals (injection): no 'fits in 512' comparison
        t_, o_ = RA.comparisons(f"Further edits, {LAB[pair[0]]} − {LAB[pair[1]]} ({n} paired seeds)", Fp, tot_use, y, boot, NAMES, [pair], cboot)
        cmp_text.append(t_); cmp_out.update(o_)
    counts = []
    for pair in PAIRS:
        for rate in ("malware TPR", "padded-benign FPR"):
            n_ = hi = lo = bh = bl = 0
            for k, d in cmp_out.items():
                p, s, t, r = k.split("|")
                if p != f"{pair[0]}-{pair[1]}" or r != rate:
                    continue
                n_ += 1
                if d["resolved"]:
                    pos = d["mean"] > 0
                    hi += pos; lo += (not pos)
                    if d.get("cluster", {}).get("resolved"):
                        bh += pos; bl += (not pos)
            if n_:
                counts.append([f"{LAB[pair[0]]} − {LAB[pair[1]]}", rate, n_, f"{hi} ({bh})", f"{lo} ({bl})", n_ - hi - lo])
    L += ["**Further edits: counts of tests (23 edit sets × two thresholds) in which the first model is higher / lower by the descriptive rule (CI excludes 0 and ≥ 7 of 10 paired seeds on the same side; in brackets the same under the cluster bootstrap). For the padded-benign FPR higher is worse.**", "",
          md(counts, ["comparison", "rate", "tests", "first higher (cluster)", "first lower (cluster)", "neither"]), ""]
    head_md = "\n".join(L)
    full = ["**All further-edit rows (seeds as listed).** " + f"Seeds scored per model: " + ", ".join(f"{LAB[f]} {seeds[f]}" for f in Z), "",
            md(full_rows, ["model", "seeds", "edit", "malware TPR @1%", "padded-benign FPR @1%", "malware TPR @0.1%", "padded-benign FPR @0.1%", "malware that fit in 512"])]
    open(os.path.join(a.out, "extra_tables.md"), "w").write(head_md + "\n\n" + "\n".join(full) + "\n\n" + "\n\n".join(cmp_text) + "\n")
    json.dump({"seeds": seeds, "rows": agg, "cmp": cmp_out}, open(os.path.join(a.out, "extra_aggregates.json"), "w"), indent=1)
    open(os.path.join(a.out, "extra_headline.md"), "w").write(head_md + "\n")
    print(head_md)


if __name__ == "__main__":
    main()
