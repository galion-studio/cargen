# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Text -> SVG path data (OFL fonts only), shaped with HarfBuzz so kerning is kept.
SVG masters therefore need no font files."""
import functools, io
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

G = "/usr/share/fonts/truetype/sand-box/google/"
FONTS = {  # all SIL Open Font License 1.1
    "archivo": G + "Archivo/Archivo-VariableFont_wdth,wght.ttf",
    "plexsans": G + "IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf",
    "plexmono": G + "IBM Plex Mono/IBMPlexMono-Regular.ttf",
    "plexmono-med": G + "IBM Plex Mono/IBMPlexMono-Medium.ttf",
}

@functools.lru_cache(None)
def _font(name, axes):
    f = TTFont(FONTS[name])
    if "fvar" in f:
        loc = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
        loc.update(dict(axes))
        f = instantiateVariableFont(f, loc)
    buf = io.BytesIO(); f.save(buf); data = buf.getvalue()
    return TTFont(io.BytesIO(data)), hb.Font(hb.Face(data))

def text_path(text, name, size, x=0.0, y=0.0, tracking=0.0, anchor="start", **axes):
    """Return (d, width). y = baseline. tracking in em. axes e.g. wght=600, wdth=112."""
    tt, hf = _font(name, tuple(sorted(axes.items())))
    upm = tt["head"].unitsPerEm; s = size / upm
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hf, buf, {"kern": True, "liga": False})
    gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    infos, pos = buf.glyph_infos, buf.glyph_positions
    adv = [p.x_advance + tracking * upm for p in pos]
    total = (sum(adv) - tracking * upm) * s
    if anchor == "middle": x -= total / 2
    elif anchor == "end": x -= total
    pen = SVGPathPen(gs, lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
    bp = BoundsPen(gs)
    cx = 0.0
    for i, p, a in zip(infos, pos, adv):
        m = (s, 0, 0, -s, x + (cx + p.x_offset) * s, y - p.y_offset * s)
        gs[order[i.codepoint]].draw(TransformPen(pen, m)); gs[order[i.codepoint]].draw(TransformPen(bp, m))
        cx += a
    text_path.last_bounds = bp.bounds  # (xmin, ymin, xmax, ymax) in output coords
    return pen.getCommands(), total

def metrics(name, size, **axes):
    tt, _ = _font(name, tuple(sorted(axes.items())))
    o = tt["OS/2"]; k = size / tt["head"].unitsPerEm
    return {"cap": o.sCapHeight * k, "x": o.sxHeight * k, "asc": o.sTypoAscender * k, "desc": -o.sTypoDescender * k}
