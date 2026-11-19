"""
Evaluation of baseline v2-PE against baseline v2 and the released checkpoint, following EVAL_PROTOCOL.md.   (OURS)

    python -m baseline.v2pe_report --raw results/v2_pe/raw --out results/v2_pe [--boot 1000]

Inputs  v2-PE: <raw>/seed<k>.json, seed<k>_epoch2_{test,val}_logits.npy (k = 0..9, from baseline/v2pe.py);
        v2: results/logits/v2.npz (the 10 seeds of REPORT 5.7 / 5.8); released checkpoint: results/logits/released.npz; labels: results/logits/labels.npz.
Primary metric pAUC@1e-2 (normalized, logits). Secondary: TPR@1e-3, TPR@1e-2, AUC, F1@0.5, pAUC@1e-3 (+ McClish, + literal float32 TPR@1e-3).
Statistics: per-seed mean +- std; the 10-seed ensemble (mean logit); stratified bootstrap over the April test reports (1,000 resamples, numpy seed 0, the same resamples as everywhere),
per-seed means ("ps") and ensembles ("ens"); per-seed paired differences (same seed index: same initial weights and data order) and the claim rule of EVAL_PROTOCOL.md section 5:
a difference counts only if the paired bootstrap 95% CI of the PRIMARY metric (per-seed means) excludes 0 AND the per-seed difference has the same sign in at least 7 of the 10 seeds.
Writes <out>/per_model.json, bootstrap.json, tables.md and results/logits/v2_pe.npz (same format as v2.npz: seed<k>_test, seed<k>_val, float32).
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import common as C
from baseline import gap_final

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = ["tpr@0.001", "tpr@0.01", "auc", "f1@0.5", "pauc@0.01", "pauc@0.001", "pauc_mcclish@0.01"]
COLS = [("tpr@0.001", "TPR@1e-3", 3), ("tpr@0.01", "TPR@1e-2", 3), ("auc", "AUC", 4), ("f1@0.5", "F1", 3), ("pauc@0.01", "**pAUC@1e-2**", 3), ("pauc@0.001", "pAUC@1e-3", 3)]
BOOT = [("pauc@0.01", "**pAUC@1e-2**", 3), ("tpr@0.001", "TPR@1e-3", 3), ("tpr@0.01", "TPR@1e-2", 3), ("auc", "AUC", 4), ("pauc@0.001", "pAUC@1e-3", 3)]
SEEDS = list(range(10))
PRIMARY = "pauc@0.01"


def metrics_of(y, Z):
    out = {k: [] for k in KEYS + ["tpr@0.001_literal_float32"]}
    for z in Z:
        m = C.binary_metrics(y, z, decision=0.0)
        for k in KEYS:
            out[k].append(m[k])
        out["tpr@0.001_literal_float32"].append(C.binary_metrics(y, C.sigmoid32(z))["tpr@0.001"])
    return {k: np.array(v) for k, v in out.items()}


def ms(a, d=3):
    a = np.asarray(a)
    return f"{a.mean():.{d}f} ± {a.std(ddof=1):.{d}f}" if len(a) > 1 else f"{a[0]:.{d}f}"


def md(rows, header):
    return "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n" + "".join("| " + " | ".join(str(c) for c in r) + " |\n" for r in rows)


def load(raw, dry=False):
    d = os.path.join(ROOT, "results", "logits")
    lab, v2, rel = np.load(os.path.join(d, "labels.npz")), np.load(os.path.join(d, "v2.npz")), np.load(os.path.join(d, "released.npz"))
    y_val, y_test = lab["y_val"].astype(int), lab["y_test"].astype(int)
    g = lambda npz, w: np.stack([npz[f"seed{k}_{w}"].astype(np.float64) for k in SEEDS])
    test = {"v2": g(v2, "test"), "released": rel["test"].astype(np.float64)[None]}
    val = {"v2": g(v2, "val"), "released": rel["val_in_sample"].astype(np.float64)[None]}
    if dry:                                                          # pipeline check: v2 stands in for v2-PE (all differences are exactly 0)
        test["v2_pe"], val["v2_pe"] = test["v2"].copy(), val["v2"].copy()
        return y_val, y_test, test, val, [None] * 10
    test["v2_pe"] = np.stack([np.load(os.path.join(raw, f"seed{k}_epoch2_test_logits.npy")).astype(np.float64) for k in SEEDS])
    val["v2_pe"] = np.stack([np.load(os.path.join(raw, f"seed{k}_epoch2_val_logits.npy")).astype(np.float64) for k in SEEDS])
    js = [json.load(open(os.path.join(raw, f"seed{k}.json"))) for k in SEEDS]
    return y_val, y_test, test, val, js


def scale_stats(y, Z):
    """Output scale as in REPORT 5.7: mean |logit|, mean and p99 of the benign logits, share of malware above logit 16.64 (the float32 sigmoid saturates), per model, averaged."""
    r = [[np.abs(z).mean(), z[y == 0].mean(), np.percentile(z[y == 0], 99), (z[y == 1] > 16.64).mean()] for z in Z]
    return np.array(r)


def weight_l2(paths):
    import torch
    out = []
    for p in paths:
        sd = torch.load(p, map_location="cpu", weights_only=True)
        out.append(sum(float(v.double().pow(2).sum()) for v in sd.values() if v.is_floating_point()) ** 0.5)      # as in 5.7 (the constant PE table included)
    return np.array(out)


def verdict(pair_ci, diffs, label_better="better"):
    """The claim rule of EVAL_PROTOCOL.md section 5 on the primary metric."""
    pos, neg = int((diffs > 0).sum()), int((diffs < 0).sum())
    excl = pair_ci["lo"] > 0 or pair_ci["hi"] < 0
    if excl and pair_ci["point"] > 0 and pos >= 7:
        return f"**RESOLVED: v2-PE better** (CI excludes 0 and positive in {pos}/10 seeds)"
    if excl and pair_ci["point"] < 0 and neg >= 7:
        return f"**RESOLVED: v2-PE worse** (CI excludes 0 and negative in {neg}/10 seeds)"
    return f"not resolved (CI {'excludes' if excl else 'contains'} 0; positive in {pos}/10, negative in {neg}/10 seeds)"


def build(y_val, y_test, test, val, js, boot, raw, weights):
    T = {g: metrics_of(y_test, Z) for g, Z in test.items()}
    V = {g: metrics_of(y_val, Z) for g, Z in val.items()}
    ens = {g: C.binary_metrics(y_test, Z.mean(0), decision=0.0) for g, Z in test.items() if len(Z) > 1}
    ens_val = {g: C.binary_metrics(y_val, Z.mean(0), decision=0.0) for g, Z in val.items() if len(Z) > 1}
    groups = {g: test[g] for g in ("released", "v2", "v2_pe")}
    bs = gap_final.bootstrap(y_test, groups, boot, pairs=[("v2_pe", "v2"), ("v2_pe", "released"), ("v2", "released")])
    names = {"released": "released checkpoint (1 model)", "v2": "baseline v2 (released code), 10 seeds", "v2_pe": "**baseline v2-PE (paper positional encoding), 10 seeds**"}
    L = ["### Test set (April), logit-ranked: per-seed mean ± std", ""]
    rows = [[names[g], len(T[g]["auc"])] + [ms(T[g][k], d) for k, _, d in COLS] + [ms(T[g]["pauc_mcclish@0.01"], 3), ms(T[g]["tpr@0.001_literal_float32"], 3)] for g in ("released", "v2", "v2_pe")]
    L.append(md(rows, ["model", "n"] + [c[1] for c in COLS] + ["McClish pAUC@1e-2", "TPR@1e-3 literal f32"]))
    L += ["", "10-seed ensemble (mean logit over the seeds):", ""]
    rows = [[names[g], f"{ens[g]['tpr@0.001']:.3f}", f"{ens[g]['tpr@0.01']:.3f}", f"{ens[g]['auc']:.4f}", f"{ens[g]['f1@0.5']:.3f}", f"**{ens[g]['pauc@0.01']:.3f}**", f"{ens[g]['pauc@0.001']:.3f}"] for g in ("v2", "v2_pe")]
    L.append(md(rows, ["model", "TPR@1e-3", "TPR@1e-2", "AUC", "F1", "**pAUC@1e-2**", "pAUC@1e-3"]))
    L += ["", "### Validation slice (7,530 reports; clean for v2 and v2-PE, in-sample for the released checkpoint): per-seed mean ± std", ""]
    rows = [[names[g], len(V[g]["auc"])] + [ms(V[g][k], d) for k, _, d in COLS] for g in ("v2", "v2_pe")]
    rows.append(["released checkpoint (in-sample: trained on this slice)", 1] + [ms(V["released"][k], d) for k, _, d in COLS])
    L.append(md(rows, ["model", "n"] + [c[1] for c in COLS]))
    if js[0] is not None:
        rows = []
        for e in (0, 1):
            vals = lambda k: np.array([j["per_epoch"][e]["val"][k] for j in js])
            rows.append([f"v2-PE epoch {e + 1}", ms(vals("tpr@0.001")), ms(vals("tpr@0.01")), ms(vals("auc"), 4), ms(vals("pauc@0.01")), ms(np.array([j["per_epoch"][e]["val_loss"] for j in js]), 4)])
        L += ["", "Per-epoch validation of v2-PE (stored during training):", "", md(rows, ["", "TPR@1e-3", "TPR@1e-2", "AUC", "pAUC@1e-2", "val loss"])]
    L += ["", f"### Differences (stratified bootstrap over the April test reports, {boot} resamples, numpy seed 0; 95% CI; points = x 100)", ""]
    rows = []
    for dname in ("v2_pe - v2", "v2_pe - released", "v2 - released"):
        for kind, kl in (("ps", "per-seed means"), ("ens", "10-seed ensembles")):
            for k, lab, d in BOOT:
                e = bs[kind]["diffs"][dname][k]
                rows.append([dname, kl, lab, f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]" + (" **resolved**" if e["resolved"] else " not resolved")])
    L.append(md(rows, ["difference", "statistic", "metric", "difference in points, 95% CI"]))
    L += ["", "### Per-seed paired differences v2-PE − v2 (the same seed index: the same initial weights and data order), points x 100", ""]
    rows = []
    for k, lab, d in BOOT:
        dd = T["v2_pe"][k] - T["v2"][k]
        rows.append([lab] + [f"{100 * x:+.1f}" for x in dd] + [f"{100 * dd.mean():+.2f} ± {100 * dd.std(ddof=1):.2f}", f"{int((dd > 0).sum())}/10"])
    L.append(md(rows, ["metric"] + [f"s{s}" for s in SEEDS] + ["mean ± std", "seeds > 0"]))
    dd = T["v2_pe"][PRIMARY] - T["v2"][PRIMARY]
    v_vs_v2 = verdict(bs["ps"]["diffs"]["v2_pe - v2"][PRIMARY], dd)
    dr = T["v2_pe"][PRIMARY] - T["released"][PRIMARY][0]                    # against the single released model: per-seed difference of each v2-PE seed
    v_vs_rel = verdict(bs["ps"]["diffs"]["v2_pe - released"][PRIMARY], dr)
    L += ["", "**Claim rule (EVAL_PROTOCOL.md section 5: CI of the primary metric excludes 0 AND the same sign in at least 7 of the 10 seeds):**", "",
          f"- v2-PE against v2 on pAUC@1e-2: {v_vs_v2}", f"- v2-PE against the released checkpoint on pAUC@1e-2 (each v2-PE seed against the one released model): {v_vs_rel}",
          f"- ensembles (10-seed): v2-PE − v2 on pAUC@1e-2 = {100 * bs['ens']['diffs']['v2_pe - v2'][PRIMARY]['point']:+.2f} points, CI [{100 * bs['ens']['diffs']['v2_pe - v2'][PRIMARY]['lo']:+.2f}, {100 * bs['ens']['diffs']['v2_pe - v2'][PRIMARY]['hi']:+.2f}]"]
    # output scale
    S = {g: scale_stats(y_test, test[g]) for g in ("released", "v2", "v2_pe")}
    rows = []
    for g in ("released", "v2", "v2_pe"):
        s = S[g]
        w = f"{weights[g].mean():.1f}" if weights.get(g) is not None else "n/a"
        rows.append([names[g], f"{s[:, 0].mean():.1f}", f"{s[:, 1].mean():.1f}", f"{s[:, 2].mean():.1f}", f"{100 * s[:, 3].mean():.0f}%", w])
    L += ["", "### Output scale (as in REPORT 5.7; April test, mean over the models)", "", md(rows, ["model", "mean abs(logit)", "benign logit mean", "benign logit p99", "malware above logit 16.6", "total weight L2 (incl. the constant PE table)"])]
    per = {"test": {g: {k: v.round(6).tolist() for k, v in m.items()} for g, m in T.items()}, "validation": {g: {k: v.round(6).tolist() for k, v in m.items()} for g, m in V.items()},
           "ensemble_test": {g: {k: v for k, v in m.items() if k not in ("roc_on_grid",)} for g, m in ens.items()},
           "ensemble_validation": {g: {k: v for k, v in m.items() if k not in ("roc_on_grid",)} for g, m in ens_val.items()},
           "scale": {g: S[g].round(4).tolist() for g in S}, "claim": {"v2_pe_vs_v2": v_vs_v2, "v2_pe_vs_released": v_vs_rel}}
    return "\n".join(L), per, bs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(ROOT, "results", "v2_pe", "raw"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "v2_pe"))
    ap.add_argument("--models", default=None, help="folder with seed<k>_epoch2_model.pt (default: --raw), for the weight norms")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--dry", action="store_true", help="pipeline check only: v2 stands in for v2-PE")
    ap.add_argument("--no-logits-npz", action="store_true")
    a = ap.parse_args()
    C.setup_nebula(require_patched=True)
    os.makedirs(a.out, exist_ok=True)
    y_val, y_test, test, val, js = load(a.raw, a.dry)
    big = os.path.join(ROOT, "results", "_models_big", "detection", "bpe50k")
    w = {"v2": weight_l2([os.path.join(big, "v2", f"seed{k}.pt") for k in SEEDS if os.path.exists(os.path.join(big, "v2", f"seed{k}.pt"))]) if os.path.isdir(os.path.join(big, "v2")) else None,
         "released": np.array([424.0])}
    pe_models = sorted(glob.glob(os.path.join(a.models or a.raw, "seed*_epoch2_model.pt")))
    w["v2_pe"] = weight_l2(pe_models) if pe_models else None
    txt, per, bs = build(y_val, y_test, test, val, js, a.boot, a.raw, w)
    open(os.path.join(a.out, "tables.md"), "w").write(txt + "\n")
    json.dump(per, open(os.path.join(a.out, "per_model.json"), "w"), indent=1)
    json.dump(bs, open(os.path.join(a.out, "bootstrap.json"), "w"), indent=1)
    if not a.dry and not a.no_logits_npz:
        np.savez_compressed(os.path.join(ROOT, "results", "logits", "v2_pe.npz"), **{f"seed{k}_{w_}": (test if w_ == "test" else val)["v2_pe"][k].astype(np.float32) for k in SEEDS for w_ in ("test", "val")})
    print(txt)


if __name__ == "__main__":
    main()
