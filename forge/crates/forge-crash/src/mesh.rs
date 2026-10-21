// SPDX-License-Identifier: MIT
// Copyright (c) 3000 Galion / galion-studio
//! Structured quad shell mesh of a square tube mid-surface (sharp corners), with a
//! local-buckling-shaped geometric imperfection.

use crate::params::TubeCrush;
use std::f64::consts::PI;

#[derive(Debug, Clone)]
pub struct Mesh {
    /// (id, x, y, z)
    pub nodes: Vec<(u32, [f64; 3])>,
    /// (id, [n1, n2, n3, n4])
    pub quads: Vec<(u32, [u32; 4])>,
    pub bottom_nodes: Vec<u32>,
    pub top_nodes: Vec<u32>,
    pub per_side: usize,
    pub n_axial: usize,
    pub actual_size_mm: (f64, f64),
}

pub const FIRST_NODE_ID: u32 = 101;
pub const FIRST_ELEM_ID: u32 = 1001;

/// Imperfection shape: adjacent faces buckle in opposite directions (the classic first
/// local mode of a square tube), sinusoidal across each face (zero at the corners) and
/// along the length (zero at both ends). It approximates, but is not, the eigenmode the
/// authors computed with ABAQUS.
pub fn imperfection(face: usize, u: f64, z: f64, length: f64, half_waves: u32, w0: f64) -> f64 {
    let sign = if face % 2 == 0 { 1.0 } else { -1.0 };
    sign * w0 * (PI * u).sin() * (half_waves as f64 * PI * z / length).sin()
}

pub fn build(p: &TubeCrush) -> Mesh {
    if p.section == crate::params::Section::Circular {
        return build_circular(p);
    }
    let a = p.midline_width();
    let c = 0.5 * a;
    let per_side = ((a / p.element_size_mm).round() as usize).max(2);
    let n_axial = ((p.length_mm / p.element_size_mm).round() as usize).max(2);
    let ring = 4 * per_side;
    let w0 = p.imperfection_w0();
    let mut nodes = Vec::with_capacity(ring * (n_axial + 1));
    let id = |k: usize, i: usize| FIRST_NODE_ID + (k * ring + i) as u32;
    for k in 0..=n_axial {
        let z = p.length_mm * k as f64 / n_axial as f64;
        for i in 0..ring {
            let face = i / per_side;
            let u = (i % per_side) as f64 / per_side as f64;
            let s = -c + a * u;
            // base point and outward normal per face (counter-clockwise seen from +z)
            let (x, y, nx, ny) = match face {
                0 => (s, -c, 0.0, -1.0),
                1 => (c, s, 1.0, 0.0),
                2 => (-s, c, 0.0, 1.0),
                _ => (-c, -s, -1.0, 0.0),
            };
            let w = imperfection(face, u, z, p.length_mm, p.imperfection_half_waves, w0);
            nodes.push((id(k, i), [x + w * nx, y + w * ny, z]));
        }
    }
    let mut quads = Vec::with_capacity(ring * n_axial);
    let mut eid = FIRST_ELEM_ID;
    for k in 0..n_axial {
        for i in 0..ring {
            let i2 = (i + 1) % ring;
            quads.push((eid, [id(k, i), id(k, i2), id(k + 1, i2), id(k + 1, i)]));
            eid += 1;
        }
    }
    Mesh {
        bottom_nodes: (0..ring).map(|i| id(0, i)).collect(),
        top_nodes: (0..ring).map(|i| id(n_axial, i)).collect(),
        nodes,
        quads,
        per_side,
        n_axial,
        actual_size_mm: (a / per_side as f64, p.length_mm / n_axial as f64),
    }
}

/// Circular tube: `ring` nodes around, imperfection w = w0 cos(k theta) sin(m pi z / L).
pub fn build_circular(p: &TubeCrush) -> Mesh {
    let r = 0.5 * p.midline_width();
    let ring = ((p.midline_perimeter() / p.element_size_mm).round() as usize).max(8);
    let n_axial = ((p.length_mm / p.element_size_mm).round() as usize).max(2);
    let w0 = p.imperfection_w0();
    let id = |k: usize, i: usize| FIRST_NODE_ID + (k * ring + i) as u32;
    let mut nodes = Vec::with_capacity(ring * (n_axial + 1));
    for k in 0..=n_axial {
        let z = p.length_mm * k as f64 / n_axial as f64;
        for i in 0..ring {
            let th = 2.0 * PI * i as f64 / ring as f64;
            let w = w0 * (p.circ_waves as f64 * th).cos() * (p.imperfection_half_waves as f64 * PI * z / p.length_mm).sin();
            nodes.push((id(k, i), [(r + w) * th.cos(), (r + w) * th.sin(), z]));
        }
    }
    let mut quads = Vec::with_capacity(ring * n_axial);
    let mut eid = FIRST_ELEM_ID;
    for k in 0..n_axial {
        for i in 0..ring {
            let i2 = (i + 1) % ring;
            quads.push((eid, [id(k, i), id(k, i2), id(k + 1, i2), id(k + 1, i)]));
            eid += 1;
        }
    }
    Mesh {
        bottom_nodes: (0..ring).map(|i| id(0, i)).collect(),
        top_nodes: (0..ring).map(|i| id(n_axial, i)).collect(),
        nodes,
        quads,
        per_side: ring / 4,
        n_axial,
        actual_size_mm: (p.midline_perimeter() / ring as f64, p.length_mm / n_axial as f64),
    }
}
