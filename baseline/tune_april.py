"""
April evaluation of the tuned candidate (NOTES 16.5 step 5) and the appendix of all candidates ("not used for selection").   (OURS)

    python -m baseline.tune_april --runs results/tune --out results/tune

GUARD: refuses to run unless NOTES.md already states the choice ("CHOSEN: lr=<lr> p=<p> epoch=<e>") and it is the choice in selection.json (made from validation numbers only by baseline/tune_select.py).
Evaluates the chosen candidate ONCE: clean metrics per seed and as 10-seed ensemble, bootstrap differences (stratified over reports as in EVAL_PROTOCOL.md; cluster bootstrap over duplicate groups as a
sensitivity) against v2-PE and against the existing ATT+bal, and the claim rule. The appendix lists the April clean numbers of the other candidates.
If the chosen candidate is the existing ATT+bal (2e-3, 0.5, epoch 2) and it reproduced, the stored logits of the existing models are the "tuned" family.
"""
import argparse
import json
import os
import re

import numpy as np

from baseline import att_report as AR, common as C, gap_final
from baseline.tune_select import CELLS, EPOCHS, ROOT, tag_of
from baseline.v2pe_report import md, ms

KEYS = [("pauc@0.01", "pAUC@1e-2", 3), ("tpr@0.01", "TPR@1e-2", 3), ("tpr@0.001", "TPR@1e-3", 3), ("auc", "AUC", 4)]


def logits_of(runs, lr, p, e):
    tag = tag_of(lr, p)
    return np.stack([np.load(os.path.join(runs, tag, f"seed{k}_epoch{e}_test_logits.npy")).astype(np.float64).reshape(-1) for k in range(10)])


