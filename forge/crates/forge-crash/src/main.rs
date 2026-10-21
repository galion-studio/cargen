// SPDX-License-Identifier: MIT
// Copyright (c) 2026 Galion / galion-studio
//! `forge-p1a`: P1a square-tube crush pipeline.
//!
//!   forge-p1a deck    --variant baseline --h 5 --out DIR
//!   forge-p1a run     --variant baseline --h 5 --runs DIR --solver OPENCOURANT_ROOT [--threads 4] [--exp CSV]
//!   forge-p1a report  --dir RUN_DIR [--exp CSV]            (re-evaluate an existing run)
//!   forge-p1a summary --dirs D1,D2,... --out DIR           (combined JSON + Markdown)
//!   forge-p1a config  --variant baseline --h 5             (print case JSON)

use anyhow::{bail, Context, Result};
use forge_crash::compute::{Compute, CpuOpenCourant, RunRecord, SolverJob};
use forge_crash::report::{self, CaseReport, MeshInfo, Tolerances};
use forge_crash::{deck, experiment, mesh, params, th};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

const RUN: &str = "TUBE";
const DEFAULT_EXP: &str = "data/p1a/park2022_us2_fig3_digitized.csv";

fn args() -> (String, HashMap<String, String>) {
    let mut it = std::env::args().skip(1);
    let cmd = it.next().unwrap_or_default();
    let mut m = HashMap::new();
    let rest: Vec<String> = it.collect();
    let mut i = 0;
    while i < rest.len() {
        if let Some(k) = rest[i].strip_prefix("--") {
            let v = rest.get(i + 1).cloned().unwrap_or_default();
            m.insert(k.to_string(), v);
            i += 2;
        } else {
            i += 1;
        }
    }
    (cmd, m)
}

fn case_from(a: &HashMap<String, String>) -> Result<params::TubeCrush> {
    if let Some(cfg) = a.get("config") {
        let c: params::TubeCrush = serde_json::from_str(&std::fs::read_to_string(cfg)?)?;
        c.validate()?;
        return Ok(c);
    }
    let h: f64 = a.get("h").map(|s| s.parse()).transpose()?.unwrap_or(5.0);
    let variant = a.get("variant").map(String::as_str).unwrap_or("baseline");
    let mut c = params::p1a_us2_baseline(h);
    match variant {
        "baseline" => {}
        "pp" => c.material = params::a500_us2_perfectly_plastic(),
        "friction" => c.top_boundary = params::TopBoundary::FrictionWall,
        v => bail!("unknown variant {v} (baseline | pp | friction)"),
    }
    if let Some(v) = a.get("speed") {
        c.platen_speed_mm_s = v.parse()?;
    }
    if let Some(t) = a.get("threads") {
        c.threads = t.parse()?;
    }
    c.case_id = format!("p1a_us2_{variant}_h{h}");
    c.validate()?;
    Ok(c)
}

fn write_deck(c: &params::TubeCrush, dir: &Path) -> Result<MeshInfo> {
    std::fs::create_dir_all(dir)?;
    let m = mesh::build(c);
    let d = deck::build(c, &m, RUN);
    std::fs::write(dir.join(format!("{RUN}_0000.rad")), d.starter)?;
    std::fs::write(dir.join(format!("{RUN}_0001.rad")), d.engine)?;
    std::fs::write(dir.join("case.json"), serde_json::to_string_pretty(c)?)?;
    let info = MeshInfo { elements: m.quads.len(), nodes: m.nodes.len(), per_side: m.per_side, n_axial: m.n_axial, element_size_mm: m.actual_size_mm };
    std::fs::write(dir.join("mesh.json"), serde_json::to_string_pretty(&info)?)?;
    Ok(info)
}

