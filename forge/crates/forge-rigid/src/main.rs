// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! `forge-rigid`: run every play-layer validation scenario and print a results table.
//! Play-layer only: these numbers check the game engine, never crash results.

fn main() {
    let checks = forge_rigid::all_checks();
    println!("forge-rigid: Rapier {} (CPU, f32) vs analytic — PLAY LAYER, not crash results", "0.36");
    println!(
        "{:<14} {:<48} {:>12} {:>12} {:>11} {:>10} {:<4}",
        "scenario", "quantity", "simulated", "analytic", "error", "tol", "ok"
    );
    let mut fails = 0;
    for c in &checks {
        let (err, tol) = if c.relative {
            (format!("{:.3}%", c.error * 100.0), format!("{:.2}%", c.tolerance * 100.0))
        } else {
            (format!("{:.2e}", c.error), format!("{:.1e}", c.tolerance))
        };
        if !c.pass() {
            fails += 1;
        }
        println!(
            "{:<14} {:<48} {:>12.6} {:>12.6} {:>11} {:>10} {:<4}",
            c.scenario,
            format!("{} [{}]", c.quantity, c.unit),
            c.simulated,
            c.analytic,
            err,
            tol,
            if c.pass() { "PASS" } else { "FAIL" }
        );
    }
    println!("{} checks, {} failed", checks.len(), fails);
    if fails > 0 {
        std::process::exit(1);
    }
}
