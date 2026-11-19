"""
GPU stages of the review experiments (NOTES 15), one Kaggle kernel per stage.   (OURS)

    python -m baseline.review_gpu --stage smoke|3a|padprobe|3b1|3b2 --out /kaggle/working/out

Every stage runs baseline.attack_run / baseline.probe on the two GPUs (one process per GPU, one family or model-seed each). Inputs are found under /kaggle/input (labels.npz, all.npz,
all_released.npz, ranking.json, <kind>/seed<k>.pt). Edits are built in memory; only scores and AUCs are written to --out.
"""
import argparse
import os
import subprocess
import sys

STAGES = {
    "smoke": [("attack_run", ["--mode", "3a", "--seeds", "0"], ["v2_pe:v2_pe", "attbal:attbal"]), ("attack_run", ["--mode", "pad", "--seeds", "0"], ["v2_pe:v2_pe", "attbal:attbal"]),
              ("probe", ["--seeds", "0"], ["v2_pe:v2_pe", "attbal:attbal"]), ("attack_run", ["--mode", "3b", "--smoke"], ["v2_pe:v2_pe:0", "attbal:attbal:0"])],
    "3a": [("attack_run", ["--mode", "3a"], ["released:released", "v2_pe:v2_pe", "pebal:pebal", "attbal:attbal", "attkeep:attkeep", "pekeep:pekeep"])],
    "padprobe": [("attack_run", ["--mode", "pad"], ["released:released", "v2_pe:v2_pe", "pebal:pebal", "attbal:attbal", "attkeep:attkeep", "pekeep:pekeep", "attaug:attaug", "peaug:peaug"]),
                 ("probe", [], ["v2_pe:v2_pe", "pebal:pebal", "attbal:attbal", "attaug:attaug", "peaug:peaug"])],
    "3b1": [("attack_run", ["--mode", "3b"], ["released:released:0"] + [f"{f}:{f}:{s}" for f in ("v2_pe", "pebal") for s in (0, 1, 2)])],
    "tuned": [("attack_run", ["--mode", "3a"], ["tuned:tuned"]), ("attack_run", ["--mode", "pad"], ["tuned:tuned"]), ("attack_run", ["--mode", "3b"], [f"tuned:tuned:{s}" for s in (0, 1, 2)])],
    "3b2": [("attack_run", ["--mode", "3b"], [f"{f}:{f}:{s}" for f in ("attbal", "attkeep", "pekeep") for s in (0, 1, 2)])],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=list(STAGES))
    ap.add_argument("--out", required=True)
    ap.add_argument("--tuned-tag", default=None, help="stage 'tuned': the training run folder of the chosen candidate (e.g. tune_lr2e-3_p0.5)")
    ap.add_argument("--tuned-epoch", default=None)
    a = ap.parse_args()
    if a.tuned_tag:
        os.environ["TUNED_TAG"], os.environ["TUNED_EPOCH"] = a.tuned_tag, str(a.tuned_epoch)
    for module, extra, jobs in STAGES[a.stage]:
        cmd = [sys.executable, "-m", f"baseline.{module}", "--plan", "--search", "/kaggle/input", "--out", a.out, "--jobs"] + jobs + extra
        print("RUN:", " ".join(cmd), flush=True)
        rc = subprocess.call(cmd)
        if rc:
            raise SystemExit(f"{module} failed ({rc})")


if __name__ == "__main__":
    main()
