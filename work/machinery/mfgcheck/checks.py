# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Rule checks. Input: a plain dict describing one part (see README.md).
Output: a list of Finding objects, each with cited sources and a suggestion."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from . import data as D

ERROR, WARNING, INFO = "error", "warning", "info"


@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    value: Optional[float] = None
    limit: Optional[float] = None
    suggestion: dict = field(default_factory=dict)
    sources: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": self.rule, "severity": self.severity, "message": self.message,
            "value": self.value, "limit": self.limit, "suggestion": self.suggestion,
            "sources": [{"id": s, "title": D.SOURCES[s][0], "url": D.SOURCES[s][1]}
                        for s in self.sources],
        }


def _up(x: float, step: float = 0.1) -> float:
    """Round up to the next step (suggestions must not undershoot a limit)."""
    return round(math.ceil(x / step - 1e-9) * step, 6)


def _down(x: float, step: float = 0.1) -> float:
    return round(math.floor(x / step + 1e-9) * step, 6)


# ---------------------------------------------------------------- FLC (steel)
def flc0_keeler(t_mm: float, n: float) -> float:
    """Keeler-Brazier FLC0, engineering major strain in % (asp-keeler)."""
    if t_mm <= 0 or n <= 0:
        raise ValueError("thickness and n must be positive")
    return (D.KEELER_A + D.KEELER_B * t_mm) * n / D.KEELER_NREF


def flc_major_limit(flc0: float, minor_pct: float) -> float:
    """Allowable engineering major strain (%) at a given engineering minor strain.
    Left side: constant thinning in true strain. Right side: slope +0.6 (ahss-flc)."""
    if minor_pct >= 0:
        return flc0 + D.FLC_RIGHT_SLOPE * minor_pct
    if minor_pct <= -100:
        raise ValueError("minor strain must be > -100 %")
    return ((1 + flc0 / 100.0) / (1 + minor_pct / 100.0) - 1) * 100.0


# ---------------------------------------------------------------- sheet
def _al_bend_range(material: str, t_mm: float):
    rows = D.FAA_AL_BEND_RT.get(material)
    if rows is None:
        return None
    t_in = t_mm / D.IN
    for i, col in enumerate(D.FAA_THICKNESS_IN):
        if t_in <= col + 1e-9:
            return rows[i][0], rows[i][1], col, False
    return rows[-1][0], rows[-1][1], D.FAA_THICKNESS_IN[-1], True


