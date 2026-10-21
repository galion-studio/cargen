<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 galion-studio -->
# Product definition (v0, 2026-10-21, Europe/Zagreb)

Scope: what Forge / cargen ships to users in 2026 (71 days left from 2026-10-21), grounded in what the solvers in this repo can check today. No tagline here; the owner picks it.

Inputs read: README.md, PLAN.md, LOG.md, research/*.md, branding/BRIEF.md, branding/RESEARCH-enterprise.md, forge/runs/* (interim P1a and aluminium reports), forge/scripts/air/*, work/*/META and STATUS. The welding, machinery and robotics folders hold only META and STATUS so far (5–6 %), so anything this file asks of them is a dependency, not a result.

## 0. Ground truth on 2026-10-21 (what can be validated now)
| Capability | State | Evidence |
|---|---|---|
| Axial crush, thin-walled steel tube, closed-form | Working | A&J/W&A theory vs 48 published tests: mean error −0.6 %, mean abs 11.3 %, 27 of 48 within ±10 % (research/crush-experiments.md). Over-predicts Park/Jung A500 tubes by 10–32 %, cause unknown |
| Axial crush, steel tube, OpenCourant FE (P1a) | In progress, not passed | Coarse 10 mm mesh vs Park US-2: peak 327.46 vs 337.1 kN (−2.9 %, pass); mean 114.08 vs 101.0 kN (+12.9 %, fail at ±10 %); 5 vs 7 folds (fail); ISO/TS 18571 0.50 (fail at ≥0.58). Engine wall time 357 s on 4 threads. 5 mm mesh and A&J E3 drop-hammer runs still running (forge/runs/) |
| Axial crush, aluminium tube, FE | Not usable | Interim runs (Lykakos cases) under-predict peak by 61.6 % and mean by 46.7–51.1 % |
| Bending collapse, bent rails, joints, spot welds | Not started | Dataset is axial only; welding workstream is researching spot-weld solver cards |
| Stiffness / modal (MFEM, CalculiX) | Not started | README roadmap item 3 |
| Air environment | Working, no CFD | forge/scripts/air: ISA atmosphere, humid air, drag/lift/road load from a given Cd/Cl, cited Ahmed-body coefficients, gusts. Its own header: "Nothing here is a CFD result" |
| CFD (SU2 8.5.0) | Installed, tutorial cases only | third_party/su2/cases: QuickStart, Inc_Turbulent_Flat_Plate. No Ahmed/DrivAer validation yet |
| Rigid body (Rapier 0.36) | Prototype, play layer only | forge-rigid, 47 analytic checks, 8/8 tests pass. Never a crash or handling result |
| Materials | Partial | Cited JC sets for Ti-6Al-4V, 6061-T6, 6082-T6, 7075-T6, 22MnB5, DP600 (low confidence), AM60B; data/materials/mg-ti.csv (274 rows, 23 materials). Gaps: HSLA, DP780/980, TRIP, Mg/Ti FLCs |
| CAD / export | Not started | Pick: OCCT via build123d (Apache-2.0 on LGPL OCCT) |
| Manufacturability, weld plan, robot path | Not started | machinery, welding, robotics workstreams at 5–6 % |

Consequence: in 2026 the product can make honest crash claims only for straight, thin-walled steel tubes under axial load, and only after P1a passes. Everything else ships as geometry plus manufacturing output, with physics labelled "unvalidated estimate" or "not computed".

## 1. What the product generates: categories and validation tiers
Each output carries one of four labels, shown in the UI next to every number:
- **Validated**: an FE result inside the stated tolerance of a cited physical test of the same kind.
- **Theory-checked**: a closed-form result whose formula has been checked against cited tests; error band shown.
- **Unvalidated estimate**: computed by a solver or formula with no matching test.
- **Not computed**.

| # | Category | Example parts | 2026 physics label | 2026 manufacturing output | Ships |
|---|---|---|---|---|---|
| A1 | Crush member, steel, square or circular, straight | Crash box, straight rail segment, energy-absorber tube | Theory-checked now (mean force, SEA, fold length); Validated once P1a and P1b-equivalent tube cases pass | STEP/STL, cut list, weld plan for end plates | MVP (first) |
| A2 | Crush member, aluminium / Mg / Ti | Same shapes in 6061/6082/7075, AM60B, Ti-6Al-4V | Unvalidated estimate (aluminium FE currently off by ~50 %) | Same as A1 | Behind a flag, late 2026 |
| B1 | Frame tube member | Straight or single-bend round/square tube with end cuts (miter, cope) | Not computed (stiffness sector not started); mass from geometry and density | STEP/STL, cut list with angles, bend data from machinery | MVP |
| B2 | Tube node / joint | Two to four tubes meeting at a node, gussets | Not computed | Weld plan (joint list, sequence), fixture notes | Late 2026 |
| C1 | Small-vehicle frame | Kart, buggy, microcar tube frame | Member-level crush where members are A1; frame stiffness "not computed" until MFEM/CalculiX lands; air check from a user-chosen or cited Cd | Full BOM, cut list, weld plan, STEP assembly | Kart or buggy frame by end of 2026 if M4 lands; microcar is 2027 |
| C2 | Small-vehicle body panels | Kart nose, buggy panels | Not computed | Flat patterns from machinery (bend radii, FLD) | 2027 |
| D | Full car | Body-in-white, full car | Gated by P1b (Yaris full-frontal) per README: "no claims about generated cars until P1b passes" | — | Not in 2026 |

