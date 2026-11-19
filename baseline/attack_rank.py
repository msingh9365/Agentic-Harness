"""
Attack 3a, step 1: rank the API names by how much a call of that name lowers a surrogate's score of malware (NOTES 15.3a).   (OURS)

    python -m baseline.attack_rank --store results/callstore/all.npz --tokens <dir with labels.npz> --v2pe-model <seed0_epoch2_model.pt> --out results/attack/ranking.json

Candidates: the EVAL pool = benign reports of the VALIDATION slice (not the training slice, not April) with at least one call. The unit is the API NAME; its representative call is the most
frequent call (identical token array) of that name in the EVAL pool. Score drop of a name = mean over 500 malware reports of the 90% slice (numpy seed 21) of
(surrogate score with the representative call added) - (surrogate score); ranked most negative first.
  (i)  LightGBM on the bag of API names (counts; 300 trees, 31 leaves, lr 0.05; fitted on the 90% slice; adding the call raises its name count by 1; raw margin as the score)
  (ii) v2-PE seed 0: the representative call is PREPENDED to the report, which is rebuilt from the store's pieces IN MEMORY and scored (logit).
Only the ranking (names, representative call = (store row, call index) pointers into the ORIGINAL reports, drops) is saved. No edited report is written.
"""
import argparse
import json
import os
import time
from collections import Counter

import numpy as np

from baseline import callstore as CS, common as C, gap

SAMPLE_SEED = 21
N_SAMPLE = 500


def eval_pool(store, y, val):
    return np.array([int(r) for r in val if y[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)


def representatives(store, pool):
    """name id -> (store row, call index) of the most frequent call of that name in the pool (identical token array = same call; ties: the first seen)."""
    cnt, first = {}, {}
    for r in pool:
        for i in range(store.n_calls(int(r))):
            nm = store.name(int(r), i)
            key = (nm, store.call(int(r), i).tobytes())
            cnt[key] = cnt.get(key, 0) + 1
            first.setdefault(key, (int(r), i))
    best = {}
    for (nm, key), c in cnt.items():
        if nm not in best or c > best[nm][0]:
            best[nm] = (c, first[(nm, key)])
    return {nm: v[1] for nm, v in best.items()}


def name_counts(store, rows, n_names):
    X = np.zeros((len(rows), n_names), dtype=np.float32)
    for k, r in enumerate(rows):
        for i in range(store.n_calls(int(r))):
            X[k, store.name(int(r), i)] += 1
    return X


def lgbm_drops(store, y, trn, sample, names, reps):
    import lightgbm as lgb
    n = len(store.names)
    X = name_counts(store, trn, n)
    m = lgb.LGBMClassifier(n_estimators=300, num_leaves=31, learning_rate=0.05, random_state=0, n_jobs=4, verbose=-1)
    m.fit(X, y[trn])
    Xs = name_counts(store, sample, n)
    base = m.predict(Xs, raw_score=True)
    drops = {}
    for nm in names:
        Xp = Xs.copy()
        Xp[:, nm] += 1
        drops[nm] = float((m.predict(Xp, raw_score=True) - base).mean())
    return drops


def v2pe_drops(store, sample, names, reps, model_path, bs=256):
    import torch
    from baseline import padtest
    torch.set_num_threads(4)
    model = padtest.load_model("v2_pe", model_path, "cpu")

    def score(rows, extra):
        toks = np.stack([CS.build_tokens(store, int(r), ([(store, *extra)] if extra else []) + list(range(store.n_calls(int(r)))))[0] for r in rows]).astype(np.int64)
        out = []
        with torch.no_grad():
            for i in range(0, len(toks), bs):
                out.append(model(torch.as_tensor(toks[i:i + bs])).reshape(-1).numpy())
        return np.concatenate(out)

    base = score(sample, None)
    drops, t0 = {}, time.time()
    for j, nm in enumerate(names):
        drops[nm] = float((score(sample, reps[nm]) - base).mean())
        if j % 100 == 0:
            print(f"  v2-PE ranking {j}/{len(names)} names, {time.time() - t0:.0f}s", flush=True)
    return drops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--v2pe-model", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--which", nargs="*", default=["lgbm", "v2pe"])
    a = ap.parse_args()
    store = CS.CallStore.load(a.store)
    lab = np.load(os.path.join(a.tokens, "labels.npz"))
    y = lab["y_train"]
    trn, val = gap.val_slice(lab["ym_train"])
    pool = eval_pool(store, y, val)
    reps = representatives(store, pool)
    names = sorted(reps)
    sample = np.sort(np.random.default_rng(SAMPLE_SEED).choice(trn[y[trn] == 1], N_SAMPLE, replace=False))
    print(f"EVAL pool {len(pool):,} benign reports; {len(names):,} API names with a representative call; sample {len(sample)} malware reports of the 90% slice", flush=True)
    out = {"eval_pool_n": int(len(pool)), "sample_seed": SAMPLE_SEED, "n_sample": N_SAMPLE, "names": {int(nm): store.names[nm] for nm in names}, "rep_call": {int(nm): [int(reps[nm][0]), int(reps[nm][1])] for nm in names}}
    if os.path.exists(a.out):
        out.update({k: v for k, v in json.load(open(a.out)).items() if k.startswith("drops_")})
    if "lgbm" in a.which:
        t0 = time.time()
        out["drops_lgbm"] = {int(k): v for k, v in lgbm_drops(store, y, trn, sample, names, reps).items()}
        print(f"LightGBM drops done in {time.time() - t0:.0f}s", flush=True)
    if "v2pe" in a.which:
        out["drops_v2pe"] = {int(k): v for k, v in v2pe_drops(store, sample, names, reps, a.v2pe_model).items()}
    for s in ("lgbm", "v2pe"):
        d = out.get(f"drops_{s}")
        if d:
            out[f"rank_{s}"] = [int(k) for k, _ in sorted(d.items(), key=lambda kv: (kv[1], kv[0]))]
            print(s, "top 10:", [out["names"][int(k)] for k in out[f"rank_{s}"][:10]], flush=True)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    C.dump_json(out, a.out)


if __name__ == "__main__":
    main()
