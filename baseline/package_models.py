"""
Collect the trained models, tokenizers and the AR-pretrained encoders of a finished run into baseline_models/.   (OURS)

    python -m baseline.package_models --results results/baseline_raw --tokens results/_tokens_raw --out baseline_models --big /tmp/models_big

Layout of --out (small files, committed to git):
    manifest.json                    key -> {arch, tokenizer, weights, ...}; read by baseline_models/load_baseline.py
    tokenizers/<name>/...            tokenizer.model (BPE) + vocab.json for bpe50k, ws50k, bpe8k
    ssl/ar_pretrained_seed{0..4}.pt the AR-pretrained encoder BEFORE fine-tuning (with its LM head), full-attention causal Nebula, V = 8,193
Layout of --big (too large for git, published as the private Kaggle dataset msingh9365/nebula-baseline-models together with the files
above, so that one folder holds everything):
    detection/<variant>/<regime>/seed<s>_fold<i>.pt, classification/..., ssl/<run>_seed<k>.pt   (variant: bpe50k, ws50k, ws50k_legacy)
"""
import argparse
import glob
import json
import os
import shutil

from baseline import common as C


def put(src, dst):
    """Hard link when possible (same disk, no extra space), else copy."""
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        os.remove(dst)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy(src, dst)


def cp(src, dst):
    put(src, dst)
    return os.path.relpath(dst, os.path.dirname(os.path.dirname(dst)))


