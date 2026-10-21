<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Galion / galion-studio -->
# AI car generation system — plan v0 (2026-10-21 16:50 +02:00)
Separate from obsidian-open-mind / Wave 4. Planning only; nothing built yet.

## Principle: two physics layers, never mixed
- Truth layer: validated external solvers + real test data. Every number carries its source, solver version, mesh and a validation error vs a real test. If it is not validated it is labelled "unvalidated estimate".
- Play layer: the drivable game uses real-time physics (approximate by nature). It is fed by truth-layer outputs (mass, inertia, stiffness, Cd/Cl) but its own outputs are never shown as real crash or aero results.

## Sectors, goals, agent allocation (20 total to start; cap 20 per sector)
| # | Sector | Goal | Start agents |
|---|---|---|---|
| 1 | Physics (first) | Validated crash/impact pipeline: reproduce real crash tests within a stated error | 8 |
| 2 | Frame & structure | Parametric chassis, load paths, torsional/bending stiffness via FE | 3 |
| 3 | Body panels | Panels with stamping/molding constraints (draw depth, radii, thinning) | 2 |
| 4 | Aero | CFD Cd/Cl validated on DrivAer/Ahmed before any generated car | 3 |
| 5 | Assembly | Joints, snap-fits, adhesive bonds, no extra screws; joint strength via FE | 1 |
| 6 | Drivable game | Bevy (Rust, Linux) car fed by truth-layer data | 2 |
| 7 | One-prompt pipeline | Prompt → spec → geometry → solvers → report → drivable car | 1 |
Physics gets the most agents because it gates everything else. Sectors 2–7 start with plans and tooling only.

## Physics sector: proposed solvers
- OpenCourant (AGPL-3.0, community fork of OpenRadioss after its repo was removed; reads LS-DYNA .k input) — main crash solver, run unmodified as a separate program. Fork is young (stable since 2026-10-11): pin a version and validate it ourselves.
- CalculiX and/or Code_Aster (implicit FE) — stiffness, modal, static loads.
- Gmsh (meshing), OpenCASCADE / FreeCAD (CAD geometry).
- Project Chrono (open-source multibody/vehicle dynamics) as an option for suspension/vehicle-dynamics truth checks.
- Rust orchestrates (job runner, data pipeline, result checks); solvers run as external processes.

## Proposed real-world data
- NHTSA Vehicle Crash Test Database (measured accelerations, barrier forces) and NCAP results.
- NCAC/CCSA public finite-element vehicle models (e.g. Toyota Yaris, Honda Accord), already validated against NHTSA tests.
- FMVSS 208/214/216 and Euro NCAP / IIHS protocols for test setups and pass criteria.
- Materials: WorldAutoSteel AHSS data, published stress-strain/strain-rate data for steel and aluminium grades; each value cited.
- Aero: DrivAer (TU Munich) open geometry with wind-tunnel data, and the Ahmed body.
- Validation metric: ISO/TS 18571 curve-correlation score against the measured signals.

## First physics deliverable (P1)
P1a: square steel-tube axial crush in OpenCourant vs a published experiment (peak and mean crush force, fold pattern). This proves the solver, material and mesh chain works.
P1b: NHTSA full-frontal 56 km/h rigid-barrier test reproduced with the public CCSA Toyota Yaris model in OpenCourant. Compare barrier force and B-pillar acceleration with the real NHTSA test signals, report the ISO 18571 score and pass/fail honestly, with every input traceable.
Done means: reproducible run script, input files with sources, result curves vs test curves, error report. No "generated car" claims until P1b passes.

