"""One Kaggle GPU session for the remaining experiments, run one after the other (each uses both T4s):
legacy-cleaning Whitespace detection (+ released-model check with all three released variants), type classification, ablations."""
import subprocess
import sys
import time

STEPS = [
    ["-m", "baseline.detect", "--plan", "legacy", "--out", "/kaggle/working/out"],
    ["-m", "baseline.classify", "--plan", "main", "--out", "/kaggle/working/out"],
    ["-m", "baseline.ablate", "--plan", "main", "--out", "/kaggle/working/out"],
]

for s in STEPS:
    t = time.time()
    rc = subprocess.call([sys.executable] + s)
    print(f"== {' '.join(s[:4])}: exit {rc} after {(time.time() - t) / 60:.1f} min", flush=True)
