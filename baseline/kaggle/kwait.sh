#!/usr/bin/env bash
# Wait for a Kaggle kernel to finish, then pull its output. The token is read from the environment
# (KAGGLE_ACCESS_TOKEN) and is never printed.
# Usage: bash baseline/kaggle/kwait.sh <owner/slug> <output-dir> [poll-seconds] [max-minutes]
set -uo pipefail
KERNEL="$1"; OUT="$2"; POLL="${3:-60}"; MAXMIN="${4:-720}"
export KAGGLE_API_TOKEN="${KAGGLE_API_TOKEN:-$KAGGLE_ACCESS_TOKEN}"
start=$(date +%s)
while true; do
  s=$(kaggle kernels status "$KERNEL" 2>&1 | tr '\n' ' ')
  echo "$(date -u +%H:%M:%S) $s" | cut -c1-200
  case "$s" in
    *COMPLETE*) break ;;
    *ERROR*|*CANCEL*) echo "KERNEL ENDED WITHOUT SUCCESS"; break ;;
  esac
  [ $(( ($(date +%s) - start) / 60 )) -ge "$MAXMIN" ] && { echo "TIMEOUT waiting"; break; }
  sleep "$POLL"
done
mkdir -p "$OUT"
kaggle kernels output "$KERNEL" -p "$OUT" 2>&1 | tail -3
