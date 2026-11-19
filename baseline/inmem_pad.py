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


def epoch_edits(store, y, trn, seed, epoch, pool_rows, stream=7000, labels="all"):
    """(rows [m] int64, tokens [m, 512] uint16) of the edited training reports of this (seed, epoch)."""
    pool_n = np.array([store.n_calls(int(r)) for r in pool_rows], dtype=np.int64)
    rows, toks = [], []
    for r in trn:
        r = int(r)
        if labels == "malware" and y[r] == 0:
            continue
        plan = plan_train_row(r, seed, epoch, store.n_calls(r), pool_n, stream)
        if plan is None:
            continue
        rows.append(r)
        toks.append(edit_row(store, r, plan, pool_rows)[0])
    if not rows:
        return np.zeros(0, dtype=np.int64), np.zeros((0, CS.SEQ), dtype=np.uint16)
    return np.asarray(rows, dtype=np.int64), np.stack(toks)