def add_long(out, big, long_raws):
    """Follow-up B2: add the AR-pretrained encoders of the long pre-training (best epoch, per seed) to <out>/ssl and the manifest, and the
    epoch-3/6/10 checkpoints to <big>/ssl/ar_long_checkpoints (Kaggle dataset only). Run after the main packaging."""
    man = json.load(open(os.path.join(out, "manifest.json")))
    n = 0
    for raw in long_raws:
        for sd in sorted(glob.glob(os.path.join(raw, "ssl_long", "seed*"))):
            seed = os.path.basename(sd)[4:]
            best = os.path.join(sd, "pretrained_ar_long.pt")
            if not os.path.exists(best):
                continue
            h = json.load(open(os.path.join(sd, "pretrain_ar_long.json")))
            put(best, os.path.join(out, "ssl", f"ar_pretrained_long_seed{seed}.pt"))
            put(best, os.path.join(big, "ssl", f"ar_pretrained_long_seed{seed}.pt"))
            man["models"][f"ssl/ar_pretrained_long/seed{seed}"] = {
                "arch": "ar_pretrained", "tokenizer": "bpe8k", "weights": f"ssl/ar_pretrained_long_seed{seed}.pt", "seq_len": 512,
                "pretrain_epoch": h["best_epoch"], "epochs_run": len(h["epochs"]), "val_lm_loss": h["epochs"][h["best_epoch"] - 1]["val_loss"],
                "note": "causal full-attention Nebula, next-token pre-trained up to 15 epochs on 80% of January (best validation epoch); with LM head. "
                        "The 3-epoch encoders are ssl/ar_pretrained/seed<k>"}
            for ep in (3, 6, 10):
                c = os.path.join(sd, "ckpt_ar", f"epoch{ep}.pt")
                if os.path.exists(c):
                    put(c, os.path.join(big, "ssl", "ar_long_checkpoints", f"seed{seed}_epoch{ep}.pt"))
            n += 1
    for d in (out, big):
        C.dump_json(man, os.path.join(d, "manifest.json"))
    print(f"added {n} long AR encoders to the manifest ({len(man['models'])} models in total)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--out", default="baseline_models")
    ap.add_argument("--big", required=True)
    ap.add_argument("--long-raw", nargs="*", default=None, help="only add the long pre-training encoders of these kernel outputs (contain ssl_long/)")
    a = ap.parse_args()
    if a.long_raw is not None:
        return add_long(a.out, a.big, a.long_raw)
    models = {}
    for tk in ["bpe50k", "ws50k", "ws50k_legacy", "bpe8k"]:
        src = os.path.join(a.tokens, "variants", tk)
        if not os.path.isdir(src):
            continue
        for d in (a.out, a.big):
            os.makedirs(os.path.join(d, "tokenizers", tk), exist_ok=True)
            for f in ("tokenizer.model", "vocab.json", "info.json"):
                if os.path.exists(os.path.join(src, f)):
                    shutil.copy(os.path.join(src, f), os.path.join(d, "tokenizers", tk, f))
    # detection and classification fold models
    for task, sub in [("detect", "detect"), ("classify", "classify")]:
        for mf in sorted(glob.glob(os.path.join(a.results, sub, "*", "metrics.json"))):
            m = json.load(open(mf))
            tag = os.path.basename(os.path.dirname(mf))
            variant = "ws50k_legacy" if "legacy" in tag else ("ws50k" if "ws50k" in tag else "bpe50k")
            regime = "time" if "_time_" in tag else "batches"
            seed = tag.rsplit("seed", 1)[1]
            for i, fold in enumerate(m["folds"]):
                w = os.path.join(os.path.dirname(mf), f"fold{i}_model.pt")
                if not os.path.exists(w):
                    continue
                rel = f"{'detection' if task == 'detect' else 'classification'}/{variant}/{regime}/seed{seed}_fold{i}.pt"
                put(w, os.path.join(a.big, rel))
                key = f"{'detect' if task == 'detect' else 'classify'}/{variant}/{regime}/seed{seed}/fold{i}"
                t = m["test"] if "test" in m else m["folds"][i]["test"]
                models[key] = {"arch": "chunked", "tokenizer": variant, "weights": rel, "seq_len": 512,
                               "n_classes": 1 if task == "detect" else 8, "batches_seen": fold["batches_seen"],
                               "test": {k: fold["test"][k] for k in fold["test"] if k in ("auc", "tpr@0.001", "f1@0.5", "acc@0.5", "f1_macro", "acc")}}
    # self-supervised models
    for sd in sorted(glob.glob(os.path.join(a.results, "ssl", "seed*"))):
        seed = os.path.basename(sd)[4:]
        pre = os.path.join(sd, "pretrained_ar.pt")
        if os.path.exists(pre):
            rel = cp(pre, os.path.join(a.out, "ssl", f"ar_pretrained_seed{seed}.pt"))
            put(pre, os.path.join(a.big, "ssl", f"ar_pretrained_seed{seed}.pt"))
            models[f"ssl/ar_pretrained/seed{seed}"] = {"arch": "ar_pretrained", "tokenizer": "bpe8k", "weights": f"ssl/ar_pretrained_seed{seed}.pt", "seq_len": 512,
                                                       "note": "causal full-attention Nebula, next-token pre-trained on 80% of January; with LM head"}
        for run in sorted(os.listdir(sd)):
            f = os.path.join(sd, run, "model.pt")
            if not os.path.exists(f):
                continue
            arch = {"upper": "chunked", "lower": "chunked", "mlm_theirs": "chunked", "mlm_bert": "chunked", "ar_flatten": "fullattn",
                    "ar_lasttoken": "fullattn_causal_lasttoken", "lower_fullattn": "fullattn", "upper_fullattn": "fullattn"}[run]
            rel = f"ssl/{run}_seed{seed}.pt"
            put(f, os.path.join(a.big, rel))
            m = json.load(open(os.path.join(sd, run, "metrics.json")))
            models[f"ssl/{run}/seed{seed}"] = {"arch": arch, "tokenizer": "bpe8k", "weights": rel, "seq_len": 512,
                                               "test": {k: m["test"][k] for k in ("auc", "tpr@0.001", "f1@0.5")}}
    man = {"nebula_commit": C.NEBULA_PINNED_COMMIT, "note": "load with baseline_models/load_baseline.py", "models": models}
    for d in (a.out, a.big):
        C.dump_json(man, os.path.join(d, "manifest.json"))
    print(f"{len(models)} models in the manifest; small files in {a.out}, everything in {a.big}")


if __name__ == "__main__":
    main()
