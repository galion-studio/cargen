# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Generate every SVG master for the cargen 'Grown, not built' concept.
Run: /workspace/cargen/.venv/bin/python src/gen.py   (then src/render.sh for PNGs)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import brand
from brand import PAL as P, body, wheels, poisson, lloyd, voronoi, rounded, to_d, mix
from glyphs import text_path
from growth import filament_attractors, colonise, network_svg

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "svg")
os.makedirs(OUT, exist_ok=True)
HDR = "<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original generative artwork (cargen 'Grown, not built'). Letterforms: Manrope / IBM Plex Sans (SIL OFL 1.1), converted to paths. -->"

def svg(w, h, body_, title, vb=None):
    vb = vb or f"0 0 {w} {h}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>\n{HDR}\n{body_}</svg>\n')

def save(name, s):
    open(os.path.join(OUT, name), "w").write(s); print("wrote", name)

# ---------------------------------------------------------------- mark
brand.BODY_D = ("M 24 166 L 24 149 C 24 139 31 133 42 131 L 76 125 C 96 106 117 98 142 98 "
                "C 165 98 183 106 199 120 L 219 124 C 228 126 232 133 232 142 L 232 166 Z")
brand.WHEELS = [(70, 166), (188, 166)]; brand.ARCH_R = 25
X0, X1 = 24, 232
B = body()
def r_of(x, y):
    t = (x - X0) / (X1 - X0)
    return 23 - 15 * t ** 1.6           # graded: coarse cells at the rear, fine at the crush zone
XY = lloyd(poisson(B, r_of, seed=23, tries=20000), B, r_of, 4)
CELLS = voronoi(XY, B)
MINY, MAXY = B.bounds[1], 166 + 18.5
DY = 128 - (MINY + MAXY) / 2

def mark_group(scheme="dark"):
    s = {"dark":  dict(a=P["moss"], b=P["lichen"], nose=P["foxfire"], ring=P["lichen"]),
         "light": dict(a=P["moss"], b=mix(P["moss"], P["lichen"], 0.55), nose=P["foxfire_ink"], ring=P["humus"]),
         "mono":  dict(a=P["loam"], b=P["loam"], nose=P["loam"], ring=P["loam"]),
         "mono_rev": dict(a=P["bone"], b=P["bone"], nose=P["bone"], ring=P["bone"])}[scheme]
    parts = []
    for (x, y), c in zip(XY, CELLS):
        t = (x - X0) / (X1 - X0)
        col = s["nose"] if t > 0.88 else mix(s["a"], s["b"], min(1, max(0, (t - 0.25) / 0.65)) ** 1.5)
        parts.append(f'<path d="{to_d(rounded(c, 2.6, 1.4))}" fill="{col}"/>')
    for w in wheels(18.5):
        parts.append(f'<path d="{to_d(w.difference(w.buffer(-7, 64)))}" fill="{s["ring"]}" fill-rule="evenodd"/>')
    return f'<g transform="translate(0 {DY:.2f})">{"".join(parts)}</g>'

def tile(fill=P["loam"]):
    return f'<rect x="8" y="8" width="240" height="240" rx="56" fill="{fill}"/>'

def mark_small_group():
    """Simplified mark for 16-48 px: one silhouette, 3-cell crush zone, solid hubs."""
    from shapely.geometry import box
    nose = B.intersection(box(203, 0, 256, 256))
    rear = B.difference(box(199, 0, 256, 256))
    parts = [f'<path d="{to_d(rear)}" fill="{P["lichen"]}"/>']
    for y0, y1 in ((90, 131), (135, 150), (154, 200)):
        c = nose.intersection(box(203, y0, 256, y1))
        if not c.is_empty: parts.append(f'<path d="{to_d(c)}" fill="{P["foxfire"]}"/>')
    for w in wheels(18.5):
        parts.append(f'<path d="{to_d(w.difference(w.buffer(-8, 64)))}" fill="{P["lichen"]}" fill-rule="evenodd"/>')
    return f'<g transform="translate(0 {DY:.2f})">{"".join(parts)}</g>'

