// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! Typed parameters for the P1a square-tube axial crush case.
//! Units throughout: tonne (Mg), mm, s  =>  force N, stress MPa, energy mJ.

use serde::{Deserialize, Serialize};

/// Hardening description, always as (equivalent plastic strain, true stress MPa).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Material {
    pub name: String,
    /// Where every number below comes from.
    pub source: String,
    pub density_t_per_mm3: f64,
    pub youngs_mpa: f64,
    pub poisson: f64,
    /// Piecewise-linear hardening curve, first point must be at plastic strain 0.
    pub hardening: Vec<(f64, f64)>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum TopBoundary {
    /// Moving rigid wall, nodes stick once they touch it (Radioss RWALL slide=1).
    /// Closest to the "fixed" loading BC selected by Park et al. (2022), Table 11.
    TiedWall,
    /// Moving rigid wall with Coulomb friction (Radioss RWALL slide=2).
    FrictionWall,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TubeCrush {
    pub case_id: String,
    /// Outer section breadth b (mm).
    pub breadth_mm: f64,
    /// Wall thickness t (mm).
    pub thickness_mm: f64,
    /// Tube height L (mm).
    pub length_mm: f64,
    /// Target in-plane element edge (mm); actual size is rounded to fit the geometry.
    pub element_size_mm: f64,
    /// Imperfection amplitude factor `amp` in w0 = amp * beta^2 * t (Park et al. 2022, Eq. 1).
    pub imperfection_amp: f64,
    /// Number of axial half-waves of the imperfection shape.
    pub imperfection_half_waves: u32,
    pub material: Material,
    /// Platen speed used in the explicit run (mm/s). The test was quasi-static (0.05 mm/s);
    /// the solver run is sped up and the kinetic/internal energy ratio is checked.
    pub platen_speed_mm_s: f64,
    /// Time to ramp the platen speed from 0 (s).
    pub ramp_time_s: f64,
    /// Total platen travel (mm).
    pub crush_distance_mm: f64,
    pub top_boundary: TopBoundary,
    /// Coulomb friction for self contact and the friction wall.
    pub friction: f64,
    /// Shell through-thickness integration points.
    pub integration_points: u32,
    /// Time-history sampling interval (s).
    pub th_dt_s: f64,
    /// Number of animation frames written over the run.
    pub anim_frames: u32,
    /// SMP threads for the engine.
    pub threads: u32,
    /// Floor for the nodal time step as a fraction of h_min/c (0 disables mass scaling).
    pub dt_floor_fraction: f64,
}

impl TubeCrush {
    /// Mid-surface section width a = b - t (sharp-corner idealisation).
    pub fn midline_width(&self) -> f64 {
        self.breadth_mm - self.thickness_mm
    }
    /// Yield stress = first point of the hardening curve.
    pub fn yield_mpa(&self) -> f64 {
        self.material.hardening[0].1
    }
    /// beta = (b/t) * sqrt(sigma_y / E)  (Park et al. 2022, Eq. 1).
    pub fn beta(&self) -> f64 {
        (self.breadth_mm / self.thickness_mm) * (self.yield_mpa() / self.material.youngs_mpa).sqrt()
    }
    /// w0 = amp * beta^2 * t (mm).
    pub fn imperfection_w0(&self) -> f64 {
        self.imperfection_amp * self.beta().powi(2) * self.thickness_mm
    }
    pub fn end_time_s(&self) -> f64 {
        // travel = v * (t_end - ramp/2) for a linear ramp
        self.crush_distance_mm / self.platen_speed_mm_s + 0.5 * self.ramp_time_s
    }
    pub fn validate(&self) -> anyhow::Result<()> {
        anyhow::ensure!(self.breadth_mm > 2.0 * self.thickness_mm, "breadth must exceed 2t");
        anyhow::ensure!(self.element_size_mm > 0.0, "element size must be positive");
        anyhow::ensure!(self.crush_distance_mm < self.length_mm, "crush distance must be < length");
        anyhow::ensure!(!self.material.hardening.is_empty(), "hardening curve empty");
        anyhow::ensure!(self.material.hardening[0].0 == 0.0, "hardening must start at plastic strain 0");
        for w in self.material.hardening.windows(2) {
            anyhow::ensure!(w[1].0 > w[0].0, "hardening strains must increase");
        }
        anyhow::ensure!(self.platen_speed_mm_s > 0.0 && self.ramp_time_s >= 0.0, "bad loading");
        Ok(())
    }
}

/// ASTM A500 Grade A tube, specimen US-2, from Park, Cho & Kim (2022) Table 2.
/// Table 2 gives E = 205.8 GPa, sigma_y(0.2%) = 310.8 MPa, sigma_T = 363.3 MPa, eps_T = 0.177.
/// sigma_T/eps_T are taken as engineering tensile strength and uniform strain (a true-stress
/// reading would put the tensile strength below the yield stress). Conversion to true stress
/// and plastic strain is done here (our derivation, not the authors'): sigma_true = s(1+e),
/// eps_p = ln(1+e) - sigma_true/E. The stress is held constant beyond the last point,
/// as in the authors' multi-linear model (Section 3.6).
pub fn a500_us2_multilinear() -> Material {
    let e = 205_800.0;
    let s_u = 363.3_f64;
    let e_u = 0.177_f64;
    let sig_true = s_u * (1.0 + e_u);
    let eps_p = (1.0 + e_u).ln() - sig_true / e;
    Material {
        name: "ASTM A500 Gr.A (US-2), multi-linear true stress".into(),
        source: "Park, Cho & Kim (2022) Materials 15:2107 Table 2, doi:10.3390/ma15062107 (CC BY 4.0); engineering->true conversion by Forge".into(),
        density_t_per_mm3: 7.85e-9, // nominal carbon steel density; not given in the paper
        youngs_mpa: e,
        poisson: 0.3, // Park et al. 2022 Table 3
        hardening: vec![(0.0, 310.8), (eps_p, sig_true), (1.0, sig_true)],
    }
}

/// Perfectly plastic variant (the material model the authors finally selected, Table 11).
pub fn a500_us2_perfectly_plastic() -> Material {
    let mut m = a500_us2_multilinear();
    m.name = "ASTM A500 Gr.A (US-2), perfectly plastic".into();
    m.source = "Park, Cho & Kim (2022) Materials 15:2107 Tables 2 and 11, doi:10.3390/ma15062107 (CC BY 4.0)".into();
    m.hardening = vec![(0.0, 310.8), (1.0, 310.8)];
    m
}

/// Baseline P1a case: specimen US-2 (b = 100 mm, t = 2.8 mm, L = 450 mm).
pub fn p1a_us2_baseline(element_size_mm: f64) -> TubeCrush {
    TubeCrush {
        case_id: format!("p1a_us2_h{}", element_size_mm),
        breadth_mm: 100.0,
        thickness_mm: 2.8,
        length_mm: 450.0,
        element_size_mm,
        imperfection_amp: 0.10, // Park et al. 2022 Table 11
        imperfection_half_waves: 5,
        material: a500_us2_multilinear(),
        platen_speed_mm_s: 2000.0,
        ramp_time_s: 0.005,
        crush_distance_mm: 350.0,
        top_boundary: TopBoundary::TiedWall,
        friction: 0.08, // Park et al. 2022 Table 11
        integration_points: 5,
        th_dt_s: 5.0e-5,
        anim_frames: 8,
        threads: 4,
        dt_floor_fraction: 0.5,
    }
}