def _check_sheet(p: dict) -> list:
    out = []
    t = float(p["thickness_mm"])
    mat = p.get("material", "")
    process = p.get("process", "fabricated")
    steel = D.STEEL.get(mat)
    al = mat in D.FAA_AL_BEND_RT
    if not steel and not al:
        out.append(Finding("material.unknown", INFO,
                           f"No cited bend or FLC data for material '{mat}'. Known: "
                           f"{sorted(D.FAA_AL_BEND_RT) + sorted(D.STEEL)}. Geometry rules still apply."))
    V = p.get("die_opening_mm")
    for i, b in enumerate(p.get("bends", [])):
        r = float(b["inside_radius_mm"])
        rt = r / t
        ctx = b.get("context", "free")
        if al:
            lo, hi, col, beyond = _al_bend_range(mat, t)
            if beyond:
                out.append(Finding("sheet.bend.al.table_range", WARNING,
                                   f"bend {i}: t = {t} mm is thicker than the FAA table (0.258 in); "
                                   "the last column is used as a lower bound.", t, D.FAA_THICKNESS_IN[-1] * D.IN,
                                   sources=["faa-ac43"]))
            if rt < lo - 1e-9:
                out.append(Finding("sheet.bend.al.min_radius", ERROR,
                                   f"bend {i}: R/t = {rt:.2f} is below the FAA minimum {lo}t for {mat} "
                                   f"(table column {col} in). Expect cracking.", rt, lo,
                                   {"inside_radius_mm": _up(max(lo, hi) * t)}, ["faa-ac43", "united-al"]))
            elif rt < hi - 1e-9:
                out.append(Finding("sheet.bend.al.marginal_radius", WARNING,
                                   f"bend {i}: R/t = {rt:.2f} is inside the FAA range {lo}-{hi}t for {mat}; "
                                   "do a test bend, bend across the grain, or use the high end.", rt, hi,
                                   {"inside_radius_mm": _up(hi * t)}, ["faa-ac43"]))
        elif steel:
            min_rt = steel["min_rt"]
            srcs = [steel["src"]]
            if steel["dp"] and ctx in ("emboss", "tension"):
                need = D.AHSS_RT_EMBOSS if ctx == "emboss" else D.AHSS_RT_UNDER_TENSION
                min_rt = max(min_rt or 0.0, need)
                srcs.append("ahss-shear")
            if min_rt is None:
                if rt < D.DESIGNER_RADIUS_T - 1e-9:
                    out.append(Finding("sheet.bend.designer_radius", WARNING,
                                       f"bend {i}: R/t = {rt:.2f}; no mill minimum is published for {mat}. "
                                       f"Designer rule is {D.DESIGNER_RADIUS_T}t.", rt, D.DESIGNER_RADIUS_T,
                                       {"inside_radius_mm": _up(D.DESIGNER_RADIUS_T * t)}, ["fab-tooling"]))
            elif rt < min_rt - 1e-9:
                out.append(Finding("sheet.bend.steel.min_radius", ERROR,
                                   f"bend {i}: R/t = {rt:.2f} is below the minimum {min_rt}t for {mat}"
                                   f" (context: {ctx}).", rt, min_rt,
                                   {"inside_radius_mm": _up(min_rt * t)}, srcs))
            if steel["dp"] and ctx == "free":
                out.append(Finding("sheet.bend.ahss_tension_note", INFO,
                                   f"bend {i}: {mat} free-bend minimum used. If this radius is a stamping die "
                                   f"radius (sheet pulled over it), the limit rises to >= {D.AHSS_RT_UNDER_TENSION}t; "
                                   "set context='tension'.", rt, D.AHSS_RT_UNDER_TENSION, sources=["ahss-shear"]))
        if V and mat == "DC04":
            r_pred = D.AIR_BEND_RADIUS_FRAC_V * V
            out.append(Finding("pressbrake.predicted_radius", INFO,
                               f"bend {i}: air bending mild steel over V = {V} mm gives R about {r_pred:.2f} mm "
                               f"(designed {r} mm). To hit the design radius use V about {r / D.AIR_BEND_RADIUS_FRAC_V:.1f} mm "
                               f"(not below {D.V_DIE_MIN_T}t = {D.V_DIE_MIN_T * t:.1f} mm).", r_pred, None,
                               {"die_opening_mm": _up(max(r / D.AIR_BEND_RADIUS_FRAC_V, D.V_DIE_MIN_T * t))},
                               ["fab-tooling"]))
        fl = b.get("flange_mm")
        if fl is not None:
            fl = float(fl)
            if fl < D.MIN_FLANGE_T * t - 1e-9:
                out.append(Finding("sheet.flange.min", ERROR,
                                   f"bend {i}: flange {fl} mm < {D.MIN_FLANGE_T}t = {D.MIN_FLANGE_T * t:.2f} mm.",
                                   fl, D.MIN_FLANGE_T * t, {"flange_mm": _up(D.MIN_FLANGE_T * t)},
                                   ["protolabs-sheet"]))
            if V and fl < D.MIN_FLANGE_FRAC_V * V - 1e-9:
                v_fit = fl / D.MIN_FLANGE_FRAC_V
                sug = {"flange_mm": _up(D.MIN_FLANGE_FRAC_V * V)}
                if v_fit >= D.V_DIE_MIN_T * t:
                    sug["die_opening_mm"] = _down(v_fit)
                out.append(Finding("pressbrake.flange_vs_die", ERROR,
                                   f"bend {i}: flange {fl} mm < 0.77 x V = {D.MIN_FLANGE_FRAC_V * V:.2f} mm; the "
                                   "flange cannot sit across the die.", fl, D.MIN_FLANGE_FRAC_V * V, sug,
                                   ["fab-tooling"]))
    # holes
    k = D.HOLE_MIN_D_OVER_T.get(process)
    if k is None:
        raise ValueError(f"unknown sheet process '{process}'")
    edge_min = D.HOLE_EDGE_MIN_THIN if t <= D.HOLE_EDGE_T_SPLIT else D.HOLE_EDGE_MIN_THICK
    for i, h in enumerate(p.get("holes", [])):
        d = float(h["diameter_mm"])
        if d < k * t - 1e-9:
            out.append(Finding("sheet.hole.min_diameter", ERROR,
                               f"hole {i}: diameter {d} mm < {k}t = {k * t:.2f} mm for process '{process}'.",
                               d, k * t, {"diameter_mm": _up(k * t)}, [D.HOLE_MIN_D_SRC[process]]))
        if process == "plasma" and steel and t <= 25.0 and 1.0 <= d / t <= 2.0:
            out.append(Finding("sheet.hole.plasma_truehole", INFO,
                               f"hole {i}: D/t = {d / t:.2f} is in the True Hole window (1:1 to 2:1, mild "
                               "steel <= 25 mm) on XPR/HPRXD systems; a hobby plasma will show taper.",
                               d / t, None, sources=["hypertherm-truehole"]))
        e = h.get("edge_distance_mm")
        if e is not None and float(e) < edge_min - 1e-9:
            out.append(Finding("sheet.hole.edge_distance", ERROR,
                               f"hole {i}: hole-to-edge {e} mm < {edge_min:.3f} mm (t = {t} mm); it will distort.",
                               float(e), edge_min, {"edge_distance_mm": _up(edge_min)}, ["protolabs-sheet"]))
        bd = h.get("bend_distance_mm")
        if bd is not None:
            bd = float(bd)
            if bd < D.FEATURE_BEND_RISK_T * t - 1e-9:
                out.append(Finding("sheet.hole.near_bend", WARNING,
                                   f"hole {i}: {bd} mm from a bend (< 4t = {4 * t:.2f} mm); the hole will stretch. "
                                   "Move it, add a relief cut, or cut it after bending.", bd, 4 * t,
                                   {"bend_distance_mm": _up(D.FEATURE_BEND_RISK_T * t)}, ["protolabs-sheet"]))
            elif bd < D.DESIGNER_FEATURE_BEND_T * t - 1e-9:
                out.append(Finding("sheet.hole.designer_bend_distance", INFO,
                                   f"hole {i}: {bd} mm from a bend; designer rule is 6t = {6 * t:.2f} mm.", bd, 6 * t,
                                   {"bend_distance_mm": _up(D.DESIGNER_FEATURE_BEND_T * t)}, ["fab-tooling"]))
    # press brake die and tonnage
    if V:
        V = float(V)
        if V < D.V_DIE_MIN_T * t - 1e-9:
            out.append(Finding("pressbrake.die_min", ERROR,
                               f"V-die {V} mm < 5t = {5 * t:.2f} mm: poor angle accuracy and risk to machine and "
                               "tooling.", V, 5 * t, {"die_opening_mm": _up(D.V_DIE_RULE_T * t)}, ["fab-tooling"]))
    L = p.get("bend_length_mm")
    cap = p.get("press_capacity_t")
    if L and cap:
        uts = p.get("uts_mpa") or (steel["uts"][1] if steel else None)
        if uts is None:
            out.append(Finding("pressbrake.tonnage.no_uts", INFO,
                               "Tonnage not checked: give uts_mpa (no cited UTS for this material in the tool).",
                               sources=["noramark-tonnage"]))
        else:
            Vt = V or D.V_DIE_RULE_T * t
            force = D.TONNAGE_METRIC_K * t * t / Vt * (uts / D.TONNAGE_REF_UTS) * (float(L) / 1000.0)
            if force > float(cap):
                v_need = D.TONNAGE_METRIC_K * t * t * (uts / D.TONNAGE_REF_UTS) * (float(L) / 1000.0) / float(cap)
                out.append(Finding("pressbrake.tonnage", ERROR,
                                   f"Estimated air-bend force {force:.1f} t (V = {Vt:.1f} mm, UTS {uts} MPa, "
                                   f"L = {L} mm) exceeds press capacity {cap} t. Estimate only (+/-10 %).",
                                   round(force, 2), float(cap),
                                   {"die_opening_mm": _up(v_need),
                                    "bend_length_mm": _down(float(L) * float(cap) / force, 1.0)},
                                   ["noramark-tonnage"]))
            else:
                out.append(Finding("pressbrake.tonnage.ok", INFO,
                                   f"Estimated air-bend force {force:.1f} t <= capacity {cap} t (estimate).",
                                   round(force, 2), float(cap), sources=["noramark-tonnage"]))
    # forming limit
    pts = p.get("strain_points", [])
    if pts:
        if not steel or not steel["flc_ok"]:
            out.append(Finding("flc.not_applicable", WARNING,
                               f"Keeler-Brazier FLC is not valid for '{mat}'; strains NOT checked. A measured FLC "
                               "(ISO 12004 / ASTM E2218) is needed.", sources=["ahss-flc"]))
        else:
            n = p.get("n_value") or steel["n"]
            if n is None:
                out.append(Finding("flc.no_n", WARNING, "No n-value given or cited; strains NOT checked.",
                                   sources=["asp-keeler"]))
            else:
                f0 = flc0_keeler(t, float(n))
                for i, s in enumerate(pts):
                    e1, e2 = float(s["major_pct"]), float(s["minor_pct"])
                    lim = flc_major_limit(f0, e2)
                    margin = lim - e1
                    srcs = ["asp-keeler", "ahss-flc"]
                    if e2 > D.FLC_RIGHT_MAX_MINOR:
                        out.append(Finding("flc.extrapolated", WARNING,
                                           f"strain {i}: minor {e2} % > 20 %; right-side slope is only stated to 20 %.",
                                           e2, D.FLC_RIGHT_MAX_MINOR, sources=["ahss-flc"]))
                    sug = {"major_pct": _down(lim - D.FLC_YELLOW_BAND)}
                    if margin < 0:
                        out.append(Finding("flc.above", ERROR,
                                           f"strain {i}: major {e1} % is above the FLC ({lim:.1f} % at minor {e2} %; "
                                           f"FLC0 {f0:.1f} %, n {n}, t {t} mm). Necking expected.",
                                           e1, round(lim, 2), sug, srcs))
                    elif margin < D.FLC_YELLOW_BAND:
                        out.append(Finding("flc.marginal", WARNING,
                                           f"strain {i}: safety margin {margin:.1f} % < 10 % (A/SP yellow zone).",
                                           e1, round(lim - D.FLC_YELLOW_BAND, 2), sug, srcs))
    return out


