<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 galion-studio -->
# cargen brand concept: Wind & Shell

## Story
Nature has already solved cargen's two problems: wind shapes bodies, and shells protect what lives inside them. The mark is a streamliner drawn the way air would carve it. A round nose sits on a flat floor, and one curve runs from the roof to a raised tail. At the front is the orange crush cap from the current cargen mark, cut by two folds. Their spacing shrinks by 1/φ toward the nose, like the chambers of a nautilus, and they read as the folds of a crumple zone. In the banners the lockup sits inside the stagnation streamline of a Rankine half-body: the wind flows around the name. The social preview puts a nautilus, a log spiral that grows ×3 per turn, inside potential flow past a cylinder. Its living chamber, the part that takes the load, is orange. Nature appears only as an engineer would measure it: closed-form flows, real growth rates and equations printed as captions. There is no scenery, no glow and no illustration. The system keeps the existing graphite and orange codes, so it continues the current Forge and cargen assets instead of replacing them (see `branding/RESEARCH-enterprise.md`).

No tagline appears anywhere; Mate chooses it. `banner/templates/` holds a marked empty slot.

## Files
| Deliverable | File(s) |
|---|---|
| Logo mark (app tile) | `mark/cargen-windshell-mark.svg` + `-1024/-512/-256/-64/-32.png` |
| Small-size mark (16-48 px, favicon) | `mark/cargen-windshell-mark-small.svg` + `-48/-32/-16.png` (fuller body, thick tail, one fold, bigger wheels and gaps, full-bleed tile) |
| Glyph without tile | `mark/cargen-windshell-glyph-dark.svg` (for dark grounds), `-glyph-light.svg` (for light grounds), `-glyph-mono-dark.svg` / `-glyph-mono-light.svg` (one colour); folds and wheel arches are real holes + 512 px PNGs |
| Knockout mark | `mark/cargen-windshell-mark-knockout.svg` + `-512.png`: body cut out of the graphite tile, folds in orange |
| Wordmark | `wordmark/cargen-wordmark-{light,dark}.svg` + `@2x.png` |
| Lockups | `lockup/cargen-lockup-{light,dark}.svg` (horizontal), `lockup/cargen-lockup-stacked-{light,dark}.svg` + `@2x.png` |
| Banners 1280x320 | `banner/cargen-banner-{light,dark}-1280x320.{svg,png}`, plus `-2560x640.png` for retina |
| Tagline-slot layout guides (not for publishing) | `banner/templates/cargen-banner-{light,dark}-tagline-slot.{svg,png}` |
| GitHub social preview 1280x640 | `social/cargen-social-preview-1280x640.{svg,png}` |
| Graphic device: the corridor | `device/cargen-corridor-{light,dark}.{svg,png}` |
| Palette + WCAG check | `palette/palette.{svg,png}`, `palette/contrast.md` |
| Typography | `typography/typography.{svg,png}` |
| Graph style | `graph/windshell.mplstyle`, `graph/windshell-dark.mplstyle`, `graph/render_parity.py`, `graph/crush-parity-windshell-{light,dark}.png` |
| Sources | `src/mark.py` (mark geometry), `src/fields.py` (half-body, cylinder flow, nautilus), `src/glyphs.py` (text to outlines), `src/build.py` (all layouts), `src/palette.py`, `src/typography.py`, `src/render_all.sh` |

To rebuild everything, run `branding/windshell/src/render_all.sh`. It uses the repo `.venv` and `rsvg-convert`. The output is deterministic: there is no randomness, and every line comes from a formula.

## Palette
| Name | Hex | Use | Contrast |
|---|---|---|---|
| Graphite | `#16202A` | primary dark: ground, tiles, text on light (existing cargen code) | 14.6:1 on Paper |
| Shell Graphite | `#24323F` | raised tile on dark, shell region on dark | Paper on it 11.6:1 |
| Paper | `#F4F1EA` | primary light: ground, mark body, text on dark | 14.6:1 on Graphite |
| Sand | `#E9DFCB` | shell region and corridor fill on light; never text | Graphite on it 12.5:1 |
| Signal Orange | `#F26B1D` | crush cap, model/simulation line, one accent per layout (existing code) | 5.4:1 on Graphite; 2.7:1 on Paper, so never text on light |
| Orange Ink | `#B5470C` | orange for text and thin lines on light | 4.8:1 on Paper |
| Wind Blue | `#2F5F8F` | streamlines, corridor edges, measured test data on light | 5.9:1 on Paper |
| Sky | `#7FA8D6` | streamlines, corridor edges, measured test data on dark | 6.7:1 on Graphite |
| Ink Grey | `#5A6470` | secondary text on light; unvalidated estimates (dashed) | 5.3:1 on Paper |
| Mist | `#9AA3AD` | secondary text on dark; unvalidated estimates on dark (dashed) | 6.5:1 on Graphite, 5.1:1 on Shell Graphite |

