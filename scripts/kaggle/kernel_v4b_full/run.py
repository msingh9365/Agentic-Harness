"""Kaggle entry point (round 4, results/pooling_v4: Cbal, MMbal, ATTbal (balanced padding), regime J, 5 seeds, 2 epochs). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--trainer", "train_pooling_v4.py", "--jobs", "Cbal:0:tag=_all:all=1:epochs=2,MMbal:0:tag=_all:all=1:epochs=2,ATTbal:0:tag=_all:all=1:epochs=2,Cbal:1:tag=_all:all=1:epochs=2,MMbal:1:tag=_all:all=1:epochs=2,ATTbal:1:tag=_all:all=1:epochs=2,Cbal:2:tag=_all:all=1:epochs=2,MMbal:2:tag=_all:all=1:epochs=2,ATTbal:2:tag=_all:all=1:epochs=2,Cbal:3:tag=_all:all=1:epochs=2,MMbal:3:tag=_all:all=1:epochs=2,ATTbal:3:tag=_all:all=1:epochs=2,Cbal:4:tag=_all:all=1:epochs=2,MMbal:4:tag=_all:all=1:epochs=2,ATTbal:4:tag=_all:all=1:epochs=2", "--", "--epochs", "2"]

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
