<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 galion-studio -->
# cargen brand concept: Strata

## Story
A thin-walled steel tube under axial impact folds into stacked lobes, and a crumple zone keeps the record of a crash as layers of metal. Rock does the same over millions of years. Compression buckles sediment into folds and kink bands, and a meteor strike shocks bedrock into new layers. It is one piece of physics, plastic buckling of layered material, at every scale from a 2.8 mm tube wall to a mountain range, and that is the nature the universe actually writes. The Strata mark is a single kink band: three layers run flat, are thrust up through a steep fold, then relax. The outer two light layers are the measured test corridor. The orange layer between them is the simulation, and it has to fold with the evidence and stay inside it. The social preview shows strata drawn under a real crash record: the digitized force-displacement curve of a published crush test (Park, Cho & Kim 2022, US-2). No data is changed and no simulated curve is shown, because none is validated yet.

Fit with the enterprise research (`branding/RESEARCH-enterprise.md`): it keeps the existing Forge codes (charcoal tile `#16202A`, orange `#F26B1D`, crumple-zone idea). The mark is one geometric sign, not a car picture. Imagery is only real data and geometry, with no scenery, glow or gradients. The colour rule doubles as the honesty layer: **orange = validated simulation, blue = physical test, grey/dashed = theory or unvalidated.** Decorative art never uses orange. The only orange outside a validated result is the middle band of the mark.

No tagline appears anywhere. Mate chooses it. `banner/templates/` and `social/templates/` hold a clearly marked empty slot (layout guides only, not for publishing).

## Files
| Deliverable | File(s) |
|---|---|
| Logo mark (tile) | `mark/cargen-strata-mark.svg` + `-1024/-512/-256/-180/-64.png` |
| 16-48 px mark (favicon) | `mark/cargen-strata-mark-small.svg` (16-unit grid, pixel-snapped flats, no relaxation slope) + `-48/-32/-16.png` |
| One-colour mark | `mark/cargen-strata-mark-mono-graphite.svg`, `-mono-limestone.svg` (bands knocked out) + `-512.png` |
| Glyph without tile | `mark/cargen-strata-glyph-on-light.svg`, `-glyph-on-dark.svg` + `-512.png` |
| Wordmark | `wordmark/cargen-wordmark-{light,dark}.svg` + `@2x.png` (light = ink for light grounds) |
| Lockups | `lockup/cargen-lockup-{light,dark}.svg`, `lockup/cargen-lockup-stacked-{light,dark}.svg` + `@2x.png` |
| Banners 1280x320 | `banner/cargen-banner-{dark,light}-1280x320.{svg,png}` |
| GitHub social preview 1280x640 | `social/cargen-social-preview-dark-1280x640.{svg,png}` (primary), `-light-` variant |
| Tagline-slot templates (not for publishing) | `banner/templates/*`, `social/templates/*` |
| Palette + WCAG | `palette/palette.{svg,png}`, `palette/contrast.md` |
| Typography | `typography/typography.{svg,png}` |
| Graph style | `graph/strata.mplstyle`, `graph/strata-dark.mplstyle`, `graph/render_parity.py`, `graph/crush-parity-strata-{light,dark}.png` |
| Sources | `src/build.py` (mark geometry, layouts, seeded strata), `src/sheets.py`, `src/palette.py`, `src/fontpath.py` (HarfBuzz-shaped text to outlines), `src/render.sh` (resvg) |

Rebuild from `branding/strata/`: `../../.venv/bin/python src/build.py && ../../.venv/bin/python src/sheets.py && src/render.sh && ../../.venv/bin/python graph/render_parity.py`. The output is deterministic. The banner strata use seed 1983 and the social strata seed 2022 (numpy `default_rng`), and a rebuild gives byte-identical SVGs.

