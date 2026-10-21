# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Space-colonisation growth (the algorithm used to model leaf veins, roots and
fungal hyphae) with Murray's-law branch widths. Attractors are clustered along
filaments so the grown network also rhymes with the cosmic web."""
import numpy as np
from scipy.spatial import cKDTree

def filament_attractors(W, H, n=2200, n_nodes=14, seed=3, spread=10, bounds=None):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = bounds or (0, 0, W, H)
    nodes = np.c_[rng.uniform(x0, x1, n_nodes), rng.uniform(y0, y1, n_nodes)]
    # filaments: join each node to its 2-3 nearest neighbours (cosmic-web skeleton)
    tree = cKDTree(nodes); segs = set()
    for i, p in enumerate(nodes):
        _, idx = tree.query(p, k=min(4, len(nodes)))
        for j in idx[1:]: segs.add(tuple(sorted((i, int(j)))))
    segs = list(segs); pts = []
    for k in range(n):
        if rng.random() < 0.25:   # cluster halo
            c = nodes[rng.integers(len(nodes))]; pts.append(c + rng.normal(0, spread * 1.6, 2))
        else:                       # along a filament
            i, j = segs[rng.integers(len(segs))]; t = rng.random()
            pts.append(nodes[i] * (1 - t) + nodes[j] * t + rng.normal(0, spread, 2))
    pts = np.array(pts)
    m = (pts[:, 0] > x0) & (pts[:, 0] < x1) & (pts[:, 1] > y0) & (pts[:, 1] < y1)
    return pts[m], nodes

def colonise(attr, roots, step=5.0, kill=9.0, influence=48.0, iters=400, seed=1):
    rng = np.random.default_rng(seed)
    P = [np.array(r, float) for r in roots]; parent = [-1] * len(roots)
    alive = np.ones(len(attr), bool)
    for _ in range(iters):
        if not alive.any(): break
        tree = cKDTree(np.array(P))
        A = attr[alive]; d, idx = tree.query(A, distance_upper_bound=influence)
        ok = np.isfinite(d)
        if not ok.any(): break
        grow = {}
        for a, i in zip(A[ok], idx[ok]):
            v = a - P[i]; n = np.linalg.norm(v)
            if n > 0: grow.setdefault(i, []).append(v / n)
        added = 0
        for i, vs in grow.items():
            v = np.mean(vs, 0) + rng.normal(0, 0.12, 2); n = np.linalg.norm(v)
            if n < 1e-6: continue
            q = P[i] + step * v / n
            P.append(q); parent.append(i); added += 1
        if not added: break
        tree = cKDTree(np.array(P))
        near = tree.query_ball_point(attr, kill)
        alive &= np.array([len(nb) == 0 for nb in near])
    P = np.array(P); parent = np.array(parent)
    # Murray's law: r_parent^3 = sum r_child^3, leaves r = 1
    r3 = np.ones(len(P)); order = np.argsort(-np.arange(len(P)))
    for i in order:
        if parent[i] >= 0: r3[parent[i]] += r3[i]
    # leaves counted once; parents accumulate children
    r = np.cbrt(r3)
    kids = np.bincount(parent[parent >= 0], minlength=len(P))
    return P, parent, r, kids

def chains(P, parent, kids):
    """Split the tree into smooth polylines (one per branch) for nicer strokes."""
    children = [[] for _ in P]
    for i, p in enumerate(parent):
        if p >= 0: children[p].append(i)
    out = []; stack = [i for i, p in enumerate(parent) if p < 0]
    starts = [(s, None) for s in stack]
    while starts:
        s, prev = starts.pop()
        line = [prev, s] if prev is not None else [s]
        cur = s
        while len(children[cur]) == 1:
            cur = children[cur][0]; line.append(cur)
        out.append(line)
        for c in children[cur]: starts.append((c, cur))
    return out

def smooth_d(pts):
    """Catmull-Rom -> cubic Bezier path data."""
    if len(pts) < 2: return ""
    p = np.vstack([pts[0], pts, pts[-1]])
    d = [f"M{p[1][0]:.1f} {p[1][1]:.1f}"]
    for i in range(1, len(p) - 2):
        c1 = p[i] + (p[i+1] - p[i-1]) / 6; c2 = p[i+1] - (p[i+2] - p[i]) / 6
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p[i+1][0]:.1f} {p[i+1][1]:.1f}")
    return "".join(d)

def network_svg(P, parent, r, kids, line_col, tip_col=None, node_col=None, w0=0.55, wmax=4.2, op=1.0, wscale=None, tip_every=3, tip_r=1.3):
    out = []
    ch = chains(P, parent, kids)
    for c in sorted(ch, key=lambda c: r[c[0]]):
        w = min(wmax, w0 * r[c[-1]] ** 0.9)
        if wscale is not None: w *= wscale(P[c[0]])
        out.append(f'<path d="{smooth_d(P[c])}" stroke="{line_col}" stroke-width="{w:.2f}" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')
    if node_col is not None:
        junc = np.where(kids >= 3)[0]
        for i in junc:
            out.append(f'<circle cx="{P[i][0]:.1f}" cy="{P[i][1]:.1f}" r="{1.2 + 0.25*np.sqrt(r[i]):.2f}" fill="{node_col}"/>')
    if tip_col is not None:
        tips = np.where(kids == 0)[0]
        for i in tips[::tip_every]:
            out.append(f'<circle cx="{P[i][0]:.1f}" cy="{P[i][1]:.1f}" r="{tip_r}" fill="{tip_col}"/>')
    return "".join(out)
