# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Cited lookup tables for weldtool.

Every number in this file was transcribed from the source named next to it
(see SOURCES for full citation and URL). Nothing here is fitted or invented.
Where no open source was found, the entry is absent and the tool says so.
Unit conversions (in->mm, lb->kN, cycles->ms) are done in core.py, not here.
"""

SOURCES = {
    "MILLER211": ("Miller Electric, Millermatic 211 PRO Welding Parameter Chart (299298)",
                  "https://contenthub.itwwelding.com/api/public/content/miller-electric-mfg-llc/parameter-chart/PIM/d31dfc-millermatic-211-pro-parameter-chart-299298.pdf"),
    "MILLER_RULES": ("Miller Electric, MIG Welding: Setting the Correct Parameters",
                     "https://www.millerwelds.com/en-us/resources/knowledge-hub/mig-welding/how-to/mig-welding-setting-the-correct-parameters"),
    "LINCOLN_SQW": ("Lincoln Electric, Square Wave TIG quick-reference (TIG amperage, tungsten, filler)",
                    "https://ch-delivery.lincolnelectric.com/api/public/content/582e9857a7324db29d14ceb7d16a8609?v=dfb50bd9"),
    "NSRW_LC": ("NSRW Application Data Sheet p.72, Spot welding schedules for low carbon steel SAE 1010 (RWMA-style tables)",
                "https://nsrw.com/wp-content/uploads/Spot-Welding-schedule-for-low-Carbon-Steel_72.pdf"),
    "AWS_C11": ("AWS C1.1M/C1.1:2019-AMD1 Recommended Practices for Resistance Welding, Amendment 1 (preview)",
                "https://pubs.aws.org/Download_PDFS/C1.1M_C1.1_2019_AMD1_PV.pdf"),
    "TWI_UHSS": ("Westgate S., The resistance spot welding of high and ultra-high strength steels, TWI, 2004",
                 "https://www.twi-global.com/technical-knowledge/published-papers/the-resistance-spot-welding-of-high-and-ultra-high-strength-steels-november-2004"),
    "EAA_RSW": ("European Aluminium, Aluminium Automotive Manual - Joining, 5. Resistance welding (2015)",
                "https://european-aluminium.eu/wp-content/uploads/2022/11/5-resistance-welding_2015.pdf"),
    "EC9_WS": ("Hoglund T., Strength and stability of aluminium members according to EN 1999-1-1, Eurocodes workshop Brussels 2008 (slides 21-22, 25)",
               "https://wapi.gov.me/download/b0a72923-59dd-4164-9b43-b5ed6c38c0dc?version=1.0"),
    "EC9_EAA": ("European Aluminium, Design of aluminium structures - Introduction to Eurocode 9 with worked examples",
                "https://european-aluminium.eu/wp-content/uploads/2022/08/design-of-aluminium-structure-introduction-to-eurocode-9-with-worked-examples-1.pdf"),
    "CESTRUCO": ("CESTRUCO lecture 13, Aluminium connections (ENV 1999 HAZ tables 13.2/13.3)",
                 "https://people.fsv.cvut.cz/www/wald/Leonardo-CESTRUCO/DOKUMENTS/T10-13_Aluminium_connections_revised.pdf"),
    "LINCOLN_AL": ("Lincoln Electric, Common Design Mistakes in Aluminum",
                   "https://www.lincolnelectric.com/en/welding-and-cutting-resource-center/welding-how-tos/common-design-mistakes-in-aluminum"),
    "ADM2020": ("STRUCTURE magazine, The 2020 Aluminum Design Manual",
                "https://www.structuremag.org/article/the-2020-aluminum-design-manual/"),
    "MA2022_FSW": ("Ma X. et al., FSW AA6082-T6 joints, Materials 15 (2022) 6579, CC BY 4.0",
                   "https://www.mdpi.com/1996-1944/15/19/6579"),
    "DP980_GMAW_RSW": ("On the Measurability and Predictability of HAZ Softening in GMAW of Automotive DP980 Steel, Metals 12 (2022) 1009, CC BY 4.0",
                       "https://www.mdpi.com/2075-4701/12/6/1009"),
    "ENGRXIV_HAZ": ("Effects of HAZ softening extent on the strength of AHSS resistance spot welds (U. Tennessee / ArcelorMittal), engrXiv preprint",
                    "https://engrxiv.org/preprint/download/281/721"),
    "HUANG2022_DP980": ("Huang J. et al., Laser-welded DP980, Mater. Res. Express 9 (2022) 126501, CC BY",
                        "https://iopscience.iop.org/article/10.1088/2053-1591/aca5f1"),
    "CHOWDHURY2011_MG": ("Chowdhury S.M. et al., Fiber- and diode-laser-welded AZ31 Mg, Metall. Mater. Trans. A 42 (2011) 1974-1989 (author copy)",
                         "https://uwaterloo.ca/centre-advanced-materials-joining/sites/default/files/uploads/files/mettrans-2011_chowdhury.pdf"),
    "WANG2022_MG": ("Wang S. et al., Laser-arc hybrid welded AZ31B, Metals 12 (2022) 696, CC BY 4.0",
                    "https://www.mdpi.com/2075-4701/12/4/696"),
    "TOLVANEN2024_TI": ("Tolvanen S., Pederson R., Klement U., Ti-6Al-4V welds by different processes, Materials 17 (2024) 782, CC BY 4.0",
                        "https://www.mdpi.com/1996-1944/17/4/782"),
    "ALTAIR_LAW59": ("Altair Radioss reference, /MAT/LAW59 (CONNECT)",
                     "https://help.altair.com/hwsolvers/rad/topics/solvers/rad/mat_law59_connect_starter_r.htm"),
    "ALTAIR_FAILCONNECT": ("Altair Radioss reference, /FAIL/CONNECT",
                           "https://help.altair.com/hwsolvers/rad/topics/solvers/rad/fail_connect_starter_r.htm"),
    "ALTAIR_SPOTWELD": ("Altair Radioss user guide, Spotweld (bolt or adhesive connection)",
                        "https://help.altair.com/hwsolvers/rad/topics/solvers/rad/spotweld_bolt_adhesive_connect_r.htm"),
    "WIKI_GAUGE": ("Wikipedia, Sheet metal - gauge table (Manufacturers' Standard Gauge for sheet steel, after Oberg, Machinery's Handbook p.2502)",
                   "https://en.wikipedia.org/wiki/Sheet_metal#Gauge"),
}

# Manufacturers' Standard Gauge for sheet steel, inches (WIKI_GAUGE).
# Fractions are exact. Used to put a mm thickness on Miller chart columns.
GAUGE_IN = {
    "24 ga": 0.0239, "22 ga": 0.0299, "20 ga": 0.0359, "18 ga": 0.0478,
    "16 ga": 0.0598, "14 ga": 0.0747,
    "1/8 in": 0.125, "3/16 in": 0.1875, "1/4 in": 0.25, "5/16 in": 0.3125, "3/8 in": 0.375,
}

# ---------------------------------------------------------------- MIG (GMAW)
# MILLER211, 240 V input columns. Values are (volts, wire feed speed in/min).
MIG_STEEL = {
    "source": "MILLER211",
    "consumable": "ER70S-6 solid wire, DCEP",
    "gas": "C25 (75% Ar / 25% CO2), 25-35 CFH",
    "wires": {
        '.024"': {"24 ga": (15.0, 145), "22 ga": (15.5, 160), "20 ga": (16.0, 170), "18 ga": (17.8, 325),
                  "16 ga": (20.0, 520), "14 ga": (20.2, 550), "1/8 in": (21.2, 565), "3/16 in": (22.0, 600)},
        '.030"': {"24 ga": (14.2, 98), "22 ga": (14.5, 100), "20 ga": (15.2, 110), "18 ga": (16.2, 145),
                  "16 ga": (17.0, 215), "14 ga": (17.8, 265), "1/8 in": (20.0, 315), "3/16 in": (20.3, 340),
                  "1/4 in": (21.0, 425), "5/16 in": (21.5, 470), "3/8 in": (22.5, 515)},
        '.035"': {"22 ga": (14.8, 75), "20 ga": (15.0, 80), "18 ga": (15.8, 115), "16 ga": (16.5, 140),
                  "14 ga": (17.5, 175), "1/8 in": (19.0, 230), "3/16 in": (20.0, 275), "1/4 in": (20.8, 350),
                  "5/16 in": (21.5, 420), "3/8 in": (22.6, 450)},
    },
}

MIG_ALUMINIUM = {
    "source": "MILLER211",
    "consumable": "aluminium wire with Spoolmate spool gun, DCEP",
    "gas": "100% Argon, 25-45 CFH",
    "wires": {
        'ER4043 .030"': {"18 ga": (13.5, 305), "16 ga": (14.5, 350), "14 ga": (15.5, 420), "1/8 in": (19.8, 500),
                         "3/16 in": (23.0, 580), "1/4 in": (23.0, 600)},
        'ER4043 .035"': {"16 ga": (14.5, 285), "14 ga": (15.5, 340), "1/8 in": (20.5, 420), "3/16 in": (23.5, 510),
                         "1/4 in": (24.0, 560), "5/16 in": (25.0, 580), "3/8 in": (25.0, 600)},
        'ER5356 .030" (Spoolmate 150)': {"18 ga": (13.4, 355), "16 ga": (14.9, 480), "14 ga": (15.5, 515),
                                         "1/8 in": (19.9, 600)},
        'ER5356 .035" (Spoolmate 150)': {"16 ga": (14.5, 400), "14 ga": (15.5, 445), "1/8 in": (20.8, 555),
                                         "3/16 in": (22.2, 600)},
    },
}

# MILLER_RULES rules of thumb (steel, solid wire).
MIG_RULE_AMP_PER_THOU = 1.0          # 1 A per 0.001 in of thickness
MIG_WIRE_AMP_RANGE = {'.023"': (30, 130), '.030"': (40, 145), '.035"': (50, 180), '.045"': (75, 250)}
MIG_WFS_IPM_PER_AMP = {'.023"': 3.5, '.030"': 2.0, '.035"': 1.6, '.045"': 1.0}

# ---------------------------------------------------------------- TIG (GTAW)
# LINCOLN_SQW. Rows: (thickness_in, amp_lo, amp_hi, tungsten_in, filler_in)
TIG_STEEL = {
    "source": "LINCOLN_SQW", "polarity": "DC electrode negative (also listed for stainless)",
    "rows": [(0.024, 25, 35, "1/16", "1/16"), (0.060, 70, 85, "3/32", "1/16"), (0.105, 80, 100, "3/32", "3/32"),
             (0.135, 90, 120, "3/32", "3/32"), (0.1875, 130, 160, "3/32", "1/8")],
}
TIG_ALUMINIUM = {
    "source": "LINCOLN_SQW", "polarity": "AC",
    "rows": [(0.024, 25, 35, "1/16", "1/16"), (0.062, 75, 85, "3/32", "1/16"), (0.090, 85, 110, "3/32", "3/32"),
             (0.125, 120, 135, "3/32", "3/32"), (0.1875, 165, 195, "3/32", "1/8")],
}
TIG_TUNGSTEN_NOTES = {
    "steel": "1.5% lanthanated (gold): good for titanium, nickel, copper, mild and stainless steel (LINCOLN_SQW)",
    "aluminium": "0.8% zirconiated (white): very good for aluminium or magnesium; 2% ceriated/lanthanated also listed for AC (LINCOLN_SQW)",
    "magnesium": "0.8% zirconiated (white): very good for aluminium or magnesium alloys (LINCOLN_SQW). No open amperage table found for Mg.",
    "titanium": "1.5% lanthanated (gold): good choice for titanium (LINCOLN_SQW). No open amperage table found for Ti.",
}

# ---------------------------------------------------------------- Resistance spot (RSW)
# NSRW_LC 'Low Carbon Steel Spot Welding Data Chart - Single Impulse Welding'.
# Two equal sheets, SAE 1005-1010, UTS 42-45 ksi, CMW 3 (RWMA class 2) electrodes.
# Common: (t_in, D_min_in, d_max_in, min_spacing_in, min_overlap_in)
RSW_LC_COMMON = [
    (0.010, 0.5, 0.125, 0.25, 0.375), (0.021, 0.5, 0.1875, 0.375, 0.4375), (0.031, 0.5, 0.1875, 0.5, 0.4375),
    (0.040, 0.625, 0.25, 0.75, 0.5), (0.050, 0.625, 0.25, 0.875, 0.5625), (0.062, 0.625, 0.25, 1.0, 0.625),
    (0.078, 0.625, 0.3125, 1.125, 0.6875), (0.094, 0.625, 0.3125, 1.25, 0.75), (0.109, 0.875, 0.375, 1.3125, 0.8125),
    (0.125, 0.875, 0.375, 1.5, 0.875),
]
# Per class: (weld_time_cycles_60Hz, force_lb, current_A, nugget_dia_in, avg_tensile_shear_lb)
RSW_LC_CLASS = {
    "A": {"tol": 0.14, "rows": [(4, 200, 4000, .13, 235), (6, 300, 6100, .17, 530), (8, 400, 8000, .21, 980),
                                (10, 500, 9200, .23, 1305), (12, 650, 10300, .25, 1820), (14, 800, 11600, .27, 2350),
                                (21, 1100, 13300, .31, 3225), (25, 1300, 14700, .34, 4100), (29, 1600, 16100, .37, 5300),
                                (30, 1800, 17500, .40, 6900)]},
    "B": {"tol": 0.17, "rows": [(5, 130, 3700, .12, 200), (10, 200, 5100, .16, 460), (15, 275, 6300, .20, 850),
                                (21, 360, 7500, .22, 1230), (24, 410, 8000, .23, 1700), (29, 500, 9000, .26, 2150),
                                (36, 650, 10400, .30, 3025), (44, 790, 11400, .33, 3900), (50, 960, 12200, .36, 5050),
                                (60, 1140, 12900, .39, 6500)]},
    "C": {"tol": 0.20, "rows": [(15, 65, 3000, .11, 160), (22, 100, 3800, .14, 390), (29, 135, 4700, .18, 790),
                                (38, 180, 5600, .21, 1180), (42, 205, 6100, .22, 1600), (48, 250, 6800, .25, 2050),
                                (58, 325, 7900, .28, 2900), (66, 390, 8800, .31, 3750), (72, 480, 9500, .35, 4850),
                                (78, 570, 10000, .37, 6150)]},
}
RSW_LC_BASE_UTS_PSI = (42000, 45000)   # NSRW_LC note 1

# AWS_C11 Amendment 1, footnote d: ST[kN] = (-8.83e-7*S^2 + 1.34e-3*S + 1.514) * S * 4 t^1.5 / 1000
AWS_ST_COEFFS = (-8.83e-7, 1.34e-3, 1.514)

# TWI_UHSS: plug diameter normally specified as 4*sqrt(t) mm; 5*sqrt(t) used for UHSS welds in the paper.
NUGGET_FACTOR_MIN = 4.0
# TWI_UHSS: HS steels up to ~600 MPa: electrode force typically 20-50% higher than low-carbon steel.
HSS_FORCE_INCREASE = (0.20, 0.50)
# TWI_UHSS: cross-tension / shear ratio. LC steel 0.70-0.80; ~600 MPa ~0.50; interface failure ~0.30.
CTS_TSS = {"low_carbon": (0.70, 0.80), "around_600MPa": 0.50, "interface_or_uhss": 0.30}

# EAA_RSW: aluminium vs steel spot welding ranges (no thickness schedule given)
RSW_AL_RANGES = {"force_kN": (0.2, 8.0), "current_kA_max": 40, "steel_force_kN": (0.2, 4.0),
                 "steel_current_kA_below": 15, "nugget_mm": (4, 7), "electrode_face_mm": (5.0, 10.0),
                 "face_valid_t_mm": (0.8, 4.0), "coolant_l_min": (5, 10)}

# ---------------------------------------------------------------- Laser / FSW reference points
# Not parameter ranges: single published conditions that produced the quoted joint.
REFERENCE_POINTS = {
    ("steel", "laser"): [{"what": "DP980 1.40 mm butt, fiber laser 4.5 kW, 4.5 m/min, 0.3 mm spot, Ar 15 l/min",
                          "source": "HUANG2022_DP980"}],
    ("magnesium", "laser"): [{"what": "AZ31B-H24 2 mm butt, fiber laser 2 kW, 100 mm/s, He shield (diode: 3 kW, 8.33 mm/s)",
                              "source": "CHOWDHURY2011_MG"},
                             {"what": "AZ31B 7 mm butt, laser-arc hybrid 3.5 kW, 1.8 m/min, 100 A, Ar 25 l/min (best of set)",
                              "source": "WANG2022_MG"}],
    ("aluminium", "fsw"): [{"what": "AA6082-T6 10 mm butt, 400 rpm, 1.5 deg tilt, 0.1 mm plunge, 20 mm shoulder, large-tip pin, 100-500 mm/min",
                            "source": "MA2022_FSW"}],
    ("titanium", "laser"): [{"what": "Ti-6Al-4V 4 mm, parameters 'optimized for 4 mm' not published; PWHT 704 C / 2 h",
                             "source": "TOLVANEN2024_TI"}],
}
PROCESS_NOTES = {
    ("magnesium", "mig"): ("Arc welding of Mg: spatter and poor arc stability because of low boiling point and high "
                           "vapour pressure; no open MIG parameter table found.", "WANG2022_MG"),
}

# ---------------------------------------------------------------- Materials
# uts_mpa only where a cited value exists (used as default for the spot-weld card).
MATERIALS = {
    "mild-steel": {"family": "steel", "desc": "low-carbon steel SAE 1005-1010, UTS 42-45 ksi",
                   "uts_mpa": 290, "uts_src": "NSRW_LC (42 ksi lower bound, note 1)"},
    "dp590": {"family": "steel", "desc": "dual-phase 590, ~16% martensite", "uts_mpa": None, "uts_src": None},
    "dp980": {"family": "steel", "desc": "dual-phase 980", "uts_mpa": 1026,
              "uts_src": "HUANG2022_DP980 (1.40 mm sheet, measured)"},
    "m1700": {"family": "steel", "desc": "fully martensitic 1700", "uts_mpa": None, "uts_src": None},
    "al-6082-t6-extrusion": {"family": "aluminium", "desc": "EN AW-6082-T6 extrusion"},
    "al-6082-t6-sheet": {"family": "aluminium", "desc": "EN AW-6082-T6 sheet/plate"},
    "al-6082-t4": {"family": "aluminium", "desc": "EN AW-6082-T4 extrusion"},
    "al-6061-t6": {"family": "aluminium", "desc": "6061-T6"},
    "al-5754-h14": {"family": "aluminium", "desc": "EN AW-5754-H14 sheet"},
    "al-7020-t6": {"family": "aluminium", "desc": "EN AW-7020-T6 extrusion"},
    "al-o-temper": {"family": "aluminium", "desc": "any alloy in O (annealed) temper"},
    "mg-az31b": {"family": "magnesium", "desc": "AZ31B-H24 sheet"},
    "ti-6al-4v": {"family": "titanium", "desc": "Ti-6Al-4V sheet"},
}

# ---------------------------------------------------------------- HAZ / joint knockdowns
# rho_yield, rho_uts: weld-zone value / base value. None = not reported.
# kind: 'code' (design-code minimum factor), 'joint' (measured cross-weld tensile ratio),
#       'hardness' (min HAZ hardness / base hardness; a proxy, ENGRXIV_HAZ scales flow curves by it).
HAZ = [
    {"metal": "dp590", "process": "spot", "kind": "hardness", "rho_yield": None, "rho_uts": 0.94,
     "note": "6% sub-critical HAZ hardness drop", "source": "ENGRXIV_HAZ"},
    {"metal": "dp980", "process": "spot", "kind": "hardness", "rho_yield": None, "rho_uts": 0.82,
     "note": "18% (about 60 HV) sub-critical HAZ hardness drop", "source": "DP980_GMAW_RSW"},
    {"metal": "dp980", "process": "mig", "kind": "hardness", "rho_yield": None, "rho_uts": 0.46,
     "note": "54% (157 HV) sub-critical HAZ hardness drop in GMAW", "source": "DP980_GMAW_RSW"},
    {"metal": "dp980", "process": "laser", "kind": "joint", "rho_yield": None, "rho_uts": 0.984,
     "note": "joint UTS 1010 vs 1026 MPa, fails in soft HAZ (HAZ hardness 276 vs 305 HV, -10%); elongation 12 -> 8%",
     "source": "HUANG2022_DP980"},
    {"metal": "m1700", "process": "spot", "kind": "hardness", "rho_yield": None, "rho_uts": 0.58,
     "note": "42% sub-critical HAZ hardness drop (100% martensite)", "source": "ENGRXIV_HAZ"},
    {"metal": "al-6082-t6-extrusion", "process": "arc", "kind": "code", "rho_yield": 0.50, "rho_uts": 0.64,
     "note": "EN 1999-1-1 rho_o,haz / rho_u,haz, extruded profile t<5 mm", "source": "EC9_WS"},
    {"metal": "al-6082-t6-sheet", "process": "arc", "kind": "code", "rho_yield": 0.48, "rho_uts": 0.60,
     "note": "EN 1999-1-1, sheet/strip/plate t<5 mm", "source": "EC9_WS"},
    {"metal": "al-6082-t4", "process": "arc", "kind": "code", "rho_yield": 0.91, "rho_uts": 0.78,
     "note": "EN 1999-1-1, extruded profile t<5 mm", "source": "EC9_WS"},
    {"metal": "al-7020-t6", "process": "arc", "kind": "code", "rho_yield": 0.71, "rho_uts": 0.80,
     "note": "EN 1999-1-1, extruded profile t<5 mm", "source": "EC9_WS"},
    {"metal": "al-5754-h14", "process": "arc", "kind": "code", "rho_yield": 0.53, "rho_uts": 0.63,
     "note": "EN 1999-1-1, sheet t<5 mm", "source": "EC9_WS"},
    {"metal": "al-o-temper", "process": "arc", "kind": "code", "rho_yield": 1.00, "rho_uts": 1.00,
     "note": "O/F condition: no HAZ weakening (ENV 1999 table)", "source": "CESTRUCO"},
    {"metal": "al-6061-t6", "process": "arc", "kind": "code", "rho_yield": None, "rho_uts": 0.60,
     "note": "as-welded min 24 ksi (165 MPa) vs ASTM B209 T6 min 40 ksi (275 MPa) as quoted by Lincoln", "source": "LINCOLN_AL"},
    {"metal": "al-6082-t6-extrusion", "process": "fsw", "kind": "joint", "rho_yield": None, "rho_uts": 0.77,
     "note": "10 mm plate; 0.77 (conventional pin, 200 mm/min) to 0.80 (large-tip pin, 500 mm/min)", "source": "MA2022_FSW"},
    {"metal": "mg-az31b", "process": "laser", "kind": "joint", "rho_yield": None, "rho_uts": 0.91,
     "note": "fiber laser, 2 mm AZ31B-H24; diode laser gave 0.59", "source": "CHOWDHURY2011_MG"},
    {"metal": "ti-6al-4v", "process": "tig", "kind": "joint", "rho_yield": 871 / 975, "rho_uts": 958 / 1021,
     "note": "4 mm, filler AMS4954, PWHT 704 C/2 h; YS 871/975, UTS 958/1021 MPa; elongation 16.4 -> 7%",
     "source": "TOLVANEN2024_TI"},
    {"metal": "ti-6al-4v", "process": "laser", "kind": "joint", "rho_yield": 931 / 975, "rho_uts": 995 / 1021,
     "note": "4 mm autogenous, PWHT 704 C/2 h; YS 931/975, UTS 995/1021 MPa; elongation 16.4 -> 10%",
     "source": "TOLVANEN2024_TI"},
]
# 'arc' rows apply to both mig and tig. ENV-era factors show TIG harsher than MIG for 6xxx-T6:
ENV_RHO_HAZ_6XXX_T6 = {"mig": 0.65, "tig": 0.50, "source": "CESTRUCO"}

# HAZ width. EC9 b_haz (ENV table, CESTRUCO) for Al MIG/TIG; other cited widths.
BHAZ_AL_MIG_MM = [(6.0, 20.0), (12.0, 30.0), (25.0, 35.0), (float("inf"), 40.0)]   # (t upper bound, b_haz)
BHAZ_AL_TIG_MM = [(6.0, 30.0)]                                                     # only t<=6 mm listed
HAZ_WIDTH_NOTES = {
    "aluminium": ("ADM 2020: strength reduction typically extends 1 in (25 mm) each side of the weld centreline", "ADM2020"),
    ("dp980", "laser"): ("HAZ width about 0.50 mm", "HUANG2022_DP980"),
    ("ti-6al-4v", "tig"): ("HAZ width 3.2 mm (fusion zone 12.3/7.5 mm top/bottom)", "TOLVANEN2024_TI"),
    ("ti-6al-4v", "laser"): ("HAZ width 1.6 mm (fusion zone 3/1.8 mm)", "TOLVANEN2024_TI"),
}

# ---------------------------------------------------------------- Crash solver card (Radioss format)
# Values copied from the Altair example decks (units Mg, mm, s). They are EXAMPLE values,
# not material data: calibrate against 0 deg, 90 deg, combined and peel coupon tests (ALTAIR_SPOTWELD).
CARD_EXAMPLE = {"E_per_mm": 21000.0, "G_per_mm": 21000.0, "u_max_n_mm": 1.0, "u_max_t_mm": 1.8,
                "source": "ALTAIR_LAW59 / ALTAIR_FAILCONNECT example (Spotweld)"}
STEEL_DENSITY_T_MM3 = 7.85e-9   # 7850 kg/m3, same assumption as research/crush-experiments.md
