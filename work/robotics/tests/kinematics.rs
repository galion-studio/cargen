// SPDX-License-Identifier: MIT
// Copyright (c) 3000 galion-studio
//! FK -> IK round trips, Rapier-vs-DH agreement, reach and joint-limit detection,
//! and the box-tube seam trajectory.

use std::f64::consts::PI;
use weld_arm::*;

/// Small deterministic PRNG (no extra dependencies).
struct Lcg(u64);
impl Lcg {
    fn next(&mut self) -> f64 {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        (self.0 >> 11) as f64 / (1u64 << 53) as f64
    }
    fn range(&mut self, lo: f64, hi: f64) -> f64 {
        lo + (hi - lo) * self.next()
    }
    /// Random joint vector inside +-170 deg (elbow +-150 deg), i.e. inside the UR5e limits.
    fn q(&mut self) -> Q {
        let mut q = [0.0; 6];
        for (i, v) in q.iter_mut().enumerate() {
            let m = if i == 2 { 150f64 } else { 170f64 }.to_radians();
            *v = self.range(-m, m);
        }
        q
    }
}

const TOL_POS: f64 = 1e-6; // m
const TOL_ROT: f64 = 1e-6; // rad
/// Below this Yoshikawa manipulability (UR5e with the 0.15 m test tool), IK
/// branches lie close together and a nearby seed may land on a neighbouring
/// branch with the same pose; joint recovery is only asserted above it.
const MANIP_OK: f64 = 0.02;

fn tool() -> Iso {
    Iso::translation(0.0, 0.0, 0.15) // example torch offset for the tests
}

#[test]
fn ur5e_zero_pose_matches_dh_table() {
    // At q = 0 the UR DH chain gives x = a2 + a3, y = -(d4 + d6), z = d1 - d5.
    let arm = ur5e();
    let p = arm.fk(&[0.0; 6], &Iso::identity()).translation.vector;
    assert!((p.x - (-0.425 - 0.3922)).abs() < 1e-12, "{p}");
    assert!((p.y - (-(0.1333 + 0.0996))).abs() < 1e-12, "{p}");
    assert!((p.z - (0.1625 - 0.0997)).abs() < 1e-12, "{p}");
}

#[test]
fn jacobian_matches_finite_difference() {
    let arm = ur5e();
    let mut rng = Lcg(7);
    let t = tool();
    for _ in 0..20 {
        let q = rng.q();
        let j = arm.jacobian(&q, &t);
        let h = 1e-6;
        for i in 0..6 {
            let (mut qp, mut qm) = (q, q);
            qp[i] += h;
            qm[i] -= h;
            let dp = (arm.fk(&qp, &t).translation.vector - arm.fk(&qm, &t).translation.vector) / (2.0 * h);
            for r in 0..3 {
                assert!((dp[r] - j[(r, i)]).abs() < 1e-6, "col {i} row {r}");
            }
        }
    }
}

#[test]
fn fk_ik_round_trip_near_seed_recovers_joints() {
    // Seed within +-0.2 rad of the true joints: IK must hit the pose and,
    // away from singularities, the same joint vector.
    let arm = ur5e();
    let t = tool();
    let mut rng = Lcg(42);
    let opt = IkOptions::default();
    let (mut n_pose, mut n_joint, mut n_checked) = (0, 0, 0);
    for _ in 0..300 {
        let q = rng.q();
        let target = arm.fk(&q, &t);
        let mut seed = q;
        for s in seed.iter_mut() {
            *s += rng.range(-0.2, 0.2);
        }
        let sol = arm.ik(&target, &t, &[seed], &seed, &opt).expect("IK from a nearby seed");
        let (ep, eo) = pose_error(&target, &arm.fk(&sol.q, &t));
        assert!(ep.norm() < TOL_POS && eo.norm() < TOL_ROT, "pose residual {} m {} rad", ep.norm(), eo.norm());
        assert!(arm.check_limits(&sol.q).is_ok());
        n_pose += 1;
        if arm.manipulability(&q, &t) > MANIP_OK {
            n_checked += 1;
            let d = joint_dist(&sol.q, &q);
            if d < 1e-5 {
                n_joint += 1;
            } else {
                println!("miss: dist {d:.3e} rad, manip {:.4}", arm.manipulability(&q, &t));
            }
        }
    }
    println!("round trip: {n_pose}/300 poses within {TOL_POS} m / {TOL_ROT} rad; joints recovered {n_joint}/{n_checked} with manipulability > {MANIP_OK}");
    assert_eq!(n_joint, n_checked, "a non-singular sample converged to a different branch");
}

