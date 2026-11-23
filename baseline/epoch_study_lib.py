"""
NOTES 28 (epoch study): helpers shared by baseline/v2pe.py and baseline/twolevel.py (January data only; no April file is read).   (OURS)

  load_fold(n)        the split of fold n (hash asserted), its evaluation pool (benign reports of the POOL fold, >= 1 call) and its LightGBM ranking, from <ES_FOLDS or /kaggle/input>/**/fold<n>/
  attack_sets(...)    in memory: the validation reports with 50 calls prepended: random pool calls (malware and benign) and the LightGBM-ranked calls (malware)
  attack_metrics(...) detection / padded-benign FPR of those sets at the 1% threshold of the unedited validation benign scores of the same model and epoch
"""
import json
import os

import numpy as np

from baseline import callstore as CS, groupsplit as G

STREAM = 8400                                                             # per report: default_rng([8400, row]); per call a uniform pool report, then a uniform call of it


def find_fold_dir(n):
    roots = [os.environ["ES_FOLDS"]] if os.environ.get("ES_FOLDS") else []
    roots.append(os.environ.get("NEBULA_INPUT", "/kaggle/input"))
    for root in roots:
        for dp, dn, fn in os.walk(root):
            if os.path.basename(dp) == f"fold{n}" and "split.npz" in fn and "ranking.json" in fn:
                return dp
    raise FileNotFoundError(f"fold{n}/ (split.npz, ranking.json) not found under {roots}")


def load_fold(n):
    d = find_fold_dir(n)
    trn, val = G.val_slice(os.path.join(d, "split.npz"), os.path.join(d, "split_hash.json"))               # asserts the stored hash of THIS fold
    info = json.load(open(os.path.join(d, "fold.json")))
    assert (len(trn), len(val)) == (info["n_train"], info["n_val"]) and info["fold"] == n, (len(trn), len(val), info)
    ev_pool = np.load(os.path.join(d, "eval_pool.npy"))
    assert not (set(ev_pool.tolist()) & set(val.tolist())) and set(ev_pool.tolist()) <= set(trn.tolist()), "evaluation pool must lie in the training part, not in the validation part"
    assert len(ev_pool) == info["eval_pool_n"]
    ranking = json.load(open(os.path.join(d, "ranking.json")))
    assert ranking["fold"] == n and ranking["n_train"] == len(trn) and ranking["eval_pool_n"] == len(ev_pool)
    return {"trn": trn, "val": val, "eval_pool": ev_pool, "ranking": ranking, "info": info, "dir": d}


def load_train_tokens(tokens, variant):
    """x_train rows (January) and the vocabulary; the April token array is NOT opened."""
    d = os.path.join(tokens, "variants", variant)
    return np.load(os.path.join(d, "x_train.npy")), json.load(open(os.path.join(d, "vocab.json")))


def train_pool_without_eval(pool_rows, ev_pool, info=None, strict=True):
    """The training padding pool: benign reports of the training part (>= 1 call) minus the evaluation pool."""
    ev = set(int(r) for r in ev_pool)
    out = np.array([int(r) for r in pool_rows if int(r) not in ev], dtype=np.int64)
    if strict:
        assert len(out) + len(ev) == len(pool_rows), "the evaluation pool must be inside the training pool"
    if info is not None and strict:
        assert len(out) == info["train_pool_after_holdout"], (len(out), info["train_pool_after_holdout"])
    return out


def attack_sets(store, y, val, ev_pool, ranking, k=50, cut=512):
    """{name: (tokens uint16 [m, cut], total token counts int64 [m])}: rand_mal / rand_ben = the validation malware / benign reports with k random evaluation-pool calls prepended; lgbm_mal = the validation
    malware reports with the k top-ranked representative calls prepended (ranking order). Built from the call store in memory; nothing is written."""
    pool_n = np.array([store.n_calls(int(r)) for r in ev_pool], dtype=np.int64)
    rep_call = {int(i): v for i, v in ranking["rep_call"].items()}
    arr = [store.call(rep_call[int(nm)][0], rep_call[int(nm)][1]) for nm in ranking["rank_lgbm"][:k]]

    def build(rows, random):
        tok = np.zeros((len(rows), cut), dtype=np.uint16)
        tot = np.zeros(len(rows), dtype=np.int64)
        for i, r in enumerate(rows):
            r = int(r)
            if random:
                rng = np.random.default_rng([STREAM, r])
                added = []
                for _ in range(k):
                    pr = int(rng.integers(len(ev_pool)))
                    added.append(store.call(int(ev_pool[pr]), int(rng.integers(pool_n[pr]))))
            else:
                added = arr
            tok[i], tot[i] = CS.build_fast(store, r, added, None, cut=cut)
        return tok, tot
    mal = [int(r) for r in val if y[int(r)] == 1]
    ben = [int(r) for r in val if y[int(r)] == 0]
    return {"rand_mal": build(mal, True), "rand_ben": build(ben, True), "lgbm_mal": build(mal, False)}


def attack_metrics(score, thr, sets):
    """score(tokens, totals) -> logits. Flagged = logit strictly above thr (the 1% threshold of the unedited validation benign scores of the same model and epoch)."""
    zr, zb, zl = score(*sets["rand_mal"]), score(*sets["rand_ben"]), score(*sets["lgbm_mal"])
    return {"study_rand50_tpr": float((zr > thr).mean()), "study_rand50_benign_fpr": float((zb > thr).mean()), "study_lgbm50_tpr": float((zl > thr).mean()), "study_thr": float(thr),
            "study_n_mal": int(len(zr)), "study_n_ben": int(len(zb)), "study_mean_total_tokens_rand_mal": float(sets["rand_mal"][1].mean())}
