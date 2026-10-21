// SPDX-License-Identifier: MIT
// Copyright (c) 3000 galion-studio
//! Spike: truck (Apache-2.0, ricosjp/truck) as Forge's B-rep kernel.
//! Builds two exact B-rep solids, tessellates them, checks the mesh volume
//! against the closed-form volume, and writes STL files for the web viewer.

use std::f64::consts::PI;
use truck_meshalgo::prelude::*;
use truck_modeling::*;

/// Box w x d x h (mm) by sweeping a vertex -> edge -> face -> solid.
fn plate(w: f64, d: f64, h: f64) -> Solid {
    let v = builder::vertex(Point3::origin());
    let e = builder::tsweep(&v, w * Vector3::unit_x());
    let f = builder::tsweep(&e, d * Vector3::unit_y());
    builder::tsweep(&f, h * Vector3::unit_z())
}

/// Cylinder radius r, height h (mm): revolve a point into a circle, cap, extrude.
fn cylinder(r: f64, h: f64) -> Solid {
    let v = builder::vertex(Point3::new(r, 0.0, 0.0));
    let circle = builder::rsweep(&v, Point3::origin(), Vector3::unit_z(), Rad(7.0));
    let disk = builder::try_attach_plane(&[circle]).expect("planar circle");
    builder::tsweep(&disk, h * Vector3::unit_z())
}

/// Signed volume of a closed triangle mesh (divergence theorem).
fn mesh_volume(m: &PolygonMesh) -> f64 {
    let p = m.positions();
    m.faces()
        .triangle_iter()
        .map(|t| {
            let (a, b, c) = (p[t[0].pos], p[t[1].pos], p[t[2].pos]);
            a.to_vec().dot(b.to_vec().cross(c.to_vec())) / 6.0
        })
        .sum::<f64>()
        .abs()
}

fn run(name: &str, solid: &Solid, exact: f64, tol: f64) -> bool {
    let mesh = solid.triangulation(tol).to_polygon();
    let v = mesh_volume(&mesh);
    let rel = (v - exact).abs() / exact;
    let path = format!("out/{name}.stl");
    let mut f = std::fs::File::create(&path).expect("create stl");
    truck_meshalgo::prelude::stl::write(&mesh, &mut f, stl::StlType::Binary).expect("write stl");
    let ok = rel < 1e-2;
    println!(
        "{name:9} tris={:6} mesh_vol={v:12.1} mm3 exact={exact:12.1} mm3 rel_err={rel:.2e} {} -> {path}",
        mesh.faces().triangle_iter().count(),
        if ok { "PASS" } else { "FAIL" }
    );
    ok
}

fn main() {
    std::fs::create_dir_all("out").expect("out dir");
    let tol = 0.05; // mm chord tolerance
    let a = run("plate", &plate(200.0, 100.0, 5.0), 200.0 * 100.0 * 5.0, tol);
    let b = run("cylinder", &cylinder(20.0, 100.0), PI * 20.0 * 20.0 * 100.0, tol);
    std::process::exit(if a && b { 0 } else { 1 });
}
