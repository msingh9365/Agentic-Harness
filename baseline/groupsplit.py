"""
Group-split validation slice (NOTES 21).   (OURS)

The old validation slice (`gap.val_slice`) is a random 10% of the January reports, so most of its reports have an exact twin (same API-name sequence) in the training part. Here the split is by GROUP:
group = reports with the same `hash_apis`, joined (union-find) with reports whose first 512 tokens are identical; the validation slice is the fold chosen by the rule of NOTES 21.3 (fold 0 was rejected) of
StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=2026) with the 9 family labels as classes. The indices are in our January row numbering (x_train rows 0..75,297 = rows of the call store).

    python -m baseline.groupsplit --build --store <all.npz> --out results/groupsplit       # split + checks (CPU, a few minutes)
    from baseline import groupsplit; trn, val = groupsplit.val_slice()                      # asserts the stored hash (every later run)
"""
import argparse
import hashlib
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "results", "groupsplit")
SEED, FOLDS = 2026, 10
MIN_SHARE, MAX_SHARE, MIN_FAMILY = 0.08, 0.12, 20


def january_table():
    """family and hash_apis of our 75,298 January rows and the 17,402 April rows (joined by row_map)."""
    import pandas as pd
    r = pd.read_csv(os.path.join(ROOT, "results", "misses", "reports.csv"), usecols=["split", "sample_id", "hash_apis", "n_calls"], low_memory=False)
    m = pd.read_csv(os.path.join(ROOT, "results", "hier", "data", "meta.csv"))
    rm = np.load(os.path.join(ROOT, "results", "padding", "row_map.npz"))
    out = {}
    for k in ("train", "test"):
        a, b = r.iloc[rm[k]].reset_index(drop=True), m.iloc[rm[k]].reset_index(drop=True)
        assert (a.sample_id.str.replace(".dat", "", regex=False).values == b.id.str.replace(".dat", "", regex=False).values).all() and (b.split.values == ("trainset" if k == "train" else "testset")).all()
        out[k] = {"hash_apis": a.hash_apis.values, "family": b.family.values, "n_calls": a.n_calls.values}
    return out


def first512_hash(store, rows, n=512):
    """sha1 of the first n tokens of every report of the store (our row numbering)."""
    return np.array([hashlib.sha1(np.ascontiguousarray(store.report_tokens(int(r))[:n]).tobytes()).hexdigest() for r in rows])


def groups_of(*keys):
    """union-find over rows: two rows are in one group if they agree in ANY of the key arrays. Returns a dense group id per row."""
    n = len(keys[0])
    parent = np.arange(n)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for k in keys:
        first = {}
        for i, v in enumerate(k):
            j = first.setdefault(v, i)
            if j != i:
                a, b = find(i), find(j)
                if a != b:
                    parent[max(a, b)] = min(a, b)
    root = np.array([find(i) for i in range(n)])
    return np.unique(root, return_inverse=True)[1]


def split_hash(trn, val):
    h = hashlib.sha256()
    h.update(np.asarray(trn).astype(np.int64).tobytes())
    h.update(np.asarray(val).astype(np.int64).tobytes())
    return h.hexdigest()[:32]


def make_split(family, groups, fold=0):
    """(train, validation) of fold `fold` of StratifiedGroupKFold(10, shuffle, 2026). Fold 0 was the first choice (NOTES 21), rejected in NOTES 21.3; the fold used now is chosen by `choose_fold`."""
    from sklearn.model_selection import StratifiedGroupKFold
    sgk = StratifiedGroupKFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    for k, (trn, val) in enumerate(sgk.split(np.zeros(len(family)), family, groups)):
        if k == fold:
            return np.sort(trn), np.sort(val)
    raise ValueError(fold)


MALWARE_AND_CLEAN = ["backdoor", "clean", "coinminer", "dropper", "keylogger", "ransomware", "rat", "trojan"]


