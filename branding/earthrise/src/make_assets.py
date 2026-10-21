# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Generates every Earthrise SVG master. Deterministic (seeded). Run render.sh afterwards for PNGs.
Fonts: Sora (wordmark) and Inter (descriptor), both SIL OFL 1.1, converted to outlines."""
import math, os, random
from mark import (NAVY, WHITE, GREEN, TEAL, AMBER, mark_group, defs as mark_defs, tile_svg, GY as MARK_GY, star)
from fontpath import text_path, x_height

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = "<!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original artwork (Earthrise concept). Letters are outlines of Sora / Inter, SIL OFL 1.1. -->"
DEEP = "#060F1D"      # deepest space, top of night sky
NAVY2 = "#12304A"     # horizon navy
TEAL_D = "#0E7C74"    # deep teal for text/lines on light
MIST = "#9FB3C8"      # secondary text on dark
SLATE = "#4A5D73"     # secondary text on light
DAWN = "#F4F7FB"
WORD = dict(name="sora", wght=430, tracking=-0.005)

def svg(w, h, body, title, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{HDR}<defs>{mark_defs()}{defs}</defs>{body}</svg>\n')

def save(rel, s):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(s); return p

def tile(x, y, size, small=False):
    k = size / 256
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f})"><rect x="8" y="8" width="240" height="240" rx="56" fill="url(#er-tile)"/>'
            f'<rect x="8.5" y="8.5" width="239" height="239" rx="55.5" fill="none" stroke="{WHITE}" stroke-opacity=".08"/>'
            f'<g transform="translate(0 {2 if small else 0})">{mark_group(small)}</g></g>')

def wordmark(x, baseline, size, color, anchor="start"):
    d, w = text_path("cargen", WORD["name"], size, x, baseline, wght=WORD["wght"], tracking=WORD["tracking"], anchor=anchor)
    return f'<path d="{d}" fill="{color}"/>', w

def lockup(x, y, h, color):
    """Horizontal lockup: tile of height h, wordmark baseline on the car's ground line."""
    t = tile(x, y, h)
    size = h * 0.62
    base = y + (MARK_GY + 13) / 256 * h      # bottom of the wheels = letters' baseline
    wm, w = wordmark(x + h * 1.16, base, size, color)
    return t + wm, h * 1.16 + w

# ---------- generative nature/sky pieces ----------
def stars(rng, w, h, n, avoid=None, col=WHITE, ymax=None, big=0.06):
    out = []
    ymax = ymax or h
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, ymax) ** 1.0
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        r = rng.choice([0.6, 0.7, 0.8, 0.9, 1.0, 1.2]) if rng.random() > big else rng.uniform(1.4, 1.9)
        op = rng.uniform(0.25, 0.9) * (1 - 0.6 * y / h)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" opacity="{op:.2f}"/>')
    return "".join(out)

def forest(rng, w, base, hmin, hmax, step, color, op=1.0, jitter=0.5):
    """Conifer tree-line silhouette as one path; trees are slim tiered spires."""
    pts = [(0, base + 40)]
    x = -step
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    def field(x):
        return 0.5 + 0.28 * math.sin(x / 97 + ph[0]) + 0.22 * math.sin(x / 41 + ph[1])
    while x < w + step:
        f = field(x)
        h = hmin + (hmax - hmin) * min(1, max(0, f + rng.uniform(-0.25, 0.25)))
        tw = h * rng.uniform(0.28, 0.36)
        cx = x + rng.uniform(-jitter, jitter) * step
        top = base - h
        tiers = 3
        pts.append((cx - tw / 2, base))
        for i in range(tiers):           # left side, stepping up with small shelves
            f0 = i / tiers; f1 = (i + 1) / tiers
            yl = base - h * (0.18 + 0.82 * f1) + h * 0.06
            pts.append((cx - tw / 2 * (1 - f0 * 0.9), base - h * 0.18 - h * 0.82 * f0))
            pts.append((cx - tw / 2 * (1 - f1) * 0.62, yl))
        pts.append((cx, top))
        for i in reversed(range(tiers)):
            f0 = i / tiers; f1 = (i + 1) / tiers
            yl = base - h * (0.18 + 0.82 * f1) + h * 0.06
            pts.append((cx + tw / 2 * (1 - f1) * 0.62, yl))
            pts.append((cx + tw / 2 * (1 - f0 * 0.9), base - h * 0.18 - h * 0.82 * f0))
        pts.append((cx + tw / 2, base))
        x += step * rng.uniform(0.6, 1.25) * (1.6 if f < 0.3 else 1.0)
    pts.append((w, base + 40))
    d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'

