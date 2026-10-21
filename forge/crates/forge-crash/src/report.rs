// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! Metrics, pass/fail against tolerances stated up front, and JSON + Markdown reports.

use crate::compute::RunRecord;
use crate::experiment::Reference;
use crate::iso18571::{self, IsoScore};
use crate::metrics::{lobe_peaks, Curve};
use crate::params::TubeCrush;
use crate::th::TimeHistory;
use serde::{Deserialize, Serialize};
use std::fmt::Write;

/// Acceptance tolerances, fixed before any run (see docs/physics/p1a-tube-crush.md).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tolerances {
    pub mean_force_pct: f64,
    pub peak_force_pct: f64,
    pub fold_count_abs: f64,
    pub iso_min_overall: f64,
    pub max_ke_ratio: f64,
    pub max_hourglass_ratio: f64,
    pub max_added_mass_pct: f64,
}

impl Default for Tolerances {
    fn default() -> Self {
        Self {
            mean_force_pct: 10.0,
            peak_force_pct: 15.0,
            fold_count_abs: 1.0,
            iso_min_overall: 0.58,
            max_ke_ratio: 0.05,
            max_hourglass_ratio: 0.10,
            max_added_mass_pct: 2.0,
        }
    }
}

/// Fold-peak detection settings, applied identically to test and simulation.
pub const FOLD_SMOOTH_MM: f64 = 3.0;
pub const FOLD_PROMINENCE_FRAC_OF_MEAN: f64 = 0.15;
pub const FOLD_MIN_SEP_MM: f64 = 15.0;
/// Grid used for all curve comparisons.
pub const GRID_MM: f64 = 0.5;
/// Smoothing window applied to the simulated force before computing the peak (mm).
pub const PEAK_SMOOTH_MM: f64 = 1.0;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CurveMetrics {
    pub peak_kn: f64,
    pub peak_at_mm: f64,
    pub mean_kn: f64,
    pub energy_j: f64,
    pub fold_count: usize,
    pub fold_peaks_mm: Vec<f64>,
    pub mean_fold_pitch_mm: Option<f64>,
}

