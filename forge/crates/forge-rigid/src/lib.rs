// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! Forge play-layer rigid-body prototype.
//!
//! Headless Rapier (CPU, f32) scenarios, each compared with a closed-form answer.
//! These numbers validate the *game* physics engine only. They are play-layer
//! checks and must never be presented as crash or vehicle-dynamics results.

use rapier3d::prelude::*;

/// Standard gravity used by every scenario (m/s²).
pub const G: f32 = 9.81;

/// One compared quantity: simulated vs analytic, with the tolerance the test asserts.
#[derive(Debug, Clone)]
pub struct Check {
    pub scenario: &'static str,
    pub quantity: String,
    pub unit: &'static str,
    pub simulated: f64,
    pub analytic: f64,
    /// Error metric actually compared with `tolerance`.
    pub error: f64,
    pub tolerance: f64,
    /// `true` for relative error (fraction), `false` for absolute error in `unit`.
    pub relative: bool,
}

impl Check {
    fn rel(scenario: &'static str, quantity: impl Into<String>, unit: &'static str, sim: f64, ana: f64, tol: f64) -> Self {
        let error = if ana.abs() > 1e-12 { ((sim - ana) / ana).abs() } else { (sim - ana).abs() };
        Self { scenario, quantity: quantity.into(), unit, simulated: sim, analytic: ana, error, tolerance: tol, relative: true }
    }
    fn abs(scenario: &'static str, quantity: impl Into<String>, unit: &'static str, sim: f64, ana: f64, tol: f64) -> Self {
        Self { scenario, quantity: quantity.into(), unit, simulated: sim, analytic: ana, error: (sim - ana).abs(), tolerance: tol, relative: false }
    }
    pub fn pass(&self) -> bool {
        self.error.is_finite() && self.error <= self.tolerance
    }
}

fn world(dt: f32, gravity: Vector) -> PhysicsWorld {
    let mut w = PhysicsWorld::new();
    w.gravity = gravity;
    w.integration_parameters.dt = dt;
    w
}

// ---------------------------------------------------------------- free fall

/// Free fall from rest for `t_end` seconds at step `dt`.
/// Returns (simulated drop, analytic 0.5·g·t², simulated speed, analytic g·t).
pub fn free_fall(dt: f32, t_end: f32) -> (f64, f64, f64, f64) {
    let mut w = world(dt, Vector::new(0.0, -G, 0.0));
    let (b, _) = w.insert(
        RigidBodyBuilder::dynamic().translation(Vector::new(0.0, 100.0, 0.0)).can_sleep(false),
        ColliderBuilder::ball(0.1),
    );
    let n = (t_end / dt).round() as usize;
    for _ in 0..n {
        w.step();
    }
    let t = n as f64 * dt as f64;
    let drop = 100.0 - w.bodies[b].translation().y as f64;
    let v = -w.bodies[b].linvel().y as f64;
    (drop, 0.5 * G as f64 * t * t, v, G as f64 * t)
}

pub fn free_fall_checks() -> Vec<Check> {
    let mut out = Vec::new();
    for (label, dt, tol) in [("dt=1/60", 1.0 / 60.0, 0.02), ("dt=1/240", 1.0 / 240.0, 0.005)] {
        let (d, da, v, va) = free_fall(dt, 1.0);
        out.push(Check::rel("free fall", format!("drop at t=1 s, {label}"), "m", d, da, tol));
        out.push(Check::rel("free fall", format!("speed at t=1 s, {label}"), "m/s", v, va, 1e-4));
    }
    out
}

// ---------------------------------------------------------- sphere collision

/// Head-on 1-D collision of two frictionless spheres in zero gravity.
/// Returns (v1', v2') measured after separation.
pub fn sphere_collision(m1: f32, m2: f32, v1: f32, v2: f32, e: f32) -> (f64, f64) {
    let mut w = world(1.0 / 240.0, Vector::ZERO);
    let r = 0.25_f32;
    let mk = |m: f32| {
        ColliderBuilder::ball(r)
            .mass(m)
            .friction(0.0)
            .restitution(e)
            .restitution_combine_rule(CoefficientCombineRule::Max)
    };
    let (a, _) = w.insert(
        RigidBodyBuilder::dynamic().translation(Vector::new(-1.0, 0.0, 0.0)).linvel(Vector::new(v1, 0.0, 0.0)).can_sleep(false),
        mk(m1),
    );
    let (b, _) = w.insert(
        RigidBodyBuilder::dynamic().translation(Vector::new(0.0, 0.0, 0.0)).linvel(Vector::new(v2, 0.0, 0.0)).can_sleep(false),
        mk(m2),
    );
    for _ in 0..480 {
        w.step();
    }
    (w.bodies[a].linvel().x as f64, w.bodies[b].linvel().x as f64)
}

