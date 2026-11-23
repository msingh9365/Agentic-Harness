"""
NOTES 28 (epoch study), preparation (CPU, January data only; no model, no April): the folds, their split files, the evaluation pools and the LightGBM rankings.   (OURS)

    python -m baseline.epoch_study_prep --store <all.npz of bpe50k_fix> --labels <labels.npz> --out results/groupsplit/epoch_study/folds [--md results/groupsplit/epoch_study/folds.md]

 * regenerates the 10 folds of StratifiedGroupKFold(10, shuffle, 2026) from the stored groups (`results/groupsplit/split.npz`, key `group`) and asserts that fold 9 equals the stored split (hash);
 * applies the rule of NOTES 21.3 / 28.1 (every family >= 300 validation reports, benign share within 5 points of January's, fold 9 first, then the qualifying folds with the smallest index, at most 3 more);
 * for every chosen fold f writes <out>/fold<f>/{split.npz, split_hash.json, fold.json, eval_pool.npy, ranking.json}: eval_pool = the benign reports (>= 1 call) of the validation part of the POOL fold of f
   (the other study fold, cyclic in the order of the chosen folds); ranking.json = the LightGBM ranking of API names (trained only on the fold's training part, candidates = representative calls of the evaluation pool,
   score drop on 500 malware training reports, numpy seed 21: baseline/attack_rank.py functions); the file holds only pointers (store row, call index), no report text.
"""
import argparse
import json
import os

import numpy as np

from baseline import attack_rank as AR, callstore as CS, common as C, groupsplit as G

ROOT = G.ROOT


