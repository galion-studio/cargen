// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! The reference experiment: Park, Cho & Kim (2022), specimen US-2.

use crate::metrics::Curve;
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Reference {
    pub citation: String,
    pub doi: String,
    pub licence: String,
    pub specimen: String,
    /// Reported ultimate (peak) force, Table 4 (kN).
    pub peak_kn: f64,
    /// Reported mean crushing force, Table 4 (kN).
    pub mean_kn: f64,
    /// Crush length used for P_m: end of folding read at point E in Fig. 3 (mm), digitized.
    pub crush_length_mm: f64,
    pub digitized_csv: String,
}

pub fn park2022_us2(digitized_csv: &str) -> Reference {
    Reference {
        citation: "Park Y.I., Cho J.-S., Kim J.-H. (2022). Numerical and Experimental Investigation of Quasi-Static Crushing Behaviors of Steel Tubular Structures. Materials 15(6), 2107. Test data from Jung J.Y. (1997), PhD thesis, Pusan National University.".into(),
        doi: "10.3390/ma15062107".into(),
        licence: "CC BY 4.0".into(),
        specimen: "US-2: ASTM A500 Gr.A square tube, b = 100 mm, t = 2.8 mm, L = 450 mm, quasi-static 0.05 mm/s".into(),
        peak_kn: 337.1,
        mean_kn: 101.0,
        crush_length_mm: 343.0,
        digitized_csv: digitized_csv.into(),
    }
}

/// Read a `displacement_mm,force_kN` CSV (lines starting with '#' are comments).
pub fn read_curve(path: &Path) -> Result<Curve> {
    let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
    let mut x = Vec::new();
    let mut y = Vec::new();
    for l in text.lines() {
        let l = l.trim();
        if l.is_empty() || l.starts_with('#') || l.starts_with("displacement") {
            continue;
        }
        let mut it = l.split(',');
        x.push(it.next().unwrap_or("").trim().parse::<f64>()?);
        y.push(it.next().unwrap_or("").trim().parse::<f64>()?);
    }
    Ok(Curve { disp_mm: x, force_kn: y })
}