# ---------------------------------------------------------------- tube
def _check_tube(p: dict) -> list:
    out = []
    od, wall = float(p["od_mm"]), float(p["wall_mm"])
    if wall <= 0 or wall * 2 >= od:
        raise ValueError("wall must be > 0 and < OD/2")
    wf = od / wall
    mandrel = bool(p.get("mandrel", False))
    for i, b in enumerate(p.get("bends", [])):
        clr = float(b["clr_mm"])
        dob = clr / od
        out.append(Finding("tube.ratios", INFO,
                           f"bend {i}: wall factor {wf:.1f}, D of bend {dob:.2f}. Use a mandrel-wiper chart; higher "
                           "WF and lower D need more support.", dob, None, sources=["fab-mandrel", "protools-wf"]))
        whole = max(D.TUBE_MIN_D_PRODUCTION, math.ceil(dob - 1e-9))
        if dob < D.TUBE_MIN_D_PRODUCTION - 1e-9:
            out.append(Finding("tube.clr.production_min", ERROR,
                               f"bend {i}: CLR {clr} mm = {dob:.2f} x OD < 2 x OD; needs special tooling.",
                               dob, D.TUBE_MIN_D_PRODUCTION, {"clr_mm": _up(whole * od)}, ["xometry-tube"]))
        if not mandrel and dob < D.TUBE_MIN_D_NO_MANDREL - 1e-9:
            out.append(Finding("tube.clr.no_mandrel", WARNING,
                               f"bend {i}: CLR {dob:.2f} x OD < 3 x OD without a mandrel (rule of thumb); expect "
                               "wrinkling or ovality.", dob, D.TUBE_MIN_D_NO_MANDREL,
                               {"clr_mm": _up(D.TUBE_MIN_D_NO_MANDREL * od), "mandrel": True}, ["protools-wf"]))
        if dob >= D.TUBE_MIN_D_PRODUCTION and abs(dob - round(dob)) > 1e-6:
            out.append(Finding("tube.clr.whole_multiple", INFO,
                               f"bend {i}: CLR is not a whole multiple of OD; standard dies are (custom tooling cost). "
                               "Suggestion rounds up to the next multiple.",
                               dob, None, {"clr_mm": round(whole * od, 3)}, ["xometry-tube"]))
    for i, s in enumerate(p.get("straights_mm", [])):
        if float(s) < D.TUBE_MIN_STRAIGHT_MANUAL - 1e-9:
            out.append(Finding("tube.straight.min", WARNING,
                               f"straight {i}: {s} mm < 76.2 mm (3 in), the low end of manual rotary-draw "
                               "requirements between bends and at the ends.", float(s), D.TUBE_MIN_STRAIGHT_MANUAL,
                               {"straight_mm": _up(D.TUBE_MIN_STRAIGHT_MANUAL)}, ["vr3-tube"]))
    if p.get("bender") == "jd2_model32":
        j = D.JD2_M32
        if not (j["od_min"] - 1e-9 <= od <= j["od_max"] + 1e-9):
            out.append(Finding("tube.bender.od_range", ERROR,
                               f"OD {od} mm is outside the JD2 Model 32 round range 12.7-63.5 mm.", od, j["od_max"],
                               sources=["jd2-m32"]))
        elif od <= j["rated_od"] + 1e-9 and wall > j["rated_wall"] + 1e-9:
            out.append(Finding("tube.bender.wall_rating", ERROR,
                               f"wall {wall} mm exceeds the rated 2 in x 0.250 in DOM capacity.", wall, j["rated_wall"],
                               {"wall_mm": round(j["rated_wall"], 2)}, ["jd2-m32"]))
        elif od > j["rated_od"] + 1e-9:
            out.append(Finding("tube.bender.unrated", WARNING,
                               f"OD {od} mm > 2 in: bendable but no wall rating is published above 2 in.", od,
                               j["rated_od"], sources=["jd2-m32"]))
        if not p.get("hydraulic", False) and (od > j["manual_od"] + 1e-9 or
                                              (od >= j["manual_od"] - 1e-9 and wall > j["manual_wall"] + 1e-9)):
            out.append(Finding("tube.bender.needs_hydraulic", ERROR,
                               "Round tube over 2 in OD x 0.120 in wall needs the hydraulic Model 32.", wall,
                               j["manual_wall"], {"hydraulic": True}, ["jd2-m32"]))
    return out


