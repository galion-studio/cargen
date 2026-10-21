<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# Welding for generated car structures: processes, HAZ knockdowns, spot-weld crash cards

Compiled 2026-10-21, 17:00–18:30 +02:00 (Europe/Zagreb). Read-only web research. Every number below was read on the linked page or PDF in this session. Source ids `[ID]` point to the table at the end. The tool in [`weldtool/`](weldtool/) carries these values with the same ids. **Everything here is a starting point. Verify it with test coupons.**

## 1. Where welding enters design and validation

| Stage | What welding changes | Where it lives here |
|---|---|---|
| Process choice | Spot (RSW) welds sheet-steel BIW lap joints. MIG/MAG welds thicker sections and Al extrusions. TIG welds thin or critical Al/Ti. Laser gives a narrow HAZ. FSW is solid-state, for Al. | `weldtool params` |
| Strength design | The HAZ is softer than the base metal in heat-treated Al (T6), in Mg (H24), and in martensitic AHSS. Use reduced strength inside a width `b_haz`. | `weldtool haz` |
| Crash model | Spot welds become connector bricks with force/displacement yield and failure. HAZ shells get knocked-down flow curves. | `weldtool card` |
| Validation | Calibrate cards on 0°, 90°, combined and peel coupons [ALTAIR_SPOTWELD]. Check nugget size and shear-tension against AWS minimums [AWS_C11]. | README, §4 |

## 2. HAZ knockdowns (multiply base yield/UTS inside b_haz)

**Aluminium, EN 1999-1-1** [EC9_WS]:

| Alloy | ρo,haz (yield) | ρu,haz (UTS) |
|---|---|---|
| 6082-T6 extrusion, t<5 mm | 0.50 | 0.64 |
| 6082-T6 sheet, t<5 mm | 0.48 | 0.60 |
| 6082-T4 | 0.91 | 0.78 |
| 7020-T6 | 0.71 | 0.80 |
| 5754-H14 | 0.53 | 0.63 |
| 3005-H14 / -H16 | 0.37 / 0.30 | 0.64 / 0.56 |

- O and F tempers do not weaken (ρ = 1.0) [CESTRUCO].
- The older ENV table for 6xxx-T6 gives ρhaz 0.65 for MIG and 0.50 for TIG, so **TIG is harsher**. The values apply 3 days after welding for 6xxx and 30 days for 7xxx, held at ≥10 °C [CESTRUCO].
- b_haz each side [CESTRUCO]:
  - MIG: 20 mm for t≤6, 30 mm for 6–12, 35 mm for 12–25, 40 mm for t>25.
  - TIG: 30 mm for t≤6.
- ADM 2020 says the reduction typically extends 25 mm (1 in) each side of the weld centreline [ADM2020].
- T6 alloys lose about 40 % of strength in the HAZ. 7020 loses about 20 % [EC9_EAA]. The EAA worked example uses ρo,haz 0.48 and b_haz 30 mm at t=10 mm [EC9_EAA].
- 6082-T6 with 5356 filler: HAZ ρu·fu is 185 MPa and weld metal fw is 210 MPa [EC9_WS].
- 6061-T6 as-welded is 24 ksi (165 MPa), against 40 ksi (275 MPa) for T6, so about 0.60 [LINCOLN_AL].
- FSW 6082-T6 at 10 mm reaches 238–247 MPa, which is 77–80 % of the 310 MPa base [MA2022_FSW].

**Steel (AHSS).** Martensite tempering softens the HAZ. Hardness ratio is used as a strength proxy.
- Spot-weld HAZ hardness drop: DP590 −6 %, DP980 −18 %, M1700 −42 % [ENGRXIV_HAZ].
- DP980 HAZ: RSW −18 % (about 60 HV), GMAW −54 % (157 HV). **Arc welding is much worse than spot welding** [DP980_GMAW_RSW].
- DP980 1.4 mm fibre laser (4.5 kW, 4.5 m/min) [HUANG2022_DP980]:
  - Joint efficiency 0.984 (1010 vs 1026 MPa).
  - HAZ 276 vs 305 HV, about 0.5 mm wide.
  - Elongation drops from 12 % to 8 %.
- Mild steel: no open HAZ knockdown was found. The tool reports "none found".

