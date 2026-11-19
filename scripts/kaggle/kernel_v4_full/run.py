"""Kaggle entry point (round 4, results/pooling_v4: M, MM, ATT, Caug, ATTaug, regime J, 5 seeds, 2 epochs). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--trainer", "train_pooling_v4.py", "--jobs", "M:0:tag=_all:all=1:epochs=2,MM:0:tag=_all:all=1:epochs=2,ATT:0:tag=_all:all=1:epochs=2,Caug:0:tag=_all:all=1:epochs=2,ATTaug:0:tag=_all:all=1:epochs=2,M:1:tag=_all:all=1:epochs=2,MM:1:tag=_all:all=1:epochs=2,ATT:1:tag=_all:all=1:epochs=2,Caug:1:tag=_all:all=1:epochs=2,ATTaug:1:tag=_all:all=1:epochs=2,M:2:tag=_all:all=1:epochs=2,MM:2:tag=_all:all=1:epochs=2,ATT:2:tag=_all:all=1:epochs=2,Caug:2:tag=_all:all=1:epochs=2,ATTaug:2:tag=_all:all=1:epochs=2,M:3:tag=_all:all=1:epochs=2,MM:3:tag=_all:all=1:epochs=2,ATT:3:tag=_all:all=1:epochs=2,Caug:3:tag=_all:all=1:epochs=2,ATTaug:3:tag=_all:all=1:epochs=2,M:4:tag=_all:all=1:epochs=2,MM:4:tag=_all:all=1:epochs=2,ATT:4:tag=_all:all=1:epochs=2,Caug:4:tag=_all:all=1:epochs=2,ATTaug:4:tag=_all:all=1:epochs=2", "--", "--epochs", "2"]

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
