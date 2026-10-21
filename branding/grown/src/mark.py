# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""cargen 'Grown' mark: a car side profile filled with a graded Voronoi lattice.
Cells are coarse at the rear and fine at the front, like the graded density of
bone, wood or an engineered crush lattice; the finest cells (the crush zone)
carry the existing cargen orange. Seeded and deterministic."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
import brand
from brand import PAL as P, poisson, lloyd, voronoi, rounded, to_d, mix

# Side profile facing right (front = +x) in a 256 design box. Low, modern hatch.
BODY_D = ("M 22 160 L 22 141 C 22 132 27 127 37 125 L 70 119 C 90 100 112 91 138 91 "
          "C 160 91 177 99 193 113 L 216 118 C 227 120 234 127 234 138 L 234 160 Z")
WHEELS = [(70, 160), (186, 160)]
ARCH_R, WHEEL_R, HUB_R = 24.5, 18.5, 6.5
X0, X1 = 22, 234
SEED = 23
CRUSH_T = 0.86            # cells whose centre is beyond this fraction of length = crush zone

def body():
    b = brand.parse_path(BODY_D)
    b = b.difference(unary_union([Point(c).buffer(ARCH_R, 64) for c in WHEELS]))
    return b.buffer(-3, join_style=1).buffer(3, join_style=1)

B = body()
GROUND = WHEELS[0][1] + WHEEL_R
DY = 128 - (B.bounds[1] + GROUND) / 2        # centre the car vertically in the tile

def r_of(x, y):
    t = (x - X0) / (X1 - X0)
    return 24 - 16 * t ** 1.5               # graded: coarse rear -> fine crush zone

_cache = {}
def cells(seed=SEED, scale=1.0):
    """(centres, cells) for the lattice; scale < 1 gives more, smaller cells (hero art)."""
    k = (seed, scale)
    if k not in _cache:
        f = lambda x, y: r_of(x, y) * scale
        xy = lloyd(poisson(B, f, seed=seed, tries=int(20000 / scale ** 2)), B, f, 4)
        _cache[k] = (xy, voronoi(xy, B))
    return _cache[k]

SCHEMES = {
    # rear colour, front colour, crush colour, wheel colour, hub (cut-out shows background)
    "dark":     dict(a=P["moss"], b=P["lichen"], crush=P["chanterelle"], wheel=P["lichen"]),
    "light":    dict(a=P["moss"], b=mix(P["moss"], P["lichen"], 0.5), crush=P["chanterelle"], wheel=P["loam"]),
    "mono":     dict(a=P["loam"], b=P["loam"], crush=P["loam"], wheel=P["loam"]),
    "mono_rev": dict(a=P["bone"], b=P["bone"], crush=P["bone"], wheel=P["bone"]),
}

def wheel_paths(col, spokes=7, gap=2.6, hub=HUB_R, rot=0.0):
    """Wheel = one more lattice: a tyre ring cut into radial cells around a solid hub."""
    import math
    from shapely.geometry import LineString
    out = []
    for c in WHEELS:
        ring = Point(c).buffer(WHEEL_R, 128).difference(Point(c).buffer(hub + gap, 96))
        cuts = unary_union([LineString([c, (c[0] + 30 * math.cos(rot + 2 * math.pi * i / spokes),
                                            c[1] + 30 * math.sin(rot + 2 * math.pi * i / spokes))]).buffer(gap / 2, cap_style=2)
                            for i in range(spokes)])
        g = ring.difference(cuts).union(Point(c).buffer(hub, 64))
        g = g.buffer(-0.6, join_style=1).buffer(0.6, join_style=1)
        out.append(f'<path d="{to_d(g)}" fill="{col}" fill-rule="evenodd"/>')
    return "".join(out)

def cell_colour(s, t):
    if t > CRUSH_T: return s["crush"]
    return mix(s["a"], s["b"], min(1, max(0, (t - 0.2) / (CRUSH_T - 0.2))) ** 1.3)

def glyph(scheme="dark", seed=SEED, scale=1.0, gap=2.8, rr=1.4, dy=None):
    """The lattice car alone (no tile), centred in the 256 box."""
    s = SCHEMES[scheme]; xy, cs = cells(seed, scale)
    parts = []
    for (x, y), c in zip(xy, cs):
        g = rounded(c, gap * scale ** 0.5, rr)
        if g.is_empty: continue
        parts.append(f'<path d="{to_d(g)}" fill="{cell_colour(s, (x - X0) / (X1 - X0))}"/>')
    parts.append(wheel_paths(s["wheel"]))
    return f'<g transform="translate(0 {DY if dy is None else dy:.2f})">{"".join(parts)}</g>'

def tile(fill=P["loam"]):
    return f'<rect x="8" y="8" width="240" height="240" rx="54" fill="{fill}"/>'

def small_glyph():
    """16-48 px version: the lattice reduced to four large graded cells with wide
    gaps (they survive at 32 px), one orange crush cell, solid wheels."""
    gap = 11
    cuts = [  # hand-placed cell borders, graded: wide rear cell, narrower toward the nose
        [(110, 60), (100, 200)],
        [(150, 60), (160, 200)],
        [(199, 60), (194, 200)],
    ]
    pieces, prev = [], None
    from shapely.geometry import LineString
    from shapely.ops import split
    geom = B
    blades = unary_union([LineString(c) for c in cuts])
    parts_geom = sorted(split(geom, blades).geoms, key=lambda g: g.centroid.x)
    cols = [P["sage"], mix(P["sage"], P["lichen"], 0.5), P["lichen"], P["chanterelle"]]   # brighter than the full mark: 16 px needs contrast
    out = []
    for g, col in zip(parts_geom, cols):
        g2 = g.buffer(-gap / 2, join_style=2).buffer(-2, join_style=1).buffer(2, join_style=1)
        out.append(f'<path d="{to_d(g2)}" fill="{col}"/>')
    for c in WHEELS:
        w = Point(c).buffer(WHEEL_R + 1, 96)
        out.append(f'<path d="{to_d(w)}" fill="{P["lichen"]}"/>')
    return f'<g transform="translate(0 {DY:.2f})">{"".join(out)}</g>'