Explicitly out of scope for 2026: road-legal or homologation claims, occupant-safety claims, bent or bending-dominated rails, spot-welded hat sections, composite parts, CFD on generated shapes.

## 2. Personas and jobs-to-be-done
| Persona | Knows | Wants to get done | What the product must give them | What they must never be told |
|---|---|---|---|---|
| Welder / fabricator | Processes, joint prep, fit-up | "Give me a frame I can cut and weld this weekend without redesigning it" | Cut list with lengths and angles, joint list with process and sequence, printable sheets | That a frame is crash-safe |
| Machinist | Stock, tooling, tolerances, bending | "Turn a design into stock lengths, bend data and setups I can run" | Stock-length nesting, bend radius checks vs tooling, STEP for CAM | Tolerances or bend data that were not sourced |
| Robotics tinkerer | Arms, ROS-type toolchains, scripting | "Get weld seams as paths I can feed my arm" | Seam list as coordinates and approach vectors (from the robotics prototype), open file formats, a CLI/API | That a path is collision-checked if it is not |
| Creative designer | Form, sketching, Blender/CAD basics | "Make my shape real without learning FE" | Parameter sliders, instant visual feedback, plain-language manufacturability warnings, mesh export for rendering | Physics numbers without a label |
| Enterprise engineer (OEM / supplier CAE) | FE, test correlation, standards | "Screen crush-member concepts fast and trust the trail" | Solver version, mesh, material source and error vs test on every number; reproducible inputs; exportable decks; ISO/TS 18571 scores | Anything without provenance. Branding research: "Validation" is a named buying job, and OEMs may require TISAX or ISO/IEC 27001 for confidential data |

## 3. MVP user journey (one category end to end: A1 steel crush member)
1. **Pick a category.** Tiles for A1 crush member and B1 frame tube are active; others are visible but marked "later". Each tile states its validation label.
2. **Generate a part.** Inputs: section (square or circular), width or diameter, wall thickness, length, steel grade from the cited list, optional trigger (bead) — trigger shown as "not computed" until validated. Optional free-text prompt goes to the AI planner, which may only fill these fields; it never produces numbers (PLAN.md rule). Output: 3D preview, mass from geometry and cited density.
3. **Check manufacturability.** Rules come only from the machinery and welding workstreams with sources: stock availability of the section, minimum bend radius (if bent), weld access to end plates, thickness vs process. Each rule shows pass/warn/fail and its source; rules without a source are not shown.
4. **Crash and air check.**
   - Crash, instant: closed-form mean crush force, SEA and fold half-length, with the theory error band for the nearest tests in the 48-test set and a warning when the input falls outside the tested range (c/t, speed, material).
   - Crash, queued: optional OpenCourant run (minutes per tube on CPU, going by the 357 s coarse P1a run). Result shown with solver build, mesh and run-quality checks, labelled per §1.
   - Air: for a part, not applicable. For a frame or vehicle (C1), drag force and power at a chosen speed and altitude from the air module, using a Cd the user enters or a cited reference body; always labelled "estimate from given Cd, no CFD".
5. **Export.** STEP and STL (OCCT/build123d); cut plan (CSV and printable PDF: stock, length, end-cut angles); weld plan (CSV and PDF: joint id, members, joint type, process, sequence, notes; parameters only where the welding workstream has a cited source); a report (Markdown/PDF) listing every number with its label and source; the solver input deck for enterprise users.

Delivery form for 2026: a CLI first (Rust core plus the existing Python scripts), then a web front end over a server that runs the solvers. A server keeps GPL tools (Gmsh, CalculiX) and AGPL OpenCourant inside the licence rules in PLAN.md.

## 4. 2026 roadmap
Effort sizes are my relative estimates (S < M < L), not measured. No dates are promised beyond the milestone order.

