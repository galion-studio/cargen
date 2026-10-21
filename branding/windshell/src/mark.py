# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""cargen 'Wind & Shell' mark geometry (256-unit grid).

Body: a streamliner drop. The nose is a circle of radius R resting on a flat floor; the
roof rises in one cubic to its crest and falls to a sharp, raised tail with a diffuser
upsweep underneath, the shape air would carve (round front, long taper).
Nose: the orange crush cap, cut by septa (circle arcs behind the nose). Chamber depth
shrinks by 1/phi toward the nose, as in a nautilus shell; they read as crush folds.
Wheels: discs set in arch cut-outs in the floor."""
import numpy as np

PHI = (1 + 5 ** 0.5) / 2
C = dict(slate="#1B2833", slate2="#2A3A47", sky="#8EC3E6", skyd="#2F6E9E", sand="#E7D6B8",
         pearl="#F6F1E8", orange="#F26B1D", rust="#B84A0E", ink="#16202A", white="#FFFFFF")

FULL = dict(x0=26, x1=230, floor=170, R=34, hump=22, lift=22, tailh=8, k1=0.42, k2=0.30,
            cap=0.9, rs=2.6, step0=13.0, gw=5.0, n_septa=2, wheel_r=13, wheels=(84, 162))
# 16-48 px version: bigger body, thicker tail, one fold, wider gaps, bigger wheels
SMALL = dict(x0=10, x1=246, floor=172, R=44, hump=24, lift=20, tailh=20, k1=0.40, k2=0.30,
             cap=0.75, rs=2.6, step0=26.0, gw=16.0, n_septa=1, wheel_r=21, ag=11.0, wheels=(78, 172))

def _bez(p0, p1, p2, p3, n=200):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

def geom(x0, x1, floor, R, hump, lift, tailh, k1, k2, **_):
    cx, cy = x1 - R, floor - R
    xt, yt = x0, floor - lift - tailh
    L = cx - xt
    P = [np.array(p, float) for p in ((cx, cy - R), (cx - k1 * L, cy - R - hump), (xt + k2 * L, yt - 6), (xt, yt))]
    top_y = _bez(*P)[:, 1].min()
    fx = xt + 0.36 * L
    d = (f"M{cx:.2f} {cy-R:.2f} C{P[1][0]:.2f} {P[1][1]:.2f} {P[2][0]:.2f} {P[2][1]:.2f} {xt:.2f} {yt:.2f}"
         f" C{xt+2:.2f} {yt+tailh*0.9:.2f} {xt+0.12*L:.2f} {floor-lift*0.25:.2f} {fx:.2f} {floor:.2f}"
         f" L{cx:.2f} {floor:.2f} A{R} {R} 0 0 0 {cx:.2f} {cy-R:.2f} Z")
    return d, (cx, cy, R), top_y

def _c(k):
    return C.get(k, k)

def mark_svg_group(tile="slate", body="pearl", accent="orange", gapc=None, bg=True, uid="ws",
                   spec=None, tile_box=(8, 8, 240, 56), center=True):
    """SVG group on a 256 grid. gapc = colour of fold gaps / wheel arches (normally = tile)."""
    s = dict(FULL if spec is None else spec)
    gapc = gapc or tile
    d, (cx, cy, R), top_y = geom(**s)
    floor, gw = s["floor"], s["gw"]
    bottom = floor + 2 + s["wheel_r"]
    dy = 128 - (top_y + bottom) / 2 if center else 0
    o = []
    if bg:
        x, y, w, rx = tile_box
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{w}" rx="{rx}" fill="{_c(tile)}"/>')
    o.append(f'<g transform="translate(0 {dy:.2f})">')
    rr = s["rs"] * R
    sx = (cx - s["cap"] * R) - rr          # septum circle centre; its right edge = start of the cap
    o.append(f'<defs><clipPath id="{uid}-b"><path d="{d}"/></clipPath>'
             f'<mask id="{uid}-n" maskUnits="userSpaceOnUse" x="-40" y="-40" width="340" height="340">'
             f'<rect x="-40" y="-40" width="340" height="340" fill="#fff"/>'
             f'<circle cx="{sx:.2f}" cy="{cy:.2f}" r="{rr:.2f}" fill="#000"/></mask></defs>')
    o.append(f'<path d="{d}" fill="{_c(body)}"/>')
    o.append(f'<g clip-path="url(#{uid}-b)"><rect x="-40" y="-40" width="340" height="340" fill="{_c(accent)}" mask="url(#{uid}-n)"/>')
    r, step = rr, s["step0"]
    for _ in range(s["n_septa"]):
        r += step + gw / 2
        o.append(f'<circle cx="{sx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="none" stroke="{_c(gapc)}" stroke-width="{gw}"/>')
        r += gw / 2
        step /= PHI
    o.append('</g>')
    ag = s.get("ag", min(gw, 6.0))
    for wx in s["wheels"]:
        o.append(f'<circle cx="{wx}" cy="{floor+2}" r="{s["wheel_r"]+ag}" fill="{_c(gapc)}"/>')
        o.append(f'<circle cx="{wx}" cy="{floor+2}" r="{s["wheel_r"]}" fill="{_c(body)}"/>')
    o.append('</g>')
    return "\n".join(o)
