<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2026 Galion / galion-studio -->
# Materials research: sources, licences, published parameter sets (v0)

Research done 2026-10-21 16:47–17:00 +02:00 (Europe/Zagreb). Read-only web research. Nothing was installed, bought or signed up for. Separate from obsidian-open-mind / Wave 4.

**Rules used in this file**
- A licence is marked "verified" only when I read it on the owner's own site, or in the licence file in the official repository, in this session.
- A number is quoted only when I read it in the cited document in this session (primary source, or a clearly labelled secondary source). Anything else says **not verified**.
- This is not legal advice. Before launch, a lawyer should review every source we bundle or redistribute.
- Facts and numbers taken from papers are generally usable with a citation. Copying a paper's tables, figures or text wholesale depends on the paper's licence: CC BY papers are fine with attribution, while for paywalled papers we should cite and re-derive, not copy.

---

## 1. Summary for the product (commercial hosted subscription)

### Usable commercially (with attribution)
| Source | What | Licence (verified where noted) |
|---|---|---|
| pycalphad | CALPHAD equilibrium engine (Python) | MIT (verified, repo LICENSE.txt) |
| ESPEI | CALPHAD database fitting / uncertainty | MIT (GitHub licence metadata) |
| MatCalc open databases mc_fe / mc_al / mc_ni (+ .ddb mobility, physical_data.pdb) | Open CALPHAD TDB files for steels and Al alloys | ODbL 1.0 + DbCL 1.0 (verified on matcalc.at). Commercial use OK. Share-alike applies to derived *databases* we publicly distribute |
| Materials Project (core data) + pymatgen + mp-api | DFT crystal/thermo/elastic data | Data: CC BY 4.0 (verified, legacy.materialsproject.org/terms). pymatgen: MIT (verified). mp-api: LBNL BSD-style (verified). **GNoME subset is non-commercial only** |
| NIST non-SRD datasets (data.nist.gov) | Measured stress–strain curves (Kolsky bar, Numisheet 2020 DP980/DP1180/6xxx) | NIST open licence (verified, nist.gov/open/license): not copyrighted in the US, worldwide royalty-free right to redistribute and make derivative works, with acknowledgement + note of changes |
| CC BY open-access papers (MDPI, PLOS ONE) | Published JC / fracture parameter sets | CC BY 4.0 (verified on article pages) |
| OpenRadioss built-in models | /MAT/LAW2 (Johnson-Cook), /FAIL/JOHNSON, /FAIL/TAB2 (tabulated GISSMO-style damage) | OpenRadioss is AGPL (see PLAN.md). Run it as a separate program |

### Usable but restricted (cite and quote, don't bulk-redistribute)
- **WorldAutoSteel AHSS Application Guidelines (ahssinsights.org):** free to read, owned by worldsteel. Quoting is allowed if the source is acknowledged each time, and the data must not be changed or misrepresented (verified, worldsteel.org/global/copyright.html). There is no open licence, so don't mirror the content.
- **OpenCalphad:** GPL v3 (GNU-GPL-v3.pdf in the official repo, and the NIST software page says "GNU General Public License"). Commercial use is fine. Running it as an unmodified external process from our service is the low-risk pattern, because GPL obligations attach when we distribute modified binaries.
- **Published paywalled papers (Elsevier, Springer):** cite the numbers, don't copy the tables or figures.