def choose_fold(folds, january_benign_share, min_family=300, benign_window=0.05):
    """The rule of NOTES 21.3 (data statistics only). folds = list of dicts as written by `build` (n, benign, groups, largest_group_share, families).
    Candidates: every family of MALWARE_AND_CLEAN has >= min_family validation reports and |benign share - January's| <= benign_window (windows_syswow64 is exempt).
    Choice: smallest largest-group share; ties -> more groups; then the lower fold number. Returns (fold or None, list of candidate folds, per-fold reasons)."""
    cands, why = [], {}
    for f in folds:
        fam_ok = all(f["families"][x] >= min_family for x in MALWARE_AND_CLEAN)
        bshare = f["benign"] / f["n"]
        ben_ok = abs(bshare - january_benign_share) <= benign_window
        why[f["fold"]] = {"families_ge_300": bool(fam_ok), "benign_share": round(bshare, 4), "benign_within_5pt": bool(ben_ok)}
        if fam_ok and ben_ok:
            cands.append(f)
    if not cands:
        return None, [], why
    best = min(cands, key=lambda f: (f["largest_group_share"], -f["groups"], f["fold"]))
    return best["fold"], [f["fold"] for f in cands], why


def val_slice(path=os.path.join(OUT, "split.npz"), hashes=os.path.join(OUT, "split_hash.json")):
    """(train, validation) January row indices of the group split, asserted against the stored hash."""
    d = np.load(path)
    trn, val = d["train"], d["val"]
    ref = json.load(open(hashes))
    assert (split_hash(trn, val), len(trn), len(val)) == (ref["sha256"], ref["n_train"], ref["n_val"]), "group-split validation slice differs from the stored one"
    return trn, val


# ----------------------------------------------------------------------------- checks
def name_sequences(store, rows):
    """API-name id sequence of every report (the calls the model reads)."""
    return [store.seg_name[int(store.rep_seg[r]) + 1:int(store.rep_seg[r + 1]) - 1] for r in rows]


def near_duplicate_share(seq_a, seq_b, hash_a, hash_b, thresholds=(0.0, 0.01, 0.05, 0.10)):
    """Share of the reports of A that have a report in B within normalised Levenshtein distance <= t on the API-name sequence (distance / max length).
    Distinct sequences only (identified by hash_apis), exact distances (rapidfuzz, score_cutoff), length filter |la - lb| <= t max(la, lb); weighted by report counts."""
    from rapidfuzz.distance import Levenshtein
    ua, ia = np.unique(hash_a, return_index=True)
    ub, ib = np.unique(hash_b, return_index=True)
    sa = [list(seq_a[i]) for i in ia]
    sb = [list(seq_b[i]) for i in ib]
    la, lb = np.array([len(s) for s in sa]), np.array([len(s) for s in sb])
    cnt = np.array([(hash_a == u).sum() for u in ua])
    best = np.full(len(ua), np.inf)
    order = np.argsort(lb)
    lbs = lb[order]
    tmax = max(thresholds)
    for i in range(len(ua)):
        L = la[i]
        # candidates with |L - l| <= tmax * max(L, l)  ->  l in [L (1 - tmax), L / (1 - tmax)]
        lo, hi = np.searchsorted(lbs, int(np.floor(L * (1 - tmax)))), np.searchsorted(lbs, int(np.ceil(L / (1 - tmax))), side="right")
        for j in order[lo:hi]:
            m = max(L, lb[j])
            cutoff = int(np.floor(tmax * m))
            d = Levenshtein.distance(sa[i], sb[j], score_cutoff=cutoff)
            if d <= cutoff:
                best[i] = min(best[i], d / m if m else 0.0)
                if best[i] == 0.0:
                    break
    return {f"{t:g}": float(cnt[best <= t].sum() / cnt.sum()) for t in thresholds}, int(len(ua)), int(len(ub))