# ---------------------------------------------------------------- extrusion
def _check_extrusion(p: dict) -> list:
    out = []
    alloy = str(p.get("alloy", ""))
    ccd_in = float(p["ccd_mm"]) / D.IN
    walls = [float(w) for w in p["walls_mm"]]
    hc = p.get("hollow_class")
    if not alloy.startswith("6"):
        out.append(Finding("extrusion.alloy_scope", INFO, f"Wall chart is for 6000-series alloys; '{alloy}' "
                           "is outside its scope.", sources=["bonnell"]))
    row = next((r for r in D.BONNELL_MIN_WALL if r[0] <= ccd_in < r[1]), None)
    if row is None:
        sev = WARNING if ccd_in >= 13 else INFO
        out.append(Finding("extrusion.ccd_range", sev,
                           f"CCD {ccd_in:.2f} in is outside the chart (0.5-13 in); above 13 in is subject to "
                           "inquiry.", ccd_in, 13.0, sources=["bonnell"]))
    else:
        col = 2 if hc is None else 3
        wmin = row[col] * D.IN
        sev = ERROR if hc in (None, 2) else WARNING
        if hc in (1, 3):
            out.append(Finding("extrusion.hollow_class", WARNING,
                               f"Class {hc} hollow: chart lists only Class 2 hollows; its column is used as a "
                               "reference. Multi-void (Class 3) needs extruder review.", sources=["bonnell"]))
        if min(walls) < wmin - 1e-9:
            out.append(Finding("extrusion.min_wall", sev,
                               f"thinnest wall {min(walls)} mm < {wmin:.2f} mm for CCD {row[0]}-{row[1]} in "
                               f"({'solid/semihollow' if hc is None else 'hollow'}).", min(walls), round(wmin, 3),
                               {"min_wall_mm": _up(wmin)}, ["bonnell"]))
    ratio = max(walls) / min(walls)
    if ratio > D.EXTRUSION_MAX_ADJ_WALL_RATIO + 1e-9:
        out.append(Finding("extrusion.wall_ratio", WARNING,
                           f"wall ratio {ratio:.2f} > 2:1; uneven flow and cooling. Use rounded transitions.",
                           ratio, 2.0, {"min_wall_mm": _up(max(walls) / 2)}, ["bonnell"]))
    return out


