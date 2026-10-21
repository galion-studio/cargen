# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Wind models for the PLAY layer (game). Not truth-layer data.

1) Discrete "1-cosine" gust, MIL-F-8785C sec. 3.7 (US mil spec), as written in the MathWorks
   Aerospace Blockset "Discrete Wind Gust Model" documentation:
   V = 0 (x<0); V = Vm/2 (1 - cos(pi x / dm)) (0<=x<=dm); V = Vm (x>dm).
   https://www.mathworks.com/help/aeroblks/discretewindgustmodel.html
2) Dryden low-altitude scale lengths and intensities, MIL-F-8785C (h in ft, h < 1000 ft):
   L_w = h, L_u = L_v = h/(0.177+0.000823 h)^1.2, sigma_w = 0.1 W20,
   sigma_u = sigma_v = sigma_w/(0.177+0.000823 h)^0.4.
   https://www.mathworks.com/help/aeroblks/drydenwindturbulencemodelcontinuous.html
   CAUTION: written for aircraft; at car height (~1 m) it is an extrapolation. Use for game
   feel only; a road-vehicle crosswind spec (e.g. ISO 12021 wind-generator test) is not open.
"""
import math, random

FT = 0.3048


def one_minus_cos(x, vm, dm):
    """Gust speed at distance x into the gust (m), amplitude vm (m/s), build-up length dm (m)."""
    if x < 0:
        return 0.0
    if x <= dm:
        return 0.5 * vm * (1.0 - math.cos(math.pi * x / dm))
    return vm


def dryden_low_alt(h_m, w20_ms):
    """Return (L_u, L_v, L_w) in m and (sigma_u, sigma_v, sigma_w) in m/s. h clamped to >= 10 ft
    (the formula is singular at h = 0); h > 1000 ft is out of the low-altitude model."""
    h_ft = max(h_m / FT, 10.0)
    if h_ft > 1000.0:
        raise ValueError("low-altitude Dryden model only below 1000 ft")
    k = 0.177 + 0.000823 * h_ft
    lw = h_ft
    lu = lv = h_ft / k ** 1.2
    sw = 0.1 * w20_ms
    su = sv = sw / k ** 0.4
    return (lu * FT, lv * FT, lw * FT), (su, sv, sw)


class DrydenU:
    """First-order Dryden longitudinal/lateral gust filter (exact discretisation of
    du/dt = -(V/L) u + sigma sqrt(2V/L) noise). Stationary std == sigma by construction."""

    def __init__(self, sigma, L, seed=None):
        self.sigma, self.L, self.u = sigma, L, 0.0
        self.rng = random.Random(seed)

    def step(self, V, dt):
        a = math.exp(-V * dt / self.L)
        self.u = a * self.u + self.sigma * math.sqrt(1 - a * a) * self.rng.gauss(0, 1)
        return self.u
