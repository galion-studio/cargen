<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 Galion / galion-studio -->
# Aero (air only): solvers, turbulence models, validation data, air environment

Compiled 2026-10-21 17:30–18:30 +02:00 (Europe/Zagreb). Scope: external aerodynamics and the air around the car. No liquids, cooling, fuel or other fluid systems. Licence classes follow research/licences.md (MIT/Apache/BSD clean; LGPL as a process; GPL servers only; AGPL unmodified only; NC = banned).
Numbers below are copied from the cited source. Where a value is quoted second-hand it says so.

## 1. Solvers
| Solver | Licence (checked) | SaaS verdict | Car-aero capability | Source |
|---|---|---|---|---|
| **SU2 8.5.0 "Harrier"** (2026-04-27) | LGPL-2.1-or-later (licences.md); GitHub API reports NOASSERTION | ✅ separate process | INC_RANS (incompressible, right for road speeds), SA and SST (V1994m/V2003m); hybrid RANS-LES only SA-based (`HYBRID_RANSLES = SA_DES, SA_DDES, SA_ZDES, SA_EDDES`, config_template.cfg v8.5.0): no SST-IDDES. Moving ground / wheels via `SURFACE_MOVEMENT= MOVING_WALL` + `TRANSLATION_RATE` / `ROTATION_RATE`; wall functions and roughness available. Prebuilt Linux OpenMP and MPI binaries | https://github.com/su2code/SU2/releases/tag/v8.5.0 , https://raw.githubusercontent.com/su2code/SU2/v8.5.0/config_template.cfg |
| OpenFOAM (ESI v2212 used by AhmedML/DrivAerML; Foundation -dev) | GPL-3.0-or-later | ⚠ servers only, never shipped | The tool behind both CC-BY-SA reference datasets (pimpleFoam, SA-DDES, snappyHexMesh). Case setups are published with AhmedML, so it is the shortest path to reproduce the reference data | https://github.com/OpenFOAM/OpenFOAM-dev ; arXiv:2407.20801 |
| waLBerla 7.3 (2026-07-21) | GPL-3.0-or-later (Zenodo record, walberla.net) | ⚠ servers only | LBM (cumulant K17 via lbmpy), CPU+CUDA, mesh refinement | https://zenodo.org/records/21534169 , https://www.walberla.net/ |
| OpenLB 1.8.1 (2025-05-16; newest found) | GPL-2.0-or-later | ⚠ servers only | LBM, CPU/GPU | https://www.openlb.net/download/ , https://zenodo.org/records/15440776 |
| Palabos | AGPL-3.0 (licences.md) | ⚠⚠ unmodified only | LBM | https://gitlab.com/unigespc/palabos |
| FluidX3D | Custom: "Commercial use is not allowed", no AI training on its code, no military use (LICENSE.md, read 2026-10-21) | ❌ **banned** | GPU LBM | https://github.com/ProjectPhysX/FluidX3D/blob/master/LICENSE.md |
| NVIDIA PhysicsNeMo v2.2.2 (2026-09-11; formerly Modulus) | Apache-2.0 (GitHub API) | ✅ | ML surrogates (e.g. trained on DrivAerML); outputs are surrogates, never truth-layer numbers | https://github.com/NVIDIA/physicsnemo , https://github.com/NVIDIA/physicsnemo-cfd (Apache-2.0) |
| NVIDIA Warp v1.18.0 (2026-10-05) | Apache-2.0 (GitHub API) | ✅ | GPU kernels in Python; candidate to write our own LBM/game-wind kernels behind the `Compute` trait | https://github.com/NVIDIA/warp |

**Recommended path.** (1) Truth layer default: SU2 INC_RANS + SST as a separate process (LGPL, clean), meshes from Netgen/fTetWild/Gmsh-on-server. (2) Reference check, server only: OpenFOAM with the published AhmedML case to reproduce AhmedML's own numbers before trusting our SU2 setup. (3) Scale-resolving runs (SA-DDES in SU2, or OpenFOAM) only on rented compute: AhmedML needed ~184 CPU node-hours per case, DrivAerML ~40 h on 1536 cores. (4) GPU later behind `Compute`: PhysicsNeMo surrogates trained on CC-BY-SA data (ShareAlike applies to adapted data), Warp kernels. LBM codes are all GPL/AGPL or banned, so they stay server-side options only.

