"""
Build colab/nebula_m1_whitebox.ipynb: a self-contained Google Colab notebook that runs the M1 white-box attack of NOTES 25 Stage J (corrected tokenizer) on a Colab GPU.   (OURS)

    python baseline/colab/make_notebook.py

The notebook carries our code (baseline/ and patches/) as a base64 tarball (the same payload as the Kaggle kernels), so it needs no access to the GitHub repository. It downloads the three private Kaggle datasets with the
owner's Kaggle token (read from the Colab secret KAGGLE_API_TOKEN; never printed), clones the authors' repository at the pinned commit, runs `baseline.gs_attack --mode wb` for m1 seeds 0-9 (the same command as the Kaggle
kernels `nebula-fix-j-wb-m1*`), checks the result, and uploads only the scores (wb_m1_seed*.npz) as the private Kaggle dataset msingh9365/gs-fix-wb-m1-colab.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "baseline", "kaggle"))
import build_kernel as BK                                              # payload(), PINNED

MD0 = """# M1 white-box attack on a Colab GPU (corrected tokenizer, NOTES 25 Stage J)

This notebook is **one more copy of the pending job** `nebula-fix-j-wb-m1`: the greedy white-box attack (200 candidates per step, prepend, 50 steps, 500 April malware reports) on the corrected-tokenizer **M1** model, seeds 0-9.
It saves **scores only** (no report text). Estimated time on one T4: 45-90 minutes.

**Before you start (once):**
1. `Runtime > Change runtime type > T4 GPU`.
2. Left bar, key icon (**Secrets**): add a secret named `KAGGLE_API_TOKEN` whose value is the Kaggle API token of the account **msingh9365**, and switch on **Notebook access**. The token is only read by the cells below; it is never printed or written to a file.
3. `Runtime > Run all`. If the session disconnects, reconnect and run all again: finished seeds are skipped.

