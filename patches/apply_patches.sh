#!/usr/bin/env bash
# Apply every patches/*.patch to the pinned Nebula checkout (third_party/nebula). Idempotent:
# a patch that is already applied is skipped, a patch that no longer applies stops the script.
# Usage: bash patches/apply_patches.sh [path/to/nebula]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
NEB="${1:-$HERE/../third_party/nebula}"
for p in "$HERE"/*.patch; do
  if git -C "$NEB" apply --reverse --check "$p" 2>/dev/null; then
    echo "already applied: $(basename "$p")"
  else
    git -C "$NEB" apply --check "$p"
    git -C "$NEB" apply "$p"
    echo "applied:         $(basename "$p")"
  fi
done