The full table is in `palette/contrast.md`; the generator asserts that every approved pair passes AA. **Colour carries meaning on graphs.** Orange means cargen's model or simulation. Blue and graphite mean physical test data. Dashed grey means an unvalidated estimate. Never draw an unvalidated number in orange.

## Typography (SIL Open Font License 1.1, no paid licences)
- **IBM Plex Sans SemiBold (600)**, tracking -3 %: wordmark and headings. The double-storey g gives the wordmark its own face, and it avoids the Inter/Geist look common in dev tools. The wordmark is outlined to paths.
- **IBM Plex Sans 400/500**: body and UI.
- **IBM Plex Mono 400/500**: numbers, units, data tables, provenance captions, equations on art.
- Source: github.com/IBM/plex. Every SVG master has its text converted to outlines (`src/glyphs.py`, fontTools + HarfBuzz), so nothing depends on installed fonts. Fallbacks: system-ui, Menlo.

## Usage
- **Lockup:** the x-height of the wordmark is centred on the tile. The gap from tile to wordmark is 0.18 × tile. Clear space is 0.25 × tile on all sides.
- **Minimum sizes:** full mark 48 px; below that use `mark-small` (tested at 16 px). Horizontal lockup at least 120 px wide.
- **Grounds:** on dark, use the Shell Graphite tile (lockups) or `glyph-dark`. On light, use the Graphite tile or `glyph-light`. For one-colour print, embossing and partner logo walls, use the mono glyphs or the knockout mark.
- **Banners:** the lockup always sits inside the shell, the region inside the stagnation streamline. The field is labelled with its equation in Plex Sans at 13 px, the only text besides the name.
- **The corridor:** two thin curves (a measured test corridor) with one orange line inside (a simulation result). Use it for dividers, section rules, loading states and the ±10 % band on graphs.
- **Graphs:** `plt.style.use("branding/windshell/graph/windshell.mplstyle")`, and add `windshell-dark.mplstyle` for dark slides. The ±10 % band is drawn as the corridor, the 1:1 model line is orange, and test data is in blues and graphite with distinct markers. A short orange bar marks the title. Captions go in Plex Mono as an evidence block. Data, captions and sources are unchanged from `scripts/crush_plots.py`.

## Do
- Keep layouts graphite and paper, with colour used as a line. Use one orange area per layout: the crush cap, or the living chamber on the social preview.
- Label generated art with the equation that drew it.
- Show measured numbers in Plex Mono with units and sources.

## Don't
- Don't recolour the body, add gradients, or put orange anywhere on the mark except the nose cap.
- Don't draw the folds evenly spaced; the 1/φ rhythm is the shell.
- Don't use Signal Orange, Sky or Mist as text on Paper or white.
- Don't add taglines, mascots, scenery, glow, stars or AI-generated imagery.
- Don't stretch, rotate or outline the mark. Don't rebuild the wordmark in a live font.
- Don't publish the tagline-slot templates.

## Credits and rules
Original artwork, generated from the code in `src/`. No stock imagery and no trademarks. Fonts are IBM Plex Sans and IBM Plex Mono (SIL OFL 1.1), embedded only as outlines. The graph re-render reads `data/crush-theory-check.csv` through `scripts/crush_plots.rows()` and changes no numbers. This concept continues the previous designer's direction (streamline body, orange crush cap, φ folds, half-body banner field). It was finished after `branding/RESEARCH-enterprise.md`: palette aligned to its graphite/orange spec, Plex type, a simplified mark with a dedicated 16 px version, a knockout mark, and the corridor device. Nothing outside `branding/windshell/` was edited.
