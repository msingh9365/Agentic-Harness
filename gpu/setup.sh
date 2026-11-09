#!/bin/bash
# One-time setup on the GPU server. Run from the repository root:
#     bash gpu/setup.sh
# Creates, next to this repository (in its parent folder):
#     ../nebula        Nebula source at the commit used in the study
#     ../nebula-venv   Python environment
#     ../hf-git        the Speakeasy dataset (about 11 GB on disk)
#     ../hier_data     tokenized data for the model (about 0.3 GB)
# Safe to run again: finished steps are skipped.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(dirname "$REPO")"
cd "$WORK"
NEBULA_COMMIT=1343ae170ef32b01a75d2dd5fb906b5541f073df
DATASET_REV=fc2e98fac0b4d43a5557ccab70c877af6cce9f4d

echo "== 1/5 Python"
# speakeasy-emulator (needed by Nebula's preprocessing) does not build on Python 3.13
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for c in python3.11 python3.10 python3.12; do command -v "$c" >/dev/null && PY="$c" && break; done
fi
if [ -z "$PY" ]; then
  echo "No python3.10/3.11/3.12 found. With conda:  conda create -y -n nebula python=3.11 && conda activate nebula"
  echo "then run:  PYTHON=python bash gpu/setup.sh"; exit 1
fi
echo "using $($PY --version) at $(command -v $PY)"
[ -d nebula-venv ] || "$PY" -m venv nebula-venv
source nebula-venv/bin/activate
pip install -q --upgrade pip
# default PyPI torch wheels for Linux include CUDA; if your server needs a specific CUDA build, see
# https://pytorch.org/get-started/locally/ and install torch first, then re-run this script
python -c "import torch" 2>/dev/null || pip install -q torch
pip install -q "setuptools<70" sentencepiece pandas speakeasy-emulator nltk orjson tqdm datasets \
               matplotlib lief tabulate scikit-learn
python -c "import torch; print('torch', torch.__version__, '| CUDA available:', torch.cuda.is_available(), \
'|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU visible on this node')"

echo "== 2/5 Nebula source"
if [ ! -d nebula ]; then git clone -q https://github.com/dtrizna/nebula; fi
git -C nebula checkout -q "$NEBULA_COMMIT"

echo "== 3/5 Speakeasy dataset (5.5 GB download)"
if [ ! -f hf-git/.download_complete ]; then
  if command -v git-lfs >/dev/null || git lfs version >/dev/null 2>&1; then
    [ -d hf-git ] || GIT_LFS_SKIP_SMUDGE=1 git clone -q https://huggingface.co/datasets/dtrizna/quovadis-speakeasy hf-git
    git -C hf-git checkout -q "$DATASET_REV"
    git -C hf-git config lfs.concurrenttransfers 32
    git -C hf-git lfs pull
  else
    echo "git-lfs not found; using huggingface_hub (slower, can take 1-2 hours)"
    python -c "from huggingface_hub import snapshot_download as s; s('dtrizna/quovadis-speakeasy', repo_type='dataset', \
revision='$DATASET_REV', local_dir='hf-git', max_workers=32)"
  fi
  n=$(find hf-git/windows_emulation_trainset hf-git/windows_emulation_testset -name '*.json' | wc -l)
  echo "dataset JSON files: $n (expected 92700)"
  [ "$n" -eq 92700 ] && touch hf-git/.download_complete || { echo "download incomplete, run again"; exit 1; }
fi

echo "== 4/5 tests"
cd "$REPO"
python -m hier_nebula.tests --nebula ../nebula 2>&1 | grep -E "^ok|PASSED|Error|Traceback"

echo "== 5/5 tokenize + cache Nebula chunk vectors"
if [ ! -f ../hier_data/speakeasy/meta.csv ]; then
  python -m hier_nebula.train prepare --dataset speakeasy --data-dir ../hf-git --out ../hier_data/speakeasy
fi
if [ ! -f ../hier_data/speakeasy/nebula_score_chunk0.npy ]; then
  python -m hier_nebula.train embed --data ../hier_data/speakeasy --batch-size 256
fi
echo "SETUP DONE. Next: bash gpu/run_experiments.sh   (or sbatch gpu/slurm_job.sh)"
