"""
P2 of NOTES 24: April reports whose API sequence (hash_apis) is in / not in a model's OWN training set ("seen" / "unseen"), from STORED logits only (no new April logit).   (OURS; CPU only)

    python -m baseline.gs_seen_unseen --labels <labels.npz with ym_train> --out results/groupsplit/stage_fgh/p2 [--boot 1000] [--procs 4]

Training sets: final models M1-M4 = all 75,298 January reports; Stage C models (and 3b) = the 66,580-report group-split training part; old-split models and the two-level A and B = the 67,768-report old training part.
Per subset: pAUC@1e-2 and TPR@1e-2 (threshold = the benign reports of the SUBSET, i.e. computed within the subset), mean ± std over the 10 seeds, 95% CI of the seed mean by the stratified bootstrap (reports resampled within
class) and by the cluster bootstrap (cells (hash_apis group, class) of the subset resampled), 1,000 resamples, numpy seed 0; pairwise differences inside a training-set group (same subset) with both CIs and the number of
seeds going each way; resolved = the cluster interval of pAUC@1e-2 excludes 0. Models whose stored logits are missing are skipped and listed.
"""
import argparse
import json
import os
from multiprocessing import Pool

import numpy as np

from baseline import att_report as AR, common as C, gap, groupsplit as G
from baseline.twolevel_eval import april_meta

ROOT = AR.ROOT
SEEDS = list(range(10))
SG = os.path.join(ROOT, "results", "groupsplit")


def load_models():
    L, miss = {}, []
    z = np.load(os.path.join(SG, "stage_d", "step5", "logits_final_models.npz"))
    L["M1 v2-PE (final)"] = ("jan", z["v2pe_test"].astype(np.float64))
    L["M3 ATT+bal (final)"] = ("jan", z["attbal_test"].astype(np.float64))
    p = os.path.join(SG, "stage_fgh", "stage_g", "logits_final_m2_m4.npz")
    if os.path.exists(p):
        z = np.load(p)
        L["M2 two-level, no padding (final)"] = ("jan", z["m2_test"].astype(np.float64))
        L["M4 ATT+bal-2L (final)"] = ("jan", z["m4_test"].astype(np.float64))
    else:
        miss.append("M2, M4 (Stage G logits not found)")
    z = np.load(os.path.join(SG, "stage_c", "logits_new_models.npz"))
    L["Stage C v2-PE (group-split part)"] = ("gs", z["v2pe_test"].astype(np.float64))
    L["Stage C ATT+bal (group-split part)"] = ("gs", z["attbal_test"].astype(np.float64))
    L["old-split v2-PE"] = ("old", AR.load_family("v2_pe", os.path.join(ROOT, "results", "att_bal"))[0])
    L["old-split ATT+bal"] = ("old", np.stack([np.load(os.path.join(ROOT, "results", "review", "attack", "a3pad_attbal.npz"))[f"seed{s}"][0].astype(np.float64) for s in SEEDS]))
    for fam, nm in (("a2l", "2L A (old split)"), ("b2l", "2L B, no padding (old split)")):
        p = os.path.join(ROOT, "results", "attbal_2l", "attack_scores", f"scores_{fam}.npz")
        if os.path.exists(p):
            d = np.load(p)
            L[nm] = ("old", np.stack([d[f"seed{s}"][0].astype(np.float64) for s in SEEDS]))
        else:
            miss.append(nm)
    return L, miss


def idx_cells(y, groups, kind):
    if kind == "strat":
        return [np.where(y == c)[0][None, :] for c in (0, 1)], None
    members = {}
    for c in (0, 1):
        idx = np.where(y == c)[0]
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    return members, True


