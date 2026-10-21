// SPDX-License-Identifier: MIT
// Copyright (c) 3000 Galion / galion-studio
//! Reference experiments (measured values with their sources).

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
    /// Measured peak force (kN) and where it is reported.
    pub peak_kn: f64,
    pub peak_source: String,
    /// Measured mean crushing force (kN).
    pub mean_kn: f64,
    pub mean_source: String,
    /// Window [0, crush_length] used for the mean force (mm).
    pub crush_length_mm: f64,
    pub crush_length_source: String,
    /// Measured fold (lobe) count, when available.
    #[serde(default)]
    pub fold_count: Option<f64>,
    #[serde(default)]
    pub fold_source: String,
    /// Digitized measured curve (displacement_mm, force_kN), when available.
    #[serde(default)]
    pub digitized_csv: Option<String>,
}

const PARK: &str = "Park Y.I., Cho J.-S., Kim J.-H. (2022). Numerical and Experimental Investigation of Quasi-Static Crushing Behaviors of Steel Tubular Structures. Materials 15(6), 2107. Test data from Jung J.Y. (1997), PhD thesis, Pusan National University.";

/// Park et al. (2022) unstiffened specimens. Peak/mean: Table 4. Crush length: Fig. 29
/// (read by Forge from the bar chart, about ±3 mm), except US-2 where point E of Fig. 3 is used.
pub fn park2022(spec: &str, digitized_csv: Option<&str>) -> Option<Reference> {
    let (b, t, pu, pm, dc) = match spec {
        "US-1" => (100.0, 2.2, 231.3, 60.6, 344.0),
        "US-2" => (100.0, 2.8, 337.1, 101.0, 343.0),
        "US-3" => (100.0, 3.0, 361.6, 106.2, 346.0),
        "US-4" => (100.0, 4.2, 626.0, 271.6, 327.0),
        "US-5" => (75.0, 2.1, 193.1, 59.0, 342.0),
        "US-6" => (75.0, 3.2, 404.7, 148.4, 326.0),
        _ => return None,
    };
    Some(Reference {
        citation: PARK.into(),
        doi: "10.3390/ma15062107".into(),
        licence: "CC BY 4.0".into(),
        specimen: format!("{spec}: ASTM A500 Gr.A square tube, b = {b} mm, t = {t} mm, L = 450 mm, quasi-static 0.05 mm/s"),
        peak_kn: pu,
        peak_source: "Park et al. 2022 Table 4 (P_u)".into(),
        mean_kn: pm,
        mean_source: "Park et al. 2022 Table 4 (P_m)".into(),
        crush_length_mm: dc,
        crush_length_source: if spec == "US-2" { "Fig. 3 point E (digitized)".into() } else { "Fig. 29 bar chart (read by Forge, ±3 mm)".into() },
        fold_count: None,
        fold_source: if digitized_csv.is_some() { "Forge count of force peaks in the digitized curve (not stated by the authors)".into() } else { "not available (curve not digitized)".into() },
        digitized_csv: digitized_csv.map(String::from),
    })
}

/// Lykakos, Kostazos, Venetsanos, Manolakos (2021), aluminium (AL) circular tubes,
/// AA6063-F annealed, D_out 38.6 / D_in 35.6 mm, L = 100 mm. Values: Table 2, mean of the
/// two specimens per loading condition. Fold count for the dynamic tests: Section 5.2.2
/// ("five groups ... coincide with the number of the internal/external lobes").
pub fn lykakos2021(dynamic: bool) -> Reference {
    let base = Reference {
        citation: "Lykakos S.S.A., Kostazos P.K., Venetsanos O.-V., Manolakos D.E. (2021). Crashworthiness Performance of Aluminium, GFRP and Hybrid Aluminium/GFRP Circular Tubes under Quasi-Static and Dynamic Axial Loading Conditions: A Comparative Experimental Study. Dynamics 1(1), 22-48.".into(),
        doi: "10.3390/dynamics1010004".into(),
        licence: "CC BY 4.0".into(),
        specimen: String::new(),
        peak_kn: 0.0,
        peak_source: String::new(),
        mean_kn: 0.0,
        mean_source: String::new(),
        crush_length_mm: 0.0,
        crush_length_source: String::new(),
        fold_count: None,
        fold_source: String::new(),
        digitized_csv: None,
    };
    if dynamic {
        Reference {
            specimen: "AL 401/402: AA6063-F (annealed) circular tube 38.6x1.5 mm, L = 100 mm, 78 kg drop hammer from 2.5 m (7.0 m/s)".into(),
            peak_kn: 0.5 * (49.5 + 48.0),
            peak_source: "Table 2 F_max, mean of AL 401/402 (IPF 25.5/25.9 kN)".into(),
            mean_kn: 0.5 * (23.1 + 22.8),
            mean_source: "Table 2 MCF, mean of AL 401/402".into(),
            crush_length_mm: 0.5 * (65.5 + 70.5),
            crush_length_source: "Table 2 delta_T, mean of AL 401/402 (measured final crush)".into(),
            fold_count: Some(5.0),
            fold_source: "Section 5.2.2: five force-peak groups coinciding with the internal/external lobes".into(),
            ..base
        }
    } else {
        Reference {
            specimen: "AL 403/404: AA6063-F (annealed) circular tube 38.6x1.5 mm, L = 100 mm, quasi-static 10 mm/min".into(),
            peak_kn: 0.5 * (43.8 + 44.1),
            peak_source: "Table 2 IPF = F_max, mean of AL 403/404".into(),
            mean_kn: 0.5 * (24.9 + 24.1),
            mean_source: "Table 2 MCF, mean of AL 403/404".into(),
            crush_length_mm: 60.0,
            crush_length_source: "Table 2 delta_T (prescribed)".into(),
            fold_count: None,
            fold_source: "not stated numerically in the text".into(),
            ..base
        }
    }
}

/// Abramowicz & Jones (1986) type E square mild-steel tubes. Values as transcribed in
/// research/crush-experiments.md / data/crush-experiments.csv (Tables 1, 3, 5b of the paper;
/// paywalled, facts cited, not copied). No peak force or fold count reported there.
pub fn aj1986_e(spec: &str) -> Option<Reference> {
    let (desc, pm, dc, dsrc) = match spec {
        "E10" => ("E10: c = 36.45 mm, h = 1.63 mm, L = 221.9 mm, quasi-static", 35.55, 150.0, "NOT reported in our transcription; Forge window 150 mm (assumption)"),
        "E3" => ("E3: c = 36.49 mm, h = 1.63 mm, L = 222.1 mm, drop hammer 135.5 kg at 9.62 m/s", 44.61, 144.8, "Table 1 final crush delta_f (measured)"),
        _ => return None,
    };
    Some(Reference {
        citation: "Abramowicz W., Jones N. (1986). Dynamic progressive buckling of circular and square tubes. Int. J. Impact Engineering 4(4), 243-270.".into(),
        doi: "10.1016/0734-743X(86)90017-5".into(),
        licence: "paywalled (Elsevier); numeric facts cited, tables not reproduced".into(),
        specimen: format!("{desc}; steel type E, sigma_y = 272.7 MPa, sigma_u = 315.6 MPa"),
        peak_kn: f64::NAN,
        peak_source: "not reported".into(),
        mean_kn: pm,
        mean_source: "Table 5b mean force (via data/crush-experiments.csv)".into(),
        crush_length_mm: dc,
        crush_length_source: dsrc.into(),
        fold_count: None,
        fold_source: "not reported".into(),
        digitized_csv: None,
    })
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
