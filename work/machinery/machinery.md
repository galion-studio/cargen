<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# Machinery and manufacturing: what a generated car part must survive

Compiled 2026-10-21, 18:00–19:00 +02:00 (Europe/Zagreb). Read-only web research. Every number below was read on the linked page or PDF in this session. Nothing was estimated. Where a value is a shop's own house rule rather than a materials limit, the text says so. The checker in [`mfgcheck/`](mfgcheck/) encodes these rules. Each rule carries a source id from the table at the end.

**Scope and honesty.** These are design rules for manufacturability. They are not fracture predictions. Every one is a published guideline from a standard body, a steel mill, a die-casting association or a job shop. Tooling, grain direction, lubrication and the shop's own machine change the real limit. The checker reports a rule breach. It does not prove that a part will crack.

## 1. Sheet metal: bending and stamping

### 1.1 Minimum inside bend radius, aluminium (90° bend), source `faa-ac43`
FAA AC 43.13-1B (1998, with change 1), Table 4-6, p. 4-13. US Government work, public domain. Radius as a multiple of thickness t. The columns are the approximate sheet thickness in inches. The table gives a range: below the low value expect cracking; the high value is the safe end.

| Alloy-temper | 0.016 | 0.032 | 0.064 | 0.128 | 0.182 | 0.258 in |
|---|---|---|---|---|---|---|
| 2024-O | 0 | 0–1t | 0–1t | 0–1t | 0–1t | 0–1t |
| 2024-T3 | 1½–3t | 2–4t | 3–5t | 4–6t | 4–6t | 5–7t |
| 2024-T61 | 2–4t | 3–5t | 3–5t | 4–6t | 5–7t | 6–10t |
| 5052-O | 0 | 0 | 0–1t | 0–1t | 0–1t | 0–1t |
| 5052-H32 | 0 | 0 | ½–1t | ½–1½t | ½–1½t | ½–1½t |
| 5052-H34 | 0 | 0 | ½–1½t | 1½–2½t | 1½–2½t | 2–3t |
| 5052-H36 | 0–1t | ½–1½t | 1–2t | 1½–3t | 2–4t | 2–4t |
| 5052-H38 | ½–1½t | 1–2t | 1½–3t | 2–4t | 3–5t | 4–6t |
| 6061-O | 0 | 0–1t | 0–1t | 0–1t | 0–1t | 0–1t |
| 6061-T4 | 0–1t | 0–1t | ½–1½t | 1–2t | 1½–3t | 2½–4t |
| 6061-T6 | 0–1t | ½–1½t | 1–2t | 1½–3t | 2–4t | 3–4t |
| 7075-O | 0 | 0–1t | 0–1t | ½–1½t | 1–2t | 1½–3t |
| 7075-T6 | 2–4t | 3–5t | 4–6t | 5–7t | 5–7t | 6–10t |

A mill table cross-checks it (`united-al`): United Aluminum gives single minimum radii for a press brake with air-bend dies. 5052-H32 at 1/64, 1/32, 1/16 and 1/8 in is 0, 0, 1t and 1½t. 6061-T6 is 1t, 1t, 1½t and 2½t. 7075-T6 is 3t, 4t, 5t and 6t. These all fall inside the FAA ranges.

Takeaway: 6061-T6 and 7075-T6 crack at radii that 5052 takes easily. A generator should default sheet aluminium brackets to 5052-H32. It should keep 6xxx-T6 for extrusions, or bend it in O/T4 temper and age it afterwards.

### 1.2 Minimum inside bend radius, automotive steels (90° free bend), SSAB data sheets
These are the mill's guaranteed minima. UC = uncoated; GI/GA/ZA = zinc coated. Coated grades need a bigger radius because the coating micro-cracks.

| Grade (SSAB name) | UTS (MPa) | UC | GI/GA/ZA | n (min) | Source |
|---|---|---|---|---|---|
| Form 04 (DC04 deep-drawing mild steel) | 270–350 | not stated | — | n90 0.18 | `ssab-form04` |
| Docol HR420LA (HSLA, hot rolled) / CR420LA (cold rolled) | 480–600 | 0.5t (HR) | 1.0t (CR and HR) | n10-20 0.11 (CR GI) | `ssab-420la` |
| Docol CR330Y590T-DP (DP600) | 590–700 | 0.0t | 1.2t | n10-20 0.14 | `ssab-600dp` |
| Docol CR440Y780T-DP (DP800) | 780–900 | 1.0t | 1.8t | n10-20 0.11 | `ssab-800dp` |
| Docol CR590Y980T-DP (DP1000) | 980–1130 | 2.0t | 3.0t | — | `ssab-1000dp` |

