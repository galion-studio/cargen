# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Humid-air density (ideal-gas mixture of dry air and water vapour).

Saturation vapour pressure over liquid water: IAPWS SR1-86(1992), "Revised Supplementary
Release on Saturation Properties of Ordinary Water Substance", eq. (1) (Wagner & Pruss 1993).
https://iapws.org/technical-guidance/release/Supp-sat  -- valid 273.16 K <= T <= 647.096 K.
Check values (Table 1 of the release): p_s(273.16 K) = 611.657 Pa, p_s(373.1243 K) = 0.101325 MPa.

Mixture model: rho = (p - e)/(R_d T) + e/(R_v T), e = RH * p_s(T).
Limits (stated, not quantified here): no enhancement factor f and no compressibility Z
(the CIPM-2007 air-density equation, Picard et al. 2008 Metrologia 45:149, includes both);
below 273.16 K the IAPWS curve is extrapolated (over supercooled water, not ice) and the
result is flagged as an unvalidated estimate.
"""
import math
from .isa import R_STAR, R_AIR

TC, PC = 647.096, 22.064e6
_A = (-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502)
M_WATER = 18.01528e-3                 # kg/mol (IAPWS-95 molar mass)
R_VAP = R_STAR / M_WATER              # J/(kg K)


def p_sat_water(T_k, extrapolate=False):
    """Saturation vapour pressure over liquid water [Pa], IAPWS SR1-86(1992) eq. 1."""
    if not (273.16 <= T_k <= TC):
        if not extrapolate:
            raise ValueError("IAPWS SR1-86 valid 273.16-647.096 K; pass extrapolate=True for an unvalidated estimate")
    tau = 1.0 - T_k / TC
    a1, a2, a3, a4, a5, a6 = _A
    s = a1 * tau + a2 * tau ** 1.5 + a3 * tau ** 3 + a4 * tau ** 3.5 + a5 * tau ** 4 + a6 * tau ** 7.5
    return PC * math.exp(TC / T_k * s)


def humid_density(p_pa, T_k, rh, extrapolate=False):
    """Moist-air density [kg/m^3]; rh is relative humidity 0..1. Returns (rho, validated: bool)."""
    if not 0.0 <= rh <= 1.0:
        raise ValueError("rh must be in 0..1")
    validated = T_k >= 273.16
    e = rh * p_sat_water(T_k, extrapolate=extrapolate)
    rho = (p_pa - e) / (R_AIR * T_k) + e / (R_VAP * T_k)
    return rho, validated