def ridge(rng, w, base, amp, color, op=1.0, n=7):
    """Soft far hills under the tree line."""
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    pts = []
    for i in range(0, w + 11, 10):
        y = base - amp * (0.5 + 0.3 * math.sin(i / w * n + ph[0]) + 0.2 * math.sin(i / w * n * 2.3 + ph[1]))
        pts.append((i, y))
    d = f"M0 {base+60} " + " ".join(f"L{a:.1f} {b:.1f}" for a, b in pts) + f" L{w} {base+60} Z"
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'

def aurora(rng, w, x0, x1, base, height, col_lo, col_hi, op, uid, waves=(2.2, 5.1), rays=True, blur=3):
    """An aurora curtain: a soft ribbon plus fine vertical rays, fading upwards."""
    ph = [rng.uniform(0, 6.28) for _ in range(4)]
    def yb(x):
        t = (x - x0) / (x1 - x0)
        return base + 14 * math.sin(t * waves[0] * math.pi + ph[0]) + 6 * math.sin(t * waves[1] * math.pi + ph[1])
    def env(x):
        t = (x - x0) / (x1 - x0)
        return max(0.0, math.sin(math.pi * t)) ** 1.7 * (0.75 + 0.25 * math.sin(t * 7 + ph[2]))
    xs = [x0 + (x1 - x0) * i / 160 for i in range(161)]
    top = [(x, yb(x) - height * env(x)) for x in xs]
    bot = [(x, yb(x)) for x in xs]
    d = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in bot) + " L" + " L".join(f"{a:.1f} {b:.1f}" for a, b in reversed(top)) + " Z"
    g = (f'<linearGradient id="au-{uid}" x1="0" y1="1" x2="0" y2="0" gradientUnits="objectBoundingBox">'
         f'<stop offset="0" stop-color="{col_lo}" stop-opacity="0"/><stop offset=".08" stop-color="{col_lo}" stop-opacity="1"/>'
         f'<stop offset=".45" stop-color="{col_hi}" stop-opacity=".55"/><stop offset="1" stop-color="{col_hi}" stop-opacity="0"/></linearGradient>'
         f'<filter id="bl-{uid}" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="{blur}"/></filter>')
    out = [f'<path d="{d}" fill="url(#au-{uid})" opacity="{op}" filter="url(#bl-{uid})"/>']
    if rays:
        r = []
        x = x0
        while x < x1:
            e = env(x)
            if e > 0.05:
                hgt = height * e * rng.uniform(0.55, 1.05)
                r.append(f'<rect x="{x:.1f}" y="{yb(x)-hgt:.1f}" width="1.2" height="{hgt:.1f}" opacity="{rng.uniform(.15,.55)*e:.2f}"/>')
            x += rng.uniform(2.0, 5.0)
        g += (f'<linearGradient id="ray-{uid}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{col_lo}" stop-opacity="0"/>'
              f'<stop offset=".1" stop-color="{col_lo}"/><stop offset=".6" stop-color="{col_hi}" stop-opacity=".4"/><stop offset="1" stop-color="{col_hi}" stop-opacity="0"/></linearGradient>')
        out.append(f'<g fill="url(#ray-{uid})" opacity="{op}">' + "".join(r) + '</g>')
    return "".join(out), g

def descriptor(x, baseline, size, color, text="open-source car generation", anchor="start", tracking=0.06):
    d, w = text_path(text, "inter", size, x, baseline, wght=450, tracking=tracking, anchor=anchor)
    return f'<path d="{d}" fill="{color}"/>', w

