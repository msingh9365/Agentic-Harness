"""
Re-score saved models with LOGITS instead of float32 probabilities (CPU, no retraining).   (OURS)

Why: after the float32 sigmoid, thousands of malware and tens of benign reports tie at exactly 1.0. FPR 1e-3 allows 8 benign
reports of 8,003; when the tie group at the top holds more, the ROC has no point with FPR <= 1e-3 and the authors'
get_tpr_at_fpr returns 0.0. That is an artifact of the output precision, not of the model. Ranking by the logit removes the ties.
The original (literal) numbers are kept in `test_p32`.

    python -m baseline.rescore --results results/baseline_raw --tokens results/_tokens_raw/out
"""
import argparse
import glob
import json
import os
import time

import numpy as np
import torch

from baseline import common as C, cv, lm


def load_arrays(tokens, variant):
    vdir = os.path.join(tokens, "variants", variant)
    return np.load(os.path.join(vdir, "x_train.npy")), np.load(os.path.join(vdir, "x_test.npy"))


def rescore_detect(res, tokens, labels, splits):
    from nebula.models.attention import TransformerEncoderChunks
    for mf in sorted(glob.glob(os.path.join(res, "detect", "*", "metrics.json"))):
        d = os.path.dirname(mf)
        tag = os.path.basename(d)
        m = json.load(open(mf))
        if "test_p32" in m["folds"][0] and m["folds"][0]["test_p32"] is not None:
            print(f"[{tag}] already rescored", flush=True)
            continue
        variant = tag.rsplit("_", 2)[0]
        x, xt = load_arrays(tokens, variant)
        y, yt = labels["y_train"], labels["y_test"]
        model = TransformerEncoderChunks(**m["config"])
        t0 = time.time()
        for i, fold in enumerate(m["folds"]):
            model.load_state_dict(torch.load(os.path.join(d, f"fold{i}_model.pt"), map_location="cpu", weights_only=True))
            va = np.asarray(splits["kfold3"][i]["val"])
            zv, zt = cv.predict_logits(model, x[va], "cpu"), cv.predict_logits(model, xt, "cpu")
            fold["val_p32"], fold["test_p32"] = fold["val"], fold["test"]          # the literal numbers from the Kaggle run
            fold["val"], fold["test"] = C.binary_metrics(y[va], zv, decision=0.0), C.binary_metrics(yt, zt, decision=0.0)
            np.save(os.path.join(d, f"fold{i}_test_logits.npy"), zt.astype(np.float32))
        cv.aggregate(m, "binary")
        C.dump_json(m, mf)
        t = m["test_mean_std"]
        print(f"[{tag}] {time.time() - t0:.0f}s  test TPR@1e-3 literal {m['test_p32_mean_std']['tpr@0.001']['mean']:.4f} -> logit-ranked "
              f"{t['tpr@0.001']['mean']:.4f} | AUC {t['auc']['mean']:.4f}", flush=True)


def rescore_released(res, tokens, labels, nebula_root):
    from nebula.models.attention import TransformerEncoderChunks
    mf = os.path.join(res, "released", "metrics.json")
    m = json.load(open(mf))
    for variant, fname in {"released_bpe50k": "bpe_50000_torch.model", "released_ws50k": "whitespace_50000_torch.model"}.items():
        if variant not in m or "test_p32" in m[variant]:
            continue
        x, xt = load_arrays(tokens, variant)
        model = TransformerEncoderChunks(**cv.model_config(len(json.load(open(os.path.join(tokens, "variants", variant, "vocab.json"))))))
        model.load_state_dict(torch.load(os.path.join(nebula_root, "nebula", "objects", fname), weights_only=True))
        zt, ztr = cv.predict_logits(model, xt, "cpu"), cv.predict_logits(model, x, "cpu")
        m[variant]["test_p32"] = m[variant]["test"]
        m[variant]["test"] = C.binary_metrics(labels["y_test"], zt, decision=0.0)
        m[variant]["train_in_sample"] = C.binary_metrics(labels["y_train"], ztr, decision=0.0)
        np.save(os.path.join(res, "released", f"{variant}_test_logits.npy"), zt.astype(np.float32))
        print(f"[{variant}] released: TPR@1e-3 literal {m[variant]['test_p32']['tpr@0.001']:.4f} -> logit-ranked {m[variant]['test']['tpr@0.001']:.4f}", flush=True)
    C.dump_json(m, mf)


def rescore_ssl(res, tokens, labels):
    from baseline import selfsup
    xt = np.load(os.path.join(tokens, "variants", "bpe8k", "x_test.npy"))
    V = len(json.load(open(os.path.join(tokens, "variants", "bpe8k", "vocab.json"))))
    for mf in sorted(glob.glob(os.path.join(res, "ssl", "seed*", "*", "metrics.json"))):
        d = os.path.dirname(mf)
        m = json.load(open(mf))
        if "test_p32" in m:
            continue
        run = m["run"]
        model = selfsup.downstream_model(run, V)
        model.load_state_dict(torch.load(os.path.join(d, "model.pt"), map_location="cpu", weights_only=True))
        t0 = time.time()
        zt = cv.predict_logits(model, xt, "cpu", bs=128)
        m["test_p32"], m["test"] = m["test"], C.binary_metrics(labels["y_test"], zt, decision=0.0)
        np.save(os.path.join(d, "test_logits.npy"), zt.astype(np.float32))
        C.dump_json(m, mf)
        print(f"[ssl seed{m['seed']} {run}] {time.time() - t0:.0f}s TPR@1e-3 literal {m['test_p32']['tpr@0.001']:.4f} -> logit-ranked {m['test']['tpr@0.001']:.4f}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--only", default="detect,released,ssl")
    a = ap.parse_args()
    nb = C.setup_nebula(require_patched=True)
    torch.set_num_threads(os.cpu_count())
    labels = np.load(os.path.join(a.tokens, "labels.npz"))
    splits = json.load(open(os.path.join(a.tokens, "splits.json")))
    todo = a.only.split(",")
    if "detect" in todo:
        rescore_detect(a.results, a.tokens, labels, splits)
    if "released" in todo:
        rescore_released(a.results, a.tokens, labels, nb["nebula_root"])
    if "ssl" in todo:
        rescore_ssl(a.results, a.tokens, labels)


if __name__ == "__main__":
    main()
