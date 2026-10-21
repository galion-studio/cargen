#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copy the generated input decks and case/reference JSON of each finished run from
# runs/<case>/ (not tracked) to configs/<case>/ (tracked). Usage: scripts/collect_configs.sh runs/*/
set -euo pipefail
cd "$(dirname "$0")/.."
for d in "$@"; do
  d=${d%/}; c=$(basename "$d")
  [ -f "$d/report.json" ] || { echo "skip $c (no report)"; continue; }
  mkdir -p "configs/$c"
  cp "$d"/TUBE_0000.rad "$d"/TUBE_0001.rad "$d"/case.json "$d"/reference.json "configs/$c/" 2>/dev/null || true
  echo "configs/$c"
done