def task(args):
    gname, sname, kind, y, groups, Z, pairs, n_boot = args           # Z: {name: [10, n_subset]}
    rng = np.random.default_rng(0)
    members, is_cluster = idx_cells(y, groups, kind)
    names = list(Z)
    draws = {n: [] for n in names}
    for _ in range(n_boot):
        if is_cluster:
            sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        else:
            sel = np.concatenate([members[c][0][rng.integers(0, len(members[c][0]), len(members[c][0]))] for c in (0, 1)])
        for n in names:
            draws[n].append(np.mean([C.roc_summary(y[sel], z[sel]) for z in Z[n]], axis=0))
    d = {n: np.array(v) for n, v in draws.items()}
    out = {"models": {n: {"pauc": [float(x) for x in np.percentile(d[n][:, 3], [2.5, 97.5])], "tpr01": [float(x) for x in np.percentile(d[n][:, 1], [2.5, 97.5])]} for n in names}, "pairs": {}}
    for a_, b_ in pairs:
        dd = d[a_] - d[b_]
        out["pairs"][f"{a_}|{b_}"] = {"pauc": [float(x) for x in np.percentile(dd[:, 3], [2.5, 97.5])], "tpr01": [float(x) for x in np.percentile(dd[:, 1], [2.5, 97.5])]}
    return (gname, sname, kind), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", default=os.path.join(SG, "stage_fgh", "p2"))
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--fixed-logits", default=None, help="NOTES 25: logits_fixed_models.npz (keys f1_test..f4_test) of the four models with the corrected tokenizer: added to the group `jan` (all of January)")
    ap.add_argument("--p3-logits", default=None, help="NOTES 27 P3: logits_p3.npz (keys r1_test, r3_test and, if the control was built, a1_test, a3_test): added to the group `jan` (all of January)")
    ap.add_argument("--groups", nargs="*", default=["jan", "gs", "old"])
    a = ap.parse_args()
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    fam, hsh, groups = april_meta()
    jt = G.january_table()
    trn, val = G.val_slice()
    otrn, _ = gap.val_slice(np.load(a.labels)["ym_train"])
    hj = jt["train"]["hash_apis"]
    sets = {"jan": set(hj), "gs": set(hj[trn]), "old": set(hj[otrn])}
    hap = jt["test"]["hash_apis"]
    models, missing = load_models()
    FIX = {"f1": "M1 v2-PE (fixed tokenizer)", "f2": "M2 two-level, no padding (fixed tokenizer)", "f3": "M3 ATT+bal (fixed tokenizer)", "f4": "M4 ATT+bal-2L (fixed tokenizer)"}
    if a.fixed_logits:
        zf = np.load(a.fixed_logits)
        for k, nm in FIX.items():
            models[nm] = ("jan", zf[f"{k}_test"].astype(np.float64))
    P3 = {"r1": "M1 v2-PE + address roles", "r3": "M3 ATT+bal + address roles", "a1": "M1 v2-PE + address control", "a3": "M3 ATT+bal + address control"}
    if a.p3_logits:
        zp = np.load(a.p3_logits)
        for k, nm in P3.items():
            if f"{k}_test" in zp.files:
                models[nm] = ("jan", zp[f"{k}_test"].astype(np.float64))
    masks = {g: np.array([h in s for h in hap]) for g, s in sets.items()}                  # seen
    tasks, meta = [], {}
    pair_defs = {"jan": [("M2 two-level, no padding (final)", "M1 v2-PE (final)"), ("M4 ATT+bal-2L (final)", "M3 ATT+bal (final)"), ("M4 ATT+bal-2L (final)", "M2 two-level, no padding (final)"), ("M3 ATT+bal (final)", "M1 v2-PE (final)")],
                 "gs": [("Stage C ATT+bal (group-split part)", "Stage C v2-PE (group-split part)")],
                 "old": [("old-split ATT+bal", "old-split v2-PE"), ("2L A (old split)", "old-split ATT+bal"), ("2L A (old split)", "2L B, no padding (old split)"), ("2L B, no padding (old split)", "old-split v2-PE")]}
    if a.fixed_logits:
        cur = {"f1": "M1 v2-PE (final)", "f2": "M2 two-level, no padding (final)", "f3": "M3 ATT+bal (final)", "f4": "M4 ATT+bal-2L (final)"}
        pair_defs["jan"] = pair_defs["jan"] + [(FIX[k], cur[k]) for k in FIX] + [(FIX["f3"], FIX["f1"]), (FIX["f4"], FIX["f3"]), (FIX["f4"], FIX["f2"])]
    if a.p3_logits:
        have = [k for k in P3 if P3[k] in models]
        pair_defs["jan"] = pair_defs["jan"] + [(P3["r1"], "M1 v2-PE (final)"), (P3["r3"], "M3 ATT+bal (final)")] + ([(P3["r1"], P3["a1"]), (P3["r3"], P3["a3"]), (P3["a1"], "M1 v2-PE (final)"), (P3["a3"], "M3 ATT+bal (final)")] if "a1" in have else [])
    for g in a.groups:
        names = [n for n, (gg, _) in models.items() if gg == g]
        pairs = [(p, q) for p, q in pair_defs[g] if p in names and q in names]
        for sname, sel in (("seen", masks[g]), ("unseen", ~masks[g])):
            Z = {n: models[n][1][:, sel] for n in names}
            for kind in ("strat", "cluster"):
                tasks.append((g, sname, kind, y[sel], groups[sel], Z, pairs, a.boot))
            meta[(g, sname)] = {"reports": int(sel.sum()), "malware": int(y[sel].sum()), "benign": int((1 - y[sel]).sum()), "groups": int(len(set(groups[sel]))), "names": names, "pairs": pairs, "sel": sel}
    with Pool(a.procs) as pool:
        res = dict(pool.map(task, tasks, chunksize=1))
    L = ["### P2: April reports seen / unseen by each model's OWN training set (stored logits; pAUC@1e-2 and TPR@1e-2 computed within the subset; mean ± std over 10 seeds; 95% CI of the seed mean: stratified | cluster)", ""]
    if missing:
        L += ["Not available: " + "; ".join(missing), ""]
    out = {"missing": missing, "subsets": {}, "models": {}, "pairs": {}}
    rows = []
    for g in a.groups:
        for sname in ("seen", "unseen"):
            m = meta[(g, sname)]
            out["subsets"][f"{g}|{sname}"] = {k: v for k, v in m.items() if k not in ("sel", "pairs", "names")}
            for n in m["names"]:
                pa = np.array([C.pauc(y[m["sel"]], z) for z in models[n][1][:, m["sel"]]])
                tp = np.array([C.roc_summary(y[m["sel"]], z)[1] for z in models[n][1][:, m["sel"]]])
                cs, cc = res[(g, sname, "strat")]["models"][n], res[(g, sname, "cluster")]["models"][n]
                out["models"][f"{n}|{sname}"] = {"pauc_per_seed": pa.tolist(), "tpr01_per_seed": tp.tolist(), "ci_strat": cs, "ci_cluster": cc}
                rows.append([n, {"jan": "all January (75,298)", "gs": "group-split part (66,580)", "old": "old training part (67,768)"}[g], sname, f"{m['reports']:,} / {m['malware']:,} / {m['benign']:,} / {m['groups']:,}",
                             f"{pa.mean():.3f} ± {pa.std(ddof=1):.3f}", f"[{cs['pauc'][0]:.3f}, {cs['pauc'][1]:.3f}] | [{cc['pauc'][0]:.3f}, {cc['pauc'][1]:.3f}]",
                             f"{tp.mean():.3f} ± {tp.std(ddof=1):.3f}", f"[{cs['tpr01'][0]:.3f}, {cs['tpr01'][1]:.3f}] | [{cc['tpr01'][0]:.3f}, {cc['tpr01'][1]:.3f}]"])
    L += [ "| model | training set of the model | April subset | reports / malware / benign / groups | pAUC@1e-2 | 95% CI (stratified \\| cluster) | TPR@1e-2 | 95% CI (stratified \\| cluster) |", "|---|---|---|---|---|---|---|---|"] + ["| " + " | ".join(r) + " |" for r in rows]
    prow = []
    for g in a.groups:
        for sname in ("seen", "unseen"):
            m = meta[(g, sname)]
            for p, q in m["pairs"]:
                dp = np.array([C.pauc(y[m["sel"]], z1) - C.pauc(y[m["sel"]], z2) for z1, z2 in zip(models[p][1][:, m["sel"]], models[q][1][:, m["sel"]])])
                dt = np.array([C.roc_summary(y[m["sel"]], z1)[1] - C.roc_summary(y[m["sel"]], z2)[1] for z1, z2 in zip(models[p][1][:, m["sel"]], models[q][1][:, m["sel"]])])
                cs, cc = res[(g, sname, "strat")]["pairs"][f"{p}|{q}"], res[(g, sname, "cluster")]["pairs"][f"{p}|{q}"]
                resolved = "**RESOLVED " + ("better" if dp.mean() > 0 else "worse") + "**" if (cc["pauc"][0] > 0 or cc["pauc"][1] < 0) else "not resolved"
                out["pairs"][f"{p}|{q}|{sname}"] = {"pauc_diff_per_seed": dp.tolist(), "tpr01_diff_per_seed": dt.tolist(), "ci_strat": cs, "ci_cluster": cc}
                prow.append([f"{p} − {q}", sname, f"{100 * dp.mean():+.2f}", f"[{100 * cs['pauc'][0]:+.2f}, {100 * cs['pauc'][1]:+.2f}]", f"[{100 * cc['pauc'][0]:+.2f}, {100 * cc['pauc'][1]:+.2f}]", f"{int((dp > 0).sum())} up / {int((dp < 0).sum())} down", resolved,
                             f"{100 * dt.mean():+.2f}", f"[{100 * cs['tpr01'][0]:+.2f}, {100 * cs['tpr01'][1]:+.2f}] | [{100 * cc['tpr01'][0]:+.2f}, {100 * cc['tpr01'][1]:+.2f}]"])
    L += ["", "### Pairwise differences inside a training-set group (points ×100; pAUC@1e-2 outcome by the cluster interval; TPR@1e-2 descriptive)", "",
          "| difference | subset | pAUC diff | stratified CI | cluster CI | seeds | outcome | TPR@1e-2 diff | TPR CI (stratified \\| cluster) |", "|---|---|---|---|---|---|---|---|---|"] + ["| " + " | ".join(r) + " |" for r in prow]
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "seen_unseen.md"), "w").write("\n".join(L) + "\n")
    json.dump(out, open(os.path.join(a.out, "seen_unseen.json"), "w"), indent=1)
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