**Bending under tension is much harsher** (`ahss-shear`). For DP340/590 and above, AHSS Guidelines give R/t of at least 3 for low-metal-motion features such as embossments. They give at least 5 when the sheet is pulled over a radius or through a draw bead. Studies quote critical R/t of 8 (DP800) and 7 or more (DP980). With high speed and back tension, DP590/780 reach 12 and DP980 goes past 16. Free-bend data-sheet values must not be used for stamped die radii.

### 1.3 Forming limit (stamping), source `asp-keeler` + `ahss-flc`
- Keeler–Brazier: FLC0 (engineering major strain at plane strain, %) = (23.3 + 14.2·t)·n/0.21, with t in mm and n the terminal (10–20 %) n-value. Source: A/SP *Enhanced Forming Limit Diagram* report, §8.2.5 and Step 1. This formula is already in research/materials.md §3.9; I re-read it in the PDF this session.
- Shape: the left side (minor < 0) is a line of constant thinning in true strain. The right side has slope +0.6 up to 20 % minor (engineering) strain (`ahss-flc`).
- Severity zones (A/SP Step 7): red starts at FLC0. Yellow starts at FLC0 − 10 % (engineering major strain).
- Validity (`ahss-flc`): mild steel, conventional HSLA and some lower-strength DP (e.g. CR340Y/590T-DP). TRIP, martensitic, TWIP and retained-austenite grades need measured FLCs (ISO 12004 / ASTM E2218). The checker refuses to apply the formula to DP800/DP1000 and to aluminium.
- Example: DC04 at 1.0 mm with n = 0.18 gives FLC0 = (23.3 + 14.2)·0.18/0.21 = 32.1 %.

### 1.4 Holes, edges, flanges and features near bends
| Rule | Value | Source |
|---|---|---|
| Hole/slot diameter (fabricated sheet) | ≥ t | `protolabs-sheet` |
| Laser-cut hole/cutout | ≥ 0.5 t | `scs-bending` (pre-flight checklist) |
| Plasma hole, general rule | diameter ≥ t (1:1) | `hypertherm-holes` |
| Plasma True Hole (XPR/HPRXD, mild steel ≤ 25 mm) | D/t from 2:1 down to 1:1 | `hypertherm-truehole` |
| Hole to material edge | ≥ 1.575 mm (0.062 in) if t ≤ 0.914 mm; ≥ 3.175 mm (0.125 in) if thicker | `protolabs-sheet` |
| Features within 4 t of a bend | at risk of deformation | `protolabs-sheet` |
| Designer rule: holes and flanges ≥ 6 t from the bend; inside radius 1.5 t; Z-offset web ≥ 10 t | house rule (Bystronic) | `fab-tooling` |
| Minimum flange | ≥ 4 t | `protolabs-sheet` |
| Hem | inside diameter = t; return length 6 t | `protolabs-sheet` |
| Notch width ≥ max(t, 1.016 mm), length ≤ 5 × width; tab width ≥ max(2t, 3.2 mm), length ≤ 5 × width | | `protolabs-sheet` |
| Tolerances, one surface, t < 3.3 mm | edge-edge, edge-hole, hole-hole ±0.13 mm; bend-hole ±0.38 mm; bend-edge ±0.25 mm | `protolabs-sheet` |
| Tolerances across 3+ bends | ±0.76 mm (t < 3.3 mm), ±1.016 mm (thicker) | `protolabs-sheet` |
| Bend angle tolerance | ±1° (Protolabs; SendCutSend for bends ≤ 24 in), ±2° for longer bends (SendCutSend) | `protolabs-sheet`, `scs-bending` |
| U/C channel base | ≥ 2 × flange length (sheet metal) | `scs-bending` |

