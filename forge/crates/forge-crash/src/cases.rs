// SPDX-License-Identifier: MIT
// Copyright (c) 3000 Galion / galion-studio
//! Named validation cases: solver parameters plus the reference experiment.

use crate::experiment::{self, Reference};
use crate::params::{self, BottomBoundary, Loading, Material, Section, TopBoundary, TubeCrush};

pub const US2_DIGITIZED: &str = "data/p1a/park2022_us2_fig3_digitized.csv";

pub struct Case {
    pub params: TubeCrush,
    pub reference: Reference,
}

/// Multi-linear true-stress curve from Park et al. (2022) Table 2 values (yield, engineering
/// tensile strength, uniform strain), converted by Forge as in `params::a500_us2_multilinear`.
pub fn park_material(spec: &str, e: f64, sy: f64, su: f64, eu: f64) -> Material {
    let sig = su * (1.0 + eu);
    let ep = (1.0 + eu).ln() - sig / e;
    Material {
        name: format!("ASTM A500 Gr.A ({spec}), multi-linear true stress"),
        source: "Park, Cho & Kim (2022) Materials 15:2107 Table 2, doi:10.3390/ma15062107 (CC BY 4.0); engineering->true conversion by Forge".into(),
        density_t_per_mm3: 7.85e-9,
        youngs_mpa: e,
        poisson: 0.3,
        hardening: vec![(0.0, sy), (ep, sig), (1.0, sig)],
    }
}

/// AA6063-F annealed: E, nu, density, 0.2% proof stress 50 MPa and tensile strength 120 MPa
/// from Lykakos et al. (2021) Table 1 (manufacturer data). The uniform strain is NOT given;
/// Forge ASSUMES 0.15 and fits a Voce curve through yield and the true tensile point with the
/// Considere condition. This hardening shape is an assumption, not source data.
pub fn aa6063f_assumed() -> Material {
    let (sy, su, eu, e) = (50.0_f64, 120.0_f64, 0.15_f64, 69_500.0_f64);
    let sig_u = su * (1.0 + eu);
    let eps_u = (1.0 + eu).ln();
    // Voce: s = sy + Q (1 - exp(-b ep)); need s(eps_u) = sig_u and ds/dep = sig_u at eps_u.
    // => (sig_u - sy) = Q (1 - x), Q b x = sig_u with x = exp(-b eps_u). Solve for b by bisection.
    let f = |b: f64| {
        let x = (-b * eps_u).exp();
        let q = (sig_u - sy) / (1.0 - x);
        q * b * x - sig_u
    };
    let (mut lo, mut hi) = (1e-3, 200.0);
    for _ in 0..200 {
        let mid = 0.5 * (lo + hi);
        if f(lo) * f(mid) <= 0.0 { hi = mid } else { lo = mid }
    }
    let b = 0.5 * (lo + hi);
    let q = (sig_u - sy) / (1.0 - (-b * eps_u).exp());
    let mut pts: Vec<(f64, f64)> = [0.0, 0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14]
        .iter()
        .map(|ep| (*ep, sy + q * (1.0 - (-b * ep).exp())))
        .collect();
    let last = pts.last().unwrap().1;
    pts.push((1.0, last));
    Material {
        name: "AA6063-F annealed (Voce fit, ASSUMED uniform strain 0.15)".into(),
        source: "Lykakos et al. (2021) Dynamics 1:22 Table 1 (E, nu, rho, Rp0.2 = 50 MPa, Rm = 120 MPa; manufacturer data), doi:10.3390/dynamics1010004 (CC BY 4.0); uniform strain 0.15 and Voce shape assumed by Forge".into(),
        density_t_per_mm3: 2.70e-9,
        youngs_mpa: e,
        poisson: 0.33,
        hardening: pts,
    }
}

fn park_case(spec: &str, h: f64) -> Option<Case> {
    let (b, t, e, sy, su, eu) = match spec {
        "US-1" => (100.0, 2.2, 199_200.0, 286.1, 351.9, 0.210),
        "US-2" => (100.0, 2.8, 205_800.0, 310.8, 363.3, 0.177),
        "US-3" => (100.0, 3.0, 207_800.0, 299.3, 351.2, 0.178),
        "US-4" => (100.0, 4.2, 199_900.0, 366.8, 450.8, 0.183),
        "US-5" => (75.0, 2.1, 200_100.0, 328.5, 399.4, 0.187),
        "US-6" => (75.0, 3.2, 209_700.0, 427.6, 477.2, 0.125),
        _ => return None,
    };
    let mut p = params::p1a_us2_baseline(h);
    p.breadth_mm = b;
    p.thickness_mm = t;
    p.material = park_material(spec, e, sy, su, eu);
    // imperfection half-waves ~ L / a
    p.imperfection_half_waves = ((p.length_mm / p.midline_width()).round() as u32).max(1);
    p.case_id = format!("park_{}_h{h}", spec.to_lowercase().replace('-', ""));
    let dig = if spec == "US-2" { Some(US2_DIGITIZED) } else { None };
    Some(Case { params: p, reference: experiment::park2022(spec, dig)? })
}

fn lykakos_case(dynamic: bool, h: f64) -> Case {
    let mut p = params::p1a_us2_baseline(h);
    p.section = Section::Circular;
    p.breadth_mm = 38.6;
    p.thickness_mm = 1.5;
    p.length_mm = 100.0;
    p.material = aa6063f_assumed();
    p.top_boundary = TopBoundary::FrictionWall;
    p.bottom_boundary = BottomBoundary::FrictionWall;
    p.friction = 0.2; // not reported; Forge assumption
    p.imperfection_w0_mm = Some(0.02); // tiny axisymmetric seed; not measured
    p.imperfection_half_waves = 10;
    p.circ_waves = 0;
    p.th_dt_s = 1.0e-5;
    if dynamic {
        p.loading = Loading::DropMass { mass_t: 0.078, velocity_mm_s: (2.0_f64 * 9810.0 * 2500.0).sqrt() };
        p.crush_distance_mm = 68.0;
        p.case_id = format!("lykakos_al_dyn_h{h}");
    } else {
        p.platen_speed_mm_s = 1000.0;
        p.ramp_time_s = 0.002;
        p.crush_distance_mm = 62.0;
        p.case_id = format!("lykakos_al_qs_h{h}");
    }
    Case { params: p, reference: experiment::lykakos2021(dynamic) }
}