/// Closed-form 1-D impact with coefficient of restitution `e`.
pub fn sphere_collision_analytic(m1: f64, m2: f64, v1: f64, v2: f64, e: f64) -> (f64, f64) {
    let p = m1 * v1 + m2 * v2;
    let a = (p + m2 * e * (v2 - v1)) / (m1 + m2);
    let b = (p + m1 * e * (v1 - v2)) / (m1 + m2);
    (a, b)
}

pub fn collision_checks() -> Vec<Check> {
    let (m1, m2, v1, v2) = (1.0_f32, 3.0_f32, 4.0_f32, -1.0_f32);
    let mut out = Vec::new();
    for (label, e) in [("elastic e=1.0", 1.0_f32), ("inelastic e=0.5", 0.5), ("plastic e=0.0", 0.0)] {
        let (s1, s2) = sphere_collision(m1, m2, v1, v2, e);
        let (a1, a2) = sphere_collision_analytic(m1 as f64, m2 as f64, v1 as f64, v2 as f64, e as f64);
        let p0 = (m1 * v1 + m2 * v2) as f64;
        let p1 = m1 as f64 * s1 + m2 as f64 * s2;
        let ke0 = 0.5 * (m1 * v1 * v1 + m2 * v2 * v2) as f64;
        let ke1 = 0.5 * (m1 as f64 * s1 * s1 + m2 as f64 * s2 * s2);
        let ke_a = 0.5 * (m1 as f64 * a1 * a1 + m2 as f64 * a2 * a2);
        out.push(Check::abs("sphere impact", format!("{label}: momentum change"), "kg·m/s", p1, p0, 1e-3));
        out.push(Check::abs("sphere impact", format!("{label}: restitution"), "-", (s2 - s1) / (v1 - v2) as f64, e as f64, 0.02));
        out.push(Check::abs("sphere impact", format!("{label}: v1'"), "m/s", s1, a1, 0.05));
        out.push(Check::abs("sphere impact", format!("{label}: v2'"), "m/s", s2, a2, 0.05));
        out.push(Check::abs("sphere impact", format!("{label}: KE after / before"), "-", ke1 / ke0, ke_a / ke0, 0.02));
    }
    out
}

// ---------------------------------------------------------------- incline

/// Box released from rest on a fixed incline of angle `theta` (rad) with Coulomb
/// coefficient `mu` on both colliders. Returns the measured acceleration along the
/// slope (positive = downhill), fitted between t=0.25 s and t=1.25 s.
pub fn incline(theta: f32, mu: f32, coulomb: bool) -> f64 {
    incline_with(theta, mu, coulomb, 4)
}

/// [`incline`] with an explicit solver iteration (substep) count.
pub fn incline_with(theta: f32, mu: f32, coulomb: bool, iters: usize) -> f64 {
    incline_cfg(theta, mu, coulomb, iters, false)
}