### 1.5 Press brake (job shop and small shop), source `fab-tooling` + `noramark-tonnage`
- Rule of 8: V-die opening = 8 t. Never go below 5 t: angle accuracy suffers, and the machine and tooling can be damaged.
- Air bending mild steel gives an inside radius of about 16 % of V. So V = 8 t gives about 1.28 t.
- The minimum flange a V-die can form is about 77 % of V.
- Tonnage (estimate): tons/ft = 575·t²/V·(UTS/60 ksi), with t and V in inches. In metric this is about 67.4·t²/V metric t per metre (t and V in mm, 414 MPa steel). Published metric versions differ by about 10 %, so treat it as an estimate.
- Example (Noramark): 1/8 in mild steel over a 1 in die needs 8.98 t/ft.
- SendCutSend house limits (`scs-bending`, `scs-minmax`): air bending only, max bend angle 130°, fixed radius per material and thickness. For example, mild steel 0.119 in has a 0.063 in effective radius; 5052 0.125 in has 0.125 in. No custom radii.

## 2. Tube bending, source `xometry-tube`, `protools-wf`, `vr3-tube`, `jd2-m32`
- Wall factor WF = OD / wall. D of bend = CLR / OD. A higher WF and a lower D make a harder bend. They set the mandrel and wiper choice (`fab-mandrel`).
- Production rotary-draw: CLR ≥ 2 × OD is the minimum recommended. 2×Ø tooling is the most common. Whole-number multiples of OD avoid custom tooling. Roll bending: about 7 × OD (`xometry-tube`).
- No mandrel, rule of thumb: CLR ≥ 3 × OD (`protools-wf`).
- Manual rotary draw (Ercolina-type shop): standard CLR is 3–4 × OD. Straight between bends and at the ends is typically 3.0–5.0 in, i.e. 76–127 mm (`vr3-tube`).
- Hobby bender example, JD2 Model 32 (`jd2-m32`): round tube 1/2–2 1/2 in OD; square 1/2–2 in. Rated for 2 in OD × 0.250 in wall DOM. Round tube over 2 in OD × 0.120 in wall needs the hydraulic version. Its dies are steel; aluminium dies spread when bending 4130.

## 3. Aluminium extrusion (crash boxes, rails), source `bonnell`
- Minimum practical wall vs circumscribing circle (CCD), 6xxx. For solids and semihollows it runs from 0.040 in (CCD 0.5–2 in) to 0.188 in (12–13 in). For Class 2 hollows it runs from 0.055 in to 0.236 in. Above 13 in CCD is "subject to inquiry".
- Avoid adjacent-wall thickness ratios above 2:1. Use rounded transitions.
- Hollow classes: Class 1 has a round void ≥ 1 in, symmetric. Class 2 has a single void ≥ 0.375 in diameter or 0.110 in², with CCD ≤ 5 in. Class 3 is everything else, e.g. multi-cell crash boxes, and needs the extruder's review.
- Minimum properties: 6061-T6 has UTS 38 ksi, YS 35 ksi and elongation 8 % (≤ 0.249 in) or 10 %. 6063-T6 has 30/25 ksi. 6082-T6 (0.200–0.750 in) has 45/38 ksi and 6 %.

## 4. CNC milling and turning
| Rule | Value | Source |
|---|---|---|
| Wall thickness, metal | 0.8 mm recommended, 0.5 mm feasible (plastics 1.5 / 1.0 mm) | `hubs-cnc` |
| Cavity depth | ≤ 4 × cavity width recommended | `hubs-cnc` |
| Internal vertical corner radius | ≥ ⅓ × cavity depth recommended | `hubs-cnc` |
| Hole depth | 4 × D recommended, 10 × D typical, 40 × D feasible | `hubs-cnc` |
| Hole diameter | standard drill size recommended; 2.5 mm and up is normal (below is micro-machining) | `hubs-cnc` |
| Thread length | ≥ 1.5 × D, 3 × D recommended | `hubs-cnc` |
| Tolerance | ±0.1 mm typical, ±0.02 mm feasible (Hubs); ±0.13 mm standard (Protolabs) | `hubs-cnc`, `protolabs-cnc` |
| Min feature thickness / nominal part thickness | 0.51 mm / 1.02 mm | `protolabs-cnc` |
| Turning workholding (L/D) | chuck only < 3 (to 5 with reduced cuts); tailstock 3–6 (to 10); steady rest 6–12 (to 20) | `cadem-turning` |
| Desktop CNC example: Shapeoko 5 Pro | ballscrew accuracy ±50 µm per 300 mm; step 0.012 mm XY. A part tolerance tighter than the machine's positioning accuracy is not credible | `shapeoko5pro` |

