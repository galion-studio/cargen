// SPDX-License-Identifier: MIT
// Copyright (c) 3000 galion-studio
//! `weld_arm`: plan a UR5e joint trajectory along a straight box-tube fillet
//! seam, cross-check every waypoint with the Rapier multibody model, and
//! save the trajectory as CSV. Kinematics only (no collision checks).
//!
//! All geometry flags are example inputs, not measured shop data.

use std::process::ExitCode;
use weld_arm::*;

struct Args {
    tool_z: f64,
    step_mm: f64,
    work_deg: f64,
    travel_deg: f64,
    x0: f64,
    y: f64,
    z: f64,
    length: f64,
    width: f64,
    max_jump_deg: f64,
    out: String,
}

fn parse() -> Result<Args, String> {
    let mut a = Args {
        tool_z: 0.0,
        step_mm: 10.0,
        work_deg: 45.0,
        travel_deg: 0.0,
        x0: -0.15,
        y: 0.45,
        z: 0.0,
        length: 0.30,
        width: 0.05,
        max_jump_deg: 10.0,
        out: "trajectory.csv".into(),
    };
    let v: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    while i < v.len() {
        let key = v[i].as_str();
        if key == "-h" || key == "--help" {
            return Err(String::new());
        }
        let val = v.get(i + 1).ok_or(format!("missing value for {key}"))?;
        let num = || val.parse::<f64>().map_err(|_| format!("bad number for {key}: {val}"));
        match key {
            "--tool-z" => a.tool_z = num()?,
            "--step-mm" => a.step_mm = num()?,
            "--work-deg" => a.work_deg = num()?,
            "--travel-deg" => a.travel_deg = num()?,
            "--x0" => a.x0 = num()?,
            "--y" => a.y = num()?,
            "--z" => a.z = num()?,
            "--length" => a.length = num()?,
            "--width" => a.width = num()?,
            "--max-jump-deg" => a.max_jump_deg = num()?,
            "--out" => a.out = val.clone(),
            _ => return Err(format!("unknown flag {key}")),
        }
        i += 2;
    }
    Ok(a)
}

const USAGE: &str = "weld_arm [--tool-z M] [--step-mm MM] [--work-deg D] [--travel-deg D] \
[--x0 M] [--y M] [--z M] [--length M] [--width M] [--max-jump-deg D] [--out FILE]
Tube lies on a plate at height z, axis along +x from x0, bottom-face centre at y.
The seam is the fillet on the tube wall facing the robot (-y side). Units: metres unless noted.";

fn main() -> ExitCode {
    let a = match parse() {
        Ok(a) => a,
        Err(e) => {
            if !e.is_empty() {
                eprintln!("error: {e}");
            }
            eprintln!("{USAGE}");
            return ExitCode::from(2);
        }
    };
    let arm = ur5e();
    let tool = Iso::translation(0.0, 0.0, a.tool_z);
    let tube = BoxTube {
        bottom_start: V3::new(a.x0, a.y, a.z),
        axis: V3::x(),
        up: V3::z(),
        width: a.width,
        length: a.length,
        side: -1.0,
    };
    let seam = tube.seam();
    let angles = TorchAngles { work_deg: a.work_deg, travel_deg: a.travel_deg };
    let opt = PlanOptions { step_m: a.step_mm * 1e-3, max_joint_step_rad: a.max_jump_deg.to_radians(), ik: IkOptions::default() };

    println!("weld_arm: {} (UR DH table), kinematics only, no collision checks", arm.name);
    println!(
        "seam: start ({:.3}, {:.3}, {:.3}) m, dir +x, length {:.0} mm, work {:.1} deg, travel {:.1} deg, tool z {:.3} m",
        seam.start.x, seam.start.y, seam.start.z, seam.length * 1e3, a.work_deg, a.travel_deg, a.tool_z
    );
    let r0 = arm.reach(&seam.tcp(0.0, &angles), &tool);
    let r1 = arm.reach(&seam.tcp(seam.length, &angles), &tool);
    println!(
        "reach: shoulder->TCP {:.3} / {:.3} m (start/end), chain bound {:.3} m; shoulder->flange {:.3} / {:.3} m (datasheet reach {:.3} m)",
        r0.distance_m, r1.distance_m, r0.bound_m, r0.flange_distance_m, r1.flange_distance_m, arm.datasheet_reach_m
    );

    let wps = match plan_seam(&arm, &seam, &angles, &tool, &opt) {
        Ok(w) => w,
        Err(e) => {
            println!("PLAN FAILED: {e}");
            return ExitCode::from(1);
        }
    };

    // Cross-check every waypoint against the Rapier multibody model.
    let mut rapier = RapierArm::build(&arm);
    let mut max_dp: f64 = 0.0;
    let mut max_do: f64 = 0.0;
    for w in &wps {
        rapier.set_q(&w.q);
        let (dp, dor) = pose_error(&arm.fk(&w.q, &Iso::identity()), &rapier.flange());
        max_dp = max_dp.max(dp.norm());
        max_do = max_do.max(dor.norm());
    }

    println!("{:>3} {:>7} {:>9} {:>9} {:>9} {:>9} {:>9} {:>9} {:>9} {:>9} {:>9} {:>9} {:>7}", "i", "s_mm", "x_mm", "y_mm", "z_mm", "q1", "q2", "q3", "q4", "q5", "q6", "pos_err", "manip");
    for (i, w) in wps.iter().enumerate() {
        let p = w.tcp.translation.vector * 1e3;
        print!("{:>3} {:>7.1} {:>9.2} {:>9.2} {:>9.2}", i, w.s_m * 1e3, p.x, p.y, p.z);
        for q in w.q {
            print!(" {:>9.3}", q.to_degrees());
        }
        println!(" {:>9.1e} {:>7.4}", w.pos_err_m, w.manipulability);
    }
    let worst_pos = wps.iter().map(|w| w.pos_err_m).fold(0.0, f64::max);
    let worst_rot = wps.iter().map(|w| w.rot_err_rad).fold(0.0, f64::max);
    let min_m = wps.iter().map(|w| w.manipulability).fold(f64::INFINITY, f64::min);
    let max_jump = wps.iter().map(|w| w.dq_max_rad).fold(0.0, f64::max);
    println!(
        "{} waypoints, all within joint limits; worst IK residual {:.2e} m / {:.2e} rad; max joint step {:.3} deg; min manipulability {:.4}",
        wps.len(), worst_pos, worst_rot, max_jump.to_degrees(), min_m
    );
    println!("Rapier multibody vs DH flange pose: max {:.2e} m / {:.2e} rad", max_dp, max_do);

    if let Err(e) = std::fs::write(&a.out, trajectory_csv(&wps)) {
        eprintln!("could not write {}: {e}", a.out);
        return ExitCode::from(1);
    }
    println!("trajectory saved to {}", a.out);
    ExitCode::SUCCESS
}
