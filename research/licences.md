<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 Galion / galion-studio -->
# Open-source building blocks: licences and maturity (cargen)

Compiled 2026-10-21 16:55 +02:00 (Europe/Zagreb). Read-only web research; nothing installed, nothing signed up for.
Separate from obsidian-open-mind / Wave 4.

## How this was checked
- Licence: read from the project's own LICENSE / COPYING file (raw file on GitHub/GitLab) or its official site. The SPDX id is my mapping of that text. Where only the full licence text was found and no "or later" wording, I note `only/or-later not verified`.
- Latest release and date: the project's own releases/tags feed (dates are release dates, UTC calendar day). Last commit: the default-branch commit feed on 2026-10-21.
- Contributors: GitHub API contributor count (including anonymous) where the unauthenticated rate limit allowed; otherwise `not found`.
- "Not found" means I could not verify it on a primary source today. It does not mean the thing is absent.
- This is engineering research, not legal advice. Before launch, get a lawyer to review the copyleft items marked ⚠.

## Licence rule applied (from Mate)
| Class | SPDX examples | Hosted SaaS verdict |
|---|---|---|
| Permissive | MIT, Apache-2.0, BSD-2/3-Clause, Zlib, 0BSD, MPL-2.0 (file-level copyleft) | ✅ Clean. Keep notices; Apache-2.0 includes a patent grant and a patent-retaliation clause |
| Weak copyleft | LGPL-2.1, LGPL-3.0 | ✅ Fine as a dynamic library or separate process. If you modify the library and distribute it, you must publish those modifications |
| Strong copyleft | GPL-2.0, GPL-3.0 | ⚠ OK when it runs only on our servers and is never distributed (no binaries to customers, no on-prem build, no desktop app). Flagged |
| Network copyleft | AGPL-3.0 | ⚠⚠ If we modify it, §13 requires offering the modified source to users who interact with it over the network. Unmodified, as a separate process (input deck in, results out, no linking), the risk is low. Any patch we make must be published or kept upstream. Flagged |
| Non-commercial / custom | CC-BY-NC, "non-commercial" clauses, site terms | ❌ Blocks commercial use without a separate licence |

---

## ⚠ Major finding: OpenRadioss is gone and continues as OpenCourant
- Siemens (which acquired Altair) discontinued OpenRadioss on 2026-10-01. The website was retired and github.com/OpenRadioss/OpenRadioss returns 404 (I confirmed the 404 from the box). Sources: https://www.phoronix.com/news/Siemens-Ends-OpenRadioss and https://opencourant.org/
- Community continuation: **OpenCourant**, https://github.com/OpenCourant/OpenCourant, AGPL-3.0 (LICENSE.md verified). It is an Incubator Project of the Rocky Enterprise Software Foundation. The tag `openradioss-final` is dated 2026-10-08; the first stable build `20261011` is dated 2026-10-11; there was a commit on 2026-10-21; about 50 contributors on GitHub. Its README says Starter natively reads the LS-DYNA `.k`/`.key` format.
- Impact on PLAN.md: replace "OpenRadioss" with "OpenCourant (ex-OpenRadioss)". The fork is only 3 weeks old, so continuity risk is real. Pin a known build and keep our own mirror of the source, which AGPL allows. The AGPL obligations are unchanged.

---

