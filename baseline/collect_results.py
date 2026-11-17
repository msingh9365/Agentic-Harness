"""Copy the small result files (metrics JSON, configs, logs) of a finished run into results/<experiment>/.   (OURS)

    python -m baseline.collect_results --raw results/baseline_raw --out results

No model weights, token arrays or per-report scores are copied (they are in the Kaggle datasets).
"""
import argparse
import glob
import os
import shutil

GROUPS = {"A_detection": "detect", "C_classification": "classify", "D_ablations": "ablate", "B_selfsup": "ssl", "E_released": "released"}


def collect_long(raw, out):
    """Follow-up B2: <raw>/ssl_long/seed*/<run>/{metrics.json,test_logits.npy}, pretrain_*_long.json, logs -> <out>/B_selfsup_long."""
    n = 0
    for f in glob.glob(os.path.join(raw, "ssl_long", "seed*", "**", "*"), recursive=True):
        base = os.path.basename(f)
        if os.path.isdir(f) or "ckpt_ar" in f or not (base.endswith(".json") or base == "test_logits.npy"):
            continue
        dst = os.path.join(out, "B_selfsup_long", os.path.relpath(f, os.path.join(raw, "ssl_long")))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(f, dst)
        n += 1
    for f in glob.glob(os.path.join(raw, "logs", "long_*.log")):
        dst = os.path.join(out, "baseline_logs", "long", os.path.basename(f))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(f, dst)
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", default="results")
    ap.add_argument("--long-raw", nargs="*", default=[], help="output folders of the follow-up kernels (contain ssl_long/)")
    a = ap.parse_args()
    n = sum(collect_long(r, a.out) for r in a.long_raw)
    for exp, sub in GROUPS.items():
        for f in glob.glob(os.path.join(a.raw, sub, "**", "*.json"), recursive=True):
            dst = os.path.join(a.out, exp, os.path.relpath(f, os.path.join(a.raw, sub)))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(f, dst)
            n += 1
    # per-report test logits of the self-supervised runs (17,402 floats each): needed for the paired bootstrap of the follow-up
    for f in glob.glob(os.path.join(a.raw, "ssl", "seed*", "*", "test_logits.npy")):
        dst = os.path.join(a.out, "B_selfsup", os.path.relpath(f, os.path.join(a.raw, "ssl")))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(f, dst)
        n += 1
    for f in glob.glob(os.path.join(a.raw, "logs*", "*.log")):
        dst = os.path.join(a.out, "baseline_logs", os.path.basename(os.path.dirname(f)), os.path.basename(f))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(f, dst)
        n += 1
    print(f"copied {n} files into {a.out}")


if __name__ == "__main__":
    main()
