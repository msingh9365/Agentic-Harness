#!/usr/bin/env bash
# Rebuild, on a new machine, the folders this repository expects NEXT TO it:
#
#   ../nebula        Nebula source at the pinned commit. It already contains the released model and
#                    BPE tokenizer (nebula/objects/bpe_50000_torch.model, bpe_50000_sentencepiece.model,
#                    bpe_50000_vocab.json). ~335 MB, public GitHub.
#   ../hf-git        the raw Speakeasy reports, dtrizna/quovadis-speakeasy at the pinned revision.
#                    ~5.5 GB download, ~11 GB on disk with the Git LFS cache. Public Hugging Face.
#   ../nebula-venv   Python 3.11 environment (speakeasy-emulator does not build on 3.13).
#   ../hier_data     files generated from the two above (~1.8 GB): analyze_signal.py collect
#                    (~8 min on 4 cores) and a copy of results/hier/data. Too large for GitHub,
#                    so it is rebuilt here instead of downloaded.
#
# Nothing is executed from the dataset: the reports are JSON files that are only read.
# Re-running the script is safe: finished steps are skipped.
#
# Usage (from the repository root):   bash scripts/setup_local.sh [all|nebula|data|venv|hier]
# Needs: git, git-lfs, uv (or python3.11), ~20 GB free disk.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="${PARENT:-$(dirname "$REPO")}"            # override for testing: PARENT=/tmp/x bash scripts/setup_local.sh
NEBULA_URL=https://github.com/dtrizna/nebula
NEBULA_COMMIT=1343ae170ef32b01a75d2dd5fb906b5541f073df
DATA_URL=https://huggingface.co/datasets/dtrizna/quovadis-speakeasy
DATA_REV=fc2e98fac0b4d43a5557ccab70c877af6cce9f4d
STEP="${1:-all}"

say() { printf '\n== %s\n' "$*"; }

step_nebula() {
  say "Nebula source -> $PARENT/nebula @ $NEBULA_COMMIT"
  [ -d "$PARENT/nebula/.git" ] || git clone -q "$NEBULA_URL" "$PARENT/nebula"
  git -C "$PARENT/nebula" fetch -q origin
  git -C "$PARENT/nebula" checkout -q "$NEBULA_COMMIT"
  for f in bpe_50000_torch.model bpe_50000_sentencepiece.model bpe_50000_vocab.json; do
    test -s "$PARENT/nebula/nebula/objects/$f" || { echo "missing nebula/objects/$f"; exit 1; }
  done
  echo "ok: released model and BPE tokenizer present in $PARENT/nebula/nebula/objects/"
}

step_data() {
  say "Speakeasy reports -> $PARENT/hf-git @ $DATA_REV (~5.5 GB)"
  command -v git-lfs >/dev/null || { echo "git-lfs is required (https://git-lfs.com)"; exit 1; }
  [ -d "$PARENT/hf-git/.git" ] || GIT_LFS_SKIP_SMUDGE=1 git clone -q "$DATA_URL" "$PARENT/hf-git"
  git -C "$PARENT/hf-git" checkout -q "$DATA_REV"
  git -C "$PARENT/hf-git" lfs pull
  n=$(find "$PARENT/hf-git" -path '*windows_emulation_*' -name '*.json' | wc -l | tr -d ' ')
  echo "report files: $n (expected 92700)"
  [ "$n" = 92700 ] || { echo "unexpected number of report files"; exit 1; }
}

step_venv() {
  say "Python 3.11 environment -> $PARENT/nebula-venv"
  if [ ! -x "$PARENT/nebula-venv/bin/python" ]; then
    if command -v uv >/dev/null; then uv venv -q -p 3.11 "$PARENT/nebula-venv"; else python3.11 -m venv "$PARENT/nebula-venv"; fi
  fi
  PY="$PARENT/nebula-venv/bin/python"
  if command -v uv >/dev/null; then PIP="uv pip install -q --python $PY"; else PIP="$PY -m pip install -q"; fi
  $PIP sentencepiece pandas speakeasy-emulator nltk orjson tqdm datasets matplotlib lief "setuptools<70" tabulate \
       lightgbm scikit-learn rapidfuzz pyarrow scipy
  if [ "$(uname -s)" = Linux ]; then $PIP torch --index-url https://download.pytorch.org/whl/cpu; else $PIP torch; fi
  "$PY" -c "import torch, lightgbm, sklearn, sentencepiece; print('ok: torch', torch.__version__, 'lightgbm', lightgbm.__version__)"
}

step_hier() {
  say "Generated files -> $PARENT/hier_data"
  PY="$PARENT/nebula-venv/bin/python"
  mkdir -p "$PARENT/hier_data/speakeasy"
  cp "$REPO"/results/hier/data/meta.csv "$REPO"/results/hier/data/nebula_score_chunk0.npy "$PARENT/hier_data/speakeasy/"
  cd "$REPO"
  "$PY" measure_lengths.py --nebula "$PARENT/nebula" sanity
  if [ ! -s "$PARENT/hier_data/signal/reps.bin" ]; then
    # one pass over all reports with Nebula's own filter; it checks itself against the committed
    # results (API-name hashes, token counts, link counts) and stops on any difference
    "$PY" analyze_signal.py --nebula "$PARENT/nebula" collect --data-dir "$PARENT/hf-git"
    git -C "$REPO" diff --quiet -- results/signal/reports.csv && echo "ok: results/signal/reports.csv unchanged"
  fi
  ls -la "$PARENT/hier_data/signal"
}

case "$STEP" in
  nebula) step_nebula ;;
  data)   step_data ;;
  venv)   step_venv ;;
  hier)   step_hier ;;
  all)    step_nebula; step_data; step_venv; step_hier
          say "done. Optional: rebuild the go/no-go parquet scores with scripts/go_no_go/score_models.py and test*.py" ;;
  *) echo "unknown step: $STEP (all|nebula|data|venv|hier)"; exit 1 ;;
esac
