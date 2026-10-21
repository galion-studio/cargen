# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Generative fields, all closed-form and deterministic, drawn as SVG polylines:
Rankine oval and half-body streamlines, flow past a cylinder, and a nautilus log spiral."""
import numpy as np, contourpy

PHI = (1 + 5 ** 0.5) / 2

def rankine_psi(X, Y, U=1.0, m=1.0, a=1.0):
    """Stream function: uniform flow + source at -a, sink at +a (closed oval body)."""
    return U * Y + m / (2 * np.pi) * (np.arctan2(Y, X + a) - np.arctan2(Y, X - a))

def streamlines(cx, cy, sx, sy, W, H, levels, m=2.2, a=1.0, n=700):
    """Return list of polylines (canvas coords) of psi levels, body centred at (cx,cy),
    1 flow unit = sx px horizontally, sy px vertically."""
    xs = np.linspace(-cx / sx, (W - cx) / sx, n)
    ys = np.linspace(-cy / sy, (H - cy) / sy, int(n * H / W) + 2)
    X, Y = np.meshgrid(xs, ys)
    Z = rankine_psi(X, Y, m=m, a=a)
    gen = contourpy.contour_generator(xs, ys, Z)
    out = []
    for lv in levels:
        for line in gen.lines(lv):
            if len(line) < 4:
                continue
            px = cx + line[:, 0] * sx
            py = cy + line[:, 1] * sy
            out.append((lv, np.c_[px, py]))
    return out

def poly(pts, **attr):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attr.items())
    return f'<path d="{d}" fill="none" {a}/>'

def halfbody_lines(nose_x, cy, half_w, W, H, levels, n=900, facing=-1):
    """Rankine half-body: uniform flow + point source. Body nose at nose_x, far-field
    half-width half_w px. facing=-1: nose points right, body trails left (car driving right).
    Returns [(level, pts)] including level 0 (the body surface)."""
    # in flow units: source at origin, U=1, m chosen so half width = 1 unit -> m = 2
    # stagnation point at x = -m/(2*pi*U) = -1/pi
    s = half_w  # px per unit
    xs_c = np.linspace(0, W, n); ys_c = np.linspace(0, H, int(n * H / W) + 2)
    Xc, Yc = np.meshgrid(xs_c, ys_c)
    # canvas -> flow coords (mirror x if facing right)
    X = facing * (Xc - nose_x) / s - 1 / np.pi
    Y = (Yc - cy) / s
    Z = Y + 2 / (2 * np.pi) * np.arctan2(Y, X)
    gen = contourpy.contour_generator(xs_c, ys_c, Z)
    out = []
    for lv in levels:
        for line in gen.lines(lv):
            if len(line) >= 4:
                out.append((lv, line))
    # body surface (psi = +-1), analytic: y = 1 - theta/pi, x = y cot(theta)
    th = np.linspace(1e-3, np.pi - 1e-3, 600)
    y = 1 - th / np.pi
    x = y * np.cos(th) / np.sin(th)
    keep = x < (nose_x + 40) / s + 1     # trim far downstream
    for sg in (1, -1):
        px = nose_x + facing * (x + 1 / np.pi) * s
        py = cy + sg * y * s
        ok = (px > -40) & (px < W + 40)
        out.append((0.0, np.c_[px[ok], py[ok]]))
    return out

def cylinder_lines(cx, cy, R, W, H, levels, n=900):
    """Potential flow past a circular cylinder of radius R px (uniform flow + doublet):
    psi = y (1 - R^2 / r^2). Returns [(level, pts)] for psi != 0 (outside the body)."""
    xs = np.linspace(0, W, n); ys = np.linspace(0, H, int(n * H / W) + 2)
    X, Y = np.meshgrid(xs - cx, ys - cy)
    r2 = np.maximum(X ** 2 + Y ** 2, 1e-9)
    Z = Y * (1 - R ** 2 / r2)
    Z[r2 < R ** 2] = np.nan
    gen = contourpy.contour_generator(xs, ys, Z)
    out = []
    for lv in levels:
        for line in gen.lines(lv):
            if len(line) >= 4:
                out.append((lv, line))
    return out

B_NAUT = np.log(3.0) / (2 * np.pi)   # Nautilus pompilius: whorl radius grows about 3x per turn

def nautilus(cx, cy, r_end, turns=3.0, rot=0.0, step_deg=24.0, flip=-1, living_deg=120.0, b=B_NAUT):
    """Log-spiral shell r = r_end * exp(b t), t <= 0. Returns (spiral_pts, septa, living_chamber_poly).
    Septa join the whorl at t to the whorl beneath it (t - 2pi), bowed toward the opening.
    The opening is the radial segment at angle `rot`."""
    def P(t):
        r = r_end * np.exp(b * t)
        return np.array([cx + r * np.cos(flip * t + rot), cy + r * np.sin(flip * t + rot)])
    def wall(t):
        a, c0 = P(t), P(t - 2 * np.pi)
        m = (a + c0) / 2
        tang = P(t + 0.02) - P(t); tang /= (np.linalg.norm(tang) + 1e-9)
        c = m + tang * np.linalg.norm(a - c0) * 0.28
        u = np.linspace(0, 1, 40)[:, None]
        return (1 - u) ** 2 * a + 2 * (1 - u) * u * c + u ** 2 * c0
    ts = np.linspace(-turns * 2 * np.pi, 0, 1600)
    spiral = np.array([P(t) for t in ts])
    t_last = -np.deg2rad(living_deg)
    septa, t = [], t_last
    while t > -(turns - 1.0) * 2 * np.pi:
        septa.append(wall(t)); t -= np.deg2rad(step_deg)
    to = np.linspace(t_last, 0, 200); ti = np.linspace(-2 * np.pi, t_last - 2 * np.pi, 200)
    living = np.vstack([[P(x) for x in to], [P(x) for x in ti], wall(t_last)[::-1]])
    return spiral, septa, living
