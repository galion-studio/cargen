<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Galion / galion-studio -->
# Rigid-body validation: Rapier vs analytic answers (play layer)
**Play layer only.** These numbers check the game engine. They are never crash, impact or vehicle-dynamics results.

- Crate: `forge/crates/forge-rigid` (rapier3d 0.36.1, CPU, f32, headless; MSRV 1.86)
- Run the table: `cargo run --release -p forge-rigid`. Run the suite: `cargo test -p forge-rigid` (8 tests, 47 checks).
- Measured 2026-10-21 17:35 +02:00 on the box (x86_64 Linux, rustc/cargo 1.99.1). All checks pass.

| Scenario | Quantity | Simulated | Analytic | Error | Tolerance |
|---|---|---|---|---|---|
| Free fall, dt=1/60 | drop at 1 s | 4.92544 m | 4.90500 m | 0.417 % | 2 % |
| Free fall, dt=1/240 | drop at 1 s | 4.91010 m | 4.90500 m | 0.104 % | 0.5 % |
| Free fall | speed at 1 s | 9.81001 m/s | 9.81 m/s | <0.001 % | 0.01 % |
| Spheres m=1/3 kg, 4 and −1 m/s, e=1 | v1′, v2′ | −3.500, 1.500 | −3.500, 1.500 | <1e-6 m/s | 0.05 m/s |
| same, e=0.5 | v1′, v2′; KE ratio | −1.625, 0.875; 0.25987 | same | <1e-6 | 0.05; 0.02 |
| same, e=0 | v1′=v2′; KE ratio | 0.250; 0.01316 | same | <1e-6 | 0.05; 0.02 |
| all impacts | momentum change; measured e | 0; e exact | — | <1e-6 | 1e-3; 0.02 |
| Incline 30°, μ=0 | accel | 4.90506 m/s² | 4.905 | 0.001 % | 2 % |
| Incline 30°, μ=0.2 (Simplified) | accel | 3.20586 | 3.20586 | <0.001 % | 2 % |
| Incline 30°, μ=0.4 (Simplified) | accel | 1.50672 | 1.50672 | <0.001 % | 2 % |
| Incline 30°, μ=0.2 / 0.4 (**Coulomb**) | effective μ | 0.1873 / 0.3745 | 0.2 / 0.4 | **6.37 %** | 8 % (known deviation) |
| Incline 30°, μ=0.7 (sticks) | accel | ~0 (<1e-7) | 0 | <1e-7 | 0.01 |
| Pendulum l=1 m, r=5 cm, 5°, impulse joint | period | 2.008025 s | 2.008025 s | <0.001 % | 0.5 % |
| same, 45°, impulse joint | period; amplitude after 6 T | 2.086755 s; 0.9948 | 2.087299 s; 1 | 0.026 %; 0.52 % | 0.5 %; 5 % |
| same, 45°, multibody (damping 0) | period; amplitude after 6 T | 2.087298 s; 0.999995 | 2.087299 s; 1 | <0.001 %; 5e-6 | 0.5 %; 5 % |
| Pendulum, all | joint drift max | ≤ 9.5e-7 m | 0 | — | 1e-3 m |
| CCD: r=2 cm steel ball vs 1 cm wall, 100 and 300 m/s, dt=1/60 (5 m/step) | stop position | −0.02000 m | −0.02 m (front face) | ≤ 9e-7 m | 1 cm |
| CCD off (`max_ccd_substeps=0`), 300 m/s | tunnels? | yes | yes (control) | — | — |
| Determinism: 20-box pile, 2 runs | differing pose words | 0 / 140 | 0 | bit-exact | 0 |

## What the numbers say
- **Integrator:** with symplectic Euler over n steps × 4 substeps, the drop is ½gt²(1 + 1/(4n)). The measured errors are 1/240 and 1/960, exactly as predicted, and `free_fall_error_is_first_order_in_dt` asserts the ratio of 4.
- **Restitution and momentum** are exact for frictionless head-on spheres. This is Rapier's end-of-step restitution solve (fixed upstream in issue #974).
- **Friction:** `FrictionModel::Simplified` (the default) is exact. `FrictionModel::Coulomb` under-applies μ by about 6.4 %, regardless of solver iterations (1 to 32) or `friction_in_bias_pass`. This is a candidate upstream issue, so keep Simplified for now.
- **Joints:** multibody joints are exact once their default angular damping of 0.1 is zeroed. With the default, the 45° case lost 63 % of its amplitude and its period was 2.5 % short. Impulse joints lose about 0.5 % of amplitude in 6 periods at 45°.
- **CCD:** both default (vs fixed) and `ccd_enabled` stop a 300 m/s projectile on the front face of a 1 cm wall, and switching CCD off tunnels as expected. Speeds above 400 m/s are capped by `normalized_max_linear_velocity`.

## Not covered yet
Rolling resistance, stacking stability, mass ratios above 100:1, wheel and suspension (to be checked against Chrono), cross-platform determinism (`enhanced-determinism`), and f64.
