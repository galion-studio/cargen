# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""ISA / U.S. Standard Atmosphere 1976 (identical to ICAO/ISO 2533 below 32 km).

Source: U.S. Standard Atmosphere, 1976, NOAA/NASA/USAF, NASA-TM-X-74335 (US Gov work, public domain).
https://ntrs.nasa.gov/citations/19770009539  (PDF: .../api/citations/19770009539/downloads/19770009539.pdf)
Constants (Part 1 of the document): g0 = 9.80665 m/s^2, R* = 8.31432 J/(mol K),
M0 = 28.9644 g/mol, r0 = 6 356 766 m, sea level T0 = 288.15 K, p0 = 101 325 Pa.
Layers (geopotential altitude H): 0-11 km lapse -6.5 K/km; 11-20 km 0; 20-32 km +1.0 K/km.
Valid range here: -5 km <= H <= 32 km (the 1976 tables start at -5 km). Outside: ValueError.
Checked against Table I of the same document in tests/test_air.py.
"""
import math

G0 = 9.80665            # m/s^2
R_STAR = 8.31432        # J/(mol K), USSA-1976 value (not CODATA)
M0 = 28.9644e-3         # kg/mol, sea-level mean molar mass of dry air
R_AIR = R_STAR / M0     # J/(kg K) ~ 287.053
R0_EARTH = 6356766.0    # m, effective earth radius for geopotential conversion
T0 = 288.15             # K
P0 = 101325.0           # Pa
GAMMA = 1.40            # ratio of specific heats used by USSA-1976 for speed of sound
BETA_S = 1.458e-6       # kg/(m s K^0.5), Sutherland constant, USSA-1976 eq. for viscosity
S_SUTH = 110.4          # K, Sutherland temperature, USSA-1976

# (base geopotential altitude m, base temperature K, lapse rate K/m)
_LAYERS = [(0.0, 288.15, -0.0065), (11000.0, 216.65, 0.0), (20000.0, 216.65, 0.0010), (32000.0, 228.65, 0.0028)]
H_MIN, H_MAX = -5000.0, 32000.0


def geometric_to_geopotential(z_m):
    """Geometric altitude Z (m) -> geopotential altitude H (m), USSA-1976 eq. 18."""
    return R0_EARTH * z_m / (R0_EARTH + z_m)


def _base_pressures():
    pb = [P0]
    for i in range(len(_LAYERS) - 1):
        hb, tb, lb = _LAYERS[i]
        h1 = _LAYERS[i + 1][0]
        pb.append(_p_in_layer(pb[i], tb, lb, h1 - hb))
    return pb


def _p_in_layer(pb, tb, lb, dh):
    if lb == 0.0:
        return pb * math.exp(-G0 * M0 * dh / (R_STAR * tb))
    return pb * (tb / (tb + lb * dh)) ** (G0 * M0 / (R_STAR * lb))


_PB = _base_pressures()


def isa(h_m, geometric=False, dT=0.0):
    """Standard atmosphere at altitude h_m.

    h_m: geopotential altitude in m (or geometric if geometric=True).
    dT: ISA temperature deviation in K (ISA+dT day). Pressure stays the standard
        pressure at that altitude (pressure-altitude convention); density is then
        p / (R T). dT != 0 is a convention, not part of the 1976 standard.
    Returns dict: T [K], p [Pa], rho [kg/m^3], a [m/s], mu [Pa s], nu [m^2/s], H [m].
    """
    H = geometric_to_geopotential(h_m) if geometric else float(h_m)
    if not (H_MIN <= H <= H_MAX):
        raise ValueError(f"geopotential altitude {H:.1f} m outside validated range [{H_MIN}, {H_MAX}] m")
    i = 0 if H < _LAYERS[1][0] else (1 if H < _LAYERS[2][0] else 2)
    hb, tb, lb = _LAYERS[i]
    T_std = tb + lb * (H - hb)
    p = _p_in_layer(_PB[i], tb, lb, H - hb)
    T = T_std + dT
    rho = p / (R_AIR * T)
    a = math.sqrt(GAMMA * R_AIR * T)
    mu = BETA_S * T ** 1.5 / (T + S_SUTH)
    return {"H": H, "T": T, "p": p, "rho": rho, "a": a, "mu": mu, "nu": mu / rho}


def density(p_pa, T_k):
    """Dry-air ideal-gas density p/(R T) with the USSA-1976 gas constant."""
    return p_pa / (R_AIR * T_k)