## Palette
| Name | Hex | Use | Contrast |
|---|---|---|---|
| Basalt | `#0F1317` | deepest ground: dark banners, social | Limestone on it 16.1:1 |
| Graphite | `#16202A` | existing Forge tile; text on light | 14.2:1 on Limestone |
| Shale | `#2C3540` | strata lines, cards on dark | decorative |
| Fold Orange | `#F26B1D` | mark middle band; validated-simulation line on dark | 6.1:1 on Basalt; **2.6:1 on Limestone: never text or thin lines on light** |
| Oxide | `#B5470C` | orange text and lines on light | 4.7:1 on Limestone |
| Limestone | `#F2EEE6` | light ground; mark bands; text on dark | 16.1:1 on Basalt |
| Chalk | `#FBFAF7` | cards on Limestone, sheets | Graphite on it 15.8:1 |
| Glacier | `#2F5F8F` | physical-test data on light | 5.8:1 on Limestone |
| Ice | `#86AEDA` | physical-test data on dark | 8.1:1 on Basalt |
| Stone | `#5A6470` | secondary text on light | 5.2:1 on Limestone |
| Ash | `#8E97A1` | secondary text on dark | 6.3:1 on Basalt |
| Sediment | `#D9D2C5` | rules and strata lines on light | decorative only (1.3:1) |

Full table: `palette/contrast.md` (WCAG 2.1, computed in `src/sheets.py`).

## Typography (all SIL Open Font License 1.1)
- **Archivo** (Omnibus-Type), width 125 (Expanded), weight 700, tracking -1.2 %, lowercase: wordmark and display headings 28 px and up. The wordmark is outlined, so never retype it.
- **IBM Plex Sans** (IBM), 400 body / 600 headings and labels: UI, docs, slides.
- **IBM Plex Mono** (IBM), 400/500: every number, unit, provenance caption and code.
- Fallbacks (also OFL): Inter Tight 700, Inter, JetBrains Mono.
- All text in SVG masters is converted to paths, so no master depends on installed fonts.

## Usage
- **Lockup geometry:** the wordmark's x-height spans exactly the mark's left strata, from the top of the upper band to the bottom of the orange band, so the letters sit in the rock. The tile-to-text gap is 0.24 x tile height. Keep clear space of 0.25 x tile height on all sides.
- **Minimum sizes:** full mark 48 px; below that use `mark-small` (16-32 px); horizontal lockup 120 px wide.
- **Grounds:** the tile works on any ground. Use the glyph only where a tile would be redundant (inside a UI chrome that is already Graphite). Use the mono marks for single-colour print, embossing and partner logo walls.
- **Generative strata:** they sit behind and to the right of the lockup, fade out before it and stay low-contrast (Shale or Sediment lines). The kink band in the banner uses the same deformation as the mark.
- **Graphs:** `plt.style.use(["branding/strata/graph/strata.mplstyle"])`, adding `strata-dark.mplstyle` for dark. The ±10 % band is drawn as a corridor (two thin walls plus a faint fill). Measured data is blue and theory is a dashed ink line. Add a mono status chip ("published tests vs theory", "validated simulation", or "unvalidated estimate"). Orange enters a graph only for a validated simulation curve.

## Do
- Keep layouts mostly Basalt/Graphite and Limestone; colour is one band or one line.
- Use real data as imagery (force curves, meshes, deformation sequences) with a Plex Mono source caption.
- Show numbers with units, source and status.

## Don't
- Don't use orange for decoration, for test data, or for an unvalidated estimate.
- Don't add gradients, glows, starfields, cracks or explosion effects to the mark. The aggression is in the geometry, not effects.
- Don't rotate, flip, re-space or outline the bands. The thrust always rises left to right.
- Don't place the lockup over dense strata or a busy photo.
- Don't put taglines or slogans in any asset. Don't publish the tagline-slot templates.
- Don't retype the wordmark in a live font.

## Credits and rules
Original artwork generated from code in `src/`. No stock imagery and no trademarks. The force curve in the social preview is `forge/data/p1a/park2022_us2_fig3_digitized.csv` (Park, Cho & Kim 2022, *Materials* 15:2107, CC BY 4.0, digitized Fig. 3), read only and not altered. The graph re-render reads `data/crush-theory-check.csv` and keeps the data, axes and caption text of `scripts/crush_plots.py`. Fonts are Archivo, IBM Plex Sans and IBM Plex Mono (OFL 1.1), embedded only as outlines. For matplotlib, static Plex weights are cut into a temp folder at run time. Nothing outside `branding/strata/` was edited.