def cluster_boot(y, Z, pairs, groups, n_boot):
    cells = {c: np.where(y == c)[0] for c in (0, 1)}
    members = {}
    for c, idx in cells.items():
        u, inv = np.unique(groups[idx], return_inverse=True)
        members[c] = [idx[inv == k] for k in range(len(u))]
    rng = np.random.default_rng(0)
    draws = {p: [] for p in pairs}
    for _ in range(n_boot):
        sel = np.concatenate([np.concatenate([members[c][i] for i in rng.integers(0, len(members[c]), len(members[c]))]) for c in (0, 1)])
        pa = {f: np.mean([C.pauc(y[sel], z[sel]) for z in Z[f]]) for f in Z}
        for p in pairs:
            draws[p].append(pa[p[0]] - pa[p[1]])
    out = {}
    for (a_, b_) in pairs:
        d = np.array(draws[(a_, b_)])
        per = np.array([C.pauc(y, za) - C.pauc(y, zb) for za, zb in zip(Z[a_], Z[b_])])
        lo, hi = np.percentile(d, [2.5, 97.5])
        out[f"{a_}-{b_}"] = {"lo": float(lo), "hi": float(hi), "seeds_above_0": int((per > 0).sum()), "resolved": bool((lo > 0 or hi < 0) and max((per > 0).sum(), (per < 0).sum()) >= 7)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=os.path.join(ROOT, "results", "tune"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "tune"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    sel = json.load(open(os.path.join(a.runs, "selection.json")))
    notes = open(os.path.join(ROOT, "NOTES.md")).read()
    m = re.search(r"CHOSEN: lr=([0-9.e-]+) p=([0-9.]+) epoch=(\d)", notes)
    if sel["chosen"] is None:
        raise SystemExit("selection.json: no candidate survived the rules; the existing ATT+bal stays; nothing to evaluate")
    lr, p, e = sel["chosen"]
    if not m or (float(m.group(1)), float(m.group(2)), int(m.group(3))) != (lr, p, e):
        raise SystemExit("GUARD: NOTES.md does not state the choice that selection.json makes ('CHOSEN: lr=.. p=.. epoch=..'); write it first (NOTES 16.6)")
    y = np.load(os.path.join(ROOT, "results", "logits", "labels.npz"))["y_test"].astype(int)
    v2 = AR.load_family("v2_pe", os.path.join(ROOT, "results", "att_bal"))[0]
    old = AR.load_family("attbal", os.path.join(ROOT, "results", "att_bal"))[0]
    use_existing = (lr, p, e) == (2e-3, 0.5, 2) and sel["reproduces_existing"]
    new = old if use_existing else logits_of(a.runs, lr, p, e)
    Z = {"v2_pe": v2, "attbal": old, "tuned": new}
    T = {f: AR.metrics_of(y, Z[f]) for f in Z}
    ens = {f: C.binary_metrics(y, Z[f].mean(0), decision=0.0) for f in Z}
    pairs = [("tuned", "v2_pe"), ("tuned", "attbal"), ("attbal", "v2_pe")]
    bs = gap_final.bootstrap(y, Z, a.boot, pairs=pairs)
    gp = os.path.join(ROOT, "results", "review", "april_hash_apis_group.npy")
    cl = cluster_boot(y, Z, pairs, np.load(gp), a.boot)
    name = {"v2_pe": "v2-PE", "attbal": "ATT+bal (existing, lr 2e-3, p 0.5, epoch 2)", "tuned": f"ATT+bal-tuned (lr {lr:g}, p {p:g}, epoch {e})" + (" = the existing ATT+bal" if use_existing else "")}
    L = [f"**Table A. Clean April data for the chosen candidate (chosen on validation numbers only; evaluated once).** Per-seed mean ± std and 10-seed ensemble.", ""]
    rows = [[name[f], 10] + [ms(T[f][k], d) for k, _, d in KEYS] + [f"{ens[f][k]:.{d}f}" for k, _, d in KEYS] for f in ("v2_pe", "attbal", "tuned")]
    L.append(md(rows, ["model", "n"] + [c[1] for c in KEYS] + [c[1] + " (ens.)" for c in KEYS]))
    L += ["", "**Claim rule (CI of the per-seed means excludes 0 and the same sign in ≥ 7 of 10 seeds); points × 100. Stratified bootstrap (EVAL_PROTOCOL.md) and, for pAUC@1e-2, the cluster bootstrap over duplicate groups.**", ""]
    rows = []
    for (n_, b_) in pairs:
        for k, lbl, _ in KEYS:
            ps, en = bs["ps"]["diffs"][f"{n_} - {b_}"][k], bs["ens"]["diffs"][f"{n_} - {b_}"][k]
            dd = T[n_][k] - T[b_][k]
            pos, neg = int((dd > 0).sum()), int((dd < 0).sum())
            rule = "RESOLVED " + ("better" if ps["point"] > 0 else "worse") if (ps["lo"] > 0 or ps["hi"] < 0) and max(pos, neg) >= 7 else "not resolved"
            c = cl.get(f"{n_}-{b_}") if k == "pauc@0.01" else None
            rows.append([f"{n_} − {b_}", lbl, f"{100 * ps['point']:+.2f} [{100 * ps['lo']:+.2f}, {100 * ps['hi']:+.2f}]", f"{pos}/{neg}", rule, f"{100 * en['point']:+.2f} [{100 * en['lo']:+.2f}, {100 * en['hi']:+.2f}]" + (" resolved" if en["resolved"] else " not resolved"),
                         (f"[{100 * c['lo']:+.2f}, {100 * c['hi']:+.2f}] " + ("resolved" if c["resolved"] else "not resolved")) if c else "—"])
    L.append(md(rows, ["difference", "metric", "per-seed means (CI)", "seeds >0 / <0", "claim rule", "10-seed ensembles (CI)", "cluster bootstrap CI (pAUC only)"]))
    # appendix
    L += ["", "## Appendix: April clean numbers of every candidate (NOT USED FOR SELECTION; the choice was made on validation numbers)", "",
          "Per-seed mean ± std over 10 seeds and the 10-seed ensemble pAUC@1e-2; the last two columns count the seeds in which the candidate is above v2-PE (same seed index).", ""]
    rows = []
    for lr_, p_ in CELLS:
        for e_ in EPOCHS:
            z = logits_of(a.runs, lr_, p_, e_)
            tm = AR.metrics_of(y, z)
            en = C.binary_metrics(y, z.mean(0), decision=0.0)["pauc@0.01"]
            rows.append([f"{lr_:g}", f"{p_:g}", e_] + [ms(tm[k], d) for k, _, d in KEYS] + [f"{en:.3f}", f"{int((tm['pauc@0.01'] > T['v2_pe']['pauc@0.01']).sum())}/10", f"{int((tm['tpr@0.01'] > T['v2_pe']['tpr@0.01']).sum())}/10",
                         "**chosen**" if (lr_, p_, e_) == (lr, p, e) else ("the existing ATT+bal" if (lr_, p_, e_) == (2e-3, 0.5, 2) else "")])
    L.append(md(rows, ["lr", "p", "epoch"] + [c[1] for c in KEYS] + ["pAUC@1e-2 (ens.)", "pAUC > v2-PE", "TPR@1e-2 > v2-PE", "note"]))
    text = "\n".join(L)
    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "april_chosen.md"), "w").write(text + "\n")
    json.dump({"chosen": [lr, p, e], "use_existing": use_existing, "test": {f: {k: v.round(6).tolist() for k, v in m_.items()} for f, m_ in T.items()}, "ensemble": {f: {k: v for k, v in m_.items() if k != "roc_on_grid"} for f, m_ in ens.items()},
               "bootstrap": bs, "cluster": cl}, open(os.path.join(a.out, "april_chosen.json"), "w"), indent=1)
    print(text)


if __name__ == "__main__":
    main()
