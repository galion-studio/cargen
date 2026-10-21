// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! Curve correlation after ISO/TS 18571:2014 (corridor, phase, magnitude, slope;
//! weights 0.4/0.2/0.2/0.2). Implemented by Forge from the published method description;
//! it has NOT been checked against the ISO reference implementation, so scores are
//! indicative. ISO/TS 18571 is written for time signals; here it is applied to force vs
//! displacement on a uniform displacement grid, which is a Forge adaptation.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct IsoParams {
    pub a0: f64,
    pub b0: f64,
    pub kz: f64,
    pub eps_p: f64,
    pub kp: f64,
    pub eps_m: f64,
    pub km: f64,
    pub eps_s: f64,
    pub ks: f64,
}

impl Default for IsoParams {
    fn default() -> Self {
        Self { a0: 0.05, b0: 0.5, kz: 2.0, eps_p: 0.2, kp: 1.0, eps_m: 0.5, km: 1.0, eps_s: 2.0, ks: 1.0 }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IsoScore {
    pub corridor: f64,
    pub phase: f64,
    pub magnitude: f64,
    pub slope: f64,
    pub overall: f64,
    pub rating: String,
    pub shift_samples: i64,
}

pub fn rating(r: f64) -> &'static str {
    if r > 0.94 {
        "excellent"
    } else if r > 0.80 {
        "good"
    } else if r > 0.58 {
        "fair"
    } else {
        "poor"
    }
}

fn clamp01(x: f64) -> f64 {
    x.clamp(0.0, 1.0)
}

pub fn corridor(t: &[f64], c: &[f64], p: &IsoParams) -> f64 {
    let tmax = t.iter().fold(0.0_f64, |m, v| m.max(v.abs()));
    let (di, d_o) = (p.a0 * tmax, p.b0 * tmax);
    let s: f64 = t
        .iter()
        .zip(c)
        .map(|(t, c)| {
            let e = (c - t).abs();
            if e <= di {
                1.0
            } else if e >= d_o {
                0.0
            } else {
                ((d_o - e) / (d_o - di)).powf(p.kz)
            }
        })
        .sum();
    s / t.len() as f64
}

fn pearson(a: &[f64], b: &[f64]) -> f64 {
    let n = a.len() as f64;
    let ma = a.iter().sum::<f64>() / n;
    let mb = b.iter().sum::<f64>() / n;
    let (mut sab, mut saa, mut sbb) = (0.0, 0.0, 0.0);
    for (x, y) in a.iter().zip(b) {
        sab += (x - ma) * (y - mb);
        saa += (x - ma).powi(2);
        sbb += (y - mb).powi(2);
    }
    if saa == 0.0 || sbb == 0.0 { 0.0 } else { sab / (saa * sbb).sqrt() }
}

/// Overlapping parts of t and c when c is shifted by `k` samples (positive: c lags).
fn shifted<'a>(t: &'a [f64], c: &'a [f64], k: i64) -> (&'a [f64], &'a [f64]) {
    let n = t.len();
    let k_abs = k.unsigned_abs() as usize;
    if k >= 0 { (&t[..n - k_abs], &c[k_abs..]) } else { (&t[k_abs..], &c[..n - k_abs]) }
}

/// Fraction of the curve length that dynamic time warping may move a sample (Sakoe-Chiba
/// band). Forge choice: warping is only meant to remove residual phase error; an
/// unconstrained warp can hide magnitude errors.
pub const DTW_BAND_FRACTION: f64 = 0.02;

/// Banded dynamic time warping alignment; returns the warped pair.
fn dtw(a: &[f64], b: &[f64]) -> (Vec<f64>, Vec<f64>) {
    let band = ((DTW_BAND_FRACTION * a.len().max(b.len()) as f64).ceil() as usize).max(1);
    let (n, m) = (a.len(), b.len());
    let inf = f64::INFINITY;
    let mut d = vec![inf; (n + 1) * (m + 1)];
    let idx = |i: usize, j: usize| i * (m + 1) + j;
    d[0] = 0.0;
    for i in 1..=n {
        let lo = i.saturating_sub(band).max(1);
        let hi = (i + band).min(m);
        for j in lo..=hi {
            let cost = (a[i - 1] - b[j - 1]).powi(2);
            let best = d[idx(i - 1, j)].min(d[idx(i, j - 1)]).min(d[idx(i - 1, j - 1)]);
            d[idx(i, j)] = cost + best;
        }
    }
    let (mut i, mut j) = (n, m);
    let (mut wa, mut wb) = (Vec::new(), Vec::new());
    while i > 0 && j > 0 {
        wa.push(a[i - 1]);
        wb.push(b[j - 1]);
        let diag = d[idx(i - 1, j - 1)];
        let up = d[idx(i - 1, j)];
        let left = d[idx(i, j - 1)];
        if diag <= up && diag <= left {
            i -= 1;
            j -= 1;
        } else if up <= left {
            i -= 1;
        } else {
            j -= 1;
        }
    }
    wa.reverse();
    wb.reverse();
    (wa, wb)
}

