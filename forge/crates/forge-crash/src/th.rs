// SPDX-License-Identifier: MIT
// Copyright (c) 3000 Galion / galion-studio
//! Parse the CSV written by OpenCourant's `th_to_csv` for the P1a deck.
//! Rigid-wall forces are stored by the solver as impulses (N*s); the force is their
//! time derivative.

use anyhow::{anyhow, Context, Result};
use std::path::Path;

#[derive(Debug, Clone, Default)]
pub struct TimeHistory {
    pub time_s: Vec<f64>,
    /// Platen travel (mm, positive = crushing).
    pub disp_mm: Vec<f64>,
    /// Platen normal force (N, positive = compressive).
    pub force_n: Vec<f64>,
    pub tube_internal_mj: Vec<f64>,
    pub tube_kinetic_mj: Vec<f64>,
    pub tube_hourglass_mj: Vec<f64>,
    pub added_mass_pct: Vec<f64>,
}

fn col(header: &[String], pred: impl Fn(&str) -> bool, what: &str) -> Result<usize> {
    header.iter().position(|h| pred(h.trim())).ok_or_else(|| anyhow!("column {what} not found"))
}

pub fn parse_csv_str(text: &str) -> Result<TimeHistory> {
    let mut lines = text.lines();
    let header: Vec<String> = lines
        .next()
        .ok_or_else(|| anyhow!("empty csv"))?
        .split(',')
        .map(|s| s.trim().trim_matches('"').to_string())
        .collect();
    let i_t = col(&header, |h| h == "time", "time")?;
    let i_ie = col(&header, |h| h.starts_with("tube") && h.ends_with(" IE"), "tube IE")?;
    let i_ke = col(&header, |h| h.starts_with("tube") && h.ends_with(" KE"), "tube KE")?;
    let i_he = col(&header, |h| h.starts_with("tube") && h.ends_with(" HE"), "tube HE")?;
    let i_am = col(&header, |h| h == "PERCENTAGE ADDED MASS", "added mass")?;
    // platen force block: 6 vars (FNX FNY FNZ FTX FTY FTZ impulses); FNZ is the 3rd
    let i_f0 = col(&header, |h| h.starts_with("platen force"), "platen force")?;
    // platen node block: DX DY DZ VX VY VZ; DZ is the 3rd
    let i_n0 = col(&header, |h| h.starts_with("platen node"), "platen node")?;
    let (i_fnz, i_dz) = (i_f0 + 2, i_n0 + 2);
    let mut th = TimeHistory::default();
    let mut impulse = Vec::new();
    for (k, l) in lines.enumerate() {
        if l.trim().is_empty() {
            continue;
        }
        let v: Vec<f64> = l
            .split(',')
            .map(|s| s.trim().parse::<f64>())
            .collect::<std::result::Result<_, _>>()
            .with_context(|| format!("bad number in csv row {}", k + 2))?;
        th.time_s.push(v[i_t]);
        th.disp_mm.push(-v[i_dz]);
        impulse.push(v[i_fnz]);
        th.tube_internal_mj.push(v[i_ie]);
        th.tube_kinetic_mj.push(v[i_ke]);
        th.tube_hourglass_mj.push(v[i_he]);
        th.added_mass_pct.push(v[i_am]);
    }
    th.force_n = derivative(&th.time_s, &impulse).into_iter().map(|f| f.abs()).collect();
    Ok(th)
}

pub fn parse_csv(path: &Path) -> Result<TimeHistory> {
    let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
    parse_csv_str(&text)
}

/// Central differences (one-sided at the ends).
pub fn derivative(x: &[f64], y: &[f64]) -> Vec<f64> {
    let n = x.len();
    if n < 2 {
        return vec![0.0; n];
    }
    (0..n)
        .map(|i| {
            let (a, b) = if i == 0 { (0, 1) } else if i == n - 1 { (n - 2, n - 1) } else { (i - 1, i + 1) };
            (y[b] - y[a]) / (x[b] - x[a])
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn derivative_of_line() {
        let x = [0.0, 1.0, 2.0, 3.0];
        let y = [0.0, 2.0, 4.0, 6.0];
        assert_eq!(derivative(&x, &y), vec![2.0; 4]);
    }
    #[test]
    fn parses_minimal_csv() {
        let csv = "\"time\",\"PERCENTAGE ADDED MASS\",\"tube   IE \",\"tube   KE \",\"tube   HE \",\"platen force 1 var 33\",\"platen force var 34\",\"platen force var 35\",\"x\",\"x\",\"x\",\"platen node 1 var 39\",\"y\",\"y\"\n\
0.0,0,0,0,0,0,0,0.0,0,0,0,0,0,0.0\n\
1.0,0,5,1,0,0,0,-10.0,0,0,0,0,0,-2.0\n\
2.0,0,9,1,0,0,0,-20.0,0,0,0,0,0,-4.0\n";
        let th = parse_csv_str(csv).unwrap();
        assert_eq!(th.disp_mm, vec![0.0, 2.0, 4.0]);
        assert_eq!(th.force_n, vec![10.0, 10.0, 10.0]);
        assert_eq!(th.tube_internal_mj[2], 9.0);
    }
}
