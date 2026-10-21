#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Render every Strata SVG master to PNG with resvg (deterministic).
set -e
cd "$(dirname "$0")/.."
r() { resvg "$@"; }
for s in 1024 512 256 180 64; do r -w $s mark/cargen-strata-mark.svg mark/cargen-strata-mark-$s.png; done
for s in 48 32 16; do r -w $s mark/cargen-strata-mark-small.svg mark/cargen-strata-mark-small-$s.png; done
for f in mark/cargen-strata-mark-mono-*.svg mark/cargen-strata-glyph-*.svg; do r -w 512 "$f" "${f%.svg}-512.png"; done
for f in wordmark/*.svg lockup/*.svg; do r -z 2 "$f" "${f%.svg}@2x.png"; done
for f in banner/*.svg banner/templates/*.svg social/*.svg social/templates/*.svg palette/*.svg typography/*.svg; do [ -f "$f" ] && r "$f" "${f%.svg}.png"; done
echo rendered
