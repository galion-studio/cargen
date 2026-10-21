# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Wind & Shell typography sheet (typography/typography.svg/.png). All text outlined to paths."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glyphs import text_path
from mark import C
from build import corridor_paths, poly
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "typography"); os.makedirs(OUT, exist_ok=True)
W, H = 1280, 760
o = [f'<rect width="{W}" height="{H}" fill="{C["paper"]}"/>']

def t(s, x, y, size, font="plexsans", wght=400, fill=C["graphite"], tracking=0.0, anchor="start"):
    d, w = text_path(s, name=font, wght=wght, size=size, x=x, y=y, tracking=tracking, anchor=anchor)
    o.append(f'<path d="{d}" fill="{fill}"/>'); return w

def label(s, x, y):
    t(s, x, y, 13, font="plexmono", fill=C["grey"], tracking=0.06)

X = 72
label("WORDMARK  ·  IBM PLEX SANS 600  ·  TRACKING −3 %", X, 70)
t("cargen", X - 6, 196, 150, wght=600, tracking=-0.03)
label("HEADINGS  ·  IBM PLEX SANS 600", 700, 70)
t("Measured vs theory", 700, 122, 40, wght=600, tracking=-0.01)
t("Axial crush of thin-walled tubes", 700, 166, 26, wght=500)
# corridor rule
lo, hi, sim = corridor_paths(W, 262, 10, 6, X, W - X)
band = np.vstack([lo, hi[::-1]])
o.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in band) + f' Z" fill="{C["sand"]}"/>')
o += [poly(lo, stroke=C["wind"], stroke_width=1.1), poly(hi, stroke=C["wind"], stroke_width=1.1),
      poly(sim, stroke=C["orange_ink"], stroke_width=1.8, stroke_linecap="round")]
label("BODY AND UI  ·  IBM PLEX SANS 400 / 500", X, 340)
body = ["Axial crush of thin-walled steel tubes, measured",
        "against closed-form theory: 48 tests from four",
        "published sources, each with its error in percent."]
for i, line in enumerate(body):
    t(line, X, 380 + i * 30, 19, wght=400)
t("Aa Bb Cc Gg Rr  0123456789  ( ) [ ] → ± × ·", X, 492, 19, wght=500, fill=C["grey"])
label("DATA, UNITS, CAPTIONS  ·  IBM PLEX MONO 400 / 500", 700, 340)
mono = ["48 tests, 27 within ±10 %", "PARK-US2  F_mean  101.0 kN", "          theory  123.8 kN", "          error   +22.6 %"]
for i, line in enumerate(mono):
    t(line, 700, 380 + i * 30, 19, font="plexmono-r")
t("data/crush-theory-check.csv  ·  Park et al. 2022", 700, 502, 15, font="plexmono", fill=C["orange_ink"])
# dark strip
o.append(f'<rect x="0" y="560" width="{W}" height="200" fill="{C["graphite"]}"/>')
t("cargen", X - 4, 668, 72, wght=600, tracking=-0.03, fill=C["paper"])
t("Plex Sans 600 on Graphite, 14.6:1", X, 712, 15, font="plexmono", fill=C["mist"])
t("Both families: SIL Open Font License 1.1, free for any use.", 560, 640, 18, wght=500, fill=C["paper"])
t("github.com/IBM/plex  ·  embedded as outlines, no font files", 560, 672, 15, font="plexmono", fill=C["mist"])
t("needed  ·  fallback: system-ui, Menlo", 560, 698, 15, font="plexmono", fill=C["mist"])
p = os.path.join(OUT, "typography.svg")
open(p, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Wind and Shell typography">'
                   "<!-- SPDX-License-Identifier: MIT. Text outlined from IBM Plex Sans / Mono (SIL OFL 1.1). -->" + "".join(o) + "</svg>\n")
subprocess.run(["rsvg-convert", p, "-o", os.path.join(OUT, "typography.png")], check=True)
print(os.path.join(OUT, "typography.png"))
