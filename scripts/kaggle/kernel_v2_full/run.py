"""Kaggle entry point (v2, final runs, regime S (January train side, epoch chosen on validation)). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
import os
import runpy
import sys
import subprocess

# fail fast: a session without GPUs would silently train on CPU for hours
try:
    print(subprocess.check_output(["nvidia-smi", "-L"], text=True, timeout=30), flush=True)
except Exception as e:
    raise SystemExit(f"NO GPU in this session ({e!r}): stopping instead of training on CPU. "
                     "Check the kernel's accelerator setting (T4 x2) and the account's GPU access (phone verification).")

ARGS = ["--jobs", "A:0,B:0,C:0,A:1,B:1,C:1,A:2,B:2,C:2,A:3,B:3,C:3,A:4,B:4,C:4,A:5,B:5,C:5,A:6,B:6,C:6,A:7,B:7,C:7,A:8,B:8,C:8,A:9,B:9,C:9,B0:0,C0:0,B0:1,C0:1,B0:2,C0:2", "--", "--epochs", "10"]

for dp, dn, fn in os.walk("/kaggle/input"):
    if "launch_pooling_v2.py" in fn and "train_pooling_v2.py" in fn:
        break
    if dp.count(os.sep) > 6:
        dn[:] = []
else:
    raise SystemExit("launch_pooling_v2.py not found under /kaggle/input: is nebula-thesis-code attached?")
print("launcher:", dp, flush=True)
sys.argv = [os.path.join(dp, "launch_pooling_v2.py")] + ARGS
runpy.run_path(sys.argv[0], run_name="__main__")
