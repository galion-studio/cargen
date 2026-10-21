// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! Analytic validation suite for the play-layer rigid-body engine (Rapier, CPU).
//! Each test asserts the error against a closed-form answer within a stated tolerance.

use forge_rigid::*;

fn assert_all(checks: Vec<Check>) {
    let mut failed = Vec::new();
    for c in &checks {
        println!("{:<14} {:<55} sim={:<14.7} ana={:<14.7} err={:.3e} tol={:.1e}", c.scenario, c.quantity, c.simulated, c.analytic, c.error, c.tolerance);
        if !c.pass() {
            failed.push(format!("{}: {} (err {:.3e} > tol {:.1e})", c.scenario, c.quantity, c.error, c.tolerance));
        }
    }
    assert!(failed.is_empty(), "failed checks:\n{}", failed.join("\n"));
}

#[test]
fn free_fall_matches_half_g_t_squared() {
    assert_all(free_fall_checks());
}

#[test]
fn free_fall_error_is_first_order_in_dt() {
    // Symplectic Euler over n·k steps (k = 4 solver substeps) gives drop = ½g t² (1 + 1/(n k)):
    // the relative error must shrink ~4x when dt shrinks 4x.
    let (d1, a1, _, _) = free_fall(1.0 / 60.0, 1.0);
    let (d2, a2, _, _) = free_fall(1.0 / 240.0, 1.0);
    let (e1, e2) = ((d1 - a1) / a1, (d2 - a2) / a2);
    let ratio = e1 / e2;
    assert!((ratio - 4.0).abs() < 0.2, "error ratio {ratio} (e1={e1}, e2={e2})");
    assert!((e1 - 1.0 / 240.0).abs() < 2e-4, "dt=1/60 error {e1} vs predicted 1/240");
}

#[test]
fn sphere_collisions_conserve_momentum_and_restitution() {
    assert_all(collision_checks());
}

#[test]
fn incline_with_friction() {
    assert_all(incline_checks());
}

#[test]
fn revolute_pendulum_period() {
    assert_all(pendulum_checks());
}

#[test]
fn ccd_fast_projectile_vs_thin_wall() {
    assert_all(ccd_checks());
}

#[test]
fn same_machine_determinism() {
    assert_all(determinism_checks());
}

#[test]
fn analytic_helpers_sanity() {
    // Small-angle limit: AGM correction → 1, so T → 2π√(I/(m g l)).
    let t = pendulum_analytic(1.0, 0.0, 1e-6);
    let t0 = 2.0 * std::f64::consts::PI * (1.0 / G as f64).sqrt();
    assert!((t - t0).abs() < 1e-9);
    // 90° release: T/T0 = 1.18034 (tabulated complete elliptic integral).
    let r = pendulum_analytic(1.0, 0.0, std::f64::consts::FRAC_PI_2) / t0;
    assert!((r - 1.18034).abs() < 1e-4, "{r}");
    let (a, b) = sphere_collision_analytic(1.0, 1.0, 1.0, 0.0, 1.0);
    assert!((a - 0.0).abs() < 1e-12 && (b - 1.0).abs() < 1e-12);
}