save("mark.svg", svg(256, 256, tile() + mark_group("dark"), "cargen mark"))
save("mark-light.svg", svg(256, 256, mark_group("light"), "cargen mark, for light backgrounds"))
save("mark-mono.svg", svg(256, 256, mark_group("mono"), "cargen mark, one colour"))
save("mark-mono-reversed.svg", svg(256, 256, mark_group("mono_rev"), "cargen mark, one colour reversed"))
save("mark-small.svg", svg(256, 256, tile() + mark_small_group(), "cargen mark, small sizes"))

# ---------------------------------------------------------------- wordmark
WM_FONT, WM_W = "manrope", 640
def wordmark(x, y_center, xh, col):
    """Lowercase 'cargen'; x-height band centred on y_center; returns (svg, width)."""
    _, _, _, xh_unit = text_path("cargen", WM_FONT, WM_W, 100)
    size = 100 * xh / xh_unit
    base = y_center + xh / 2
    d, w, _, _ = text_path("cargen", WM_FONT, WM_W, size, x=x, y=base, tracking=-12)
    return f'<path d="{d}" fill="{col}"/>', w

g, w = wordmark(0, 60, 64, P["loam"])
save("wordmark.svg", svg(int(w + 8), 120, f'<g transform="translate(4 0)">{g}</g>', "cargen wordmark"))
g, w = wordmark(0, 60, 64, P["bone"])
save("wordmark-reversed.svg", svg(int(w + 8), 120, f'<g transform="translate(4 0)">{g}</g>', "cargen wordmark, reversed"))

def lockup(x, y, size, col, scheme="dark"):
    """Tile mark at (x, y) size px + wordmark; returns (svg, total width)."""
    s = size / 256
    g = f'<g transform="translate({x} {y}) scale({s:.4f})">{tile() + mark_group(scheme)}</g>'
    wx = x + size + size * 0.16
    wg, ww = wordmark(wx, y + size * 0.5, size * 0.36, col)
    return g + wg, wx + ww - x

g, w = lockup(16, 16, 160, P["loam"])
save("lockup.svg", svg(int(w + 40), 192, g, "cargen lockup"))
g, w = lockup(16, 16, 160, P["bone"])
save("lockup-reversed.svg", svg(int(w + 40), 192, f'<rect width="100%" height="100%" fill="{P["loam"]}"/>' + g, "cargen lockup, reversed"))

# ---------------------------------------------------------------- growth fields
def field(W, H, seed, bounds, roots, n=2600, nodes=16, influence=60):
    A, N = filament_attractors(W, H, n=n, n_nodes=nodes, seed=seed, bounds=bounds)
    return colonise(A, roots, step=5, kill=8, influence=influence, seed=seed), N

def glow_defs():
    return ('<defs><filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="5"/></filter>'
            '</defs>')

