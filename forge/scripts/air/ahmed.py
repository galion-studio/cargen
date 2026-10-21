# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Published Ahmed-body force coefficients (experiments and reference CFD), with sources.

Reference area A = 0.112 m^2 (frontal area of the 1044 mm Ahmed body; Meile et al. 2011,
AhmedML paper). Values are copied as printed by the cited source; nothing digitised from plots.

Sources
  AHMED1984  Ahmed, Ramm & Faltin (1984), SAE 840300, doi:10.4271/840300, Re_L = 4.29e6.
             Values as quoted in GUIL2018 Tables 4/6 (Cd 25 deg = 0.285, 35 deg = 0.258) and in
             GANT Table 7.4 (25 deg breakdown). Primary paper is paywalled (not read directly).
  MEILE2011  Meile, Brenn, Reppenhagen, Lechner, Fuchs (2011), CFD Letters 3(1):32-39, Fig. 4,
             Re_L = 2.78e6 (40 m/s), stilt tare loads subtracted.
             https://www.akademiabaru.com/submit/index.php/cfdl/article/view/3333
  THACKER2012 Thacker, Aubrun, Leroy, Devinant (2012), JWEIA 107-108:237-243, as quoted in GUIL2018 Table 6.
  GUIL2018   Guilmineau et al. (2018), Computers & Fluids 176:302-319, doi:10.1016/j.compfluid.2017.01.005,
             accepted manuscript CC BY 4.0: https://hal.science/hal-02391167v1 . ISIS-CFD, Re_H = 7.68e5.
  GANT       S. Gant, PhD thesis (UMIST), ch. 7 "Ahmed Body Flow", Table 7.3/7.4.
             https://www.gant.org.uk/research/THESIS/ahmed.pdf
  AHMEDML    Ashton et al. (2024), arXiv:2407.20801, Table 1 (OpenFOAM v2212 SA-DDES, baseline 25 deg,
             no stilts), dataset CC-BY-SA-4.0.

Experimental scatter is large at 25 deg (0.285 to 0.384 across three experiments); a CFD
result can only be called validated against a named experiment at matching Re and set-up.
"""

# kind: "exp" or "cfd". model only for cfd. cl None where the source gives n.a.
RECORDS = [
    # 25 deg
    dict(slant=25, kind="exp", source="AHMED1984", cd=0.285, cl=None, re_l=4.29e6),
    dict(slant=25, kind="exp", source="MEILE2011", cd=0.299, cl=0.345, re_l=2.78e6),
    dict(slant=25, kind="exp", source="THACKER2012", cd=0.384, cl=0.422, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="GUIL2018", model="k-omega SST", cd=0.3218, cl=0.1724, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="GUIL2018", model="EARSM", cd=0.2804, cl=0.0083, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="GUIL2018", model="DES", cd=0.4371, cl=0.3747, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="GUIL2018", model="IDDES", cd=0.3802, cl=0.3306, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="MEILE2011", model="RSM (Fluent 6.3)", cd=0.295, cl=0.387, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="AHMEDML", model="SA-DDES fine 21.3M", cd=0.285, cl=0.343, re_l=2.78e6),
    dict(slant=25, kind="cfd", source="AHMEDML", model="SA-DDES extra-fine 31.5M", cd=0.280, cl=0.344, re_l=2.78e6),
    # 35 deg
    dict(slant=35, kind="exp", source="AHMED1984", cd=0.258, cl=None, re_l=4.29e6),
    dict(slant=35, kind="exp", source="MEILE2011", cd=0.279, cl=0.004, re_l=2.78e6),
    dict(slant=35, kind="cfd", source="GUIL2018", model="k-omega SST", cd=0.2999, cl=0.0052, re_l=2.78e6),
    dict(slant=35, kind="cfd", source="GUIL2018", model="EARSM", cd=0.2603, cl=-0.0388, re_l=2.78e6),
    dict(slant=35, kind="cfd", source="GUIL2018", model="DES", cd=0.3156, cl=-0.0145, re_l=2.78e6),
    dict(slant=35, kind="cfd", source="GUIL2018", model="IDDES", cd=0.3452, cl=-0.0145, re_l=2.78e6),
    dict(slant=35, kind="cfd", source="MEILE2011", model="RSM (Fluent 6.3)", cd=0.276, cl=0.013, re_l=2.78e6),
]

# Ahmed et al. 1984 25-deg drag breakdown as tabulated by GANT Table 7.4 (pressure on nose,
# slant, base; friction obtained by Ahmed as total minus pressure parts).
AHMED1984_25_BREAKDOWN = {"nose": 0.020, "slant": 0.140, "base": 0.070, "friction": 0.055}

A_REF = 0.112  # m^2


def lookup(slant, kind="exp", source=None, model=None):
    """Return matching records (list of dicts). slant must be 25 or 35."""
    if slant not in (25, 35):
        raise ValueError("only 25 and 35 deg slants are tabulated")
    out = [r for r in RECORDS if r["slant"] == slant and r["kind"] == kind]
    if source:
        out = [r for r in out if r["source"] == source]
    if model:
        out = [r for r in out if r.get("model") == model]
    return out


def cd_exp(slant, source="MEILE2011"):
    """Single experimental Cd. Default MEILE2011: same Re (2.78e6) as Lienhart & Becker and AhmedML."""
    r = lookup(slant, "exp", source)
    if not r:
        raise KeyError((slant, source))
    return r[0]["cd"]


def cd_error(cd_cfd, slant, source="MEILE2011"):
    """Relative error of a CFD Cd against a named experiment."""
    ref = cd_exp(slant, source)
    return (cd_cfd - ref) / ref
