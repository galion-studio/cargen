# SPDX-License-Identifier: MIT
"""Earthrise mark geometry. The car's roof and tail are one circular arc (a planet's limb);
a concentric arc is the thin atmosphere; the amber dot is the sun rising at the front."""
import math
NAVY="#0B1A2E"; WHITE="#F4F7FB"; GREEN="#3DDC97"; TEAL="#1FB5A8"; AMBER="#F5A524"
CX, CY, R = 116.0, 236.0, 130.0          # planet/roof circle
GY = 168.0                               # ground (bottom of body sill)
def P(a, r=R):
    return CX + r*math.cos(math.radians(a)), CY - r*math.sin(math.radians(a))
def arc(a0, a1, r=R, n=96):
    return [P(a0+(a1-a0)*i/n, r) for i in range(n+1)]
def L(pts): return " ".join(f"L{x:.2f} {y:.2f}" for x, y in pts)

def body_d(wheel_r=13, gap=4.5):
    a_tail = math.degrees(math.acos((40 - CX) / R))
    roof = arc(a_tail, 48)                # tail -> windshield top
    tx, ty = roof[0]; fx, fy = roof[-1]
    w1, w2 = 74.0, 186.0
    ro = wheel_r + gap
    d = f"M{tx+6:.2f} {GY:.2f} Q{tx:.2f} {GY:.2f} {tx:.2f} {GY-6:.2f} L{tx:.2f} {ty+14:.2f} Q{tx:.2f} {ty+3:.2f} {roof[7][0]:.2f} {roof[7][1]:.2f} " + L(roof[8:])
    d += f" C{fx+6:.2f} {fy+1.5:.2f} 210 {fy+3:.2f} 216 {fy+5:.2f}"
    d += f" C221 {fy+7:.2f} 223 {fy+11:.2f} 223 {fy+16:.2f} L223 {GY-6:.2f} Q223 {GY:.2f} 217 {GY:.2f}"
    d += f" L{w2+ro:.2f} {GY:.2f} A{ro} {ro} 0 0 0 {w2-ro:.2f} {GY:.2f}"
    d += f" L{w1+ro:.2f} {GY:.2f} A{ro} {ro} 0 0 0 {w1-ro:.2f} {GY:.2f} Z"
    return d, (w1, w2)

def mark_group(small=False, stars=True, body=WHITE, atm_grad="url(#er-aurora)", sun=AMBER):
    wr = 14 if small else 13
    d, (w1, w2) = body_d(wheel_r=wr, gap=6 if small else 4.5)
    sw = 12 if small else 7
    ra = R + (20 if small else 16)
    a0, a1 = (128, 54) if small else (134, 53)
    atm = arc(a0, a1, ra)
    sx, sy = P(a1, ra)
    ad = f"M{atm[0][0]:.2f} {atm[0][1]:.2f} " + L(atm[1:])
    sr = 11 if small else 8.5
    s = [f'<path d="{d}" fill="{body}"/>',
         f'<circle cx="{w1}" cy="{GY}" r="{wr}" fill="{body}"/>',
         f'<circle cx="{w2}" cy="{GY}" r="{wr}" fill="{body}"/>',
         f'<path d="{ad}" fill="none" stroke="{atm_grad}" stroke-width="{sw}" stroke-linecap="round"/>',
         f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{sr*2.6:.1f}" fill="url(#er-halo)"/>' if not small else '',
         f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{sr}" fill="{sun}"/>']
    if stars and not small:
        s.append(star(66, 66, 7, WHITE, .9)); s.append(star(96, 50, 3.4, WHITE, .5))
    return "\n".join(s)

def star(x, y, r, col, op=1):
    k = r*0.22
    return (f'<path d="M{x} {y-r} Q{x+k} {y-k} {x+r} {y} Q{x+k} {y+k} {x} {y+r} '
            f'Q{x-k} {y+k} {x-r} {y} Q{x-k} {y-k} {x} {y-r} Z" fill="{col}" opacity="{op}"/>')

def defs(prefix="er"):
    return (f'<linearGradient id="{prefix}-aurora" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{TEAL}" stop-opacity=".0"/><stop offset=".25" stop-color="{TEAL}"/>'
            f'<stop offset=".8" stop-color="{GREEN}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>'
            f'<radialGradient id="{prefix}-halo"><stop offset=".3" stop-color="{AMBER}" stop-opacity=".45"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="{prefix}-tile" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="#0B1A2E"/><stop offset="1" stop-color="#10304A"/></linearGradient>')

def tile_svg(size=256, small=False, title="cargen mark"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="{size}" height="{size}" role="img" aria-label="{title}">'
            f'<title>{title}</title><!-- SPDX-License-Identifier: MIT. Copyright (c) 2026 galion-studio. Original artwork. -->'
            f'<defs>{defs()}</defs><rect x="8" y="8" width="240" height="240" rx="56" fill="url(#er-tile)"/>'
            f'<g transform="translate(0 {2 if small else 0})">{mark_group(small)}</g></svg>')
if __name__ == "__main__":
    open("/tmp/m.svg","w").write(tile_svg())
    open("/tmp/ms.svg","w").write(tile_svg(small=True))
