"""
ITEM C1' of NOTES 30.1 (CPU): a LightGBM bag-of-API-names detector (MalDy-style), trained on ALL January reports with FIXED settings (300 trees, 31 leaves, learning rate 0.05, random_state 0, no bagging, no
feature subsampling, no tuning anywhere), scored once on April (April opening 31) on the clean reports and on the Stage J padding sets.   (OURS)

    python -m baseline.c1_lgbm --store <all.npz of bpe50k_fix> --labels <labels.npz> --out results/groupsplit/c1_lgbm

Features: number of calls of every API name of the store (the store's name ids, 2,856 names), per report. Score = the raw margin (a logit). The model has no random component, so ONE model is trained
(NOTES 30.1: deviation from 10 seeds); a second fit with another random_state and one thread must give the same logits (checked, the difference is written). Where the evaluation tools expect 10 seeds the single
score vector is replicated 10 times (std 0).
Padding sets (the sampler of Stage J: make_pad.plan_test_row, draws from the 3,161 held-out benign validation-slice reports; for a bag of names only the NAMES of the drawn calls matter, so a set changes the counts):
random_20_prepend, random_50_prepend, random_100_prepend, random_200_insert, lgbm_50_prepend (the 50 top-ranked names of ranking_gs.json added once to EVERY report, as in Stage J). Reports without calls are left
unedited by the random sets (as Stage J). Output: logits_c1.npz (c1_test), scores_c1.npz (names, tot, seed0..seed9), c1_summary.json, c1_model.txt. Scores only; no edited report is saved.
"""
import argparse
import json
import os

import numpy as np

from baseline import callstore as CS, groupsplit as G
from baseline.make_pad import plan_test_row

NTR = 75298
SETS = [("unedited", "none", 0, None), ("random_20_prepend", "random", 20, "prepend"), ("random_50_prepend", "random", 50, "prepend"), ("random_100_prepend", "random", 100, "prepend"),
        ("random_200_insert", "random", 200, "insert"), ("lgbm_50_prepend", "lgbm", 50, "prepend")]


def counts(store, rows, n_names):
    X = np.zeros((len(rows), n_names), dtype=np.float32)
    for i, r in enumerate(rows):
        s0, n = int(store.rep_seg[r]), store.n_calls(int(r))
        if n:
            X[i] = np.bincount(store.seg_name[s0 + 1:s0 + 1 + n], minlength=n_names)
    return X


def main():
    import lightgbm as lgb
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--ranking", default=os.path.join(G.ROOT, "results", "groupsplit", "stage_fgh", "stage_h", "ranking_gs.json"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    store = CS.CallStore.load(a.store)
    n_names = len(store.names)
    lab = np.load(a.labels)
    y_tr = lab["y_train"].astype(int)
    assert len(y_tr) == NTR and len(store) == NTR + 17402
    Xtr = counts(store, np.arange(NTR), n_names)
    Xte = counts(store, np.arange(NTR, len(store)), n_names)
    print(f"features {n_names}; train {Xtr.shape}, April {Xte.shape}", flush=True)
    mk = lambda rs, nj: lgb.LGBMClassifier(n_estimators=300, num_leaves=31, learning_rate=0.05, random_state=rs, n_jobs=nj, verbose=-1)
    m = mk(0, 4).fit(Xtr, y_tr)
    z0 = m.predict(Xte, raw_score=True).astype(np.float32)
    m2 = mk(1, 1).fit(Xtr, y_tr)
    z1 = m2.predict(Xte, raw_score=True).astype(np.float32)
    det = float(np.abs(z0 - z1).max())
    print(f"determinism: second fit (random_state 1, one thread) max abs logit difference {det:.3e}", flush=True)
    m.booster_.save_model(os.path.join(a.out, "c1_model.txt"))
    np.savez_compressed(os.path.join(a.out, "logits_c1.npz"), c1_test=z0[None, :])
    # padding sets
    val = np.load(os.path.join(G.OUT, "split.npz"))["val"]
    pool = np.array([int(r) for r in val if y_tr[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
    assert len(pool) == 3161
    pool_n = np.array([store.n_calls(int(r)) for r in pool], dtype=np.int64)
    pool_names = [store.seg_name[int(store.rep_seg[int(r)]) + 1:int(store.rep_seg[int(r)]) + 1 + store.n_calls(int(r))] for r in pool]
    ranking = json.load(open(a.ranking))
    assert ranking["eval_pool_n"] == 3161
    top50 = [int(x) for x in ranking["rank_lgbm"][:50]]
    scores, tots = [], []
    for name, kind, k, mode in SETS:
        X = Xte.copy()
        if kind == "random":
            for t in range(len(Xte)):
                n = store.n_calls(NTR + t)
                if n == 0:
                    continue
                plan = plan_test_row(t, k, mode, n, pool_n)
                for pr, c in plan["draws"]:
                    X[t, pool_names[pr][c]] += 1
        elif kind == "lgbm":
            for nm in top50:
                X[:, nm] += 1
        scores.append(m.predict(X, raw_score=True).astype(np.float32))
        tots.append(np.zeros(len(Xte), dtype=np.int32))
        print(f"set {name}: mean logit {scores[-1].mean():.3f}", flush=True)
    S = np.stack(scores)
    assert np.array_equal(S[0], z0), "unedited scores must equal the clean logits"
    np.savez_compressed(os.path.join(a.out, "scores_c1.npz"), names=np.array([s[0] for s in SETS]), tot=np.stack(tots), **{f"seed{s}": S for s in range(10)})
    imp = m.booster_.feature_importance("gain")
    top = np.argsort(-imp)[:15]
    json.dump({"n_features": n_names, "n_train": NTR, "settings": {"n_estimators": 300, "num_leaves": 31, "learning_rate": 0.05, "random_state": 0, "bagging": False, "feature_fraction": 1.0},
               "determinism_second_fit_max_abs_logit_diff": det, "top_features_by_gain": [[store.names[int(i)], float(imp[i])] for i in top], "sets": [s[0] for s in SETS],
               "note": "single deterministic model; scores replicated 10x only for the evaluation tools"}, open(os.path.join(a.out, "c1_summary.json"), "w"), indent=1)
    print("done", flush=True)


if __name__ == "__main__":
    main()
