"""Kaggle entry point (round 5, G2: regime S, ATT+bal, MM+bal, C+bal, ATT, A, seeds 0-9, 2 epochs). Finds launch_pooling_v2.py in the attached code dataset and runs it."""
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

ARGS = ["--trainer", "train_pooling_v4.py", "--jobs", "ATTbal:0:tag=_S:epochs=2,MMbal:0:tag=_S:epochs=2,Cbal:0:tag=_S:epochs=2,ATT:0:tag=_S:epochs=2,A:0:tag=_S:epochs=2,ATTbal:1:tag=_S:epochs=2,MMbal:1:tag=_S:epochs=2,Cbal:1:tag=_S:epochs=2,ATT:1:tag=_S:epochs=2,A:1:tag=_S:epochs=2,ATTbal:2:tag=_S:epochs=2,MMbal:2:tag=_S:epochs=2,Cbal:2:tag=_S:epochs=2,ATT:2:tag=_S:epochs=2,A:2:tag=_S:epochs=2,ATTbal:3:tag=_S:epochs=2,MMbal:3:tag=_S:epochs=2,Cbal:3:tag=_S:epochs=2,ATT:3:tag=_S:epochs=2,A:3:tag=_S:epochs=2,ATTbal:4:tag=_S:epochs=2,MMbal:4:tag=_S:epochs=2,Cbal:4:tag=_S:epochs=2,ATT:4:tag=_S:epochs=2,A:4:tag=_S:epochs=2,ATTbal:5:tag=_S:epochs=2,MMbal:5:tag=_S:epochs=2,Cbal:5:tag=_S:epochs=2,ATT:5:tag=_S:epochs=2,A:5:tag=_S:epochs=2,ATTbal:6:tag=_S:epochs=2,MMbal:6:tag=_S:epochs=2,Cbal:6:tag=_S:epochs=2,ATT:6:tag=_S:epochs=2,A:6:tag=_S:epochs=2,ATTbal:7:tag=_S:epochs=2,MMbal:7:tag=_S:epochs=2,Cbal:7:tag=_S:epochs=2,ATT:7:tag=_S:epochs=2,A:7:tag=_S:epochs=2,ATTbal:8:tag=_S:epochs=2,MMbal:8:tag=_S:epochs=2,Cbal:8:tag=_S:epochs=2,ATT:8:tag=_S:epochs=2,A:8:tag=_S:epochs=2,ATTbal:9:tag=_S:epochs=2,MMbal:9:tag=_S:epochs=2,Cbal:9:tag=_S:epochs=2,ATT:9:tag=_S:epochs=2,A:9:tag=_S:epochs=2", "--", "--epochs", "2", "--skip-best"]

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
