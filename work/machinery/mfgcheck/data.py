# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Cited rule data. Every number here was read on the source page in
machinery.md. Units: mm unless a name says otherwise. Do not add a number
without adding its source id."""

IN = 25.4  # mm per inch (exact)

SOURCES = {
    "faa-ac43": ("FAA AC 43.13-1B w/ chg 1, Table 4-6, p. 4-13 (public domain)",
                 "https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf"),
    "united-al": ("United Aluminum, Recommended minimum bend radii for 90-degree cold forming",
                  "https://unitedaluminum.com/wp-content/uploads/techmanual/RecommMinBlendpg10.pdf"),
    "ssab-form04": ("SSAB Form 04 (DC04) data sheet",
                    "https://www.ssab.com/en/brands-and-products/ssab-form-deep-drawing-steel/product-offer/04"),
    "ssab-420la": ("SSAB Docol 420LA data sheet",
                   "https://www.ssab.com/en/brands-and-products/ssab-docol/automotive-steel-grades/hsla-steel/420la"),
    "ssab-600dp": ("SSAB Docol 600DP data sheet",
                   "https://www.ssab.com/en-us/brands-and-products/ssab-docol/automotive-steel-grades/dual-phase-steel/600dp"),
    "ssab-800dp": ("SSAB Docol 800DP data sheet",
                   "https://www.ssab.com/en-us/brands-and-products/ssab-docol/automotive-steel-grades/dual-phase-steel/800dp"),
    "ssab-1000dp": ("SSAB Docol 1000DP data sheet",
                    "https://www.ssab.com/en-us/brands-and-products/ssab-docol/automotive-steel-grades/dual-phase-steel/1000dp"),
    "ahss-shear": ("AHSS Guidelines: Shear fracture (R/t under tension)",
                   "https://ahssinsights.org/forming/formability/shear-fracture/"),
    "ahss-flc": ("AHSS Guidelines: Forming limit curves",
                 "https://ahssinsights.org/forming/formability/forming-limit-curves-flc/"),
    "asp-keeler": ("Keeler, Enhanced Forming Limit Diagram, A/SP report (FLC0 eq., severity zones)",
                   "https://www.a-sp.org/wp-content/uploads/2020/08/Technology-Report-Final.pdf"),
    "protolabs-sheet": ("Protolabs sheet metal design guidelines",
                        "https://www.protolabs.com/services/sheet-metal-fabrication/design-guidelines/"),
    "scs-bending": ("SendCutSend bending guidelines",
                    "https://sendcutsend.com/guidelines/bending/"),
    "hypertherm-holes": ("Hypertherm FAQ: How can I cut better holes?",
                         "https://www.hypertherm.com/resources/faqs/how-can-i-cut-better-holes/"),
    "hypertherm-truehole": ("Hypertherm True Hole technology",
                            "https://www.hypertherm.com/solutions/about-our-products/surecut-technology/true-hole/"),
    "fab-tooling": ("LeTang (Bystronic), The rules of press brake tool selection, The Fabricator 2019",
                    "https://www.thefabricator.com/thefabricator/article/bending/the-rules-of-press-brake-tool-selection"),
    "noramark-tonnage": ("Noramark press brake tonnage calculator (575 t^2/V rule)",
                         "https://www.noramark.com/resources/press-brake-tonnage-calculator/"),
    "xometry-tube": ("Xometry tube bending design tips",
                     "https://www.xometry.com/resources/tube/tube-bending-design-tips/"),
    "protools-wf": ("Pro-Tools: Wall factor and D of bend",
                    "https://pro-tools.com/blogs/protoolsusa/42288387-wall-factor-and-d-of-bend-getting-to-the-center-of-the-centerline-radius-debate"),
    "fab-mandrel": ("The Fabricator: Selecting the right mandrel and wiper (wall factor, D of bend)",
                    "https://www.thefabricator.com/tubepipejournal/article/tubepipefabrication/selecting-the-right-mandrel-and-wiper"),
    "scs-minmax": ("SendCutSend processing min/max (effective bend radius per thickness)",
                   "https://sendcutsend.com/materials/processing-min-max/"),
    "vr3-tube": ("VR3 tube bending guidelines, manual rotary draw (Sept 2026)",
                 "https://vr3.ca/documents/TubeBendingGuidelines.20260916.pdf"),
    "jd2-m32": ("JD Squared Model 32 tube bender",
                "https://www.jd2.com/model-32-bender"),
    "bonnell": ("Bonnell Aluminum: Designing aluminum extrusions",
                "https://bonnellaluminum.com/tech-info-resources/designing-aluminum-extrusions/"),
    "hubs-cnc": ("Protolabs Network (Hubs): How to design parts for CNC machining",
                 "https://www.hubs.com/knowledge-base/how-design-parts-cnc-machining/"),
    "protolabs-cnc": ("Protolabs CNC milling design guidelines",
                      "https://www.protolabs.com/services/cnc-machining/cnc-milling/"),
    "cadem-turning": ("CADEM: CNC lathe work holding thumb rules",
                      "https://cadem.com/cnc-turning-work-holding-thumb-rules/"),
    "shapeoko5pro": ("Carbide 3D Shapeoko 5 Pro specs",
                     "https://carbide3d.com/shapeoko/shapeoko5pro-specs/"),
    "nadca": ("NADCA Product Specification Standards for Die Castings 2009, sec. 4A",
              "https://www.paceind.com/wp-content/uploads/2016/02/NADCA-Tolerances-2009.pdf"),
}

# --- Aluminium sheet, FAA AC 43.13-1B Table 4-6: (low, high) radius in multiples of t.
FAA_THICKNESS_IN = (0.016, 0.032, 0.064, 0.128, 0.182, 0.258)
FAA_AL_BEND_RT = {
    "2024-O":   ((0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)),
    "2024-T3":  ((1.5, 3), (2, 4), (3, 5), (4, 6), (4, 6), (5, 7)),
    "2024-T61": ((2, 4), (3, 5), (3, 5), (4, 6), (5, 7), (6, 10)),
    "5052-O":   ((0, 0), (0, 0), (0, 1), (0, 1), (0, 1), (0, 1)),
    "5052-H32": ((0, 0), (0, 0), (0.5, 1), (0.5, 1.5), (0.5, 1.5), (0.5, 1.5)),
    "5052-H34": ((0, 0), (0, 0), (0.5, 1.5), (1.5, 2.5), (1.5, 2.5), (2, 3)),
    "5052-H36": ((0, 1), (0.5, 1.5), (1, 2), (1.5, 3), (2, 4), (2, 4)),
    "5052-H38": ((0.5, 1.5), (1, 2), (1.5, 3), (2, 4), (3, 5), (4, 6)),
    "6061-O":   ((0, 0), (0, 1), (0, 1), (0, 1), (0, 1), (0, 1)),
    "6061-T4":  ((0, 1), (0, 1), (0.5, 1.5), (1, 2), (1.5, 3), (2.5, 4)),
    "6061-T6":  ((0, 1), (0.5, 1.5), (1, 2), (1.5, 3), (2, 4), (3, 4)),
    "7075-O":   ((0, 0), (0, 1), (0, 1), (0.5, 1.5), (1, 2), (1.5, 3)),
    "7075-T6":  ((2, 4), (3, 5), (4, 6), (5, 7), (5, 7), (6, 10)),
}

# --- Steel sheet (SSAB data sheets). min_rt: minimum inner radius / t for a 90 deg
# free bend; None = not stated by the source. uts: (min, max) MPa. n: minimum n.
# flc_ok: Keeler-Brazier FLC allowed per AHSS Guidelines scope.
STEEL = {
    "DC04":         dict(min_rt=None, uts=(270, 350), n=0.18, flc_ok=True,  dp=False, src="ssab-form04"),
    "HSLA420-HR":   dict(min_rt=0.5,  uts=(480, 600), n=None, flc_ok=True,  dp=False, src="ssab-420la"),
    "HSLA420-CR-GI": dict(min_rt=1.0, uts=(480, 600), n=0.11, flc_ok=True,  dp=False, src="ssab-420la"),
    "DP600-UC":     dict(min_rt=0.0,  uts=(590, 700), n=0.14, flc_ok=True,  dp=True,  src="ssab-600dp"),
    "DP600-GI":     dict(min_rt=1.2,  uts=(590, 700), n=0.14, flc_ok=True,  dp=True,  src="ssab-600dp"),
    "DP800-UC":     dict(min_rt=1.0,  uts=(780, 900), n=0.11, flc_ok=False, dp=True,  src="ssab-800dp"),
    "DP800-GI":     dict(min_rt=1.8,  uts=(780, 900), n=0.11, flc_ok=False, dp=True,  src="ssab-800dp"),
    "DP1000-UC":    dict(min_rt=2.0,  uts=(980, 1130), n=None, flc_ok=False, dp=True, src="ssab-1000dp"),
    "DP1000-GI":    dict(min_rt=3.0,  uts=(980, 1130), n=None, flc_ok=False, dp=True, src="ssab-1000dp"),
}
# AHSS Guidelines (ahss-shear): DP340/590 and above, R/t under tension.
AHSS_RT_EMBOSS = 3.0       # low metal motion features (embossments)
AHSS_RT_UNDER_TENSION = 5.0  # pulled over a radius or through a draw bead

# --- Keeler-Brazier FLC (asp-keeler, ahss-flc)
KEELER_A, KEELER_B, KEELER_NREF = 23.3, 14.2, 0.21
FLC_RIGHT_SLOPE = 0.6        # right side slope, valid to 20 % minor strain
FLC_RIGHT_MAX_MINOR = 20.0
FLC_YELLOW_BAND = 10.0       # yellow zone starts at FLC0 - 10 % (A/SP Step 7)

# --- Sheet features (protolabs-sheet, scs-bending, hypertherm-*)
HOLE_MIN_D_OVER_T = {"fabricated": 1.0, "punch": 1.0, "laser": 0.5, "plasma": 1.0}
HOLE_MIN_D_SRC = {"fabricated": "protolabs-sheet", "punch": "protolabs-sheet",
                  "laser": "scs-bending", "plasma": "hypertherm-holes"}
HOLE_EDGE_T_SPLIT = 0.036 * IN       # 0.914 mm
HOLE_EDGE_MIN_THIN = 0.062 * IN      # 1.575 mm
HOLE_EDGE_MIN_THICK = 0.125 * IN     # 3.175 mm
FEATURE_BEND_RISK_T = 4.0            # features within 4 t of a bend deform (Protolabs)
DESIGNER_FEATURE_BEND_T = 6.0        # Bystronic designer rule (fab-tooling)
DESIGNER_RADIUS_T = 1.5              # Bystronic designer rule (fab-tooling)
MIN_FLANGE_T = 4.0                   # Protolabs

# --- Press brake (fab-tooling, noramark-tonnage)
V_DIE_RULE_T = 8.0
V_DIE_MIN_T = 5.0
AIR_BEND_RADIUS_FRAC_V = 0.16        # mild steel
MIN_FLANGE_FRAC_V = 0.77
TONNAGE_METRIC_K = 67.4              # metric t per metre = K t^2 / V (414 MPa steel)
TONNAGE_REF_UTS = 414.0

# --- Tube (xometry-tube, protools-wf, vr3-tube, jd2-m32)
TUBE_MIN_D_PRODUCTION = 2.0
TUBE_MIN_D_NO_MANDREL = 3.0
TUBE_MIN_STRAIGHT_MANUAL = 3.0 * IN  # 76.2 mm, low end of VR3 3.0-5.0 in
JD2_M32 = dict(od_min=0.5 * IN, od_max=2.5 * IN, rated_od=2.0 * IN, rated_wall=0.250 * IN,
               manual_od=2.0 * IN, manual_wall=0.120 * IN)

# --- Extrusion (bonnell): (ccd_lo_in, ccd_hi_in, solid_semihollow_in, class2_hollow_in)
BONNELL_MIN_WALL = (
    (0.5, 2, 0.040, 0.055), (2, 3, 0.045, 0.062), (3, 4, 0.050, 0.078),
    (4, 5, 0.062, 0.094), (5, 6, 0.078, 0.110), (6, 7, 0.094, 0.125),
    (7, 8, 0.110, 0.140), (8, 9, 0.125, 0.156), (9, 10, 0.140, 0.188),
    (10, 11, 0.156, 0.204), (11, 12, 0.172, 0.220), (12, 13, 0.188, 0.236),
)
EXTRUSION_MAX_ADJ_WALL_RATIO = 2.0

# --- CNC (hubs-cnc, protolabs-cnc, cadem-turning, shapeoko5pro)
CNC_WALL = {"metal": (0.8, 0.5), "plastic": (1.5, 1.0)}  # (recommended, feasible)
CNC_HOLE_DEPTH_D = (4.0, 10.0, 40.0)   # recommended, typical, feasible
CNC_HOLE_MIN_D_REC = 2.5
CNC_HOLE_MIN_D_FEASIBLE = 1.0          # "any diameter larger than 1 mm"
CNC_CAVITY_DEPTH_W = 4.0
CNC_CORNER_R_FRAC_DEPTH = 1.0 / 3.0
CNC_TOL_TYPICAL, CNC_TOL_FEASIBLE = 0.1, 0.02
SHAPEOKO5PRO_ACCURACY = 0.050          # +/- mm per 300 mm (ballscrew)

# --- Die casting (nadca), metric C constants
NADCA_C = {"aluminum": {"inside": 6.0, "outside": 12.0},
           "magnesium": {"inside": 7.0, "outside": 14.0}}
NADCA_K = 57.2738
NADCA_WALL_TYPICAL = (1.016, 5.08)
NADCA_WALL_MIN_CONSULT = 0.50
NADCA_WALL_RANGE_RATIO = 2.0
NADCA_FILLET_MIN = 1.5
NADCA_CORNER_MIN = 0.5
NADCA_CORE_MIN_D = 6.0
NADCA_CORE_LD = ((12.5, 4.0), (float("inf"), 10.0))
