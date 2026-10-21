# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio. Field Notes mark: a measured specimen roundel.
"""The mark is a specimen roundel: a measuring ring (60 graduations, like a gauge or
protractor) around one 'specimen', the existing cargen car whose crumple zone is drawn as a
folded hornbeam leaf, pressed against a rigid barrier on a fixed-support ground line
(the engineering-drawing symbol). Nothing else: no stars, no gradients.

Drawings:
  mark()        full roundel, 48 px and up. Primary = graphite disc (continues the charcoal tile).
  glyph()       the specimen without the roundel (inline use, partner walls)
  mark_small()  roundel tuned for 24-48 px: no graduations, thicker ring, single midrib
  mark_16()     16 x 16 pixel master for favicons"""
from fn_lib import *

# Car body + crumple zone from the existing cargen mark (assets/logo/cargen-mark.svg, MIT, same project),
# kept verbatim so the silhouette continues. The crumple zone is recoloured and veined as a pleated leaf.
BODY = "M34 178 V160 C34 151 40 146 48 145 L84 140 C100 121 120 111 146 111 C162 111 173 118 182 130 L182 178 Z"
PLEAT = "M182 136 L192 124 L200.2 136 L206.9 124 L212.4 136 L212.4 172 L206.9 184 L200.2 172 L192 184 L182 172 Z"
VEINS = ("M197.2 132 V176 M197.2 142 L186 136 M197.2 152 L186 146 M197.2 162 L186 156 "
         "M197.2 142 L208 136 M197.2 152 L208 146 M197.2 162 L208 156")

THEMES = {
    #               disc           line/ink       body          pleat         vein
    "graphite":   (P["graphite"], P["chalk"],    P["signal"],  P["lichen"],  P["graphite"]),
    "paper":      (P["paper"],    P["graphite"], P["signal"],  P["fern"],    P["paper"]),
    "mono":       (P["paper"],    P["graphite"], P["graphite"], P["graphite"], P["paper"]),
    "mono-chalk": (P["graphite"], P["chalk"],    P["chalk"],   P["chalk"],   P["graphite"]),
}

