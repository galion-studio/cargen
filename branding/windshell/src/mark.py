# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""cargen 'Wind & Shell' mark geometry (256-unit grid).

Body: a streamliner drop. The nose is a circle of radius R resting on a flat floor; the
roof leaves it tangentially and rises in one cubic to its crest and falls to a sharp, raised tail with a diffuser
upsweep underneath, the shape air would carve (round front, long taper).
Nose: the orange crush cap, cut by septa (circle arcs behind the nose). Chamber depth
shrinks by 1/phi toward the nose, as in a nautilus shell; they read as crush folds.
Wheels: discs set in arch cut-outs in the floor."""
import numpy as np

PHI = (1 + 5 ** 0.5) / 2
# Palette (see palette/contrast.md). Graphite + Signal Orange are the existing cargen codes.
C = dict(graphite="#16202A", graphite2="#24323F", paper="#F4F1EA", sand="#E9DFCB",
         orange="#F26B1D", orange_ink="#B5470C", wind="#2F5F8F", sky="#7FA8D6",
         grey="#5A6470", mist="#9AA3AD", white="#FFFFFF")

FULL = dict(x0=26, x1=230, floor=170, R=34, hump=22, lift=22, tailh=8, k1=0.42, k2=0.30,
            cap=0.9, rs=2.6, step0=13.0, gw=5.0, n_septa=2, wheel_r=13, wheels=(84, 157))
# 16-48 px version: bigger body, thicker tail, one fold, wider gaps, bigger wheels
SMALL = dict(x0=10, x1=246, floor=172, R=44, hump=24, lift=20, tailh=20, k1=0.40, k2=0.30,
             cap=0.75, rs=2.6, step0=26.0, gw=16.0, n_septa=1, wheel_r=21, ag=11.0, wheels=(78, 172))

def _bez(p0, p1, p2, p3, n=200):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

def geom(x0, x1, floor, R, hump, lift, tailh, k1, k2, **_):
    """Roof leaves the nose circle tangentially at angle a (from the top, toward the front),
    so the joint has no kink; `hump` sets how far the first control point climbs."""
    cx, cy = x1 - R, floor - R
    xt, yt = x0, floor - lift - tailh
    L = cx - xt
    a = np.arctan2(hump, k1 * L)                       # tangent angle of the roof at the joint
    p0 = np.array([cx + R * np.sin(a), cy - R * np.cos(a)])
    d1 = np.hypot(k1 * L, hump)
    p1 = p0 + d1 * np.array([-np.cos(a), -np.sin(a)])
    P = [p0, p1, np.array([xt + k2 * L, yt - 6.0]), np.array([xt, yt], float)]
    top_y = min(_bez(*P)[:, 1].min(), cy - R)
    fx = xt + 0.36 * L
    d = (f"M{p0[0]:.2f} {p0[1]:.2f} C{p1[0]:.2f} {p1[1]:.2f} {P[2][0]:.2f} {P[2][1]:.2f} {xt:.2f} {yt:.2f}"
         f" C{xt+2:.2f} {yt+tailh*0.9:.2f} {xt+0.12*L:.2f} {floor-lift*0.25:.2f} {fx:.2f} {floor:.2f}"
         f" L{cx:.2f} {floor:.2f} A{R} {R} 0 0 0 {p0[0]:.2f} {p0[1]:.2f} Z")
    return d, (cx, cy, R), top_y

def _c(k):
    return C.get(k, k)

def mark_svg_group(tile="graphite", body="paper", accent="orange", gapc=None, bg=True, uid="ws",
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