## 5. Casting (Al / Mg high-pressure die casting), source `nadca`
NADCA *Product Specification Standards for Die Castings* (2009), section 4A:
- Typical walls are 1.016–5.08 mm, depending on alloy and size. Walls as thin as 0.50 mm are possible on small castings with die-caster consultation.
- Draft (Standard Tolerance): angle A = 57.2738 / (C·√L), with L the feature depth from the parting line. The metric C constants are: aluminium 6 (inside wall) and 12 (outside); magnesium 7 and 14. Example: Al inside wall, 25 mm deep, gives 1.9°.
- Large castings (§4A-42 guideline): keep the wall range within 2× of the thinnest wall. General wall 3.5 ± 0.5 mm. Fillet ≥ 1.5 mm, corner radius ≥ 0.5 mm. Cored holes ≥ 6 mm diameter. L/D ≤ 4:1 below 12.5 mm diameter and ≤ 10:1 above.
- The NADCA PDF was read from a die caster's public copy. The standard is NADCA copyright, so only the numbers are cited here.

## 6. Small shop and hobbyist equivalents (summary)
| Industrial process | Small-shop equivalent | Rule in checker |
|---|---|---|
| Transfer-press stamping | Press brake, air bending | V ≥ 5 t, V = 8 t default, flange ≥ 0.77 V, tonnage estimate vs press capacity |
| CNC rotary-draw mandrel bending | Manual or hydraulic rotary-draw bender (JD2 Model 32, Ercolina) | CLR ≥ 3 × OD with no mandrel, bender OD and wall limits, 76 mm straights |
| Fibre laser | Online laser service (SendCutSend) or CNC plasma (Hypertherm) | hole ≥ 0.5 t (laser), ≥ 1 t (plasma) |
| 5-axis VMC | Desktop router (Shapeoko 5 Pro) | tolerance ≥ machine accuracy |
| HPDC Al/Mg | — (outsourced; sand casting not covered yet) | NADCA draft and wall rules |