# ---------- deliverables ----------
def make_marks():
    save("mark/cargen-earthrise-mark.svg", tile_svg(256, False, "cargen mark (Earthrise)"))
    save("mark/cargen-earthrise-mark-small.svg", tile_svg(256, True, "cargen mark, small sizes 16-48 px (Earthrise)"))
    # one-colour versions for print, embossing, engineering documents
    for name, fg, bg in (("mono-dark", WHITE, None), ("mono-light", NAVY, None)):
        g = mark_group(False, stars=False, body=fg, atm_grad=fg, sun=fg).replace('fill="url(#er-halo)"', 'fill="none"')
        save(f"mark/cargen-earthrise-glyph-{name}.svg", svg(256, 256, f'<g transform="translate(0 -6)">{g}</g>', f"cargen glyph, one colour ({name})"))
    # full-colour glyph without tile
    save("mark/cargen-earthrise-glyph.svg", svg(256, 256, f'<g transform="translate(0 -6)">{mark_group(False, stars=False)}</g>', "cargen glyph (Earthrise)"))
    g = mark_group(False, stars=False, body=NAVY)
    save("mark/cargen-earthrise-glyph-light.svg", svg(256, 256, f'<g transform="translate(0 -6)">{g}</g>', "cargen glyph for light backgrounds (Earthrise)"))

def make_wordmarks():
    for name, col, bg in (("dark", WHITE, NAVY), ("light", NAVY, None)):
        wm, w = wordmark(24, 112, 120, col)
        W = int(w + 48)
        save(f"wordmark/cargen-wordmark-{name}.svg", svg(W, 150, wm, f"cargen wordmark ({name} backgrounds)"))

def make_lockups():
    for name, col in (("dark", WHITE), ("light", NAVY)):
        lk, w = lockup(24, 24, 160, col)
        save(f"lockup/cargen-lockup-{name}.svg", svg(int(w + 56), 208, lk, f"cargen lockup ({name} backgrounds)"))
    # stacked lockup
    for name, col in (("dark", WHITE), ("light", NAVY)):
        t = tile(80, 22, 160)
        wm, w = wordmark(160, 262, 74, col, anchor="middle")
        save(f"lockup/cargen-lockup-stacked-{name}.svg", svg(320, 300, t + wm, f"cargen stacked lockup ({name} backgrounds)"))

def banner_dark(W=1280, H=320, seed=7):
    rng = random.Random(seed)
    defs = (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{DEEP}"/>'
            f'<stop offset=".55" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient>'
            f'<radialGradient id="dawn" cx="1040" cy="300" r="420" gradientUnits="userSpaceOnUse" gradientTransform="translate(1040 300) scale(1 .32) translate(-1040 -300)">'
            f'<stop offset="0" stop-color="{AMBER}" stop-opacity=".55"/><stop offset=".35" stop-color="{AMBER}" stop-opacity=".16"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>')
    a1, g1 = aurora(rng, W, 640, 1330, 222, 130, GREEN, TEAL, .6, "d1", blur=2.5)
    a2, g2 = aurora(rng, W, 760, 1280, 176, 90, TEAL, "#6FE7C8", .35, "d2", waves=(1.6, 4.3), blur=2)
    body = [f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
            stars(rng, W, H, 260, avoid=(40, 40, 700, 280), ymax=250),
            stars(rng, W, H, 30, ymax=250, big=0),
            a2, a1,
            f'<rect y="160" width="{W}" height="160" fill="url(#dawn)"/>',
            ridge(rng, W, 286, 30, "#0F2A40", 1),
            forest(rng, W, 300, 14, 44, 12, "#0A1D30", 1),
            forest(random.Random(3), W, 318, 18, 70, 15, "#050D18", 1)]
    lk, w = lockup(72, 64, 176, WHITE)
    body.append(lk)
    return svg(W, H, "".join(body), "cargen banner, dark", defs + g1 + g2)