#[test]
fn fk_ik_round_trip_blind_multi_seed() {
    // No knowledge of the true joints: the seed grid must still find a pose
    // match (possibly another IK branch) for every sample.
    let arm = ur5e();
    let t = tool();
    let mut rng = Lcg(2026);
    let seeds = default_seeds();
    let opt = IkOptions::default();
    for k in 0..60 {
        let q = rng.q();
        let target = arm.fk(&q, &t);
        let sol = arm.ik(&target, &t, &seeds, &q, &opt).unwrap_or_else(|e| panic!("sample {k}: {e}"));
        let (ep, eo) = pose_error(&target, &arm.fk(&sol.q, &t));
        assert!(ep.norm() < TOL_POS && eo.norm() < TOL_ROT, "sample {k}");
        assert!(arm.check_limits(&sol.q).is_ok(), "sample {k} outside limits");
    }
}

#[test]
fn rapier_multibody_fk_matches_dh() {
    let arm = ur5e();
    let mut r = RapierArm::build(&arm);
    let mut rng = Lcg(3);
    let mut worst: f64 = 0.0;
    for _ in 0..200 {
        let q = rng.q();
        r.set_q(&q);
        let (ep, eo) = pose_error(&arm.fk(&q, &Iso::identity()), &r.flange());
        worst = worst.max(ep.norm()).max(eo.norm());
    }
    println!("rapier vs DH worst flange error: {worst:.2e}");
    assert!(worst < 1e-12);
}

#[test]
fn rapier_multibody_ik_round_trip() {
    // Rapier's own multibody IK (no limits) from a nearby start.
    let arm = ur5e();
    let mut r = RapierArm::build(&arm);
    let mut rng = Lcg(11);
    for k in 0..50 {
        let q = rng.q();
        if arm.manipulability(&q, &Iso::identity()) < 1e-3 {
            continue;
        }
        let target = arm.fk(&q, &Iso::identity());
        let mut start = q;
        for s in start.iter_mut() {
            *s += rng.range(-0.1, 0.1);
        }
        r.set_q(&start);
        let (_, ep, eo) = r.ik(&target, 1e-3, 200);
        assert!(ep < TOL_POS && eo < TOL_ROT, "sample {k}: {ep} m {eo} rad");
    }
}

#[test]
fn reach_limit_is_detected() {
    let arm = ur5e();
    let t = tool();
    let opt = IkOptions::default();
    let seeds = default_seeds();
    // 1.5 m from the base is beyond the chain bound (sum of offsets + tool).
    let far = Iso::translation(1.5, 0.0, 0.3);
    let r = arm.reach(&far, &t);
    assert!(!r.within_bound);
    match arm.ik(&far, &t, &seeds, &[0.0; 6], &opt) {
        Err(IkError::OutOfReach { distance_m, bound_m }) => assert!(distance_m > bound_m),
        other => panic!("expected OutOfReach, got {other:?}"),
    }
    // Just inside the bound but still unreachable (would need a fully
    // straight chain with the wrist offsets aligned): IK must fail, not lie.
    let fringe = Iso::translation(r.bound_m - 0.01, 0.0, arm.shoulder().z);
    let rr = arm.reach(&fringe, &t);
    assert!(rr.within_bound);
    assert!(matches!(arm.ik(&fringe, &t, &seeds, &[0.0; 6], &opt), Err(IkError::NoConvergence { .. })));
}

