<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 galion-studio -->
# cargen brand concept: Field Notes

## Story
A naturalist's field notebook and an engineer's test report work the same way: draw the specimen, measure it, write down where every number came from. Field Notes treats cargen as that notebook. The mark is a specimen roundel: a measuring ring with 60 graduations around the existing cargen car, whose crumple zone is drawn as a folded hornbeam leaf (*Carpinus betulus* leaves open from tight pleats, the way a crush tube folds), pressed against a rigid barrier on an engineering fixed-support line. Every layout is a plate: hairline sheet border with a ruler, numbered figures, captions in a monospace provenance line, and colour that means something (cyanotype blue = physical test, signal orange = validated simulation, dotted grey = unvalidated). Nature appears only as a measured reference drawing, never as scenery, so it reads as engineering software first.

No tagline appears anywhere. Mate chooses the tagline; `banner/templates/` holds a marked empty slot for it.

### What changed after `branding/RESEARCH-enterprise.md`
The research rated Field Notes "strong system, weak mark" (too many elements, orange dot at 16 px, vintage/heritage feel). This version responds:
- Mark simplified: stars, constellation lines and body hatching removed. Primary roundel is now **graphite** (continues the existing charcoal tile and orange body; body and crumple-zone paths are kept verbatim from `assets/logo/cargen-mark.svg`).
- A dedicated, pixel-drawn **16 px mark** (`mark-16`) and a 24-48 px **small mark**.
- Typography moved from EB Garamond to the **IBM Plex** superfamily (Plex Serif wordmark, Plex Sans text, Plex Mono numbers), as the research recommends; the serif keeps the notebook voice without the antique look.
- Paper grain, star fields and asterisms removed. The dark banner keeps only a measuring grid behind the plate.
- The plate became an explicit **evidence format** (`templates/cargen-evidence-plate-*.svg`): SOURCE / SOLVER / MESH / ERROR VS TEST, with the colour key above.
- The graph style encodes the research's colour rule; the re-rendered graph is P1a, where the experiment is cyanotype blue and the pending simulation is a dotted legend entry, not a warning box over the data.

## Files
| Deliverable | File(s) |
|---|---|
| Logo mark (primary, graphite) | `mark/cargen-fieldnotes-mark.svg` + `-512/-256/-128/-64/-48.png` |
| Mark variants | `mark/cargen-fieldnotes-mark-paper.svg` (paper roundel for print), `-mono.svg` (graphite on paper), `-mono-chalk.svg` (chalk on graphite) + `-512.png` each |
| Small marks | `mark/cargen-fieldnotes-mark-small{,-paper}.svg` + `-48/-32/-24.png` (no graduations, one midrib); `mark/cargen-fieldnotes-mark-16{,-paper}.svg/.png` (pixel master, 16 x 16) |
| Touch icon | `mark/cargen-fieldnotes-touch-icon.svg` + `-180.png` (full-bleed square; iOS/Android mask the corners) |
| Glyph without roundel | `mark/cargen-fieldnotes-glyph{,-paper,-mono,-mono-chalk}.svg` + `@2x.png` (keylines are real cut-outs, so it works on any ground) |
| Wordmark | `wordmark/cargen-wordmark-{light,dark,signal}.svg` + `@2x.png` |
| Lockups | `lockup/cargen-lockup-{light,dark}.svg` (horizontal), `lockup/cargen-lockup-stacked-{light,dark}.svg` + `@2x.png` |
| Banners 1280x320 | `banner/cargen-banner-{light,dark}-1280x320.{svg,png}` |
| Tagline-slot layout guides (not for publishing) | `banner/templates/cargen-banner-{light,dark}-tagline-slot.{svg,png}` |
| GitHub social preview 1280x640 | `social/cargen-social-preview-1280x640.{svg,png}` |
| Evidence plate template | `templates/cargen-evidence-plate-{light,dark}.{svg,png}` (fields are bracketed placeholders) |
| Palette + WCAG check | `palette/palette.{svg,png}`, `palette/contrast.md` |
| Typography | `typography/typography.{svg,png}` |
| Graph style | `graph/fieldnotes.mplstyle`, `graph/fieldnotes-dark.mplstyle`, `graph/render_p1a.py`, `graph/p1a-force-energy-fieldnotes-{light,dark}.png` |
| Sources | `src/fn_lib.py` (palette, OFL fonts to outlines, leaf / car / tube drawing primitives), `src/fn_mark.py`, `src/fn_build.py` (all layouts), `src/fn_palette.py`, `src/fn_type.py`, `src/render.sh` |

Rebuild everything (SVG masters, PNGs, graph) with `branding/fieldnotes/src/render.sh`. It uses the repo `.venv` (uharfbuzz, fontTools, matplotlib) and `resvg`. Output is deterministic (fixed seeds). Fonts are read from the system Google Fonts folder and instanced into `src/.fontcache/`.

