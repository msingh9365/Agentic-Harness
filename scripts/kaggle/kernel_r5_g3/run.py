"""Kaggle entry point (round 5, G3: ATT+bal over the whole report, up to 4,096 tokens, balanced padding of the full report, regime J, seeds 0-4, 2 epochs). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--trainer", "train_fulltrace_v5.py", "--jobs", "ATTbalW:0:tag=_all:all=1:epochs=2,ATTbalW:1:tag=_all:all=1:epochs=2,ATTbalW:2:tag=_all:all=1:epochs=2,ATTbalW:3:tag=_all:all=1:epochs=2,ATTbalW:4:tag=_all:all=1:epochs=2", "--", "--epochs", "2", "--skip-best", "--epoch-fp32"]

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
