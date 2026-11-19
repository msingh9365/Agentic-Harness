#!/usr/bin/env bash
# Wait for a Kaggle kernel to finish, then download only the SMALL files (run files and logits; not the weights).  Usage: kwait_light.sh <owner/slug> <outdir> [poll] [max-min]
set -uo pipefail
KERNEL="$1"; OUT="$2"; POLL="${3:-60}"; MAXMIN="${4:-720}"
start=$(date +%s)
while true; do
  s=$(kaggle kernels status "$KERNEL" 2>&1 | tr '\n' ' ')
  echo "$(date -u +%H:%M:%S) $s" | cut -c1-200
  case "$s" in *COMPLETE*) break ;; *ERROR*|*CANCEL*) echo "KERNEL ENDED WITHOUT SUCCESS"; break ;; esac
  [ $(( ($(date +%s) - start) / 60 )) -ge "$MAXMIN" ] && { echo "TIMEOUT waiting"; break; }
  sleep "$POLL"
done
mkdir -p "$OUT"
kaggle kernels output "$KERNEL" -p "$OUT" --file-pattern '(\.json$|logits\.npy$|\.log$)' 2>&1 | tail -2
