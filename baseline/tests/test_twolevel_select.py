"""Selection rule of NOTES 19.5 on synthetic run files."""
import json
import os

import numpy as np

from baseline import twolevel_select as S


def write(root, tag, means, aucs=None, rng=None):
    os.makedirs(os.path.join(root, tag), exist_ok=True)
    for s in range(10):
        pe = [{"val_pauc@1e-2": m + 0.002 * (s - 4.5) / 4.5, "val_loss": 0.05, "val_auc": (aucs or [0.99] * 3)[i]} for i, m in enumerate(means)]
        json.dump({"per_epoch": pe}, open(os.path.join(root, tag, f"seed{s}.json"), "w"))


def test_tie_break_fewest_epochs_then_lower_lr_then_scratch(tmp_path):
    r = str(tmp_path)
    for tag, init, lr in S.CELLS["A"]:
        write(r, tag, [0.95, 0.96, 0.96])
    c = S.candidates({t: r for t, _, _ in S.CELLS["A"]}, "A")
    sel, _ = S.select(c)
    ch = sel["chosen"]
    assert (ch["epoch"], ch["lr"], ch["init"]) == (2, 1e-3, "scratch")        # all cells tie: epoch 2 (fewest among the tied), lr 1e-3, scratch


def test_best_alone_when_clearly_ahead_and_collapse_guard(tmp_path):
    r = str(tmp_path)
    write(r, "A_scratch_lr1e-3", [0.90, 0.91, 0.92])
    write(r, "A_scratch_lr2e-3", [0.90, 0.91, 0.99], aucs=[0.99, 0.99, 0.5])    # best on paper, but collapsed at epoch 3 -> excluded
    write(r, "A_warm_lr1e-3", [0.90, 0.91, 0.94])
    write(r, "A_warm_lr2e-3", [0.90, 0.91, 0.93])
    sel, c = S.select(S.candidates({t: r for t, _, _ in S.CELLS["A"]}, "A"))
    assert (sel["chosen"]["cell"], sel["chosen"]["epoch"]) == ("A_warm_lr1e-3", 3)
    assert [x for x in c if x["cell"] == "A_scratch_lr2e-3" and x["epoch"] == 3][0]["collapsed"]
