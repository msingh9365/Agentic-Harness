#!/usr/bin/env bash
# Publish (or version) a folder as a PRIVATE Kaggle dataset. The token is read from the environment, never printed.
# Usage: bash baseline/kaggle/publish_dataset.sh <folder> <slug> "<title>" ["<version message>"]
set -euo pipefail
DIR="$1"; SLUG="$2"; TITLE="$3"; MSG="${4:-update}"
export KAGGLE_API_TOKEN="${KAGGLE_API_TOKEN:-$KAGGLE_ACCESS_TOKEN}"
OWNER="${KAGGLE_OWNER:-msingh9365}"
cat > "$DIR/dataset-metadata.json" <<JSON
{"title": "$TITLE", "id": "$OWNER/$SLUG", "licenses": [{"name": "other"}],
 "subtitle": "Derived from dmitrijstrizna/quo-vadis-malware-emulation for reproducing Nebula"}
JSON
if kaggle datasets status "$OWNER/$SLUG" >/dev/null 2>&1; then
  kaggle datasets version -p "$DIR" -m "$MSG" --dir-mode zip
else
  kaggle datasets create -p "$DIR" --dir-mode zip
fi
kaggle datasets status "$OWNER/$SLUG"
