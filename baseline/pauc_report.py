"""
Partial AUC (the low-FPR metric of EVAL_PROTOCOL.md) for every existing result, from the STORED LOGITS only: nothing is retrained and nothing is re-selected.   (OURS)

    python -m baseline.pauc_report --out results/pauc [--boot 1000]

Groups (April test set; validation slice where the model has a clean one)
  released     the authors' released checkpoint (1 model; its "validation" is in-sample: it was trained on all of January, so the validation numbers are only shown as such)
  prev_A       our previous recipe (A: lr 2.5e-4, 2/3 of January, fixed budget; 9 fold models of 3 CV repeats): no clean validation slice (the slice was in some of its training folds)
  v2_5, v2_10  baseline v2, seeds 0-4 / 0-9 (same recipe, data, slice and tokenizer); v2_s0_4 and v2_s5_9 are the two independent halves, to check that they agree
  B3 runs      upper, lower, lower_lasttoken (control), ar_lasttoken, mlm_bert, ar_flatten, mlm_theirs, each at the (lr, epoch) chosen on validation in B3 (choice.json, untouched)
Metrics: TPR@1e-3, TPR@1e-2, AUC, F1@0.5, pAUC@1e-2 (PRIMARY), pAUC@1e-3 (normalized: area under the ROC curve for FPR in [0, max_fpr] / max_fpr), and sklearn's McClish form.
Bootstrap: 1,000 stratified resamples of the April test reports (seed 0, the same resamples as in B2, B3 and F, so the earlier TPR numbers are reproduced exactly); "ps" = per-seed mean, "ens" = ensemble of the seeds.
Writes: <out>/per_model.json, bootstrap_groups.json, bootstrap_b3.json, tables.md, and the compressed logits under results/logits/.
"""
import argparse
import glob
import json
import os

import numpy as np

from baseline import b3_report as BR
from baseline import common as C
from baseline import gap, gap_final
from baseline import long_stats as LS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAP, B3RAW = os.path.join(ROOT, "results", "F_gap"), os.path.join(ROOT, "results", "B3_selfsup_v2", "raw")
KEYS = ["tpr@0.001", "tpr@0.01", "auc", "f1@0.5", "pauc@0.01", "pauc@0.001", "pauc_mcclish@0.01", "pauc_mcclish@0.001"]
COLS = [("tpr@0.001", "TPR@1e-3", 3), ("tpr@0.01", "TPR@1e-2", 3), ("auc", "AUC", 4), ("f1@0.5", "F1", 3), ("pauc@0.01", "**pAUC@1e-2**", 3), ("pauc@0.001", "pAUC@1e-3", 3)]
B3_NAMES = ["upper", "lower", "lower_lasttoken", "ar_lasttoken", "mlm_bert", "ar_flatten", "mlm_theirs"]


def metrics_of(y, Z):
    """{key: array over models} of binary_metrics on logits (decision 0), plus the literal float32 TPR@1e-3."""
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


def labels():
    """y_val (the F validation slice, in index order) and y_test; stored next to the logits so that nothing needs Kaggle."""
    p = os.path.join(ROOT, "results", "logits", "labels.npz")
    if os.path.exists(p):
        d = np.load(p)
        return d["y_val"].astype(int), d["y_test"].astype(int)
    lab = np.load(os.path.join(ROOT, "results", "_tokens_raw", "out", "labels.npz"))
    _, val = gap.val_slice(lab["ym_train"])
    y_val, y_test = lab["y_train"][val].astype(int), lab["y_test"].astype(int)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    np.savez_compressed(p, y_val=y_val.astype(np.int8), y_test=y_test.astype(np.int8), val_index=val.astype(np.int32))
    return y_val, y_test


def load_groups(y_test):
    """Test (and validation) logits of every group. Returns (test, val): {group: [models, N]}."""
    cal = np.load(os.path.join(GAP, "calib_arrays.npz"))
    assert (cal["y_test"].astype(int) == y_test).all()
    test, val = {}, {}
    test["released"] = cal["released_test"][None].astype(np.float64)
    test["prev_A"] = cal["ours_test"].astype(np.float64)
    seeds = sorted(int(os.path.basename(f)[4:].split("_")[0]) for f in glob.glob(os.path.join(GAP, "v2", "seed*_epoch2_test_logits.npy")))
    if not seeds:                                                  # the 5-seed run stored its logits as seed<k>_epoch2_*; (older layout: seed<k>_test_logits.npy)
        seeds = sorted(int(os.path.basename(f)[4]) for f in glob.glob(os.path.join(GAP, "v2", "seed*_test_logits.npy")))
    tl = lambda k, w: os.path.join(GAP, "v2", f"seed{k}_epoch2_{w}_logits.npy")
    t_v2 = {k: np.load(tl(k, "test")).astype(np.float64) for k in seeds}
    v_v2 = {k: np.load(tl(k, "val")).astype(np.float64) for k in seeds}
    for name, ks in (("v2_5", [k for k in seeds if k < 5]), ("v2_10", seeds), ("v2_s0_4", [k for k in seeds if k < 5]), ("v2_s5_9", [k for k in seeds if k >= 5])):
        if ks:
            test[name] = np.stack([t_v2[k] for k in ks]); val[name] = np.stack([v_v2[k] for k in ks])
    return test, val, seeds


