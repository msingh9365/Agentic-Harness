"""Environment probe (CPU). Prints what the Kaggle container offers; installs and imports the authors' package.
Not part of the reproduction itself."""
import os, sys, platform, subprocess, shutil, time, json

def sh(cmd, timeout=900):
    t = time.time()
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    out = (r.stdout + r.stderr).strip()
    print(f"$ {cmd}   [exit {r.returncode}, {time.time()-t:.0f}s]\n{out[-1500:]}\n", flush=True)
    return r.returncode

print("python", sys.version.replace("\n", " "), "|", platform.platform())
print("cpus:", os.cpu_count(), "| RAM GB:", round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2**30, 1))
du = shutil.disk_usage("/kaggle/working"); print("disk /kaggle/working free GB:", round(du.free / 2**30, 1))
sh("pip list 2>/dev/null | grep -i -E '^(torch|numpy|pandas|scikit-learn|sentencepiece|lightning|pytorch-lightning|torchmetrics|lief|speakeasy|orjson|nltk|tensorboard|matplotlib|scipy) '")
sh("nvidia-smi -L || echo 'no GPU in this probe (expected)'")

# --- how the dataset is mounted
root = "/kaggle/input"
print("top of /kaggle/input:", os.listdir(root))
ds = None
for dp, dn, fn in os.walk(root):
    if "windows_emulation_trainset" in dn:
        ds = dp; break
    if dp[len(root):].count(os.sep) > 5:
        dn[:] = []
print("dataset dir:", ds)
assert ds, "windows_emulation_trainset not found under /kaggle/input"
for dp, dn, fn in os.walk(ds):
    depth = dp[len(ds):].count(os.sep)
    if depth <= 2:
        js = sum(1 for f in fn if f.endswith(".json"))
        print(f"{'  ' * depth}{os.path.basename(dp) or ds}: {len(dn)} dirs, {js} json files here")
n = sum(1 for _, _, fn in os.walk(ds) for f in fn if f.endswith(".json"))
print("total .json files under the dataset:", n)

# --- install what the authors' package needs, then import it
for pkg in ["lightning", "torchmetrics", "tensorboard", "sentencepiece", "orjson", "nltk", "speakeasy-emulator", "lief"]:
    sh(f"pip install -q {pkg} 2>&1 | tail -3")
sh("rm -rf /tmp/nebula && git clone -q https://github.com/dtrizna/nebula /tmp/nebula && git -C /tmp/nebula checkout -q "
   "1343ae170ef32b01a75d2dd5fb906b5541f073df && git -C /tmp/nebula rev-parse HEAD")
sh("pip install -q -e /tmp/nebula --no-deps 2>&1 | tail -3")
sys.path.insert(0, "/tmp/nebula")
for m in ["nebula", "nebula.preprocessing", "nebula.pretraining", "nebula.evaluation", "nebula.lit_utils"]:
    try:
        __import__(m); print("import OK  ", m)
    except Exception as e:
        print("import FAIL", m, "->", type(e).__name__, str(e)[:200])