def specimen(theme, ground=True, barrier=True, colours=None):
    """Car + leaf pleat + barrier, in the 256 mark coordinate space (unscaled)."""
    bg, ink, body, pleat, vein = colours or THEMES[theme]
    mono = theme.startswith("mono")
    g = []
    if ground:  # fixed-support symbol: one rule with short hatches
        g.append(f'<path d="M22 193.5 H230" stroke="{ink}" stroke-width="1.6"/>')
        g.append(f'<path d="{" ".join(f"M{x} 193.5 l-6 6.5" for x in range(32, 228, 10))}" stroke="{ink}" stroke-width="1"/>')
    g.append(f'<path d="{BODY}" fill="{body}"/>')
    # one-colour versions: a disc-coloured keyline separates leaf from body
    gap = f' paint-order="stroke" stroke="{bg}" stroke-width="7"' if mono else f' stroke="{pleat}" stroke-width="2"'
    g.append(f'<path d="{PLEAT}" fill="{pleat}"{gap} stroke-linejoin="round"/>')
    g.append(f'<path d="{VEINS}" stroke="{vein}" stroke-width="2.4" stroke-linecap="round" fill="none"/>')
    if barrier:
        g.append(f'<path d="M221.4 108 V196" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    for wx in (76, 150):
        g.append(f'<circle cx="{wx}" cy="178" r="15" fill="{ink}" stroke="{bg}" stroke-width="4.5"/>'
                 f'<circle cx="{wx}" cy="178" r="5" fill="{bg}"/>')
    return "".join(g)

def mark(theme="graphite", uid="m"):
    """256x256 full roundel."""
    bg, ink = THEMES[theme][:2]
    R = 118
    out = [f'<circle cx="128" cy="128" r="{R}" fill="{bg}"/>']
    # measuring ring: hairline + 60 graduations, long every 30 degrees
    out.append(f'<circle cx="128" cy="128" r="{R-14}" fill="none" stroke="{ink}" stroke-width="1.2"/>')
    ticks = []
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = R - 14; r1 = R - (5 if i % 5 == 0 else 9.5)
        ticks.append(f"M{128 + r0*math.cos(a):.2f} {128 + r0*math.sin(a):.2f} L{128 + r1*math.cos(a):.2f} {128 + r1*math.sin(a):.2f}")
    out.append(f'<path d="{" ".join(ticks)}" stroke="{ink}" stroke-width="1.3"/>')
    s = 0.8
    cx_car, cy_car = 130, 155          # centre of the specimen incl. ground hatching
    tx = 128 - cx_car * s; ty = 136 - cy_car * s
    out.append(f'<g transform="translate({tx:.2f} {ty:.2f}) scale({s})">{specimen(theme)}</g>')
    if theme in ("paper", "mono"):
        out.append(f'<circle cx="128" cy="128" r="{R-2.5}" fill="none" stroke="{ink}" stroke-width="5"/>')
    else:  # chalk rim keeps the disc visible on graphite grounds
        out.append(f'<circle cx="128" cy="128" r="{R-1.5}" fill="none" stroke="{ink}" stroke-width="3"/>')
    return "".join(out)

def glyph(theme="paper"):
    """Specimen only, cropped to a 216x116 box (no roundel, no ground). Keylines, hubs and veins are
    real cut-outs (SVG mask), so the glyph works on any background, including one-colour print."""
    mask_cols = ("#000", "#fff", "#fff", "#fff", "#000")
    m = f'<mask id="gm{theme}" maskUnits="userSpaceOnUse" x="0" y="0" width="256" height="256">{specimen(theme, ground=False, colours=mask_cols)}</mask>'
    return (f'<defs>{m}</defs><g transform="translate(-22 -97)"><g mask="url(#gm{theme})">'
            f'{specimen(theme, ground=False)}</g></g>')

def mark_small(theme="graphite"):
    """Roundel tuned for 24-48 px: no graduations, one midrib, the ring stands in for the barrier.
    Edges sit on the 32 px grid (8 units = 1 px at 32 px)."""
    bg, ink, body, pleat, vein = THEMES[theme]
    o = [f'<circle cx="128" cy="128" r="124" fill="{bg}"/>']
    o.append(f'<path d="M40 168 V144 Q40 128 56 128 L88 120 Q108 88 144 88 Q164 88 176 108 V168 Z" fill="{body}"/>')
    o.append(f'<path d="M176 112 L188 100 L200 112 L212 100 V184 L200 172 L188 184 L176 172 Z" fill="{pleat}"/>')
    o.append(f'<path d="M194 116 V168" stroke="{vein}" stroke-width="6" stroke-linecap="round"/>')
    for wx in (80, 144):
        o.append(f'<circle cx="{wx}" cy="168" r="20" fill="{ink}" stroke="{bg}" stroke-width="8"/>')
        o.append(f'<circle cx="{wx}" cy="168" r="7" fill="{bg}"/>')
    o.append(f'<circle cx="128" cy="128" r="{116 if theme == "paper" else 118}" fill="none" stroke="{ink}" '
             f'stroke-width="{16 if theme == "paper" else 8}"/>')
    return "".join(o)

# 16 px: drawn pixel by pixel. One string per row: . = disc, c = car body, h = half-covered body pixel,
# g = leaf, k = wheel.
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

def mark_16(theme="graphite"):
    """16x16 pixel master (viewBox 0 0 16 16). Disc and ring use exact per-pixel coverage;
    the specimen is pixel-snapped so it stays crisp in a browser tab."""
    bg, ink, body, pleat, _ = THEMES[theme]
    cols = {"c": body, "g": pleat, "k": ink}
    ring_in = 6.7 if theme == "paper" else 7.3   # graphite: hairline chalk ring only
    o = []
    SS = 8
    for y in range(16):
        for x in range(16):
            cin = cring = 0
            for sy in range(SS):
                for sx in range(SS):
                    r = math.hypot(x + (sx + .5) / SS - 8, y + (sy + .5) / SS - 8)
                    if r <= ring_in: cin += 1
                    elif r <= 7.95: cring += 1
            n = SS * SS
            if cin:
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{bg}" fill-opacity="{cin/n:.3f}"/>')
            if cring:
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{ink}" fill-opacity="{cring/n:.3f}"/>')
            ch = PIX16[y][x]
            if ch in cols:
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{cols[ch]}"/>')
            elif ch == "h":
                o.append(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{body}" fill-opacity="0.45"/>')
    return "".join(o)

def build():
    for theme in THEMES:
        sfx = "" if theme == "graphite" else f"-{theme}"
        write(f"mark/cargen-fieldnotes-mark{sfx}.svg", svg(256, 256, mark(theme, uid=theme), f"cargen mark ({theme})"))
        write(f"mark/cargen-fieldnotes-glyph{sfx}.svg",
              svg(216, 116, glyph(theme), f"cargen glyph ({theme})", bg=P["graphite"] if theme in ("graphite", "mono-chalk") else None))
    for theme in ("graphite", "paper"):
        sfx = "" if theme == "graphite" else "-paper"
        write(f"mark/cargen-fieldnotes-mark-small{sfx}.svg", svg(256, 256, mark_small(theme), f"cargen small mark ({theme})"))
        write(f"mark/cargen-fieldnotes-mark-16{sfx}.svg",
              svg(16, 16, mark_16(theme), "cargen 16 px mark").replace('viewBox="0 0 16 16"', 'viewBox="0 0 16 16" shape-rendering="crispEdges"'))

def build_touch():
    """Full-bleed square for iOS / Android home screens (they mask corners themselves)."""
    body = f'<rect width="256" height="256" fill="{P["graphite"]}"/><g transform="translate(18 18) scale(0.86)">{mark("graphite", uid="touch")}</g>'
    write("mark/cargen-fieldnotes-touch-icon.svg", svg(256, 256, body, "cargen touch icon"))

if __name__ == "__main__":
    build(); build_touch()