#[test]
fn joint_limits_are_detected_and_respected() {
    let arm = ur5e();
    let mut q = [0.0; 6];
    q[2] = 170f64.to_radians(); // UR5e elbow limit is +-160 deg
    assert_eq!(arm.check_limits(&q).unwrap_err().0, 2);
    q[2] = 0.0;
    q[0] = 2.0 * PI + 0.01;
    assert_eq!(arm.check_limits(&q).unwrap_err().0, 0);
    // Target produced with an elbow angle outside the limit, seeded there:
    // the solver clamps, so any answer it returns is within limits.
    let mut qbad = [0.3, -1.2, 165f64.to_radians(), -1.0, 1.2, 0.4];
    let target = arm.fk(&qbad, &tool());
    if let Ok(sol) = arm.ik(&target, &tool(), &[qbad], &qbad, &IkOptions::default()) {
        assert!(arm.check_limits(&sol.q).is_ok());
        assert!(sol.q[2].abs() <= 160f64.to_radians() + 1e-12);
    }
    qbad[2] = 0.0;
    assert!(arm.check_limits(&qbad).is_ok());
}

fn demo_tube(y: f64) -> BoxTube {
    BoxTube { bottom_start: V3::new(-0.15, y, 0.0), axis: V3::x(), up: V3::z(), width: 0.05, length: 0.30, side: -1.0 }
}

#[test]
fn seam_trajectory_is_straight_continuous_and_within_limits() {
    let arm = ur5e();
    let t = tool();
    let seam = demo_tube(0.45).seam();
    let angles = TorchAngles { work_deg: 45.0, travel_deg: 10.0 };
    let opt = PlanOptions { step_m: 0.005, max_joint_step_rad: 5f64.to_radians(), ik: IkOptions::default() };
    let wps = plan_seam(&arm, &seam, &angles, &t, &opt).expect("seam should be reachable");
    assert_eq!(wps.len(), 61);
    let mut r = RapierArm::build(&arm);
    for w in &wps {
        assert!(arm.check_limits(&w.q).is_ok());
        let tcp = arm.fk(&w.q, &t);
        let (ep, eo) = pose_error(&w.tcp, &tcp);
        assert!(ep.norm() < TOL_POS && eo.norm() < TOL_ROT);
        // On the seam line: distance from the line through start along dir.
        let d = tcp.translation.vector - seam.start;
        let off = (d - seam.dir * d.dot(&seam.dir)).norm();
        assert!(off < TOL_POS, "TCP {off} m off the seam");
        assert!(w.dq_max_rad <= opt.max_joint_step_rad);
        r.set_q(&w.q);
        let (ep, _) = pose_error(&(r.flange() * t), &tcp);
        assert!(ep.norm() < 1e-12);
    }
    std::fs::write(std::env::temp_dir().join("weld_arm_test_traj.csv"), trajectory_csv(&wps)).unwrap();
}

#[test]
fn torch_angles_are_applied() {
    let seam = demo_tube(0.45).seam();
    let tcp = seam.tcp(0.1, &TorchAngles { work_deg: 45.0, travel_deg: 0.0 });
    let z = tcp.rotation * V3::z();
    // 45 deg below horizontal, pointing into the wall, no along-seam component.
    assert!((z.dot(&seam.plate_normal) + (45f64.to_radians()).sin()).abs() < 1e-12);
    assert!(z.dot(&seam.dir).abs() < 1e-12);
    let tcp = seam.tcp(0.1, &TorchAngles { work_deg: 45.0, travel_deg: 10.0 });
    let z = tcp.rotation * V3::z();
    assert!((z.dot(&seam.dir) - 10f64.to_radians().sin()).abs() < 1e-12);
}

#[test]
fn seam_out_of_reach_is_reported_at_first_waypoint() {
    let arm = ur5e();
    let seam = demo_tube(1.6).seam();
    let angles = TorchAngles { work_deg: 45.0, travel_deg: 0.0 };
    let opt = PlanOptions { step_m: 0.01, max_joint_step_rad: 0.2, ik: IkOptions::default() };
    match plan_seam(&arm, &seam, &angles, &tool(), &opt) {
        Err(PlanError::Ik { index: 0, err: IkError::OutOfReach { .. }, .. }) => {}
        other => panic!("expected OutOfReach at waypoint 0, got {other:?}"),
    }
}
