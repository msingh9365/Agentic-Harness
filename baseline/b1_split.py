"""
ITEM B1 (NOTES 30.4 / 30.4a): the ADAPT / TEST split of the April reports by hash_apis group (CPU; labels are NOT used; this is the first thing that is committed for B1).   (OURS)

    python -m baseline.b1_split --out results/groupsplit/b1

Groups = the April hash_apis values (2,509). Groups are put in the order of sha256("2027:" + hash_apis) and assigned one by one to the part (ADAPT or TEST) that has fewer reports so far (ties -> ADAPT), which gives
two parts of nearly equal size made of whole groups. TEST-unseen = the TEST reports whose hash_apis does not occur in the January training set. Writes split.npz (adapt, test, test_unseen as indices into the 17,402 April
rows / a boolean over `test`) and split.json (seed, counts, sha256 of split.npz). No label is read.
"""
import argparse
import hashlib
import json
import os

import numpy as np

from baseline import groupsplit as G

SEED = 2027


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jt = G.january_table()
    h_apr = np.asarray(jt["test"]["hash_apis"]).astype(str)
    h_jan = set(np.asarray(jt["train"]["hash_apis"]).astype(str).tolist())
    groups, inv = np.unique(h_apr, return_inverse=True)
    sizes = np.bincount(inv)
    order = sorted(range(len(groups)), key=lambda g: hashlib.sha256(f"{SEED}:{groups[g]}".encode()).hexdigest())
    part, n = np.zeros(len(groups), dtype=np.int8), [0, 0]
    for g in order:
        p = 0 if n[0] <= n[1] else 1
        part[g] = p
        n[p] += int(sizes[g])
    adapt = np.where(part[inv] == 0)[0]
    test = np.where(part[inv] == 1)[0]
    unseen = np.array([h not in h_jan for h in h_apr[test]])
    assert len(adapt) + len(test) == len(h_apr) and not (set(h_apr[adapt].tolist()) & set(h_apr[test].tolist()))
    os.makedirs(a.out, exist_ok=True)
    p = os.path.join(a.out, "split.npz")
    np.savez(p, adapt=adapt, test=test, test_unseen=unseen)
    info = {"seed": SEED, "rule": "groups ordered by sha256('2027:' + hash_apis), each assigned to the part with fewer reports so far (ties -> ADAPT)", "n_april": int(len(h_apr)), "n_groups": int(len(groups)),
            "adapt_reports": int(len(adapt)), "test_reports": int(len(test)), "adapt_groups": int((part == 0).sum()), "test_groups": int((part == 1).sum()), "test_unseen_reports": int(unseen.sum()),
            "groups_shared_between_adapt_and_test": 0, "sha256_split_npz": hashlib.sha256(open(p, "rb").read()).hexdigest(), "labels_used": False}
    json.dump(info, open(os.path.join(a.out, "split.json"), "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
