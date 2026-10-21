# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio. Field Notes mark: a specimen roundel.
"""The mark is a specimen roundel: a star-atlas ring (degree graticule) around one
'specimen', the cargen car whose crumple zone is a folded hornbeam leaf, pressed
against a barrier on an engraved ground line.

Three drawings:
  mark()        full roundel, >= 48 px
  glyph()       the specimen without the roundel (inline use, partner walls)
  mark_small()  pixel-tuned roundel for 16-48 px (favicons): no ticks, no stars,
                every edge on the 16 px grid (1 px = 16 units of the 256 canvas)."""
from fn_lib import *

# Car body from the existing cargen mark (assets/logo/cargen-mark.svg, MIT, same project), kept verbatim
# so the silhouette continues. The crumple zone becomes a pleated leaf (hornbeam leaves fold like a crush tube).
BODY = "M34 178 V160 C34 151 40 146 48 145 L84 140 C100 121 120 111 146 111 C162 111 173 118 182 130 L182 178 Z"
PLEAT = "M182 136 L192 124 L200.2 136 L206.9 124 L212.4 136 L212.4 172 L206.9 184 L200.2 172 L192 184 L182 172 Z"
VEINS = ("M197.2 132 V176 M197.2 142 L186 136 M197.2 152 L186 146 M197.2 162 L186 156 "
         "M197.2 142 L208 136 M197.2 152 L208 146 M197.2 162 L208 156")

THEMES = {
    #           bg            ring/ink        body          pleat      vein (on pleat)  star
    "light":   (P["paper"],  P["ink"],       P["copper"],  P["fern"],  P["paper"],      P["copper"]),
    "dark":    (P["night"],  P["starlight"], P["copper"],  "#6FA27C",  P["night"],      P["copper"]),
    "mono":    (P["paper"],  P["ink"],       P["ink"],     P["ink"],   P["paper"],      P["ink"]),
    "mono-dark": (P["night"], P["starlight"], P["starlight"], P["starlight"], P["night"], P["starlight"]),
}

def specimen(theme, ground=True, barrier=True, bg=None):
    """Car + leaf pleat + barrier, in the 256 mark coordinate space (unscaled)."""
    bg0, ink, body, pleat, vein, _ = THEMES[theme]
    bg = bg or bg0
    mono = theme.startswith("mono")
    g = []
    if ground:
        g.append(f'<path d="M18 193.5 H232" stroke="{ink}" stroke-width="1.4"/>')
        g.append(f'<path d="{" ".join(f"M{x} 193.5 l-6 6" for x in range(30, 226, 9))}" stroke="{ink}" stroke-width="0.9"/>')
    g.append(f'<path d="{BODY}" fill="{body}"/>')
    # in one-colour versions a bg-coloured keyline separates the leaf from the body
    gap = f' paint-order="stroke" stroke="{bg}" stroke-width="7"' if mono else f' stroke="{pleat}" stroke-width="2"'
    g.append(f'<path d="{PLEAT}" fill="{pleat}"{gap} stroke-linejoin="round"/>')
    g.append(f'<path d="{VEINS}" stroke="{vein}" stroke-width="2.2" stroke-linecap="round" fill="none"/>')
    if barrier:
        g.append(f'<path d="M221.4 108 V196" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    for wx in (76, 150):
        g.append(f'<circle cx="{wx}" cy="178" r="15" fill="{ink}" stroke="{bg}" stroke-width="4"/>'
                 f'<circle cx="{wx}" cy="178" r="5" fill="{bg}"/>')
    return "".join(g)

def mark(theme="light", uid="m"):
    """256x256 full roundel."""
    bg, ink, body, pleat, vein, star = THEMES[theme]
    R = 116
    out = [f'<circle cx="128" cy="128" r="{R}" fill="{bg}"/>']
    # star-atlas graticule: hairline inner ring + degree ticks every 6 deg, long every 30 deg
    out.append(f'<circle cx="128" cy="128" r="{R-12}" fill="none" stroke="{ink}" stroke-width="1.1"/>')
    ticks = []
    for i in range(60):
        a = math.radians(i * 6)
        r0 = R - 12; r1 = R - (4 if i % 5 == 0 else 8)
        ticks.append(f"M{128 + r0*math.cos(a):.2f} {128 + r0*math.sin(a):.2f} L{128 + r1*math.cos(a):.2f} {128 + r1*math.sin(a):.2f}")
    out.append(f'<path d="{" ".join(ticks)}" stroke="{ink}" stroke-width="1.1"/>')
    # one atlas star with a two-line asterism, upper left (the 'explore' note of the plate)
    out.append(f'<path d="M84 78 L112 62 M84 78 L60 102" stroke="{ink}" stroke-width="0.9" stroke-dasharray="2 3"/>')
    out.append(star_glyph(84, 78, 3.4, star))
    out.append(f'<circle cx="112" cy="62" r="1.8" fill="{ink}"/><circle cx="60" cy="102" r="1.5" fill="{ink}"/>'
               f'<circle cx="170" cy="72" r="1.3" fill="{ink}"/>')
    s = 0.9
    cx_car = (34 + 221) / 2; cy_car = (111 + 193) / 2
    tx = 128 - cx_car * s; ty = 140 - cy_car * s
    out.append(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s})">{specimen(theme)}</g>')
    out.append(f'<circle cx="128" cy="128" r="{R}" fill="none" stroke="{ink}" stroke-width="6"/>')
    return "".join(out)

