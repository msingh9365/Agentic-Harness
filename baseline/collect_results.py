"""Copy the small result files (metrics JSON, configs, logs) of a finished run into results/<experiment>/.   (OURS)

    python -m baseline.collect_results --raw results/baseline_raw --out results

No model weights, token arrays or per-report scores are copied (they are in the Kaggle datasets).
"""
import argparse
import glob
import os
import shutil

GROUPS = {"A_detection": "detect", "C_classification": "classify", "D_ablations": "ablate", "B_selfsup": "ssl", "E_released": "released"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    n = 0
    for exp, sub in GROUPS.items():
        for f in glob.glob(os.path.join(a.raw, sub, "**", "*.json"), recursive=True):
            dst = os.path.join(a.out, exp, os.path.relpath(f, os.path.join(a.raw, sub)))
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
