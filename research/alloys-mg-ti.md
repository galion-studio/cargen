<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 Galion / galion-studio -->
# Mg and Ti alloys, plus gap materials: open chemistry and mechanical data

This is literature-only and free data (no TCMG/TCTI, no MMPDS). Every number below was read in the open full text of the cited source on 2026-10-21, unless it is marked "carried over" (verified earlier in `materials.md`).
- Machine-readable data: `data/materials/mg-ti.csv` (274 rows, 23 material entries, 16 sources).
- Banned sources (MatWeb, NIMS MatNavi, Thermo-Calc DBs, Granta, MMPDS, NIST SRD, GNoME subset) were not used. Where a paper re-quoted one of them, that table was excluded (see Licence flags).
- Confidence:
  - H: measured, primary source, full text read.
  - M: primary source but narrow conditions, or handbook/secondary.
  - L: fit outside the crash regime, ambiguous units, or a non-standard model.

## 1. Summary table (RT unless noted)

| Material | Chemistry (wt%) | ρ | E (GPa) | YS / UTS (MPa) | El. | JC / CS | Thermal | Src (conf) |
|---|---|---|---|---|---|---|---|---|
| AZ31B sheet | Al 2.5–3.5, Zn 0.6–1.4, Mn ≤0.2 (spec) | gap | gap | gap (RT) | gap | JC per RD angle, 50–250 °C, 0.005 s⁻¹ ref | T_m 630 °C (JC input) | MUR2023 (L/M) |
| AZ91 HPDC | Al 8.88, Mn 0.19, Zn 0.74 (meas.) | gap | ≈45 | 163 / 274.6 | 6.6 % | gap | — | ANG2021 (H) |
| AZ91D-F | Al 9.0, Zn 0.7, Mn ≥0.13 (nom.) | gap | — | 150 / 230 | 3 % | gap | 595/470 °C, k 73, cp 1050 | OSTI1097772 (M) |
| AM60 HPDC | Al 6.26, Mn 0.29, Zn 0.1 (meas.) | gap | ≈45 | 126 / 291.5 | 13.7 % | — | — | ANG2021 (H) |
| AM60A-F | Al 6.0, Mn ≥0.13 | gap | — | 131 / 241 | 13 % | — | 615/545 °C, k 61, cp 1000 | OSTI1097772 (M) |
| AM60B die-cast | gap | gap | gap | 143 / 246 | gap | JC fracture D1–D3; CS best fit but C, P **unpublished** | — | YANG2024 (H/M) |
| AM50A-F | Al 5.0, Mn ≥0.13 | gap | — | 124 / 228 | 15 % | gap | 620/550 °C, k 65, cp 1020 | OSTI1097772 (M) |
| AM40 HPDC | Al 4.44, Mn 0.21 (meas.) | gap | ≈45 | 111.8 / 287.0 | 17.8 % | — | — | ANG2021 (H) |
| AE44 HPDC (Mg-RE) | Al 3.67, Mn 0.31, RE 3.83 (meas.) | gap | ≈45 | not transcribed | — | gap | — | ANG2021 (H) |
| WE43 (Mg-RE) | Y 3.6, Nd 2.2, Dy 0.3, Gd 0.3, Zr 0.4 (meas.) | gap | gap | 140–280 / 210–325 (range over routes) | gap | gap | ignition 855–1082 °C | DVO2021 (M) |
| ZK60 | Zn 6, Zr 0.6 (nom.) | gap | gap | dyn. 67–172 yield @1700 s⁻¹ | — | modified JC, single rate only | — | LIU2023 (L/M) |
| Ti-6Al-4V | gap (open measured) | 4428 / 4450 | 112.5 | 773.9 YS (HT) | gap | 2 JC + JC fracture sets (LLNL), 1 SHPB JC | T_m 1605 °C, cp 580; k 3.85? | LES1999 (M), QIAN2019 (M/L) |
| CP-Ti Gr2 (T40) | gap | gap | 112–115 | 322–330 / true 619–631 | εu 12.4 % | JC A, B, n; C≈0; no m | — | SIE2021 (H) |
| Ti-3Al-2.5V tube | Al 3.05, V 2.69, Fe 0.10, O 0.10 (meas.) | gap | gap | 780–820 / 925–960 | 14–16 % | dyn/static 1.08–1.16 @3000 s⁻¹ | — | LIU2018 (H) |
| Ti-10V-2Fe-3Al | gap | gap | gap | gap | gap | 2 JC sets (cutting) | — | STO2019 (L) |
| TRIP780 weld nugget | — | 7850 | 185 | mJC A* 1526.5 | — | modified JC (weld) | cp 420, T_m 1806.7 K | LI2020 (L) |
| AA5182-O sheet | — | — | — | JC A 166, B 681, n 0.64 | — | JC C, CS D 14945, P 0.865 (EM forming) | — | LIU2022 (M/L) |
| CFRP T700GC/2510 UD | — | 1520 | E1 127, E2 8.41, G12 4.21 | XT 2200, XC 1470, YT 48.9, YC 199, S 154 | — | (MAT54 inputs) | — | FER2011 (M) |
| CFRP CarboDur S812 | — | 1600 | 165 | 3000 (limit) | εf 0.05 | — | — | SPI2026 (M) |
| SikaPower 1277 epoxy | — | 1190 | MAT305 En 1.6, Es 0.37 | CZM peak tractions | G_II 1979–2816 J/m² | rate peaks @1e4 s⁻¹ | — | SPI2026 (M/L) |
| LGF/PP 30 wt% | — | gap | 6.225 | UTS 92.4 | gap | gap | — | DU2022 (H) |