def glyph(theme="light"):
    """Specimen only, cropped to a 216x116 box (no roundel, no ground hatching)."""
    bg = None
    if theme in ("light", "mono"):
        bg = P["paper"]
    return f'<g transform="translate(-22 -97)">{specimen(theme, ground=False)}</g>'

def mark_small(theme="light"):
    """Roundel tuned for 24-48 px: no ticks, no stars, thicker ring, bolder leaf, the ring stands in
    for the barrier. Edges sit on the 32 px grid (8 units = 1 px at 32 px)."""
    if theme == "dark":
        disc, ring, body, pleat, wheel, hub = P["night"], P["starlight"], P["copper"], "#7DB08A", P["starlight"], P["night"]
    else:
        disc, ring, body, pleat, wheel, hub = P["paper"], P["ink"], P["copper"], P["fern"], P["ink"], P["paper"]
    o = [f'<circle cx="128" cy="128" r="120" fill="{disc}"/>']
    o.append(f'<path d="M40 168 V144 Q40 128 56 128 L88 120 Q108 88 144 88 Q164 88 176 108 V168 Z" fill="{body}"/>')
    o.append(f'<path d="M176 112 L188 100 L200 112 L212 100 V184 L200 172 L188 184 L176 172 Z" fill="{pleat}"/>')
    o.append(f'<path d="M194 116 V168" stroke="{disc}" stroke-width="6" stroke-linecap="round"/>')
    for wx in (80, 144):
        o.append(f'<circle cx="{wx}" cy="168" r="20" fill="{wheel}" stroke="{disc}" stroke-width="8"/>')
        o.append(f'<circle cx="{wx}" cy="168" r="7" fill="{hub}"/>')
    o.append(f'<circle cx="128" cy="128" r="116" fill="none" stroke="{ring}" stroke-width="16"/>')
    return "".join(o)

# 16 px: drawn pixel by pixel. Each string is one row; . = disc, c = copper body, g = leaf, k = wheel.
PIX16 = [
    "................",
    "................",
    "................",
    "................",
    ".....hccch......",
    "...hcccccc......",
    "..cccccccc.g....",
    "..cccccccc.gg...",
    "..cccccccc.gg...",
    "..ckkcckkc.gg...",
    "...kk..kk...g...",
    "................",
    "................",
    "................",
    "................",
    "................",
]

def mark_16(theme="light"):
    """16x16 pixel master (viewBox 0 0 16 16). Ring is anti-aliased by exact per-pixel coverage;
    the specimen is pixel-snapped so it stays crisp in a browser tab."""
    if theme == "dark":
        disc, ring, cols = P["night"], P["starlight"], {"c": P["copper"], "g": "#7DB08A", "k": P["starlight"]}
    else:
        disc, ring, cols = P["paper"], P["ink"], {"c": P["copper"], "g": P["fern"], "k": P["ink"]}
    o = []
    SS = 8
    for y in range(16):
        for x in range(16):
            cin = cring = 0
            for sy in range(SS):
                for sx in range(SS):
                    px = x + (sx + .5) / SS - 8; py = y + (sy + .5) / SS - 8
                    r = math.hypot(px, py)
                    if r <= 6.7: cin += 1
                    elif r <= 7.9: cring += 1
            n = SS * SS
            if cin:
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{disc}" fill-opacity="{cin/n:.3f}"/>')
            if cring:
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{ring}" fill-opacity="{cring/n:.3f}"/>')
            ch = PIX16[y][x]
            if ch in cols:
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{cols[ch]}"/>')
            elif ch == "h":  # half-covered copper pixel: anti-aliased roof slope
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{cols["c"]}" fill-opacity="0.45"/>')
    return "".join(o)

def build():
    for theme, name in (("light", "mark"), ("dark", "mark-dark"), ("mono", "mark-mono"), ("mono-dark", "mark-mono-dark")):
        write(f"mark/cargen-fieldnotes-{name}.svg", svg(256, 256, mark(theme, uid=name), f"cargen mark ({theme})"))
    for theme, name in (("light", "glyph"), ("dark", "glyph-dark"), ("mono", "glyph-mono"), ("mono-dark", "glyph-mono-dark")):
        bg = P["night"] if "dark" in theme else None
        write(f"mark/cargen-fieldnotes-{name}.svg", svg(216, 116, glyph(theme), f"cargen glyph ({theme})", bg=bg))
    write("mark/cargen-fieldnotes-mark-small.svg", svg(256, 256, mark_small("light"), "cargen small mark"))
    write("mark/cargen-fieldnotes-mark-small-dark.svg", svg(256, 256, mark_small("dark"), "cargen small mark (dark)"))
    for theme, sfx in (("light", ""), ("dark", "-dark")):
        body = mark_16(theme)
        write(f"mark/cargen-fieldnotes-mark-16{sfx}.svg",
              svg(16, 16, body, "cargen 16 px mark").replace('viewBox="0 0 16 16"', 'viewBox="0 0 16 16" shape-rendering="crispEdges"'))

if __name__ == "__main__":
    build()