**Magnesium, AZ31B-H24 at 2 mm.** Laser joint efficiency is about 91 % with a fibre laser and 59 % with a diode laser [CHOWDHURY2011_MG]. The laser-arc hybrid data are in [WANG2022_MG].

**Titanium, Ti-6Al-4V at 4 mm, after PWHT 704 °C / 2 h** [TOLVANEN2024_TI]:

| Process | Yield / UTS (MPa) | Elongation | HAZ width |
|---|---|---|---|
| Base metal | 975 / 1021 | 16.4 % | — |
| TIG | 871 / 958 | 7 % | 3.2 mm |
| Laser (LBW) | 931 / 995 | 10 % | 1.6 mm |
| EBW | 940 / 1014 | — | — |
| PAW | 856 / 954 | — | — |

## 3. Process parameter sources (what the tool looks up)

- **MIG/MAG on steel and Al:** Millermatic 211 chart columns (volts and wire speed by gauge) [MILLER211], with gauges converted to mm [WIKI_GAUGE]. Rules of thumb from Miller [MILLER_RULES]:
  - About 1 A per 0.001 in of thickness.
  - Wire-speed multipliers 3.5 / 2 / 1.6 / 1 by wire size.
- **TIG on steel and Al:** Lincoln quick-reference amperage and tungsten tables [LINCOLN_SQW].
- **Spot welding on low-carbon steel:** NSRW class A/B/C schedules give force, current, time, nugget, shear, spacing and overlap [NSRW_LC].
  - HSS needs 20–50 % more electrode force [TWI_UHSS].
  - Al resistance-welding ranges come from European Aluminium [EAA_RSW].
- **Laser and FSW:** no open thickness tables were found. The tool returns only the cited reference points above.

## 4. Spot welds in OpenRadioss / OpenCourant

**Recommended model** [ALTAIR_SPOTWELD], [ALTAIR_LAW59], [ALTAIR_FAILCONNECT]:
- One `/BRICK` with `/PROP/TYPE43` and `/MAT/LAW59` (CONNECT), tied to the two shells with `/INTER/TYPE2`.
- E and G are given per unit length.
- Yield curves are stress vs plastic displacement.
- Failure comes from `/FAIL/CONNECT` through displacement limits u_maxN and u_maxT. Ifail is 0 (uncoupled) or 1 (coupled).

**How the tool fills the card:**
- Nugget d = 4√t [AWS_C11], [TWI_UHSS]. The factor can be changed, e.g. 5√t.
- Shear force is the AWS C1.1 minimum: ST[kN] = (−8.83e-7·S² + 1.34e-3·S + 1.514)·S·4t^1.5/1000 [AWS_C11]. At S=300 MPa and t=1 mm this gives 2.20 kN.
- Normal force = CTS/TSS × shear, with ratios from [TWI_UHSS]:
  - 0.70–0.80 for low-carbon steel.
  - About 0.5 near 600 MPa.
  - About 0.3 for UHSS with interface failure.
  - The UTS bins (≤350, 350–700, >700 MPa) are our own choice.
- Stress = force / nugget area, as flat curves.
- E, G, u_max are the Altair example values, marked "calibrate".

**Example:** mild steel at 1 mm gives d 4 mm, shear 2.121 kN, normal 1.485 kN, τ 168.8 MPa and σn 118.1 MPa.

**Solver smoke check** (`smoke/`, local OpenCourant, run 2026-10-21 18:15 +02:00):
- The starter read the card with 0 errors, and the engine ended in NORMAL TERMINATION.
- The weld's shear stress held at 168.8 MPa, which equals the card τ.
- The weld was deleted at a tangential displacement of 1.800 mm, which equals u_maxT.
- So the solver does what the card says. **This proves the card is wired correctly. It does not prove the weld strength.**

## 5. Joint design rules (cited)

