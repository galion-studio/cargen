// SPDX-License-Identifier: MIT
// Copyright (c) 3000 Galion / galion-studio
//! forge-crash: truth-layer orchestration for crash cases.
//! The solver (OpenCourant, AGPL-3.0) is never linked: it runs as a separate, unmodified
//! program. This crate only writes its input files and reads its output files.

pub mod cases;
pub mod compute;
pub mod deck;
pub mod experiment;
pub mod iso18571;
pub mod mesh;
pub mod metrics;
pub mod params;
pub mod report;
pub mod th;
