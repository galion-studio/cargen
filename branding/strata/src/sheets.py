# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Palette sheet + WCAG contrast table, and typography specimen (text outlined)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from palette import P, C, contrast
from build import write, mono, sans, wordmark, mark_group, MARK, ROOT
from fontpath import text_path

PAIRS = [  # (fg, bg, use)
    ("limestone", "basalt", "text on dark"), ("limestone", "graphite", "text on tile"),
    ("ash", "basalt", "secondary text on dark"), ("fold", "basalt", "orange line / large text on dark"),
    ("fold", "graphite", "mark band on tile"), ("ice", "basalt", "test data on dark"),
    ("graphite", "limestone", "text on light"), ("stone", "limestone", "secondary text on light"),
    ("oxide", "limestone", "orange text / lines on light"), ("glacier", "limestone", "test data on light"),
    ("fold", "limestone", "orange on light: NOT for text or thin lines"), ("oxide", "basalt", "oxide on dark: avoid"),
    ("sediment", "limestone", "decorative strata lines only"), ("graphite", "chalk", "text on cards"),
]
def verdict(r):
    return "AA" if r >= 4.5 else ("AA large / graphics" if r >= 3 else "fail")

def palette():
    rows = ["| Foreground | Background | Ratio | WCAG 2.1 | Use |", "|---|---|---|---|---|"]
    for fg, bg, use in PAIRS:
        r = contrast(C[fg], C[bg])
        rows.append(f"| {P[fg][1]} `{C[fg]}` | {P[bg][1]} `{C[bg]}` | {r:.2f}:1 | {verdict(r)} | {use} |")
    md = "<!-- SPDX-License-Identifier: MIT -->\n# Strata palette: WCAG 2.1 contrast\nComputed by `src/sheets.py` (relative luminance, WCAG 2.1). AA = 4.5:1 for body text; 3:1 for large text (24 px, or 18.66 px bold) and for graphics.\n\n" + "\n".join(rows) + "\n"
    open(os.path.join(ROOT, "palette/contrast.md"), "w").write(md)
    W, H = 1280, 820
    b = f'<rect width="{W}" height="{H}" fill="{C["chalk"]}"/>'
    t, _ = sans("Strata palette", 64, 84, 34, C["graphite"], 600); b += t
    t, _ = mono("hex / role / contrast vs Basalt (dark) and Limestone (light)", 64, 114, 14, C["stone"]); b += t
    keys = list(P)
    for i, k in enumerate(keys):
        col, row = i % 4, i // 4
        x, y = 64 + col * 292, 150 + row * 220
        hexv, name, role = P[k]
        b += f'<rect x="{x}" y="{y}" width="268" height="112" rx="10" fill="{hexv}" stroke="#D9D2C5" stroke-width="1"/>'
        t, _ = sans(name, x, y + 138, 18, C["graphite"], 600); b += t
        t, _ = mono(hexv, x + 268, y + 138, 14, C["stone"], "end"); b += t
        rd, rl = contrast(hexv, C["basalt"]), contrast(hexv, C["limestone"])
        t, _ = mono(f"{rd:4.1f}:1 dark  {rl:4.1f}:1 light", x, y + 160, 12.5, C["stone"]); b += t
        words, line, ly = role.split(), "", y + 180
        for w in words:
            if len(line + " " + w) > 38:
                t, _ = sans(line.strip(), x, ly, 12.5, C["stone"]); b += t; line, ly = "", ly + 16
            line += " " + w
        t, _ = sans(line.strip(), x, ly, 12.5, C["stone"]); b += t
    return write("palette/palette.svg", W, H, b, "cargen Strata palette")

def typography():
    W, H = 1280, 840
    b = f'<rect width="{W}" height="{H}" fill="{C["chalk"]}"/>'
    t, _ = sans("Strata typography", 64, 84, 34, C["graphite"], 600); b += t
    t, _ = mono("all SIL Open Font License 1.1; every SVG master has text converted to outlines", 64, 114, 14, C["stone"]); b += t
    # wordmark specimen
    b += mark_group(MARK, C["graphite"], C["limestone"], C["fold"], 64, 160, 96, "ty")
    p, w, _ = wordmark(64 + 96 * 1.24, 160 + 44 * 1.5, 22.5 * 1.5, C["graphite"]); b += p
    t, _ = mono("WORDMARK  Archivo, wdth 125 (Expanded), wght 700, tracking -1.2 %, lowercase. Outlined; never retyped.", 64, 300, 13, C["stone"]); b += t
    d, _ = text_path("Archivo Expanded Bold  Aa Bb Cc 0123456789", "archivo", 40, 64, 360, wdth=125, wght=700); b += f'<path d="{d}" fill="{C["graphite"]}"/>'
    t, _ = mono("DISPLAY  headings only, 28 px and up. Omnibus-Type, github.com/Omnibus-Type/Archivo", 64, 390, 13, C["stone"]); b += t
    t, _ = sans("Axial crush test, A500 steel tube, 100 x 100 x 2.8 mm, quasi-static", 64, 460, 30, C["graphite"], 600); b += t
    t, _ = sans("IBM Plex Sans 400 for body text, 600 for headings and labels. Plex Sans Condensed is available for dense tables.", 64, 500, 18, C["graphite"], 400); b += t
    t, _ = mono("TEXT  IBM Plex Sans 400 / 600. IBM, github.com/IBM/plex", 64, 530, 13, C["stone"]); b += t
    for i, line in enumerate(["PARK-US2   Pm 101.0 kN   peak 337.1 kN   SEA 11.49 kJ/kg", "source  Park, Cho & Kim 2022, Table 4  |  solver  none (published test)", "closed-form theory 123.8 kN   error +22.61 %   status  theory check"]):
        t, _ = mono(line, 64, 600 + i * 32, 20, C["graphite"]); b += t
    t, _ = mono("DATA  IBM Plex Mono 400 / 500: every number, unit, provenance caption and code. IBM, github.com/IBM/plex", 64, 710, 13, C["stone"]); b += t
    b += f'<rect x="64" y="760" width="1152" height="1" fill="#D9D2C5"/>'
    t, _ = mono("Fallbacks: Archivo -> Inter Tight 700; Plex Sans -> Inter; Plex Mono -> JetBrains Mono (all OFL).", 64, 800, 13, C["stone"]); b += t
    return write("typography/typography.svg", W, H, b, "cargen Strata typography")

if __name__ == "__main__":
    print(palette()); print(typography())
