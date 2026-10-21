# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Generate every SVG master for the cargen 'Grown' concept (internal working name).
Deterministic: every random source uses a fixed seed. Run render.sh afterwards for PNGs.
Letters: Manrope (wordmark) and IBM Plex Mono (URL), SIL OFL 1.1, converted to outlines."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from brand import PAL as P, mix
from glyphs import text_path
from growth import filament_attractors, colonise, network_svg
import mark as M

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = ("<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original generative artwork "
       "(cargen brand concept 'Grown'). Letters are outlines of Manrope / IBM Plex Mono, SIL OFL 1.1. -->")

def svg(w, h, body, title, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{HDR}<defs>{defs}</defs>{body}</svg>\n')

def save(rel, s):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(s); print("wrote", rel)

# ------------------------------------------------------------------ mark
def tile(x, y, size, small=False):
    k = size / 256
    inner = M.small_glyph() if small else M.glyph("dark")
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f})">{M.tile()}{inner}</g>'

def glyph_at(x, y, size, scheme):
    k = size / 256
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f})">{M.glyph(scheme)}</g>'

def marks():
    pre = "mark/cargen-grown"
    save(f"{pre}-mark.svg", svg(256, 256, tile(0, 0, 256), "cargen mark"))
    save(f"{pre}-mark-small.svg", svg(256, 256, tile(0, 0, 256, small=True), "cargen mark, small sizes (16-48 px)"))
    save(f"{pre}-glyph.svg", svg(256, 256, glyph_at(0, 0, 256, "dark"), "cargen glyph, for dark backgrounds"))
    save(f"{pre}-glyph-light.svg", svg(256, 256, glyph_at(0, 0, 256, "light"), "cargen glyph, for light backgrounds"))
    save(f"{pre}-glyph-mono-dark.svg", svg(256, 256, glyph_at(0, 0, 256, "mono"), "cargen glyph, one colour (loam)"))
    save(f"{pre}-glyph-mono-light.svg", svg(256, 256, glyph_at(0, 0, 256, "mono_rev"), "cargen glyph, one colour (bone)"))

# ------------------------------------------------------------------ wordmark + lockups
WM = dict(font="manrope", wght=640, tracking=-14)
_, _, _, XH_UNIT = text_path("cargen", WM["font"], WM["wght"], 100)

def wordmark(x, baseline, xh, col):
    """Lowercase 'cargen' with the given x-height (px). Returns (svg, width)."""
    size = 100 * xh / XH_UNIT
    d, w, _, _ = text_path("cargen", WM["font"], WM["wght"], size, x=x, y=baseline, tracking=WM["tracking"])
    return f'<path d="{d}" fill="{col}"/>', w

# car geometry inside the 256 tile (for optical alignment)
CAR_TOP = M.B.bounds[1] + M.DY
CAR_GROUND = M.GROUND + M.DY

def lockup(x, y, h, col):
    """Horizontal lockup: tile height h. Wordmark baseline sits on the car's ground line,
    x-height = height of the car body, so letters and car share one ground."""
    base = y + CAR_GROUND / 256 * h
    xh = (CAR_GROUND - CAR_TOP) / 256 * h * 0.62
    wm, w = wordmark(x + h * 1.14, base, xh, col)
    return tile(x, y, h) + wm, h * 1.14 + w

def stacked(cx, y, h, col):
    """Stacked lockup: tile centred above the wordmark."""
    xh = h * 0.30
    _, w = wordmark(0, 0, xh, col)
    wm, _ = wordmark(cx - w / 2, y + h * 1.12 + xh * 1.0, xh, col)
    return tile(cx - h / 2, y, h) + wm, max(w, h), h * 1.12 + xh * 1.0 + xh * 0.45