def banner_light(W=1280, H=320, seed=11):
    rng = random.Random(seed)
    defs = (f'<linearGradient id="skyl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/>'
            f'<stop offset=".6" stop-color="{DAWN}"/><stop offset="1" stop-color="#E4F2EF"/></linearGradient>'
            f'<linearGradient id="orb" x1="600" y1="0" x2="1280" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset=".3" stop-color="{TEAL_D}"/><stop offset=".85" stop-color="{TEAL}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>'
            f'<radialGradient id="dawnl" cx="1040" cy="300" r="460" gradientUnits="userSpaceOnUse" gradientTransform="translate(1040 300) scale(1 .34) translate(-1040 -300)">'
            f'<stop offset="0" stop-color="{AMBER}" stop-opacity=".42"/><stop offset=".4" stop-color="#F8C977" stop-opacity=".14"/><stop offset="1" stop-color="#F8C977" stop-opacity="0"/></radialGradient>')
    # in daylight the aurora becomes orbital lines: thin concentric arcs of a planet whose limb crests on the right
    cx, cy, r0 = 1010, 1180, 1000
    orbits = []
    for i, (dr, op, sw) in enumerate(((0, .55, 1.6), (26, .35, 1.1), (54, .22, .9), (88, .14, .8))):
        r = r0 + dr
        a0, a1 = math.radians(118), math.radians(62)
        x0, y0 = cx + r * math.cos(a0), cy - r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
        orbits.append(f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="url(#orb)" stroke-opacity="{op*1.5:.2f}" stroke-width="{sw}" stroke-linecap="round"/>')
    body = [f'<rect width="{W}" height="{H}" fill="url(#skyl)"/>',
            f'<rect y="140" width="{W}" height="180" fill="url(#dawnl)"/>',
            "".join(orbits),
            stars(rng, W, H, 70, avoid=(40, 40, 700, 280), col="#5B7A93", ymax=200, big=0.0),
            ridge(rng, W, 288, 30, "#C9DDE0", 1),
            forest(rng, W, 302, 14, 44, 12, "#8FAAB5", 1),
            forest(random.Random(3), W, 318, 18, 68, 15, "#16324A", 1)]
    lk, w = lockup(72, 64, 176, NAVY)
    body.append(lk)
    return svg(W, H, "".join(body), "cargen banner, light", defs)

def constellation_car(x, y, s, col=WHITE):
    """Star nodes joined by thin lines tracing a car profile (the same profile as the mark)."""
    P = [(0, 54), (2, 30), (30, 14), (62, 2), (104, 0), (140, 12), (166, 30), (184, 36), (190, 50), (186, 58),
         (164, 58), (26, 58)]
    P = [(x + a * s, y + b * s) for a, b in P]
    lines = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in P[:10]) + f" L{P[10][0]:.1f} {P[10][1]:.1f} M{x+137*s:.1f} {y+58*s:.1f} L{x+53*s:.1f} {y+58*s:.1f} M{P[11][0]:.1f} {P[11][1]:.1f} L{P[0][0]:.1f} {P[0][1]:.1f}"
    out = [f'<path d="{lines}" fill="none" stroke="{col}" stroke-opacity=".28" stroke-width="1" stroke-linejoin="round"/>']
    for (cxw) in (40, 150):  # wheels: two small orbits
        wx, wy = x + cxw * s, y + 58 * s
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{13*s:.1f}" fill="none" stroke="{col}" stroke-opacity=".28" stroke-width="1"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="1.6" fill="{col}" opacity=".7"/>')
    for i, (a, b) in enumerate(P):
        rr = 2.6 if i in (3, 4, 7) else 1.7
        out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{rr}" fill="{col}" opacity=".9"/>')
        if i in (3, 7):
            out.append(star(a, b, 7, col, .9))
    return "".join(out)

