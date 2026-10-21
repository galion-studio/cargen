// SPDX-License-Identifier: MIT
// Copyright (c) 3000 galion-studio
//! Forge robotics prototype: a 6-axis arm following a straight weld seam.
//!
//! * The arm is a UR5e, described by Universal Robots' published DH table
//!   (see [`ur5e`]). It is modelled twice: as plain f64 DH matrices (the
//!   reference) and as a **Rapier multibody** of six revolute joints
//!   ([`RapierArm`]). The tests check that both give the same poses.
//! * IK is damped least squares (DLS) with joint limits enforced at every
//!   step ([`ArmSpec::ik`]). Rapier's own multibody IK is exposed too
//!   ([`RapierArm::ik`]) as a cross-check. It does not know about limits.
//! * A straight fillet seam along the bottom edge of a box tube lying on a
//!   plate ([`BoxTube`]) is sampled into TCP poses, solved point by point and
//!   checked for reach, joint limits, joint jumps and manipulability
//!   ([`plan_seam`]).
//!
//! Kinematics only: no collisions, dynamics, cable or torch-body checks.

#![allow(clippy::needless_range_loop)]

use rapier3d_f64::math::{Pose, Rotation, Vector};
use rapier3d_f64::na;
use rapier3d_f64::prelude::*;
use std::f64::consts::{FRAC_PI_2, PI};
use std::fmt;

pub type Iso = na::Isometry3<f64>;
pub type V3 = na::Vector3<f64>;
/// Joint vector in radians.
pub type Q = [f64; 6];

// ------------------------------------------------------------------ arm spec

/// One row of a standard (distal) Denavit-Hartenberg table:
/// `A = Rz(theta) * Tz(d) * Tx(a) * Rx(alpha)`.
#[derive(Debug, Clone, Copy)]
pub struct Dh {
    pub a: f64,
    pub d: f64,
    pub alpha: f64,
}

#[derive(Debug, Clone)]
pub struct ArmSpec {
    pub name: &'static str,
    pub dh: [Dh; 6],
    /// (min, max) joint limits in radians.
    pub limits: [(f64, f64); 6],
    /// Reach from the datasheet, in metres (informational only: the
    /// manufacturer's measuring point is not modelled here).
    pub datasheet_reach_m: f64,
}

/// UR5e. DH a, d, alpha from Universal Robots, "DH Parameters for
/// calculations of kinematics and dynamics":
/// <https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/>.
/// Joint ranges (+-360 deg, elbow +-160 deg) and 850 mm reach from the UR5e
/// technical specification (SW 5.22 manual):
/// <https://www.universal-robots.com/manuals/EN/HTML/SW5_22/Content/prod-usr-man/complianceUR5e/H_g5_sections/appendix_g5/tech_spec_sheet.htm>.
pub fn ur5e() -> ArmSpec {
    let full = (-2.0 * PI, 2.0 * PI);
    let elbow = (-160f64.to_radians(), 160f64.to_radians());
    ArmSpec {
        name: "UR5e",
        dh: [
            Dh { a: 0.0, d: 0.1625, alpha: FRAC_PI_2 },
            Dh { a: -0.425, d: 0.0, alpha: 0.0 },
            Dh { a: -0.3922, d: 0.0, alpha: 0.0 },
            Dh { a: 0.0, d: 0.1333, alpha: FRAC_PI_2 },
            Dh { a: 0.0, d: 0.0997, alpha: -FRAC_PI_2 },
            Dh { a: 0.0, d: 0.0996, alpha: 0.0 },
        ],
        limits: [full, full, elbow, full, full, full],
        datasheet_reach_m: 0.850,
    }
}

/// Constant part of a DH row: `Tz(d) * Tx(a) * Rx(alpha)`.
fn dh_const(r: &Dh) -> Iso {
    Iso::translation(0.0, 0.0, r.d)
        * Iso::translation(r.a, 0.0, 0.0)
        * Iso::rotation(V3::x() * r.alpha)
}

/// Pose error (target vs actual) as (position error vector, rotation error
/// as a world-frame scaled axis).
pub fn pose_error(target: &Iso, actual: &Iso) -> (V3, V3) {
    let ep = target.translation.vector - actual.translation.vector;
    let eo = (target.rotation * actual.rotation.inverse()).scaled_axis();
    (ep, eo)
}

