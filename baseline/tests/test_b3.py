"""Tests for B3 (Fig. 6 with the v2 recipe): the splits, the validation-only selection rule (NOTES.md 11.4), and a tiny end-to-end run on CPU."""
import json
import os
import types

import numpy as np
import pytest

from baseline import b3, b3_report as BR, common as C

C.setup_nebula(require_patched=True)
V = 200
LABELS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "results", "_tokens_raw", "out", "labels.npz")


def fake_ym(n=3000, seed=0):
    r = np.random.default_rng(seed)
    return r.choice(8, n, p=[0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.15, 0.15])


def test_split_is_disjoint_stratified_and_deterministic():
    ym = fake_ym()
    unl, lab, val, info = b3.b3_split(ym, 0, check=False)
    assert len(unl) + len(lab) + len(val) == len(ym) and not (set(unl) | set(lab)) & set(val) and not set(unl) & set(lab)
    assert abs(len(lab) / (len(lab) + len(unl)) - 0.2) < 0.01 and abs(len(val) / len(ym) - 0.1) < 0.01
    for c in range(8):                                                # stratified by family
        assert abs((ym[lab] == c).mean() - (ym[unl] == c).mean()) < 0.02
    unl2, lab2, val2, info2 = b3.b3_split(ym, 0, check=False)
    assert info == info2 and b3.b3_split(ym, 1, check=False)[3]["sha256"] != info["sha256"]


@pytest.mark.skipif(not os.path.exists(LABELS), reason="labels of the tokens dataset not on this machine")
def test_stored_hashes_match_the_published_labels():
    ym = np.load(LABELS)["ym_train"]
    ref = json.load(open(b3.HASHES))["seeds"]
    for s in range(5):
        unl, lab, val, info = b3.b3_split(ym, s)                      # asserts the validation slice (F) and the stored 80/20 hash
        assert info == ref[str(s)] and (len(unl), len(lab), len(val)) == (54214, 13554, 7530)


def cell(curves, losses, auc_last=0.99):
    """cell[seed] = result dict with per-epoch validation TPR@1e-3 and loss; curves[seed] = list over epochs."""
    out = {}
    for s, (c, l) in enumerate(zip(curves, losses)):
        out[s] = {"per_epoch": [{"val": {"tpr@0.001": t, "tpr@0.01": 0.9, "auc": 0.99}, "val_loss": ls} for t, ls in zip(c, l)]}
        out[s]["per_epoch"][-1]["val"]["auc"] = auc_last
    return out


def test_choose_best_epoch_then_ties_go_to_fewer_epochs_then_lower_loss():
    # tpr mean per epoch: .50 .70 .72 .71 .60 .50; std ~0.1 -> SE 0.045: epochs 2, 3, 4 are all within one SE of the best (epoch 3) -> the fewest epochs = 2
    base = np.array([0.50, 0.70, 0.72, 0.71, 0.60, 0.50])
    off = np.array([0.1, 0.05, 0.0, -0.05, -0.1])
    curves = [list(base + o * (1 if i % 2 else -1)) for i, o in enumerate(off)]
    curves = [list(base + o) for o in off]                         # seed offsets: mean = base, std 0.0791 -> SE 0.0354
    R = {"upper": {2e-3: cell(curves, [[0.3] * 6] * 5)}}
    ch = BR.choose(R)["upper"]
    assert ch["lr"] == 2e-3 and ch["epoch"] == 2 and ch["n_tied"] == 3
    # two lrs, identical TPR curves, lr 1e-3 has the lower validation loss at the (same) chosen epoch -> lr 1e-3
    R = {"upper": {2e-3: cell(curves, [[0.3] * 6] * 5), 1e-3: cell(curves, [[0.2] * 6] * 5)}}
    ch = BR.choose(R)["upper"]
    assert ch["lr"] == 1e-3 and ch["epoch"] == 2
    # a clear winner (no tie): the best epoch is taken even if it is late
    steep = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.9])
    R = {"lower": {2e-3: cell([list(steep + o * 0.001) for o in off], [[0.3] * 6] * 5)}}
    assert BR.choose(R)["lower"]["epoch"] == 6


def test_collapse_guard_excludes_a_collapsed_lr():
    good = [[0.6, 0.7, 0.7, 0.7, 0.7, 0.7]] * 5
    c_bad = cell([[0.0] * 6] + good[1:], [[0.3] * 6] * 5, auc_last=0.5)                         # every seed's last epoch has AUC 0.5 -> collapsed
    c_bad[1] = cell(good, [[0.3] * 6] * 5)[1]                                                    # only seeds 0, 2, 3, 4 collapsed; still excluded
    c_ok = cell([[0.55, 0.6, 0.62, 0.6, 0.6, 0.6]] * 5, [[0.4] * 6] * 5)
    R = {"mlm_bert": {2e-3: c_bad, 1e-3: c_ok}}
    ch = BR.choose(R)["mlm_bert"]
    assert ch["lr"] == 1e-3 and "0.002" in ch["excluded"] and {c["lr"] for c in ch["cells"]} == {1e-3}


def tiny_data(n=360, L=512, seed=0):
    r = np.random.default_rng(seed)
    x = np.zeros((n, L), dtype=np.int32)
    y = (r.random(n) < 0.5).astype(np.int64)
    for i in range(n):
        k = int(r.integers(60, 200))
        x[i, :k] = r.integers(3, V - 5, k) + y[i] * 5
    return x, y