fn evaluate(dir: &Path, exp_csv: &str) -> Result<CaseReport> {
    let case: params::TubeCrush = serde_json::from_str(&std::fs::read_to_string(dir.join("case.json"))?)?;
    let mesh: MeshInfo = serde_json::from_str(&std::fs::read_to_string(dir.join("mesh.json"))?)?;
    let run: RunRecord = serde_json::from_str(&std::fs::read_to_string(dir.join("run.json"))?)?;
    let hist = th::parse_csv(&dir.join(format!("{RUN}T01.csv")))?;
    let reference = experiment::park2022_us2(exp_csv);
    let exp = experiment::read_curve(Path::new(exp_csv))?;
    let r = report::build_case_report(case, mesh, run, &hist, &reference, &exp, &Tolerances::default());
    std::fs::write(dir.join("report.json"), serde_json::to_string_pretty(&r)?)?;
    std::fs::write(dir.join("report.md"), report::case_markdown(&r))?;
    // simulated curve for plotting
    let sim = report::sim_curve(&hist, 400.0);
    let mut csv = format!("# simulation output: OpenCourant, case {}\ndisplacement_mm,force_kN\n", r.case.case_id);
    for (x, f) in sim.disp_mm.iter().zip(&sim.force_kn) {
        csv.push_str(&format!("{x:.2},{f:.3}\n"));
    }
    std::fs::write(dir.join("sim_curve.csv"), csv)?;
    Ok(r)
}

fn main() -> Result<()> {
    let (cmd, a) = args();
    let exp = a.get("exp").cloned().unwrap_or_else(|| DEFAULT_EXP.to_string());
    match cmd.as_str() {
        "config" => println!("{}", serde_json::to_string_pretty(&case_from(&a)?)?),
        "deck" => {
            let c = case_from(&a)?;
            let out = PathBuf::from(a.get("out").context("--out required")?);
            let info = write_deck(&c, &out)?;
            println!("wrote deck to {} ({} shells)", out.display(), info.elements);
        }
        "run" => {
            let c = case_from(&a)?;
            let runs = PathBuf::from(a.get("runs").map(String::as_str).unwrap_or("runs"));
            let dir = runs.join(&c.case_id);
            let solver = a.get("solver").cloned().or_else(|| std::env::var("OPENCOURANT_PATH").ok()).context("--solver or OPENCOURANT_PATH required")?;
            let info = write_deck(&c, &dir)?;
            eprintln!("[forge-p1a] {}: {} shells, running solver ...", c.case_id, info.elements);
            let backend = CpuOpenCourant::new(solver);
            let rec = backend.run(&SolverJob { dir: dir.clone(), run_name: RUN.into(), threads: c.threads })?;
            std::fs::write(dir.join("run.json"), serde_json::to_string_pretty(&rec)?)?;
            let r = evaluate(&dir, &exp)?;
            println!("{}", report::case_markdown(&r));
        }
        "report" => {
            let dir = PathBuf::from(a.get("dir").context("--dir required")?);
            println!("{}", report::case_markdown(&evaluate(&dir, &exp)?));
        }
        "summary" => {
            let out = PathBuf::from(a.get("out").context("--out required")?);
            std::fs::create_dir_all(&out)?;
            let mut reps = Vec::new();
            for d in a.get("dirs").context("--dirs required")?.split(',') {
                let r: CaseReport = serde_json::from_str(&std::fs::read_to_string(Path::new(d).join("report.json"))?)?;
                std::fs::copy(Path::new(d).join("sim_curve.csv"), out.join(format!("{}_sim_curve.csv", r.case.case_id)))?;
                reps.push(r);
            }
            std::fs::write(out.join("p1a_report.json"), serde_json::to_string_pretty(&reps)?)?;
            let mut md = String::from("<!-- SPDX-License-Identifier: MIT -->\n<!-- Generated by forge-p1a summary -->\n");
            for r in &reps {
                md.push_str(&report::case_markdown(r));
                md.push('\n');
            }
            std::fs::write(out.join("p1a_report.md"), md)?;
            println!("wrote {}", out.join("p1a_report.json").display());
        }
        _ => bail!("usage: forge-p1a <config|deck|run|report|summary> [--options]; see src/main.rs"),
    }
    Ok(())
}
