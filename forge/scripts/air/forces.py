# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Aerodynamic forces and road-load power from coefficients (definitions, no empirical data).

D = 0.5 rho V^2 Cd A,  L = 0.5 rho V^2 Cl A  (standard coefficient definitions, e.g.
Hucho, Aerodynamics of Road Vehicles; same definition used by DrivAerML/AhmedML force files).
V is the air speed relative to the car (apparent wind), not the road speed.
Road load: F = D_x + Crr m g cos(theta) + m g sin(theta); P = F v_road.
Crr and m are inputs the caller must source (tyre data is outside the air sector); no defaults.
"""
import math

G = 9.80665


def dynamic_pressure(rho, v):
    return 0.5 * rho * v * v


def drag(cd, area, rho, v):
    return dynamic_pressure(rho, v) * cd * area


def lift(cl, area, rho, v):
    """Positive = upward lift; negative Cl gives downforce."""
    return dynamic_pressure(rho, v) * cl * area


def apparent_wind(v_road, wind_speed=0.0, wind_from_deg=0.0):
    """Air velocity seen by the car.

    v_road: car speed over ground (m/s, >= 0), heading along +x.
    wind_speed: wind speed over ground (m/s); wind_from_deg: direction the wind comes FROM,
    relative to the car heading (0 = pure headwind, 90 = from the right, 180 = tailwind).
    Returns (V_rel [m/s], yaw beta [deg], u_x [m/s], u_y [m/s]) where u_x is the axial
    component (positive = flowing nose to tail) and u_y the lateral component.
    """
    th = math.radians(wind_from_deg)
    ux = v_road + wind_speed * math.cos(th)
    uy = wind_speed * math.sin(th)
    vrel = math.hypot(ux, uy)
    beta = math.degrees(math.atan2(uy, ux)) if vrel > 0 else 0.0
    return vrel, beta, ux, uy


def road_load(cd, area, rho, v_road, wind_speed=0.0, wind_from_deg=0.0, crr=None, mass=None, grade_rad=0.0):
    """Road-load force and power at constant speed.

    Aero drag is applied along the apparent-wind direction and its axial (x) component is
    used: D_x = q(V_rel) Cd A cos(beta). Cd must be the coefficient AT that yaw angle (Cd(beta)
    from CFD or test); this function does not invent a yaw correction.
    Rolling/grade terms only if crr and mass are both given.
    Returns dict with F_aero, F_roll, F_grade, F_total [N], P_aero, P_total [W], V_rel, beta.
    """
    vrel, beta, ux, uy = apparent_wind(v_road, wind_speed, wind_from_deg)
    d = drag(cd, area, rho, vrel)
    f_aero = d * (ux / vrel) if vrel > 0 else 0.0
    f_roll = f_grade = 0.0
    if crr is not None and mass is not None:
        f_roll = crr * mass * G * math.cos(grade_rad)
        f_grade = mass * G * math.sin(grade_rad)
    elif (crr is None) != (mass is None):
        raise ValueError("give both crr and mass, or neither")
    f = f_aero + f_roll + f_grade
    return {"V_rel": vrel, "beta_deg": beta, "F_aero": f_aero, "F_roll": f_roll, "F_grade": f_grade,
            "F_total": f, "P_aero": f_aero * v_road, "P_total": f * v_road}
