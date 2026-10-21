# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio. Field Notes: wordmark, lockups, banners, social preview.
import sys
from fn_lib import *
from fn_mark import mark

def place_mark(x, y, size, theme="light", uid="pm"):
    return f'<g transform="translate({f2(x)} {f2(y)}) scale({size/256:.4f})">{mark(theme, "full", uid=uid)}</g>'

def frame(w, h, color, inset=14, gap=6, op=1.0):
    return (f'<rect x="{inset}" y="{inset}" width="{w-2*inset}" height="{h-2*inset}" fill="none" stroke="{color}" stroke-width="1.6" opacity="{op}"/>'
            f'<rect x="{inset+gap}" y="{inset+gap}" width="{w-2*(inset+gap)}" height="{h-2*(inset+gap)}" fill="none" stroke="{color}" stroke-width="0.6" opacity="{op}"/>')

def corner_ticks(w, h, color, inset=14, n=0):
    """ruler ticks along top & bottom frame edge, like a plate's measured border"""
    s = []
    for x in range(inset + 20, w - inset - 10, 10):
        l = 6 if (x - inset - 20) % 50 == 0 else 3
        s.append(f"M{x} {inset} v{l} M{x} {h-inset} v{-l}")
    return f'<path d="{" ".join(s)}" stroke="{color}" stroke-width="0.6"/>'

def graticule(w, h, color, step=40, op=0.5):
    s = " ".join([f"M{x} 0 V{h}" for x in range(0, w + 1, step)] + [f"M0 {y} H{w}" for y in range(0, h + 1, step)])
    return f'<path d="{s}" stroke="{color}" stroke-width="0.5" opacity="{op}"/>'

def paper_grain(w, h, uid, op=0.06):
    return (f'<filter id="{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4"/>'
            f'<feColorMatrix values="0 0 0 0 0.35  0 0 0 0 0.28  0 0 0 0 0.18  0 0 0 {op*8:.2f} 0"/></filter>',
            f'<rect width="{w}" height="{h}" filter="url(#{uid})" opacity="0.5"/>')

# ------------------------------------------------------------------ wordmark
def wordmark(color, size=120, x=0, y=0):
    return T("cargen", "garamond", size, x, y, color, tracking=0.005)

def build_wordmarks():
    p, w = wordmark(P["ink"], 120, 8, 104)
    W = int(w + 16)
    write("wordmark.svg", svg(W, 140, p, "cargen wordmark"))
    p, w = wordmark(P["starlight"], 120, 8, 104)
    write("wordmark-dark.svg", svg(W, 140, p, "cargen wordmark (on dark)", bg=P["night"]))
    return W

def lockup(theme="light", descriptor=True):
    ink = P["ink"] if theme == "light" else P["starlight"]
    sub = P["sepia"] if theme == "light" else "#B9B09C"
    acc = P["copperInk"] if theme == "light" else P["copper"]
    b = place_mark(20, 20, 200, theme, uid="lk" + theme)
    wm, w = wordmark(ink, 132, 248, 140)
    b += wm
    H = 240
    if descriptor:
        b += f'<path d="M252 166 H{248 + w:.0f}" stroke="{acc}" stroke-width="1.4"/>'
        t, _ = T("open-source car generation", "mono", 17, 253, 194, sub, tracking=0.06)
        b += t
    W = int(248 + w + 28)
    return W, H, b

def build_lockups():
    for theme in ("light", "dark"):
        W, H, b = lockup(theme)
        write(f"lockup{'-dark' if theme=='dark' else ''}.svg", svg(W, H, b, "cargen lockup", bg=None if theme == "light" else P["night"]))
    # stacked
    b = place_mark(80, 16, 200, "light", uid="lks")
    wm, w = wordmark(P["ink"], 104, 180, 316)
    wm, w = T("cargen", "garamond", 104, 180, 316, P["ink"], anchor="middle", tracking=0.005)
    b += wm
    t, _ = T("open-source car generation", "mono", 13, 180, 350, P["sepia"], anchor="middle", tracking=0.06)
    b += t
    write("lockup-stacked.svg", svg(360, 372, b, "cargen stacked lockup"))

if __name__ == "__main__":
    build_wordmarks(); build_lockups()
