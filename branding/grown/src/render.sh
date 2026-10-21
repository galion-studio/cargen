#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Render every SVG master of the Grown concept to PNG with resvg (deterministic).
set -euo pipefail
cd "$(dirname "$0")/.."
r() { resvg "$@" 2>/dev/null; }
for s in 512 256 128 64; do r -w $s mark/cargen-grown-mark.svg mark/cargen-grown-mark-$s.png; done
for s in 48 32 24 16; do r -w $s mark/cargen-grown-mark-small.svg mark/cargen-grown-mark-small-$s.png; done
for f in mark/cargen-grown-glyph*.svg; do r -w 512 "$f" "${f%.svg}-512.png"; done
for f in wordmark/*.svg lockup/*.svg; do r -z 2 "$f" "${f%.svg}@2x.png"; done
for f in banner/*.svg banner/templates/*.svg social/*.svg; do r "$f" "${f%.svg}.png"; done
for f in palette/*.svg typography/*.svg; do [ -f "$f" ] && r "$f" "${f%.svg}.png"; done
echo rendered
