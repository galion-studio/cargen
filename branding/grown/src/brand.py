# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""cargen 'Grown, not built' concept: shared palette and generative geometry.
Everything is computed (seeded, reproducible); no stock art, no fonts embedded."""
import math, random, re
import numpy as np
from shapely.geometry import Polygon, Point, MultiPoint, box
from shapely.ops import unary_union
import shapely

PAL = {
    "loam":        "#141B17",  # forest-floor dark: primary dark background, text on light
    "humus":       "#1F2A23",  # raised dark surface (cards, tiles on loam)
    "moss":        "#4E6B45",  # primary brand green: coarse rear cells, graph series, lines on light
    "sage":        "#8FA37F",  # secondary text and network lines on dark
    "lichen":      "#B9C6A0",  # pale grey-green: fine cells, wheels, highlights on dark
    "bone":        "#F2EFE6",  # paper: light background, text on dark
    "chanterelle": "#F26B1D",  # crush-zone accent = the existing cargen orange (on dark only)
    "rust":        "#A8480C",  # chanterelle for text/lines on light
    "fern":        "#2F5D3A",  # deep green for links/emphasis on light
    "stone":       "#5E6A62",  # secondary text on light
}

def parse_path(d, steps=24):
    toks = re.findall(r"[MLCZ]|-?\d+\.?\d*", d)
    pts, i, cur, cmd = [], 0, (0, 0), None
    while i < len(toks):
        t = toks[i]
        if t in "MLCZ":
            cmd = t; i += 1
            if t == "Z": continue
        if cmd in "ML":
            cur = (float(toks[i]), float(toks[i+1])); pts.append(cur); i += 2
        elif cmd == "C":
            p1 = (float(toks[i]), float(toks[i+1])); p2 = (float(toks[i+2]), float(toks[i+3])); p3 = (float(toks[i+4]), float(toks[i+5])); i += 6
            p0 = cur
            for k in range(1, steps + 1):
                u = k / steps
                x = (1-u)**3*p0[0] + 3*(1-u)**2*u*p1[0] + 3*(1-u)*u**2*p2[0] + u**3*p3[0]
                y = (1-u)**3*p0[1] + 3*(1-u)**2*u*p1[1] + 3*(1-u)*u**2*p2[1] + u**3*p3[1]
                pts.append((x, y))
            cur = p3
    return Polygon(pts)

# Side profile, facing right (front = +x), in a 256 design box.
BODY_D = ("M 30 170 L 30 150 C 30 139 37 133 49 131 L 72 127 C 90 103 112 92 140 92 "
          "C 165 92 182 103 198 121 L 213 124 C 222 126 226 133 226 143 L 226 170 Z")
WHEELS = [(72, 170), (184, 170)]
WHEEL_R, ARCH_R = 19.5, 26

def body():
    b = parse_path(BODY_D)
    arches = unary_union([Point(c).buffer(ARCH_R, 64) for c in WHEELS])
    b = b.difference(arches)
    return b.buffer(-3, join_style=1).buffer(3, join_style=1)   # soften corners

def wheels(r=WHEEL_R):
    return [Point(c).buffer(r, 64) for c in WHEELS]

def poisson(region, r_of, seed=7, k=40, tries=6000):
    """Variable-radius dart throwing: cell size follows r_of(x, y)."""
    rng = random.Random(seed)
    minx, miny, maxx, maxy = region.bounds
    pts = []
    for _ in range(tries):
        x, y = rng.uniform(minx, maxx), rng.uniform(miny, maxy)
        if not region.contains(Point(x, y)): continue
        r = r_of(x, y)
        if all((x-px)**2 + (y-py)**2 >= (0.5*(r+pr))**2 for px, py, pr in pts):
            pts.append((x, y, r))
    return pts

def lloyd(pts, region, r_of, iters=3):
    """Weighted relaxation keeps the density gradient but evens the cells."""
    xy = np.array([(p[0], p[1]) for p in pts])
    for _ in range(iters):
        cells = voronoi(xy, region)
        new = []
        for (x, y), c in zip(xy, cells):
            if c.is_empty: new.append((x, y)); continue
            cx, cy = c.centroid.x, c.centroid.y
            new.append((0.5*x + 0.5*cx, 0.5*y + 0.5*cy))
        xy = np.array(new)
    return xy

def voronoi(xy, region):
    mp = MultiPoint([tuple(p) for p in xy])
    vor = shapely.voronoi_polygons(mp, extend_to=region.envelope.buffer(60))
    cells = {}
    for poly in vor.geoms:
        for i, p in enumerate(xy):
            if poly.contains(Point(p)):
                cells[i] = poly.intersection(region); break
    return [cells.get(i, Polygon()) for i in range(len(xy))]

def rounded(poly, gap, rr):
    p = poly.buffer(-gap / 2, join_style=2)
    if p.is_empty: return p
    return p.buffer(-rr, join_style=1).buffer(rr, join_style=1)

def to_d(geom, nd=2):
    out = []
    geoms = getattr(geom, "geoms", [geom])
    for g in geoms:
        if g.is_empty: continue
        for ring in [g.exterior] + list(g.interiors):
            c = list(ring.coords)
            out.append("M" + " L".join(f"{x:.{nd}f} {y:.{nd}f}" for x, y in c[:-1]) + "Z")
    return "".join(out)

def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def mix(a, b, t):
    A, B = hexrgb(a), hexrgb(b)
    return "#" + "".join(f"{round(255*(x + (y - x) * t)):02X}" for x, y in zip(A, B))

def lum(h):
    def f(c): return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in hexrgb(h)); return 0.2126*r + 0.7152*g + 0.0722*b

def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True); return (la + 0.05) / (lb + 0.05)