At the end the scores are uploaded as the private Kaggle dataset `msingh9365/gs-fix-wb-m1-colab` (and offered as a zip download). Tell Claude Code when it is done."""

CELLS = [
("md", MD0),
("code", '''# 1. GPU check
import subprocess, torch
print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip())
assert torch.cuda.is_available(), "No GPU: Runtime > Change runtime type > T4 GPU, then run all again."
print("torch", torch.__version__, "| cuda", torch.version.cuda)'''),
("code", '''# 2. token from the Colab secret (never printed) and the Kaggle CLI
import os, subprocess
from google.colab import userdata
os.environ["KAGGLE_API_TOKEN"] = userdata.get("KAGGLE_API_TOKEN")
subprocess.run("pip install -q kaggle", shell=True, check=True)
who = subprocess.run("kaggle config view", shell=True, capture_output=True, text=True).stdout
print([l for l in who.splitlines() if "username" in l])           # must say msingh9365
assert "msingh9365" in who, "The secret must be the Kaggle token of the account msingh9365."'''),
("code", '''# 3. our code (embedded), the authors' repository at the pinned commit, the dependencies
import base64, io, subprocess, tarfile, time
PAYLOAD = "__PAYLOAD__"
PINNED = "__PINNED__"
CODE, NEB = "/tmp/kcode", "/tmp/nebula"
def sh(cmd, check=True):
    t = time.time()
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"$ {cmd[:140]}   [exit {r.returncode}, {time.time() - t:.0f}s]" + (f"\\n{(r.stdout + r.stderr).strip()[-1200:]}" if r.returncode else ""), flush=True)
    if check and r.returncode:
        raise SystemExit("setup step failed: " + cmd[:100])
os.makedirs(CODE, exist_ok=True)
tarfile.open(fileobj=io.BytesIO(base64.b64decode(PAYLOAD)), mode="r:gz").extractall(CODE)
sh("pip install -q lightning torchmetrics tensorboard sentencepiece orjson nltk scikit-learn matplotlib")
sh("pip install -q speakeasy-emulator lief lxml", check=False)      # only the preprocessing needs these; a failure here is not fatal
sh(f"rm -rf {NEB} && git clone -q https://github.com/dtrizna/nebula {NEB} && git -C {NEB} checkout -q {PINNED}")
sh(f"bash {CODE}/patches/apply_patches.sh {NEB}")
sh(f"pip install -q -e {NEB} --no-deps")
print("nebula commit:", subprocess.check_output(["git", "-C", NEB, "rev-parse", "HEAD"], text=True).strip())'''),
("code", '''# 4. the three private datasets (M1 weights and stored logits, the corrected-tokenizer call store, the group split); on Colab /kaggle is read-only, so they go to /content/input (the code reads NEBULA_INPUT)
INPUT = "/content/input"
for slug in ("gs-fix-models", "gs-fix-inputs", "nebula-groupsplit"):
    d = f"{INPUT}/{slug}"
    if os.path.exists(d) and os.listdir(d):
        print("already there:", slug)
        continue
    os.makedirs(d, exist_ok=True)
    sh(f"kaggle datasets download -d msingh9365/{slug} -p {d} --unzip")
for dp, dn, fn in os.walk(INPUT):
    if dp.count(os.sep) <= 4:
        print(dp, len(fn), "files")'''),
("code", '''# 5. THE JOB: white-box attack on M1, seeds 0-9 (the command of the Kaggle kernels nebula-fix-j-wb-m1*). Takes the longest; finished seeds are skipped after a reconnect.
OUT = "/content/out"
os.makedirs(OUT, exist_ok=True)
jobs = " ".join(f"m1:{s}" for s in range(10))
env = dict(os.environ, PYTHONPATH=CODE, NEBULA_ROOT=NEB, NEBULA_INPUT=INPUT, PYTHONUNBUFFERED="1", TQDM_DISABLE="1")
cmd = f"python -m baseline.gs_attack --mode wb --plan --jobs {jobs} --out {OUT}"
print("RUN:", cmd, flush=True)
rc = subprocess.call(cmd, shell=True, env=env, cwd=CODE)
assert rc == 0, f"the attack job failed (exit {rc}); read the output above"'''),
("code", '''# 6. checks on the result (scores only): 10 files, step 0 = stored April logits, thresholds = those of the stored logits, flagged share never increases
import sys, glob, numpy as np
sys.path.insert(0, CODE)
from baseline import padtest
y = np.load(glob.glob(f"{INPUT}/gs-fix-inputs/**/labels.npz", recursive=True)[0])["y_test"].astype(int)
bad = []
for s in range(10):
    z = np.load(f"{OUT}/wb_m1_seed{s}.npz")
    z0 = np.load(glob.glob(f"{INPUT}/gs-fix-models/**/m1/seed{s}_april.npy", recursive=True)[0]).astype(np.float64)
    best, sel = z["best"].astype(np.float64), z["sel"]
    d0, dt1, dt01 = float(np.abs(best[0] - z0[sel]).max()), abs(float(z["t1"]) - padtest.thresholds(z0, y, 0.01)), abs(float(z["t01"]) - padtest.thresholds(z0, y, 0.001))
    ok = best.shape == (51, 500) and d0 <= 1e-4 and dt1 <= 1e-4 and dt01 <= 1e-4
    for key in ("t1", "t01"):
        share = (best > float(z[key])).mean(1)
        ok = ok and bool((np.diff(share) <= 0).all())
    print(f"seed {s}: step-0 diff {d0:.1e}, threshold diffs {dt1:.1e} / {dt01:.1e}, flagged share {float((best[0] > float(z['t1'])).mean()):.3f} -> {float((best[-1] > float(z['t1'])).mean()):.3f}  {'OK' if ok else 'CHECK FAILED'}")
    if not ok:
        bad.append(s)
assert not bad, f"checks failed for seeds {bad}: do NOT use these files"
print("all 10 seeds pass the checks")'''),
("code", '''# 7. hand the scores back: private Kaggle dataset msingh9365/gs-fix-wb-m1-colab (scores only) + a zip you can download
import json, shutil
UP = "/content/upload"
shutil.rmtree(UP, ignore_errors=True)
os.makedirs(UP)
for s in range(10):
    shutil.copy(f"{OUT}/wb_m1_seed{s}.npz", UP)
json.dump({"title": "gs fix wb m1 colab", "id": "msingh9365/gs-fix-wb-m1-colab", "licenses": [{"name": "other"}]}, open(f"{UP}/dataset-metadata.json", "w"))
sh(f"kaggle datasets create -p {UP} --dir-mode zip")
shutil.make_archive("/content/wb_m1_scores", "zip", UP)
try:
    from google.colab import files
    files.download("/content/wb_m1_scores.zip")
except Exception as e:
    print("zip is at /content/wb_m1_scores.zip", e)
print("done: tell Claude Code that the dataset msingh9365/gs-fix-wb-m1-colab exists")'''),
]


def main():
    cells = []
    for kind, src in CELLS:
        src = src.replace("__PAYLOAD__", BK.payload()).replace("__PINNED__", BK.PINNED) if kind == "code" else src
        base = {"metadata": {}, "source": src.splitlines(True)}
        cells.append({"cell_type": "markdown", **base} if kind == "md" else {"cell_type": "code", "execution_count": None, "outputs": [], **base})
    nb = {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"gpuType": "T4", "provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
    os.makedirs(os.path.join(ROOT, "colab"), exist_ok=True)
    path = os.path.join(ROOT, "colab", "nebula_m1_whitebox.ipynb")
    json.dump(nb, open(path, "w"), indent=1)
    print("wrote", path, f"{os.path.getsize(path) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
