# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Strata palette: single source of truth for every asset and the graph styles."""
P = {
    "basalt":    ("#0F1317", "Basalt", "deepest ground: dark banners, social preview"),
    "graphite":  ("#16202A", "Graphite", "existing Forge tile; primary dark; text on light"),
    "shale":     ("#2C3540", "Shale", "strata lines and cards on dark"),
    "fold":      ("#F26B1D", "Fold Orange", "existing accent: the mark's middle band; validated-simulation line on dark"),
    "oxide":     ("#B5470C", "Oxide", "orange for text and thin lines on light"),
    "limestone": ("#F2EEE6", "Limestone", "light ground; mark bands; text on dark"),
    "chalk":     ("#FBFAF7", "Chalk", "lightest surface, cards on Limestone"),
    "glacier":   ("#2F5F8F", "Glacier", "physical-test data on light"),
    "ice":       ("#86AEDA", "Ice", "physical-test data on dark"),
    "stone":     ("#5A6470", "Stone", "secondary text on light"),
    "ash":       ("#8E97A1", "Ash", "secondary text on dark"),
    "sediment":  ("#D9D2C5", "Sediment", "strata lines and rules on light (decorative only)"),
}
C = {k: v[0] for k, v in P.items()}

def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lum(h):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)
