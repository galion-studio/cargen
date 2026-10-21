<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 Galion / galion-studio -->
# Air environment and aero forces: tools and verification

Written 2026-10-21 (Europe/Zagreb). Code: `forge/scripts/air/` (Python 3.13, stdlib only). Research and sources: `research/aero.md`.
Layer: the atmosphere, humidity and force formulas are **truth-layer utilities** (definitions and standards, checked against published tables). The gust module is **play layer only**. No CFD numbers are produced here; a force is only as good as the Cd/Cl fed in, and that Cd/Cl must carry its own validation.

## Modules
| File | What | Basis |
|---|---|---|
| `isa.py` | T, p, ρ, a, μ, ν vs altitude, −5 to 32 km geopotential (or geometric), optional ISA+ΔT | U.S. Standard Atmosphere 1976 (NASA-TM-X-74335), = ICAO/ISO 2533 below 32 km |
| `humid.py` | saturation vapour pressure, humid-air density | IAPWS SR1-86(1992) eq. 1 + ideal-gas mixture |
| `forces.py` | q, drag, lift, apparent wind and yaw, road-load force and power | coefficient definitions |
| `ahmed.py` | published Ahmed-body Cd/Cl (exp + CFD), 25° and 35°, with sources; error helper | Ahmed 1984, Meile 2011, Thacker 2012, Guilmineau 2018, Gant, AhmedML |
| `gust.py` | 1-cosine discrete gust, Dryden scale lengths/intensities, first-order Dryden filter | MIL-F-8785C (aircraft spec; extrapolated to car height) |
| `cli.py` | `python -m air.cli isa 1000`, `... drag --cd 0.3 --area 2.2 --v 36.1 --wind 10 --wind-from 90`, `... ahmed 25` | |

Run the tests from `forge/scripts`: `../../.venv/bin/python -m unittest discover -s air/tests -t . -v`

## Verification results (2026-10-21): 16/16 tests pass
**ISA vs USSA-1976 Table I** (read from the scanned NASA PDF: geopotential pages 52, 54, 58 and the 21–24 km page; geometric page 55). 15 geopotential rows from −1000 m to 24 000 m covering all three layers, plus 3 geometric rows (3000, 4000, 4500 m):
- max |ΔT| = 0.00035 K (table gives 3 decimals);
- max relative pressure error 8.0e-5 (at H = −1000 m: we give 1139.29 mb, the table prints 1.1392e3 mb; the same row's torr column, 854.53 torr, is 1139.27 mb, so this is table rounding); all other rows ≤ 3.2e-5;
- max relative density error 3.8e-5 (table rounding at 5 significant figures).
- Test tolerance 1e-4 relative. Speed of sound and Sutherland viscosity use the USSA-1976 constants (γ = 1.4, β = 1.458e-6, S = 110.4 K) but are **not** checked against the table yet.

**Humidity:** IAPWS check values reproduced: p_s(273.16 K) = 611.6571 Pa (table 611.657), p_s(373.1243 K) = 101 325.015 Pa (table 101 325): both < 1e-6 relative. Example: ρ(101 325 Pa, 20 °C) = 1.20411 / 1.19885 / 1.19360 kg/m³ at RH 0 / 50 / 100%. The humid density is an ideal-gas estimate (no CIPM-2007 Z and f corrections, not validated against CIPM numbers). Below 273.16 K the code refuses unless `extrapolate=True`, and then returns `validated=False`.

**Forces:** definition checks (q·Cd·A), P_aero ∝ v³ (exact ratio 8 for 2× speed), head/tail wind add/subtract, crosswind yaw = atan(w/v), rolling term = Crr·m·g. Example: Cd 0.30, A 2.2 m², sea-level ISA, 130 km/h, still air → F_aero = 527.1 N, P_aero = 19.04 kW. The Cd and A are illustrative inputs, not data.

**Ahmed lookup:** values match the cited tables; the Ahmed 1984 25° breakdown (nose 0.020, slant 0.140, base 0.070, friction 0.055, via Gant Table 7.4) sums to 0.285.

**Gusts:** 1-cos shape end points; the Dryden filter's sampled standard deviation is within 5% of σ (200 000 steps, fixed seed).

## Physics notes for users of the numbers
- **Density:** drag scales with ρ. ISA 1000 m gives ρ = 1.1116 kg/m³ (−9.3% vs 1.2250 at sea level). ISA+15 K at sea level gives −4.9%. Humid air at 20 °C saturated: −0.9%.
- **Apparent wind:** forces use V_rel and yaw β. `road_load` takes the axial component of drag, but Cd must be Cd(β) from CFD or test at that yaw. The tool does not invent a yaw correction. Open yawed validation data is a gap.
- **Ground:** quote the ground boundary condition with every Cd/Cl (fixed no-slip floor like AhmedML, tunnel boundary layer like DrivAerML, or a moving ground at road speed). Lift and downforce are most sensitive to it.
- **Reynolds number:** Ahmed experiments sit at Re_L 2.78e6 (Meile, Lienhart & Becker, AhmedML) and 4.29e6 (Ahmed 1984). Use ν from `isa()` to match Re when comparing.
- **Gusts in the game:** `one_minus_cos` and `DrydenU` drive play-layer wind. Their outputs feed the game only and are never reported as measured or validated wind loads.
