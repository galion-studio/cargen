<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# weld_arm: 6-axis weld-seam arm prototype (Forge robotics sector)

This is a standalone Rust crate, not part of the forge workspace. It does kinematics only. It does **not** check collisions with the part, torch, cables or fixtures, and it does not model dynamics.

## What it does
1. **Arm model.** A UR5e is built from Universal Robots' published DH table, using the UR5e datasheet joint ranges (±360°, elbow ±160°). The arm exists in two forms:
   - an f64 DH chain with FK and a geometric Jacobian (the reference), and
   - a **Rapier 0.36 multibody** (`rapier3d-f64`): a fixed base plus 6 revolute multibody joints with limits. `RapierArm` sets joint coordinates, runs Rapier's forward kinematics and also exposes Rapier's built-in multibody IK.
2. **IK.** Damped least squares, 6-D (position and orientation), clamped to the joint limits at every step and limited to 0.2 rad per iteration. The first waypoint tries 32 seeds and keeps the branch with the best manipulability. Each later waypoint is seeded from the previous one.
3. **Weld seam.** A box tube lies on a plate. The seam is the fillet where the wall facing the robot meets the plate. The torch (TCP z axis) bisects the corner at the work angle (default 45°) and can be tilted along the seam by the travel angle (push positive).
4. **Checks.**
   - Reach bound: if shoulder-to-TCP distance is greater than the sum of link offsets plus the tool offset, the target is `OutOfReach`.
   - IK non-convergence within limits gives `NoConvergence`.
   - Joint limits are checked on every solution.
   - A joint jump between waypoints greater than `--max-jump-deg` gives `JointJump`, which catches branch flips and singularities.
   - Yoshikawa manipulability is reported for every waypoint.
   - Every waypoint is cross-checked against the Rapier multibody.
5. **Output.** A table on stdout and a CSV (`i, s_mm, x/y/z_mm, q1..q6_deg, residuals, manipulability, dq_max_deg`).

All geometry and settings are **example inputs**, not shop data. These include the tube position, 50 mm width, 300 mm length, the tool offset, the step and the jump threshold. The only robot data are the UR DH table and the UR5e joint ranges (sources in robotics.md).

## Run
```bash
cd /workspace/cargen/work/robotics
cargo test                      # 11 tests
cargo run --release -- --tool-z 0.15 --travel-deg 10 --out trajectory.csv
cargo run --release -- --tool-z 0.15 --y 1.6      # out-of-reach demo, exits 1
cargo run --release -- --help
```
Flags (metres unless noted): `--tool-z` (TCP offset along the flange z axis), `--step-mm`, `--work-deg`, `--travel-deg`, `--x0`, `--y`, `--z` (tube bottom-face start centre; the axis runs along +x), `--length`, `--width`, `--max-jump-deg`, `--out`.

## Results (2026-10-21, this box)
`cargo test`: **11 passed, 0 failed**.
- UR5e zero pose equals the DH closed form (x = a2+a3, y = −(d4+d6), z = d1−d5), within 1e-12 m.
- The Jacobian matches central finite differences.
- **FK→IK round trip.** 300 random configurations were each seeded within ±0.2 rad of the true joints. All 300 poses were recovered within 1e-6 m and 1e-6 rad, and all within limits. In the 154 samples with manipulability above 0.02, the joints were recovered within 1e-5 rad. Below that threshold a neighbouring IK branch with the same pose can be returned. That is expected near singularities, so the test only asserts pose accuracy there.
- **Blind multi-seed IK** (no knowledge of the true joints): 60 of 60 poses were recovered within 1e-6 m and 1e-6 rad.
- **Rapier multibody FK vs DH:** worst flange error 3.9e-15 over 200 samples. Rapier's own multibody IK converges to 1e-6 from nearby starts.
- **Reach-limit detection.**
  - A target 1.5 m out gives `OutOfReach`.
  - A target 1 cm inside the chain bound but unreachable gives `NoConvergence`. The solver fails rather than returning a wrong answer.
  - A seam moved to y = 1.6 m fails at waypoint 0 with `OutOfReach`.
- **Joint limits.** An elbow at 170° and a base at 360.6° are both flagged. IK never returns an elbow beyond ±160°.
- **Seam test** (5 mm step, 45° work angle, 10° travel angle, 0.15 m tool): 61 waypoints. Every TCP lies on the seam line within 1e-6 m, every joint step is at most 5°, and Rapier and DH agree within 1e-12.

Demo run (`--tool-z 0.15 --travel-deg 10`, 10 mm step): 31 waypoints, worst IK residual 5.2e-12 m / 1.5e-12 rad, largest joint step 2.47°, minimum manipulability 0.0231, Rapier vs DH 6.2e-16 m. Output is in `trajectory.csv`.

## Limits and next steps
- No collision checks. Next step: add the tube, plate and torch as Parry/Rapier colliders and run a sweep test along the path.
- Rapier's IK ignores joint limits, so `ArmSpec::ik` is the one used for planning.
- No timing yet. Next step: constant-TCP-speed parameterisation (as in ROS-Industrial Scan-N-Plan), once the welding sector supplies a travel speed.
- Export a URDF so the same cell can be planned in ROS 2 + MoveIt 2.