## 7. Open-source tools that could supply real CAD geometry later (licences read in each repo's LICENSE file, 2026-10-21)
| Tool | Licence (repo LICENSE) | Use for the checker |
|---|---|---|
| [ezdxf](https://github.com/mozman/ezdxf) | MIT | Read DXF flat patterns: hole diameters, hole-to-edge distances, bend lines |
| [trimesh](https://github.com/mikedh/trimesh) | MIT | Meshes (STL/OBJ/GLB): wall thickness by ray casting, bounding and circumscribing sizes |
| [Shapely](https://github.com/shapely/shapely) | BSD-3-Clause | 2D profile maths: hole-to-edge and hole-to-bend distances, extrusion CCD (minimum bounding circle) |
| [numpy-stl](https://github.com/WoLpH/numpy-stl) | BSD-3-Clause | Light STL I/O |
| [build123d](https://github.com/gumyr/build123d), [CadQuery](https://github.com/CadQuery/cadquery), [OCP](https://github.com/CadQuery/OCP) | Apache-2.0 (permissive, not MIT/BSD) on OCCT (LGPL-2.1 + exception) | B-rep/STEP: true bend radii, sheet-metal unfolding, draft-angle measurement; the repo's chosen CAD path (research/licences.md) |
| [truck](https://github.com/ricosjp/truck) | Apache-2.0 | Rust B-rep with STEP I/O, if the checker moves into the Rust core |
| [FreeCAD SheetMetal](https://github.com/shaise/FreeCAD_SheetMetal) | LGPL-2.1 | Unfolding reference; separate process only |

## 8. Gaps (not found or not verified this session)
- No open FLC for aluminium sheet (5182-O, 6016-T4) or for DP800+ and TRIP. These need measured FLCs, e.g. NIST Numisheet 2020 raw data (research/materials.md §2.1).
- No open, primary minimum-bend-radius value for plain mild steel (DC01/DC04, 1008/1018). SSAB Form 04 does not state one. The checker uses only the Bystronic 1.5 t designer rule there, as a warning.
- No open tube-bending fracture limit (minimum CLR by material). The tube rules are tooling and shop rules.
- Laser cut tolerances and kerf by thickness, plasma bevel, magnesium sheet (AZ31) bending (needs warm forming) and sand or gravity casting rules: not covered yet.
- The mandrel/wiper chart values (WF vs D) are published only as a figure. They were not transcribed.

## Sources
| id | Source | URL |
|---|---|---|
| faa-ac43 | FAA AC 43.13-1B w/ change 1, Table 4-6 (public domain) | https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf |
| united-al | United Aluminum, Recommended minimum bend radii for 90° cold forming | https://unitedaluminum.com/wp-content/uploads/techmanual/RecommMinBlendpg10.pdf |
| ssab-form04 | SSAB Form 04 data | https://www.ssab.com/en/brands-and-products/ssab-form-deep-drawing-steel/product-offer/04 |
| ssab-420la | SSAB Docol 420LA | https://www.ssab.com/en/brands-and-products/ssab-docol/automotive-steel-grades/hsla-steel/420la |
| ssab-600dp | SSAB Docol 600DP | https://www.ssab.com/en-us/brands-and-products/ssab-docol/automotive-steel-grades/dual-phase-steel/600dp |
| ssab-800dp | SSAB Docol 800DP | https://www.ssab.com/en-us/brands-and-products/ssab-docol/automotive-steel-grades/dual-phase-steel/800dp |
| ssab-1000dp | SSAB Docol 1000DP | https://www.ssab.com/en-us/brands-and-products/ssab-docol/automotive-steel-grades/dual-phase-steel/1000dp |
| ahss-shear | AHSS Guidelines, Shear fracture | https://ahssinsights.org/forming/formability/shear-fracture/ |
| ahss-flc | AHSS Guidelines, Forming limit curves | https://ahssinsights.org/forming/formability/forming-limit-curves-flc/ |
| asp-keeler | Keeler, Enhanced Forming Limit Diagram, A/SP report | https://www.a-sp.org/wp-content/uploads/2020/08/Technology-Report-Final.pdf |
| protolabs-sheet | Protolabs sheet metal design guidelines | https://www.protolabs.com/services/sheet-metal-fabrication/design-guidelines/ |
| scs-bending | SendCutSend bending guidelines | https://sendcutsend.com/guidelines/bending/ |
| scs-minmax | SendCutSend processing min/max | https://sendcutsend.com/materials/processing-min-max/ |
| hypertherm-holes | Hypertherm FAQ, How can I cut better holes | https://www.hypertherm.com/resources/faqs/how-can-i-cut-better-holes/ |
| hypertherm-truehole | Hypertherm True Hole | https://www.hypertherm.com/solutions/about-our-products/surecut-technology/true-hole/ |
| fab-tooling | LeTang (Bystronic), The rules of press brake tool selection, The Fabricator 2019 | https://www.thefabricator.com/thefabricator/article/bending/the-rules-of-press-brake-tool-selection |
| noramark-tonnage | Noramark press brake tonnage calculator | https://www.noramark.com/resources/press-brake-tonnage-calculator/ |
| xometry-tube | Xometry tube bending design tips | https://www.xometry.com/resources/tube/tube-bending-design-tips/ |
| protools-wf | Pro-Tools, Wall factor and D of bend | https://pro-tools.com/blogs/protoolsusa/42288387-wall-factor-and-d-of-bend-getting-to-the-center-of-the-centerline-radius-debate |
| fab-mandrel | The Fabricator, Selecting the right mandrel and wiper | https://www.thefabricator.com/tubepipejournal/article/tubepipefabrication/selecting-the-right-mandrel-and-wiper |
| vr3-tube | VR3 tube bending guidelines (manual rotary draw), Sept 2026 | https://vr3.ca/documents/TubeBendingGuidelines.20260916.pdf |
| jd2-m32 | JD Squared Model 32 bender | https://www.jd2.com/model-32-bender |
| bonnell | Bonnell Aluminum, Designing aluminum extrusions | https://bonnellaluminum.com/tech-info-resources/designing-aluminum-extrusions/ |
| hubs-cnc | Protolabs Network (Hubs), How to design parts for CNC machining | https://www.hubs.com/knowledge-base/how-design-parts-cnc-machining/ |
| protolabs-cnc | Protolabs CNC milling guidelines | https://www.protolabs.com/services/cnc-machining/cnc-milling/ |
| cadem-turning | CADEM, CNC lathe work holding thumb rules | https://cadem.com/cnc-turning-work-holding-thumb-rules/ |
| shapeoko5pro | Carbide 3D Shapeoko 5 Pro specs | https://carbide3d.com/shapeoko/shapeoko5pro-specs/ |
| nadca | NADCA Product Specification Standards for Die Castings 2009, §4A (public copy) | https://www.paceind.com/wp-content/uploads/2016/02/NADCA-Tolerances-2009.pdf |
