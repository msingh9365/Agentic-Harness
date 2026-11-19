#!/usr/bin/env python
"""
Round 5, item 3c: rank the calls of the EVAL pool by how much they lower the score of a surrogate model, for padding that is "chosen to look benign"
(transfer attack: the surrogate is not one of the attacked models).

    python scripts/round5/surrogate_rank.py --which lgb|c

lgb  surrogate = LightGBM on the bag of API names (counts per API name), trained here on the train side of January (validation side for early
     stopping); same family as the bag-of-API LightGBM of results/go_no_go (retrained because that model is not stored, only its scores).
     Candidate = every distinct API name of the EVAL-pool calls (first call of that name as the representative). Drop(name) = mean over
     1,000 malware reports of the January train side of [logit(report) - logit(report + one call of that name)]; ties are broken by the drop with 5 calls.
c    surrogate = C (J) seed 0 (512 tokens). Candidates = 1,000 random distinct EVAL-pool calls (api name + arguments); Drop(call) = mean over 100 malware
     reports of the January validation side of [logit(report) - logit(call prepended to the report)].
Both lists use only the EVAL pool for candidates and January malware (not April) for the effect. Writes results/round5/surrogate_<which>.json:
ranked_calls = [[report row, call index], ...] (references into the EVAL pool, best first), names, drops. No edited reports are saved.
"""
import argparse
import json
import os
import sys
import time

import lightgbm  # noqa: F401  (imported before torch: the two OpenMP runtimes clash otherwise)
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import r5_common as R  # noqa: E402
from r5_common import C, V, _W, _init  # noqa: E402
from r5_compose import Composer  # noqa: E402


def eval_calls():
    p = json.load(open("results/pooling_v4/pools.json"))
    out = []
    for r in p["eval_rows"]:
        for i, c in enumerate(_W["reps"].get(int(r)).get("apis") or []):
            out.append((int(r), i, c))
    return out


def lgb_surrogate(a):
    import lightgbm as lgb
    import scipy.sparse as sp
    meta = C.meta_full()
    jan = meta[meta.split == "trainset"]
    tr, va = jan[jan.side == "train"], jan[jan.side == "val"]
    t0 = time.time()
    names = {}
    def bag(rows):
        ind, dat, ptr = [], [], [0]
        for r in rows:
            cnt = {}
            for c in _W["reps"].get(int(r)).get("apis") or []:
                j = names.setdefault(c["api_name"], len(names))
                cnt[j] = cnt.get(j, 0) + 1
            ind += list(cnt); dat += list(cnt.values()); ptr.append(len(ind))
        return ind, dat, ptr
    btr, bva = bag(tr.row.values), bag(va.row.values)
    V_ = len(names)
    # add the EVAL-call names so that every candidate has a column (their counts in the training data are 0 if unseen)
    ev = eval_calls()
    for _, _, c in ev:
        names.setdefault(c["api_name"], len(names))
    V_ = len(names)
    mk = lambda b, n: sp.csr_matrix((b[1], b[0], b[2]), shape=(n, V_), dtype=np.float32)
    Xtr, Xva = mk(btr, len(tr)), mk(bva, len(va))
    print(f"bag of API names: {V_} names, {len(tr):,} train / {len(va):,} val reports, built in {time.time() - t0:.0f}s", flush=True)
    dtr = lgb.Dataset(Xtr, tr.label.values); dva = lgb.Dataset(Xva, va.label.values, reference=dtr)
    params = dict(objective="binary", learning_rate=0.05, num_leaves=63, feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1,
                  min_data_in_leaf=20, verbose=-1, seed=0, num_threads=1)
    m = lgb.train(params, dtr, 1500, valid_sets=[dva], callbacks=[lgb.early_stopping(100, verbose=False)])
    from sklearn.metrics import roc_auc_score
    test, y = V.april()
    bte = bag(test.row.values)
    zte = m.predict(mk(bte, len(test)), raw_score=True)
    print(f"surrogate LightGBM: best iteration {m.best_iteration}, January val AUC {roc_auc_score(va.label.values, m.predict(Xva, raw_score=True)):.4f}, "
          f"April AUC {roc_auc_score(y, zte):.4f}", flush=True)
    rng = np.random.default_rng(5)
    mal = tr[tr.label == 1].row.values
    pick = rng.choice(len(mal), 1000, replace=False)
    Xm = mk(bag(mal[pick]), 1000).tocsc()
    base = m.predict(Xm.tocsr(), raw_score=True)
    rep, seen = {}, {}
    for r, i, c in ev:
        if c["api_name"] not in rep:
            rep[c["api_name"]] = (r, i)
    cand = sorted(rep)
    drops1, drops5 = [], []
    Xr = Xm.tocsr()
    for n in cand:
        j = names[n]
        add = sp.csr_matrix(([1.0], ([0], [j])), shape=(1, V_), dtype=np.float32)
        ones = sp.csr_matrix(np.ones((1000, 1), dtype=np.float32)) @ add
        drops1.append(float((base - m.predict(Xr + ones, raw_score=True)).mean()))
        drops5.append(float((base - m.predict(Xr + 5 * ones, raw_score=True)).mean()))
    return cand, np.array(drops1), np.array(drops5), rep, {"surrogate_april_auc": float(roc_auc_score(y, zte)), "best_iteration": int(m.best_iteration)}


