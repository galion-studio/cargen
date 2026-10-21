#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Rebuild every Wind & Shell asset (SVG masters + PNGs) and the graph re-render. Deterministic.
# Run from anywhere; uses the repo venv (.venv) and rsvg-convert.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../../.." && pwd)"
py="$repo/.venv/bin/python"
cd "$repo"
"$py" "$here/build.py"
"$py" "$here/palette.py"
"$py" "$here/typography.py"
"$py" "$repo/branding/windshell/graph/render_parity.py"