| Milestone | Target | Contents | Depends on | Effort | Honest note |
|---|---|---|---|---|---|
| M0 Definition | late Oct | This file, mockup, owner decisions in §5 | — | S | Done with this file except decisions |
| M1 Crush member core | early Nov | P1a pass on a finer mesh (or a written reason why not); CLI `generate crush-member` with closed-form check, range warnings and labels; A&J E3 drop-hammer case as a second FE validation | physics sector (forge-crash) | M | Coarse P1a fails mean force (+12.9 %) and fold count today. If finer meshes do not close it, A1 ships as Theory-checked only |
| M2 Geometry and export | mid Nov | build123d tube and crash-box generator; STEP/STL export; cut list CSV; report generator | oss-scout (integration spikes) | M | Nothing built yet; OCCT is LGPL, so link dynamically or run as a process |
| M3 Manufacturing checks v0 | late Nov | Sourced rules: bend radii, stock sections, weld access; weld plan v0 for end plates | machinery, welding | M–L | Both workstreams are at 5–6 %; scope shrinks to whatever rules have sources by then |
| M4 Frame tubes and first small-vehicle frame | Dec | B1 members, B2 nodes, one kart or buggy frame template; BOM, cut and weld plans; air check from given Cd | M2, M3, air module | L | Frame stiffness stays "not computed" unless MFEM/CalculiX work starts now; that would be a separate L |
| M5 Web MVP | Dec | Static front end (from the mockup) over a job server; queued FE runs; downloads | M1–M4, compute decision | L | Hosting, accounts and compute cost are open decisions |
| Stretch | Dec | Weld-seam path export for the robotics arm prototype; aluminium crush behind a flag | robotics, physics | M each | Aluminium FE currently ~50 % off; flag only, no Validated label |

After 2026, in README order: P1b full-frontal Yaris, frame stiffness, body panels with forming limits, CFD validated on AhmedML/DrivAerML, assembly joints, drivable game, one-prompt pipeline, full cars.

## 5. Risks and open decisions
### Risks
1. **P1a may not pass soon.** Mean force and fold count fail on the coarse mesh. Mitigation: ship A1 as Theory-checked, keep the label honest.
2. **Theory gap on A500 tubes** (+10–32 %, cause unknown) means the closed-form band is wider for cold-formed hollow sections, the stock most fabricators buy.
3. **Aluminium FE far off** (−47 to −62 %); Mg/Ti lack crash-rate data.
4. **Liability.** Hobby users may build and drive karts or buggies from generated frames. Needs clear "not validated for occupant safety" language and a legal review (research/materials.md already flags a lawyer review before launch).
5. **Young crash solver.** OpenCourant stable since 2026-10-11; pinned build cb760c2. Upstream changes can move results.
6. **Three of the inputs (welding, machinery, robotics) are just starting**; M3–M4 depend on them.
7. **Compute.** Box has 8 cores and 15 GB RAM (PLAN.md); many users queuing FE runs needs rented compute.
8. **Data licences.** Euro NCAP/IIHS content and NC datasets are off limits; NHTSA and CCSA terms are not yet re-verified on primary pages.
9. **Scope creep toward full cars** before P1b.

### Open decisions for the owner
1. Tagline (left empty everywhere).
2. Product name in the UI: "Forge" (README) or "cargen" (repo, branding brief).
3. Delivery: hosted web app only, or also a downloadable CLI/desktop build (GPL/AGPL tools then cannot be bundled freely).
4. Who is first: hobby fabricators (welder, machinist, designer) or enterprise CAE engineers. It changes onboarding, pricing and security work (TISAX/ISO 27001).
5. Validation gate for the "Validated" label: keep the current P1a tolerances (mean ±10 %, peak ±15 %, folds ±1, ISO/TS 18571 ≥ 0.58) or set others.
6. Ship A1 as Theory-checked in 2026 if P1a does not pass, or hold it.
7. First small vehicle: kart, buggy or microcar.
8. Weld-symbol and drawing standard for exported plans (ISO 2553 or AWS A2.4), and units (metric only or both).
9. Pricing: free tier, subscription, compute pass-through; RunPod budget.
10. Colour: this mockup uses navy and white as asked; the enterprise branding research recommends building on the existing charcoal and orange. Pick one for the product UI.
11. Materials: literature-only for Mg/Ti, or buy Thermo-Calc TCMG/TCTI and MMPDS (already open in PLAN.md).

## Files
- `mockup/index.html`: static, self-contained, mobile-friendly mockup of the §3 journey. Example values are real: Park 2022 US-2 measured 101.0 kN mean, closed-form 122.5 kN static (data/crush-theory-check.csv), coarse FE 114.08 kN (forge/runs/p1a_us2_baseline_h10/report.md); drag 31.3 N at 40 m/s for Cd 0.285, A 0.112 m² at ISA sea level (air module, Ahmed 25° experiment Cd).
