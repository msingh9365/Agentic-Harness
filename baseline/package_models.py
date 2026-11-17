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


V2_RECIPE = {"name": "baseline v2 (recipe R8_lr2e-3)", "lr": 2e-3, "clip_grad_norm": 0.5, "dropout": 0.3, "batch_size": 96, "weight_decay": 1e-2,
             "optimizer": "AdamW (the authors' ModelTrainer), BCE, constant lr, no schedule", "epochs": 2, "tokenizer": "bpe50k",
             "train_data": "90% of the January training reports (stratified by family, seed 2025, hash in baseline/gap_split_hash.json)",
             "selected_on": "held-out 10% January validation slice only (never on the April test set)"}


def add_v2(out, big, v2_dir):
    """Follow-up F (gap to the released model): add the 5 baseline-v2 detection models (recipe R8, epoch 2) to <big>/detection/bpe50k/v2 and the
    manifest. The test metrics are the logit-ranked ones; 'test_tpr@0.001_literal_float32' is the authors' number computed on float32 probabilities."""
    man = json.load(open(os.path.join(out, "manifest.json")))
    n = 0
    for f in sorted(glob.glob(os.path.join(v2_dir, "seed*_epoch2_model.pt"))):
        seed = os.path.basename(f)[4:].split("_")[0]
        r = json.load(open(os.path.join(v2_dir, f"seed{seed}.json")))
        e = r["per_epoch"][1]
        rel = f"detection/bpe50k/v2/seed{seed}.pt"
        put(f, os.path.join(big, rel))
        man["models"][f"detect/bpe50k/v2/seed{seed}"] = {
            "arch": "chunked", "tokenizer": "bpe50k", "weights": rel, "seq_len": 512, "n_classes": 1, "epochs": 2, "batches_seen": e["batches"],
            "recipe": V2_RECIPE, "seed": int(seed),
            "validation": {k: e["val"][k] for k in ("auc", "tpr@0.001", "tpr@0.01", "f1@0.5")} | {"loss": e["val_loss"]},
            "test": {k: e["test_NOT_FOR_SELECTION"][k] for k in ("auc", "tpr@0.001", "tpr@0.01", "f1@0.5", "acc@0.5")},
            "test_tpr@0.001_literal_float32": e["test_p32_tpr@0.001"],
            "note": "THE baseline from follow-up F on: load_baseline('bpe_v2', seed=k). Rank by logit (model.score_logit), not by float32 probability."}
        n += 1
    for d in (out, big):
        C.dump_json(man, os.path.join(d, "manifest.json"))
    print(f"added {n} baseline-v2 models to the manifest ({len(man['models'])} models in total)")


def add_b3(out, big, b3_raws, tokens_dir):
    """Follow-up B3: the AR and per-position-MLM encoders pre-trained on the v2 splits (best epoch, per seed, with their LM heads) -> <out>/ssl and <big>/ssl,
    the tokenizer bpe8k_v2 (fit on the 90% of January only) -> tokenizers/bpe8k_v2, and the manifest entries ssl/{ar,mlm}_pretrained_v2/seed<k>."""
    man = json.load(open(os.path.join(out, "manifest.json")))
    for d in (out, big):
        os.makedirs(os.path.join(d, "tokenizers", "bpe8k_v2"), exist_ok=True)
        for f in ("tokenizer.model", "vocab.json", "info.json"):
            src = os.path.join(tokens_dir, "variants", "bpe8k_v2", f)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(d, "tokenizers", "bpe8k_v2", f))
    n = 0
    for raw in b3_raws:
        for sd in sorted(glob.glob(os.path.join(raw, "b3", "seed*"))):
            seed = os.path.basename(sd)[4:]
            for kind, arch, fn in (("ar", "ar_pretrained", "ar_pretrained_v2"), ("mlm_bert", "mlm_pretrained", "mlm_pretrained_v2")):
                w, hp = os.path.join(sd, f"pretrained_{kind}_v2.pt"), os.path.join(sd, f"pretrain_{kind}_v2.json")
                if not (os.path.exists(w) and os.path.exists(hp)):
                    continue
                h = json.load(open(hp))
                put(w, os.path.join(out, "ssl", f"{fn}_seed{seed}.pt"))
                put(w, os.path.join(big, "ssl", f"{fn}_seed{seed}.pt"))
                man["models"][f"ssl/{fn}/seed{seed}"] = {
                    "arch": arch, "tokenizer": "bpe8k_v2", "weights": f"ssl/{fn}_seed{seed}.pt", "seq_len": 512, "seed": int(seed),
                    "pretrain_epoch": h["best_epoch"], "epochs_run": len(h["epochs"]), "val_lm_loss": h["epochs"][h["best_epoch"] - 1]["val_loss"],
                    "note": ("causal full-attention Nebula, next-token pre-trained (<= 6 epochs, best validation LM loss) on the unlabeled 80% of the 90% of January that is not the "
                             "validation slice; with LM head" if kind == "ar" else
                             "chunked Nebula, per-position BERT MLM pre-trained (<= 6 epochs, best validation LM loss) on the same split; with MLM head") +
                            ". Tokenizer bpe8k_v2 is fit on the 90% only. Splits: baseline/b3_split_hashes.json"}
                n += 1
    for d in (out, big):
        C.dump_json(man, os.path.join(d, "manifest.json"))
    print(f"added {n} B3 encoders to the manifest ({len(man['models'])} models in total)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--out", default="baseline_models")
    ap.add_argument("--big", required=True)
    ap.add_argument("--long-raw", nargs="*", default=None, help="only add the long pre-training encoders of these kernel outputs (contain ssl_long/)")
    ap.add_argument("--v2", default=None, help="only add the baseline-v2 models of this folder (gap/R8_lr2e-3 of the final kernel output)")
    ap.add_argument("--b3-raw", nargs="*", default=None, help="only add the B3 pre-trained encoders of these kernel outputs (contain b3/seed*/), needs --tokens (folder with variants/bpe8k_v2)")
    a = ap.parse_args()
    if a.b3_raw is not None:
        return add_b3(a.out, a.big, a.b3_raw, a.tokens)
    if a.v2:
        return add_v2(a.out, a.big, a.v2)
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
