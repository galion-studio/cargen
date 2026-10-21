# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio. Field Notes typography specimen (all IBM Plex, SIL OFL 1.1, outlined).
from fn_lib import *

def sheet():
    W, H = 1280, 800
    b = f'<rect width="{W}" height="{H}" fill="{P["paper"]}"/>'
    t, _ = T("Field Notes typography", "serif-semi", 30, 48, 64, P["graphite"]); b += t
    t, _ = T("IBM Plex superfamily, SIL Open Font License 1.1 (github.com/IBM/plex). Every master SVG uses outlines.", "mono", 13, 48, 90, P["sepia"]); b += t
    rows = [
        ("WORDMARK", "IBM Plex Serif SemiBold, tracking -1 %", "cargen", "serif-semi", 120, P["graphite"]),
        ("HEADINGS", "IBM Plex Serif SemiBold / Regular", "Axial crush of thin-walled steel tubes", "serif-semi", 34, P["graphite"]),
        ("TEXT, UI", "IBM Plex Sans 400 / 600", "P1a compares a crushed square steel tube with its measured curve.", "sans", 22, P["graphite"]),
        ("NUMBERS, CAPTIONS", "IBM Plex Mono 400 / 500", "Pm 101.0 kN   peak 337.1 kN   100 × 100 × 2.8 mm", "mono", 22, P["cyan"]),
        ("SPECIMEN NAMES", "IBM Plex Serif Italic", "Carpinus betulus", "serif-it", 24, P["sepia"]),
    ]
    y = 140
    for lab, spec, sample, key, size, col in rows:
        b += f'<path d="M48 {y} H1232" stroke="{P["graphite"]}" stroke-width="0.7" opacity="0.5"/>'
        t, _ = T(lab, "mono-med", 12, 48, y + 24, P["graphite"], tracking=0.06); b += t
        t, _ = T(spec, "mono", 12, 48, y + 44, P["sepia"]); b += t
        sy = y + 30 + size * 0.75 if size < 60 else y + 112
        t, _ = T(sample, key, size, 340, sy, col); b += t
        y += 170 if size >= 60 else 112
    # caption example
    t, _ = T("Fig. 2", "mono", 14, 340, y + 8, P["sepia"]); b += t
    t, _ = T("tube US-2, Park et al. 2022", "mono", 14, 400, y + 8, P["sepia"]); b += t
    t, _ = T("CAPTION", "mono-med", 12, 48, y + 8, P["graphite"], tracking=0.06); b += t
    return svg(W, H, b, "cargen Field Notes typography")

if __name__ == "__main__":
    write("typography/typography.svg", sheet())