/// [`incline_with`] plus the `friction_in_bias_pass` switch.
pub fn incline_cfg(theta: f32, mu: f32, coulomb: bool, iters: usize, friction_in_bias: bool) -> f64 {
    let dt = 1.0 / 240.0;
    let mut w = world(dt, Vector::new(0.0, -G, 0.0));
    w.integration_parameters.num_solver_iterations = iters;
    w.integration_parameters.friction_in_bias_pass = friction_in_bias;
    if coulomb {
        w.integration_parameters.friction_model = FrictionModel::Coulomb;
    }
    let rot = Rotation::from_scaled_axis(Vector::new(0.0, 0.0, theta));
    let (gh, bh) = (0.1_f32, 0.1_f32);
    w.insert(
        RigidBodyBuilder::fixed().rotation(Vector::new(0.0, 0.0, theta)),
        ColliderBuilder::cuboid(50.0, gh, 2.0).friction(mu).friction_combine_rule(CoefficientCombineRule::Average),
    );
    let start = rot * Vector::new(0.0, gh + bh, 0.0);
    let (b, _) = w.insert(
        RigidBodyBuilder::dynamic().translation(start).rotation(Vector::new(0.0, 0.0, theta)).can_sleep(false),
        ColliderBuilder::cuboid(bh, bh, bh).density(1000.0).friction(mu).friction_combine_rule(CoefficientCombineRule::Average),
    );
    let downhill = rot * Vector::new(-1.0, 0.0, 0.0);
    let (n0, n1) = ((0.25 / dt) as usize, (1.25 / dt) as usize);
    let mut v0 = 0.0;
    for i in 1..=n1 {
        w.step();
        if i == n0 {
            v0 = w.bodies[b].linvel().dot(downhill) as f64;
        }
    }
    let v1 = w.bodies[b].linvel().dot(downhill) as f64;
    (v1 - v0) / ((n1 - n0) as f64 * dt as f64)
}

pub fn incline_analytic(theta: f64, mu: f64) -> f64 {
    if mu >= theta.tan() {
        0.0
    } else {
        G as f64 * (theta.sin() - mu * theta.cos())
    }
}

/// Friction coefficient implied by a measured downhill acceleration.
pub fn effective_mu(theta: f64, accel: f64) -> f64 {
    (G as f64 * theta.sin() - accel) / (G as f64 * theta.cos())
}

/// Tolerance on the effective friction coefficient per friction model.
/// `FrictionModel::Coulomb` shows a systematic ~6 % under-friction in Rapier 0.36
/// (independent of solver iterations); the wider bound documents that known deviation.
pub const MU_TOL_SIMPLIFIED: f64 = 0.02;
pub const MU_TOL_COULOMB: f64 = 0.08;

pub fn incline_checks() -> Vec<Check> {
    let th = 30f32.to_radians();
    let thd = th as f64;
    let mut out = Vec::new();
    for (model, coulomb, mu_tol) in [("simplified", false, MU_TOL_SIMPLIFIED), ("coulomb", true, MU_TOL_COULOMB)] {
        let a = incline(th, 0.0, coulomb);
        out.push(Check::rel("incline 30°", format!("accel, mu=0, {model}"), "m/s²", a, incline_analytic(thd, 0.0), 0.02));
        for mu in [0.2_f32, 0.4] {
            let a = incline(th, mu, coulomb);
            if !coulomb {
                out.push(Check::rel("incline 30°", format!("accel, mu={mu}, {model}"), "m/s²", a, incline_analytic(thd, mu as f64), 0.02));
            }
            out.push(Check::rel("incline 30°", format!("effective mu, mu={mu}, {model}"), "-", effective_mu(thd, a), mu as f64, mu_tol));
        }
        let a = incline(th, 0.7, coulomb);
        out.push(Check::abs("incline 30°", format!("accel, mu=0.7 (sticks), {model}"), "m/s²", a, 0.0, 0.01));
    }
    out
}

// ---------------------------------------------------------------- pendulum

/// Arithmetic–geometric mean, for the exact large-amplitude pendulum period.
fn agm(mut a: f64, mut b: f64) -> f64 {
    for _ in 0..30 {
        let (an, bn) = (0.5 * (a + b), (a * b).sqrt());
        a = an;
        b = bn;
    }
    a
}

/// Exact period of a compound pendulum: ball of radius `r` on a massless arm of length `l`,
/// released from `theta0` (rad). T = 2π/ω0 / AGM(1, cos(θ0/2)), ω0² = m g l / I_pivot.
pub fn pendulum_analytic(l: f64, r: f64, theta0: f64) -> f64 {
    let i_over_m = 0.4 * r * r + l * l;
    let t0 = 2.0 * std::f64::consts::PI * (i_over_m / (G as f64 * l)).sqrt();
    t0 / agm(1.0, (theta0 / 2.0).cos())
}