def word_and_lockups():
    for name, col, bg in (("dark", P["bone"], P["loam"]), ("light", P["loam"], None)):
        xh = 64; _, w = wordmark(0, 0, xh, col)
        pad = 24
        g, _ = wordmark(pad, pad + 100, xh, col)   # ascender room above x-height
        H = 100 + xh * 0.55 + pad * 2 - 4
        bgr = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
        save(f"wordmark/cargen-wordmark-{name}.svg", svg(round(w + 2 * pad), round(H), bgr + g, f"cargen wordmark ({name})"))
        h = 160; pad = 40
        g, w = lockup(pad, pad, h, col)
        save(f"lockup/cargen-lockup-{name}.svg", svg(round(w + 2 * pad), h + 2 * pad, bgr + g, f"cargen lockup ({name})"))
        g, w, hh = stacked(0, pad, h, col)
        W = round(w + 2 * pad + 40)
        g, w, hh = stacked(W / 2, pad, h, col)
        save(f"lockup/cargen-lockup-stacked-{name}.svg", svg(W, round(hh + 2 * pad), bgr + g, f"cargen stacked lockup ({name})"))

# ------------------------------------------------------------------ growth networks
def grow(bounds, roots, n, nodes, seed, influence=60, spread=10):
    A, _ = filament_attractors(0, 0, n=n, n_nodes=nodes, seed=seed, bounds=bounds, spread=spread)
    return colonise(A, roots, step=5, kill=8, influence=influence, seed=seed)

def fade(uid, W, H, x0, x1, y=False):
    a = f'x1="{x0}" x2="{x1}" y1="0" y2="0"' if not y else f'x1="0" x2="0" y1="{x0}" y2="{x1}"'
    return (f'<linearGradient id="g{uid}" {a} gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="m{uid}"><rect width="{W}" height="{H}" fill="url(#g{uid})"/></mask>')

def fruit(Pt, r, kids, col, n, rng_seed, rad=3.0):
    """A few 'fruiting bodies': the heaviest junctions, drawn as small solid dots."""
    idx = np.where(kids >= 2)[0]
    idx = idx[np.argsort(-r[idx])]
    chosen = []
    for i in idx:
        if all(np.hypot(*(Pt[i] - Pt[j])) > 110 for j in chosen): chosen.append(i)
        if len(chosen) == n: break
    return "".join(f'<circle cx="{Pt[i][0]:.1f}" cy="{Pt[i][1]:.1f}" r="{rad}" fill="{col}"/>' for i in chosen)

BW, BH = 1280, 320
def banner_net():
    return grow((540, 10, 1290, 330),
                [(1290, 290), (1290, 90), (1150, 330), (930, 330), (720, 330)],
                n=3400, nodes=22, seed=5, influence=58, spread=8)

def banner(dark, net, slot=False):
    Pt, par, r, k = net
    bg = P["loam"] if dark else P["bone"]
    line = mix(P["moss"], P["loam"], 0.05) if dark else mix(P["lichen"], P["bone"], 0.25)
    tipc = mix(P["sage"], P["loam"], 0.35) if dark else mix(P["moss"], P["bone"], 0.55)
    fr = P["chanterelle"] if dark else P["rust"]
    net_svg = network_svg(Pt, par, r, k, line, w0=0.6, wmax=4.0) + network_svg(Pt, par, r, k, "none", tip_col=tipc, tip_every=4, tip_r=1.2)
    h = 168
    lk, lw = lockup(80, (BH - h) / 2, h, P["bone"] if dark else P["loam"])
    defs = fade("b", BW, BH, 560, 880)
    body = (f'<rect width="{BW}" height="{BH}" fill="{bg}"/>'
            f'<g mask="url(#mb)">{net_svg}{fruit(Pt, r, k, fr, 5, 1)}</g>' + lk)
    if slot:
        body += slot_box(80 + h * 1.14 + 4, (BH - h) / 2 + h * 0.86, 520, 30, P["chanterelle"] if dark else P["rust"])
    return svg(BW, BH, body, "cargen banner" + (" layout guide with empty tagline slot" if slot else ""), defs)