def c_surrogate(a):
    meta = C.meta_full()
    jan = meta[(meta.split == "trainset") & (meta.side == "val") & (meta.label == 1)]
    rng = np.random.default_rng(6)
    reports = rng.choice(jan.row.values, 100, replace=False)
    ev = eval_calls()
    keyed = {}
    for r, i, c in ev:
        keyed.setdefault((c["api_name"], tuple(map(str, c.get("args") or []))), (r, i, c))
    keys = sorted(keyed)
    pick = rng.choice(len(keys), min(1000, len(keys)), replace=False)
    cands = [keyed[keys[i]] for i in sorted(pick)]
    m, w, z0 = R.load_model("C", 0)
    comp = Composer(_W["nb"])
    parts = [comp.parts(_W["reps"].get(int(r))) for r in reports]
    base = R.score_tokens(m, 512, [comp.compose(p, []) for p in parts])
    drops = []
    t0 = time.time()
    for n, (r, i, c) in enumerate(cands):
        toks = [comp.compose(p, [c]) for p in parts]
        drops.append(float((base - R.score_tokens(m, 512, toks)).mean()))
        if n % 100 == 0:
            print(f"  candidate {n}/{len(cands)} ({time.time() - t0:.0f}s)", flush=True)
    names = [f"{c['api_name']}({', '.join(map(str, c.get('args') or []))})"[:100] for _, _, c in cands]
    rep = {n: (r, i) for n, (r, i, c) in zip(names, cands)}
    return names, np.array(drops), np.zeros(len(drops)), rep, {"candidates": len(cands), "reports": len(reports)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", choices=["lgb", "c"], required=True)
    a = ap.parse_args()
    R.n_threads()
    _init(R.NEBULA)
    cand, d1, d5, rep, info = lgb_surrogate(a) if a.which == "lgb" else c_surrogate(a)
    order = sorted(range(len(cand)), key=lambda i: (-d1[i], -d5[i], cand[i]))
    out = {"which": a.which, "info": info, "n_candidates": len(cand),
           "ranked_calls": [list(map(int, rep[cand[i]])) for i in order[:200]],
           "names": [cand[i] for i in order[:200]], "drops": [float(d1[i]) for i in order[:200]],
           "drops_5": [float(d5[i]) for i in order[:200]], "median_drop": float(np.median(d1)), "share_positive_drop": float((d1 > 0).mean())}
    json.dump(out, open(f"{R.OUT}/surrogate_{a.which}.json", "w"), indent=1)
    print("top 10:", list(zip(out["names"][:10], np.round(out["drops"][:10], 3))))
    print(f"{out['n_candidates']} candidates, median drop {out['median_drop']:.3f}, share with a positive drop {out['share_positive_drop']:.2f}")


if __name__ == "__main__":
    main()
