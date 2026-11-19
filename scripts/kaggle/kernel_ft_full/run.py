"""Kaggle entry point (v2, final runs, results/fulltrace: F (C over the whole report), regime J, 5 seeds, 10 epochs). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--trainer", "train_fulltrace.py", "--jobs", "F:0:tag=_all:all=1:epochs=10,F:1:tag=_all:all=1:epochs=10,F:2:tag=_all:all=1:epochs=10,F:3:tag=_all:all=1:epochs=10,F:4:tag=_all:all=1:epochs=10", "--", "--epochs", "10"]

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