def b3_runs(y_test):
    R = BR.load(B3RAW)
    ch = BR.choose(R)                                              # the same rule on the same validation curves: nothing is re-selected (checked against choice.json below)
    saved = json.load(open(os.path.join(ROOT, "results", "B3_selfsup_v2", "choice.json")))
    for r in B3_NAMES:
        assert (ch[r]["lr"], ch[r]["epoch"]) == (saved[r]["lr"], saved[r]["epoch"]), f"{r}: the chosen setting changed"
    runs = BR.chosen_runs(R, ch, B3RAW, y_test)
    val = {r: np.stack([np.load(os.path.join(B3RAW, f"seed{s}", f"{r}_lr{ch[r]['lr']:g}_val_logits.npy"))[ch[r]["epoch"] - 1].astype(np.float64) for s in BR.SEEDS]) for r in runs}
    return runs, val, ch


def save_logits(test, val, runs, b3val, ch, seeds):
    d = os.path.join(ROOT, "results", "logits")
    os.makedirs(d, exist_ok=True)
    np.savez_compressed(os.path.join(d, "v2.npz"), **{f"seed{k}_{w}": a.astype(np.float32) for k in seeds
                        for w, a in (("test", test["v2_10"][seeds.index(k)]), ("val", val["v2_10"][seeds.index(k)]))})
    cal = np.load(os.path.join(GAP, "calib_arrays.npz"))
    lab = np.load(os.path.join(d, "labels.npz"))
    np.savez_compressed(os.path.join(d, "released.npz"), test=cal["released_test"].astype(np.float32),
                        val_in_sample=cal["released_train"][lab["val_index"]].astype(np.float32))
    np.savez_compressed(os.path.join(d, "prev_recipe_A.npz"), test=cal["ours_test"].astype(np.float32))
    np.savez_compressed(os.path.join(d, "b3_chosen.npz"), **{f"{r}_seed{s}_{w}": (runs[r][s][1] if w == "test" else b3val[r][i]).astype(np.float32)
                        for r in runs for i, s in enumerate(BR.SEEDS) for w in ("test", "val")})
    json.dump({"b3_chosen": {r: {"lr": ch[r]["lr"], "epoch": ch[r]["epoch"]} for r in runs}, "v2": {"epoch": 2, "lr": 2e-3, "seeds": seeds},
               "note": "float32 logits; labels in labels.npz (y_val = the January validation slice of follow-up F in index order, y_test = April); released.npz: val_in_sample is IN-SAMPLE (the released model was trained on January)"},
              open(os.path.join(d, "README.json"), "w"), indent=1)


def abs_table(test, val, y_test, y_val, runs):
    T, V = {}, {}
    for g, Z in test.items():
        T[g] = metrics_of(y_test, Z)
    for g, Z in val.items():
        V[g] = metrics_of(y_val, Z)
    for r in runs:
        T[r] = metrics_of(y_test, np.stack([runs[r][s][1] for s in BR.SEEDS]))
    return T, V


def md(rows, header):
    return "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n" + "".join("| " + " | ".join(str(c) for c in r) + " |\n" for r in rows)