## 2. Notes per material
- **AZ31B (MUR2023):**
  - JC sets by angle to RD (A/B/n/C/m): 0° 186.163/536.359/0.719/0.0049/0.643; 45° 187.871/541.828/0.707/0.0022/0.613; 90° 211.682/799.457/1.005/0.0032/0.607.
  - References: ε̇₀ 0.005 s⁻¹, T_r 50 °C, T_m 630 °C.
  - The text's Eq. 7 uses m 0.662, which conflicts with Table 1 (0.643). We use the table.
  - The fit is calibrated for warm forming (AARE 13.5 %), so do not use it for crash. The paper also gives modified JC and modified ZA sets.
- **Die-cast Mg (ANG2021):**
  - CSIRO HPDC with ICP-AES chemistry.
  - Table 2 also has values at 50, 100 and 150 °C (not transcribed).
  - E ≈ 45 GPa is the initial loading modulus from an anelasticity study, so confidence is M.
- **OSTI1097772:** the thermal data are secondary (the report cites the ASM Specialty Handbook). The mechanical values are "industry-obtainable" typicals, not a single test.
- **AM60B:** the Cowper-Symonds fit (R² 0.9829) is the paper's chosen rate model. I re-checked the full-text XML: **C and P are not published.** The JC fracture set has no D4/D5.
- **WE43:** per-state YS/UTS values exist only in Fig. 6 (not digitised). The 140–280 / 210–325 MPa ranges come from the conclusions.
- **ZK60:** the modified JC is cubic in strain and fitted at a single rate (1700 s⁻¹), so it has no C or m that can be used.
- **Ti-6Al-4V:**
  - The LLNL sets are carried over from `materials.md` §3.1.
  - QIAN2019 gives ρ 4450, E 112.5, YS 773.9 and CTE 6.5e-6 for forged + 989 °C/30 min AC material.
  - Its k = 3.85 W/m·K looks low and is flagged L.
  - Its SHPB JC (874/583/0.316/0.003/0.95) does not state ε̇₀.
- **CP-Ti:** quasi-static only. C ≈ 1e-13 means no rate effect was resolved. No temperature term.
- **Ti-10V-2Fe-3Al:** the JC sets come from inverse cutting fits (simultaneous fit 1012.5/875.4/0.2613/0.0215/1.07). Use them only as a low-confidence starting point.
- **TRIP780:** the source is a spot-weld material model, not base sheet. Base-sheet TRIP780 is still a gap.
- **AA5182-O:** the rate terms come from inverse identification on electromagnetic hole-flanging. ε̇₀ is not stated.
- **CFRP T700/2510:** values are from Feraboli 2011 Table 1, which reproduces the AGATE allowables (Tomblin et al., FAA/NASA AGATE program). Cite AGATE as the primary source.
- **SikaPower 1277:**
  - The MAT305 table's unit column is inconsistent. Values are stored with "GPa?" / "kN/mm?" and confidence L.
  - The analytic test-derived G_II (1979–2816 J/m²) is M.
  - The authors state that AI-assisted language editing was used (text, not data).
- **LGF/PP:**
  - Only the 30 wt% measured E and UTS are data.
  - The 40 % values are DIGIMAT predictions and were excluded.
  - Constituent properties are unsourced in the paper (L).

## 3. CALPHAD (open)
- **Found:** MatCalc `mc_al` v2.037 (TU Wien), licensed ODbL 1.0 + DbCL 1.0, stored as `data/calphad/mc_al_v2037.tdb` with `NOTICE.md`.
  - It is an Al-alloy database, but it has a full Mg-Al description (LIQUID, FCC_A1, HCP_A3, γ-Al12Mg17, β-Al3Mg2, ε-Al30Mg23).