## 1. Explicit crash and impact FE solvers
| Project | SPDX | Commercial SaaS? | Obligations | Maturity | Validation / users | Lang / Rust | Source |
|---|---|---|---|---|---|---|---|
| **OpenCourant** (ex-OpenRadioss) | AGPL-3.0 (only/or-later not verified) | ⚠⚠ Yes as an unmodified separate process; modifications must be offered to network users | AGPL §13, copyleft, no patent grant beyond the GPLv3 patent clause (§11) | Radioss code base opened as OpenRadioss in 2022 (original repo created 2022-05-10); fork 2026-10-01; latest stable build 2026-10-11; active (commit 2026-10-21); ~50 contributors | Inherits the Radioss QA suite; the fork says its builds are "gated on the same regression suite". No fork-specific published benchmarks found | Fortran/C/C++; no Rust bindings (run as a process) | https://github.com/OpenCourant/OpenCourant |
| Kratos Multiphysics (incl. explicit structural apps) | BSD-3-Clause for the core (kratos/license.txt, CIMNE); each application has its own licence file | ✅ (check each app's licence) | Attribution | Latest v10.4.4 on 2026-10-06; very active (commit 2026-10-21); ~300 contributors; 111,974 commits | not found (no crash-specific validation verified) | C++ core, Python API; no Rust | https://github.com/KratosMultiphysics/Kratos |
| Akantu (EPFL, explicit dynamics, cohesive fracture) | LGPL-3.0 (README badge "LGPLv3"; LICENSE file not read) | ✅ As a lib or process | LGPL | Tags: v5.0.7-post1 on 2024-09-20; GitLab activity 2026-10-21; contributors not found | JOSS paper (badge); no crash benchmarks found | C++/Python | https://gitlab.com/akantu/akantu |
| OOFEM | LGPL-2.1 (only/or-later not verified) | ✅ | LGPL | v3.0 on 2025-12-29 (previous release v2.5 in 2020); commit 2026-10-09 | not found | C++/Python | https://github.com/oofem/oofem |
| MOOSE (INL; explicit time integration in solid mechanics) | LGPL-2.1 (LICENSE + COPYING) | ✅ | LGPL | Release 2026-09-25; very active (commit 2026-10-21); 67,545 commits | Nuclear-industry use at INL (COPYRIGHT file); no crash validation found | C++ | https://github.com/idaholab/moose |
| FEBio (biomechanics, large deformation, dynamic) | MIT | ✅ | Attribution | 4.13 on 2026-08-04; commit 2026-10-13 | Biomechanics verification suite (not checked in detail) | C++ | https://github.com/febiosoftware/FEBio |
| Peridigm (Sandia peridynamics: fracture, impact) | BSD-3-Clause | ✅ | Attribution | No release feed; last commit 2026-02-25 (low activity) | not found | C++ (Trilinos) | https://github.com/peridigm/peridigm |
| code_aster (DYNA_NON_LINE, explicit schemes) | GPL-3.0 (LICENSE in the GitLab repo) | ⚠ Servers only | GPL | See category 2 | EDF nuclear/industrial use | Fortran/C/Python | https://gitlab.com/codeaster/src |

**Top pick, best overall: OpenCourant.** It is the only open-source code in the list with production crash heritage (Radioss), LS-DYNA deck input, and the material, contact and airbag models a P1b Yaris run needs. It is AGPL-3.0, so run it unmodified in a separate process. If we patch it, publish the patches.
**Best clean-for-SaaS crash option: none of equal capability.** Kratos (BSD-3) is the strongest permissive multiphysics framework, but crash use would be R&D, not reproducing NHTSA tests. **Blocker:** no permissive, production-grade explicit crash solver exists. Our crash layer either accepts AGPL as a separate process or we build our own.

## 2. Implicit FE, structural and stiffness solvers
| Project | SPDX | Commercial SaaS? | Obligations | Maturity | Validation / users | Lang / Rust | Source |
|---|---|---|---|---|---|---|---|
| **MFEM** (LLNL) | BSD-3-Clause | ✅ | Attribution | v4.10 on 2026-09-01; active (commit 2026-10-20); ~257 contributors | DOE lab use (LLNL) | C++; no official Rust | https://github.com/mfem/mfem |
| **deal.II** | Apache-2.0 WITH LLVM-exception OR LGPL-2.1-or-later (dual) | ✅ Choose Apache-2.0 | Attribution, Apache patent clause; the project asks for citation | 9.8.0 on 2026-08-09; very active; ~412 contributors; 68,410 commits | Large academic user base; tutorial-validated | C++ | https://github.com/dealii/dealii |
| FEniCSx (DOLFINx) | LGPL-3.0-or-later (COPYING.LESSER + COPYING GPL-3.0) | ✅ As a library | LGPL | v0.11.0 on 2026-06-09; active (commit 2026-10-19) | Academic | C++/Python | https://github.com/FEniCS/dolfinx |
| CalculiX (ccx) | GPL-2.0 (the site links the GPL v2 text; or-later not verified) | ⚠ Servers only | GPL | 2.23 (Oct/Nov 2025, per the dhondt.de README and search); maintenance moving to an MTU team (2026, forum) | Thanks MTU Aero Engines (site); Abaqus-like input deck | C/Fortran; no Rust | http://www.dhondt.de/ |
| code_aster (EDF) | GPL-3.0 (LICENSE) | ⚠ Servers only | GPL | Stable 17.x (tag 17.5.8 on 2026-10-16), dev 18.1.11 (2026-10-16); active | EDF industrial/nuclear; large V&V test base | Fortran/C/Python | https://gitlab.com/codeaster/src |
| Elmer FEM | Mixed: ElmerSolver library LGPL, GUI/Grid/most modules GPL (ElmerLicensePolicy.md; LICENSE.md is GPL-2.0) | ⚠ Mixed. GPL parts servers only | GPL/LGPL | v26.2.1 on 2026-07-30; commit 2026-10-20 | CSC Finland | Fortran/C++ | https://github.com/ElmerCSC/elmerfem |
| Kratos StructuralMechanics | BSD-3-Clause (core) | ✅ | Attribution | See category 1 | not found | C++/Python | https://github.com/KratosMultiphysics/Kratos |
| SfePy | BSD-3-Clause (LICENSE text) | ✅ | Attribution | 2026.3 on 2026-09-29 | Academic | Python | https://github.com/sfepy/sfepy |
| Rust: fenris | MIT OR Apache-2.0 | ✅ | Attribution | crate 0.0.33, last commit 2023-09-25 (stale) | Research code | Rust | https://github.com/InteractiveComputerGraphics/fenris |
| Rust: pmsim + russell (cpmech) | MIT | ✅ | Attribution | russell v4.0.0 on 2026-10-21; pmsim last release 2023 (commit 2026-10-20); single main author | not found | Rust | https://github.com/cpmech/pmsim |
| Rust: faer (sparse/dense linear algebra) | MIT | ✅ | Attribution | 0.24.4 (2026-06/07); 5.2M crate downloads | Published benchmarks on the repo (not checked) | Rust | https://codeberg.org/sarah-quinones/faer |

**Top pick (clean and best overall for building our own stiffness/modal pipeline): MFEM (BSD-3)**, with deal.II (Apache-2.0 option) as an equal alternative.
**Best "ready-to-run solver" with industrial decks: code_aster (GPL-3.0) or CalculiX (GPL-2.0)**, both ⚠ servers only. No Rust FE crate is production-grade; use Rust for orchestration plus faer/russell for linear algebra.

## 3. CFD and aero
| Project | SPDX | Commercial SaaS? | Obligations | Maturity | Validation / users | Lang / Rust | Source |
|---|---|---|---|---|---|---|---|
| OpenFOAM (Foundation, openfoam.org) | GPL-3.0-or-later (COPYING: "version 3 ... or any later version") | ⚠ Servers only | GPL; "OpenFOAM" is a trademark (naming rules) | Dated snapshot 2026-09-07; very active (commit 2026-10-21) | Widely used in automotive (the AhmedML/DrivAerML datasets were generated with OpenFOAM) | C++ | https://github.com/OpenFOAM/OpenFOAM-dev |
| OpenFOAM (ESI/OpenCFD, openfoam.com) | GPL-3.0 assumed. COPYING could not be read (GitLab sign-in wall), so **not verified** | ⚠ Servers only | GPL + trademark | v2606 released 2026-06-26 (openfoam.com news) | AhmedML used v2212 | C++ | https://www.openfoam.com/ |
| **SU2** | LGPL-2.1-or-later (LICENSE + source header "or any later version") | ✅ As a separate process | LGPL | 8.5.0 "Harrier" on 2026-04-28; ~239 contributors; last default-branch commit 2026-04-28 (development on the develop branch not checked) | V&V cases (not checked in detail) | C++/Python | https://github.com/su2code/SU2 |
| PyFR (high-order LES) | BSD-3-Clause | ✅ | Attribution | v3.1 on 2026-03-13; commit 2026-10-21 | Imperial College | Python + GPU kernels | https://github.com/PyFR/PyFR |
| NekRS (spectral element, GPU) | BSD-3-Clause (ANL text) | ✅ | Attribution, DOE notice | v26.0 on 2026-01-27 | ANL/DOE | C++/OCCA | https://github.com/Nek5000/nekRS |
| code_saturne (EDF) | GPL-2.0 (only/or-later not verified) | ⚠ Servers only | GPL | v9.2.0 on 2026-07-06 | EDF | C/Fortran | https://github.com/code-saturne/code_saturne |
| Palabos (LBM) | AGPL-3.0 (COPYING) | ⚠⚠ AGPL | AGPL | GitLab activity 2026-07-28 | Academic | C++ | https://gitlab.com/unigespc/palabos |
| Nalu-Wind (Exawind) | BSD-3-Clause (NTESS text) | ✅ | Attribution | v2.7.1 on 2026-04-01 | Wind energy, DOE | C++ | https://github.com/Exawind/nalu-wind |

**Validation data (aero)**
| Dataset | Licence / terms | Commercial use? | Source |
|---|---|---|---|
| DrivAer geometry (TU Munich, 2011) | No open licence. Free download after registration; the form makes you confirm you will use the data "only for the stated purpose", not share it with third parties, and always credit TUM AER as the author | ⚠ Unclear. Needs written permission from TUM before commercial or SaaS use or redistribution | https://www.epc.ed.tum.de/en/aer/research-groups/automotive/drivaer/download/ |
| DrivAerML (500 CFD variants, HF) | CC-BY-SA-4.0 (LICENSE.txt) | ✅ With attribution and ShareAlike on adapted data | https://huggingface.co/datasets/neashton/drivaerml |
| AhmedML (500 Ahmed variants) | CC-BY-SA-4.0 | ✅ Attribution + ShareAlike | https://huggingface.co/datasets/neashton/ahmedml |
| DrivAerNet / DrivAerNet++ (MIT) | CC-BY-NC-4.0 (code MIT) | ❌ Explicitly bans commercial use, ML training for commercial tools, and running simulations on its geometries | https://github.com/Mohamedelrefaie/DrivAerNet |
| DrivAer wind-tunnel dataset (Loughborough) | CC-BY-NC-4.0 | ❌ Non-commercial | https://repository.lboro.ac.uk/articles/dataset/DrivAer_model/26096761 |
| Ahmed body experiments (ERCOFTAC case 082, LSTM) | KBwiki says CC-BY-4.0 "unless otherwise indicated". The Classic Collection page states no licence | ✅ Probably (KBwiki CC-BY-4.0). Confirm for the Classic Collection files | http://cfd.mace.manchester.ac.uk/ercoftac/doku.php?id=cases:case082 |

**Top pick, clean for SaaS: SU2 (LGPL-2.1-or-later) as a separate process.** **Best overall for automotive external aero: OpenFOAM (GPL-3.0)**, ⚠ servers only. Validate on AhmedML/DrivAerML (CC-BY-SA). Do not use DrivAerNet++ (NC), and get TUM's permission before relying on the DrivAer CAD.

## 4. CAD kernels and meshing
| Project | SPDX | Commercial SaaS? | Obligations | Maturity | Validation / users | Lang / Rust | Source |
|---|---|---|---|---|---|---|---|
| **Open CASCADE Technology (OCCT)** | LGPL-2.1-only WITH OCCT-exception-1.0 (LICENSE_LGPL_21.txt + OCCT_LGPL_EXCEPTION.txt) | ✅ Dynamic lib | LGPL; the exception allows header inclusion; give notice | V8_0_1 on 2026-07-30; active (commit 2026-10-20) | Used by FreeCAD, CadQuery, build123d, Gmsh | C++; Rust: `opencascade` crate (LGPL-2.1, v0.3 Aug 2026, small) | https://github.com/Open-Cascade-SAS/OCCT |
| CadQuery | Apache-2.0 | ✅ | Attribution | 2.8.0 on 2026-06-22 | — | Python on OCCT | https://github.com/CadQuery/cadquery |
| build123d | Apache-2.0 | ✅ | Attribution | v0.13.0 on 2026-09-21; very active | — | Python on OCCT | https://github.com/gumyr/build123d |
| FreeCAD | LGPL-2.1 (or-later per headers not verified) | ✅ As a process | LGPL | 26.3 RC2 on 2026-10-18; very active | Large community | C++/Python | https://github.com/FreeCAD/FreeCAD |
| Gmsh | GPL-2.0-or-later with a linking exception for Netgen/METIS/OCCT/ParaView (LICENSE.txt) | ⚠ Servers only (as a process or linked) | GPL | 4.15.2 on 2026-03-24 | Very widely used | C++; APIs for C/Python/Julia; Rust `gmsh-sys` 0.1.2 (2019, stale) | https://gmsh.info/ |
| Netgen | LGPL-2.1 (only/or-later not verified) | ✅ | LGPL | v6.2.2608 on 2026-10-01 | Used by NGSolve, Gmsh | C++/Python | https://github.com/NGSolve/netgen |
| TetGen | AGPL-3.0 (v1.5+, LICENSE; v1.4.3 was MIT with a non-commercial clause); commercial licence from WIAS | ⚠⚠ AGPL, or buy a licence | AGPL | v1.6.1 on 2026-09-17 | Widely cited (ACM TOMS 2015) | C++ | https://github.com/TetGen/TetGen |
| fTetWild | MPL-2.0 (LICENSE.MPL2) | ✅ | File-level copyleft | No releases; commit 2026-09-23 | Robust tet meshing (paper) | C++ | https://github.com/wildmeshing/fTetWild |
| Manifold (mesh booleans) | Apache-2.0 | ✅ | Attribution | v3.5.4 on 2026-09-25 | not found | C++; Rust crates manifold3d / manifold-rs (MIT OR Apache-2.0) | https://github.com/elalish/manifold |
| Rust: truck (B-rep) | Apache-2.0 | ✅ | Attribution | Crates v0.6.0 (2024-09-20); commit 2026-10-19 | — | Pure Rust, STEP I/O | https://github.com/ricosjp/truck |
| Rust: Fornjot | 0BSD | ✅ | None | ⚠ **Repo archived**; last release v0.49.0 (2024-03-21) | — | Rust | https://github.com/hannobraun/fornjot |
| Rust: csgrs | MIT | ✅ | Attribution | v0.20.1 (2025-07-24); commit 2026-10-20 | — | Rust | https://github.com/timschmidt/csgrs |
| libfive (SDF) | MPL-2.0 library and Python bindings; GPL-2.0-or-later Studio/Guile | ✅ Library only | MPL | No recent releases; commit 2026-10-16 | — | C++ | https://github.com/libfive/libfive |

**Top pick: OCCT (LGPL-2.1 + exception) through build123d/CadQuery (Apache-2.0).** It is clean when OCCT is linked dynamically. Meshing pick, clean: **Netgen (LGPL) + fTetWild (MPL-2.0)**. Best overall mesher: **Gmsh**, ⚠ GPL, servers only. Avoid TetGen (AGPL) unless we buy a licence. Rust-native: truck is the only live B-rep crate. Fornjot is archived.

## 5. Multibody and vehicle dynamics
| Project | SPDX | Commercial SaaS? | Obligations | Maturity | Validation / users | Lang / Rust | Source |
|---|---|---|---|---|---|---|---|
| **Project Chrono** (incl. Chrono::Vehicle) | BSD-3-Clause | ✅ | Attribution | 10.0.0 on 2026-04-07 (+877 commits since); active (commit 2026-10-21); ~156 contributors | Validation page (vs ADAMS/Car, tires); US Army GVSC listed as a user; Army "Mercury" mobility tool built on Chrono::Vehicle (SAE 2017-01-0273, 2024-01-3841) | C++, PyChrono; no Rust | https://github.com/projectchrono/chrono |
| MuJoCo | Apache-2.0 | ✅ | Attribution, patent grant | 3.16.0 on 2026-10-14; very active; ~177 contributors | Robotics research (DeepMind) | C/C++/Python; Rust `mujoco-rs` 6.1.0 (MIT OR Apache-2.0, 2026-09-22) | https://github.com/google-deepmind/mujoco |
| Drake (TRI) | BSD-3-Clause | ✅ | Attribution | v1.58.0 on 2026-10-15 | Robotics | C++/Python | https://github.com/RobotLocomotion/drake |
| Simbody | Apache-2.0 | ✅ | Attribution | 3.8 on 2025-05-17 | OpenSim biomechanics | C++ | https://github.com/simbody/simbody |
| DART | BSD-2-Clause | ✅ | Attribution | 6.20.2 on 2026-10-19 | Robotics | C++/Python | https://github.com/dartsim/dart |
| Exudyn | BSD-3-Clause-style "EXUDYN General License 1.0" (custom text, not an SPDX id) | ✅ Probably; custom text needs review | Attribution | v1.13.6 on 2026-10-09 | Univ. Innsbruck | C++/Python | https://github.com/jgerstmayr/EXUDYN |
| CARLA (driving simulator) | MIT (code); assets may carry other licences | ✅ Code | Attribution | 0.10.0 (2026-09-07) / 0.9.16 | AV research | C++/Python (Unreal) | https://github.com/carla-simulator/carla |

**Top pick: Project Chrono (BSD-3)**. It is clean and also the best overall for vehicle-dynamics truth checks. It is the only candidate here with a vehicle module and published vehicle validation.

## 6. Game engines and real-time physics
| Project | SPDX | Commercial SaaS? | Obligations | Maturity | Lang / Rust | Source |
|---|---|---|---|---|---|---|
| **Bevy** | MIT OR Apache-2.0 | ✅ | Attribution | v0.20.0 on 2026-10-08; ~1,698 contributors; 8.2M crate downloads | Rust | https://github.com/bevyengine/bevy |
| **Rapier** | Apache-2.0 | ✅ | Attribution, patent | 0.36.1 on 2026-10-06; ~84 contributors; 1.9M downloads | Rust (bevy_rapier) | https://github.com/dimforge/rapier |
| Avian | MIT OR Apache-2.0 | ✅ | Attribution | v0.8.0 on 2026-10-20 (repo moved to avianphysics/avian); ~96 contributors | Rust, Bevy-native ECS physics | https://github.com/avianphysics/avian |
| Jolt Physics | MIT | ✅ | Attribution | 5.6.0 on 2026-07-11; commit 2026-10-18; ~93 contributors | C++. **Rust: `oxijolt` 1.1.0+jolt-5.6.0 (MIT OR Apache-2.0, created 2026-10-04, 2k downloads: very new)**; older `rolt`/`joltc-sys` 0.3.1 (Jolt 5.0, last 2024-05) | https://github.com/jrouwe/JoltPhysics |
| Bullet3 | Zlib (except Extras/ThirdPartyLibs) | ✅ | Notice | Last tagged release 3.24 (2022-04) / PyBullet 3.2.5 (2023-01); occasional commits (2026-10-09) | C++. **Rust: no maintained binding.** `rubullet` 0.1.0-alpha-3 (MIT, last 2021-06) | https://github.com/bulletphysics/bullet3 |
| NVIDIA PhysX 5 | BSD-3-Clause | ✅ | Attribution | ovphysx 0.7.0 on 2026-10-15 | C++. **Rust: `physx`/`physx-sys` (EmbarkStudios) archived, last 2023-10, targets PhysX 5.1** | https://github.com/NVIDIA-Omniverse/PhysX |
| Godot | MIT | ✅ | Attribution | 4.7.2 on 2026-08-22 | C++/GDScript (Rust via godot-rust, not checked) | https://github.com/godotengine/godot |

**Top pick: Bevy + Rapier** (or Avian for ECS-native code), all permissive. This confirms PLAN Q5: Bullet has no maintained Rust binding. Jolt is the best non-Rust engine, and oxijolt is promising but only 2 weeks old.

## 7. Crash and test data sources
| Source | Terms | Commercial use? | Notes | URL |
|---|---|---|---|---|
| NHTSA Vehicle Crash Test Database | ⚠ Primary terms page **blocked from the box (HTTP 403 / fetch timeout)**. Search summaries of nhtsa.gov/about-nhtsa/terms-use say site information is public and may be copied or distributed; US federal works are public domain (17 U.S.C. §105) | ✅ Likely (US Gov public data). **Not verified on the primary page today** | Cite NHTSA; do not imply endorsement | https://www.nhtsa.gov/research-data/research-testing-databases |
| CCSA/NCAC FE vehicle models (GMU) | ccsa.gmu.edu **unreachable today (504/timeout)**. FHWA (highways.dot.gov) states the FE vehicle and hardware models made under its CCSA programme "are in the public domain for the purpose of encouraging safety research in both the public and private sectors". Model pages name NHTSA/FHWA contracts and validation presentations with DOIs | ✅ Likely (public domain per FHWA). Check each model page/zip for a README licence | The models are LS-DYNA decks; OpenCourant reads `.k`. The Yaris 2010 is the 1100C model | https://www.ccsa.gmu.edu/models/ ; https://highways.dot.gov/research/research-programs/safety/roadway-safety |
| Euro NCAP | Site T&C (verified): content is Euro NCAP copyright; "Reproduction is not authorised for commercial purposes"; prior permission needed. Protocols: non-commercial educational sharing only | ❌ No reproduction of results/media without permission. We may implement the test procedures (methods) ourselves, but must not republish their text or results commercially | Ratings/logo use has its own guidelines | https://www.euroncap.com/terms-conditions/ |
| IIHS / HLDI | Copyright page (verified): content for "limited noncommercial, educational and personal use only"; commercial use or redistribution needs written permission (legal@iihs.org); a ratings API exists for registered users | ❌ Not without written permission | TechData portal: https://techdata.iihs.org/ | https://www.iihs.org/copyright-information-and-privacy-policy |

**Top pick: NHTSA crash test database + CCSA FE models (US Gov / public domain)**, after re-checking both primary pages, which were unreachable today. Euro NCAP and IIHS are reference-only unless licensed.

---

## Summary of blockers
1. **OpenRadioss discontinued on 2026-10-01; repo deleted.** Use OpenCourant (AGPL-3.0, fork 3 weeks old). There is no permissive production crash solver.
2. AGPL items: OpenCourant, TetGen, Palabos. Run them unmodified as separate processes, or publish our patches.
3. GPL items (servers only, never ship binaries): OpenFOAM, Gmsh, CalculiX, code_aster, code_saturne, the GPL parts of Elmer.
4. Data: DrivAerNet/DrivAerNet++ and the Loughborough DrivAer data are CC-BY-NC (❌). TUM DrivAer CAD has a no-third-party-sharing condition (needs permission). Euro NCAP and IIHS ban commercial reuse.
5. Not verified today: the NHTSA terms page (403), the CCSA site (timeout), the ESI OpenFOAM COPYING (sign-in wall), and contributor counts for some repos.
