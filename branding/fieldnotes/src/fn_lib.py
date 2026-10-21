# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio. "Field Notes" branding concept for cargen. Original artwork.
"""Shared helpers: palette, OFL fonts -> SVG outline paths (uharfbuzz shaping +
fontTools outlines), and generative engraving primitives (leaf, moth wing, car,
crush tube, stars). Every SVG written here is self-contained: no font files are
referenced, all lettering is converted to paths."""
import math, os, random, functools
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
GF = "/usr/share/fonts/truetype/sand-box/google"
CACHE = os.path.join(HERE, ".fontcache")
os.makedirs(CACHE, exist_ok=True)

# ---------------------------------------------------------------- palette
P = dict(
    graphite="#16202A",   # existing cargen charcoal: primary dark ground, text on paper
    rule="#2A3843",       # graticule / grid lines on graphite (non-text)
    paper="#F3EDDF",      # field-notebook paper: light ground
    vellum="#E7DDC6",     # deeper paper: plate panels, caption blocks (non-text)
    chalk="#EDE6D3",      # text and line work on graphite
    sepia="#5E5141",      # secondary text on paper (captions, provenance)
    dust="#B9B09C",       # secondary text on graphite
    signal="#F26B1D",     # existing cargen orange: the car, validated-simulation results
    signalInk="#A8461A",  # signal orange for text / thin lines on paper (AA)
    cyan="#2F5F8F",       # cyanotype blue: physical test data on paper
    cyanPale="#7FA8D6",   # cyanotype blue on graphite
    fern="#3D6B4A",       # specimen green on paper: the leaf, never data
    lichen="#8DB89A",     # specimen green on graphite
    sage="#A9BC9C",       # pale leaf wash (fills only)
)
# legacy aliases used by the primitives below
P.update(ink=P["graphite"], night=P["graphite"], nightLine=P["rule"], starlight=P["chalk"],
         copper=P["signal"], copperInk=P["signalInk"], moss=P["fern"])

# ---------------------------------------------------------------- fonts (OFL)
FONTS = {
    # key: (file, variation axes or None). All SIL Open Font License 1.1 (IBM Plex: github.com/IBM/plex).
    "serif-semi":  ("IBM Plex Serif/IBMPlexSerif-SemiBold.ttf", None),     # wordmark
    "serif":       ("IBM Plex Serif/IBMPlexSerif-Regular.ttf", None),
    "serif-it":    ("IBM Plex Serif/IBMPlexSerif-Italic.ttf", None),       # binomial names in captions
    "sans":        ("IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf", {"wght": 400, "wdth": 100}),
    "sans-semi":   ("IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf", {"wght": 600, "wdth": 100}),
    "mono":        ("IBM Plex Mono/IBMPlexMono-Regular.ttf", None),
    "mono-med":    ("IBM Plex Mono/IBMPlexMono-Medium.ttf", None),
}

@functools.lru_cache(None)
def _font(key):
    fn, axes = FONTS[key]
    src = os.path.join(GF, fn)
    if axes:
        tag = "_".join(f"{k}{v}" for k, v in axes.items())
        dst = os.path.join(CACHE, os.path.basename(fn).replace(".ttf", f"-{tag}.ttf"))
        if not os.path.exists(dst):
            f = instancer.instantiateVariableFont(TTFont(src), axes)
            f.save(dst)
        src = dst
    tt = TTFont(src)
    blob = hb.Blob.from_file_path(src)
    hbf = hb.Font(hb.Face(blob))
    return tt, hbf

def text_path(text, key, size, x=0, y=0, anchor="start", tracking=0.0, features=None):
    """Return (svg path d, width). tracking in em. Baseline at y."""
    tt, hbf = _font(key)
    upm = tt["head"].unitsPerEm
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf, features or {"kern": True, "liga": True})
    gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    s = size / upm
    pen_x = 0.0; parts = []
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        sp = SVGPathPen(gs)
        tp = TransformPen(sp, (s, 0, 0, -s, pen_x * s + pos.x_offset * s, -pos.y_offset * s))
        gs[name].draw(tp)
        parts.append((sp.getCommands()))
        pen_x += pos.x_advance + (tracking * upm if i < n - 1 else 0)
    width = pen_x * s
    dx = {"start": 0, "middle": -width / 2, "end": -width}[anchor]
    # bake translation
    d = " ".join(p for p in parts if p)
    return f'<path transform="translate({x+dx:.2f} {y:.2f})" d="{d}"/>', width