def fold_table(fam, g, folds):
    sizes = np.bincount(g)
    out = []
    for k, (trn, val) in folds.items():
        out.append({"fold": k, "n": int(len(val)), "benign": int(np.isin(fam[val], ["clean", "windows_syswow64"]).sum()), "groups": int(len(set(g[val]))), "largest_group_share": round(float(sizes[g[val]].max() / len(val)), 3),
                    "families": {f: int((fam[val] == f).sum()) for f in sorted(set(fam))}})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--md", default=None)
    ap.add_argument("--max-extra", type=int, default=3)
    a = ap.parse_args()
    jt = G.january_table()
    fam = jt["train"]["family"]
    d = np.load(os.path.join(G.OUT, "split.npz"))
    g = d["group"]
    ref = json.load(open(os.path.join(G.OUT, "split_hash.json")))
    folds = {}
    from sklearn.model_selection import StratifiedGroupKFold
    for k, (trn, val) in enumerate(StratifiedGroupKFold(n_splits=G.FOLDS, shuffle=True, random_state=G.SEED).split(np.zeros(len(fam)), fam, g)):
        folds[k] = (np.sort(trn), np.sort(val))
    assert G.split_hash(*folds[9]) == ref["sha256"] and np.array_equal(folds[9][0], d["train"]) and np.array_equal(folds[9][1], d["val"]), "fold 9 does not reproduce the stored split"
    print("fold 9 reproduces the stored split", ref["sha256"], flush=True)
    table = fold_table(fam, g, folds)
    jan_benign = float(np.isin(fam, ["clean", "windows_syswow64"]).mean())
    _, cands, why = G.choose_fold(table, jan_benign)
    extra = [f for f in sorted(cands) if f != 9][:a.max_extra]
    chosen = [9] + extra
    print("candidates", cands, "chosen", chosen, flush=True)
    store = CS.CallStore.load(a.store)
    y = np.load(a.labels)["y_train"]
    assert len(store) >= len(y)
    os.makedirs(a.out, exist_ok=True)
    pool_of = {f: chosen[(i + 1) % len(chosen)] for i, f in enumerate(chosen)}
    md = [f"### Epoch study folds (NOTES 28.1): rule of NOTES 21.3 applied to the ten folds; candidates {cands}; chosen {chosen} ({1 + len(extra)} fold(s): fewer than 4 qualify, so the study has {len(chosen)})", "",
          "| fold | validation reports | benign % | groups | largest group % | " + " | ".join(sorted(set(fam))) + " | qualifies |", "|---|---|---|---|---|" + "---|" * len(set(fam)) + "---|"]
    for t in table:
        md.append(f"| {t['fold']} | {t['n']} | {100 * t['benign'] / t['n']:.1f} | {t['groups']} | {100 * t['largest_group_share']:.1f} | " + " | ".join(str(t["families"][f]) for f in sorted(set(fam))) + f" | {'yes' if t['fold'] in cands else 'no'}{' (chosen)' if t['fold'] in chosen else ''} |")
    md += ["", f"January benign share {100 * jan_benign:.1f}%; window {100 * (jan_benign - 0.05):.1f}% to {100 * (jan_benign + 0.05):.1f}%; per-fold reasons: " + json.dumps(why), ""]
    for f in chosen:
        trn, val = folds[f]
        pf = pool_of[f]
        pool = np.array([int(r) for r in folds[pf][1] if y[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)
        assert not (set(pool.tolist()) & set(val.tolist())) and set(pool.tolist()) <= set(trn.tolist()), "the evaluation pool must lie in the training part and not in the validation part"
        sd = os.path.join(a.out, f"fold{f}")
        os.makedirs(sd, exist_ok=True)
        np.savez(os.path.join(sd, "split.npz"), train=trn, val=val, group=g)
        h = G.split_hash(trn, val)
        json.dump({"sha256": h, "n_train": int(len(trn)), "n_val": int(len(val)), "seed": G.SEED, "folds": G.FOLDS, "fold": int(f)}, open(os.path.join(sd, "split_hash.json"), "w"), indent=1)
        np.save(os.path.join(sd, "eval_pool.npy"), pool)
        reps = AR.representatives(store, pool)
        names = sorted(reps)
        sample = np.sort(np.random.default_rng(AR.SAMPLE_SEED).choice(trn[y[trn] == 1], AR.N_SAMPLE, replace=False))
        drops = AR.lgbm_drops(store, y, trn, sample, names, reps)
        rank = [int(k) for k, _ in sorted(drops.items(), key=lambda kv: (kv[1], kv[0]))]
        rk = {"fold": int(f), "pool_fold": int(pf), "eval_pool_n": int(len(pool)), "sample_seed": AR.SAMPLE_SEED, "n_sample": AR.N_SAMPLE, "n_train": int(len(trn)), "names": {int(nm): store.names[nm] for nm in names},
              "rep_call": {int(nm): [int(reps[nm][0]), int(reps[nm][1])] for nm in names}, "drops_lgbm": {int(k): v for k, v in drops.items()}, "rank_lgbm": rank}
        C.dump_json(rk, os.path.join(sd, "ranking.json"))
        t = [x for x in table if x["fold"] == f][0]
        json.dump({"fold": int(f), "pool_fold": int(pf), "split_hash": h, "n_train": int(len(trn)), "n_val": int(len(val)), "n_val_benign": int((y[val] == 0).sum()), "n_val_malware": int((y[val] == 1).sum()), "eval_pool_n": int(len(pool)),
                   "families": t["families"], "largest_group_share": t["largest_group_share"], "groups": t["groups"], "train_pool_after_holdout": int(len([r for r in trn if y[r] == 0 and store.n_calls(int(r)) > 0 and int(r) not in set(pool.tolist())]))},
                  open(os.path.join(sd, "fold.json"), "w"), indent=1)
        print(f"fold {f}: train {len(trn)} val {len(val)} hash {h} pool fold {pf} eval pool {len(pool)}; top LightGBM names: {[rk['names'][k] for k in rank[:5]]}", flush=True)
        md.append(f"- fold {f}: split hash `{h}`, train {len(trn):,}, validation {len(val):,} (benign {int((y[val] == 0).sum())}, malware {int((y[val] == 1).sum())}), evaluation pool = benign reports of fold {pf} ({len(pool):,} with >= 1 call), the training padding pool = the benign training reports with >= 1 call minus these.")
    open(a.md or os.path.join(a.out, "..", "folds.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