# ---------------------------------------------------------------- casting
def _check_casting(p: dict) -> list:
    out = []
    alloy = p["alloy"]
    if alloy not in D.NADCA_C:
        raise ValueError(f"casting alloy must be one of {sorted(D.NADCA_C)}")
    walls = [float(w) for w in p.get("walls_mm", [])]
    lo, hi = D.NADCA_WALL_TYPICAL
    for i, w in enumerate(walls):
        if w < D.NADCA_WALL_MIN_CONSULT - 1e-9:
            out.append(Finding("casting.wall.min", ERROR, f"wall {i}: {w} mm < 0.50 mm.", w,
                               D.NADCA_WALL_MIN_CONSULT, {"wall_mm": lo}, ["nadca"]))
        elif w < lo - 1e-9:
            out.append(Finding("casting.wall.thin", WARNING,
                               f"wall {i}: {w} mm below the typical {lo}-{hi} mm; only small castings, with "
                               "die-caster consultation.", w, lo, {"wall_mm": lo}, ["nadca"]))
        elif w > hi + 1e-9:
            out.append(Finding("casting.wall.thick", WARNING,
                               f"wall {i}: {w} mm above the typical {hi} mm (porosity, cycle time).", w, hi,
                               {"wall_mm": hi}, ["nadca"]))
    if walls and max(walls) / min(walls) > D.NADCA_WALL_RANGE_RATIO + 1e-9:
        out.append(Finding("casting.wall.range", WARNING,
                           f"wall range {max(walls) / min(walls):.2f}x > 2x the thinnest wall.",
                           max(walls) / min(walls), 2.0, {"max_wall_mm": _down(2 * min(walls))}, ["nadca"]))
    for i, f in enumerate(p.get("features", [])):
        side = f.get("side", "inside")
        L = float(f["depth_mm"])
        need = D.NADCA_K / (D.NADCA_C[alloy][side] * math.sqrt(L))
        if float(f["draft_deg"]) < need - 1e-9:
            out.append(Finding("casting.draft", ERROR,
                               f"feature {i}: {side} draft {f['draft_deg']} deg < {need:.2f} deg needed at depth "
                               f"{L} mm ({alloy}).", float(f["draft_deg"]), round(need, 3),
                               {"draft_deg": _up(need)}, ["nadca"]))
    fr = p.get("fillet_radius_mm")
    if fr is not None and float(fr) < D.NADCA_FILLET_MIN - 1e-9:
        out.append(Finding("casting.fillet", WARNING, f"fillet {fr} mm < 1.5 mm minimum (large castings).",
                           float(fr), D.NADCA_FILLET_MIN, {"fillet_radius_mm": D.NADCA_FILLET_MIN}, ["nadca"]))
    cr = p.get("corner_radius_mm")
    if cr is not None and float(cr) < D.NADCA_CORNER_MIN - 1e-9:
        out.append(Finding("casting.corner", WARNING, f"corner radius {cr} mm < 0.5 mm minimum.",
                           float(cr), D.NADCA_CORNER_MIN, {"corner_radius_mm": D.NADCA_CORNER_MIN}, ["nadca"]))
    for i, h in enumerate(p.get("cored_holes", [])):
        d, l = float(h["diameter_mm"]), float(h["length_mm"])
        if d < D.NADCA_CORE_MIN_D - 1e-9:
            out.append(Finding("casting.core.min_d", WARNING,
                               f"cored hole {i}: {d} mm < 6 mm; cast a 6 mm core or drill after casting.", d,
                               D.NADCA_CORE_MIN_D, {"diameter_mm": D.NADCA_CORE_MIN_D}, ["nadca"]))
        max_ld = D.NADCA_CORE_LD[0][1] if d < D.NADCA_CORE_LD[0][0] else D.NADCA_CORE_LD[1][1]
        if l / d > max_ld + 1e-9:
            out.append(Finding("casting.core.ld", WARNING,
                               f"cored hole {i}: L/D {l / d:.1f} > {max_ld:.0f}:1.", l / d, max_ld,
                               {"length_mm": _down(max_ld * d)}, ["nadca"]))
    return out