/// Steel US-2 crushed at 10 m/s with Cowper-Symonds rate scaling (D = 6844 1/s, q = 3.91,
/// A&J 1984, as quoted in research/crush-experiments.md). There is no
/// matching measured dynamic test: the reference values are the quasi-static ones and the
/// result is an unvalidated prediction of the rate effect.
fn us2_dynamic(h: f64) -> Case {
    let mut c = park_case("US-2", h).unwrap();
    c.params.platen_speed_mm_s = 10_000.0;
    c.params.ramp_time_s = 0.0005;
    c.params.cowper_symonds = Some((6844.0, 3.91));
    c.params.th_dt_s = 1.0e-5;
    c.params.case_id = format!("park_us2_10ms_cs_h{h}");
    c.reference.specimen.push_str(" [simulated at 10 m/s with Cowper-Symonds; compared with the QUASI-STATIC test, no dynamic test exists]");
    c
}

/// A&J (1986) type E steel. Hardening: yield and tensile strength from the paper; the
/// uniform strain (0.15) is a Forge ASSUMPTION. Rate: Cowper-Symonds D = 6844 1/s, q = 3.91
/// (A&J 1984 eq. 38-39, fitted to the ultimate stress; see research/crush-experiments.md).
fn aj86_case(spec: &str, h: f64, rate: bool) -> Option<Case> {
    let reference = experiment::aj1986_e(spec)?;
    let mut p = params::p1a_us2_baseline(h);
    let (c, t, l) = match spec { "E10" => (36.45, 1.63, 221.9), _ => (36.49, 1.63, 222.1) };
    p.breadth_mm = c; // treated as the outer side (A&J define c as the side length)
    p.thickness_mm = t;
    p.length_mm = l;
    let e = 207_000.0; // not reported; nominal steel modulus (assumption)
    let mut m = park_material("A&J type E", e, 272.7, 315.6, 0.15);
    m.name = "mild steel A&J type E, bilinear true stress (ASSUMED uniform strain 0.15)".into();
    m.source = "Abramowicz & Jones (1986) IJIE 4:243, sigma_y 272.7 / sigma_u 315.6 MPa; E = 207 GPa and uniform strain 0.15 assumed by Forge".into();
    p.material = m;
    p.imperfection_half_waves = ((l / p.midline_width()).round() as u32).max(1);
    p.th_dt_s = 1.0e-5;
    if spec == "E3" {
        p.loading = Loading::DropMass { mass_t: 0.1355, velocity_mm_s: 9620.0 };
        p.crush_distance_mm = 160.0;
    } else {
        p.crush_distance_mm = 160.0;
    }
    if rate {
        p.cowper_symonds = Some((6844.0, 3.91));
    }
    p.case_id = format!("aj86_{}{}_h{h}", spec.to_lowercase(), if rate { "_cs" } else { "" });
    Some(Case { params: p, reference })
}

pub fn by_name(name: &str, h: f64) -> Option<Case> {
    match name {
        "baseline" | "us2" => park_case("US-2", h).map(|mut c| {
            c.params.case_id = format!("p1a_us2_baseline_h{h}");
            c
        }),
        "pp" => park_case("US-2", h).map(|mut c| {
            c.params.material = params::a500_us2_perfectly_plastic();
            c.params.case_id = format!("p1a_us2_pp_h{h}");
            c
        }),
        "friction" => park_case("US-2", h).map(|mut c| {
            c.params.top_boundary = TopBoundary::FrictionWall;
            c.params.case_id = format!("p1a_us2_friction_h{h}");
            c
        }),
        "us1" => park_case("US-1", h),
        "us3" => park_case("US-3", h),
        "us4" => park_case("US-4", h),
        "us5" => park_case("US-5", h),
        "us6" => park_case("US-6", h),
        "al_qs" => Some(lykakos_case(false, h)),
        "al_dyn" => Some(lykakos_case(true, h)),
        "us2_dyn" => Some(us2_dynamic(h)),
        "aj_e10" => aj86_case("E10", h, false),
        "aj_e10_cs" => aj86_case("E10", h, true),
        "aj_e3" => aj86_case("E3", h, false),
        "aj_e3_cs" => aj86_case("E3", h, true),
        _ => None,
    }
}

pub const NAMES: &[&str] = &["baseline", "pp", "friction", "us1", "us3", "us4", "us5", "us6", "al_qs", "al_dyn", "us2_dyn", "aj_e10", "aj_e10_cs", "aj_e3", "aj_e3_cs"];

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn all_cases_validate() {
        for n in NAMES {
            let c = by_name(n, 5.0).unwrap();
            c.params.validate().unwrap();
        }
    }
    #[test]
    fn voce_fit_hits_targets() {
        let m = aa6063f_assumed();
        assert_eq!(m.hardening[0].1, 50.0);
        let last = m.hardening.last().unwrap().1;
        assert!(last > 120.0 && last < 140.0, "{last}");
    }
    #[test]
    fn baseline_id_unchanged() {
        assert_eq!(by_name("baseline", 5.0).unwrap().params.case_id, "p1a_us2_baseline_h5");
    }
}
