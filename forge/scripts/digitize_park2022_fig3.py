# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Digitize Figure 3 of Park, Cho & Kim (2022), Materials 15:2107 (CC BY 4.0),
doi:10.3390/ma15062107 -- the US-2 indentation vs reaction-force curve
(P_m = 100.98 kN marked in the figure, matches Table 4 US-2).

Input: the figure image as embedded in the publisher PDF (extracted with pdfimages).
Output: CSV (displacement_mm, force_kN) with a provenance header.
Method: colour mask of the blue curve, axis calibration from the tick marks,
column-wise tracking with continuity, removal of the dashed P_m line and the
black annotation markers (gaps linearly interpolated).
"""
import sys, numpy as np
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert("RGB")).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
blue = (b > 170) & (b - r > 50) & (b - g > 10)

# axis calibration (pixel centres of tick marks / gridlines, measured from the image)
X0, X400 = 98.5, 1171.5      # 0 mm and 400 mm ticks
Y0, Y400 = 496.5, 19.5       # 0 kN and 400 kN gridlines
px2mm = lambda x: (x - X0) * 400.0 / (X400 - X0)
py2kN = lambda y: (Y0 - y) * 400.0 / (Y0 - Y400)
dash_row = Y0 - 100.98 * (Y0 - Y400) / 400.0  # dashed P_m line

xs, ys = [], []
prev = None
for x in range(int(X0) + 1, int(X400)):
    rows = np.where(blue[:, x])[0]
    rows = rows[(rows > Y400 - 2) & (rows < Y0)]
    if rows.size == 0:
        continue
    # split into contiguous runs
    runs = np.split(rows, np.where(np.diff(rows) > 1)[0] + 1)
    cand = []
    for run in runs:
        c = run.mean()
        is_dash = abs(c - dash_row) < 3 and len(run) <= 5
        cand.append((c, is_dash, run))
    nond = [c for c in cand if not c[1]]
    use = nond if nond else cand
    if prev is None:
        pick = min(use, key=lambda c: c[0])  # topmost (spike)
    else:
        pick = min(use, key=lambda c: abs(c[0] - prev))
    # if only dash candidates and the curve was far away, skip (curve hidden)
    if not nond and prev is not None and abs(pick[0] - prev) > 6:
        continue
    yv = pick[0]
    prev = yv
    xs.append(px2mm(x)); ys.append(py2kN(yv))

xs, ys = np.array(xs), np.array(ys)
# resample on a 0.5 mm grid up to the last digitized point
grid = np.arange(0.0, xs.max(), 0.5)
fy = np.interp(grid, xs, ys)
fy[0] = 0.0
with open(out, "w") as f:
    f.write("# source: Park Y.I., Cho J.-S., Kim J.-H. (2022) Materials 15(6):2107, doi:10.3390/ma15062107, Fig. 3 (specimen US-2), CC BY 4.0\n")
    f.write("# digitized by forge/scripts/digitize_park2022_fig3.py from the publisher PDF image; digitization uncertainty ~ +/-1 mm, +/-2 kN; initial spike under-resolved (use Table 4 P_u=337.1 kN for peak)\n")
    f.write("displacement_mm,force_kN\n")
    for a, c in zip(grid, fy):
        f.write(f"{a:.2f},{c:.3f}\n")
E = np.trapezoid(fy, grid)
print("points", len(grid), "max x", grid[-1], "max F", fy.max(), "E/d(343)", np.trapezoid(fy[grid<=343], grid[grid<=343])/343)
