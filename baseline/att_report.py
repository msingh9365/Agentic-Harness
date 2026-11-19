"""
Evaluation of the ATT+bal follow-up following EVAL_PROTOCOL.md: ATT, ATT+bal (and PE+bal) against v2-PE (the baseline), v2 and the released checkpoint, plus the random benign padding test.   (OURS)

    python -m baseline.att_report --out results/att_bal [--boot 1000] [--no-pad]

Inputs  results/att_bal/<tag>/seed<k>_epoch2_{test,val}_logits.npy for tag in att, attbal, pebal (outputs of baseline/v2pe.py), results/logits/{v2,v2_pe,released}.npz, labels.npz;
        for the padding test results/att_bal/pad/april_pad.npz (baseline/make_pad.py --april) and results/att_bal/pad/pad_<family>.npz (baseline/padtest.py).
Primary metric pAUC@1e-2 (normalized, logits); secondary TPR@1e-3, TPR@1e-2, AUC, F1, pAUC@1e-3 (+ McClish, literal float32 TPR@1e-3). Per-seed mean +- std, 10-seed ensembles, stratified
bootstrap over the April test reports (1,000 resamples, numpy seed 0, the same resamples as everywhere), per-seed paired differences and the claim rule of EVAL_PROTOCOL.md section 5
(the CI of the primary metric excludes 0 AND the same sign in at least 7 of the 10 seeds).
Padding test: thresholds fixed at 1% FPR on the unedited April benign reports (per model: baseline/padtest.py thresholds); share of padded malware flagged, share of padded benign flagged.
"""
import argparse
import json
import os

import numpy as np

from baseline import common as C
from baseline import gap_final, padtest
from baseline.v2pe_report import BOOT, COLS, KEYS, metrics_of, ms, md, scale_stats, weight_l2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"
LABEL = {"released": "released checkpoint (1 model)", "v2": "baseline v2 (released code)", "v2_pe": "**baseline v2-PE** (the baseline)", "att": "v2-PE + attention pooling (ATT)",
         "attbal": "**ATT+bal** (attention pooling + balanced padding)", "pebal": "v2-PE + balanced padding (PE+bal, flatten)"}
NEW = ["att", "attbal", "pebal"]


def load_family(name, d):
    g = lambda npz, w: np.stack([npz[f"seed{k}_{w}"].astype(np.float64) for k in SEEDS])
    L = os.path.join(ROOT, "results", "logits")
    if name == "released":
        r = np.load(os.path.join(L, "released.npz"))
        return r["test"].astype(np.float64)[None], r["val_in_sample"].astype(np.float64)[None]
    if name in ("v2", "v2_pe"):
        z = np.load(os.path.join(L, f"{name}.npz"))
        return g(z, "test"), g(z, "val")
    p = os.path.join(d, name)
    if not all(os.path.exists(os.path.join(p, f"seed{k}_epoch2_test_logits.npy")) for k in SEEDS):
        return None
    return (np.stack([np.load(os.path.join(p, f"seed{k}_epoch2_test_logits.npy")).astype(np.float64) for k in SEEDS]),
            np.stack([np.load(os.path.join(p, f"seed{k}_epoch2_val_logits.npy")).astype(np.float64) for k in SEEDS]))


def verdict(ci, diffs, who):
    pos, neg = int((diffs > 0).sum()), int((diffs < 0).sum())
    excl = ci["lo"] > 0 or ci["hi"] < 0
    if excl and ci["point"] > 0 and pos >= 7:
        return f"**RESOLVED, {who} better** (CI excludes 0; positive in {pos}/10 seeds)"
    if excl and ci["point"] < 0 and neg >= 7:
        return f"**RESOLVED, {who} worse** (CI excludes 0; negative in {neg}/10 seeds)"
    return f"not resolved (CI {'excludes' if excl else 'contains'} 0; positive in {pos}/10, negative in {neg}/10 seeds)"


