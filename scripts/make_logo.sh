#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
# Regenerate logo SVGs and PNG exports (needs python3 and rsvg-convert).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/make_logo.py
cd assets/logo
for m in forge cargen; do
  rsvg-convert -w 512 -h 512 "$m-mark.svg" -o "$m-mark-512.png"
  for v in light dark; do rsvg-convert -w 1280 -h 320 "$m-banner-$v.svg" -o "$m-banner-$v-1280x320.png"; done
done
ls -la
