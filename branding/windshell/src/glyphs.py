# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Convert text in an OFL font to SVG path data (so SVGs need no font files).
Fonts: IBM Plex Sans and IBM Plex Mono (SIL OFL 1.1, github.com/IBM/plex). Manrope stays
registered only for comparison; the brand does not use it."""
import io
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from functools import lru_cache

G = "/usr/share/fonts/truetype/sand-box/google/"
FONTS = {"manrope": G + "Manrope/Manrope-VariableFont_wght.ttf",
         "plexmono": G + "IBM Plex Mono/IBMPlexMono-Medium.ttf",
         "plexmono-r": G + "IBM Plex Mono/IBMPlexMono-Regular.ttf",
         "plexsans": G + "IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf"}

@lru_cache(None)
def _font(name, wght):
    f = TTFont(FONTS[name])
    if "fvar" in f:
        axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
        axes["wght"] = wght
        f = instancer.instantiateVariableFont(f, axes)
    buf = io.BytesIO(); f.save(buf); data = buf.getvalue()
    return TTFont(io.BytesIO(data)), data

def text_path(text, name="manrope", wght=600, size=100, x=0, y=0, tracking=0.0, anchor="start"):
    """Return (d, width). y is baseline. tracking in em."""
    f, data = _font(name, wght)
    upem = f["head"].unitsPerEm
    face = hb.Face(data); hbf = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, {"kern": True, "liga": False})
    gs = f.getGlyphSet(); order = f.getGlyphOrder()
    s = size / upem
    adv_total = sum(p.x_advance for p in buf.glyph_positions) + tracking * upem * (len(text) - 1)
    width = adv_total * s
    if anchor == "middle": x -= width / 2
    elif anchor == "end": x -= width
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    cx = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = order[info.codepoint]
        tp = TransformPen(pen, (s, 0, 0, -s, x + (cx + pos.x_offset) * s, y - pos.y_offset * s))
        gs[gname].draw(tp)
        cx += pos.x_advance + tracking * upem
    return pen.getCommands(), width

def metrics(name="manrope", wght=600):
    f, _ = _font(name, wght)
    os2 = f["OS/2"]; upem = f["head"].unitsPerEm
    return {"xh": os2.sxHeight / upem, "cap": os2.sCapHeight / upem}