def tables(T, V, bg, bb, runs, ch, seeds, n_boot, welch):
    names = {"released": "released checkpoint (authors, 1 model)", "prev_A": "previous recipe A (9 fold models)", "v2_5": "**baseline v2, seeds 0-4**", "v2_10": "**baseline v2, seeds 0-9**",
             "v2_s0_4": "v2 seeds 0-4 (half 1)", "v2_s5_9": "v2 seeds 5-9 (half 2)"}
    b3n = {r: BR.LABELS[r] for r in B3_NAMES}
    L = ["### Test set: low-FPR metrics (logit-ranked; mean ± std over models)", ""]
    rows = []
    for g in [x for x in ("released", "prev_A", "v2_5", "v2_10", "v2_s0_4", "v2_s5_9") if x in T]:
        rows.append([names[g], len(T[g]["auc"])] + [ms(T[g][k], d) for k, _, d in COLS] + [ms(T[g]["pauc_mcclish@0.01"], 3), ms(T[g]["tpr@0.001_literal_float32"], 3)])
    for r in B3_NAMES:
        rows.append([f"B3: {b3n[r]} (lr {ch[r]['lr']:g}, ep {ch[r]['epoch']})", 5] + [ms(T[r][k], d) for k, _, d in COLS] + [ms(T[r]["pauc_mcclish@0.01"], 3), ms(T[r]["tpr@0.001_literal_float32"], 3)])
    L.append(md(rows, ["model", "n"] + [c[1] for c in COLS] + ["McClish pAUC@1e-2", "TPR@1e-3 literal f32"]))
    L += ["", "### Validation slice (7,530 reports, 2,467 benign): the same metrics where the slice is clean", ""]
    rows = []
    for g in ("v2_5", "v2_10"):
        if g in V:
            rows.append([names[g], len(V[g]["auc"])] + [ms(V[g][k], d) for k, _, d in COLS])
    for r in B3_NAMES:
        if r in b3val_cache:
            rows.append([f"B3: {b3n[r]}", 5] + [ms(b3val_cache[r][k], d) for k, _, d in COLS])
    L.append(md(rows, ["model", "n"] + [c[1] for c in COLS]))
    L += ["", "### How much more stable is pAUC@1e-2? Per-seed (per-model) std and coefficient of variation (std / mean), test set", ""]
    rows = []
    for g in [x for x in ("prev_A", "v2_5", "v2_10") if x in T] + B3_NAMES:
        a, b = T[g]["tpr@0.001"], T[g]["pauc@0.01"]
        rows.append([names.get(g, b3n.get(g)), len(a), f"{a.std(ddof=1):.3f}", f"{b.std(ddof=1):.3f}", f"{a.std(ddof=1) / a.mean():.2f}", f"{b.std(ddof=1) / b.mean():.2f}",
                     f"{(a.std(ddof=1) / a.mean()) / (b.std(ddof=1) / b.mean()):.1f}x"])
    L.append(md(rows, ["model", "n", "std TPR@1e-3", "std pAUC@1e-2", "CV TPR@1e-3", "CV pAUC@1e-2", "CV ratio"]))
    # groups: v2 against released and previous recipe; agreement of the halves
    L += ["", f"### Baseline v2 against the released model and the previous recipe (bootstrap 95% CI over the April test reports, {n_boot} stratified resamples; per-model means)", ""]
    rows = []
    for dname, e in bg["ps"]["diffs"].items():
        for k, lab, d in [("pauc@0.01", "pAUC@1e-2", 3), ("pauc@0.001", "pAUC@1e-3", 3), ("tpr@0.001", "TPR@1e-3", 3), ("tpr@0.01", "TPR@1e-2", 3), ("auc", "AUC", 4)]:
            x = e[k]
            rows.append([dname, lab, f"{x['point']:+.{d}f} [{x['lo']:+.{d}f}, {x['hi']:+.{d}f}]" + (" **resolved**" if x["resolved"] else " not resolved")])
    L.append(md(rows, ["difference", "metric", "difference of means, 95% CI"]))
    if welch:
        L += ["", "Agreement of the two independent halves of the v2 seeds (seeds 0-4 against 5-9; Welch t-test on the per-seed values; the bootstrap row `v2_s5_9 - v2_s0_4` above is the test-set view):", "",
              md([[k, f"{w['mean_a']:.3f}", f"{w['mean_b']:.3f}", f"{w['diff']:+.3f}", f"{w['p']:.2f}"] for k, w in welch.items()], ["metric", "seeds 0-4", "seeds 5-9", "difference", "Welch p"])]
    L += ["", "### B3 paired differences under pAUC (per-seed mean ± std over 5 seeds; seeds > 0; bootstrap 95% CI of the difference of the seed means, [points x 100])", ""]
    B = bb["bootstrap"]
    pairs = [("upper − lower", "upper", "lower", "vs_lower", +1), ("AR − lower", "ar_lasttoken", "lower", "vs_lower", +1), ("AR − its causal control", "ar_lasttoken", "lower_lasttoken", "vs_ctrl", +1),
             ("upper − AR", "ar_lasttoken", "upper", "upper_minus", -1), ("MLM − lower", "mlm_bert", "lower", "vs_lower", +1), ("upper − MLM", "mlm_bert", "upper", "upper_minus", -1),
             ("AR flatten − lower", "ar_flatten", "lower", "vs_lower", +1), ("MLM (authors') − lower", "mlm_theirs", "lower", "vs_lower", +1)]
    rows = []
    for label, name, ref, kind, sign in pairs:
        for k, lab in [("pauc@0.01", "**pAUC@1e-2**"), ("pauc@0.001", "pAUC@1e-3"), ("tpr@0.001", "TPR@1e-3"), ("tpr@0.01", "TPR@1e-2"), ("auc", "AUC")]:
            if label == "upper − lower":
                e, d = B["upper"][k]["ps"]["vs_lower"], LS.paired(runs, "upper", "lower", metrics=LS.METRICS_P)[k]
            elif kind == "upper_minus":
                e, d = B[name][k]["ps"]["upper_minus"], LS.paired(runs, name, "upper", sign=-1, metrics=LS.METRICS_P)[k]
            else:
                e, d = B[name][k]["ps"][kind], LS.paired(runs, name, ref, metrics=LS.METRICS_P)[k]
            f = 100.0
            rows.append([label, lab, f"{f * d['mean']:+.2f} ± {f * d['std']:.2f}", f"{d['n_positive']}/5",
                         f"{f * e['point']:+.2f} [{f * e['lo']:+.2f}, {f * e['hi']:+.2f}]" + (" **resolved**" if e["resolved"] else " not resolved")])
    L.append(md(rows, ["difference", "metric", "per-seed mean ± std", "seeds > 0", "bootstrap 95% CI (points)"]))
    L += ["", "Seed-ensemble flavour (mean logit over the 5 seeds) of the pAUC@1e-2 differences:", ""]
    rows = []
    for label, name, ref, kind, sign in pairs:
        e = B["upper"]["pauc@0.01"]["ens"]["vs_lower"] if label == "upper − lower" else B[name]["pauc@0.01"]["ens"][kind]
        rows.append([label, f"{100 * e['point']:+.2f} [{100 * e['lo']:+.2f}, {100 * e['hi']:+.2f}]" + (" **resolved**" if e["resolved"] else " not resolved")])
    L.append(md(rows, ["difference", "pAUC@1e-2 (ensemble), 95% CI (points)"]))
    return "\n".join(L)