/// Result of a simulated pendulum run.
#[derive(Debug, Clone, Copy)]
pub struct PendulumRun {
    pub period: f64,
    /// Max |distance(pivot, bob) − l| over the run (joint drift), m.
    pub max_drift: f64,
    /// Amplitude at the end relative to the start (energy drift indicator).
    pub amplitude_ratio: f64,
}

/// Revolute-joint pendulum (axis Z). `multibody` selects the reduced-coordinate
/// multibody joint instead of the impulse (constraint) joint.
pub fn pendulum(l: f32, r: f32, theta0: f32, dt: f32, multibody: bool) -> PendulumRun {
    let mut w = world(dt, Vector::new(0.0, -G, 0.0));
    w.integration_parameters.num_solver_iterations = 8;
    let anchor = w.insert_body(RigidBodyBuilder::fixed());
    let pos = Vector::new(l * theta0.sin(), -l * theta0.cos(), 0.0);
    let (bob, _) = w.insert(
        RigidBodyBuilder::dynamic().translation(pos).can_sleep(false),
        ColliderBuilder::ball(r).density(1000.0),
    );
    let joint = RevoluteJointBuilder::new(Vector::Z).local_anchor1(Vector::ZERO).local_anchor2(-pos);
    if multibody {
        let h = w.insert_multibody_joint(anchor, bob, joint).expect("multibody joint");
        // Rapier gives every free angular multibody DoF a default damping of 0.1;
        // zero it so the analytic (undamped) period applies.
        w.multibody_joints.get_mut(h).expect("multibody").0.damping_mut().fill(0.0);
    } else {
        w.insert_impulse_joint(anchor, bob, joint);
    }
    let t_est = pendulum_analytic(l as f64, r as f64, theta0 as f64);
    let n = ((6.2 * t_est) / dt as f64) as usize; // ~6 periods
    let mut crossings: Vec<f64> = Vec::new();
    let mut prev_x = pos.x as f64;
    let mut max_drift = 0.0_f64;
    let mut last_amp = 0.0_f64;
    for i in 1..=n {
        w.step();
        let p = w.bodies[bob].translation();
        let x = p.x as f64;
        max_drift = max_drift.max((p.length() as f64 - l as f64).abs());
        // Downward-going zero crossings of x (x: + → −), linearly interpolated in time.
        if prev_x > 0.0 && x <= 0.0 {
            let frac = prev_x / (prev_x - x);
            crossings.push(((i - 1) as f64 + frac) * dt as f64);
        }
        if i > n - (t_est / dt as f64) as usize {
            last_amp = last_amp.max(x.abs());
        }
        prev_x = x;
    }
    let k = crossings.len();
    let period = if k >= 2 { (crossings[k - 1] - crossings[0]) / (k - 1) as f64 } else { f64::NAN };
    PendulumRun { period, max_drift, amplitude_ratio: last_amp / pos.x as f64 }
}

pub fn pendulum_checks() -> Vec<Check> {
    let (l, r) = (1.0_f32, 0.05_f32);
    let mut out = Vec::new();
    for (deg, tol) in [(5.0_f32, 0.005), (45.0, 0.005)] {
        let th = deg.to_radians();
        let ana = pendulum_analytic(l as f64, r as f64, th as f64);
        for (label, mb) in [("impulse joint", false), ("multibody joint", true)] {
            let run = pendulum(l, r, th, 1.0 / 240.0, mb);
            out.push(Check::rel("pendulum", format!("period, θ0={deg}°, {label}"), "s", run.period, ana, tol));
            out.push(Check::abs("pendulum", format!("joint drift, θ0={deg}°, {label}"), "m", run.max_drift, 0.0, 1e-3));
            out.push(Check::abs("pendulum", format!("amplitude after 6 T, θ0={deg}°, {label}"), "ratio", run.amplitude_ratio, 1.0, 0.05));
        }
    }
    out
}

// -------------------------------------------------------------------- CCD

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CcdMode {
    /// `max_ccd_substeps = 0`: all CCD off (expected to tunnel).
    Off,
    /// Rapier default: fast bodies are swept against fixed colliders automatically.
    Default,
    /// `ccd_enabled(true)` on the projectile.
    Bullet,
}