### Licence blockers (do not ingest into the paid product)
| Source | Blocker (verified on owner's site) |
|---|---|
| **MatWeb** | Personal, single-computer licence. Max 500 materials. **No selling or redistribution, no mass export, and no AI/ML training, embeddings, fine-tuning or evaluation datasets.** The footer says "intended for personal, non-commercial use". This is the hardest blocker: we cannot use it even as RAG input |
| **NIMS MatNavi** (incl. CPDDB, CCT diagrams, creep/fatigue data sheets) | The data is licensed only to the registrant, for their own education, R&D or product development. Prohibited: use by others, transmission, derivative use outside that scope, scraping and mass download. Needs an approved organisational DICE account. **No redistribution in a hosted service** |
| **Thermo-Calc** (TCFE, TCAL, TCMG, TCTI…) | Proprietary paid EULA. The free Educational Package is "only for educational purposes in an academic environment", one user, expires after 12 months. The Trial licence forbids commercial or production use. The demo DBs (FEDEMO, ALDEMO…) are under those same terms. PURE5 (SGTE unary) is a free download, but I did not verify separate redistribution terms, so treat it as **not cleared** |
| **Ansys Granta** (MI, Materials Data for Simulation, EduPack) | Licensed Ansys product (MDS is billed per 30-minute checkout). EduPack is education-only. Not open data |
| **MMPDS** (successor of MIL-HDBK-5) | Battelle copyright, sold through Battelle and its distributors. Redistribution or derivative works only for paying ISG members at a certain level (per Battelle letters found in search; the purchase page itself only lists vendors). Treat as **blocked** unless we buy a licence |
| **NIST Standard Reference Data (SRD)** | Copyrighted under 15 U.S.C. §290e. Redistribution needs NIST permission. (This is different from the normal NIST datasets above, which are open) |
| **Materials Project GNoME subset** | Non-commercial (MP docs: opting in is "for non-commercial uses"). Filter out `batch_id = gnome_r2scan_statics` |

Maybe: **MIL-HDBK-5J (2003)**, the last public predecessor of MMPDS. Search results (archive.org text copy) show "Distribution Statement A. Approved for public release; distribution is unlimited." **I did not open the document myself; not verified.** If confirmed, it is a legally clean, old-but-real source of A/B-basis allowables for 6061, 7075, Ti-6Al-4V and steels. It does not cover AHSS.

---

## 2. Source-by-source detail

### 2.1 CALPHAD / chemistry and phase tools
**pycalphad**: https://pycalphad.org · https://github.com/pycalphad/pycalphad
- Contains: a Python library for CALPHAD (Gibbs energy minimisation, phase diagrams, property calculation from TDB files). No databases are bundled except examples.
- Licence: MIT (verified from LICENSE.txt: © Otis, Liu, Bocklund, Caltech, Materials Genome Foundation, Walz). Commercial use and redistribution are allowed.
- Maturity: actively maintained (last push 2026-10-21), about 420 GitHub stars, widely cited in the literature. Accuracy depends entirely on the TDB file used.

**ESPEI**: https://github.com/PhasesResearchLab/ESPEI
- Contains: tools to fit and refine CALPHAD parameters, with MCMC uncertainty. Licence: MIT (GitHub licence metadata). Maturity: maintained (last push 2026-09).

**OpenCalphad**: https://www.opencalphad.com · https://github.com/sundmanbo/opencalphad
- Contains: a Fortran equilibrium code (Sundman, Kattner, Palumbo, first released 2013; stable v6.0) and the OCASI API for coupling into simulations. No large assessed databases are included.
- Licence: GPL v3 (GNU-GPL-v3.pdf in the repo; the NIST software page also says GPL). Commercial use is OK. Copyleft applies if we distribute modified code.
- Maturity: research-grade, small community, command-line driven.

**MatCalc open databases**: https://www.matcalc.at/index.php/databases/open-databases
- Contains: mc_fe.tdb v2.062 (2024-11-08; Fe, Al, B, C, Co, Cr, Cu, H, Hf, La, Mn, Mo, N, Nb, Ni, O, P, Pd, S, Si, Ta, Ti, V, W, Y), which covers mild, HSLA, DP, TRIP and 22MnB5 chemistries. mc_al.tdb v2.037 (2025-07-25; Al, Cr, Cu, Fe, Mg, Mn, Ni, Sc, Si, Ti, Zn, Zr), which covers 5xxx, 6xxx and 7xxx. There are also mobility .ddb files and physical_data.pdb.
- Licence: ODbL 1.0 + DbCL 1.0 (verified on the page). Commercial use is allowed. Attribution is required. Share-alike applies to adapted databases that we publicly use or distribute.
- Gaps: there is **no open Mg (AZ31, AM60) or Ti (Ti-6Al-4V) multicomponent database** here. Options: TDBs published as supplements to papers (check each file's licence), or a paid TCMG/TCTI licence. Not resolved.
- Maturity: maintained by the MatCalc team (TU Wien spin-off). Whether pycalphad reads these TDBs without edits is **not verified**; it needs testing.

**Thermo-Calc**: https://thermocalc.com/licensing-options/ · EULA https://thermocalc.com/wp-content/uploads/Documentation/Terms_Conditions/eula.pdf
- The best-validated commercial databases (TCFE, TCAL, TCMG, TCTI). Proprietary, and no open databases are usable for our product (see blockers).

**Materials Project**: https://materialsproject.org · docs https://docs.materialsproject.org
- Contains: DFT (GGA/GGA+U/r2SCAN) structures, formation energies, phase stability, elastic tensors, and an alloys section. It is useful for intermetallic phases (Mg17Al12, Mg2Si, MgZn2, Al3Ti, Fe3C…) and elastic constants. It has **no** strain-rate, fracture or forming data.
- Licence: CC BY 4.0 for content (verified on the legacy terms page). The next-gen terms page (next-gen.materialsproject.org/about/terms) was blocked to my fetch by a Cloudflare challenge, so it was skipped. Do not scrape: the API terms ask you to email them before large downloads.
- Maturity: high. Large, well-documented DFT database, but the values are DFT, not experimental.

**NIST**: licence page https://www.nist.gov/open/license
- Non-SRD NIST data: open (see §1). SRD: copyrighted (see blockers).
- Relevant open NIST datasets found (data.nist.gov, licence field = nist.gov/open/license):
  - *Data for Numisheet 2020 uniaxial tensile and tension/compression tests*, NIST Center for Automotive Lightweighting (NCAL), tests done Oct 2019 – Jan 2020. Materials: DP980, DP1180, AA6xxx-T4, AA6xxx-T81. Includes per-orientation CSV curves (0–90°). DOI 10.18434/M32202.
  - Mates S.P., Lopez-Hawa H., *Dynamic compressive stress-strain curves of aluminum alloy 6061-T6 with rapid heating* (2023). DOI 10.18434/mds2-3090.
  - Mates S., Siegler A., *Dynamic Compressive Stress-Strain Curves of Aluminum 7075-T6 Between 20 °C and 410 °C with Rapid Heating* (2025). DOI 10.18434/mds2-3807.
  - Mates S.P., *Dynamic Compressive Stress-Strain Curves for 1018 Carbon Steel Between 23 °C and 940 °C with Rapid Heating* (2025). DOI 10.18434/mds2-3746. (A 1075 steel set also exists: DOI 10.18434/mds2-3749.)
  - These are ideal **validation** data for our JC fits: measured, high-rate, with temperature, from NIST, and redistributable.

**NIMS MatNavi**: https://mits.nims.go.jp/en/ · terms https://mits.nims.go.jp/agreement/MatNavi_agreement_en.pdf (rev. 2024-08-01)
- Contains: polymer, inorganic and metallic DBs, CCT diagrams for welding, NIMS creep, fatigue and corrosion data sheets, and the computational phase diagram DB. High quality, but blocked for our use (see §1).

**MatWeb**: https://www.matweb.com/reference/terms.aspx. Blocked (see §1).

### 2.2 Engineering design data
**WorldAutoSteel AHSS Application Guidelines v7.x**: https://ahssinsights.org (updated edition announced 2025-11-24)
- Contains: metallurgy, forming, joining, FLC guidance and simulation inputs for mild, HSLA, DP, TRIP, CP, MS, PHS (22MnB5) and 3rd-gen grades, with about 1,000 citations. The best free *engineering* overview for steels. It is guidance, not a numeric database.
- Licence: worldsteel copyright (verified, see §1). Read, cite and quote with "Source: World Steel Association (worldsteel)". Don't redistribute.

**MMPDS**: https://www.mmpds.org/purchase-handbook/. Paid (see blockers). It is the aerospace standard for design allowables (A/B basis) for Al, Ti and steel.

**Ansys Granta**: proprietary (see blockers).

### 2.3 Solver-side models (how the data gets used)
- **OpenRadioss** (from the Altair Radioss reference guide, which shares the keyword set): `/MAT/LAW2` (PLAS_JOHNS) is Johnson-Cook plasticity, with an optional Zerilli-Armstrong form. `/MAT/LAW36` is tabulated hardening. `/FAIL/JOHNSON` is JC cumulative damage. `/FAIL/TAB2` is tabulated failure strain vs triaxiality, Lode, temperature, rate and element size, with damage exponent N, DCRIT softening, an instability (necking) curve and element-size regularisation. That is the GISSMO concept in Radioss form (doc read at https://2024.help.altair.com/2024.1/hwsolvers/rad/topics/solvers/rad/fail_tab2_starter_r.htm). The doc's example steel failure curve is illustrative only and is **not** a material dataset.
- **GISSMO** (original LS-DYNA formulation; papers verified via Crossref):
  - Andrade F., Feucht M., Haufe A., Neukamm F., "An incremental stress state dependent damage model for ductile failure prediction", *Int. J. Fracture* 200 (2016) 127–150. DOI 10.1007/s10704-016-0081-2.
  - Feucht M., Neukamm F., Haufe A., "A Phenomenological Damage Model to Predict Material Failure in Crashworthiness Applications", in *Recent Developments and Innovative Applications in Computational Mechanics*, Springer (2011) 143–153. DOI 10.1007/978-3-642-17484-1_17.
  - Published GISSMO parameter sets for specific grades: **not verified**. None were found in open-access sources this session.

---

## 3. Published parameter sets (values read from the cited document this session)

JC flow stress: σ = (A + B·εᵖⁿ)(1 + C·ln ε̇*)(1 − T*ᵐ). JC failure: ε_f = [D1 + D2·exp(D3·σ*)](1 + D4·ln ε̇*)(1 + D5·T*). Units are MPa. Always record the reference strain rate ε̇₀, T_ref and T_melt alongside the set. Mixing sets with different ε̇₀ is a common error.

### 3.1 Ti-6Al-4V
| Set | A | B | n | C | m | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|---|---|---|---|
| "Original" (Johnson, NSWC TR 86-144, 1985, as tabulated by Lesuer) | 862 | 331 | 0.34 | 0.012 | 0.8 | −0.09 | 0.25 | −0.5 | 0.014 | 3.87 |
| "New" LLNL set (Lesuer 1999) | 1098 | 1092 | 0.93 | 0.014 | 1.1 | −0.09 | 0.25 | −0.50 | 0.014 | 3.87 |
- Physical data in the same report (Table 7): T_melt 1605 °C, ρ 4428 kg/m³, c_p 580 J/kg·K.
- Sources:
  - Lesuer D.R., "Experimental Investigations of Material Models for Ti-6Al-4V and 2024-T3", LLNL report UCRL-ID-134691, 3 May 1999 (Tables 6 and 8). https://digital.library.unt.edu/ark:/67531/metadc623770/ (no DOI).
  - The original set also appears in Lesuer D.R., Kay G.J., LeBlanc M.M., "Modeling Large-Strain, High-Rate Deformation in Metals", LLNL UCRL-JC-134118, Third Biennial Tri-Laboratory Engineering Conference, 2001, Table 1. https://www.osti.gov/biblio/15005327.
- Underlying primary: Johnson G.R., "Strength and Fracture Characteristics of a Titanium Alloy (.06Al, .04V)…", NSWC TR 86-144 (1985). Not read: **not verified directly**.
- Validation: the 1999 set was fitted to LLNL Hopkinson-bar data plus literature data (10⁻⁴ to about 5000 s⁻¹). The report shows the original set under-predicts strength for higher-hardness material.

### 3.2 Aluminium 6061-T6
| A | B | n | C | m | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|---|---|---|
| 324 | 114 | 0.42 | 0.002 | 1.34 | −0.77 | 1.45 | −0.47 | 0.0 | 1.60 |
- Source: Lesuer, Kay, LeBlanc, UCRL-JC-134118 (2001), Table 1 (as above). The report lists Johnson & Cook (1983, 1985) as its JC references.
- Primary references (bibliographic data verified; values not read in the primaries):
  - Johnson G.R., Cook W.H., "A constitutive model and data for metals subjected to large strains, high strain rates and high temperatures", Proc. 7th Int. Symp. Ballistics, The Hague, 1983, pp. 541–547 (no DOI).
  - Johnson G.R., Cook W.H., "Fracture characteristics of three metals subjected to various strains, strain rates, temperatures and pressures", *Eng. Fract. Mech.* 21(1) (1985) 31–48. DOI 10.1016/0013-7944(85)90052-9 (verified via Crossref).
- Validation data available: NIST 6061-T6 Kolsky-bar curves with rapid heating (DOI 10.18434/mds2-3090, open).

### 3.3 Aluminium 6082-T6 (CC BY 4.0 source)
- JC: A = 277.33 MPa, B = 307.93 MPa, n = 0.69, C = 0.0032, ε̇₀ = 0.0001 s⁻¹ (Table 3). m = 1.28, Taylor–Quinney χ = 0.9, ρ = 2.71 g/cm³, c_p = 0.96 J/(g·K), E = 71,000 MPa, ν = 0.3 (Table 5).
- JC fracture (Table 7):
  - "Common method": D1 = 0.26862, D2 = 9.20158, D3 = −10.6552.
  - Calibrated: D1 = 0.21125, D2 = 3.91116, D3 = −4.72526.
  - D4 and D5: not given in the tables I read.
- Measured yield stress vs rate (Table 2): 277.33 MPa at 10⁻⁴ s⁻¹ up to 288.83 MPa at 3400 s⁻¹, so the alloy is weakly rate sensitive.
- Source: Chen X., Peng Y., Peng S., Yao S., Chen C., Xu P., "Flow and fracture behavior of aluminum alloy 6082-T6 at different tensile strain rates and triaxialities", *PLOS ONE* 12 (2017) e0181983. DOI 10.1371/journal.pone.0181983. CC BY (verified on the article page).
- Validation: Charpy simulation vs experiment in the same paper (Table 8). Errors are large with the "common" set and smaller with the calibrated set.

### 3.4 Aluminium 7075-T6 / T651
| Temper | A | B | n | C | m | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|---|---|---|---|
| 7075-T651 | 527 | 676 | 0.71 | 0.017 | 1.61 | 0.110 | 0.573 | −3.4446 | 0.016 | 1.099 |
| 7075-T6 | 546 | 674 | 0.72 | 0.059 | 1.56 | 0.451 | −0.952 | −0.068 | 0.036 | 0.697 |
- Source: Brar N.S., Joshi V.S., Harris B.W., "Constitutive model constants for Al7075-T651 and Al7075-T6", *AIP Conf. Proc.* 1195 (Shock Compression of Condensed Matter 2009) 945–948. DOI 10.1063/1.3295300 (verified via Crossref).
- Values read from the official APS meeting abstract (https://meetings-archive.aps.org/sccm/2009/b5/2/). The full paper is paywalled and was not read.
- Calibration: tension tests at room temperature up to 250 °C, plus notched and smooth fracture specimens.
- Validation data available: NIST 7075-T6 dynamic compression, 20–410 °C (DOI 10.18434/mds2-3807, open).

### 3.5 22MnB5 press-hardened (quenched, lath martensite; TSCR-produced) (CC BY 4.0 source)
- JC (Table 2): A = 1452.03 MPa, B = 1201.14 MPa, n = 0.56, C = 0.00704, m = 0.84736. ε̇₀ = 0.001 s⁻¹, T_ref = 293 K, T_melt = 1517.63 °C.
- The paper's modified JC (polynomial-in-strain terms, c1 = 1.523) reaches R² = 0.94 ± 0.03 over 0.001–3000 s⁻¹ and 293, 423 and 523 K.
- JC fracture: D1 = 0.03265, D2 = −0.05868, D3 = 8.1825, D4 = −2.82663. D5 was not determined. These come from 3 specimen geometries at quasi-static rate. Note: the published fracture strains are very low (0.012–0.032), and D2 < 0 and D4 = −2.83 are unusual. **Treat this damage set as low confidence** and validate it before use.
- Chemistry (Table 1, wt.%): C 0.214, Si 0.228, Mn 1.297, P 0.011, S 0.0042, B 0.0028, N 0.0057, Fe balance.
- Source: Song Y., Xu Y., Yang G., "Johnson–Cook Constitutive Model Parameters Estimation of 22MnB5 Hot Stamping Steel for Automotive Application Produced via the TSCR Process", *Metals* 15(7) (2025) 811. DOI 10.3390/met15070811. CC BY (MDPI).
- Better crash-grade reference (rate-sensitive model for quenched boron steel with tailored properties; not read, values **not verified**): Bardelcik A., Worswick M., Winkler S., Wells M., *Int. J. Impact Eng.* 50 (2012) 49–62. DOI 10.1016/j.ijimpeng.2012.06.007.

### 3.6 DP600
- JC: A = 350 MPa, B = 902 MPa, C = 0.014, m = 1.23, n = 0.189.
- **Secondary source only:** Farokhi Nejad A., Pourasghar M., Peirovi S., Tamin M.N., "Computational Aided Design for Generating a Modular, Lightweight Car Concept", arXiv:1711.10782, Table 2. It cites Alipour R., Farokhi Nejad A., Izman S., "The reliability of finite element analysis results of the low impact test in predicting the energy absorption performance of thin-walled structures", *J. Mech. Sci. Technol.* 29(5) (2015) 2035–2045, DOI 10.1007/s12206-015-0424-3. I did not read the primary, so the value is verified in the secondary only. ε̇₀ is not stated, so **low confidence**.
- Better DP600 primaries (paywalled, values **not verified**):
  - Yu H., Guo Y., Lai X., "Rate-dependent behavior and constitutive model of DP600 steel at strain rate from 10⁻⁴ to 10³ s⁻¹", *Mater. Des.* 30 (2009) 2501–2505. DOI 10.1016/j.matdes.2008.10.001.
  - Yu H., Guo Y., Zhang K., Lai X., *Comput. Mater. Sci.* 46 (2009) 36–41. DOI 10.1016/j.commatsci.2009.01.025.

### 3.7 AM60B (die-cast) (CC BY 4.0 source)
- Hardening (Swift-weighted Hockett–Sherby): K = 666.769, ε₀ = 0.02929, n = 0.444, σ₀ = 146.361, A = 168.581, B = 23.815, m = 1.263. Weighting α = 0.2 (uniaxial) or 0.185 (global, 4 stress states).
- Quasi-static YS 143 MPa, UTS 246 MPa.
- Fracture (Table 5):
  - JC: D1 = 0.106, D2 = 6.767, D3 = −17.842.
  - MMC: K = 669.973, C = 142.197, f = 0.076, n = 0.447.
  - DIEM: k = −3.970, e0 = 0.317, e1 = 0.007, f = 0.593.
- Stress state vs fracture strain (Table 4): shear η 0.01 → 0.134; tension 0.333 → 0.118; R10 notch 0.386 → 0.128; cupping 0.666 → 0.454.
- Rate model: Cowper–Symonds fitted best (R² 0.9829 average over 1–1000 s⁻¹), but the C and P values are **not given in the text I could read**, so they are **not verified**.
- Validation: three-point bending of a front-end member. Fracture-time error is JC 21.6 %, MMC 14.7 % and DIEM 8.8 %.
- Source: Yang Q., Jiang B., Gao L., Gao Y., Liang B., Lan S., Qin Z., Zou W., Yang F., Pan F., "Study on Plastic Constitutive Relation and Ductile Fracture Criterion of AM60B Magnesium Alloy", *Materials* 17(7) (2024) 1684. DOI 10.3390/ma17071684. CC BY (MDPI).

### 3.8 Cowper–Symonds, mild steel
- σ_d = σ_y[1 + (ε̇/D)^(1/q)], with D = 40.4 s⁻¹ and q = 5 ("standard coefficients" for mild steel).
- Read in: Liu B., Guedes Soares C., "Recent developments in ship collision analysis and challenges to an accidental limit state design method", *Ocean Eng.* 270 (2023) 113636, DOI 10.1016/j.oceaneng.2023.113636. It cites Cowper G.R., Symonds P.S., "Strain hardening and strain rate effects in the loading of cantilever beams", Brown Univ. Applied Mathematics Report 28 (1957), and Jones N. (2013) for the caveat that D and q vary with strain.
- Aluminium D = 6500 s⁻¹, q = 4 (often quoted from Jones, *Structural Impact*): **not verified** this session.
- Note: in LS-DYNA MAT_003, C corresponds to D and P to q.

### 3.9 Forming limit (FLC0) for steels
- Keeler–Brazier: FLC0 (engineering major strain, %) = (23.3 + 14.2·t)·n/0.21, with t in mm. In inches: (23.3 + 360·t)·n/0.21.
- Source: Keeler S., *Enhanced Forming Limit Diagram, Project Team Technology Report*, Auto/Steel Partnership, https://www.a-sp.org/wp-content/uploads/2020/08/Technology-Report-Final.pdf (equations read in the PDF).
- AHSS Guidelines (https://ahssinsights.org/forming/formability/forming-limit-curves-flc/) confirm the scope:
  - The formula is fine for mild, conventional HSLA and some lower-strength DP (e.g. CR340Y/590T-DP).
  - The left side is constant thinning; the right side has slope about +0.6 up to 20 % minor strain.
  - **TRIP, MS, TWIP and retained-austenite grades need experimental FLCs** (ISO 12004 / ASTM E2218; Nakajima or Marciniak).

### 3.10 Not verified this session (open gaps)
- **Not verified:** JC or Cowper–Symonds sets for mild steel (as JC), HSLA, DP780, DP980, TRIP (690/780), 5182-O, AZ31B, and the JC damage values for 4340, OFHC Cu and Armco iron from Johnson & Cook 1985.
- AZ31B: Ulacia I., Salisbury C., Hurtado I., Worswick M., *J. Mater. Process. Technol.* 211(5) (2011) 830–839, DOI 10.1016/j.jmatprotec.2010.09.010, is the right primary. It is paywalled, and a search-snippet value set was **not verified**.
- 5182-O: Smerd R. et al., "High strain rate tensile testing of automotive aluminum alloy sheet", *Int. J. Impact Eng.* (2005), DOI 10.1016/j.ijimpeng.2005.04.013. Values **not verified**.
- University of Waterloo theses (Smerd 2005; Thompson AHSS high-rate thesis with DP600/DP800/TRIP tables): the UWSpace and collectionscanada downloads were blocked by bot protection or timed out, so they were **skipped**. They are worth reading by hand.
- DP980 / DP1180 / 6xxx quasi-static curves: available as raw open data (NIST Numisheet 2020, §2.1). We can fit our own JC/Swift/Voce hardening to them and publish the fit with the dataset as source.

---

## 4. Recommendations
1. **Build the material library from open sources only:** NIST open datasets, CC BY papers, MatCalc ODbL databases, Materials Project CC BY, pycalphad/ESPEI. Store the source DOI, licence, ε̇₀, T_ref and validation error with every parameter set (this matches the "truth layer" rule in PLAN.md).
2. **Never ingest MatWeb, MatNavi, Thermo-Calc DBs, Granta, MMPDS or NIST SRD** into the product, its RAG index or its training data.
3. **Fit our own parameters to open raw data** (NIST DP980/DP1180/6xxx, NIST Kolsky 6061/7075/1018) and validate against the NIST rapid-heating curves. Our own fits are cleanly ours to distribute.
4. **Need Mate's decision:** whether to buy licences for proprietary data covering Mg and Ti CALPHAD (TCMG/TCTI) and MMPDS allowables, or accept literature-only coverage for AZ31, AM60 and Ti-6Al-4V.
5. Before release, a lawyer should confirm ODbL share-alike scope, the GPL boundary for OpenCalphad, and MIL-HDBK-5J public-release status.
