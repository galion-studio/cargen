<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Galion / galion-studio -->
# Rigid-body dynamics and collision for Forge (play layer + truth checks)
2026-10-21. Play-layer engine choice plus a truth-layer cross-check. Play-layer outputs are never reported as crash or vehicle-dynamics results (PLAN.md, "two physics layers").

## Candidates
| Engine | Licence | Language / Bevy fit | Role for us |
|---|---|---|---|
| Rapier 0.36 (dimforge) | Apache-2.0 [1] | Rust; `bevy_rapier` plugin, Apache-2.0 [1] | **Default play-layer engine** (prototype: `forge/crates/forge-rigid`) |
| Parry 0.31 | Apache-2.0 [1] | Rust collision library under Rapier and Avian | Shape queries, ray/shape casts, mesh tools |
| Avian 0.8 | MIT/Apache-2.0 [2] | Rust, ECS-native Bevy engine (Bevy 0.20) [3] | Alternative if we want physics state in the ECS. Uses Parry for collision. |
| Project Chrono 10 | BSD-3 [4][5] | C++ (PyChrono). Run as a separate program. | **Truth-layer** multibody and vehicle checks (Chrono::Vehicle) |
| PhysX 5.6 | BSD-3, GPU source included since 5.6.0 (2025-03-25) [6][7] | C++; no maintained Rust/Bevy binding | Optional NVIDIA GPU backend behind `Compute` |
| Jolt | MIT [8] | C++ | Not planned. Licence is clean. |
| Bullet 3 | zlib, except `Extras/` and `examples/ThirdPartyLibs` [9] | C++; no maintained Rust binding | Not planned. Licence is clean. |
All of these are clean for a hosted SaaS under our licence rule (MIT/Apache/BSD/zlib).

## Integrators and solvers
- **Rapier**: semi-implicit (symplectic) Euler with substepping. `num_solver_iterations` (default 4) is the substep count. Contacts use soft constraints with warm-starting and a relax pass [10]. This is the TGS-Soft / "Soft Step" family that Catto benchmarked in Solver2D [11], building on Macklin et al.'s "Small Steps" result: substeps beat iterations [12]. **Measured:** the free-fall error is exactly 1/(n·4) (see the validation doc), so position is first order in the substep size.
- **Avian**: contacts use the same impulse-based TGS Soft solver (warm start, bias solve, relax). Joints still use XPBD [3][13].
- **Chrono**: `EULER_IMPLICIT_LINEARIZED` (first order) is the default for NSC (hard complementarity contact, DVI). `HHT` is second order with adjustable numerical damping but works only with SMC (penalty contact) [14][15]. Chrono is the right reference when we need an implicit DAE solver with validated tyre models.

## CCD (continuous collision detection)
- Rapier uses nonlinear (translation plus rotation) motion clamping, so a body stops at its first time of impact. Fast dynamic bodies are swept against **fixed** colliders automatically. `ccd_enabled(true)` ("bullet") also sweeps against dynamic and kinematic bodies. `max_ccd_substeps` (default 1) cuts the time lost to clamping, and setting it to 0 switches CCD off world-wide. Soft-CCD (`soft_ccd_prediction`) is a cheaper predictive-contact variant for thin, moderately fast bodies [10][16][17].
- Gotchas found in the Rapier source/tests: there is a speed cap, `normalized_max_linear_velocity` = 400 m/s by default. Moving trimeshes are never swept, so use convex or compound shapes for fast parts [18].
- Avian 0.8 reworked CCD to avoid ghost collisions at high speed [3].

## Joints (snap-fits and bonded joints)
- Rapier supports fixed, revolute, prismatic and spherical joints, plus any DoF mix through `GenericJoint`, with limits and PD motors [19]. **Impulse joints** are constraints with small drift. **Multibody joints** use reduced coordinates and are exact by construction [19].
- Snap-fit (play layer): a prismatic joint with limits and a motor/spring as the latch preload. Release it by removing the joint when the force read from the solver exceeds a threshold taken from the truth layer (FE).
- Bonded joint (play layer): a fixed joint that we read and break. Rapier notes that a fixed joint is only worth using over multiple colliders on one body when you need its force, for example to break it [19].
- Joint *strength* is never a play-layer number. It comes from FE (sector 5) and only flows *into* the game.
- **Measured gotcha:** Rapier gives every free angular multibody DoF a **default damping of 0.1**. Undamped, a 45° pendulum lost 63 % of its amplitude in 6 periods and its period was 2.5 % short. Zero it (`damping_mut()`) whenever energy matters.

