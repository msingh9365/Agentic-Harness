"""
Tables and figure of the attacks for the tuned candidate (REPORT 5.12): the families of REPORT 5.11 (released, v2-PE, PE+bal, ATT+bal) plus the tuned ATT+bal, with the comparison tuned - existing ATT+bal.   (OURS)

    python -m baseline.tune_attacks --tuned-src results/tune/attack --out results/tune

Reuses baseline/review_attacks.py. The scores of the existing families are read from results/review/attack (they are not recomputed), the scores of the tuned family from --tuned-src; a merged
folder of links results/tune/attack_all is made. Only scores are read; nothing edited exists.
"""
import argparse
import glob
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tuned-src", default=os.path.join(ROOT, "results", "tune", "attack"))
    ap.add_argument("--old-src", default=os.path.join(ROOT, "results", "review", "attack"))
    ap.add_argument("--out", default=os.path.join(ROOT, "results", "tune"))
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    merged = os.path.join(a.out, "attack_all")
    shutil.rmtree(merged, ignore_errors=True)
    os.makedirs(merged)
    for f in ("released", "v2_pe", "pebal", "attbal"):
        for p in glob.glob(os.path.join(a.old_src, f"*_{f}.npz")) + glob.glob(os.path.join(a.old_src, f"a3b_{f}_seed*.npz")):
            os.symlink(os.path.abspath(p), os.path.join(merged, os.path.basename(p)))
    for p in glob.glob(os.path.join(a.old_src, "*_meta_*.npz")):
        os.symlink(os.path.abspath(p), os.path.join(merged, os.path.basename(p)))
    for p in glob.glob(os.path.join(a.tuned_src, "*tuned*.npz")):
        os.symlink(os.path.abspath(p), os.path.join(merged, os.path.basename(p)))
    g = os.path.join(ROOT, "results", "review", "april_hash_apis_group.npy")
    shutil.copy(g, os.path.join(a.out, "april_hash_apis_group.npy"))
    from baseline import review_attacks as RA
    RA.ORDER = ["released", "v2_pe", "pebal", "attbal", "tuned"]
    RA.FIG_FAMS = ("released", "v2_pe", "pebal", "attbal", "tuned")
    RA.LABEL["tuned"] = "ATT+bal-tuned"
    RA.PAIRS = [("tuned", "attbal"), ("tuned", "v2_pe")]
    sys.argv = ["review_attacks", "--src", merged, "--out", a.out, "--boot", str(a.boot)]
    RA.main()


if __name__ == "__main__":
    main()