fn smoothed_slope(y: &[f64], dx: f64) -> Vec<f64> {
    let d: Vec<f64> = y.windows(2).map(|w| (w[1] - w[0]) / dx).collect();
    let n = d.len();
    (0..n)
        .map(|i| {
            let a = i.saturating_sub(4);
            let b = (i + 4).min(n - 1);
            d[a..=b].iter().sum::<f64>() / (b - a + 1) as f64
        })
        .collect()
}

/// Score candidate `c` against reference `t`; both on the same uniform grid with step `dx`.
pub fn score(t: &[f64], c: &[f64], dx: f64, p: &IsoParams) -> IsoScore {
    assert_eq!(t.len(), c.len(), "curves must share the grid");
    let n = t.len();
    let z = corridor(t, c, p);
    // phase: search shifts up to eps_p * n
    let kmax = (p.eps_p * n as f64).floor() as i64;
    let mut best = (0_i64, f64::NEG_INFINITY);
    for k in -kmax..=kmax {
        let (a, b) = shifted(t, c, k);
        let r = pearson(a, b);
        if r > best.1 + 1e-12 || ((r - best.1).abs() <= 1e-12 && k.abs() < best.0.abs()) {
            best = (k, r);
        }
    }
    let k = best.0;
    let phase = if kmax == 0 { 1.0 } else { clamp01(((kmax - k.abs()) as f64 / kmax as f64).powf(p.kp)) };
    let (ts, cs) = shifted(t, c, k);
    // magnitude on DTW-warped shifted curves
    let (wt, wc) = dtw(ts, cs);
    let num: f64 = wt.iter().zip(&wc).map(|(a, b)| (b - a).abs()).sum();
    let den: f64 = wt.iter().map(|a| a.abs()).sum();
    let e_mag = if den > 0.0 { num / den } else { 0.0 };
    let magnitude = clamp01(((p.eps_m - e_mag) / p.eps_m).powf(p.km));
    // slope on shifted curves
    let st = smoothed_slope(ts, dx);
    let sc = smoothed_slope(cs, dx);
    let num: f64 = st.iter().zip(&sc).map(|(a, b)| (b - a).abs()).sum();
    let den: f64 = st.iter().map(|a| a.abs()).sum();
    let e_s = if den > 0.0 { num / den } else { 0.0 };
    let slope = clamp01(((p.eps_s - e_s) / p.eps_s).powf(p.ks));
    let overall = 0.4 * z + 0.2 * phase + 0.2 * magnitude + 0.2 * slope;
    IsoScore { corridor: z, phase, magnitude, slope, overall, rating: rating(overall).into(), shift_samples: k }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn sine(n: usize, shift: f64) -> Vec<f64> {
        (0..n).map(|i| 100.0 + 50.0 * ((i as f64 - shift) * 0.05).sin()).collect()
    }
    #[test]
    fn identical_curves_score_one() {
        let t = sine(300, 0.0);
        let s = score(&t, &t, 1.0, &IsoParams::default());
        assert!((s.overall - 1.0).abs() < 1e-9, "{s:?}");
        assert_eq!(s.rating, "excellent");
    }
    #[test]
    fn shift_lowers_phase_and_is_detected() {
        let t = sine(300, 0.0);
        let c = sine(300, 10.0);
        let s = score(&t, &c, 1.0, &IsoParams::default());
        assert_eq!(s.shift_samples, 10);
        assert!(s.phase < 1.0 && s.phase > 0.7);
        assert!(s.magnitude > 0.95);
    }
    #[test]
    fn scaled_curve_lowers_magnitude() {
        let t = sine(300, 0.0);
        let c: Vec<f64> = t.iter().map(|v| v * 1.3).collect();
        let s = score(&t, &c, 1.0, &IsoParams::default());
        assert!(s.magnitude < 0.7, "{s:?}");
        assert!(s.overall < 0.9);
    }
}
