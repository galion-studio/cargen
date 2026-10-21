# SPDX-License-Identifier: MIT
"""Convert text to SVG path data with fontTools (OFL fonts only), so SVGs need no font files."""
import functools
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

G = "/usr/share/fonts/truetype/sand-box/google/"
FONTS = {
    "outfit": G + "Outfit/Outfit-VariableFont_wght.ttf",
    "sora": G + "Sora/Sora-VariableFont_wght.ttf",
    "inter": G + "Inter/Inter-VariableFont_opsz,wght.ttf",
    "manrope": G + "Manrope/Manrope-VariableFont_wght.ttf",
    "plexmono": G + "IBM Plex Mono/IBMPlexMono-Regular.ttf",
    "plexmono-med": G + "IBM Plex Mono/IBMPlexMono-Medium.ttf",
}

@functools.lru_cache(None)
def font(name, wght=None):
    f = TTFont(FONTS[name])
    if "fvar" in f and wght is not None:
        axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
        axes["wght"] = wght
        if "opsz" in axes:
            axes["opsz"] = 32
        f = instantiateVariableFont(f, axes)
    return f

def text_path(text, name, size, x=0, y=0, wght=None, tracking=0.0, anchor="start"):
    """Return (path_d, width). y is the baseline. tracking in em units."""
    f = font(name, wght)
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f["head"].unitsPerEm
    s = size / upm
    hmtx = f["hmtx"]
    # kerning via GPOS is skipped; tracking handles spacing (letters checked visually)
    adv = [hmtx[cmap[ord(c)]][0] for c in text]
    total = (sum(adv) + tracking * upm * (len(text) - 1)) * s
    if anchor == "middle": x -= total / 2
    elif anchor == "end": x -= total
    pen = SVGPathPen(gs, lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    cx = 0
    for c, a in zip(text, adv):
        tp = TransformPen(pen, (s, 0, 0, -s, x + cx * s, y))
        gs[cmap[ord(c)]].draw(tp)
        cx += a + tracking * upm
    return pen.getCommands(), total

def cap_height(name, size, wght=None):
    f = font(name, wght)
    os2 = f["OS/2"]
    return getattr(os2, "sCapHeight", 700) * size / f["head"].unitsPerEm

def x_height(name, size, wght=None):
    f = font(name, wght)
    return f["OS/2"].sxHeight * size / f["head"].unitsPerEm