def T(text, key, size, x, y, fill, anchor="start", tracking=0.0, opacity=None, features=None):
    p, w = text_path(text, key, size, x, y, anchor, tracking, features)
    op = f' opacity="{opacity}"' if opacity is not None else ""
    return p.replace("<path ", f'<path fill="{fill}"{op} '), w

def svg(w, h, body, title, bg=None, extra_defs=""):
    bgr = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>\n<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original artwork, "Field Notes" concept. '
            f'Lettering: IBM Plex Serif, Sans and Mono (SIL Open Font License 1.1), converted to outlines. -->\n'
            f'<defs>{extra_defs}</defs>{bgr}{body}</svg>\n')

def write(name, content):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as fh:
        fh.write(content)
    return p

# ---------------------------------------------------------------- geometry helpers
def f2(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")

def poly(pts, close=False):
    d = "M" + " L".join(f"{f2(x)} {f2(y)}" for x, y in pts)
    return d + (" Z" if close else "")

def smooth(pts, close=False, t=0.5):
    """Catmull-Rom -> cubic bezier path through pts."""
    if close:
        P_ = [pts[-1]] + pts + pts[:2]
    else:
        P_ = [pts[0]] + pts + [pts[-1]]
    d = f"M{f2(pts[0][0])} {f2(pts[0][1])}"
    rng = len(pts) if close else len(pts) - 1
    for i in range(1, rng + 1):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f" C{f2(c1[0])} {f2(c1[1])} {f2(c2[0])} {f2(c2[1])} {f2(p2[0])} {f2(p2[1])}"
    return d + (" Z" if close else "")

def hatch_pattern(pid, spacing, angle, color, width, opacity=1.0):
    return (f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="{spacing}" height="{spacing}" '
            f'patternTransform="rotate({angle})"><line x1="0" y1="0" x2="0" y2="{spacing}" stroke="{color}" '
            f'stroke-width="{width}" stroke-opacity="{opacity}"/></pattern>')

# ---------------------------------------------------------------- leaf
def leaf(cx, cy, length, width, angle=0, n_veins=9, serrate=True, seed=3, ink="#16202A", green="#3D6B4A",
         wash="#A9BC9C", lw=1.0, pid="lh", petiole=0.18):
    """Pinnate leaf with lateral and tertiary veins. Base at (cx,cy), pointing along angle (deg, 0 = right)."""
    rnd = random.Random(seed)
    L, W = length, width
    def halfw(t):
        return W / 2 * (math.sin(math.pi * t ** 0.75)) ** 0.9
    def mid(t):
        return (t * L, 0.035 * L * math.sin(math.pi * t))
    N = 90
    up, dn = [], []
    teeth_n = n_veins * 3
    for i in range(N + 1):
        t = i / N
        mx, my = mid(t)
        w = halfw(t)
        if serrate and 0.06 < t < 0.97:
            ph = (t * teeth_n) % 1.0
            w *= 1 + 0.045 * (1 - ph) - 0.02
        up.append((mx, my - w)); dn.append((mx, my + w))
    outline = smooth(up + dn[::-1][1:-1], close=True, t=0.4)
    veins = []
    for k in range(n_veins):
        t0 = 0.08 + 0.80 * k / (n_veins - 1)
        for side in (-1, 1):
            t0j = t0 + rnd.uniform(-0.012, 0.012) + (0.03 if side > 0 else 0)
            mx, my = mid(t0j)
            t1 = min(t0j + 0.16 + 0.04 * (1 - t0j), 0.985)
            ex, ey = mid(t1); ex += 0; ey += side * halfw(t1) * 0.93
            c = (mx + (ex - mx) * 0.35, my + (ey - my) * 0.75)
            veins.append(f"M{f2(mx)} {f2(my)} Q{f2(c[0])} {f2(c[1])} {f2(ex)} {f2(ey)}")
            # tertiary veinlets
            for s_ in (0.45, 0.72):
                bx = mx + (ex - mx) * s_ ; by = my + (ey - my) * (s_ ** 0.8)
                tx = bx - L * 0.035; ty = by - side * W * 0.06
                veins.append(f"M{f2(bx)} {f2(by)} L{f2(tx)} {f2(ty)}")
    midrib = f"M{-petiole*L:.1f} {0.02*L:.1f} Q{-petiole*L*0.4:.1f} 0 0 0 " + smooth([mid(i / 20) for i in range(21)])[0:0]
    mr = smooth([( -petiole * L, 0.03 * L)] + [mid(i / 20) for i in range(20)], t=0.5)
    g = (f'<g transform="translate({f2(cx)} {f2(cy)}) rotate({angle})">'
         f'<clipPath id="{pid}c"><path d="{outline}"/></clipPath>'
         f'<path d="{outline}" fill="{wash}"/>'
         f'<g clip-path="url(#{pid}c)"><rect x="0" y="0" width="{L}" height="{W}" fill="url(#{pid})"/></g>'
         f'<path d="{" ".join(veins)}" fill="none" stroke="{green}" stroke-width="{lw*0.7:.2f}" stroke-linecap="round"/>'
         f'<path d="{mr}" fill="none" stroke="{ink}" stroke-width="{lw*1.5:.2f}" stroke-linecap="round"/>'
         f'<path d="{outline}" fill="none" stroke="{ink}" stroke-width="{lw:.2f}" stroke-linejoin="round"/>'
         f'</g>')
    defs = hatch_pattern(pid, 3.2 * lw + 1.2, 35, green, 0.55 * lw, 0.55)
    return g, defs

# ---------------------------------------------------------------- moth wing (fore + hind)
def moth_wing(x, y, s=1.0, ink="#16202A", copper="#E2662A", wash="#E7DDC6", green="#3D6B4A", lw=1.0, pid="mw", mirror=False):
    """A single moth's right wing pair, base at (x,y). Scale s ~ 1 => ~170 px wide."""
    fw = [(0, 0), (40, -34), (95, -62), (150, -78), (172, -72), (168, -48), (150, -20), (118, 2), (70, 10), (25, 8)]
    hw = [(6, 6), (50, 12), (98, 22), (124, 46), (116, 82), (84, 104), (46, 98), (18, 64), (4, 30)]
    fo = smooth(fw, close=True, t=0.55); ho = smooth(hw, close=True, t=0.6)
    # veins: radiate from base to margin points
    fv = []
    base = (6, 0)
    for mx, my in [(150, -76), (168, -66), (170, -52), (160, -34), (142, -14), (118, 2)]:
        cxm = base[0] + (mx - base[0]) * 0.45; cym = base[1] + (my - base[1]) * 0.25
        fv.append(f"M{base[0]} {base[1]} Q{f2(cxm)} {f2(cym)} {mx} {my}")
    fv.append("M8 -2 Q60 -30 140 -72")  # costal vein
    hv = []
    hb_ = (8, 8)
    for mx, my in [(110, 32), (120, 56), (110, 84), (86, 101), (56, 98), (30, 78)]:
        cxm = hb_[0] + (mx - hb_[0]) * 0.5; cym = hb_[1] + (my - hb_[1]) * 0.3
        hv.append(f"M{hb_[0]} {hb_[1]} Q{f2(cxm)} {f2(cym)} {mx} {my}")
    # discal cell crossbar + eyespot
    cross = "M70 -18 Q84 -10 92 -2"
    eye = (f'<circle cx="74" cy="56" r="15" fill="none" stroke="{ink}" stroke-width="{lw:.2f}"/>'
           f'<circle cx="74" cy="56" r="10" fill="{copper}"/>'
           f'<circle cx="74" cy="56" r="4.2" fill="{ink}"/>'
           f'<circle cx="71.5" cy="53.5" r="1.4" fill="{wash}"/>')
    band = smooth([(98, -70), (110, -46), (118, -22), (114, 0)], t=0.5)
    tr = f"translate({f2(x)} {f2(y)}) scale({-s if mirror else s} {s})"
    g = (f'<g transform="{tr}">'
         f'<clipPath id="{pid}c"><path d="{fo} {ho}"/></clipPath>'
         f'<path d="{ho}" fill="{wash}"/><path d="{fo}" fill="{wash}"/>'
         f'<g clip-path="url(#{pid}c)"><rect x="-10" y="-90" width="200" height="200" fill="url(#{pid})"/>'
         f'<path d="{band}" fill="none" stroke="{green}" stroke-width="{7*lw:.1f}" stroke-opacity="0.55" stroke-linecap="round"/></g>'
         f'<path d="{" ".join(fv)} {cross}" fill="none" stroke="{ink}" stroke-width="{lw*0.65:.2f}" stroke-linecap="round"/>'
         f'<path d="{" ".join(hv)}" fill="none" stroke="{ink}" stroke-width="{lw*0.65:.2f}" stroke-linecap="round"/>'
         f'{eye}'
         f'<path d="{ho}" fill="none" stroke="{ink}" stroke-width="{lw:.2f}"/>'
         f'<path d="{fo}" fill="none" stroke="{ink}" stroke-width="{lw:.2f}"/>'
         f'</g>')
    defs = hatch_pattern(pid, 3.6, -50, ink, 0.45, 0.35)
    return g, defs

# ---------------------------------------------------------------- car (side elevation, engraved)
CAR_BODY = ("M30 168 L27 142 C27 130 34 122 48 120 L96 113 C122 80 160 64 218 62 C268 62 300 76 330 102 "
            "L404 112 C432 116 448 124 452 140 L455 168 L420 168 A40 40 0 0 0 340 168 L150 168 A40 40 0 0 0 70 168 Z")
CAR_GLASS = "M108 113 C130 86 162 73 212 71 L212 113 Z M222 71 C262 71 290 82 312 104 L222 110 Z"

def car(x, y, s=1.0, ink="#16202A", copper="#E2662A", paper="#F3EDDF", green="#3D6B4A", lw=1.2, pid="car",
        crumple=True, wall=True, hatch=True):
    """Engraved side elevation. Native box ~ 0..530 x 60..210 (ground y=208)."""
    wheels = ""
    for wx in (110, 380):
        spokes = " ".join(f"M{wx + 10*math.cos(a):.1f} {168 + 10*math.sin(a):.1f} L{wx + 23*math.cos(a):.1f} {168 + 23*math.sin(a):.1f}"
                          for a in [i * math.pi / 5 for i in range(10)])
        wheels += (f'<circle cx="{wx}" cy="168" r="33" fill="{paper}" stroke="{ink}" stroke-width="{lw*1.4:.2f}"/>'
                   f'<circle cx="{wx}" cy="168" r="25" fill="none" stroke="{ink}" stroke-width="{lw*0.7:.2f}"/>'
                   f'<path d="{spokes}" stroke="{ink}" stroke-width="{lw*0.6:.2f}"/>'
                   f'<circle cx="{wx}" cy="168" r="6" fill="{ink}"/>')
    details = (f'<path d="M212 71 L212 162 M330 104 L334 160 M96 113 L100 160 M44 132 L452 136" fill="none" stroke="{ink}" stroke-width="{lw*0.7:.2f}"/>'
               f'<path d="M244 128 h20 M120 126 h20" stroke="{ink}" stroke-width="{lw*1.2:.2f}" stroke-linecap="round"/>'
               f'<path d="M436 124 l12 2 l1 7 l-11 -1 z" fill="{copper}" stroke="{ink}" stroke-width="{lw*0.5:.2f}"/>')
    hatchg = ""
    defs = hatch_pattern(pid + "h", 3.4, 0, ink, 0.55, 0.6) + hatch_pattern(pid + "g", 2.6, 60, ink, 0.45, 0.45)
    if hatch:
        hatchg = (f'<clipPath id="{pid}c"><path d="{CAR_BODY}"/></clipPath>'
                  f'<g clip-path="url(#{pid}c)"><rect x="20" y="142" width="440" height="30" fill="url(#{pid}h)"/></g>'
                  f'<path d="{CAR_GLASS}" fill="url(#{pid}g)"/>')
    crump = ""
    if crumple:
        # folded square tube: progressive folds (like Park 2022 US-2), drawn as an accordion
        xs = [455, 463, 471, 479, 487, 495, 503]
        top = []; bot = []
        for i, xx in enumerate(xs):
            top.append((xx, 118 if i % 2 == 0 else 108)); bot.append((xx, 162 if i % 2 == 0 else 172))
        crump = (f'<path d="{poly(top + bot[::-1], close=True)}" fill="{copper}" stroke="{ink}" stroke-width="{lw:.2f}" stroke-linejoin="round"/>'
                 + "".join(f'<path d="M{xx} {t[1]} L{xx} {b[1]}" stroke="{ink}" stroke-width="{lw*0.5:.2f}" opacity="0.8"/>' for xx, t, b in zip(xs[1:-1], top[1:-1], bot[1:-1])))
    wallg = ""
    if wall:
        hp = " ".join(f"M516 {yy} l10 -10" for yy in range(70, 212, 9))
        wallg = (f'<path d="M514 62 V208" stroke="{ink}" stroke-width="{lw*2.2:.2f}" stroke-linecap="round"/>'
                 f'<path d="{hp}" stroke="{ink}" stroke-width="{lw*0.6:.2f}"/>')
    ground = f'<path d="M10 208 H506" stroke="{ink}" stroke-width="{lw*0.8:.2f}"/>' + "".join(
        f'<path d="M{gx} 208 l-7 7" stroke="{ink}" stroke-width="{lw*0.5:.2f}"/>' for gx in range(20, 506, 12))
    g = (f'<g transform="translate({f2(x)} {f2(y)}) scale({s})">'
         f'{ground}<path d="{CAR_BODY}" fill="{paper}"/>{hatchg}'
         f'<path d="{CAR_BODY}" fill="none" stroke="{ink}" stroke-width="{lw*1.5:.2f}" stroke-linejoin="round"/>'
         f'<path d="{CAR_GLASS}" fill="none" stroke="{ink}" stroke-width="{lw*0.9:.2f}" stroke-linejoin="round"/>'
         f'{details}{wheels}{crump}{wallg}</g>')
    return g, defs

# ---------------------------------------------------------------- crushed tube specimen (P1a)
def tube(x, y, s=1.0, ink="#16202A", copper="#E2662A", paper="#F3EDDF", lw=1.1, folds=5, pid="tb"):
    """Square tube, 100 wide x 450 tall native units scaled (proportional to Park 2022 US-2, 100x100 mm x 450 mm),
    upper part folded progressively. Origin top-left of the undeformed tube."""
    w = 100; H = 450
    fold_h = 26  # visual only
    crushed = folds * fold_h
    top_y = 0 + (H - crushed - 220)  # crushed length shown as offset from original top
    left = []; right = []
    yy = 0
    pts_l = []; pts_r = []
    # folded section from y=0 down
    for i in range(folds * 2 + 1):
        dx = 12 if i % 2 else -0
        pts_l.append((-dx, i * fold_h / 2)); pts_r.append((w + dx, i * fold_h / 2))
    ybase = folds * fold_h
    pts_l.append((0, ybase + 200)); pts_r.append((w, ybase + 200))
    outline = poly(pts_l + pts_r[::-1], close=True)
    folds_lines = "".join(f'<path d="M{-12 if i%2 else 0} {i*fold_h/2} L{w + (12 if i%2 else 0)} {i*fold_h/2}" stroke="{ink}" stroke-width="{lw*0.6:.2f}"/>'
                          for i in range(1, folds * 2 + 1))
    defs = hatch_pattern(pid, 3.0, 0, ink, 0.5, 0.5)
    g = (f'<g transform="translate({f2(x)} {f2(y)}) scale({s})">'
         f'<path d="{outline}" fill="{paper}"/>'
         f'<rect x="70" y="{ybase}" width="30" height="200" fill="url(#{pid})"/>'
         f'<path d="{poly(pts_l[:-1] + pts_r[:-1][::-1], close=True)}" fill="{copper}" opacity="0.9"/>'
         f'{folds_lines}<path d="{outline}" fill="none" stroke="{ink}" stroke-width="{lw*1.3:.2f}" stroke-linejoin="round"/>'
         f'<path d="M70 {ybase} V{ybase+200}" stroke="{ink}" stroke-width="{lw*0.6:.2f}"/>'
         f'</g>')
    return g, defs, ybase + 200

# ---------------------------------------------------------------- stars
def stars(w, h, n, seed=7, color="#EDE6D3", maxr=1.8, avoid=None):
    rnd = random.Random(seed); out = []
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        if avoid and any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        r = maxr * rnd.random() ** 3.2 + 0.35
        op = 0.35 + 0.65 * rnd.random()
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{color}" opacity="{op:.2f}"/>')
    return "".join(out)

def star_glyph(x, y, r, color):
    """Atlas-style bright star: dot + 4 hairline rays."""
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<path d="M{x-r*3} {y} H{x+r*3} M{x} {y-r*3} V{y+r*3}" stroke="{color}" stroke-width="{r*0.35:.2f}" opacity="0.8"/>')

# ---------------------------------------------------------------- annotation
def leader(x1, y1, x2, y2, color, lw=0.8, dot=True):
    s = f'<path d="M{f2(x1)} {f2(y1)} L{f2(x2)} {f2(y2)}" stroke="{color}" stroke-width="{lw}" fill="none"/>'
    if dot:
        s += f'<circle cx="{f2(x1)}" cy="{f2(y1)}" r="{lw*2:.2f}" fill="{color}"/>'
    return s

def dim_line(x1, x2, y, color, lw=0.8, tick=5):
    return (f'<path d="M{f2(x1)} {f2(y)} H{f2(x2)} M{f2(x1)} {f2(y-tick)} V{f2(y+tick)} M{f2(x2)} {f2(y-tick)} V{f2(y+tick)}" stroke="{color}" stroke-width="{lw}"/>'
            f'<path d="M{f2(x1)} {f2(y)} l6 -2.5 v5 z M{f2(x2)} {f2(y)} l-6 -2.5 v5 z" fill="{color}"/>')