pub fn curve_metrics(c: &Curve, crush_mm: f64, mean_for_prominence: f64, peak_smooth_mm: f64) -> CurveMetrics {
    let (pk, at) = if peak_smooth_mm > 0.0 { c.moving_average(peak_smooth_mm).peak_kn(crush_mm) } else { c.peak_kn(crush_mm) };
    let peaks = lobe_peaks(c, crush_mm, FOLD_SMOOTH_MM, FOLD_PROMINENCE_FRAC_OF_MEAN * mean_for_prominence, FOLD_MIN_SEP_MM);
    let xs: Vec<f64> = peaks.iter().map(|p| p.0).collect();
    let pitch = if xs.len() >= 3 { Some((xs[xs.len() - 1] - xs[1]) / (xs.len() - 2) as f64) } else { None };
    CurveMetrics {
        peak_kn: pk,
        peak_at_mm: at,
        mean_kn: c.mean_force_kn(crush_mm),
        energy_j: c.energy_j(crush_mm),
        fold_count: xs.len(),
        fold_peaks_mm: xs,
        mean_fold_pitch_mm: pitch,
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Quality {
    /// max tube KE / IE after the first 10 mm of travel
    pub max_ke_ratio: f64,
    /// hourglass / internal energy at the end
    pub hourglass_ratio_end: f64,
    pub max_added_mass_pct: f64,
    /// platen work (integral of force) vs tube internal energy at the crush length
    pub work_vs_internal_energy_pct: f64,
}

pub fn quality(th: &TimeHistory, sim: &Curve, crush_mm: f64) -> Quality {
    let mut ke_ratio: f64 = 0.0;
    let mut ie_at = 0.0;
    for i in 0..th.time_s.len() {
        if th.disp_mm[i] > 10.0 && th.tube_internal_mj[i] > 0.0 {
            ke_ratio = ke_ratio.max(th.tube_kinetic_mj[i] / th.tube_internal_mj[i]);
        }
        if th.disp_mm[i] <= crush_mm {
            ie_at = th.tube_internal_mj[i];
        }
    }
    let n = th.time_s.len() - 1;
    let he = if th.tube_internal_mj[n] > 0.0 { th.tube_hourglass_mj[n] / th.tube_internal_mj[n] } else { 0.0 };
    let am = th.added_mass_pct.iter().fold(0.0_f64, |m, v| m.max(*v));
    let w = sim.energy_j(crush_mm) * 1000.0; // J -> mJ
    Quality {
        max_ke_ratio: ke_ratio,
        hourglass_ratio_end: he,
        max_added_mass_pct: am,
        work_vs_internal_energy_pct: if ie_at > 0.0 { 100.0 * (w - ie_at) / ie_at } else { f64::NAN },
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Row {
    pub quantity: String,
    pub measured: f64,
    pub simulated: f64,
    pub error_pct: f64,
    pub tolerance: String,
    pub pass: bool,
    pub measured_source: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CaseReport {
    pub case: TubeCrush,
    pub mesh: MeshInfo,
    pub run: RunRecord,
    pub simulated: CurveMetrics,
    pub experiment_digitized: CurveMetrics,
    pub quality: Quality,
    pub iso18571: IsoScore,
    pub rows: Vec<Row>,
    pub note: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MeshInfo {
    pub elements: usize,
    pub nodes: usize,
    pub per_side: usize,
    pub n_axial: usize,
    pub element_size_mm: (f64, f64),
}

pub fn pct(sim: f64, meas: f64) -> f64 {
    100.0 * (sim - meas) / meas
}

pub fn sim_curve(th: &TimeHistory, max_mm: f64) -> Curve {
    // force in kN on the displacement grid; only the monotonic loading part is used
    let mut x = Vec::new();
    let mut y = Vec::new();
    let mut last = f64::NEG_INFINITY;
    for (d, f) in th.disp_mm.iter().zip(&th.force_n) {
        if *d >= last {
            x.push(*d);
            y.push(f / 1000.0);
            last = *d;
        }
    }
    let xmax = max_mm.min(*x.last().unwrap_or(&0.0));
    Curve::resample(&x, &y, GRID_MM, xmax)
}

pub fn build_case_report(
    case: TubeCrush,
    mesh: MeshInfo,
    run: RunRecord,
    th: &TimeHistory,
    reference: &Reference,
    exp: &Curve,
    tol: &Tolerances,
) -> CaseReport {
    let d = reference.crush_length_mm;
    let sim = sim_curve(th, d);
    let expg = Curve::resample(&exp.disp_mm, &exp.force_kn, GRID_MM, d);
    let sm = curve_metrics(&sim, d, reference.mean_kn, PEAK_SMOOTH_MM);
    let em = curve_metrics(&expg, d, reference.mean_kn, 0.0);
    let q = quality(th, &sim, d);
    let n = sim.force_kn.len().min(expg.force_kn.len());
    let iso = iso18571::score(&expg.force_kn[..n], &sim.force_kn[..n], GRID_MM, &Default::default());
    let mut rows = Vec::new();
    let mut row = |q: &str, m: f64, s: f64, tol_s: String, pass: bool, src: &str| {
        rows.push(Row { quantity: q.into(), measured: m, simulated: s, error_pct: pct(s, m), tolerance: tol_s, pass, measured_source: src.into() })
    };
    let e = pct(sm.peak_kn, reference.peak_kn);
    row("Peak force P_u (kN)", reference.peak_kn, sm.peak_kn, format!("±{}%", tol.peak_force_pct), e.abs() <= tol.peak_force_pct, "Park et al. 2022 Table 4");
    let e = pct(sm.mean_kn, reference.mean_kn);
    row(&format!("Mean crush force P_m over 0–{d} mm (kN)"), reference.mean_kn, sm.mean_kn, format!("±{}%", tol.mean_force_pct), e.abs() <= tol.mean_force_pct, "Park et al. 2022 Table 4");
    let (fm, fs) = (em.fold_count as f64, sm.fold_count as f64);
    row("Fold (lobe) count in 0–343 mm", fm, fs, format!("±{}", tol.fold_count_abs), (fs - fm).abs() <= tol.fold_count_abs, "Forge count of force peaks in digitized Park et al. 2022 Fig. 3 (not stated by the authors)");
    if let (Some(pm), Some(ps)) = (em.mean_fold_pitch_mm, sm.mean_fold_pitch_mm) {
        row("Mean fold pitch (mm)", pm, ps, "info only".into(), true, "Forge, from digitized Fig. 3");
    }
    rows.push(Row {
        quantity: "ISO/TS 18571 overall score (vs digitized curve)".into(),
        measured: 1.0,
        simulated: iso.overall,
        error_pct: f64::NAN,
        tolerance: format!("≥ {} (fair)", tol.iso_min_overall),
        pass: iso.overall >= tol.iso_min_overall,
        measured_source: "digitized Park et al. 2022 Fig. 3".into(),
    });
    CaseReport {
        case,
        mesh,
        run,
        simulated: sm,
        experiment_digitized: em,
        quality: q,
        iso18571: iso,
        rows,
        note: "All simulated values are OpenCourant simulation outputs. Measured values are cited; fold count and curve are Forge digitizations of a published figure.".into(),
    }
}

fn f(x: f64, d: usize) -> String {
    if x.is_nan() { "–".into() } else { format!("{x:.d$}") }
}

pub fn case_markdown(r: &CaseReport) -> String {
    let mut s = String::new();
    writeln!(s, "# P1a case `{}`\n", r.case.case_id).unwrap();
    writeln!(s, "Solver: {} ({} threads, backend `{}`). Engine wall time {:.0} s, {} cycles.\n", r.run.solver_version, r.run.threads, r.run.backend, r.run.engine_seconds, r.run.cycles.map_or("?".into(), |c| c.to_string())).unwrap();
    writeln!(s, "Mesh: {} shells, {} x {} elements of {:.2} x {:.2} mm. Material: {}. Top BC: {:?}. Platen speed {} mm/s.\n", r.mesh.elements, 4 * r.mesh.per_side, r.mesh.n_axial, r.mesh.element_size_mm.0, r.mesh.element_size_mm.1, r.case.material.name, r.case.top_boundary, r.case.platen_speed_mm_s).unwrap();
    writeln!(s, "| Quantity | Measured | Simulated | Error | Tolerance | Result |\n|---|---|---|---|---|---|").unwrap();
    for row in &r.rows {
        writeln!(s, "| {} | {} | {} | {} | {} | {} |", row.quantity, f(row.measured, 1), f(row.simulated, 2), if row.error_pct.is_nan() { "–".into() } else { format!("{:+.1}%", row.error_pct) }, row.tolerance, if row.pass { "PASS" } else { "FAIL" }).unwrap();
    }
    let i = &r.iso18571;
    writeln!(s, "\nISO/TS 18571 (Forge implementation, indicative): corridor {:.3}, phase {:.3}, magnitude {:.3}, slope {:.3}, overall {:.3} ({}).\n", i.corridor, i.phase, i.magnitude, i.slope, i.overall, i.rating).unwrap();
    let q = &r.quality;
    writeln!(s, "Run quality: max KE/IE {:.4}, hourglass/IE {:.4}, max added mass {:.3}%, platen work vs IE {:+.2}%.\n", q.max_ke_ratio, q.hourglass_ratio_end, q.max_added_mass_pct, q.work_vs_internal_energy_pct).unwrap();
    writeln!(s, "{}", r.note).unwrap();
    s
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn pct_sign() {
        assert!((pct(110.0, 100.0) - 10.0).abs() < 1e-12);
        assert!((pct(90.0, 100.0) + 10.0).abs() < 1e-12);
    }
}
