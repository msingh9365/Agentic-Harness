"""
Build a Kaggle kernel folder for a RoPE-test job (results/rope_test/kernels/<slug>/{run.py, kernel-metadata.json}).   (OURS; the bootstrap and the code payload of baseline/kaggle/build_kernel.py plus this package)

    python results/rope_test/build_kernel.py --slug rope-guard --args "--mode guard ..." --datasets a/b,c/d [--cpu]
The kernel runs `python -m rope_test.run_jobs <args>`; the owner is the account of the token in the environment (KAGGLE_OWNER, default manishsinghxdev). GPU kernels by default.
"""
import argparse
import base64
import io
import json
import os
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
from baseline.kaggle import build_kernel as BK  # noqa: E402

OWNER = os.environ.get("KAGGLE_OWNER", "manishsinghxdev")


def payload():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for base in ["baseline", "patches"]:
            for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
                dn[:] = [d for d in dn if d not in ("__pycache__", "jobs", "results") and not d.startswith(".")]
                for f in fn:
                    if f.endswith((".py", ".patch", ".sh", "ssl_split_hashes.json", "gap_split_hash.json", "b3_split_hashes.json", "b1_split_data.npz")):
                        full = os.path.join(dp, f)
                        tar.add(full, arcname=os.path.relpath(full, ROOT))
        for f in os.listdir(HERE):
            if f.endswith(".py") and f != "build_kernel.py":
                tar.add(os.path.join(HERE, f), arcname=f"rope_test/{f}")
    return base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--args", required=True)
    ap.add_argument("--datasets", default="")
    ap.add_argument("--cpu", action="store_true")
    ap.add_argument("--job", default="rope_test.run_jobs")
    a = ap.parse_args()
    out = os.path.join(HERE, "kernels", a.slug)
    os.makedirs(out, exist_ok=True)
    boot = BK.BOOTSTRAP.replace('[sys.executable, "-m", f"baseline.{JOB}"]', '[sys.executable, "-m", JOB]')
    assert boot != BK.BOOTSTRAP
    code = boot.replace("__PAYLOAD__", payload()).replace("__JOB__", a.job).replace("__ARGS__", a.args).replace("__PINNED__", BK.PINNED)
    open(os.path.join(out, "run.py"), "w").write(code)
    meta = {"id": f"{OWNER}/{a.slug}", "title": a.slug, "code_file": "run.py", "language": "python", "kernel_type": "script", "is_private": "true", "enable_gpu": "false" if a.cpu else "true",
            "enable_tpu": "false", "enable_internet": "true", "machine_shape": "", "dataset_sources": [d for d in a.datasets.split(",") if d], "competition_sources": [], "kernel_sources": [], "model_sources": []}
    json.dump(meta, open(os.path.join(out, "kernel-metadata.json"), "w"), indent=2)
    print(f"built {out} ({os.path.getsize(os.path.join(out, 'run.py')) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