# ---------------------------------------------------------------- machined
def _check_machined(p: dict) -> list:
    out = []
    cls = p.get("material_class", "metal")
    rec, feas = D.CNC_WALL[cls]
    for i, w in enumerate(p.get("walls_mm", [])):
        w = float(w)
        if w < feas - 1e-9:
            out.append(Finding("cnc.wall.min", ERROR, f"wall {i}: {w} mm < feasible {feas} mm ({cls}).", w, feas,
                               {"wall_mm": rec}, ["hubs-cnc"]))
        elif w < rec - 1e-9:
            out.append(Finding("cnc.wall.thin", WARNING, f"wall {i}: {w} mm < recommended {rec} mm ({cls}).", w,
                               rec, {"wall_mm": rec}, ["hubs-cnc"]))
    r_d, t_d, f_d = D.CNC_HOLE_DEPTH_D
    for i, h in enumerate(p.get("holes", [])):
        d = float(h["diameter_mm"])
        if d < D.CNC_HOLE_MIN_D_FEASIBLE - 1e-9:
            out.append(Finding("cnc.hole.min_d", ERROR, f"hole {i}: {d} mm is micro-machining (< 1 mm).", d,
                               D.CNC_HOLE_MIN_D_FEASIBLE, {"diameter_mm": D.CNC_HOLE_MIN_D_REC}, ["hubs-cnc"]))
        elif d < D.CNC_HOLE_MIN_D_REC - 1e-9:
            out.append(Finding("cnc.hole.small", WARNING, f"hole {i}: {d} mm < 2.5 mm normal tooling.", d,
                               D.CNC_HOLE_MIN_D_REC, {"diameter_mm": D.CNC_HOLE_MIN_D_REC}, ["hubs-cnc"]))
        dep = h.get("depth_mm")
        if dep is not None:
            ratio = float(dep) / d
            if ratio > f_d + 1e-9:
                out.append(Finding("cnc.hole.depth", ERROR, f"hole {i}: depth {ratio:.1f} x D > 40 x D.", ratio,
                                   f_d, {"depth_mm": _down(t_d * d)}, ["hubs-cnc"]))
            elif ratio > t_d + 1e-9:
                out.append(Finding("cnc.hole.depth", WARNING, f"hole {i}: depth {ratio:.1f} x D > 10 x D "
                                   "(special drills).", ratio, t_d, {"depth_mm": _down(t_d * d)}, ["hubs-cnc"]))
            elif ratio > r_d + 1e-9:
                out.append(Finding("cnc.hole.depth", INFO, f"hole {i}: depth {ratio:.1f} x D > 4 x D recommended.",
                                   ratio, r_d, {"depth_mm": _down(r_d * d)}, ["hubs-cnc"]))
    for i, k in enumerate(p.get("pockets", [])):
        dep, wid = float(k["depth_mm"]), float(k["width_mm"])
        if dep > D.CNC_CAVITY_DEPTH_W * wid + 1e-9:
            out.append(Finding("cnc.pocket.depth", WARNING, f"pocket {i}: depth {dep} mm > 4 x width.", dep,
                               D.CNC_CAVITY_DEPTH_W * wid, {"depth_mm": _down(D.CNC_CAVITY_DEPTH_W * wid)},
                               ["hubs-cnc"]))
        cr = k.get("corner_radius_mm")
        if cr is not None and float(cr) < dep * D.CNC_CORNER_R_FRAC_DEPTH - 1e-9:
            out.append(Finding("cnc.pocket.corner", WARNING,
                               f"pocket {i}: corner radius {cr} mm < depth/3 = {dep / 3:.2f} mm.", float(cr),
                               dep / 3, {"corner_radius_mm": _up(dep / 3)}, ["hubs-cnc"]))
    tol = p.get("tolerance_mm")
    if tol is not None:
        tol = float(tol)
        if tol < D.CNC_TOL_FEASIBLE - 1e-9:
            out.append(Finding("cnc.tolerance", ERROR, f"+/-{tol} mm is tighter than +/-0.02 mm feasible.", tol,
                               D.CNC_TOL_FEASIBLE, {"tolerance_mm": D.CNC_TOL_FEASIBLE}, ["hubs-cnc"]))
        elif tol < D.CNC_TOL_TYPICAL - 1e-9:
            out.append(Finding("cnc.tolerance", WARNING, f"+/-{tol} mm is tighter than +/-0.1 mm typical; needs a "
                               "drawing and costs more.", tol, D.CNC_TOL_TYPICAL,
                               {"tolerance_mm": D.CNC_TOL_TYPICAL}, ["hubs-cnc", "protolabs-cnc"]))
        if p.get("machine") == "desktop" and tol < D.SHAPEOKO5PRO_ACCURACY - 1e-9:
            out.append(Finding("cnc.desktop.tolerance", ERROR,
                               f"+/-{tol} mm is tighter than a desktop router's ballscrew accuracy (+/-0.05 mm per "
                               "300 mm, Shapeoko 5 Pro); real cut accuracy is worse.", tol,
                               D.SHAPEOKO5PRO_ACCURACY, {"tolerance_mm": D.SHAPEOKO5PRO_ACCURACY}, ["shapeoko5pro"]))
    tr = p.get("turned")
    if tr:
        ld = float(tr["length_mm"]) / float(tr["diameter_mm"])
        if ld < 3:
            pass  # chuck only (cadem-turning)
        elif ld < 6:
            out.append(Finding("turning.ld", INFO, f"L/D {ld:.1f}: use a tailstock (3-6), or chuck only with "
                               "reduced cutting parameters up to 5.", ld, 3.0, sources=["cadem-turning"]))
        elif ld < 12:
            out.append(Finding("turning.ld", WARNING, f"L/D {ld:.1f}: needs a steady rest (6-12), or a tailstock "
                               "with reduced cutting parameters up to 10.", ld, 6.0, sources=["cadem-turning"]))
        elif ld <= 20:
            out.append(Finding("turning.ld", WARNING, f"L/D {ld:.1f}: steady rest with reduced cutting parameters "
                               "(up to 20); every 3 L/D needs a new holding point at full parameters.", ld, 12.0,
                               sources=["cadem-turning"]))
        else:
            out.append(Finding("turning.ld", ERROR, f"L/D {ld:.1f} > 20: beyond steady-rest practice.", ld, 20.0,
                               {"length_mm": _down(20 * float(tr["diameter_mm"]))}, ["cadem-turning"]))
    return out


_DISPATCH = {"sheet": _check_sheet, "tube": _check_tube, "extrusion": _check_extrusion,
             "casting": _check_casting, "machined": _check_machined}


def check_part(part: dict) -> list:
    """Check one part description. Raises ValueError on malformed input."""
    kind = part.get("kind")
    if kind not in _DISPATCH:
        raise ValueError(f"kind must be one of {sorted(_DISPATCH)}")
    return _DISPATCH[kind](part)
