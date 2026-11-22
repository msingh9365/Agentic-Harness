"""
P3 training (NOTES 27): M1 (flatten, lr 2e-3, 1 epoch) and M3 (attention, lr 1e-3, balanced padding p 0.5, 3 epochs) with the role-normalised tokenizer, seeds 0-9, one kernel (one GPU session): runs `gs_grid --family v2pe --p3 role` and then `--family attbal --p3 role`.   (OURS)

    python -m baseline.gs_p3_train --p3 role --out /kaggle/working/out
"""
import argparse
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p3", default="role", choices=["role", "addr"])
    ap.add_argument("--out", default="/kaggle/working/out")
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=0, help="smoke test only")
    ap.add_argument("--device", default="cuda")
    a = ap.parse_args()
    for fam in ("v2pe", "attbal"):
        cmd = [sys.executable, "-m", "baseline.gs_grid", "--family", fam, "--p3", a.p3, "--out", a.out, "--device", a.device]
        cmd += (["--seeds"] + [str(x) for x in a.seeds]) if a.seeds else []
        cmd += ["--limit", str(a.limit)] if a.limit else []
        rc = subprocess.call(cmd)
        if rc:
            raise SystemExit(f"{fam} failed with exit code {rc}")


if __name__ == "__main__":
    main()
