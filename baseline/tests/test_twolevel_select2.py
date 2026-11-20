import json
import os

import numpy as np

from baseline import twolevel_select2 as S


def make(tmp, means):
    """means[(cell, epoch, weights)] -> mean; ten seeds with a small fixed spread."""
    rng = np.random.default_rng(0)
    off = rng.normal(0, 0.005, 10)
    for tag in S.CELLS:
        os.makedirs(os.path.join(tmp, tag), exist_ok=True)
        for s in range(10):
            pe = []
            for ep in (1, 2, 3):
                r = lambda w: {"val_pauc@1e-2": means.get((tag, ep, w), 0.90) + off[s], "val_auc": 0.99, "val_loss": 0.05}
                pe.append({**r("raw"), "ema": r("ema")})
            json.dump({"per_epoch": pe}, open(os.path.join(tmp, tag, f"seed{s}.json"), "w"))


def run(tmp):
    runs = {t: tmp for t in S.CELLS}
    return S.select(S.candidates(runs))


def test_tied_candidates_prefer_fewer_epochs_then_lower_lr_then_raw(tmp_path):
    m = {("R1_dec_lr1e-3", 3, "raw"): 0.95, ("R2_dec_lr5e-4", 3, "raw"): 0.95, ("R2_dec_lr5e-4", 2, "ema"): 0.948, ("R2_dec_lr5e-4", 2, "raw"): 0.948, ("R3_const_lr3e-4", 2, "raw"): 0.949}
    make(str(tmp_path), m)
    best, ch = run(str(tmp_path))
    assert (ch["epoch"], ch["lr"], ch["weights"]) == (2, 3e-4, "raw"), ch


def test_collapse_guard_excludes_a_candidate(tmp_path):
    make(str(tmp_path), {("R1_dec_lr1e-3", 3, "raw"): 0.99})
    f = os.path.join(str(tmp_path), "R1_dec_lr1e-3", "seed4.json")
    d = json.load(open(f))
    d["per_epoch"][2]["val_auc"] = 0.5
    json.dump(d, open(f, "w"))
    best, ch = run(str(tmp_path))
    assert not (best["cell"] == "R1_dec_lr1e-3" and best["epoch"] == 3 and best["weights"] == "raw")