def build(store_path, out):
    from sklearn.model_selection import StratifiedGroupKFold
    from baseline import callstore as CS
    from baseline import gap
    store = CS.CallStore.load(store_path)
    jt = january_table()
    n_tr, n_te = len(jt["train"]["family"]), len(jt["test"]["family"])
    assert len(store) == n_tr + n_te, (len(store), n_tr, n_te)
    rows_tr, rows_te = np.arange(n_tr), np.arange(n_tr, n_tr + n_te)
    h512 = first512_hash(store, rows_tr)
    hapi = jt["train"]["hash_apis"]
    fam = jt["train"]["family"]
    hseq = np.array([hashlib.sha1(np.ascontiguousarray(q).tobytes()).hexdigest() for q in name_sequences(store, rows_tr)])      # amendment 2026-11-21 (NOTES 21.1): identical filtered call-name sequence is a third relation
    g_h = groups_of(hapi)
    g = groups_of(hapi, h512, hseq)
    sizes = np.bincount(g)
    folds = []
    for k, (a_, b_) in enumerate(StratifiedGroupKFold(n_splits=FOLDS, shuffle=True, random_state=SEED).split(np.zeros(len(fam)), fam, g)):
        folds.append({"fold": k, "n": int(len(b_)), "share": round(len(b_) / len(fam), 4), "benign": int(np.isin(fam[b_], ["clean", "windows_syswow64"]).sum()), "groups": int(len(set(g[b_]))), "largest_group_share": round(float(sizes[g[b_]].max() / len(b_)), 3),
                      "families": {f: int((fam[b_] == f).sum()) for f in sorted(set(fam))}})
    jan_benign = float(np.isin(fam, ["clean", "windows_syswow64"]).mean())
    fold, cands, why = choose_fold(folds, jan_benign)                      # the rule of NOTES 21.3, data statistics only
    assert fold is not None, "no fold meets the rule of NOTES 21.3: stop and show the table of all ten folds"
    trn, val = make_split(fam, g, fold)
    res = {"fold_rule": {"january_benign_share": jan_benign, "candidates": cands, "chosen_fold": int(fold), "per_fold": why}, "folds_all_ten": folds, "n_groups_hash_apis": int(g_h.max() + 1), "n_groups_strict": int(g.max() + 1), "n_train": int(len(trn)), "n_val": int(len(val)), "share_val": float(len(val) / n_tr)}
    # sanity: equal hash_apis implies equal call-name sequence in the store?
    # acceptance (fixed in NOTES 21)
    fam_names = sorted(set(fam))
    val_counts = {f: int((fam[val] == f).sum()) for f in fam_names}
    res["acceptance"] = {"share_in_8_12_percent": bool(MIN_SHARE <= len(val) / n_tr <= MAX_SHARE),
                         "families_ge_20": {f: bool(val_counts[f] >= MIN_FAMILY or f == "windows_syswow64") for f in fam_names}, "windows_syswow64_present": bool(val_counts["windows_syswow64"] > 0)}
    ok = res["acceptance"]["share_in_8_12_percent"] and all(res["acceptance"]["families_ge_20"].values()) and res["acceptance"]["windows_syswow64_present"]
    res["accepted"] = bool(ok)
    os.makedirs(out, exist_ok=True)
    np.savez(os.path.join(out, "split.npz"), train=trn, val=val, group=g)
    json.dump({"sha256": split_hash(trn, val), "n_train": int(len(trn)), "n_val": int(len(val)), "seed": SEED, "folds": FOLDS, "fold": int(fold), "keys": ["hash_apis", "first512_tokens_old_bpe50k", "filtered_call_name_sequence"]}, open(os.path.join(out, "split_hash.json"), "w"), indent=1)
    json.dump(res, open(os.path.join(out, "split_summary.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return store, jt, rows_tr, rows_te, h512, g, trn, val, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--store", required=True)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--labels", default=None, help="labels.npz of the old tokens (ym_train, for the old slice); with it the checks of NOTES 21 are run")
    a = ap.parse_args()
    parts = build(a.store, a.out)
    if a.labels:
        R = checks(*parts[:8], a.labels, a.out, log=lambda s: print(s, flush=True))
        print(json.dumps({k: v for k, v in R.items() if k not in ("largest_groups", "family_counts")}, indent=1))



# ----------------------------------------------------------------------------- the checks of NOTES 21 (README numbers)
def checks(store, jt, rows_tr, rows_te, h512, g, trn, val, labels_path, out, log=print):
    from baseline import gap
    ym = np.load(labels_path)["ym_train"]
    hapi, fam = jt["train"]["hash_apis"], jt["train"]["family"]
    hte, fte = jt["test"]["hash_apis"], jt["test"]["family"]
    R = {}
    # (a) groups shared
    R["groups_shared_train_val"] = int(len(set(g[trn]) & set(g[val])))
    # (b) exact twins
    tr_set = set(hapi[trn])
    otrn, oval = gap.val_slice(ym)
    otr_set = set(hapi[otrn])
    R["val_share_hash_in_train"] = float(np.mean([h in tr_set for h in hapi[val]]))
    R["old_val_share_hash_in_old_train"] = float(np.mean([h in otr_set for h in hapi[oval]]))
    R["april_share_hash_in_new_train"] = float(np.mean([h in tr_set for h in hte]))
    R["april_share_hash_in_old_train"] = float(np.mean([h in otr_set for h in hte]))
    R["first512_shared_train_val"] = int(len(set(h512[trn]) & set(h512[val])))
    R["old_val_first512_in_old_train"] = float(np.mean([h in set(h512[otrn]) for h in h512[oval]]))
    # (c) near-duplicates, API-name sequences
    seq = name_sequences(store, rows_tr)
    seq_te = name_sequences(store, rows_te)
    log("near-duplicates: new validation vs new training ...")
    R["near_dup_val_vs_train"], R["n_distinct_val"], R["n_distinct_train"] = near_duplicate_share([seq[i] for i in val], [seq[i] for i in trn], hapi[val], hapi[trn])
    log("near-duplicates: April vs new training ...")
    R["near_dup_april_vs_new_train"], R["n_distinct_april"], _ = near_duplicate_share(seq_te, [seq[i] for i in trn], hte, hapi[trn])
    log("near-duplicates: old validation vs old training ...")
    R["near_dup_oldval_vs_oldtrain"], R["n_distinct_oldval"], R["n_distinct_oldtrain"] = near_duplicate_share([seq[i] for i in oval], [seq[i] for i in otrn], hapi[oval], hapi[otrn])
    # (d) counts
    fam_names = sorted(set(fam))
    R["family_counts"] = {f: {"train": int((fam[trn] == f).sum()), "val": int((fam[val] == f).sum()), "old_train": int((fam[otrn] == f).sum()), "old_val": int((fam[oval] == f).sum()), "april": int((fte == f).sum())} for f in fam_names}
    sizes = np.bincount(g)
    top = np.argsort(-sizes)[:10]
    R["largest_groups"] = [{"size": int(sizes[k]), "side": "val" if k in set(g[val]) else "train", "family_mix": {f: int(c) for f, c in zip(*np.unique(fam[g == k], return_counts=True))}} for k in top]
    R["groups_train"], R["groups_val"] = int(len(set(g[trn]))), int(len(set(g[val])))
    R["largest_group_share_of_train"] = float(sizes[g[trn]].max() / len(trn))
    # sanity of the identity hash_apis -> call-name sequence in the store
    first = {}
    bad = 0
    for i, h in enumerate(hapi):
        s = seq[i]
        if h in first:
            bad += int(not np.array_equal(first[h], s))
        else:
            first[h] = s
    R["rows_whose_name_sequence_differs_from_first_of_same_hash_apis"] = int(bad)
    os.makedirs(out, exist_ok=True)
    json.dump(R, open(os.path.join(out, "checks.json"), "w"), indent=1)
    return R


if __name__ == "__main__":
    main()
