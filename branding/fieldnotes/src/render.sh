#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Rebuild every Field Notes master SVG and export all PNGs with resvg. Deterministic (fixed seeds).
# Run from anywhere:  branding/fieldnotes/src/render.sh   (uses the repo .venv if present)
set -e
cd "$(dirname "$0")"
PY="$(cd ../../.. && pwd)/.venv/bin/python"; [ -x "$PY" ] || PY=python3
export PYTHONDONTWRITEBYTECODE=1
$PY fn_mark.py && $PY fn_build.py && $PY fn_palette.py && $PY fn_type.py
cd ..
r() { resvg "$@" 2>/dev/null; }
for s in 512 256 128 64 48; do r -w $s mark/cargen-fieldnotes-mark.svg mark/cargen-fieldnotes-mark-$s.png; done
for t in paper mono mono-chalk; do r -w 512 mark/cargen-fieldnotes-mark-$t.svg mark/cargen-fieldnotes-mark-$t-512.png; done
for f in mark/cargen-fieldnotes-glyph*.svg; do r -w 432 "$f" "${f%.svg}@2x.png"; done
for t in "" -paper; do
  for s in 48 32 24; do r -w $s mark/cargen-fieldnotes-mark-small$t.svg mark/cargen-fieldnotes-mark-small$t-$s.png; done
  r -w 16 mark/cargen-fieldnotes-mark-16$t.svg mark/cargen-fieldnotes-mark-16$t.png
done
r -w 180 mark/cargen-fieldnotes-touch-icon.svg mark/cargen-fieldnotes-touch-icon-180.png
for f in wordmark/*.svg lockup/*.svg; do r -z 2 "$f" "${f%.svg}@2x.png"; done
for f in banner/*.svg banner/templates/*.svg social/*.svg templates/*.svg palette/*.svg typography/*.svg; do r "$f" "${f%.svg}.png"; done
$PY graph/render_p1a.py
echo rendered