### SU2 on this box (CPU, 8 cores, 15 GB; box shared and loaded, load average ~23–26)
- Installed: `SU2-v8.5.0-linux64-omp.zip` from the release page, sha256 `aadc800cd9df34deff99d4725f5897f620c9f2979f62ab235313311bf501f09b`, unpacked in `third_party/su2/` (gitignored, not vendored). `SU2_CFD --help` runs.
- QuickStart (inviscid NACA0012, M 0.8, AoA 1.25°, 5233 points; `QuickStart/inv_NACA0012.cfg` at tag v8.5.0): converged to RMS density 1e-8 in 162 iterations, **4.9 s wall, 41 MB RSS, 1 thread**, CL = 0.328486, CD = 0.021481. Smoke test only (Euler, transonic, not car aero). A first run with `-t 8` on the loaded box crawled (oversubscribed); use few threads when other agents run.
- SST incompressible flat plate (Tutorials `Inc_Turbulent_Flat_Plate`, 545×385 grid = 208 896 cells, Re = 5e6/m; we switched SA→SST): see docs/physics/air-environment.md §6 for the result and status. Reference: NASA TMR SST-Vm on the same grid, CD = 0.00285332 (CFL3D) / 0.0028442 (FUN3D), Cf(x=0.97) = 0.00269085 / 0.00269055 (https://tmbwg.github.io/turbmodels/FlatPlate/SST/drag_convergence_sstv.dat and cf_convergence_sstv.dat). TMR notes compressible M=0.2 vs incompressible may differ slightly.

## 2. Turbulence modelling and typical Cd error
| Case | Method | Cd CFD | Cd exp | Error | Source |
|---|---|---|---|---|---|
| Ahmed 25° | k-ω SST (ISIS-CFD) | 0.3218 | 0.285 (Ahmed 1984) / 0.299 (Meile) / 0.384 (Thacker) | +12.9% / +7.6% / −16.2% | Guilmineau et al. 2018, Table 6 (CC BY 4.0) |
| Ahmed 25° | EARSM | 0.2804 | same | −1.6% / −6.2% / −27% | same |
| Ahmed 25° | DES / IDDES | 0.4371 / 0.3802 | same | IDDES −1.0% vs Thacker, +33% vs Ahmed | same |
| Ahmed 35° | k-ω SST | 0.2999 | 0.258 (Ahmed) / 0.279 (Meile) | +16.2% / +7.5% | Guilmineau 2018, Table 4 |
| Ahmed 35° | IDDES | 0.3452 | same | +33.8% / +23.7% | same |
| Ahmed 25° | RSM (Fluent), 4.5–5 M cells | 0.295 | 0.299 (Meile) | −1.3% | Meile et al. 2011, Fig. 4 |
| Ahmed 35° | RSM (Fluent) | 0.276 | 0.279 | −1.1% | same |
| Ahmed 25° | OpenFOAM SA-DDES, 3.5 / 10.1 / 21.3 / 31.5 M cells | 0.303 / 0.293 / 0.285 / 0.280 | 0.299 (Meile) | +1.3% … −6.4% (grid-dependent) | AhmedML, arXiv:2407.20801 Table 1 |
| Ahmed 25° | linear/realizable k-ε (with stilt allowance) | 0.309–0.311 | 0.285 | +8.4 … +9.1% | Gant thesis Table 7.3 |
| DrivAer notchback (Ford OCDA, case 2a) | OpenFOAM HRLES (SA-DDES variant), ~160 M cells | 0.274 | 0.255 (Hupertz et al. 2021) | +7.5% (+19 counts) | DrivAerML, arXiv:2408.11969 SI Table 1 |
| same, ΔCd from wheel deflectors (2b−2a) | HRLES | −0.007 | −0.013 | sign right, half the size | same |

Takeaways: (a) The 25° Ahmed is the hard case: RANS misses the slant bubble (Guilmineau 2018: "only the IDDES … predicts the recirculation bubble"), so a good Cd from RANS can be right for the wrong reason; Gant shows a k-ε variant at 0.4% error with the wrong (fully separated) flow. Always check the drag breakdown and Cp, not Cd alone. (b) The experiments themselves disagree by up to 35% at 25° (0.285–0.384), so a validation claim must name the experiment. (c) Realistic expectation for RANS SST on cars: several to ~15% Cd error; scale-resolving methods reach a few % on fine grids at ~10–100× the cost.

## 3. Validation data (open, commercial-OK)
- **AhmedML** (CC-BY-SA-4.0): 500 geometric Ahmed variants, OpenFOAM v2212 SA-DDES, 15–20 M cells, Re_L 2.78e6, stilts removed, body 0.05 m above a no-slip floor; includes case setup, STL, surface/volume fields, forces. https://huggingface.co/datasets/neashton/ahmedml , paper arXiv:2407.20801.
- **DrivAerML** (CC-BY-SA-4.0): 500 DrivAer notchback variants, HRLES, ~160 M cells, static wheels, U = 38.889 m/s, ρ = 1 kg/m³ normalisation, A_ref constant 2.17 m² in `force_mom_constref_i.csv`. https://huggingface.co/datasets/neashton/drivaerml , arXiv:2408.11969. Geometry derives from the Ford OCDA DrivAer; the dataset licence covers the published files, but the TUM DrivAer CAD itself still needs TUM permission (licences.md).
- **Lienhart & Becker (2003)**, SAE 2003-01-0656: LDA velocity and Reynolds-stress profiles on the slant and in the wake, 25° and 35°, U = 40 m/s, Re_H 7.68e5; distributed via ERCOFTAC Classic Collection case 082 / KBwiki (CC-BY-4.0 on KBwiki "unless otherwise indicated"; site returned 502 today, so file-level terms not re-checked). http://cfd.mace.manchester.ac.uk/ercoftac/doku.php?id=cases:case082
- **Force data:** Ahmed et al. 1984 (SAE 840300, paywalled; values quoted via Guilmineau 2018 and Gant), Meile et al. 2011 (open PDF, CFD Letters; journal licence not stated on the article page; we use the facts with citation), Thacker et al. 2012 (via Guilmineau 2018). Coded in `forge/scripts/air/ahmed.py`.
- **Verification (code correctness, not validation):** NASA TMR flat plate (public US Gov site, now mirrored at tmbwg.github.io), SU2 V&V page https://su2code.github.io/vandv/Flat_Plate/.
- Excluded: DrivAerNet/DrivAerNet++ and the Loughborough DrivAer set (CC-BY-NC), FluidX3D (NC licence).

## 4. Air environment
- **Atmosphere:** U.S. Standard Atmosphere 1976 (NASA-TM-X-74335, public domain; equal to ICAO/ISO 2533 below 32 km). https://ntrs.nasa.gov/citations/19770009539 . Implemented to 32 km and checked against its Table I (docs/physics/air-environment.md). Density at 1000 m is 1.1116 kg/m³ vs 1.2250 at sea level: drag falls 9.3% at the same airspeed.
- **Humidity:** water vapour (M = 18.015 g/mol) is lighter than dry air (28.964 g/mol), so humid air is less dense. Saturation pressure from IAPWS SR1-86(1992) (https://iapws.org/technical-guidance/release/Supp-sat), valid ≥ 273.16 K over liquid water. Our ideal-gas mix gives ρ(20 °C, 101 325 Pa) = 1.20411 / 1.19885 / 1.19360 kg/m³ at RH 0/50/100%, i.e. −0.9% at saturation. The CIPM-2007 equation (Picard et al. 2008, Metrologia 45:149) adds compressibility and enhancement factors; not implemented, so the humid value is an ideal-gas estimate.
- **Crosswind and yaw:** the apparent wind is car velocity minus wind velocity; yaw β = atan(cross/axial). Cd, Cl, side force and yaw moment all depend on β, so Cd(β) must come from CFD or test at that β; the tool never extrapolates. The open force sets used here are all at β = 0° (Meile et al. 2011 measured at β = 0°), and DrivAerML lists yaw as future work, so yawed validation data is a gap to fill.
- **Ground effect and moving ground:** wind tunnels and CFD differ in ground treatment. AhmedML uses a no-slip fixed floor (as in the original tunnel test); DrivAerML mimics the Pininfarina tunnel's ground boundary layer with static wheels, and lists moving ground and rotating wheels as not covered. Our SU2 runs must state their ground BC (slip, no-slip static, or moving at road speed via MOVING_WALL) and compare only like for like.
- **Gusts (play layer only):** MIL-F-8785C discrete 1-cosine gust and Dryden low-altitude spectra (US mil spec; formulas as documented by MathWorks https://www.mathworks.com/help/aeroblks/discretewindgustmodel.html and …/drydenwindturbulencemodelcontinuous.html). Written for aircraft above ~10 ft, so at car height they are an extrapolation, fine for game feel and never reported as truth. ISO 12021 (road-vehicle lateral-wind sensitivity) and ESDU wind data are paywalled and were not used.

## 5. Validation plan (aero sector)
1. **V0 verification (box, minutes to hours):** SU2 INC_RANS SST flat plate on the TMR grid family; target CD and Cf(0.97) within 1% of CFL3D/FUN3D on the finest grid (TMR GCI ~0.3%). Run to a real convergence criterion (the first attempt stopped at a dimensional-pressure residual of 1e-10 after 74 iterations with drag still moving; see doc).
2. **V1 Ahmed 25° and 35°, RANS SST, SU2, Re_L 2.78e6, U = 40 m/s, A = 0.112 m²:** report Cd, Cl, drag breakdown (nose/slant/base/friction) and slant Cp against Meile 2011 (forces) and Lienhart & Becker (profiles); compare with the published SST numbers (Guilmineau 0.3218 / 0.2999). Pass means the error is within the published SST spread and the slant flow state is reported honestly. Mesh study at three levels with GCI. Needs a geometry from the open Ahmed drawing and ~5–20 M cells: rented compute, or a coarse level on the box.
3. **V2 cross-code:** reproduce the AhmedML baseline with the published OpenFOAM setup (server only) and compare against SU2 on the same mesh family.
4. **V3 scale-resolving:** SU2 SA-DDES vs AhmedML (Cd 0.285 at 21.3 M cells), then DrivAerML baseline vs Ford experiment (Cd 0.255) on rented A100/CPU nodes after Mate approves spend.
5. **Only then** generated cars: every Cd/Cl carries solver, version, mesh, turbulence model, ground BC and its V1–V3 error band; otherwise "unvalidated estimate".