def test_tiny_end_to_end_units_on_cpu(tmp_path):
    x, y = tiny_data()
    xt, yt = x[300:], y[300:]
    val, lab, unl = np.arange(0, 40), np.arange(40, 120), np.arange(120, 300)
    vocab = {"<pad>": 0, "<unk>": 1, "<mask>": 2, **{f"t{i}": i for i in range(3, V)}}
    a = types.SimpleNamespace(device="cpu", lrs=[2e-3], epochs=2, variant="test", tokens_info={}, pt_epochs=2, pt_patience=2, min_delta=0.01,
                              batch_size=96, lr=2.5e-4, workers=0)
    out = str(tmp_path / "seed0")
    b3.execute("sup", a, 0, x, y, xt, yt, vocab, unl, lab, val, {"sha256": "x"}, out)
    for run in ("upper", "lower", "lower_lasttoken"):
        d = json.load(open(os.path.join(out, f"{run}_lr0.002.json")))
        assert len(d["per_epoch"]) == 2 and d["n_val"] == 40 and not d["collapsed"] in (None,)
        assert d["n_train"] == (260 if run == "upper" else 80)                                   # upper = unlabeled + labeled, the others the labeled part only
        assert np.load(os.path.join(out, f"{run}_lr0.002_test_logits.npy")).shape == (2, 60)     # one row per epoch
        assert np.load(os.path.join(out, f"{run}_lr0.002_val_logits.npy")).shape == (2, 40)
    b3.execute("ar", a, 0, x, y, xt, yt, vocab, unl, lab, val, {"sha256": "x"}, out)
    d = json.load(open(os.path.join(out, "ar_lasttoken_lr0.002.json")))
    h = json.load(open(os.path.join(out, "pretrain_ar_v2.json")))
    assert h["n_pretrain"] == 180 and h["n_val"] == 40                                           # all unlabeled reports trained on; the LM validation is the slice
    assert d["weight_proof"]["after_loading"]["dist_to_pretrained"] < 1e-6 < d["weight_proof"]["before_loading"]["dist_to_pretrained"]
    assert sorted(os.listdir(os.path.join(out, "ckpt_ar"))) == ["epoch1.pt", "epoch2.pt"]
    # the selection and the stats run on the outputs (3 more seeds' worth of copies would be needed for the full pipeline: only `choose` here)
    R = BR.load(str(tmp_path))
    assert set(R) == {"upper", "lower", "lower_lasttoken", "ar_lasttoken"} and BR.val_curve(R["upper"][2e-3], "auc").shape == (1, 2)


def fake_raw(raw, y, nval=300, seed=0):
    """5 seeds x 5 run types x 2 lrs x 6 epochs of fake results; the run types differ in signal strength (upper > ar > mlm > control > lower)."""
    r = np.random.default_rng(seed)
    strength = {"upper": 3.0, "ar_lasttoken": 2.4, "mlm_bert": 2.2, "lower_lasttoken": 1.6, "lower": 1.5}
    yv = (r.random(nval) < 0.5).astype(int)
    for s in range(5):
        os.makedirs(os.path.join(raw, f"seed{s}"), exist_ok=True)
        for run, st in strength.items():
            for lr in (2e-3, 1e-3):
                zt = np.stack([r.normal(size=len(y)) + st * y * (0.8 + 0.04 * e) for e in range(6)]).astype(np.float32)
                zv = np.stack([r.normal(size=nval) + st * yv * (0.8 + 0.04 * e) for e in range(6)]).astype(np.float32)
                np.save(os.path.join(raw, f"seed{s}", f"{run}_lr{lr:g}_test_logits.npy"), zt)
                np.save(os.path.join(raw, f"seed{s}", f"{run}_lr{lr:g}_val_logits.npy"), zv)
                per = []
                for e in range(6):
                    mv, mt = C.binary_metrics(yv, zv[e], decision=0.0), C.binary_metrics(y, zt[e], decision=0.0)
                    from baseline import gap
                    per.append({"epoch": e + 1, "val": gap.compact(mv), "val_loss": 0.3 + 0.01 * e, "test_NOT_FOR_SELECTION": gap.compact(mt)})
                json.dump({"run": run, "lr": lr, "seed": s, "epochs": 6, "per_epoch": per, "pretraining": None}, open(os.path.join(raw, f"seed{s}", f"{run}_lr{lr:g}.json"), "w"))


def test_report_pipeline_on_synthetic_results(tmp_path, monkeypatch):
    import sys
    r = np.random.default_rng(1)
    y = (r.random(2000) < 0.5).astype(int)
    raw, out, plots = str(tmp_path / "raw"), str(tmp_path / "out"), str(tmp_path / "plots")
    fake_raw(raw, y)
    np.save(tmp_path / "y.npy", y)
    monkeypatch.setattr(sys, "argv", ["b3_report", "--raw", raw, "--out", out, "--plots", plots, "--y", str(tmp_path / "y.npy"), "--boot", "20"])
    BR.main()
    for f in ("choice.json", "chosen_metrics.json", "bootstrap.json", "tables.md"):
        assert os.path.exists(os.path.join(out, f))
    assert os.path.exists(os.path.join(plots, "fig6_v2.png")) and os.path.exists(os.path.join(plots, "b3_val_curves.png"))
    txt = open(os.path.join(out, "tables.md")).read()
    assert "upper − lower" in txt and "AR − its causal control" in txt and "NOT used for selection" in txt
    boot = json.load(open(os.path.join(out, "bootstrap.json")))["bootstrap"]
    assert boot["upper"]["tpr@0.01"]["ps"]["vs_lower"]["point"] > 0                     # upper really beats lower in the synthetic data
    assert "vs_ctrl" in boot["ar_lasttoken"]["tpr@0.001"]["ps"] and "upper_minus" in boot["mlm_bert"]["auc" if False else "tpr@0.01"]["ps"]
