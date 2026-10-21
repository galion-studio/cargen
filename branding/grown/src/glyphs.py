# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Shape text with HarfBuzz from an OFL font file and return SVG path data (no font needed to view)."""
import io, functools
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

G = "/usr/share/fonts/truetype/sand-box/google/"
FONTS = {
    "outfit": G + "Outfit/Outfit-VariableFont_wght.ttf",
    "sora": G + "Sora/Sora-VariableFont_wght.ttf",
    "manrope": G + "Manrope/Manrope-VariableFont_wght.ttf",
    "figtree": G + "Figtree/Figtree-VariableFont_wght.ttf",
    "plex": G + "IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf",
    "instrument": G + "Instrument Sans/InstrumentSans-VariableFont_wdth,wght.ttf",
    "hanken": G + "Hanken Grotesk/HankenGrotesk-VariableFont_wght.ttf",
    "geologica": G + "Geologica/Geologica-VariableFont_CRSV,SHRP,slnt,wght.ttf",
    "plexmono": G + "IBM Plex Mono/IBMPlexMono-Medium.ttf",
}

@functools.lru_cache(None)
def _load(name, wght):
    path = FONTS[name]
    f = TTFont(path)
    if "fvar" in f:
        axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
        loc = {k: v for k, v in axes.items()}
        if "wght" in loc: loc["wght"] = wght
        f = instancer.instantiateVariableFont(f, loc)
    buf = io.BytesIO(); f.save(buf); data = buf.getvalue()
    return TTFont(io.BytesIO(data)), data

def text_path(text, name="outfit", wght=500, size=100, x=0, y=0, tracking=0):
    """Return (d, width, cap_height_px, xheight_px). y is the baseline."""
    f, data = _load(name, wght)
    upm = f["head"].unitsPerEm
    face = hb.Face(data); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": False})
    gs = f.getGlyphSet(); order = f.getGlyphOrder()
    s = size / upm
    pen = SVGPathPen(gs)
    cx = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = order[info.codepoint]
        tp = TransformPen(pen, (s, 0, 0, -s, x + (cx + pos.x_offset) * s, y - pos.y_offset * s))
        gs[gname].draw(tp)
        cx += pos.x_advance + tracking
    os2 = f["OS/2"]
    return pen.getCommands(), (cx - tracking) * s, os2.sCapHeight * s, os2.sxHeight * s
