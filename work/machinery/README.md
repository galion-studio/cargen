<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# mfgcheck: cited manufacturability checker (Forge / cargen, machinery sector)

`mfgcheck` takes a simple part description (sheet, tube, extrusion, casting or machined part) and flags breaches of published manufacturing rules. Each finding states the rule, the value, the limit, the nearest manufacturable change and the source URL. The research behind every number is in [machinery.md](machinery.md).

It applies **design rules, not fracture predictions**. A clean report means "no published rule broken". It does not mean "will not crack". Pure Python 3 standard library, no dependencies. MIT licence.

## Run
```bash
cd work/machinery
python3 -m mfgcheck examples/parts.json          # human-readable
python3 -m mfgcheck examples/parts.json --json   # machine-readable (each source with title + URL)
python3 -m unittest discover -s tests -v         # 56 tests
```
The exit code is 1 if any finding is an `error`, otherwise 0.

From Python:
```python
from mfgcheck import check_part
for f in check_part({"kind": "sheet", "material": "6061-T6", "thickness_mm": 3.0,
                     "bends": [{"inside_radius_mm": 3.0}]}):
    print(f.severity, f.rule, f.suggestion, f.sources)
```

## Input (all lengths in mm)
| kind | fields |
|---|---|
| `sheet` | `material` (FAA Al alloys such as `5052-H32` or `6061-T6`; SSAB steels `DC04`, `HSLA420-HR`, `HSLA420-CR-GI`, `DP600-UC/GI`, `DP800-UC/GI`, `DP1000-UC/GI`), `thickness_mm`, `process` (`fabricated`, `punch`, `laser`, `plasma`), `bends[]` {`inside_radius_mm`, `flange_mm`, `context`: `free` / `emboss` / `tension`}, `holes[]` {`diameter_mm`, `edge_distance_mm` (hole edge to sheet edge), `bend_distance_mm` (hole edge to bend line)}, press brake: `die_opening_mm`, `bend_length_mm`, `press_capacity_t` (metric t), `uts_mpa`; forming: `strain_points[]` {`major_pct`, `minor_pct`} (engineering %), `n_value` |
| `tube` | `od_mm`, `wall_mm`, `bends[]` {`clr_mm`}, `straights_mm[]`, `mandrel`, `bender` (`jd2_model32`), `hydraulic` |
| `extrusion` | `alloy`, `ccd_mm` (circumscribing circle), `walls_mm[]`, `hollow_class` (omit for solid/semihollow, or 1/2/3) |
| `casting` | `alloy` (`aluminum`, `magnesium`), `walls_mm[]`, `features[]` {`depth_mm`, `draft_deg`, `side`: `inside`/`outside`}, `fillet_radius_mm`, `corner_radius_mm`, `cored_holes[]` {`diameter_mm`, `length_mm`} |
| `machined` | `material_class` (`metal`/`plastic`), `walls_mm[]`, `holes[]` {`diameter_mm`, `depth_mm`}, `pockets[]` {`depth_mm`, `width_mm`, `corner_radius_mm`}, `tolerance_mm`, `machine` (`industrial`/`desktop`), `turned` {`length_mm`, `diameter_mm`} |

## What it checks
- **Sheet bending:**
  - Aluminium minimum radius from FAA AC 43.13-1B Table 4-6. Below the low end is an error; inside the range is a warning.
  - SSAB guaranteed minima for HSLA and DP steels.
  - AHSS ≥ 3t (embossments) or ≥ 5t (pulled over a radius) for DP grades.
  - Bystronic 1.5t designer rule for mild steel, since no mill minimum is published.
- **Stamping:** Keeler–Brazier FLC0 with the standard FLC shape and the A/SP red and yellow zones. It is refused for DP800+ and aluminium, because those need measured FLCs.
- **Holes and edges:** minimum diameter by process (laser 0.5t, plasma and fabricated 1t), hole-to-edge, feature-to-bend (4t, Protolabs) and minimum flange (4t).
- **Press brake:** V ≥ 5t (8t default), flange ≥ 0.77 V, predicted air-bend radius 0.16 V (mild steel), tonnage estimate (575·t²/V rule) against the machine's capacity.
- **Tube:** CLR ≥ 2×OD (production), ≥ 3×OD without a mandrel, whole-multiple dies, 76 mm minimum straights, JD2 Model 32 OD, wall and hydraulic limits.
- **Extrusion (6xxx):** Bonnell minimum wall vs CCD, 2:1 adjacent-wall ratio, hollow-class caveat.
- **Die casting:** NADCA draft angle A = 57.2738/(C·√L) for Al and Mg, inside and outside walls; wall range, fillets and cored holes.
- **CNC:** walls, hole size and depth, pocket depth and corner radius, tolerance (incl. desktop-router accuracy), turning L/D workholding.

Suggestions are rounded up (or down for maxima) to 0.1 mm so they never undershoot the rule. Rules are independent, so two findings may suggest different values for one field. Take the stricter one.

## Layout
```
META, STATUS          dashboard feed
machinery.md          research notes, every number with a URL
mfgcheck/data.py      rule tables + SOURCES (id -> title, URL)
mfgcheck/checks.py    checks, Finding dataclass, FLC helpers
mfgcheck/__main__.py  CLI
examples/parts.json   seven example car parts
tests/test_checks.py  unit tests (stdlib unittest)
```

## Real CAD geometry later
These are permissive tools; licences were read from each repo's LICENSE file:
- **ezdxf** (MIT): DXF flat patterns.
- **trimesh** (MIT): meshes and wall thickness.
- **Shapely** (BSD-3): 2D distances and CCD.
- **numpy-stl** (BSD-3): STL I/O.

For B-rep and STEP: **build123d / CadQuery / OCP** (Apache-2.0, on OCCT LGPL). Details in machinery.md §7. Nothing is vendored here.
