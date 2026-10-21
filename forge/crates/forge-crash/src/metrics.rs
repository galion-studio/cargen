// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! Crush metrics on a force-displacement curve. The same functions are applied to the
//! simulated and to the digitized experimental curve, so both are measured the same way.

use serde::{Deserialize, Serialize};

/// Curve sampled on a uniform displacement grid.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Curve {
    pub disp_mm: Vec<f64>,
    pub force_kn: Vec<f64>,
}

impl Curve {
    /// Resample (x, y) pairs onto 0, dx, 2dx, ... <= x_max by linear interpolation.
    /// Input x must be non-decreasing; duplicates are tolerated.
    pub fn resample(x: &[f64], y: &[f64], dx: f64, x_max: f64) -> Curve {
        let n = (x_max / dx).floor() as usize + 1;
        let mut out_x = Vec::with_capacity(n);
        let mut out_y = Vec::with_capacity(n);
        let mut j = 0;
        for i in 0..n {
            let xi = i as f64 * dx;
            while j + 1 < x.len() && x[j + 1] < xi {
                j += 1;
            }
            let yi = if xi <= x[0] {
                y[0]
            } else if j + 1 >= x.len() {
                *y.last().unwrap()
            } else {
                let (x0, x1) = (x[j], x[j + 1]);
                if x1 > x0 { y[j] + (y[j + 1] - y[j]) * (xi - x0) / (x1 - x0) } else { y[j] }
            };
            out_x.push(xi);
            out_y.push(yi);
        }
        Curve { disp_mm: out_x, force_kn: out_y }
    }
    pub fn dx(&self) -> f64 {
        self.disp_mm[1] - self.disp_mm[0]
    }
    /// Energy absorbed up to `d` (kN*mm = J), trapezoidal rule.
    pub fn energy_j(&self, d: f64) -> f64 {
        let mut e = 0.0;
        for i in 1..self.disp_mm.len() {
            if self.disp_mm[i] > d + 1e-9 {
                break;
            }
            e += 0.5 * (self.force_kn[i] + self.force_kn[i - 1]) * (self.disp_mm[i] - self.disp_mm[i - 1]);
        }
        e
    }
    /// Mean crush force over [0, d]: absorbed energy / d (kN), the definition used by
    /// Park et al. (2022), Section 2.
    pub fn mean_force_kn(&self, d: f64) -> f64 {
        self.energy_j(d) / d
    }
    /// Maximum force within [0, d] (kN) and where it occurs.
    pub fn peak_kn(&self, d: f64) -> (f64, f64) {
        let mut best = (0.0, 0.0);
        for (x, f) in self.disp_mm.iter().zip(&self.force_kn) {
            if *x <= d && *f > best.0 {
                best = (*f, *x);
            }
        }
        best
    }
    pub fn moving_average(&self, window_mm: f64) -> Curve {
        let half = ((window_mm / self.dx()) / 2.0).round() as usize;
        let n = self.force_kn.len();
        let f = (0..n)
            .map(|i| {
                let a = i.saturating_sub(half);
                let b = (i + half).min(n - 1);
                self.force_kn[a..=b].iter().sum::<f64>() / (b - a + 1) as f64
            })
            .collect();
        Curve { disp_mm: self.disp_mm.clone(), force_kn: f }
    }
}

/// Local force maxima ("lobe peaks") in [0, d]. A maximum counts when it rises at least
/// `prominence_kn` above the lowest point between it and the previous counted peak and
/// is at least `min_sep_mm` away from it. The curve is first smoothed over `smooth_mm`.
pub fn lobe_peaks(c: &Curve, d: f64, smooth_mm: f64, prominence_kn: f64, min_sep_mm: f64) -> Vec<(f64, f64)> {
    let s = c.moving_average(smooth_mm);
    let n = s.force_kn.iter().zip(&s.disp_mm).take_while(|(_, x)| **x <= d).count();
    let f = &s.force_kn[..n];
    let x = &s.disp_mm[..n];
    let mut peaks: Vec<(f64, f64)> = Vec::new();
    // valley tracking: candidate peak must rise `prominence` above the valley since the
    // last accepted peak, and the curve must then drop `prominence` below it.
    let mut valley = f64::INFINITY;
    let mut cand: Option<(f64, f64)> = None;
    for i in 0..n {
        let fi = f[i];
        match cand {
            None => {
                valley = valley.min(fi);
                if fi - valley >= prominence_kn || (peaks.is_empty() && i == 0) {
                    cand = Some((x[i], fi));
                }
            }
            Some((cx, cf)) => {
                if fi > cf {
                    cand = Some((x[i], fi));
                } else if cf - fi >= prominence_kn {
                    let ok = peaks.last().map_or(true, |p| cx - p.0 >= min_sep_mm);
                    if ok {
                        peaks.push((cx, cf));
                    }
                    cand = None;
                    valley = fi;
                }
            }
        }
    }
    peaks
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn mean_of_constant() {
        let c = Curve { disp_mm: (0..=100).map(|i| i as f64).collect(), force_kn: vec![50.0; 101] };
        assert!((c.mean_force_kn(80.0) - 50.0).abs() < 1e-12);
        assert_eq!(c.peak_kn(100.0).0, 50.0);
    }
    #[test]
    fn resample_linear() {
        let c = Curve::resample(&[0.0, 10.0], &[0.0, 100.0], 2.5, 10.0);
        assert_eq!(c.force_kn, vec![0.0, 25.0, 50.0, 75.0, 100.0]);
    }
    #[test]
    fn counts_sine_peaks() {
        // 5 full periods of a sine on top of 100 kN -> 5 peaks
        let x: Vec<f64> = (0..=1000).map(|i| i as f64 * 0.5).collect();
        let f: Vec<f64> = x.iter().map(|x| 100.0 + 40.0 * (2.0 * std::f64::consts::PI * (x - 25.0) / 100.0).sin()).collect();
        let c = Curve { disp_mm: x, force_kn: f };
        let p = lobe_peaks(&c, 500.0, 2.0, 15.0, 20.0);
        assert_eq!(p.len(), 5, "{p:?}");
        assert!((p[0].0 - 50.0).abs() < 1.0);
    }
}
