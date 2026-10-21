# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio. Field Notes: wordmark, lockups, banners, social preview, templates.
"""All layouts are generated from fn_lib primitives and fn_mark. Seeds are fixed, so output is
deterministic. No tagline appears anywhere: templates/ carries a marked, empty slot for the one
Mate chooses, and an evidence-plate template whose fields are placeholders."""
from fn_lib import *
from fn_mark import mark

WM_FONT = "serif-semi"     # IBM Plex Serif SemiBold, OFL
WM_TRACK = -0.01           # -1 % tracking
XH = 0.261                 # half the x-height of IBM Plex Serif (0.522 em)

THEME = {
    "light": dict(bg=P["paper"], ink=P["graphite"], sub=P["sepia"], acc=P["signalInk"], line=P["graphite"],
                  wash=P["sage"], green=P["fern"], test=P["cyan"], panel=P["vellum"]),
    "dark":  dict(bg=P["graphite"], ink=P["chalk"], sub=P["dust"], acc=P["signal"], line=P["chalk"],
                  wash="#2E4A3A", green=P["lichen"], test=P["cyanPale"], panel="#1E2A35"),
}

def place_mark(x, y, size, theme="graphite", uid="pm"):
    return f'<g transform="translate({f2(x)} {f2(y)}) scale({size/256:.4f})">{mark(theme, uid=uid)}</g>'

def wordmark(color, size, x, y, anchor="start"):
    return T("cargen", WM_FONT, size, x, y, color, anchor=anchor, tracking=WM_TRACK)

# ------------------------------------------------------------------ drawing-sheet furniture
def frame(w, h, color, inset=16, op=0.9):
    return f'<rect x="{inset}" y="{inset}" width="{w-2*inset}" height="{h-2*inset}" fill="none" stroke="{color}" stroke-width="1.2" opacity="{op}"/>'

def ruler(w, h, color, inset=16, op=0.6):
    """measured border: a tick every 10 px, long every 50 px, on the top and bottom rule"""
    s = []
    for x in range(inset + 10, w - inset - 5, 10):
        l = 7 if (x - inset) % 50 == 0 else 3.5
        s.append(f"M{x} {inset} v{l} M{x} {h-inset} v{-l}")
    return f'<path d="{" ".join(s)}" stroke="{color}" stroke-width="0.7" opacity="{op}"/>'

def graticule(w, h, color, step=40, inset=16, x0=None):
    """measuring grid; x0 limits it to the plate side so it never runs behind the lockup"""
    x0 = x0 if x0 is not None else inset
    s = " ".join([f"M{x} {inset} V{h-inset}" for x in range(x0 + step, w - inset, step)] +
                 [f"M{x0} {y} H{w-inset}" for y in range(inset + step, h - inset, step)])
    return f'<path d="{s}" stroke="{color}" stroke-width="0.7"/>'

def caption(parts, x, y, size, anchor="start"):
    """parts = [(text, font key, colour)], set on one baseline. 'Fig. n' in Plex Mono, Latin names in Plex Serif Italic."""
    widths = []
    for txt, key, col in parts:
        _, w = text_path(txt, key, size, 0, 0, tracking=0.01)
        widths.append(w)
    total = sum(widths) + 0.6 * size * (len(parts) - 1)
    cx = {"start": x, "middle": x - total / 2, "end": x - total}[anchor]
    out = ""
    for (txt, key, col), w in zip(parts, widths):
        t, _ = T(txt, key, size, cx, y, col, tracking=0.01)
        out += t; cx += w + 0.6 * size
    return out

# ------------------------------------------------------------------ figures
def fig_leaf(t, x, y, L, uid):
    """Carpinus betulus leaf, base at (x,y)."""
    return leaf(x, y, L, L * 0.42, angle=-22, n_veins=11, seed=5, ink=t["line"], green=t["green"],
                wash=t["wash"], lw=1.05, pid=uid, petiole=0.14)

def fig_car(t, x, y, s, uid):
    return car(x, y, s, ink=t["line"], copper=P["signal"], paper=t["bg"], lw=1.25, pid=uid)

def fig_tube(t, x, y, s, uid):
    """Park 2022 US-2 tube; folds in cyanotype blue because it is a physical test."""
    g, d, h = tube(x, y, s, ink=t["line"], copper=t["test"], paper=t["bg"], pid=uid)
    return g, d, h

# ------------------------------------------------------------------ wordmark + lockups
def build_wordmarks():
    for th, col, bg in (("light", P["graphite"], None), ("dark", P["chalk"], P["graphite"]), ("signal", P["signalInk"], None)):
        p, w = wordmark(col, 120, 12, 104)
        write(f"wordmark/cargen-wordmark-{th}.svg", svg(int(w + 24), 140, p, f"cargen wordmark ({th})", bg=bg))

