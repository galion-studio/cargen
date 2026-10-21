// SPDX-License-Identifier: MIT
//! Integration test: every named case yields a valid deck, and a synthetic OpenCourant
//! time-history CSV goes through parsing, metrics and report generation.
use forge_crash::{cases, deck, mesh, report, th};

#[test]
fn every_case_builds_a_consistent_deck() {
    for name in cases::NAMES {
        let c = cases::by_name(name, 10.0).expect(name);
        c.params.validate().expect("valid params");
        let m = mesh::build(&c.params);
        let d = deck::build(&c.params, &m, "TUBE");
        for key in ["/BEGIN", "/MAT/PLAS_TAB/1", "/PROP/SHELL/1", "/RWALL/PLANE/1", "/INTER/TYPE7/1", "/TH/RWALL/1", "/END"] {
            assert!(d.starter.contains(key), "{name}: starter lacks {key}");
        }
        assert!(d.engine.contains("/RUN/TUBE/1"), "{name}: engine lacks /RUN");
        // every shell references existing nodes
        let ids: std::collections::HashSet<u32> = m.nodes.iter().map(|n| n.0).collect();
        assert!(m.quads.iter().all(|q| q.1.iter().all(|n| ids.contains(n))), "{name}: dangling node");
        assert_eq!(d.starter.matches("\n/SHELL/").count(), 1, "{name}: one shell block");
    }
}

fn synthetic_csv() -> String {
    // 5 s of a 1 mm/s platen pushing against a constant 10 kN: impulse = 1e4 * t
    let mut h: Vec<String> = vec!["\"time\"".into(), "\"INTERNAL ENERGY\"".into(), "\"KINETIC ENERGY\"".into()];
    for v in ["IE", "KE", "HE"] { h.push(format!("\"tube {v} \"")); }
    h.push("\"PERCENTAGE ADDED MASS\"".into());
    for i in 33..=38 { h.push(format!("\"platen force 1 platen var {i}\"")); }
    for i in 39..=44 { h.push(format!("\"platen node 1 var {i}\"")); }
    let mut s = h.join(",") + "\n";
    for k in 0..=500 {
        let t = k as f64 * 0.01;
        let d = t * 10.0; // mm
        let ie = 1.0e4 * d;
        let mut row = vec![t, ie, 0.0, ie, 0.0, 0.0, 0.0];
        row.extend([0.0, 0.0, -1.0e4 * t, 0.0, 0.0, 0.0]);
        row.extend([0.0, 0.0, -d, 0.0, 0.0, -10.0]);
        s += &row.iter().map(|x| format!("{x:e}")).collect::<Vec<_>>().join(",");
        s += "\n";
    }
    s
}

#[test]
fn synthetic_time_history_round_trip() {
    let t = th::parse_csv_str(&synthetic_csv()).expect("parse");
    assert_eq!(t.time_s.len(), 501);
    let mid = t.force_n[250];
    assert!((mid - 1.0e4).abs() < 1.0, "force from impulse derivative: {mid}");
    assert!((t.disp_mm[500] - 50.0).abs() < 1e-9);
    let c = cases::by_name("baseline", 10.0).unwrap();
    let mut p = c.params.clone();
    p.crush_distance_mm = 40.0;
    let mut r = c.reference.clone();
    r.crush_length_mm = 40.0;
    r.mean_kn = 10.0;
    let m = mesh::build(&p);
    let info = report::MeshInfo { elements: m.quads.len(), nodes: m.nodes.len(), per_side: m.per_side, n_axial: m.n_axial, element_size_mm: m.actual_size_mm };
    let run = forge_crash::compute::RunRecord { backend: "test".into(), solver_version: "synthetic".into(), threads: 1, starter_seconds: 0.0, engine_seconds: 0.0, cycles: None, th_csv: "x.csv".into() };
    let rep = report::build_case_report(p, info, run, &t, &r, None, &report::Tolerances::default());
    let mean = rep.rows.iter().find(|x| x.quantity.starts_with("Mean crush force")).unwrap();
    assert!((mean.simulated - 10.0).abs() < 0.1, "mean {}", mean.simulated);
}
