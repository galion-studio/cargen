# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Writes the Forge / cargen logo SVGs (hand-authored geometry, no fonts, no external
assets) to assets/logo/. PNG exports: scripts/make_logo.sh (rsvg-convert)."""
import os
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo")
os.makedirs(OUT, exist_ok=True)
INK, EMBER, STEEL = "#16202A", "#F26B1D", "#F5F7FA"

# Mark, 256x256: dark rounded badge. A car in side view (light) whose front end is
# an orange crumple zone: axial folds that tighten toward an orange impact wall.
BODY = ("M34 178 V160 C34 151 40 146 48 145 L84 140 C100 121 120 111 146 111 "
        "C162 111 173 118 182 130 L182 178 Z")
def folds():
    """Bellows-shaped crumple zone: zigzag top and bottom edges, pitch tightening
    toward the wall; returns (filled outline, fold lines)."""
    xs, x, w = [182.0], 182.0, 10.0
    while x + w <= 216:
        x += w; xs.append(x); w *= 0.82
    top = [(xv, 124 if i % 2 else 136) for i, xv in enumerate(xs)]
    bot = [(xv, 184 if i % 2 else 172) for i, xv in enumerate(xs)]
    outline = "M" + " L".join(f"{px:.1f} {py}" for px, py in top + bot[::-1]) + " Z"
    lines = " ".join(f"M{px:.1f} {py + 4} V{by - 4}" for (px, py), (_, by) in zip(top[1:-1], bot[1:-1]) if py == 136)
    return outline, lines, xs[-1]
FOLDS, FOLD_LINES, XEND = folds()

def mark(body_col, crush_col, badge=INK):
    return (f'<rect x="8" y="8" width="240" height="240" rx="56" fill="{badge}"/>'
            f'<g transform="translate(0 -26)">'
            f'<path d="{BODY}" fill="{body_col}"/>'
            f'<path d="{FOLDS}" fill="{crush_col}" stroke="{crush_col}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="{FOLD_LINES}" stroke="{badge}" stroke-width="2.5" stroke-linecap="round"/>'
            f'<path d="M{XEND + 9:.1f} 110 V198" stroke="{crush_col}" stroke-width="9" stroke-linecap="round"/>'
            f'<g fill="{badge}" stroke="{body_col}" stroke-width="7"><circle cx="76" cy="178" r="15"/><circle cx="150" cy="178" r="15"/></g>'
            f'</g>')

# Geometric letters, cap height 80, stroke 14 (paths drawn by hand).
L = {
 "F": ("M0 0 V80 M0 0 H46 M0 38 H38", 52),
 "O": ("M30 0 H34 C52 0 64 14 64 32 V48 C64 66 52 80 34 80 H30 C12 80 0 66 0 48 V32 C0 14 12 0 30 0 Z", 64),
 "R": ("M0 80 V0 H32 C46 0 54 9 54 20 C54 31 46 40 32 40 H0 M30 40 L54 80", 56),
 "G": ("M60 14 C54 5 45 0 34 0 H30 C12 0 0 14 0 32 V48 C0 66 12 80 30 80 H34 C50 80 62 70 62 54 V44 H38", 62),
 "E": ("M50 0 H0 V80 H50 M0 40 H42", 50),
 "C": ("M60 14 C54 5 45 0 34 0 H30 C12 0 0 14 0 32 V48 C0 66 12 80 30 80 H34 C45 80 54 75 60 66", 60),
 "A": ("M0 80 L30 0 L60 80 M12 50 H48", 60),
 "N": ("M0 80 V0 L54 80 V0", 54),
}
def word(text, x0, y0, scale, col):
    out, x = [], x0
    for ch in text:
        d, w = L[ch]
        out.append(f'<path transform="translate({x:.1f} {y0}) scale({scale})" d="{d}" fill="none" stroke="{col}" '
                   f'stroke-width="14" stroke-linecap="round" stroke-linejoin="round" vector-effect="none"/>')
        x += (w + 30) * scale
    return "".join(out), x

def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>\n<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original artwork. -->\n{body}</svg>\n')

def banner(name, mark_body, text_col, tagline_col, bg=None):
    W, H = 1280, 320
    body = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ""
    body += f'<g transform="translate(64 32) scale(1)">{mark_body}</g>'
    wtxt, xend = word(name, 372, 92, 1.45, text_col)
    body += wtxt
    # thin ember rule under the wordmark, echoing the crush wave
    body += f'<path d="M376 250 H{xend - 40:.0f}" stroke="{EMBER}" stroke-width="6" stroke-linecap="round"/>'
    return svg(W, H, body, f"{name.title()} logo banner")

files = {
 "forge-mark.svg": svg(256, 256, mark(STEEL, EMBER), "Forge logo"),
 "cargen-mark.svg": svg(256, 256, mark(EMBER, STEEL), "cargen logo"),
 "forge-banner-light.svg": banner("FORGE", mark(STEEL, EMBER), INK, INK),
 "forge-banner-dark.svg": banner("FORGE", mark(STEEL, EMBER), STEEL, STEEL),
 "cargen-banner-light.svg": banner("CARGEN", mark(EMBER, STEEL), INK, INK),
 "cargen-banner-dark.svg": banner("CARGEN", mark(EMBER, STEEL), STEEL, STEEL),
}
for n, s in files.items():
    open(os.path.join(OUT, n), "w").write(s)
    print(n)