def lockup_h(th):
    t = THEME[th]
    M, pad, size = 200, 20, 120
    gap = 0.17 * M
    b = place_mark(pad, pad, M, uid="lh" + th)
    wm, w = wordmark(t["ink"], size, pad + M + gap, pad + M / 2 + XH * size)
    b += wm
    return int(pad + M + gap + w + pad + 4), int(M + 2 * pad), b

def lockup_v(th):
    t = THEME[th]
    M, size, pad = 200, 100, 24
    _, w = wordmark(t["ink"], size, 0, 0)
    W = int(max(M, w) + 2 * pad + 20)
    b = place_mark((W - M) / 2, pad, M, uid="lv" + th)
    base = pad + M + 0.2 * size + 0.534 * size   # 0.2 em gap above the x-height ascender of 'g'
    wm, _ = wordmark(t["ink"], size, W / 2, base, anchor="middle")
    b += wm
    return W, int(base + 0.212 * size + pad), b

def build_lockups():
    for th in ("light", "dark"):
        bg = None if th == "light" else P["graphite"]
        W, H, b = lockup_h(th)
        write(f"lockup/cargen-lockup-{th}.svg", svg(W, H, b, f"cargen lockup ({th})", bg=bg))
        W, H, b = lockup_v(th)
        write(f"lockup/cargen-lockup-stacked-{th}.svg", svg(W, H, b, f"cargen stacked lockup ({th})", bg=bg))

# ------------------------------------------------------------------ banners 1280x320
def banner(th, slot=False):
    t = THEME[th]; W, H = 1280, 320
    defs = ""; b = ""
    if th == "dark":
        b += graticule(W, H, P["rule"], step=40, x0=712)
    b += frame(W, H, t["line"]) + ruler(W, H, t["line"])
    # lockup, left
    M = 184; mx, my = 60, (H - M) / 2
    b += place_mark(mx, my, M, uid="bm" + th)
    size = 112
    base = my + M / 2 + XH * size
    wm, w = wordmark(t["ink"], size, mx + M + 34, base)
    b += wm
    if slot:
        sx, sy = mx + M + 38, base + 0.212 * size + 18
        b += f'<rect x="{sx}" y="{sy:.1f}" width="{w-8:.0f}" height="30" fill="none" stroke="{t["acc"]}" stroke-width="1.2" stroke-dasharray="5 4"/>'
        c, _ = T("TAGLINE SLOT: EMPTY, MATE CHOOSES", "mono-med", 11, sx + 10, sy + 19.5, t["acc"], tracking=0.06)
        b += c
    # gutter: plate starts here
    gx = 712
    b += f'<path d="M{gx} 44 V276" stroke="{t["line"]}" stroke-width="0.8" opacity="0.55"/>'
    # Fig. 1 leaf, Fig. 2 car on a rigid barrier
    g, d = fig_leaf(t, 752, 176, 146, "bl" + th); b += g; defs += d
    g, d = fig_car(t, 904, 160 - 138.5 * 0.6, 0.6, "bc" + th); b += g; defs += d
    b += caption([("Fig. 1", "mono", t["sub"]), ("Carpinus betulus", "serif-it", t["sub"])], 752, 262, 13)
    b += caption([("Fig. 2", "mono", t["sub"]), ("crush zone (drawing)", "mono", t["sub"])], 1224, 262, 13, anchor="end")
    title = f"cargen banner ({th})" + (", tagline-slot layout guide, not for publishing" if slot else "")
    return svg(W, H, b, title, bg=t["bg"], extra_defs=defs)

def build_banners():
    for th in ("light", "dark"):
        write(f"banner/cargen-banner-{th}-1280x320.svg", banner(th))
        write(f"banner/templates/cargen-banner-{th}-tagline-slot.svg", banner(th, slot=True))