def hubs(Pt, r, kids, col, n=7, dark=True):
    """Brightest junctions = 'galaxies' of the web: a soft halo + a crisp core."""
    idx = np.argsort(-(kids >= 3) * r)[:n]
    out = []
    for i in idx:
        x, y = Pt[i]
        if dark: out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{col}" opacity="0.55" filter="url(#glow)"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{col}"/>')
    return "".join(out)

def fade_mask(mid, W, H, x_from, x_to, inverse=False):
    a, b = ("0", "1") if not inverse else ("1", "0")
    return (f'<defs><linearGradient id="fg{mid}" x1="{x_from}" x2="{x_to}" y1="0" y2="0" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="{a}"/><stop offset="1" stop-color="#fff" stop-opacity="{b}"/></linearGradient>'
            f'<mask id="m{mid}"><rect width="{W}" height="{H}" fill="url(#fg{mid})"/></mask></defs>')

# banner 1280x320
W, H = 1280, 320
(Pt, par, r, k), _ = field(W, H, 5, (430, -20, 1300, 340),
                         [(1290, 40), (1290, 280), (1100, 330), (820, 330), (1010, -10), (640, -10)])
def banner(dark):
    bg = P["loam"] if dark else P["bone"]
    line = P["moss"] if dark else mix(P["lichen"], P["bone"], 0.15)
    hubc = P["foxfire"] if dark else P["foxfire_ink"]
    net = network_svg(Pt, par, r, k, line, w0=0.6, op=0.95 if dark else 1)
    tips = network_svg(Pt, par, r, k, "none", tip_col=mix(P["foxfire"], P["loam"], 0.35) if dark else mix(P["foxfire_ink"], P["bone"], 0.45))
    lk, lw = lockup(72, 72, 176, P["bone"] if dark else P["loam"])
    body_ = (f'<rect width="{W}" height="{H}" fill="{bg}"/>' + glow_defs() + fade_mask("b", W, H, 560, 900) +
             f'<g mask="url(#mb)">{net}{tips}{hubs(Pt, r, k, hubc, 6, dark)}</g>' + lk)
    return body_
save("banner-dark.svg", svg(W, H, banner(True), "cargen banner"))
save("banner-light.svg", svg(W, H, banner(False), "cargen banner"))

# social preview 1280x640
W2, H2 = 1280, 640
(Ps, pars, rs, ks), _ = field(W2, H2, 9, (-20, -20, 1300, 660),
                              [(-10, 80), (-10, 560), (1290, 60), (1290, 600), (420, 650), (880, -10), (300, -10), (1000, 650)],
                              n=5200, nodes=30, influence=70)
def social():
    net = network_svg(Ps, pars, rs, ks, P["moss"], w0=0.6, op=0.9)
    tips = network_svg(Ps, pars, rs, ks, "none", tip_col=mix(P["foxfire"], P["loam"], 0.4))
    # radial calm zone behind the lockup
    calm = (f'<defs><radialGradient id="calm" cx="640" cy="300" r="420" gradientUnits="userSpaceOnUse" gradientTransform="translate(640 300) scale(1 0.55) translate(-640 -300)">'
            f'<stop offset="0" stop-color="{P["loam"]}" stop-opacity="1"/><stop offset="0.55" stop-color="{P["loam"]}" stop-opacity="0.92"/>'
            f'<stop offset="1" stop-color="{P["loam"]}" stop-opacity="0"/></radialGradient></defs>')
    size = 200
    _, ww = wordmark(0, 0, size * 0.36, P["bone"])
    total = size + size * 0.16 + ww
    x0 = (W2 - total) / 2
    lk, _ = lockup(x0, 300 - size / 2 - 20, size, P["bone"])
    dsize = 30
    d, dw, _, _ = text_path("open-source car generation", "plex", 420, dsize)
    d, dw, _, _ = text_path("open-source car generation", "plex", 420, dsize, x=(W2 - dw) / 2, y=440)
    d2, dw2, _, _ = text_path("github.com/galion-studio/cargen", "plexmono", 500, 18)
    d2, _, _, _ = text_path("github.com/galion-studio/cargen", "plexmono", 500, 18, x=(W2 - dw2) / 2, y=580)
    return (f'<rect width="{W2}" height="{H2}" fill="{P["loam"]}"/>' + glow_defs() + net + tips + hubs(Ps, rs, ks, P["foxfire"], 9) + calm +
            f'<rect width="{W2}" height="{H2}" fill="url(#calm)"/>' + lk +
            f'<path d="{d}" fill="{P["lichen"]}"/><path d="{d2}" fill="{mix(P["lichen"], P["loam"], 0.35)}"/>')
save("social-preview.svg", svg(W2, H2, social(), "cargen social preview"))

# banner template with an empty, clearly marked tagline slot (not exported as a final asset)
slot = (f'<rect x="349" y="236" width="560" height="34" rx="4" fill="none" stroke="{P["foxfire"]}" stroke-width="1.5" stroke-dasharray="6 5"/>')
lab, lw_, _, _ = text_path("TAGLINE SLOT: EMPTY, TO BE DECIDED", "plexmono", 500, 12)
lab, _, _, _ = text_path("TAGLINE SLOT: EMPTY, TO BE DECIDED", "plexmono", 500, 12, x=361, y=257)
save("template-banner-dark-tagline-slot.svg", svg(W, H, banner(True) + slot + f'<path d="{lab}" fill="{P["foxfire"]}"/>', "cargen banner template with empty tagline slot"))
