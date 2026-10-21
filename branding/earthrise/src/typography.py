# SPDX-License-Identifier: MIT
"""Typography specimen sheet (typography/typography.svg). All fonts SIL OFL 1.1, outlined to paths."""
import os
from fontpath import text_path
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "typography")
os.makedirs(OUT, exist_ok=True)
NAVY, WHITE, MIST, GREEN, TEAL, AMBER, SLATE = "#0B1A2E", "#F4F7FB", "#9FB3C8", "#3DDC97", "#1FB5A8", "#F5A524", "#4A5D73"
W, H = 1280, 900
el = []
def t(s, font, size, x, y, col, wght=None, tr=0.0, op=1):
    d, w = text_path(s, font, size, x, y, wght=wght, tracking=tr); el.append(f'<path d="{d}" fill="{col}" opacity="{op}"/>'); return w
el.append(f'<rect width="{W}" height="{H}" fill="{NAVY}"/>')
el.append(f'<rect x="640" width="640" height="{H}" fill="{WHITE}"/>')
# left: dark
t("TYPOGRAPHY", "inter", 13, 56, 64, GREEN, 600, 0.18)
t("Sora", "sora", 96, 56, 170, WHITE, 430)
t("Wordmark and display. Weight 430, tracking -0.5 %.", "inter", 16, 56, 206, MIST, 400)
t("Axial crush of steel tubes", "sora", 40, 56, 290, WHITE, 400)
t("Crash, stiffness, aerodynamics", "sora", 28, 56, 336, MIST, 300)
t("Inter", "inter", 64, 56, 446, WHITE, 500)
t("Interface and body text. 400 body, 500-600 labels.", "inter", 16, 56, 480, MIST, 400)
for i, line in enumerate(["Every engineering number comes from a validated", "solver or a cited test. If it is not validated it is", "labelled as an unvalidated estimate."]):
    t(line, "inter", 19, 56, 530 + i * 30, WHITE, 400, op=.92)
t("IBM Plex Mono", "plexmono-med", 40, 56, 690, WHITE)
t("Numbers, units, data, code. Tabular figures.", "inter", 16, 56, 722, MIST, 400)
t("US-2  P_m 101.0 kN  peak 337.1 kN", "plexmono", 22, 56, 776, GREEN)
t("AJ84-S24  theory 35.68 kN  +1.13 %", "plexmono", 22, 56, 812, TEAL)
t("Sora, Inter and IBM Plex Mono: SIL Open Font License 1.1", "inter", 13, 56, 866, MIST, 400, op=.8)
# right: light, hierarchy sample
x = 696
t("HIERARCHY ON LIGHT", "inter", 13, x, 64, "#0E7C74", 600, 0.18)
t("H1  Sora 430 / 44", "plexmono", 13, x, 110, SLATE)
t("Truth layer", "sora", 44, x, 162, NAVY, 430)
t("H2  Sora 430 / 28", "plexmono", 13, x, 210, SLATE)
t("Published axial-crush tests", "sora", 28, x, 248, NAVY, 430)
t("Body  Inter 400 / 17, line 1.55", "plexmono", 13, x, 296, SLATE)
for i, line in enumerate(["We collected 48 published axial-crush tests on", "thin-walled steel tubes and checked each one", "against closed-form theory."]):
    t(line, "inter", 17, x, 330 + i * 26, NAVY, 400)
t("Label  Inter 600 / 12, +12 % tracking, caps", "plexmono", 13, x, 440, SLATE)
t("UNVALIDATED ESTIMATE", "inter", 12, x, 468, "#B4560F", 600, 0.12)
t("Data  IBM Plex Mono 400 / 15", "plexmono", 13, x, 516, SLATE)
rows = [("test", "P_m [kN]", "theory", "err"), ("PARK-US1", "60.6", "80.25", "+32.4 %"), ("AJ84-S34", "36.71", "36.06", "-1.8 %")]
for i, r in enumerate(rows):
    y = 552 + i * 30
    for j, c in enumerate(r):
        t(c, "plexmono-med" if i == 0 else "plexmono", 15, x + [0, 150, 270, 380][j], y, NAVY if i else SLATE)
    el.append(f'<rect x="{x}" y="{y+10}" width="500" height="1" fill="{NAVY}" opacity=".12"/>')
t("Aa", "sora", 150, x, 830, NAVY, 430)
t("Aa", "inter", 150, x + 230, 830, "#0E7C74", 400, op=1)
el.append(f'<circle cx="{x+520}" cy="{790}" r="9" fill="{AMBER}"/>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Earthrise typography">'
       f'<title>Earthrise typography</title><!-- SPDX-License-Identifier: MIT. Text outlined from Sora, Inter, IBM Plex Mono (SIL OFL 1.1). -->{"".join(el)}</svg>')
open(os.path.join(OUT, "typography.svg"), "w").write(svg)