# ------------------------------------------------------------------ social preview 1280x640
def social():
    th = "light"; t = THEME[th]; W, H = 1280, 640
    defs = ""; b = ""
    b += frame(W, H, t["line"], inset=20) + ruler(W, H, t["line"], inset=20)
    M, size, gap = 224, 150, 40
    _, w = wordmark(t["ink"], size, 0, 0)
    mx = (W - (M + gap + w)) / 2; my = 62
    b += place_mark(mx, my, M, uid="sm")
    wm, _ = wordmark(t["ink"], size, mx + M + gap, my + M / 2 + XH * size)
    b += wm
    b += f'<path d="M64 336 H1216" stroke="{t["line"]}" stroke-width="0.8" opacity="0.6"/>'
    # Fig. 1 leaf
    g, d = fig_leaf(t, 104, 498, 250, "slf"); b += g; defs += d
    # Fig. 2 tube US-2 with the measured values (README; Park et al. 2022, Table 4)
    ts = 0.5; tx0 = 470 - 50 * ts; ty0 = 380
    g, d, th_ = fig_tube(t, tx0, ty0, ts, "stb"); b += g; defs += d
    tb = ty0 + th_ * ts
    b += f'<path d="M{tx0-14} {tb} H{tx0+100*ts+14}" stroke="{t["line"]}" stroke-width="1"/>'
    b += "".join(f'<path d="M{x} {tb} l-5 5.5" stroke="{t["line"]}" stroke-width="0.7"/>' for x in range(int(tx0 - 6), int(tx0 + 100 * ts + 14), 7))
    b += leader(tx0 + 100 * ts + 6, ty0 + 30, 546, ty0 + 30, t["test"], lw=0.9)
    for i, (line, col) in enumerate((("100 × 100 × 2.8 mm", t["sub"]), ("A500 steel, 450 mm", t["sub"]),
                                     ("Pm 101.0 kN, measured", t["test"]))):
        c, _ = T(line, "mono-med" if i == 2 else "mono", 13, 554, ty0 + 34 + i * 19, col, tracking=0.01)
        b += c
    # Fig. 3 car
    cs = 0.8
    g, d = fig_car(t, 745, 548 - 208 * cs, cs, "scar"); b += g; defs += d
    b += caption([("Fig. 1", "mono", t["sub"]), ("Carpinus betulus", "serif-it", t["sub"])], 64, 592, 15)
    b += caption([("Fig. 2", "mono", t["sub"]), ("tube US-2, Park et al. 2022", "mono", t["sub"])], 430, 592, 15)
    b += caption([("Fig. 3", "mono", t["sub"]), ("crush zone (drawing)", "mono", t["sub"])], 1216, 592, 15, anchor="end")
    return svg(W, H, b, "cargen social preview", bg=t["bg"], extra_defs=defs)

def build_social():
    write("social/cargen-social-preview-1280x640.svg", social())

# ------------------------------------------------------------------ evidence plate template
def evidence_plate(th):
    """1200x800 template: figure area + Plex Mono caption block. Every field is a marked placeholder."""
    t = THEME[th]; W, H = 1200, 800
    b = frame(W, H, t["line"], inset=16) + ruler(W, H, t["line"], inset=16)
    b += place_mark(40, 36, 56, uid="ep" + th)
    c, _ = T("PLATE ##", "mono-med", 14, 112, 60, t["ink"], tracking=0.08); b += c
    c, _ = T("cargen  /  validation", "mono", 14, 112, 82, t["sub"], tracking=0.02); b += c
    # figure area
    b += f'<rect x="40" y="112" width="1120" height="440" fill="{t["panel"]}"/>'
    c, _ = T("FIGURE AREA: graph or solver output, styled with graph/fieldnotes.mplstyle", "mono", 14, 600, 338, t["sub"], anchor="middle"); b += c
    # caption block (title block of a drawing sheet)
    y0 = 576
    b += f'<rect x="40" y="{y0}" width="1120" height="148" fill="none" stroke="{t["line"]}" stroke-width="1"/>'
    b += f'<path d="M40 {y0+37} H1160 M40 {y0+74} H1160 M40 {y0+111} H1160 M240 {y0} V{y0+148}" stroke="{t["line"]}" stroke-width="0.6" opacity="0.7"/>'
    rows = [("SOURCE", "test or paper, with DOI and table / figure number"),
            ("SOLVER", "name + pinned version, or 'none: published test'"),
            ("MESH", "element type, size, count"),
            ("ERROR VS TEST", "ISO/TS 18571 score + peak / mean error, or the label 'unvalidated estimate'")]
    for i, (k, v) in enumerate(rows):
        yy = y0 + 24 + i * 37
        c, _ = T(k, "mono-med", 12.5, 56, yy, t["ink"], tracking=0.06); b += c
        c, _ = T("[" + v + "]", "mono", 12.5, 256, yy, t["sub"]); b += c
    # colour key
    kx = 40; ky = 758
    for col, lab, dash in ((t["test"], "physical test", None), (P["signal"] if th == "dark" else P["signalInk"], "validated simulation", None),
                           (t["sub"], "unvalidated / pending", "6 4")):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        b += f'<path d="M{kx} {ky-4} h28" stroke="{col}" stroke-width="2.4"{da}/>'
        c, w = T(lab, "mono", 12, kx + 36, ky, t["sub"]); b += c
        kx += 36 + w + 34
    return svg(W, H, b, f"cargen evidence plate template ({th})", bg=t["bg"])

def build_templates():
    for th in ("light", "dark"):
        write(f"templates/cargen-evidence-plate-{th}.svg", evidence_plate(th))

if __name__ == "__main__":
    build_wordmarks(); build_lockups(); build_banners(); build_social(); build_templates()
