<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 galion-studio -->
# cargen brand concept: Earthrise

## Story
Seen from orbit, the Earth's atmosphere is a line thinner than a fingernail on a globe, yet every car ever built has driven, crashed and been cooled inside it. Earthrise draws cargen from that point of view. The mark is a car whose roof and tail are one circular arc: a short piece of a planet's limb. Above it runs a second, concentric arc, the thin atmosphere that our aero work is limited to (air only), fading from teal into aurora green. Where it ends, a small amber sun rises over the bonnet. That amber is the only warm colour in the system and carries forward the orange of the current mark. Around the mark, the banners use generative night skies: aurora curtains, a seeded star field, and a conifer tree line on the horizon. The social preview shows the Earth's limb from orbit with a constellation that traces the same car profile. The language stays quiet and precise (navy, white, one line of colour, one sun), so it reads as engineering software first and as a nature story second. The arcs, horizon and constellation are drawn from geometry, as the truth layer is built from measurements.

No tagline appears anywhere. Mate chooses the tagline. `banner/templates/` holds a marked empty slot for it.

## Files
| Deliverable | File(s) |
|---|---|
| Logo mark (app tile) | `mark/cargen-earthrise-mark.svg` + `-512/-256/-64/-32.png` |
| Small-size mark (16-48 px, favicon) | `mark/cargen-earthrise-mark-small.svg` + `-48/-32/-16.png` (thicker atmosphere, bigger sun, no stars) |
| Glyph without tile | `mark/cargen-earthrise-glyph.svg` (dark bg), `-glyph-light.svg` (light bg), `-glyph-mono-dark.svg` / `-glyph-mono-light.svg` (one colour) + 512 px PNGs |
| Wordmark | `wordmark/cargen-wordmark-dark.svg` / `-light.svg` + `@2x.png` |
| Lockups | `lockup/cargen-lockup-{dark,light}.svg` (horizontal), `lockup/cargen-lockup-stacked-{dark,light}.svg` + `@2x.png` |
| Banners 1280x320 | `banner/cargen-banner-dark-1280x320.{svg,png}`, `banner/cargen-banner-light-1280x320.{svg,png}` |
| Tagline-slot layout guides (not for publishing) | `banner/templates/cargen-banner-{dark,light}-tagline-slot.{svg,png}` |
| GitHub social preview 1280x640 | `social/cargen-social-preview-1280x640.{svg,png}` |
| Palette + WCAG check | `palette/palette.{svg,png}`, `palette/contrast.md` |
| Typography | `typography/typography.{svg,png}` |
| Graph style | `graph/earthrise.mplstyle`, `graph/earthrise-dark.mplstyle`, `graph/render_parity.py`, `graph/crush-parity-earthrise-{light,dark}.png` |
| Sources | `src/mark.py` (mark geometry), `src/make_assets.py` (all layouts, seeded), `src/palette.py`, `src/typography.py`, `src/fontpath.py` (text to outlines), `src/render.sh` (resvg PNG export) |

To rebuild, run `.venv/bin/python src/make_assets.py && .venv/bin/python src/palette.py && .venv/bin/python src/typography.py && src/render.sh` from `branding/earthrise/` (with `.venv` = the repo venv), then run `graph/render_parity.py`. Output is deterministic because the random generators use fixed seeds.

## Palette
| Name | Hex | Use |
|---|---|---|
| Deep Space | `#060F1D` | night-sky top, deepest background |
| Space Navy | `#0B1A2E` | primary dark; text on light (16.3:1 on Star White) |
| Horizon Navy | `#12304A` | sky at the horizon, cards on dark |
| Aurora Green | `#3DDC97` | accent on dark (9.9:1 on navy) |
| Aurora Teal | `#1FB5A8` | secondary accent on dark (6.9:1) |
| Deep Teal | `#0E7C74` | accent/links on light (4.7:1 on Star White) |
| Sunrise Amber | `#F5A524` | the sun; one small accent per layout (8.6:1 on navy) |
| Ember | `#B4560F` | amber for text on light (4.6:1 on Star White) |
| Star White | `#F4F7FB` | text on dark, light backgrounds |
| Mist | `#9FB3C8` | secondary text on dark (8.1:1) |
| Slate | `#4A5D73` | secondary text on light (6.3:1) |

Full WCAG AA table: `palette/contrast.md`. Aurora Green, Teal and Amber fail on white, so on light backgrounds use Deep Teal or Ember for text.

## Typography (all SIL Open Font License 1.1, no paid licences)
- **Sora**, weight 430, tracking -0.5 %: wordmark and headings. The wordmark is outlined to paths, so no font file is needed.
- **Inter**, 400 body / 500-600 labels: UI, docs, descriptor line.
- **IBM Plex Mono**: numbers, units, data tables, code.
- Every SVG master has text converted to outlines (`src/fontpath.py`, fontTools). Nothing depends on installed fonts.

## Usage
- Lockup: the wordmark's baseline sits on the bottom of the wheels, so car and letters share one ground line. The visible gap between tile and wordmark is about 0.19 x tile height (the wordmark starts at 1.16 x the tile canvas). Clear space is 0.25 x tile height on all sides.
- Minimum sizes: full mark 48 px, small mark 16 px, horizontal lockup 120 px wide.
- On dark backgrounds use the full-colour tile or glyph. On light backgrounds use the tile or `glyph-light`. In print, embossing, single-colour engineering documents and partner logo walls, use the mono glyphs.
- Use one amber sun per layout. Aurora appears as a thin line or soft curtain, never as a large flat fill.
- The only text next to the name is a plain descriptor, "open-source car generation" (Inter, Mist on dark). No slogans.
- Graphs: `plt.style.use("branding/earthrise/graph/earthrise.mplstyle")` (add `earthrise-dark.mplstyle` for dark slides). The ±10 % band is drawn in teal like a thin atmosphere around the 1:1 line. A small amber dot marks the title. The data, captions and sources are unchanged from `scripts/crush_plots.py`.

## Do
- Keep layouts mostly navy and white, with colour as a line.
- Let generative backgrounds (stars, aurora, tree line) stay behind and to the right of the lockup.
- Show measured numbers in IBM Plex Mono with units and sources.

## Don't
- Don't recolour the car body, add gradients to it, or put the sun anywhere except the end of the atmosphere arc.
- Don't place the lockup over a bright aurora or on a busy photo.
- Don't use Aurora Green or Amber for text on white.
- Don't add taglines, mascots, cartoon planets, lens flares, or glow on the wordmark.
- Don't stretch, rotate or outline the mark. Don't rebuild the wordmark in a live font.
- Don't use the tagline-slot templates as published assets.

## Credits and rules
Original artwork, generated from code in `src/`. No stock imagery or trademarks. Fonts: Sora, Inter, IBM Plex Mono (SIL OFL 1.1), embedded only as outlines. The graph re-render reads `data/crush-theory-check.csv` and changes no numbers. Nothing outside `branding/earthrise/` was edited.