- Keep NSRW minimum spot spacing and overlap for the sheet thickness. The tool prints them [NSRW_LC].
- Load spot welds in shear, not in peel or cross-tension. CTS is only about 0.3–0.8 × TSS [TWI_UHSS].
- On 6xxx/7xxx-T6, keep welds out of high-stress zones, or size for ρhaz over b_haz each side [EC9_WS], [CESTRUCO], [LINCOLN_AL]. Prefer FSW or laser where the HAZ matters [MA2022_FSW].
- On AHSS, prefer RSW or laser over GMAW. The DP980 HAZ drops −18 % with RSW and −54 % with GMAW [DP980_GMAW_RSW].
- On Ti, laser leaves half the HAZ width of TIG and more elongation [TOLVANEN2024_TI].

## 6. Gaps (not invented)

The following were not found in open sources:
- An Al spot-weld thickness schedule (AWS tables are paywalled).
- Mg or Ti TIG amperage tables.
- Mg MIG parameters.
- Mg FSW or TIG joint efficiency (the review fetches timed out).
- A mild-steel HAZ knockdown.

The 1967 AA manual welded Ftyw values were read but are not encoded in the tool.

## Sources

| ID | Source |
|---|---|
| MILLER211 | <https://contenthub.itwwelding.com/api/public/content/miller-electric-mfg-llc/parameter-chart/PIM/d31dfc-millermatic-211-pro-parameter-chart-299298.pdf> |
| MILLER_RULES | <https://www.millerwelds.com/en-us/resources/knowledge-hub/mig-welding/how-to/mig-welding-setting-the-correct-parameters> |
| LINCOLN_SQW | <https://ch-delivery.lincolnelectric.com/api/public/content/582e9857a7324db29d14ceb7d16a8609?v=dfb50bd9> |
| NSRW_LC | <https://nsrw.com/wp-content/uploads/Spot-Welding-schedule-for-low-Carbon-Steel_72.pdf> |
| AWS_C11 | <https://pubs.aws.org/Download_PDFS/C1.1M_C1.1_2019_AMD1_PV.pdf> |
| TWI_UHSS | <https://www.twi-global.com/technical-knowledge/published-papers/the-resistance-spot-welding-of-high-and-ultra-high-strength-steels-november-2004> |
| EAA_RSW | <https://european-aluminium.eu/wp-content/uploads/2022/11/5-resistance-welding_2015.pdf> |
| EC9_WS | <https://wapi.gov.me/download/b0a72923-59dd-4164-9b43-b5ed6c38c0dc?version=1.0> |
| EC9_EAA | <https://european-aluminium.eu/wp-content/uploads/2022/08/design-of-aluminium-structure-introduction-to-eurocode-9-with-worked-examples-1.pdf> |
| CESTRUCO | <https://people.fsv.cvut.cz/www/wald/Leonardo-CESTRUCO/DOKUMENTS/T10-13_Aluminium_connections_revised.pdf> |
| LINCOLN_AL | <https://www.lincolnelectric.com/en/welding-and-cutting-resource-center/welding-how-tos/common-design-mistakes-in-aluminum> |
| ADM2020 | <https://www.structuremag.org/article/the-2020-aluminum-design-manual/> |
| MA2022_FSW | <https://www.mdpi.com/1996-1944/15/19/6579> |
| DP980_GMAW_RSW | <https://www.mdpi.com/2075-4701/12/6/1009> |
| ENGRXIV_HAZ | <https://engrxiv.org/preprint/download/281/721> |
| HUANG2022_DP980 | <https://iopscience.iop.org/article/10.1088/2053-1591/aca5f1> |
| CHOWDHURY2011_MG | <https://uwaterloo.ca/centre-advanced-materials-joining/sites/default/files/uploads/files/mettrans-2011_chowdhury.pdf> |
| WANG2022_MG | <https://www.mdpi.com/2075-4701/12/4/696> |
| TOLVANEN2024_TI | <https://www.mdpi.com/1996-1944/17/4/782> |
| ALTAIR_LAW59 | <https://help.altair.com/hwsolvers/rad/topics/solvers/rad/mat_law59_connect_starter_r.htm> |
| ALTAIR_FAILCONNECT | <https://help.altair.com/hwsolvers/rad/topics/solvers/rad/fail_connect_starter_r.htm> |
| ALTAIR_SPOTWELD | <https://help.altair.com/hwsolvers/rad/topics/solvers/rad/spotweld_bolt_adhesive_connect_r.htm> |
| WIKI_GAUGE | <https://en.wikipedia.org/wiki/Sheet_metal#Gauge> |