- **Smoke test:** `forge/scripts/calphad_mgal_smoke.py` (pycalphad 0.11.2 in `.venv`) parses the database in about 4 s, filtering MatCalc-only keywords in memory.
- Output is an **unvalidated estimate**: it has not been checked against an experimental Mg-Al solvus, and Zn/Mn are ignored.

| Alloy (binary) | T (°C) | HCP_A3 mole frac | γ-Al12Mg17 | X_Al in HCP |
|---|---|---|---|---|
| Mg-9Al (AZ91-like) | 200 | 0.849 | 0.151 | 0.023 |
| Mg-9Al | 300 | 0.906 | 0.094 | 0.048 |
| Mg-9Al | 400 | 0.995 | 0.005 | 0.080 |
| Mg-3Al (AZ31-like) | 200 | 0.989 | 0.011 | 0.023 |
| Mg-3Al | 300 / 400 | 1.000 | 0 | 0.027 |

- **Not found:** an open Mg-RE (WE43), Mg-Zn-Zr (ZK60) or Ti-base (Ti-Al-V, β-Ti) database whose licence is clear. This gap is still open.
- **Rejected:** pycalphad's bundled `Al-Mg_Zhong.tdb` (header: "Copyright (C) NIMS 2008", the NIMS family, which is banned).

