# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Build every 'Wind & Shell' asset: SVG masters (text outlined) + PNG exports (rsvg-convert).
Run from the repo root:  .venv/bin/python branding/windshell/src/build.py [marks type banners social]
Deterministic: no randomness, every line comes from a closed-form flow or a log spiral."""
import os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mark import mark_svg_group, C, PHI, SMALL
from glyphs import text_path, metrics
from fields import poly, halfbody_lines, cylinder_lines, nautilus

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # branding/windshell
HDR = ("<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original artwork, 'Wind & Shell' concept "
       "for cargen. Letters are outlines of IBM Plex Sans / IBM Plex Mono (SIL OFL 1.1). -->")

def svg(rel, w, h, body, title):
    p = os.path.join(ROOT, rel + ".svg"); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                       f'role="img" aria-label="{title}"><title>{title}</title>\n{HDR}\n{body}\n</svg>\n')
    return p

def png(svgp, rel, w=None):
    p = os.path.join(ROOT, rel + ".png"); os.makedirs(os.path.dirname(p), exist_ok=True)
    subprocess.run(["rsvg-convert", svgp, "-o", p] + (["-w", str(w)] if w else []), check=True)
    return p

def mark_at(x, y, size, uid, **kw):
    return f'<g transform="translate({x:.2f} {y:.2f}) scale({size / 256:.5f})">{mark_svg_group(uid=uid, **kw)}</g>'

WM = dict(name="plexsans", wght=600, tracking=-0.03)
XH = metrics("plexsans", 600)["xh"]

def wordmark(x, base, size, fill):
    d, w = text_path("cargen", size=size, x=x, y=base, **WM)
    return f'<path d="{d}" fill="{fill}"/>', w

def txt(text, x, y, size, fill, font="plexsans", wght=450, anchor="start", tracking=0.0, op=None):
    d, w = text_path(text, name=font, wght=wght, size=size, x=x, y=y, tracking=tracking, anchor=anchor)
    o = f' opacity="{op}"' if op else ""
    return f'<path d="{d}" fill="{fill}"{o}/>', w

# ---------- themes ----------
LIGHT = dict(bg=C["paper"], fg=C["graphite"], sub=C["grey"], line=C["wind"], flow=C["wind"], flow_op=(0.34, 0.08),
             shell=C["sand"], tile="graphite", gap="graphite", name="light")
DARK = dict(bg=C["graphite"], fg=C["paper"], sub=C["mist"], line=C["sky"], flow=C["sky"], flow_op=(0.40, 0.09),
            shell=C["graphite2"], tile="graphite2", gap="graphite2", name="dark")

# ---------- 1. marks ----------
def glyph(body_col, accent_col, uid, spec=None):
    """Mark without tile; fold gaps and wheel arches are real holes, so it sits on any background."""
    kw = dict(bg=False, spec=spec)
    # body mask covers the cap too (no anti-alias seam); the cap colour is laid on top
    mb = mark_svg_group(uid=uid + "b", body="#ffffff", accent="#ffffff", gapc="#000000", **kw)
    mc = mark_svg_group(uid=uid + "c", body="#000000", accent="#ffffff", gapc="#000000", **kw)
    box = 'x="-40" y="-40" width="340" height="340"'
    return (f'<defs><mask id="{uid}-mb" maskUnits="userSpaceOnUse" {box}><rect {box} fill="#000"/>{mb}</mask>'
            f'<mask id="{uid}-mc" maskUnits="userSpaceOnUse" {box}><rect {box} fill="#000"/>{mc}</mask></defs>'
            f'<rect {box} fill="{body_col}" mask="url(#{uid}-mb)"/>' +
            (f'<rect {box} fill="{accent_col}" mask="url(#{uid}-mc)"/>' if accent_col != body_col else ""))

def build_marks():
    fs = []
    p = svg("mark/cargen-windshell-mark", 256, 256, mark_svg_group(uid="m"), "cargen mark")
    fs += [p] + [png(p, f"mark/cargen-windshell-mark-{s}", s) for s in (1024, 512, 256, 64, 32)]
    p = svg("mark/cargen-windshell-mark-small", 256, 256, mark_svg_group(uid="sm", spec=SMALL, tile_box=(0, 0, 256, 52)),
            "cargen mark, small sizes")
    fs += [p] + [png(p, f"mark/cargen-windshell-mark-small-{s}", s) for s in (48, 32, 16)]
    for nm, b, a, title in (("glyph-dark", C["paper"], C["orange"], "for dark backgrounds"),
                            ("glyph-light", C["graphite"], C["orange"], "for light backgrounds"),
                            ("glyph-mono-dark", C["graphite"], C["graphite"], "one colour, dark ink"),
                            ("glyph-mono-light", C["paper"], C["paper"], "one colour, light ink")):
        p = svg(f"mark/cargen-windshell-{nm}", 256, 256, glyph(b, a, nm), f"cargen glyph, {title}")
        fs += [p, png(p, f"mark/cargen-windshell-{nm}-512", 512)]
    # knockout: body cut out of the graphite tile (shows whatever is behind), folds in orange
    box = 'x="-40" y="-40" width="340" height="340"'
    mt = mark_svg_group(uid="kot", tile="#ffffff", body="#000000", accent="#000000", gapc="#ffffff")
    mc = mark_svg_group(uid="koc", bg=False, body="#000000", accent="#ffffff", gapc="#000000")
    ko = (f'<defs><mask id="ko-t" maskUnits="userSpaceOnUse" {box}><rect {box} fill="#000"/>{mt}</mask>'
          f'<mask id="ko-c" maskUnits="userSpaceOnUse" {box}><rect {box} fill="#000"/>{mc}</mask></defs>'
          f'<rect {box} fill="{C["graphite"]}" mask="url(#ko-t)"/><rect {box} fill="{C["orange"]}" mask="url(#ko-c)"/>')
    p = svg("mark/cargen-windshell-mark-knockout", 256, 256, ko, "cargen mark, knockout tile")
    fs += [p, png(p, "mark/cargen-windshell-mark-knockout-512", 512)]
    return fs

# ---------- 2. wordmark + lockups ----------
def build_type():
    fs = []
    for th in (LIGHT, DARK):
        nm = th["name"]
        size = 200
        _, ww = wordmark(0, 0, size, th["fg"])
        W, H = int(ww + 96), 280
        base = H / 2 + XH * size / 2
        body = f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>' + wordmark(48, base, size, th["fg"])[0]
        p = svg(f"wordmark/cargen-wordmark-{nm}", W, H, body, "cargen wordmark"); fs += [p, png(p, f"wordmark/cargen-wordmark-{nm}@2x", W * 2)]
        # horizontal lockup: x-height centred on the tile; gap tile->word = 0.18 x tile
        m, size = 200, 164
        _, ww = wordmark(0, 0, size, th["fg"])
        pad = 56
        W2, H2 = int(pad + m + 0.18 * m + ww + pad), m + 2 * pad
        base = pad + m / 2 + XH * size / 2
        body = (f'<rect width="{W2}" height="{H2}" fill="{th["bg"]}"/>' +
                mark_at(pad, pad, m, f"l{nm}", tile=th["tile"], gapc=th["gap"]) +
                wordmark(pad + 1.18 * m, base, size, th["fg"])[0])
        p = svg(f"lockup/cargen-lockup-{nm}", W2, H2, body, "cargen logo"); fs += [p, png(p, f"lockup/cargen-lockup-{nm}@2x", W2 * 2)]
        # stacked
        W3, H3, m3, s3 = 560, 560, 264, 128
        _, ww3 = wordmark(0, 0, s3, th["fg"])
        body = (f'<rect width="{W3}" height="{H3}" fill="{th["bg"]}"/>' +
                mark_at((W3 - m3) / 2, 64, m3, f"s{nm}", tile=th["tile"], gapc=th["gap"]) +
                wordmark((W3 - ww3) / 2, 64 + m3 + 40 + XH * s3 + 4, s3, th["fg"])[0])
        p = svg(f"lockup/cargen-lockup-stacked-{nm}", W3, H3, body, "cargen logo, stacked"); fs += [p, png(p, f"lockup/cargen-lockup-stacked-{nm}@2x", W3 * 2)]
    return fs

# ---------- 3. banners ----------
def halfbody_field(W, H, nose_x, cy, half_w, th, step=0.17, span=2.4, uid="hb"):
    """The lockup sits inside a Rankine half-body (uniform flow + one source): the stagnation
    streamline is the 'shell', the rest of the field is the wind around it."""
    lv = [1 + k * step for k in range(1, int(span / step) + 1)]
    lines = halfbody_lines(nose_x, cy, half_w, W, H, lv + [-v for v in lv])
    surf = [pts for v, pts in lines if v == 0.0]
    o = []
    # shell fill: top surface -> off-canvas left -> bottom surface
    top, bot = sorted(surf, key=lambda p: p[:, 1].mean())
    ring = np.vstack([top[::-1] if top[0, 0] > top[-1, 0] else top, [[-60, top[:, 1].min()], [-60, bot[:, 1].max()]]])
    ring = np.vstack([top[np.argsort(top[:, 0])], bot[np.argsort(-bot[:, 0])]])
    ring = np.vstack([[[-60, ring[0, 1]]], ring, [[-60, ring[-1, 1]]]])
    o.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in ring) + f' Z" fill="{th["shell"]}"/>')
    a0, a1 = th["flow_op"]
    for v, pts in lines:
        k = abs(v)
        if k == 0.0:
            o.append(poly(pts, stroke=th["line"], stroke_width=1.6, stroke_linecap="round"))
        else:
            op = a0 - (a0 - a1) * min(1, (k - 1) / span)
            o.append(poly(pts, stroke=th["flow"], stroke_width=1.1, opacity=f"{op:.2f}", stroke_linecap="round"))
    return "<g>" + "\n".join(o) + "</g>"

def banner(th, slot=False):
    W, H = 1280, 320
    nm = th["name"]
    o = [f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>']
    o.append(halfbody_field(W, H, nose_x=930, cy=H / 2, half_w=112, th=th))
    m, size = 168, 148
    x0, y0 = 96, (H - m) / 2
    lift = 34 if slot else 0
    bt = "graphite" if th is DARK else th["tile"]
    o.append(mark_at(x0, y0, m, f"b{nm}", tile=bt, gapc=bt))
    base = y0 + m / 2 + XH * size / 2 - lift
    o.append(wordmark(x0 + 1.18 * m, base, size, th["fg"])[0])
    # the field is labelled with its own equation (figure-caption style), nothing else
    o.append(caption("ψ = U∞ y + (m / 2π) θ   ·   Rankine half-body", W - 40, H - 26, 13, th))
    if slot:
        o.append(tag_slot(x0 + 1.18 * m + 6, base + 0.27 * size, 470, 34, th))
    return o

def caption(text, x, y, size, th, anchor="end"):
    d, w = txt(text, x, y, size, th["sub"], anchor=anchor, op="0.9")
    x0 = x - w if anchor == "end" else (x - w / 2 if anchor == "middle" else x)
    return (f'<rect x="{x0 - 10:.1f}" y="{y - size - 4:.1f}" width="{w + 20:.1f}" height="{size + 12:.1f}" rx="4" fill="{th["bg"]}"/>' + d)

def tag_slot(x, y, w, h, th):
    lab, _ = txt("TAGLINE SLOT  ·  EMPTY  ·  TO BE DECIDED BY MATE", x + 14, y + h / 2 + 4.5, 12.5, C["orange"] if th is DARK else C["orange_ink"],
                 font="plexmono", tracking=0.04)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{C["orange"]}" '
            f'stroke-width="1.5" stroke-dasharray="6 5"/>' + lab)

def build_banners():
    fs = []
    for th in (LIGHT, DARK):
        nm = th["name"]
        p = svg(f"banner/cargen-banner-{nm}-1280x320", 1280, 320, "\n".join(banner(th)), "cargen banner")
        fs += [p, png(p, f"banner/cargen-banner-{nm}-1280x320"), png(p, f"banner/cargen-banner-{nm}-2560x640", 2560)]
        p = svg(f"banner/templates/cargen-banner-{nm}-tagline-slot", 1280, 320, "\n".join(banner(th, slot=True)),
                "cargen banner layout guide with empty tagline slot")
        fs += [p, png(p, f"banner/templates/cargen-banner-{nm}-tagline-slot")]
    return fs

# ---------- 4. the corridor (graphic device) ----------
def corridor_paths(W, y0, amp, half, x_from=0, x_to=None, n=600):
    """Two thin curves = a measured test corridor (tolerance band, ISO/TS 18571 style);
    the orange line inside = a simulation result that stays within it. Smooth, deterministic."""
    x_to = W if x_to is None else x_to
    x = np.linspace(x_from, x_to, n)
    u = (x - x_from) / (x_to - x_from)
    c = y0 - amp * np.tanh(4 * (u - 0.45))                          # a streamline step, like flow over a body
    w = half * (1.0 + 0.35 * np.exp(-((u - 0.45) / 0.12) ** 2))      # corridor widens where the gradient is steep
    sim = c + w * 0.55 * np.sin(2 * np.pi * 2.6 * u + 0.6) * np.exp(-1.2 * u)
    return np.c_[x, c - w], np.c_[x, c + w], np.c_[x, sim]

def build_corridor():
    fs = []
    for th in (LIGHT, DARK):
        W, H = 1280, 160
        lo, hi, sim = corridor_paths(W, H / 2, 36, 13, 40, W - 40)
        band = np.vstack([lo, hi[::-1]])
        o = [f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>',
             '<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in band) + f' Z" fill="{th["shell"]}"/>',
             poly(lo, stroke=th["line"], stroke_width=1.3), poly(hi, stroke=th["line"], stroke_width=1.3),
             poly(sim, stroke=C["orange"] if th is DARK else C["orange_ink"], stroke_width=2.2, stroke_linecap="round")]
        p = svg(f"device/cargen-corridor-{th['name']}", W, H, "\n".join(o), "cargen corridor device")
        fs += [p, png(p, f"device/cargen-corridor-{th['name']}")]
    return fs

# ---------- 5. social preview ----------
def social():
    W, H = 1280, 640
    th = DARK
    o = [f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>']
    # wind: potential flow past a cylinder that holds the shell
    scx, scy, R = 948, 322, 196
    lv = [s * (k * 15.0) for k in range(1, 30) for s in (1, -1)]
    lines = cylinder_lines(scx, scy, R, W, H, lv)
    o.append('<defs><linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">'
             '<stop offset="0" stop-color="#fff" stop-opacity="0.15"/><stop offset="0.42" stop-color="#fff" stop-opacity="0.25"/>'
             '<stop offset="0.62" stop-color="#fff" stop-opacity="1"/></linearGradient>'
             f'<mask id="fm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>')
    g = []
    for v, pts in lines:
        k = abs(v) / 15.0
        op = max(0.10, 0.5 - 0.016 * k)
        g.append(poly(pts, stroke=C["sky"], stroke_width=1.15, opacity=f"{op:.2f}", stroke_linecap="round"))
    o.append('<g mask="url(#fm)">' + "\n".join(g) + "</g>")
    o.append(f'<circle cx="{scx}" cy="{scy}" r="{R}" fill="none" stroke="{C["sky"]}" stroke-width="1.6" opacity="0.9"/>')
    # shell: golden log spiral, septa every 22.5 deg, living chamber (= crush cap) in orange, opening facing the wind
    spiral, septa, living = nautilus(0, 0, 1.0, turns=3.0, rot=np.deg2rad(20), flip=-1, living_deg=78)
    lo, hi = spiral.min(0), spiral.max(0)
    k = 2 * (R - 18) / np.hypot(*(hi - lo))          # fit the shell's bounding box inside the cylinder
    outer = spiral[spiral.shape[0] * 2 // 3:]           # last whorl: optical centre = its area centroid
    x_, y_ = outer[:, 0], outer[:, 1]
    cr_ = x_ * np.roll(y_, -1) - np.roll(x_, -1) * y_
    A = cr_.sum() / 2
    cen = np.array([((x_ + np.roll(x_, -1)) * cr_).sum(), ((y_ + np.roll(y_, -1)) * cr_).sum()]) / (6 * A)
    cen = 0.5 * cen + 0.5 * (lo + hi) / 2
    off = np.array([scx, scy]) - k * cen
    spiral, living = spiral * k + off, living * k + off
    septa = [s_ * k + off for s_ in septa]
    o.append('<path d="M' + " L".join(f"{x:.1f} {y:.1f}" for x, y in living) + f' Z" fill="{C["orange"]}"/>')
    for s in septa:
        o.append(poly(s, stroke=C["sand"], stroke_width=1.2, opacity="0.75", stroke_linecap="round"))
    o.append(poly(spiral, stroke=C["paper"], stroke_width=2.0, stroke_linecap="round"))
    # dimension line: one whorl to the next, a technical-drawing label (no slogan)
    xa, xb = spiral[:, 0].min(), spiral[:, 0].max()
    yd = spiral[:, 1].max() + 30
    o.append(f'<g stroke="{C["mist"]}" stroke-width="1" fill="none"><path d="M{xa:.1f} {yd - 7:.1f} V{yd + 7:.1f} M{xb:.1f} {yd - 7:.1f} V{yd + 7:.1f} M{xa:.1f} {yd:.1f} H{xb:.1f}"/></g>')
    o.append(caption("whorl growth  ×3.0 per turn", (xa + xb) / 2, yd + 5, 12, th, anchor="middle"))
    # lockup
    m, size = 150, 132
    x0, y0 = 96, H / 2 - m / 2
    o.append(mark_at(x0, y0, m, "soc", tile="graphite2", gapc="graphite2"))
    base = y0 + m / 2 + XH * size / 2
    o.append(wordmark(x0 + 1.18 * m, base, size, C["paper"])[0])
    o.append(txt("github.com/galion-studio/cargen", x0 + 4, H - 58, 17, th["sub"], font="plexmono")[0])
    o.append(txt("MIT", W - 48, H - 58, 17, th["sub"], font="plexmono", anchor="end")[0])
    o.append(caption("ψ = U∞ y (1 − R² / r²)   ·   r = a·exp(bθ),  b = ln 3 / 2π", W - 48, 58, 13, th))
    p = svg("social/cargen-social-preview-1280x640", W, H, "\n".join(o), "cargen social preview")
    return [p, png(p, "social/cargen-social-preview-1280x640")]

if __name__ == "__main__":
    what = sys.argv[1:] or ["marks", "type", "banners", "social", "device"]
    fs = []
    if "marks" in what: fs += build_marks()
    if "type" in what: fs += build_type()
    if "banners" in what: fs += build_banners()
    if "social" in what: fs += social()
    if "device" in what: fs += build_corridor()
    print("\n".join(os.path.relpath(f, ROOT) for f in fs))