def social(W=1280, H=640, seed=5):
    rng = random.Random(seed)
    pcx, pcy, pr = 640, 2440, 1960          # Earth from orbit: limb crest at y=480
    defs = (f'<radialGradient id="space" cx="640" cy="200" r="900" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#0E2238"/>'
            f'<stop offset="1" stop-color="{DEEP}"/></radialGradient>'
            f'<radialGradient id="planet" cx="{pcx}" cy="{pcy - pr}" r="700" gradientUnits="userSpaceOnUse" gradientTransform="translate({pcx} {pcy-pr}) scale(1.6 .5) translate({-pcx} {-(pcy-pr)})">'
            f'<stop offset="0" stop-color="#123A52"/><stop offset=".5" stop-color="#0B2236"/><stop offset="1" stop-color="#071424"/></radialGradient>'
            f'<filter id="glow" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>'
            f'<filter id="glow2" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>'
            f'<linearGradient id="limb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}" stop-opacity="0"/>'
            f'<stop offset=".3" stop-color="{TEAL}"/><stop offset=".62" stop-color="{GREEN}"/><stop offset=".8" stop-color="{AMBER}"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>'
            f'<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFF6E0"/><stop offset=".08" stop-color="{AMBER}" stop-opacity=".9"/>'
            f'<stop offset=".35" stop-color="{AMBER}" stop-opacity=".22"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>')
    a0, a1 = math.radians(128), math.radians(52)
    def ap(a, r): return pcx + r * math.cos(a), pcy - r * math.sin(a)
    x0, y0 = ap(a0, pr); x1, y1 = ap(a1, pr)
    limb = f"M{x0:.1f} {y0:.1f} A{pr} {pr} 0 0 1 {x1:.1f} {y1:.1f}"
    sa = math.radians(79); sx, sy = ap(sa, pr + 4)
    body = [f'<rect width="{W}" height="{H}" fill="url(#space)"/>',
            stars(rng, W, H, 420, avoid=(250, 170, 1030, 400), ymax=470),
            stars(rng, W, H, 40, ymax=460, big=0),
            constellation_car(890, 78, 1.45),
            f'<circle cx="{pcx}" cy="{pcy}" r="{pr}" fill="url(#planet)"/>',
            # thin atmosphere: a wide soft glow plus a crisp line
            f'<path d="{limb}" fill="none" stroke="url(#limb)" stroke-width="22" opacity=".45" filter="url(#glow)"/>',
            f'<path d="{limb}" fill="none" stroke="url(#limb)" stroke-width="5" opacity=".9" filter="url(#glow2)"/>',
            f'<path d="{limb}" fill="none" stroke="url(#limb)" stroke-width="1.6"/>',
            f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="300" ry="64" fill="url(#sun)"/>',
            f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="90" ry="22" fill="url(#sun)"/>',
            f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="3.2" fill="#FFF6E0"/>']
    # night-side city-free forest texture: faint tree line on the limb, nature seen from orbit
    lk, w = lockup(0, 0, 150, WHITE)
    lx = (W - w) / 2
    lk, w = lockup(lx, 196, 150, WHITE)
    body.append(lk)
    dsc, dw = descriptor(W / 2, 410, 25, MIST, anchor="middle")
    body.append(dsc)
    return svg(W, H, "".join(body), "cargen social preview", defs)

if __name__ == "__main__":
    make_marks(); make_wordmarks(); make_lockups()
    save("banner/cargen-banner-dark-1280x320.svg", banner_dark())
    save("banner/cargen-banner-light-1280x320.svg", banner_light())
    save("social/cargen-social-preview-1280x640.svg", social())
    print("ok")

def tagline_slot_template(src_svg, dark):
    """Same banner plus a dashed, labelled empty slot under the wordmark. Layout guide only; never ship it."""
    col = "#9FB3C8" if dark else "#4A5D73"
    x, y, w, h = 276, 228, 470, 28
    lab, _ = text_path("TAGLINE SLOT  (empty, Inter 450 / 22 px, to be decided)", "inter", 12, x + 14, y + 18.5, wght=500, tracking=0.08)
    g = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{col}" stroke-width="1.2" stroke-dasharray="6 5"/>'
         f'<path d="{lab}" fill="{col}"/>')
    return src_svg.replace("</svg>", g + "</svg>").replace('aria-label="cargen banner', 'aria-label="TEMPLATE cargen banner')

if __name__ == "__main__":
    save("banner/templates/cargen-banner-dark-tagline-slot.svg", tagline_slot_template(banner_dark(), True))
    save("banner/templates/cargen-banner-light-tagline-slot.svg", tagline_slot_template(banner_light(), False))