## Open questions for Mate
1. Pace: the request limit stopped 8 agents at 25 this morning, and Wave 4 runs about 8. Start 20 here at once, or ramp (e.g. 6 now, up to 20)?
2. Compute: a full-car crash run is hours on CPU. Run on the box (8 cores, 15 GB RAM), the VPS (production, I'd avoid), or rent a compute server (budget)?
3. Licences: OpenRadioss is AGPL, CalculiX/Gmsh/OpenFOAM are GPL. OK to use as separate external programs?
4. Repo: new GitHub repo for this project (name?), or local only for now?
5. Bullet: Bevy's native physics is Rapier (Rust); Bullet has no maintained Rust binding. Rapier for the game layer, OK?

## v1 additions (2026-10-21 16:50 +02:00, from Mate via New Bot 1)
### A. Licence research (running now, read-only web research)
Goal: a commercial subscription product (like a terminal for physics and modelling). Each candidate is recorded in research/licences.md with licence, whether commercial SaaS use is allowed, obligations, maturity (age, releases, activity, validation record) and source URL.
Licence rule for a hosted subscription: MIT/Apache/BSD/zlib are clean. LGPL is fine as a dynamic library or separate program. GPL is fine if only run on our servers and not distributed, but not if shipped to customers. AGPL (OpenRadioss) obliges us to publish our changes to that program for network users; using it unmodified as a separate program is the safe path. Any default choice must be clean for SaaS, otherwise flagged.
### B. Materials and alloy chemistry
Sector 1 gets a materials sub-team (2 of its 8 agents). They cover steel grades (mild, HSLA, DP, TRIP, press-hardened boron), aluminium 5xxx/6xxx/7xxx, magnesium AZ31/AM60 and titanium Ti-6Al-4V, under impact (strain rate: Johnson-Cook, Cowper-Symonds), heat, and forming (forming limit curves). Every parameter is cited to a published paper or dataset. Research: research/materials.md.
### C. AI models via OpenRouter
One crate, `cargen-llm`, is the only path to OpenRouter. One key comes from an env var, never committed and never printed. A task-to-model routing table sends reasoning tasks (physics planning, crash analysis) to a top reasoning model and parsing and prompt handling to a fast cheap model. Every call is logged with model, tokens and cost from the OpenRouter usage fields. There is a hard spend cap separate from hermes-rs; the call refuses past the cap.
Rule: the AI plans, writes inputs and explains results. It never produces physics numbers. All numbers come from the solvers and data.

## v2 decisions (2026-10-21 16:52 +02:00, relayed by New Bot 1; repo creation and spend wait for Mate's own confirmation)
- Repo: public from day one, named "forge" (fallback "cargen"). Own code MIT. Docs order: README, sector docs, solver notes with cited sources, agent-run log. Lightweight, no bloat.
- Pace: ramp up gradually toward 20 agents.
- Compute: CPU path is the default. CUDA sits behind a `Compute` trait as the acceleration layer. Heavy runs (full-car crash, world-model inference) go to a rented RunPod A100. Light tasks run locally. NVIDIA tools where they help: NGC containers, Triton for inference, PhysX as an optional game-physics backend; Rapier is the default.
- Licences: AGPL only unmodified, as a separate program. GPL is fine server-side.
- OpenRouter: $50/month hard cap, adjustable, key via secure field.

## v3 (2026-10-21 16:54 +02:00, relayed by New Bot 1, pending Mate's own confirmation)
- Inside galion-studio/forge only: merge and publish freely. Nothing outside that repo without asking.

## Research result (2026-10-21 16:58 +02:00), see research/licences.md
- Crash solver: OpenRadioss's GitHub repo now returns 404, so we use the OpenCourant fork (AGPL, unmodified).
- Picks: MFEM (BSD) for implicit FE, SU2 (LGPL) for CFD, OCCT via build123d for CAD, Netgen + fTetWild for meshing, Chrono (BSD) for vehicle dynamics, Bevy + Rapier for the game, NHTSA + CCSA (public domain) for data.
- Aero validation data: DrivAerML and AhmedML (CC-BY-SA, commercial OK). The NC-licensed DrivAerNet and Loughborough sets are out. The TUM DrivAer CAD needs TUM permission.
- Euro NCAP and IIHS content: no commercial reuse without written permission; use their protocols as reference only.

## Materials research (2026-10-21 17:00 +02:00), see research/materials.md
- Use: NIST open datasets (Numisheet 2020, high-rate Mates et al.), MatCalc open CALPHAD (ODbL), pycalphad/ESPEI (MIT), Materials Project core (CC BY), CC-BY papers, WorldAutoSteel guidelines (quote with source).
- Banned from product, index and training: MatWeb (explicit AI ban), NIMS MatNavi, Thermo-Calc DBs, Granta, MMPDS, NIST SRD, GNoME subset.
- Cited Johnson-Cook sets exist for Ti-6Al-4V, 6061-T6, 6082-T6, 7075-T6, 22MnB5, DP600 (low confidence), AM60B. Gaps: HSLA, DP780/980, TRIP, 5182-O, AZ31B; no open CALPHAD for Mg/Ti. Fill gaps by fitting our own parameters to NIST open curves.
- Open decision: pay for Thermo-Calc TCMG/TCTI + MMPDS, or literature-only for Mg/Ti.
