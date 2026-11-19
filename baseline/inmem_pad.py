"""
Balanced padding built IN MEMORY from the call-token store (baseline/callstore.py): nothing edited is ever written to disk.   (OURS)

epoch_edits(...) returns, for one (seed, epoch), the edited reports of the training rows as a uint16 array [n, 512] and their row numbers, using the plan of baseline/make_pad.py
(`plan_train_row`: probability 0.5, k ~ U{1..50}, insert/prepend 50/50, calls drawn from the TRAIN pool = benign reports of the 90% slice with at least one call) and `callstore.build_tokens`.
  stream 7000  the stream of REPORT 5.10 (the padded report REPLACES the original)
  stream 7100  the new stream of the 'keep' runs (a padded COPY is ADDED to all the clean reports)
  labels="malware"  only malware training reports are eligible (the plan of a report does not depend on the others, so the malware edits are identical to those of stream 7000 with all labels)
"""
import numpy as np

from baseline import callstore as CS
from baseline.make_pad import apply_plan, plan_train_row


def pool_rows_of(store, y, trn):
    """TRAIN pool: benign reports of the training slice with at least one call (our row numbers, in the order of `trn`)."""
    return np.array([int(r) for r in trn if y[r] == 0 and store.n_calls(int(r)) > 0], dtype=np.int64)


def edit_row(store, row, plan, pool_rows):
    """(tokens [512] uint16, total tokens of the whole edited report) of report `row` edited by `plan`, built from the store's pieces."""
    n = store.n_calls(int(row))
    added = [(store, int(pool_rows[pr]), int(c)) for pr, c in plan["draws"]]
    order = apply_plan(list(range(n)), plan, added)
    return CS.build_tokens(store, int(row), order)


def epoch_edits(store, y, trn, seed, epoch, pool_rows, stream=7000, labels="all", p_pad=0.5):
    """(rows [m] int64, tokens [m, 512] uint16) of the edited training reports of this (seed, epoch)."""
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    rows, toks = [], []
    for r in trn:
        r = int(r)
        if labels == "malware" and y[r] == 0:
            continue
        plan = plan_train_row(r, seed, epoch, store.n_calls(r), pool_n, stream, p_pad)
        if plan is None:
            continue
        rows.append(r)
        toks.append(edit_row(store, r, plan, pool_rows)[0])
    if not rows:
        return np.zeros(0, dtype=np.int64), np.zeros((0, CS.SEQ), dtype=np.uint16)
    return np.asarray(rows, dtype=np.int64), np.stack(toks)


VAL_ROBUST_STREAM, VAL_ROBUST_K = 8200, 20


def val_robust_set(store, y, val, pool_rows):
    """The fixed padded validation set of the tuning of NOTES 16: every validation MALWARE report with 20 calls prepended, the calls drawn from the TRAIN pool (default_rng([8200, row]): per call a
    uniform pool report, then a uniform call of it); the same draw for every cell, seed and epoch; reports without calls also receive the calls. In memory only.
    Returns (rows int64, tokens uint16 [m, 512])."""
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    rows, toks = [], []
    for r in val:
        r = int(r)
        if y[r] != 1:
            continue
        rng = np.random.default_rng([VAL_ROBUST_STREAM, r])
        added = []
        for _ in range(VAL_ROBUST_K):
            pr = int(rng.integers(len(pool_rows)))
            added.append(store.call(int(pool_rows[pr]), int(rng.integers(pool_n[pr]))))
        rows.append(r)
        toks.append(CS.build_fast(store, r, added, None)[0])
    return np.asarray(rows, dtype=np.int64), np.stack(toks)
