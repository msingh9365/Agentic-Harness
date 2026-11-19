#!/usr/bin/env python
"""
Stage the Kaggle dataset "nebula-thesis-code" (code only: no reports, no tokens, no credentials).

    python scripts/kaggle/make_code_dataset.py --stage <empty folder> [--nebula ../nebula]

Layout of the staged folder (it is what /kaggle/input/nebula-thesis-code/ will contain):
    nebula/         Nebula source at the pinned commit (the fork is a clean checkout: no local changes),
                    without .git, img/, emulation/ (sample reports), scripts/ and the unused whitespace/
                    neurlux vocabularies. nebula/COMMIT holds the commit hash.
    hier_nebula/    *.py of this repository (pooling_variants.py is what the trainer needs)
    scripts/        scripts/ of this repository (scripts/kaggle/train_pooling.py, launch_pooling.py, ...)
    dataset-metadata.json

It scans every staged file for secret-looking strings and stops if it finds one.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SECRET = re.compile(r"(api[_-]?key|secret|passwd|password|access[_-]?token|bearer |BEGIN [A-Z ]*PRIVATE KEY|"
                    r"ghp_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|\.kaggle|kaggle\.json|@gmail\.|@[a-z0-9-]+\.(com|edu|org))",
                    re.I)
NEBULA_SKIP = {".git", "img", "emulation", "scripts", "tests", "__pycache__", ".github"}
OBJ_SKIP = ("whitespace_", "neurlux_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    ap.add_argument("--nebula", default=os.path.join(REPO, "..", "nebula"))
    ap.add_argument("--owner", default="msingh9365")
    a = ap.parse_args()
    stage = os.path.abspath(a.stage)
    assert not os.path.exists(stage) or not os.listdir(stage), f"{stage} must be empty"
    os.makedirs(stage, exist_ok=True)
    neb = os.path.abspath(a.nebula)

    dirty = subprocess.check_output(["git", "-C", neb, "status", "--porcelain"], text=True).strip()
    commit = subprocess.check_output(["git", "-C", neb, "rev-parse", "HEAD"], text=True).strip()
    print(f"Nebula {commit}; local changes: {'YES' if dirty else 'none'}")
    if dirty:
        print(dirty)

    def ignore_neb(d, names):
        rel = os.path.relpath(d, neb)
        skip = [n for n in names if n in NEBULA_SKIP and rel in (".", "")]
        skip += [n for n in names if n == "__pycache__" or n.endswith(".pyc")]
        if rel == os.path.join("nebula", "objects"):
            skip += [n for n in names if n.startswith(OBJ_SKIP)]
        return skip

    shutil.copytree(neb, os.path.join(stage, "nebula"), ignore=ignore_neb)
    open(os.path.join(stage, "nebula", "COMMIT"), "w").write(commit + "\n")
    shutil.copytree(os.path.join(REPO, "hier_nebula"), os.path.join(stage, "hier_nebula"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(os.path.join(REPO, "scripts"), os.path.join(stage, "scripts"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "kernel_*"))

    hits = []
    for dp, _, fns in os.walk(stage):
        for f in fns:
            p = os.path.join(dp, f)
            if os.path.getsize(p) > 2_000_000 or f.endswith((".model", ".npy", ".pt")):
                continue
            if f == os.path.basename(__file__) or os.path.basename(dp) == "objects":
                continue                  # this scanner's own patterns; the BPE vocabulary (API names such as "password")
            try:
                txt = open(p, errors="ignore").read()
            except OSError:
                continue
            for m in SECRET.finditer(txt):
                line = txt.count("\n", 0, m.start()) + 1
                hits.append(f"{os.path.relpath(p, stage)}:{line}: {m.group(0)}")
    json.dump({"title": "nebula-thesis-code", "id": f"{a.owner}/nebula-thesis-code",
               "licenses": [{"name": "other"}],
               "description": "Code only: Nebula source at a pinned commit, hier_nebula/, scripts/. No data, no credentials."},
              open(os.path.join(stage, "dataset-metadata.json"), "w"), indent=1)
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fns in os.walk(stage) for f in fns)
    n = sum(len(fns) for _, _, fns in os.walk(stage))
    print(f"staged {n} files, {size / 2**20:.1f} MiB in {stage}")
    if hits:
        print("SECRET-LIKE STRINGS FOUND (review before uploading):")
        print("\n".join(hits[:60]))
        sys.exit(2)
    print("secret scan: no matches")


if __name__ == "__main__":
    main()