def pad_section(y_test, test, d, fams):
    """The padding test table (needs results/att_bal/pad/): per family and edit, share of padded malware flagged and of padded benign flagged at the 1%-FPR threshold of the unedited April set."""
    bp = os.path.join(d, "pad", "april_pad.npz")
    if not os.path.exists(bp):
        return None, None
    b = np.load(bp)
    pos, yb, edits = b["pos"], b["y"].astype(int), [str(e) for e in b["edits"]]
    mal, ben = yb == 1, yb == 0
    R = {}
    for f in fams:
        pp = os.path.join(d, "pad", f"pad_{f}.npz")
        if f not in test or not os.path.exists(pp):
            continue
        z = np.load(pp)
        tpr0, fpr0, tpr, fpr = [], [], [], []
        for s in SEEDS:
            thr = padtest.thresholds(test[f][s], y_test)
            zt = test[f][s][pos]
            tpr0.append((zt[mal] > thr).mean()); fpr0.append((zt[ben] > thr).mean())
            pz = z[f"seed{s}"]
            tpr.append([(pz[j][mal] > thr).mean() for j in range(len(edits))]); fpr.append([(pz[j][ben] > thr).mean() for j in range(len(edits))])
        R[f] = {"tpr0": np.array(tpr0), "fpr0": np.array(fpr0), "tpr": np.array(tpr), "fpr": np.array(fpr)}
    if not R:
        return None, None
    L = ["### Random benign padding test (thresholds fixed at 1% FPR on the unedited April benign reports; per-seed mean ± std over 10 seeds)", "",
         f"April malware reports ({int(mal.sum()):,}) and {int(ben.sum()):,} random benign April reports padded with k random calls (k = 5, 20, 50) of the EVAL pool (benign reports of the validation slice), "
         "prepended or inserted at random places. Cells: share of padded malware reports still flagged (TPR) / share of padded benign reports flagged (FPR).", ""]
    rows = []
    for f in R:
        r = R[f]
        rows.append([LABEL[f], f"{ms(r['tpr0'])} / {ms(r['fpr0'])}"] + [f"{ms(r['tpr'][:, j])} / {ms(r['fpr'][:, j])}" for j in range(len(edits))] + [f"{ms(r['tpr'].mean(1))} / {ms(r['fpr'].mean(1))}"])
    L.append(md(rows, ["model", "unedited TPR / FPR"] + [e.replace("_", " ") for e in edits] + ["mean of the 6 edits"]))
    L += ["", "Drop of the share of malware flagged against the unedited reports (points, mean over the 6 edits; per-seed mean ± std) and paired per-seed differences against v2-PE (same seed):", ""]
    rows = []
    base = R["v2_pe"]["tpr"].mean(1) - R["v2_pe"]["tpr0"] if "v2_pe" in R else None
    for f in R:
        drop = R[f]["tpr"].mean(1) - R[f]["tpr0"]
        row = [LABEL[f], f"{100 * drop.mean():+.1f} ± {100 * drop.std(ddof=1):.1f}", f"{100 * R[f]['fpr'].mean(1).mean():.2f}% ± {100 * R[f]['fpr'].mean(1).std(ddof=1):.2f}"]
        if base is not None and f != "v2_pe":
            dd = drop - base
            row += [f"{100 * dd.mean():+.1f} ± {100 * dd.std(ddof=1):.1f}", f"{int((dd > 0).sum())}/10"]
        else:
            row += ["", ""]
        rows.append(row)
    L.append(md(rows, ["model", "malware TPR change under padding (points)", "padded benign FPR (mean of 6 edits)", "change vs v2-PE (points), per seed", "seeds > 0"]))
    return "\n".join(L), {f: {k: v.round(5).tolist() for k, v in R[f].items()} | {"edits": edits} for f in R}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "att_bal"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--reuse", action="store_true", help="reuse results/att_bal/bootstrap.json (the 1,000-resample bootstrap of the same models) instead of recomputing it")
    a = ap.parse_args()
    C.setup_nebula(require_patched=True)
    lab = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))
    y_val, y_test = lab["y_val"].astype(int), lab["y_test"].astype(int)
    fams = ["released", "v2", "v2_pe"] + [f for f in NEW if load_family(f, a.out) is not None]
    test, val = {}, {}
    for f in fams:
        test[f], val[f] = load_family(f, a.out)
    new = [f for f in NEW if f in fams]
    T = {f: metrics_of(y_test, test[f]) for f in fams}
    V = {f: metrics_of(y_val, val[f]) for f in fams}
    ens = {f: C.binary_metrics(y_test, test[f].mean(0), decision=0.0) for f in fams if len(test[f]) > 1}
    pairs = [(n, b) for n in new for b in ("v2_pe", "v2", "released")] + ([("attbal", "att")] if "attbal" in new and "att" in new else []) + ([("attbal", "pebal")] if "attbal" in new and "pebal" in new else [])
    bpath = os.path.join(a.out, "bootstrap.json")
    if a.reuse and os.path.exists(bpath):
        bs = json.load(open(bpath))                       # same models, same resamples: only the padding section is new
        assert all(f"{n} - {b}" in bs["ps"]["diffs"] for n, b in pairs), "the stored bootstrap does not cover these comparisons"
    else:
        bs = gap_final.bootstrap(y_test, {f: test[f] for f in fams}, a.boot, pairs=pairs)
    L = ["### Test set (April), logit-ranked: per-seed mean ± std", ""]
    rows = [[LABEL[f], len(T[f]["auc"])] + [ms(T[f][k], d) for k, _, d in COLS] + [ms(T[f]["pauc_mcclish@0.01"], 3), ms(T[f]["tpr@0.001_literal_float32"], 3)] for f in fams]
    L.append(md(rows, ["model", "n"] + [c[1] for c in COLS] + ["McClish pAUC@1e-2", "TPR@1e-3 literal f32"]))
    L += ["", "10-seed ensembles (mean logit over the seeds):", ""]
    L.append(md([[LABEL[f], f"{ens[f]['tpr@0.001']:.3f}", f"{ens[f]['tpr@0.01']:.3f}", f"{ens[f]['auc']:.4f}", f"{ens[f]['f1@0.5']:.3f}", f"**{ens[f]['pauc@0.01']:.3f}**", f"{ens[f]['pauc@0.001']:.3f}"]
                 for f in fams if f in ens], ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1", "**pAUC@1e-2**", "pAUC@1e-3"]))
    L += ["", "**Validation slice** (7,530 reports; clean for all but the released checkpoint, which was trained on it): per-seed mean ± std", ""]
    L.append(md([[LABEL[f] + (" (in-sample)" if f == "released" else ""), len(V[f]["auc"])] + [ms(V[f][k], d) for k, _, d in COLS] for f in fams], ["model", "n"] + [c[1] for c in COLS]))
    L += ["", f"### Differences (stratified bootstrap over the April test reports, {a.boot} resamples, numpy seed 0; 95% CI; points = x 100)", ""]
    rows = []
    for (n, b) in pairs:
        for kind, kl in (("ps", "per-seed means"), ("ens", "10-seed ensembles")):
            for k, lbl, d in BOOT:
                e = bs[kind]["diffs"][f"{n} - {b}"][k]
                rows.append([f"{n} − {b}", kl, lbl, f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]" + (" **resolved**" if e["resolved"] else " not resolved")])
    L.append(md(rows, ["difference", "statistic", "metric", "difference in points, 95% CI"]))
    L += ["", "### Per-seed paired differences against v2-PE (the same seed index; points x 100) and the claim rule", ""]
    verdicts = {}
    for n in new:
        rows = []
        for k, lbl, d in BOOT:
            dd = T[n][k] - T["v2_pe"][k]
            rows.append([lbl] + [f"{100 * x:+.1f}" for x in dd] + [f"{100 * dd.mean():+.2f} ± {100 * dd.std(ddof=1):.2f}", f"{int((dd > 0).sum())}/10"])
        L += [f"**{LABEL[n]} − v2-PE**", "", md(rows, ["metric"] + [f"s{s}" for s in SEEDS] + ["mean ± std", "seeds > 0"])]
        for b in ("v2_pe", "v2"):
            dd = T[n][PRIMARY] - T[b][PRIMARY]
            verdicts[f"{n} vs {b}"] = verdict(bs["ps"]["diffs"][f"{n} - {b}"][PRIMARY], dd, n)
        dd = T[n][PRIMARY] - T["released"][PRIMARY][0]
        verdicts[f"{n} vs released"] = verdict(bs["ps"]["diffs"][f"{n} - released"][PRIMARY], dd, n)
    if "attbal" in new and "att" in new:
        verdicts["attbal vs att"] = verdict(bs["ps"]["diffs"]["attbal - att"][PRIMARY], T["attbal"][PRIMARY] - T["att"][PRIMARY], "attbal")
    if "attbal" in new and "pebal" in new:
        verdicts["attbal vs pebal"] = verdict(bs["ps"]["diffs"]["attbal - pebal"][PRIMARY], T["attbal"][PRIMARY] - T["pebal"][PRIMARY], "attbal")
    L += ["**Claim rule of EVAL_PROTOCOL.md section 5 on the primary metric pAUC@1e-2** (the CI of the per-seed means excludes 0 AND the same sign in at least 7 of the 10 seeds):", ""]
    L += [f"- {k}: {v}" for k, v in verdicts.items()]
    # output scale (+ weight norms where the models are on this machine)
    S = {f: scale_stats(y_test, test[f]) for f in fams}
    rows = [[LABEL[f], f"{S[f][:, 0].mean():.1f}", f"{S[f][:, 1].mean():.1f}", f"{S[f][:, 2].mean():.1f}", f"{100 * S[f][:, 3].mean():.0f}%"] for f in fams]
    L += ["", "### Output scale (as in REPORT 5.7; April test, mean over the models)", "", md(rows, ["model", "mean abs(logit)", "benign logit mean", "benign logit p99", "malware above logit 16.6"])]
    txt_pad, pad = pad_section(y_test, test, a.out, fams)
    if txt_pad:
        L += ["", txt_pad]
    text = "\n".join(L)
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "tables.md"), "w").write(text + "\n")
    json.dump({"test": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in T.items()}, "validation": {f: {k: v.round(6).tolist() for k, v in m.items()} for f, m in V.items()},
               "ensemble_test": {f: {k: v for k, v in m.items() if k != "roc_on_grid"} for f, m in ens.items()}, "scale": {f: S[f].round(4).tolist() for f in S}, "claims": verdicts, "padding": pad},
              open(os.path.join(a.out, "per_model.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap.json"), "w"), indent=1)
    print(text)


if __name__ == "__main__":
    main()