## 4. Biggest gaps (left empty on purpose)
1. **Forming limits (FLC)** for every Mg and Ti alloy: none found open.
2. **Crash-rate JC/CS for Mg:** none found for AZ31B (only warm forming), AZ91D, AM50, WE43 or AE44. AM60B C and P are unpublished. ZK60 has only a single-rate modified JC.
3. **Density and E for most Mg alloys:** not stated in the sources read (only ≈45 GPa for die-cast). I did not use the handbook values.
4. **Ti-6Al-4V:** no open measured chemistry or tensile set for mill-annealed sheet. Ti thermal data exist only for Ti-6Al-4V, and k is suspect.
5. **Ti-10V-2Fe-3Al:** basic properties (the only paper's Table 1 is MatWeb-sourced).
6. **Steels:**
   - DP780 and DP980: no verified data. The DP980 lead is EPJ Web Conf 183 (2018) 02060, DOI 10.1051/epjconf/201818302060, CC BY; a captcha blocked it.
   - HSLA (OSTI 380343): the report is scanned and needs OCR.
   - TRIP780 base sheet: no data.
7. **5182-O** basic properties (E, ρ, YS), and **GF/PP** rate data. Lead: Cui et al., Polymers 11 (2019), PMC6960868 (not read).
8. **Structural adhesives:** no crash-grade data for Betamate or SikaPower other than the single SPI2026 set.
9. **Open CALPHAD:** none for Ti or Mg-RE.

## 5. Sources
All of the following are open full text unless noted. Commercial use: CC BY / CC BY 3.0 = yes, with attribution.

| ID | Citation | DOI / URL | Licence | Commercial |
|---|---|---|---|---|
| S_MUR2023 | Murugesan M., Yu J.-H., Chung W., Lee C.-W., "Warm Deformation Behavior and Flow Stress Modeling of AZ31B Magnesium Alloy under Tensile Deformation", *Materials* 16(14) (2023) 5088 | 10.3390/ma16145088 | CC BY 4.0 | yes |
| S_ANG2021 | Ang H.Q., "Anelastic Behaviour of Commercial Die-Cast Magnesium Alloys: Effect of Temperature and Alloy Composition", *Materials* 14(23) (2021) 7220 | 10.3390/ma14237220 | CC BY 4.0 | yes |
| S_OSTI1097772 | Schwam D. et al., "E-SMARRT Task 5.3: Casting Porosity-Free Grain Refined Magnesium Alloys", Final Tech. Report, DOE DE-FC36-04GO14230, Case Western Reserve Univ., 2013 | https://www.osti.gov/servlets/purl/1097772 | US-DOE-funded report, free; not explicitly public domain (contractor) | facts usable; thermal values are from ASM (cite as secondary) |
| S_YANG2024 | Yang Q., Jiang B., Gao L., et al., "Study on Plastic Constitutive Relation and Ductile Fracture Criterion of AM60B Magnesium Alloy", *Materials* 17(7) (2024) 1684 | 10.3390/ma17071684 | CC BY 4.0 | yes |
| S_DVO2021 | Dvorský D., Kubásek J., Hosová K., Čavojský M., Vojtěch D., *Metals* 11(5) (2021) 728 (WE43 processing / ignition) | 10.3390/met11050728 | CC BY 4.0 | yes |
| S_LIU2023 | Liu X. et al., "Effect of Grain Size on Dynamic Compression Behavior and Deformation Mechanism of ZK60 Magnesium Alloy", *Metals* 13(2) (2023) 314 | 10.3390/met13020314 | CC BY 4.0 | yes |
| S_LES1999 | Lesuer D.R., "Experimental Investigations of Material Models for Ti-6Al-4V and 2024-T3", LLNL UCRL-ID-134691 (1999) | https://digital.library.unt.edu/ark:/67531/metadc623770/ | US-gov lab report, public release | yes (facts) |
| S_QIAN2019 | Qian X., Duan X., "Constitutive Model and Cutting Simulation of Titanium Alloy Ti6Al4V after Heat Treatment", *Materials* 12(24) (2019) 4145 | 10.3390/ma12244145 | CC BY 4.0 | yes |
| S_SIE2021 | Siegel A., Laporte S., Sauter-Starace F., "Johnson–Cook Parameter Identification for Commercially Pure Titanium at Room Temperature under Quasi-Static Strain Rates", *Materials* 14(14) (2021) 3887 | 10.3390/ma14143887 | CC BY 4.0 | yes |
| S_LIU2018 | Liu R., Li Y., "Quasi-Static and Dynamic Properties of Ti-3Al-2.5V Titanium Alloy Tubes", *IOP Conf. Ser.: Mater. Sci. Eng.* 381 (2018) 012167 | 10.1088/1757-899X/381/1/012167 | CC BY 3.0 | yes |
| S_STO2019 | Storchak M., Rupp P., Möhring H.-C., Stehle T., "Determination of Johnson–Cook Constitutive Parameters for Cutting Simulations", *Metals* 9(4) (2019) 473 | 10.3390/met9040473 | CC BY 4.0 | yes (JC table only) |
| S_LI2020 | Li X., Zhang J., Liu C., "Dynamic Constitutive Equation of Resistance Spot Weld Materials of TRIP780 Steel", *J. Eng. Sci. Technol. Rev.* 13(4) (2020) 93–101 | 10.25103/jestr.134.08 | CC BY | yes |
| S_LIU2022 | Liu W., Lin Y.Z., Meng Z.H., Li J.Q., Huang S.Y., "Constitutive model and forming limit prediction of AA5182-O aluminium alloy sheet in electromagnetic forming", *IOP Conf. Ser.: Mater. Sci. Eng.* 1270 (2022) 012047 | 10.1088/1757-899X/1270/1/012047 | CC BY 3.0 | yes |
| S_FER2011 | Feraboli P., Wade B., Deleo F., Rassaian M., Higgins M., Byar A., "LS-DYNA MAT54 modeling of the axial crushing of a composite tape sinusoidal specimen", *Compos. Part A* 42(11) (2011) 1809–1825. Primary: Tomblin J. et al., AGATE allowables for T700GC-12K-31E/#2510 | 10.1016/j.compositesa.2011.08.004 | Elsevier, paywalled (read via author copy) | facts only; do not copy text or figures |
| S_SPI2026 | Špirk S., Kalina T., "Validated Cohesive Zone Models for Epoxy-Based Adhesive Joints Between Steel and CFRP Composites…", *Polymers* 18(3) (2026) 309; raw data at Zenodo 10.5281/zenodo.18130892 | 10.3390/polym18030309 | CC BY 4.0 (paper); Zenodo licence not verified | yes (paper) |
| S_DU2022 | Du B., Li Z., Bai H., et al., "Mechanical Property of Long Glass Fiber Reinforced Polypropylene Composite: From Material to Car Seat Frame and Bumper Beam", *Polymers* 14(9) (2022) 1814 | 10.3390/polym14091814 | CC BY 4.0 | yes |
| S_MCAL | MatCalc open database mc_al v2.037 (2025-07-25), Povoden-Karadeniz E. et al., TU Wien | https://www.matcalc.at/index.php/databases/open-databases | ODbL 1.0 + DbCL 1.0 | yes; share-alike on derived DBs |

## 6. Licence flags
- **Storchak 2019, Table 1** (Ti-1023 mechanical and thermal properties) cites MatWeb. It is **excluded**; only the authors' own JC fits are used.
- **pycalphad `Al-Mg_Zhong.tdb`** has a NIMS copyright header and is banned. Do not ship or use it.
- **MatCalc mc_al is ODbL.** Attribution is required, and any derived or merged database we publish must be ODbL (not MIT). It is kept in `data/calphad/` with a NOTICE.
- **Feraboli 2011 is a paywalled Elsevier paper.** Use the numbers only. **CMH-17 is SAE copyright**, so cite the AGATE report instead of CMH-17.
- **OSTI 1097772 thermal values** come from the ASM Handbook (copyrighted compilation). Cite them as secondary and prefer a primary measurement before giving them "high" confidence.
- **Unverified:** the Zenodo 18130892 licence; and JMRT 2024 WE43 JC (10.1016/j.jmrt.2024.01.288), whose values were not visible and which was not used.