b3val_cache = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "pauc"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    C.setup_nebula(require_patched=True)
    os.makedirs(a.out, exist_ok=True)
    y_val, y_test = labels()
    test, val, seeds = load_groups(y_test)
    runs, b3val, ch = b3_runs(y_test)
    for r in runs:
        b3val_cache[r] = metrics_of(y_val, b3val[r])
    save_logits(test, val, runs, b3val, ch, seeds)
    T, V = abs_table(test, val, y_test, y_val, runs)
    # bootstrap of the v2 / released / previous-recipe groups (+ agreement of the halves)
    groups = {g: test[g] for g in ("released", "prev_A", "v2_5", "v2_10", "v2_s0_4", "v2_s5_9") if g in test}
    pairs = [("v2_5", "released"), ("v2_5", "prev_A"), ("released", "prev_A")] + ([("v2_10", "released"), ("v2_10", "prev_A"), ("v2_s5_9", "v2_s0_4")] if "v2_10" in groups and len(seeds) == 10 else [])
    bg = gap_final.bootstrap(y_test, groups, a.boot, pairs=pairs)
    names = [r for r in B3_NAMES if r in runs]
    bb = {"n_boot": a.boot, "seeds": BR.SEEDS, "bootstrap": BR.bootstrap3(runs, y_test, names, n_boot=a.boot)}
    welch = {}
    if len(seeds) == 10:
        from scipy import stats as st
        for k, lab in (("pauc@0.01", "pAUC@1e-2"), ("tpr@0.001", "TPR@1e-3"), ("tpr@0.01", "TPR@1e-2"), ("auc", "AUC")):
            x, z = T["v2_s0_4"][k], T["v2_s5_9"][k]
            welch[lab] = {"mean_a": float(x.mean()), "mean_b": float(z.mean()), "diff": float(z.mean() - x.mean()), "p": float(st.ttest_ind(x, z, equal_var=False).pvalue)}
    json.dump({g: {k: v.round(6).tolist() for k, v in m.items()} for g, m in T.items()}, open(os.path.join(a.out, "per_model_test.json"), "w"), indent=1)
    json.dump({g: {k: v.round(6).tolist() for k, v in m.items()} for g, m in V.items()} | {f"B3_{r}": {k: v.round(6).tolist() for k, v in m.items()} for r, m in b3val_cache.items()},
              open(os.path.join(a.out, "per_model_validation.json"), "w"), indent=1)
    json.dump(bg, open(os.path.join(a.out, "bootstrap_groups.json"), "w"), indent=1)
    json.dump(bb, open(os.path.join(a.out, "bootstrap_b3.json"), "w"), indent=1)
    txt = tables(T, V, bg, bb, runs, ch, seeds, a.boot, welch)
    open(os.path.join(a.out, "tables.md"), "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
