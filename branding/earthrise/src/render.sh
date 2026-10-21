#!/usr/bin/env bash
# Render all Earthrise SVG masters to PNG with resvg.
set -e
cd "$(dirname "$0")/.."
r() { resvg "$@" 2>/dev/null; }
for s in 512 256 64 32; do r -w $s mark/cargen-earthrise-mark.svg mark/cargen-earthrise-mark-$s.png; done
for s in 48 32 16; do r -w $s mark/cargen-earthrise-mark-small.svg mark/cargen-earthrise-mark-small-$s.png; done
for f in mark/cargen-earthrise-glyph*.svg; do r -w 512 "$f" "${f%.svg}-512.png"; done
for f in wordmark/*.svg lockup/*.svg; do r -z 2 "$f" "${f%.svg}@2x.png"; done
r banner/cargen-banner-dark-1280x320.svg banner/cargen-banner-dark-1280x320.png
r banner/cargen-banner-light-1280x320.svg banner/cargen-banner-light-1280x320.png
r social/cargen-social-preview-1280x640.svg social/cargen-social-preview-1280x640.png
for f in palette/*.svg typography/*.svg; do [ -f "$f" ] && r -z 1 "$f" "${f%.svg}.png"; done
echo rendered
for f in banner/templates/*.svg; do r "$f" "${f%.svg}.png"; done
echo templates