/// Sphere (r = 2 cm) at `speed` m/s against a fixed wall 1 cm thick (front face at x = 0),
/// dt = 1/60 s, so the projectile moves `speed/60` m per step (5 m at 300 m/s).
/// Returns the projectile's final x of its centre; the analytic stop position is x = −r
/// (contact on the front face; e = 0 so it does not bounce).
pub fn ccd_projectile(speed: f32, mode: CcdMode) -> f64 {
    let mut w = world(1.0 / 60.0, Vector::ZERO);
    if mode == CcdMode::Off {
        w.integration_parameters.max_ccd_substeps = 0;
    }
    let half_t = 0.005_f32;
    w.insert(
        RigidBodyBuilder::fixed().translation(Vector::new(half_t, 0.0, 0.0)),
        ColliderBuilder::cuboid(half_t, 2.0, 2.0).restitution(0.0).friction(0.0),
    );
    let (p, _) = w.insert(
        RigidBodyBuilder::dynamic()
            .translation(Vector::new(-7.3, 0.0, 0.0))
            .linvel(Vector::new(speed, 0.0, 0.0))
            .ccd_enabled(mode == CcdMode::Bullet)
            .can_sleep(false),
        ColliderBuilder::ball(0.02).density(7800.0).restitution(0.0).friction(0.0),
    );
    for _ in 0..60 {
        w.step();
    }
    w.bodies[p].translation().x as f64
}

pub const CCD_RADIUS: f64 = 0.02;

pub fn ccd_checks() -> Vec<Check> {
    let mut out = Vec::new();
    for speed in [100.0_f32, 300.0] {
        for (label, mode) in [("default CCD", CcdMode::Default), ("ccd_enabled", CcdMode::Bullet)] {
            let x = ccd_projectile(speed, mode);
            out.push(Check::abs("CCD thin wall", format!("stop x, {speed} m/s, {label}"), "m", x, -CCD_RADIUS, 0.01));
        }
    }
    // Control: CCD off must tunnel (x far beyond the wall). Error = 0 when it tunnels.
    let x = ccd_projectile(300.0, CcdMode::Off);
    let tunneled = if x > 1.0 { 1.0 } else { 0.0 };
    out.push(Check::abs("CCD thin wall", "control: CCD off tunnels (1 = yes)", "bool", tunneled, 1.0, 0.0));
    out
}

// ------------------------------------------------------------- determinism

/// A small pile of 20 boxes falling onto ground; returns the bit pattern of all final poses.
pub fn pile_state_bits() -> Vec<u32> {
    let mut w = world(1.0 / 60.0, Vector::new(0.0, -G, 0.0));
    w.insert(RigidBodyBuilder::fixed(), ColliderBuilder::cuboid(10.0, 0.1, 10.0));
    let mut hs = Vec::new();
    for i in 0..20 {
        let x = (i % 4) as f32 * 0.21 - 0.3 + 0.01 * (i / 4) as f32;
        let y = 0.3 + 0.25 * (i / 4) as f32;
        let (h, _) = w.insert(
            RigidBodyBuilder::dynamic().translation(Vector::new(x, y, 0.0)).rotation(Vector::new(0.0, 0.1 * i as f32, 0.0)),
            ColliderBuilder::cuboid(0.1, 0.1, 0.1),
        );
        hs.push(h);
    }
    for _ in 0..240 {
        w.step();
    }
    let mut bits = Vec::new();
    for h in hs {
        let t = w.bodies[h].translation();
        let q = *w.bodies[h].rotation();
        bits.extend([t.x, t.y, t.z, q.x, q.y, q.z, q.w].map(f32::to_bits));
    }
    bits
}

pub fn determinism_checks() -> Vec<Check> {
    let a = pile_state_bits();
    let b = pile_state_bits();
    let diff = a.iter().zip(&b).filter(|(x, y)| x != y).count();
    vec![Check::abs("determinism", "20-box pile, 2 runs: differing pose words", "count", diff as f64, 0.0, 0.0)]
}

/// Every scenario, in report order.
pub fn all_checks() -> Vec<Check> {
    let mut v = free_fall_checks();
    v.extend(collision_checks());
    v.extend(incline_checks());
    v.extend(pendulum_checks());
    v.extend(ccd_checks());
    v.extend(determinism_checks());
    v
}
