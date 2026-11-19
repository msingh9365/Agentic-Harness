"""Kaggle entry point (v2, final runs, regime J (all of January, epoch count chosen on the split)). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--jobs", "A:0:tag=_all:all=1:epochs=1,A:1:tag=_all:all=1:epochs=1,A:2:tag=_all:all=1:epochs=1,A:3:tag=_all:all=1:epochs=1,A:4:tag=_all:all=1:epochs=1,A:5:tag=_all:all=1:epochs=1,A:6:tag=_all:all=1:epochs=1,A:7:tag=_all:all=1:epochs=1,A:8:tag=_all:all=1:epochs=1,A:9:tag=_all:all=1:epochs=1,C:0:tag=_all:all=1:epochs=10,C:1:tag=_all:all=1:epochs=10,C:2:tag=_all:all=1:epochs=10,C:3:tag=_all:all=1:epochs=10,C:4:tag=_all:all=1:epochs=10,C:5:tag=_all:all=1:epochs=10,C:6:tag=_all:all=1:epochs=10,C:7:tag=_all:all=1:epochs=10,C:8:tag=_all:all=1:epochs=10,C:9:tag=_all:all=1:epochs=10", "--", "--epochs", "10"]

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