#[derive(Debug, Clone, PartialEq)]
pub enum IkError {
    /// The TCP target is farther from the shoulder than the sum of all link
    /// offsets, so no joint vector can reach it.
    OutOfReach { distance_m: f64, bound_m: f64 },
    /// The solver did not converge from any seed within joint limits.
    NoConvergence { pos_err_m: f64, rot_err_rad: f64 },
}

impl fmt::Display for IkError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            IkError::OutOfReach { distance_m, bound_m } => write!(
                f,
                "out of reach: TCP is {:.4} m from the shoulder, chain bound is {:.4} m",
                distance_m, bound_m
            ),
            IkError::NoConvergence { pos_err_m, rot_err_rad } => write!(
                f,
                "no IK solution within joint limits (best residual {:.3e} m, {:.3e} rad)",
                pos_err_m, rot_err_rad
            ),
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct IkOptions {
    pub max_iters: usize,
    pub tol_pos_m: f64,
    pub tol_rot_rad: f64,
    /// DLS damping lambda.
    pub damping: f64,
    /// Largest joint change per iteration (rad).
    pub max_step_rad: f64,
}

impl Default for IkOptions {
    fn default() -> Self {
        Self { max_iters: 400, tol_pos_m: 1e-8, tol_rot_rad: 1e-8, damping: 1e-3, max_step_rad: 0.2 }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct IkSolution {
    pub q: Q,
    pub iters: usize,
    pub pos_err_m: f64,
    pub rot_err_rad: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct Reach {
    /// Distance from the shoulder point to the TCP target (m).
    pub distance_m: f64,
    /// Sum of all link offsets after the shoulder plus the tool offset (m).
    pub bound_m: f64,
    pub within_bound: bool,
    /// Distance from the shoulder to the flange for this target (m), for
    /// comparison with the datasheet reach.
    pub flange_distance_m: f64,
}

impl ArmSpec {
    /// Frames 0..=6 (base, then after each joint), world = base frame.
    pub fn frames(&self, q: &Q) -> [Iso; 7] {
        let mut f = [Iso::identity(); 7];
        for i in 0..6 {
            f[i + 1] = f[i] * Iso::rotation(V3::z() * q[i]) * dh_const(&self.dh[i]);
        }
        f
    }

    /// Forward kinematics of the TCP (`flange * tool`).
    pub fn fk(&self, q: &Q, tool: &Iso) -> Iso {
        self.frames(q)[6] * tool
    }

    /// 6x6 geometric Jacobian of the TCP in the base frame (rows: v, w).
    pub fn jacobian(&self, q: &Q, tool: &Iso) -> na::Matrix6<f64> {
        let f = self.frames(q);
        let pe = (f[6] * tool).translation.vector;
        let mut j = na::Matrix6::zeros();
        for i in 0..6 {
            let z = f[i].rotation * V3::z();
            let o = f[i].translation.vector;
            let v = z.cross(&(pe - o));
            j.fixed_view_mut::<3, 1>(0, i).copy_from(&v);
            j.fixed_view_mut::<3, 1>(3, i).copy_from(&z);
        }
        j
    }

    /// Yoshikawa manipulability sqrt(det(J J^T)); 0 at a singularity.
    pub fn manipulability(&self, q: &Q, tool: &Iso) -> f64 {
        let j = self.jacobian(q, tool);
        (j * j.transpose()).determinant().max(0.0).sqrt()
    }

    /// First joint outside its limits, if any.
    pub fn check_limits(&self, q: &Q) -> Result<(), (usize, f64)> {
        for i in 0..6 {
            let (lo, hi) = self.limits[i];
            if !(q[i] >= lo - 1e-12 && q[i] <= hi + 1e-12) {
                return Err((i, q[i]));
            }
        }
        Ok(())
    }

    /// Fixed shoulder point (frame 1 origin; valid because a1 = 0).
    pub fn shoulder(&self) -> V3 {
        V3::new(0.0, 0.0, self.dh[0].d)
    }

    /// Necessary reach condition. The distance from the shoulder to the TCP
    /// can never exceed the sum of link offsets after joint 1 plus the tool
    /// offset (triangle inequality), so beyond that bound the target is
    /// certainly unreachable. Inside it, IK decides.
    pub fn reach(&self, target: &Iso, tool: &Iso) -> Reach {
        let links: f64 = self.dh[1..].iter().map(|r| (r.a * r.a + r.d * r.d).sqrt()).sum();
        let bound = links + tool.translation.vector.norm();
        let distance = (target.translation.vector - self.shoulder()).norm();
        let flange = target * tool.inverse();
        Reach {
            distance_m: distance,
            bound_m: bound,
            within_bound: distance <= bound,
            flange_distance_m: (flange.translation.vector - self.shoulder()).norm(),
        }
    }

    /// DLS IK from one seed, clamping to joint limits after every step.
    pub fn ik_from(&self, target: &Iso, tool: &Iso, seed: &Q, opt: &IkOptions) -> Result<IkSolution, IkError> {
        let mut q = *seed;
        for i in 0..6 {
            q[i] = q[i].clamp(self.limits[i].0, self.limits[i].1);
        }
        let lam2 = opt.damping * opt.damping;
        let mut best = (f64::INFINITY, f64::INFINITY);
        for it in 0..opt.max_iters {
            let (ep, eo) = pose_error(target, &self.fk(&q, tool));
            let (pn, on) = (ep.norm(), eo.norm());
            if pn + on < best.0 + best.1 {
                best = (pn, on);
            }
            if pn <= opt.tol_pos_m && on <= opt.tol_rot_rad {
                return Ok(IkSolution { q, iters: it, pos_err_m: pn, rot_err_rad: on });
            }
            let e = na::Vector6::new(ep.x, ep.y, ep.z, eo.x, eo.y, eo.z);
            let j = self.jacobian(&q, tool);
            let jjt = j * j.transpose() + na::Matrix6::identity() * lam2;
            let Some(x) = jjt.lu().solve(&e) else { break };
            let mut dq = j.transpose() * x;
            let m = dq.amax();
            if m > opt.max_step_rad {
                dq *= opt.max_step_rad / m;
            }
            for i in 0..6 {
                q[i] = (q[i] + dq[i]).clamp(self.limits[i].0, self.limits[i].1);
            }
        }
        Err(IkError::NoConvergence { pos_err_m: best.0, rot_err_rad: best.1 })
    }

    /// Reach check, then DLS IK from each seed. Returns the converged solution
    /// closest (max-abs joint distance) to `prefer`, or the best failure.
    pub fn ik(&self, target: &Iso, tool: &Iso, seeds: &[Q], prefer: &Q, opt: &IkOptions) -> Result<IkSolution, IkError> {
        let r = self.reach(target, tool);
        if !r.within_bound {
            return Err(IkError::OutOfReach { distance_m: r.distance_m, bound_m: r.bound_m });
        }
        let mut best_ok: Option<(f64, IkSolution)> = None;
        let mut best_err = IkError::NoConvergence { pos_err_m: f64::INFINITY, rot_err_rad: f64::INFINITY };
        for s in seeds {
            match self.ik_from(target, tool, s, opt) {
                Ok(sol) => {
                    debug_assert!(self.check_limits(&sol.q).is_ok());
                    let d = joint_dist(&sol.q, prefer);
                    if best_ok.as_ref().is_none_or(|(bd, _)| d < *bd) {
                        best_ok = Some((d, sol));
                    }
                }
                Err(e @ IkError::NoConvergence { pos_err_m, rot_err_rad }) => {
                    if let IkError::NoConvergence { pos_err_m: bp, rot_err_rad: br } = best_err {
                        if pos_err_m + rot_err_rad < bp + br {
                            best_err = e;
                        }
                    }
                }
                Err(e) => return Err(e),
            }
        }
        best_ok.map(|(_, s)| s).ok_or(best_err)
    }
}

/// Max-abs joint difference (rad).
pub fn joint_dist(a: &Q, b: &Q) -> f64 {
    a.iter().zip(b).map(|(x, y)| (x - y).abs()).fold(0.0, f64::max)
}

/// A spread of seeds covering shoulder / elbow / wrist branches.
pub fn default_seeds() -> Vec<Q> {
    let mut v = Vec::new();
    for &q1 in &[0.0, FRAC_PI_2, PI, -FRAC_PI_2] {
        for &q2 in &[-FRAC_PI_2 * 0.5, -FRAC_PI_2 * 1.5] {
            for &q3 in &[FRAC_PI_2, -FRAC_PI_2] {
                for &q5 in &[FRAC_PI_2, -FRAC_PI_2] {
                    v.push([q1, q2, q3, -FRAC_PI_2, q5, 0.0]);
                }
            }
        }
    }
    v
}

// ------------------------------------------------------------- rapier model

fn to_pose(t: &Iso) -> Pose {
    let p = t.translation.vector;
    let r = t.rotation;
    Pose::from_parts(Vector::new(p.x, p.y, p.z), Rotation::from_xyzw(r.i, r.j, r.k, r.w))
}

fn from_pose(p: &Pose) -> Iso {
    let t = p.translation;
    let r = p.rotation;
    Iso::from_parts(
        na::Translation3::new(t.x, t.y, t.z),
        na::UnitQuaternion::from_quaternion(na::Quaternion::new(r.w, r.x, r.y, r.z)),
    )
}

/// The same arm built as a Rapier reduced-coordinate multibody: a fixed base
/// body and six dynamic link bodies joined by revolute multibody joints
/// (with the arm's joint limits). Only kinematics are used here; the link
/// masses are unit placeholders, not robot data.
pub struct RapierArm {
    pub bodies: RigidBodySet,
    pub multibodies: MultibodyJointSet,
    pub joints: Vec<MultibodyJointHandle>,
    q: Q,
}

impl RapierArm {
    pub fn build(spec: &ArmSpec) -> Self {
        let mut bodies = RigidBodySet::new();
        let mut multibodies = MultibodyJointSet::new();
        // Rapier's revolute free axis is the local X axis; R1 maps X onto the
        // DH joint axis Z, so frame1 * Rx(q) * frame2^-1 = Rz(q) * Tz(d) Tx(a) Rx(alpha).
        let r1 = Iso::rotation(V3::y() * -FRAC_PI_2);
        let mut parent = bodies.insert(RigidBodyBuilder::fixed());
        let mut joints = Vec::new();
        let placeholder = MassProperties::new(Vector::ZERO, 1.0, Vector::new(1e-3, 1e-3, 1e-3));
        for i in 0..6 {
            let child = bodies.insert(RigidBodyBuilder::dynamic().additional_mass_properties(placeholder));
            let frame2 = dh_const(&spec.dh[i]).inverse() * r1;
            let (lo, hi) = spec.limits[i];
            let joint = GenericJointBuilder::new(JointAxesMask::LOCKED_REVOLUTE_AXES)
                .local_frame1(to_pose(&r1))
                .local_frame2(to_pose(&frame2))
                .limits(JointAxis::AngX, [lo, hi])
                .build();
            let h = multibodies.insert(parent, child, joint, true).expect("multibody joint");
            joints.push(h);
            parent = child;
        }
        let mut arm = Self { bodies, multibodies, joints, q: [0.0; 6] };
        arm.refresh();
        arm
    }

    fn refresh(&mut self) {
        let (mb, _) = self.multibodies.get_mut(self.joints[5]).unwrap();
        mb.forward_kinematics(&self.bodies, false);
    }

    /// Current joint vector (tracked as the sum of applied displacements).
    pub fn q(&self) -> Q {
        self.q
    }

    /// Set the joint coordinates, then run Rapier forward kinematics.
    pub fn set_q(&mut self, q: &Q) {
        let disp: Vec<f64> = (0..6).map(|i| q[i] - self.q[i]).collect();
        {
            let (mb, _) = self.multibodies.get_mut(self.joints[5]).unwrap();
            mb.apply_displacements(&disp);
        }
        self.q = *q;
        self.refresh();
    }

    /// Flange (link 6) pose in the world, as computed by Rapier.
    pub fn flange(&self) -> Iso {
        let (mb, link) = self.multibodies.get(self.joints[5]).unwrap();
        from_pose(&mb.link(link).unwrap().local_to_world())
    }

    /// Rapier's built-in multibody IK (damped Jacobian, no joint limits) for
    /// the flange, starting from the current coordinates. Applies the result
    /// and returns (q, position error, rotation error).
    pub fn ik(&mut self, target_flange: &Iso, damping: f64, max_iters: usize) -> (Q, f64, f64) {
        let opts = InverseKinematicsOption {
            damping,
            max_iters,
            constrained_axes: JointAxesMask::all(),
            epsilon_linear: 1e-10,
            epsilon_angular: 1e-10,
        };
        let (mb, link) = self.multibodies.get(self.joints[5]).unwrap();
        let mut disp = na::DVector::<f64>::zeros(mb.ndofs());
        mb.inverse_kinematics(&self.bodies, link, &opts, &to_pose(target_flange), |_| true, &mut disp);
        let mut q = self.q;
        for i in 0..6 {
            q[i] += disp[i];
        }
        self.set_q(&q);
        let (ep, eo) = pose_error(target_flange, &self.flange());
        (q, ep.norm(), eo.norm())
    }
}

// -------------------------------------------------------------- weld seam

/// A box (rectangular hollow) tube lying on a flat plate. The seam is the
/// fillet line where one side wall meets the plate.
#[derive(Debug, Clone, Copy)]
pub struct BoxTube {
    /// Centre of the tube's bottom face at its start (on the plate), m.
    pub bottom_start: V3,
    /// Unit tube axis (= seam direction).
    pub axis: V3,
    /// Unit plate normal (up).
    pub up: V3,
    /// Tube width across the plate (m).
    pub width: f64,
    /// Seam / tube length (m).
    pub length: f64,
    /// Which side wall: +1 for `up x axis`, -1 for the opposite side.
    pub side: f64,
}

/// Torch angles in degrees. Work angle is measured from the plate in the
/// plane normal to the seam (45 = bisecting a 90 deg T/fillet corner).
/// Travel angle tilts the torch along the seam (positive = push).
#[derive(Debug, Clone, Copy)]
pub struct TorchAngles {
    pub work_deg: f64,
    pub travel_deg: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct Seam {
    pub start: V3,
    pub dir: V3,
    pub wall_normal: V3,
    pub plate_normal: V3,
    pub length: f64,
}

impl BoxTube {
    pub fn seam(&self) -> Seam {
        let axis = self.axis.normalize();
        let up = self.up.normalize();
        let n = up.cross(&axis).normalize() * self.side.signum();
        Seam { start: self.bottom_start + n * (self.width * 0.5), dir: axis, wall_normal: n, plate_normal: up, length: self.length }
    }
}

impl Seam {
    /// TCP pose at arc length `s`: z axis is the torch (wire) direction
    /// pointing into the joint, x axis follows the travel direction.
    pub fn tcp(&self, s: f64, a: &TorchAngles) -> Iso {
        let p = self.start + self.dir * s;
        let w = a.work_deg.to_radians();
        let t = a.travel_deg.to_radians();
        let approach = -(self.wall_normal * w.cos() + self.plate_normal * w.sin());
        let z = (approach * t.cos() + self.dir * t.sin()).normalize();
        let x = (self.dir - z * self.dir.dot(&z)).normalize();
        let y = z.cross(&x);
        let m = na::Matrix3::from_columns(&[x, y, z]);
        let rot = na::UnitQuaternion::from_rotation_matrix(&na::Rotation3::from_matrix_unchecked(m));
        Iso::from_parts(na::Translation3::from(p), rot)
    }
}

// ------------------------------------------------------------- trajectory

#[derive(Debug, Clone, Copy)]
pub struct Waypoint {
    /// Arc length along the seam (m).
    pub s_m: f64,
    pub tcp: Iso,
    pub q: Q,
    pub pos_err_m: f64,
    pub rot_err_rad: f64,
    pub manipulability: f64,
    /// Max-abs joint change from the previous waypoint (rad).
    pub dq_max_rad: f64,
    /// Shoulder-to-flange distance (m).
    pub flange_distance_m: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub enum PlanError {
    Ik { index: usize, s_m: f64, err: IkError },
    /// Consecutive waypoints need a joint jump larger than allowed (branch
    /// flip or a singularity).
    JointJump { index: usize, s_m: f64, joint: usize, dq_rad: f64 },
}

impl fmt::Display for PlanError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            PlanError::Ik { index, s_m, err } => write!(f, "waypoint {} (s = {:.1} mm): {}", index, s_m * 1e3, err),
            PlanError::JointJump { index, s_m, joint, dq_rad } => write!(
                f,
                "waypoint {} (s = {:.1} mm): joint {} jumps {:.2} deg",
                index,
                s_m * 1e3,
                joint + 1,
                dq_rad.to_degrees()
            ),
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct PlanOptions {
    /// Waypoint spacing along the seam (m).
    pub step_m: f64,
    /// Largest joint change allowed between neighbouring waypoints (rad).
    pub max_joint_step_rad: f64,
    pub ik: IkOptions,
}

/// Sample the seam, solve IK for every waypoint (multi-seed for the first,
/// then seeded by the previous solution) and check reach, limits and jumps.
pub fn plan_seam(arm: &ArmSpec, seam: &Seam, angles: &TorchAngles, tool: &Iso, opt: &PlanOptions) -> Result<Vec<Waypoint>, PlanError> {
    let n = (seam.length / opt.step_m).ceil().max(1.0) as usize;
    let mut out: Vec<Waypoint> = Vec::with_capacity(n + 1);
    let seeds = default_seeds();
    for k in 0..=n {
        let s = seam.length * k as f64 / n as f64;
        let tcp = seam.tcp(s, angles);
        let sol = match out.last() {
            None => {
                // First point: prefer the most dexterous (highest manipulability) branch.
                let mut best: Option<(f64, IkSolution)> = None;
                let mut last_err = None;
                for sd in &seeds {
                    match arm.ik(&tcp, tool, std::slice::from_ref(sd), sd, &opt.ik) {
                        Ok(sol) => {
                            let m = arm.manipulability(&sol.q, tool);
                            if best.as_ref().is_none_or(|(bm, _)| m > *bm) {
                                best = Some((m, sol));
                            }
                        }
                        Err(e) => last_err = Some(e),
                    }
                }
                match best {
                    Some((_, s)) => s,
                    None => return Err(PlanError::Ik { index: k, s_m: s, err: last_err.unwrap() }),
                }
            }
            Some(prev) => arm
                .ik(&tcp, tool, &[prev.q], &prev.q, &opt.ik)
                .map_err(|err| PlanError::Ik { index: k, s_m: s, err })?,
        };
        let dq = out.last().map(|p| joint_dist(&sol.q, &p.q)).unwrap_or(0.0);
        if let Some(p) = out.last() {
            if dq > opt.max_joint_step_rad {
                let j = (0..6).max_by(|&a, &b| (sol.q[a] - p.q[a]).abs().total_cmp(&(sol.q[b] - p.q[b]).abs())).unwrap();
                return Err(PlanError::JointJump { index: k, s_m: s, joint: j, dq_rad: dq });
            }
        }
        out.push(Waypoint {
            s_m: s,
            tcp,
            q: sol.q,
            pos_err_m: sol.pos_err_m,
            rot_err_rad: sol.rot_err_rad,
            manipulability: arm.manipulability(&sol.q, tool),
            dq_max_rad: dq,
            flange_distance_m: arm.reach(&tcp, tool).flange_distance_m,
        });
    }
    Ok(out)
}

/// CSV of the joint trajectory (angles in degrees, lengths in mm).
pub fn trajectory_csv(wps: &[Waypoint]) -> String {
    let mut s = String::from("i,s_mm,x_mm,y_mm,z_mm,q1_deg,q2_deg,q3_deg,q4_deg,q5_deg,q6_deg,pos_err_m,rot_err_rad,manipulability,dq_max_deg\n");
    for (i, w) in wps.iter().enumerate() {
        let p = w.tcp.translation.vector * 1e3;
        s += &format!("{},{:.3},{:.3},{:.3},{:.3}", i, w.s_m * 1e3, p.x, p.y, p.z);
        for q in w.q {
            s += &format!(",{:.6}", q.to_degrees());
        }
        s += &format!(",{:.3e},{:.3e},{:.6},{:.4}\n", w.pos_err_m, w.rot_err_rad, w.manipulability, w.dq_max_rad.to_degrees());
    }
    s
}