def slot_box(x, y, w, h, col):
    lab = "TAGLINE SLOT (EMPTY, TO BE DECIDED)"
    d, _, _, _ = text_path(lab, "plexmono", 500, 11, x=x + 10, y=y + h / 2 + 4)
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="3" fill="none" stroke="{col}" stroke-width="1.2" stroke-dasharray="5 4"/>'
            f'<path d="{d}" fill="{col}"/>')

# ------------------------------------------------------------------ social preview
SW, SH = 1280, 640
def social():
    k = 2.45                                 # hero car: 256 box -> 627 px
    cx = SW / 2; car_x = cx - 128 * k
    ground = 492
    car_y = ground - CAR_GROUND * k
    # hyphae grow under the ground line, rooted at the wheels' contact points
    wx = [car_x + w[0] * k for w in M.WHEELS]
    net = grow((-10, ground + 10, SW + 10, SH + 10),
               [(wx[0], ground + 2), (wx[1], ground + 2), (-5, 600), (SW + 5, 560)],
               n=3400, nodes=24, seed=9, influence=70, spread=9)
    Pt, par, r, kk = net
    line = mix(P["moss"], P["loam"], 0.1)
    ns = network_svg(Pt, par, r, kk, line, w0=0.6, wmax=4.0) + network_svg(Pt, par, r, kk, "none", tip_col=mix(P["sage"], P["loam"], 0.4), tip_every=4, tip_r=1.2)
    defs = (f'<radialGradient id="gs" cx="{cx}" cy="{ground}" r="640" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="ms"><rect width="{SW}" height="{SH}" fill="url(#gs)"/></mask>'
            f'<clipPath id="below"><rect x="0" y="{ground + 3}" width="{SW}" height="{SH}"/></clipPath>')
    hero = f'<g transform="translate({car_x:.1f} {car_y - M.DY * k:.1f}) scale({k})">{M.glyph("dark", scale=0.62, gap=1.9, rr=1.0, dy=M.DY)}</g>'
    groundline = f'<rect x="0" y="{ground:.1f}" width="{SW}" height="1.2" fill="url(#gl)"/>'
    defs += (f'<linearGradient id="gl" x1="0" x2="{SW}" y1="0" y2="0" gradientUnits="userSpaceOnUse">'
             f'<stop offset="0" stop-color="{P["sage"]}" stop-opacity="0"/><stop offset=".5" stop-color="{P["sage"]}" stop-opacity=".55"/>'
             f'<stop offset="1" stop-color="{P["sage"]}" stop-opacity="0"/></linearGradient>')
    xh = 46
    _, w = wordmark(0, 0, xh, P["bone"])
    wm, _ = wordmark(cx - w / 2, 136, xh, P["bone"])
    url = "github.com/galion-studio/cargen"
    _, uw, _, _ = text_path(url, "plexmono", 500, 16)
    ud, _, _, _ = text_path(url, "plexmono", 500, 16, x=cx - uw / 2, y=184)
    body = (f'<rect width="{SW}" height="{SH}" fill="{P["loam"]}"/>'
            f'<g clip-path="url(#below)"><g mask="url(#ms)">{ns}{fruit(Pt, r, kk, P["chanterelle"], 5, 2)}</g></g>'
            + groundline + hero + wm + f'<path d="{ud}" fill="{P["sage"]}"/>')
    save("social/cargen-social-preview-1280x640.svg", svg(SW, SH, body, "cargen social preview", defs))

if __name__ == "__main__":
    marks(); word_and_lockups()
    net = banner_net()
    save("banner/cargen-banner-dark-1280x320.svg", banner(True, net))
    save("banner/cargen-banner-light-1280x320.svg", banner(False, net))
    save("banner/templates/cargen-banner-dark-tagline-slot.svg", banner(True, net, slot=True))
    save("banner/templates/cargen-banner-light-tagline-slot.svg", banner(False, net, slot=True))
    social()
