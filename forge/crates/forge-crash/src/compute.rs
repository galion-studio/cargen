// SPDX-License-Identifier: MIT
// Copyright (c) 3000 Galion / galion-studio
//! Compute backends. Only a CPU backend exists; a CUDA backend can implement the same
//! trait later. The solver is always an external, unmodified program.

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::Instant;

/// One solver job: a directory holding `<run>_0000.rad` and `<run>_0001.rad`.
#[derive(Debug, Clone)]
pub struct SolverJob {
    pub dir: PathBuf,
    pub run_name: String,
    pub threads: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunRecord {
    pub backend: String,
    pub solver_version: String,
    pub threads: u32,
    pub starter_seconds: f64,
    pub engine_seconds: f64,
    pub cycles: Option<u64>,
    pub th_csv: PathBuf,
}

pub trait Compute {
    fn name(&self) -> &str;
    /// Version string of the solver this backend launches (pinned build).
    fn solver_version(&self) -> Result<String>;
    /// Run starter + engine and convert the time history; returns the run record.
    fn run(&self, job: &SolverJob) -> Result<RunRecord>;
}

/// OpenCourant release package (unzipped) on the local CPU, SMP (OpenMP) engine.
pub struct CpuOpenCourant {
    pub root: PathBuf,
}

impl CpuOpenCourant {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        Self { root: root.into() }
    }
    fn exe(&self, name: &str) -> PathBuf {
        self.root.join("exec").join(name)
    }
    fn command(&self, exe: &str, dir: &Path) -> Command {
        let mut c = Command::new(self.exe(exe));
        let ld = format!(
            "{}:{}",
            self.root.join("extlib/hm_reader/linux64").display(),
            self.root.join("extlib/h3d/lib/linux64").display()
        );
        c.current_dir(dir)
            .env("LD_LIBRARY_PATH", ld)
            .env("RAD_CFG_PATH", self.root.join("hm_cfg_files"))
            .env("OMP_STACKSIZE", "400m")
            .env("OMP_WAIT_POLICY", "PASSIVE");
        c
    }
}

fn run_logged(mut cmd: Command, log: &Path) -> Result<f64> {
    let f = std::fs::File::create(log)?;
    let t0 = Instant::now();
    let status = cmd
        .stdout(f.try_clone()?)
        .stderr(f)
        .status()
        .with_context(|| format!("failed to launch {:?}", cmd.get_program()))?;
    let dt = t0.elapsed().as_secs_f64();
    if !status.success() {
        bail!("{:?} exited with {status}; see {}", cmd.get_program(), log.display());
    }
    Ok(dt)
}

/// Parse "TOTAL NUMBER OF CYCLES  :  233514" from an engine log.
pub fn parse_cycles(log: &str) -> Option<u64> {
    log.lines()
        .find(|l| l.contains("TOTAL NUMBER OF CYCLES"))
        .and_then(|l| l.split(':').nth(1))
        .and_then(|v| v.trim().parse().ok())
}

impl Compute for CpuOpenCourant {
    fn name(&self) -> &str {
        "cpu-opencourant-smp"
    }
    fn solver_version(&self) -> Result<String> {
        let out = self.command("starter_linux64_gf", &self.root).arg("-version").output()?;
        let txt = String::from_utf8_lossy(&out.stdout);
        let commit = txt.lines().find(|l| l.contains("CommitID")).unwrap_or("CommitID: unknown").trim();
        let date = txt.lines().find(|l| l.contains("Date of build")).unwrap_or("").trim();
        Ok(format!("OpenCourant starter/engine linux64_gf, {commit}, {date}"))
    }
    fn run(&self, job: &SolverJob) -> Result<RunRecord> {
        let starter = format!("{}_0000.rad", job.run_name);
        let engine = format!("{}_0001.rad", job.run_name);
        let mut c = self.command("starter_linux64_gf", &job.dir);
        c.args(["-i", &starter, "-np", "1"]);
        let ts = run_logged(c, &job.dir.join("starter.log"))?;
        let mut c = self.command("engine_linux64_gf", &job.dir);
        c.args(["-i", &engine, "-nt", &job.threads.to_string()]);
        let te = run_logged(c, &job.dir.join("engine.log"))?;
        let elog = std::fs::read_to_string(job.dir.join("engine.log")).unwrap_or_default();
        if !elog.contains("NORMAL TERMINATION") {
            bail!("engine did not terminate normally; see {}", job.dir.join("engine.log").display());
        }
        let th = format!("{}T01", job.run_name);
        let mut c = self.command("th_to_csv_linux64_gf", &job.dir);
        c.arg(&th);
        run_logged(c, &job.dir.join("th_to_csv.log"))?;
        Ok(RunRecord {
            backend: self.name().into(),
            solver_version: self.solver_version()?,
            threads: job.threads,
            starter_seconds: ts,
            engine_seconds: te,
            cycles: parse_cycles(&elog),
            th_csv: job.dir.join(format!("{th}.csv")),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn cycles_parse() {
        let log = "foo\n     TOTAL NUMBER OF CYCLES  :  233514\n";
        assert_eq!(parse_cycles(log), Some(233514));
        assert_eq!(parse_cycles("nothing"), None);
    }
}