## Determinism
- Rapier is deterministic on one machine by default, given the same version, compiler and insertion order. The `enhanced-determinism` feature gives cross-platform determinism on strict IEEE-754 targets (not combinable with `simd8`). Initial values must come from `nalgebra` `ComplexField` functions, not `f32::sin` [20].
- Jolt is deterministic for the same binary, and cross-platform with `CROSS_PLATFORM_DETERMINISTIC` (about 8 % slower) [21].
- **Measured:** two runs of a 20-box pile were bit-identical (0 of 140 pose words differed).

## Validating against analytic cases (method)
1. Choose cases with closed-form answers, each exercising one subsystem: free fall (integrator), 1-D impacts (restitution and momentum), incline (Coulomb friction, stick/slip), pendulum (joints and energy), and a projectile against a thin wall (CCD).
2. Compare a scalar with a stated tolerance. Check *convergence order* too, not just one point: the error ratio when dt shrinks 4× should be 4 for a first-order scheme.
3. Use exact references where possible, for example the large-amplitude pendulum T = T0 / AGM(1, cos θ0/2), rather than small-angle approximations.
4. For vehicle dynamics, cross-check against Chrono::Vehicle, which is validated against ADAMS/Car and tyre test rigs [5][22], before any game tuning is called "realistic".

## Recommendations
1. Use Rapier (CPU, f32) plus `bevy_rapier` as the play-layer default. Keep `FrictionModel::Simplified`, because `Coulomb` under-applied friction by 6.4 % in our test. Use `dt` = 1/60 with 4 substeps, or 1/120 for the car.
2. Enable `ccd_enabled` on wheels and debris, build car parts from convex or compound shapes rather than trimeshes, and check the 400 m/s cap.
3. Use multibody joints with damping zeroed for the suspension and steering chain. Use impulse joints for breakable snap-fits and bonds.
4. Turn on `enhanced-determinism` only if we need replays or networking. Same-machine determinism already holds.
5. Run Chrono (BSD) as a separate truth-check program for suspension and handling. PhysX stays an optional GPU path because it has no Rust binding, which makes it costly.

## Sources
1. Rapier LICENSE https://github.com/dimforge/rapier/blob/master/LICENSE ; Parry https://github.com/dimforge/parry ; bevy_rapier https://github.com/dimforge/bevy_rapier/
2. Avian repo https://github.com/avianphysics/avian/
3. Avian 0.8 release post (2026-10-20) https://joonaa.dev/blog/14/avian-0-8
4. Chrono FAQ (BSD-3) https://projectchrono.org/faq/
5. Chrono repo https://github.com/projectchrono/chrono ; validation index https://projectchrono.org/validation/
6. PhysX LICENSE https://github.com/NVIDIA-Omniverse/PhysX/blob/main/LICENSE.md
7. PhysX GPU source release https://github.com/NVIDIA-Omniverse/PhysX/discussions/384 ; GPU docs https://nvidia-omniverse.github.io/PhysX/physx/latest/docs/GPURigidBodies.html
8. Jolt repo https://github.com/jrouwe/JoltPhysics
9. Bullet LICENSE https://raw.githubusercontent.com/bulletphysics/bullet3/master/LICENSE.txt
10. Rapier IntegrationParameters https://docs.rs/rapier3d/latest/rapier3d/dynamics/struct.IntegrationParameters.html
11. Catto, Solver2D https://box2d.org/posts/2024/02/solver2d/
12. Macklin et al., Small Steps in Physics Simulation (SCA 2019) https://mmacklin.com/smallsteps.pdf (doi:10.1145/3309486.3340247)
13. Avian 0.1 (solver rework) https://joonaa.dev/blog/06/avian-0-1
14. Chrono simulation system (integrators, NSC/SMC) https://api.projectchrono.org/simulation_system.html
15. Chrono integrator theory https://projectchrono.org/assets/white_papers/ChronoCore/integrator.pdf
16. Rapier CCD guide https://rapier.rs/docs/user_guides/templates/rigid_body_ccd
17. Rapier RigidBodyBuilder (ccd_enabled, soft_ccd) https://docs.rs/rapier2d/latest/rapier2d/dynamics/struct.RigidBodyBuilder.html
18. rapier3d 0.36.1 source: `src/dynamics/integration_parameters.rs`, `tests/ccd_default_vs_fixed.rs` https://crates.io/crates/rapier3d
19. Rapier joints guide https://rapier.rs/docs/user_guides/rust/joints
20. Rapier determinism guide https://rapier.rs/docs/user_guides/rust/determinism/
21. Jolt deterministic simulation https://jrouwe.github.io/JoltPhysicsDocs/5.3.0/
22. Chrono::Vehicle TR-2016-10 https://sbel.wisc.edu/wp-content/uploads/sites/569/2018/05/TR-2016-10.pdf