## Palette
| Name | Hex | Use | Contrast (WCAG 2.1) |
|---|---|---|---|
| Graphite | `#16202A` | existing cargen charcoal; dark ground; text on paper | 14.1:1 on Field Paper |
| Field Paper | `#F3EDDF` | light ground: plates, docs, social | 14.1:1 with Graphite |
| Chalk | `#EDE6D3` | text and line work on graphite | 13.2:1 on Graphite |
| Sepia | `#5E5141` | secondary text on paper: captions, provenance | 6.6:1 on Field Paper |
| Dust | `#B9B09C` | secondary text on graphite | 7.7:1 on Graphite |
| Signal Orange | `#F26B1D` | existing cargen orange: the car; validated simulation on graphite | 5.4:1 on Graphite; 2.6:1 on paper: not for text there |
| Signal Ink | `#A8461A` | signal orange for text, thin lines, simulation curves on paper | 5.1:1 on Field Paper, 5.9:1 on white |
| Cyanotype | `#2F5F8F` | physical test data on paper | 5.7:1 on Field Paper |
| Cyanotype Pale | `#7FA8D6` | physical test data on graphite | 6.7:1 on Graphite |
| Fern | `#3D6B4A` | the leaf on paper; never data | 5.3:1 on Field Paper |
| Lichen | `#8DB89A` | the leaf on graphite; never data | 7.4:1 on Graphite |
| Sage | `#A9BC9C` | leaf wash, fills only | fill only |
| Vellum | `#E7DDC6` | panels, caption blocks on paper | surface only |
| Rule | `#2A3843` | measuring grid on graphite | hairline only |

Full table with every pair: `palette/contrast.md`.

**Colour means something in figures:** cyanotype = physical test; signal = validated simulation; sepia/dust, dotted or dashed = unvalidated or pending. Green belongs to the leaf and never encodes data.

## Typography (IBM Plex, SIL Open Font License 1.1, github.com/IBM/plex; no paid licences)
- **IBM Plex Serif SemiBold**, tracking -1 %: wordmark and headings. The wordmark is outlined, so no font file is needed.
- **IBM Plex Sans** 400 / 600: text, UI, graph labels.
- **IBM Plex Mono** 400 / 500: numbers, units, figure numbers, provenance captions, tick labels.
- **IBM Plex Serif Italic**: Latin specimen names in captions (*Carpinus betulus*), after a Plex Mono figure number.
- Every SVG master has its lettering converted to outlines (`fn_lib.text_path`, uharfbuzz shaping + fontTools).

## Usage
- **Lockup:** the wordmark's x-height is centred on the roundel. Gap between roundel and wordmark = 0.17 x roundel diameter. Clear space = 0.25 x roundel diameter on all sides.
- **Minimum sizes:** full mark 48 px; small mark 24-48 px; `mark-16` at 16 px only; horizontal lockup 140 px wide.
- **Grounds:** the graphite roundel is the default on both paper and graphite (its chalk rim keeps it visible on dark). Use the paper roundel for print on paper, mono / mono-chalk for single-colour documents, embossing and partner logo walls, the glyph inline in text or tables.
- **Plates:** every published figure sits on a plate with a Plex Mono caption block (SOURCE / SOLVER / MESH / ERROR VS TEST, or "unvalidated estimate"). Use `templates/cargen-evidence-plate-*.svg`.
- **Figures:** number them (Fig. 1, Fig. 2); drawings that are not results say "(drawing)".
- **Graphs:** `plt.style.use("branding/fieldnotes/graph/fieldnotes.mplstyle")`, plus `fieldnotes-dark.mplstyle` for dark slides. Keep the colour meaning; draw pending or unvalidated series dotted. `render_p1a.py` shows the pattern, including a caption block in Plex Mono, and only draws a simulated curve if a real P1a result file exists (same rule as `scripts/crush_plots.py`).
- **Tagline:** none. When Mate chooses one, it goes in the slot shown in `banner/templates/`, set in Plex Mono or Plex Sans, Sepia on paper / Dust on graphite.

## Do
- Keep layouts quiet: paper or graphite, one orange car, one green leaf, blue data.
- Put real numbers with units and a source next to anything that looks like a result.
- Use hairline borders, ruler ticks and figure numbers as the recurring plate device.

## Don't
- Don't add stars, constellations, paper texture, stains or "vintage" effects; the notebook is precise, not antique.
- Don't use signal orange for physical-test data, or green for any data.
- Don't put Signal Orange text on paper or white; use Signal Ink.
- Don't recolour, stretch, rotate or outline the mark; don't add the old body hatching back.
- Don't rebuild the wordmark in a live font; use the outlined SVG.
- Don't add taglines, slogans, mascots or glows. Don't publish the tagline-slot or evidence-plate templates as they are.

## Credits and rules
Original artwork generated from code in `src/`; no stock imagery, no trademarks, no AI-generated images. The car body and crumple-zone paths come from the project's own MIT mark. Fonts: IBM Plex Serif, Sans, Mono (SIL OFL 1.1), embedded only as outlines. The graph re-render reads `forge/data/p1a/park2022_us2_fig3_digitized.csv` and changes no numbers. Nothing outside `branding/fieldnotes/` was edited.
