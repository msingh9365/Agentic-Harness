"""Kaggle entry point (round 5, G1: ATT+bal, MM+bal, C+bal, regime J, seeds 0-9, 4 epochs, scores after every epoch). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--trainer", "train_pooling_v4.py", "--jobs", "ATTbal:0:tag=_all:all=1:epochs=4,MMbal:0:tag=_all:all=1:epochs=4,Cbal:0:tag=_all:all=1:epochs=4,ATTbal:1:tag=_all:all=1:epochs=4,MMbal:1:tag=_all:all=1:epochs=4,Cbal:1:tag=_all:all=1:epochs=4,ATTbal:2:tag=_all:all=1:epochs=4,MMbal:2:tag=_all:all=1:epochs=4,Cbal:2:tag=_all:all=1:epochs=4,ATTbal:3:tag=_all:all=1:epochs=4,MMbal:3:tag=_all:all=1:epochs=4,Cbal:3:tag=_all:all=1:epochs=4,ATTbal:4:tag=_all:all=1:epochs=4,MMbal:4:tag=_all:all=1:epochs=4,Cbal:4:tag=_all:all=1:epochs=4,ATTbal:5:tag=_all:all=1:epochs=4,MMbal:5:tag=_all:all=1:epochs=4,Cbal:5:tag=_all:all=1:epochs=4,ATTbal:6:tag=_all:all=1:epochs=4,MMbal:6:tag=_all:all=1:epochs=4,Cbal:6:tag=_all:all=1:epochs=4,ATTbal:7:tag=_all:all=1:epochs=4,MMbal:7:tag=_all:all=1:epochs=4,Cbal:7:tag=_all:all=1:epochs=4,ATTbal:8:tag=_all:all=1:epochs=4,MMbal:8:tag=_all:all=1:epochs=4,Cbal:8:tag=_all:all=1:epochs=4,ATTbal:9:tag=_all:all=1:epochs=4,MMbal:9:tag=_all:all=1:epochs=4,Cbal:9:tag=_all:all=1:epochs=4", "--", "--epochs", "4", "--skip-best", "--epoch-fp32"]

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
