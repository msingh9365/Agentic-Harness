"""Call identities for the deduplication defence without report text (audit item 4): one integer per call = hash of the call text (repr of the call dict) for the April reports and the EVAL-pool reports, saved as ids/offsets/rows
(original reports only; consistent within this file because all hashes come from this process).   python -m baseline.extra_ident --out results/review/extra_ident.npz"""
import argparse

import numpy as np

from baseline import extra_check, extra_edits as X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    store, tr, te, reps, P, ntr = extra_check.setup(False)
    rep_of = lambda row: reps.get(int(te[int(row) - ntr])) if int(row) >= ntr else reps.get(int(tr[int(row)]))
    ident = X.Ident(rep_of)
    rows = sorted(set(P.pool.tolist()) | set(range(ntr, ntr + len(te))))
    ids = [ident.ensure(r) for r in rows]
    off = np.concatenate([[0], np.cumsum([len(x) for x in ids])]).astype(np.int64)
    np.savez_compressed(a.out, rows=np.array(rows, dtype=np.int64), offsets=off, ids=np.concatenate(ids))
    print(f"identities of {len(rows):,} reports, {int(off[-1]):,} calls")


if __name__ == "__main__":
    main()
