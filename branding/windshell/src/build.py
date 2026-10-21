# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Build every 'Wind & Shell' asset: SVG masters + PNG exports (rsvg-convert).
Run: /workspace/cargen/.venv/bin/python branding/windshell/src/build.py"""
import os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from mark import mark_svg_group, C, PHI
from glyphs import text_path, metrics
from fields import streamlines, poly, golden_spiral, p1a_curve, halfbody_lines

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SVG = os.path.join(OUT, "svg"); PNG = os.path.join(OUT, "png")
os.makedirs(SVG, exist_ok=True); os.makedirs(PNG, exist_ok=True)
HDR = "<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original artwork, 'Wind & Shell' concept. Letters are outlines of Manrope / IBM Plex Mono (SIL OFL 1.1). -->"

def svg(name, w, h, body, title):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
         f'aria-label="{title}"><title>{title}</title>\n{HDR}\n{body}\n</svg>\n')
    p = os.path.join(SVG, name + ".svg"); open(p, "w").write(s); return p

def png(svgp, name, w=None):
    p = os.path.join(PNG, name + ".png")
    cmd = ["rsvg-convert", svgp, "-o", p] + (["-w", str(w)] if w else [])
    subprocess.run(cmd, check=True); return p

def mark_at(x, y, size, uid, **kw):
    return f'<g transform="translate({x} {y}) scale({size / 256:.5f})">{mark_svg_group(uid=uid, **kw)}</g>'

WM = dict(name="manrope", wght=700, tracking=-0.02)

def wordmark(x, y_base, size, fill):
    d, w = text_path("cargen", size=size, x=x, y=y_base, **WM)
    return f'<path d="{d}" fill="{fill}"/>', w

def mono(text, x, y, size, fill, anchor="start", wght=500, tracking=0.02):
    d, w = text_path(text, name="plexmono", size=size, x=x, y=y, tracking=tracking, anchor=anchor)
    return f'<path d="{d}" fill="{fill}"/>', w

def sans(text, x, y, size, fill, anchor="start", wght=500, tracking=0.0):
    d, w = text_path(text, name="manrope", wght=wght, size=size, x=x, y=y, tracking=tracking, anchor=anchor)
    return f'<path d="{d}" fill="{fill}"/>', w

# ---------- themes ----------
LIGHT = dict(bg=C["pearl"], fg=C["slate"], sub="#4A5966", line=C["skyd"], line2=C["sand"], tile="slate", gap="slate")
DARK = dict(bg=C["slate"], fg=C["pearl"], sub="#A9BCCB", line=C["sky"], line2="#3A4D5C", tile="slate2", gap="slate2")

def flow_field(W, H, cx, cy, sx, sy, theme, levels=None, m=2.4, opacity=1.0, hl=()):
    levels = levels if levels is not None else np.round(np.arange(-4.0, 4.01, 0.28), 3)
    lines = streamlines(cx, cy, sx, sy, W, H, levels, m=m)
    g = []
    for lv, pts in lines:
        k = abs(lv)
        if k < 1e-6:
            continue  # the stagnation streamline wraps the body; skip it
        col = theme["line"] if any(abs(lv - h) < 1e-3 for h in hl) else theme["line2"]
        w = 1.6 if col == theme["line"] else 1.1
        g.append(poly(pts, stroke=col, stroke_width=w, stroke_linecap="round", opacity=opacity))
    return "\n".join(g)

def halfbody_field(W, H, nose_x, cy, half_w, th, step=0.16, span=2.2):
    lv = [1 + k * step for k in range(1, int(span / step) + 1)]
    lv = lv + [-v for v in lv]
    lines = halfbody_lines(nose_x, cy, half_w, W, H, lv)
    g = []
    for v, pts in lines:
        k = abs(v)
        if k < 1e-9:   # body surface = stagnation streamline: hairline highlight
            g.append(poly(pts, stroke=th["line"], stroke_width=1.6, stroke_linecap="round"))
        else:          # fade outward
            op = max(0.22, 1 - (k - 1) / span)
            g.append(poly(pts, stroke=th["line2"], stroke_width=1.1, opacity=f"{op:.2f}", stroke_linecap="round"))
    return "<g>" + "\n".join(g) + "</g>"

# ---------- 1. marks ----------
def build_marks():
    files = []
    body = mark_svg_group(uid="m")
    p = svg("cargen-mark", 256, 256, body, "cargen mark"); files += [p, png(p, "cargen-mark-512", 512), png(p, "cargen-mark-1024", 1024)]
    for s in (16, 32, 48, 64, 180):
        files.append(png(p, f"cargen-mark-{s}", s))
    # tile-less marks for placing on colour
    p = svg("cargen-mark-notile-on-light", 256, 256, f'<rect width="256" height="256" fill="{C["pearl"]}"/>' +
            mark_svg_group(uid="nl", bg=False, body="slate", accent="orange", gapc="pearl"), "cargen mark on light")
    files += [p, png(p, "cargen-mark-notile-on-light-512", 512)]
    # mono: gaps must be transparent -> rebuild with mask-based cut
    p = svg("cargen-mark-mono", 256, 256, mono_mark("#1B2833"), "cargen mark, one colour")
    files += [p, png(p, "cargen-mark-mono-512", 512)]
    p = svg("cargen-mark-mono-white", 256, 256, f'<rect width="256" height="256" fill="{C["slate"]}"/>' + mono_mark("#FFFFFF"), "cargen mark, one colour reversed")
    files += [p, png(p, "cargen-mark-mono-white-512", 512)]
    return files

def mono_mark(col):
    """Single-colour mark: gaps and wheel arches are real holes (mask), so it works on any background."""
    g = mark_svg_group(uid="mm", bg=False, body="white", accent="white", gapc="ink")
    g = g.replace(C["white"], "#fff").replace(C["ink"], "#000")
    return (f'<defs><mask id="mono" maskUnits="userSpaceOnUse" x="0" y="0" width="256" height="256">'
            f'<rect width="256" height="256" fill="#000"/>{g}</mask></defs>'
            f'<rect width="256" height="256" fill="{col}" mask="url(#mono)"/>')

# ---------- 2. wordmark + lockups ----------
def build_type():
    files = []
    for th, nm in ((LIGHT, "light"), (DARK, "dark")):
        d, w = wordmark(0, 0, 200, th["fg"])
        xh = metrics(**{"name": "manrope", "wght": 700})["xh"] * 200
        W, H = int(w + 80), 260
        body = f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>' + wordmark(40, 175, 200, th["fg"])[0]
        p = svg(f"cargen-wordmark-{nm}", W, H, body, "cargen wordmark"); files += [p, png(p, f"cargen-wordmark-{nm}", W * 2)]
        # horizontal lockup: tile height = cap-ish of wordmark; mark tile 240 -> spans x-height+ascender
        size = 160
        wd, ww = wordmark(0, 0, size, th["fg"])
        m = 200
        W2 = int(40 + m + 40 + ww + 50); H2 = 280
        base = 40 + m / 2 + metrics("manrope", 700)["xh"] * size / 2 + 6
        body = (f'<rect width="{W2}" height="{H2}" fill="{th["bg"]}"/>' + mark_at(40, 40, m, f"l{nm}", tile=th["tile"], gapc=th["gap"]) +
                wordmark(40 + m + 36, base, size, th["fg"])[0])
        p = svg(f"cargen-lockup-{nm}", W2, H2, body, "cargen logo"); files += [p, png(p, f"cargen-lockup-{nm}", W2 * 2)]
        # stacked lockup
        W3, H3 = 520, 520
        wd3, ww3 = wordmark(0, 0, 120, th["fg"])
        body = (f'<rect width="{W3}" height="{H3}" fill="{th["bg"]}"/>' + mark_at((W3 - 260) / 2, 50, 260, f"s{nm}", tile=th["tile"], gapc=th["gap"]) +
                wordmark((W3 - ww3) / 2, 430, 120, th["fg"])[0])
        p = svg(f"cargen-lockup-stacked-{nm}", W3, H3, body, "cargen logo, stacked"); files += [p, png(p, f"cargen-lockup-stacked-{nm}", W3 * 2)]
    return files

# ---------- 3. banners ----------
def banner(th, nm, slot=False):
    W, H = 1280, 320
    o = [f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>']
    o.append(halfbody_field(W, H, nose_x=900, cy=H / 2, half_w=118, th=th))
    # oval body (solid bg) to keep the lockup area quiet
    m = 176
    x0, y0 = 92, (H - m) / 2
    o.append(mark_at(x0, y0, m, f"b{nm}", tile=th["tile"], gapc=th["gap"]))
    size = 150
    base = y0 + m / 2 + metrics("manrope", 700)["xh"] * size / 2 - (14 if True else 0)
    wd, ww = wordmark(x0 + m + 34, base, size, th["fg"])
    o.append(wd)
    dd, _ = mono("open-source car generation", x0 + m + 40, base + 50, 21, th["sub"])
    o.append(dd)
    if slot:
        o.append(tag_slot(x0 + m + 40, base + 64, 520, 34, th))
    return svg(f"cargen-banner-{nm}" + ("-template" if slot else ""), W, H, "\n".join(o), "cargen banner")

def tag_slot(x, y, w, h, th):
    lab, _ = mono("TAGLINE SLOT (EMPTY, TO BE DECIDED)", x + 12, y + h / 2 + 5, 13, th["sub"])
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{C["orange"]}" '
            f'stroke-width="1.5" stroke-dasharray="6 5"/>' + lab)

def build_banners():
    files = []
    for th, nm in ((LIGHT, "light"), (DARK, "dark")):
        p = banner(th, nm); files += [p, png(p, f"cargen-banner-{nm}-1280x320"), png(p, f"cargen-banner-{nm}-2560x640", 2560)]
        p = banner(th, nm, slot=True); files += [p, png(p, f"cargen-banner-{nm}-template-1280x320")]
    return files

if __name__ == "__main__":
    what = sys.argv[1:] or ["marks", "type", "banners"]
    fs = []
    if "marks" in what: fs += build_marks()
    if "type" in what: fs += build_type()
    if "banners" in what: fs += build_banners()
    print("\n".join(fs))
