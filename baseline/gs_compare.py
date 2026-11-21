"""
Old and new tokenisation (NOTES 21, Stage A step 4).   (OURS)

    python -m baseline.gs_compare --old-dir <old bpe50k folder: vocab.json, x_train.npy, x_test.npy> --new-dir <variants/bpe50k_gs> --new-store <all_gs.npz> --old-store <all.npz> --out results/groupsplit

Reports (as piece strings, not ids): how many pieces of the 50,001 differ between the two vocabularies, how many reports have identical first 512 tokens in both tokenisations, how many token positions agree,
the change of the total token count, and the check that no first-512 token sequence of the NEW tokenisation occurs on both sides of the group split.
"""
import argparse
import hashlib
import json
import os

import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old-dir", required=True)
    ap.add_argument("--new-dir", required=True)
    ap.add_argument("--old-store", required=True)
    ap.add_argument("--new-store", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from baseline import callstore as CS
    from baseline import groupsplit as G
    vo, vn = json.load(open(os.path.join(a.old_dir, "vocab.json"))), json.load(open(os.path.join(a.new_dir, "vocab.json")))
    po, pn = set(vo), set(vn)
    R = {"vocab_old": len(vo), "vocab_new": len(vn), "pieces_in_both": len(po & pn), "pieces_only_old": len(po - pn), "pieces_only_new": len(pn - po),
         "pieces_same_id_in_both": int(sum(1 for p in po & pn if vo[p] == vn[p]))}
    io, inn = {i: p for p, i in vo.items()}, {i: p for p, i in vn.items()}
    xo = np.concatenate([np.load(os.path.join(a.old_dir, "x_train.npy")), np.load(os.path.join(a.old_dir, "x_test.npy"))])
    xn = np.concatenate([np.load(os.path.join(a.new_dir, "x_train.npy")), np.load(os.path.join(a.new_dir, "x_test.npy"))])
    assert xo.shape == xn.shape, (xo.shape, xn.shape)
    lo = np.array([max(io.keys()) + 1]); ln = np.array([max(inn.keys()) + 1])
    # map ids to a common piece index
    allp = {p: k for k, p in enumerate(sorted(po | pn))}
    mo = np.zeros(int(lo[0]) + 1, dtype=np.int64)
    for i, p in io.items():
        mo[i] = allp[p]
    mn = np.zeros(int(ln[0]) + 1, dtype=np.int64)
    for i, p in inn.items():
        mn[i] = allp[p]
    A, B = mo[xo.astype(np.int64)], mn[xn.astype(np.int64)]
    padmask = (xo == 0) & (xn == 0)
    same = (A == B)
    R["reports"] = int(len(xo))
    R["reports_identical_first512"] = float(np.mean(same.all(1)))
    R["token_positions_same_piece"] = float(same[~padmask].mean())
    R["reports_differing_in_more_than_10_percent_of_positions"] = float(np.mean(((~same) & ~padmask).sum(1) > 0.1 * np.maximum((~padmask).sum(1), 1)))
    so, sn = CS.CallStore.load(a.old_store), CS.CallStore.load(a.new_store)
    to = np.array([len(so.report_tokens(r)) for r in range(len(so))])
    tn = np.array([len(sn.report_tokens(r)) for r in range(len(sn))])
    R["total_tokens_median_old"], R["total_tokens_median_new"] = float(np.median(to)), float(np.median(tn))
    R["total_tokens_mean_change_percent"] = float(100 * (tn.sum() / to.sum() - 1))
    R["reports_with_same_total_tokens"] = float(np.mean(to == tn))
    # first-512 identity with the NEW tokenisation across the group split
    trn, val = G.val_slice()
    h = G.first512_hash(sn, np.arange(len(trn) + len(val)))
    R["new_first512_sequences_shared_train_val"] = int(len(set(h[trn]) & set(h[val])))
    R["new_val_reports_with_first512_in_train"] = float(np.mean([x in set(h[trn]) for x in h[val]]))
    json.dump(R, open(os.path.join(a.out, "tokenizer_compare.json"), "w"), indent=1)
    print(json.dumps(R, indent=1))


if __name__ == "__main__":
    main()
