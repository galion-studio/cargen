# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Run from forge/scripts:  ../../.venv/bin/python -m unittest discover -s air/tests -t .  -v"""
import math, unittest
from air import isa, humid, forces, ahmed, gust

# U.S. Standard Atmosphere 1976, Table I, geopotential altitude, metric (NASA-TM-X-74335,
# printed pp. 52, 54, 58 and the 21-24 km page), read from the scanned PDF on 2026-10-21.
# (H m, T K, p mb, rho kg/m^3) -- tabulated to 5 significant digits.
TABLE_I_GEOPOT = [
    (-1000, 294.650, 1139.2, 1.3470),
    (0, 288.150, 1013.25, 1.2250),
    (500, 284.900, 954.60, 1.1673),
    (1000, 281.650, 898.74, 1.1116),
    (1500, 278.400, 845.55, 1.0581),
    (2000, 275.150, 794.95, 1.0065),
    (3000, 268.650, 701.08, 0.90912),
    (4000, 262.150, 616.40, 0.81913),
    (5000, 255.650, 540.19, 0.73612),
    (6000, 249.150, 471.81, 0.65970),
    (11000, 216.650, 226.32, 0.36392),
    (12000, 216.650, 193.30, 0.31083),
    (21000, 217.650, 46.778, 0.074874),
    (22000, 218.650, 39.997, 0.063727),
    (24000, 220.650, 29.304, 0.046267),
]
# Table I, geometric altitude, metric (printed p. 55): (Z m, T K, p mb, rho)
TABLE_I_GEOMETRIC = [(3000, 268.659, 701.21, 0.90925), (4000, 262.166, 616.60, 0.81935), (4500, 258.921, 577.52, 0.77704)]

TOL = 1.0e-4  # relative; table rounding at 5 s.f. is <= 5e-5 relative


class TestISA(unittest.TestCase):
    def check(self, st, T, p_mb, rho):
        self.assertAlmostEqual(st["T"], T, delta=0.0015)
        self.assertLess(abs(st["p"] / (p_mb * 100) - 1), TOL)
        self.assertLess(abs(st["rho"] / rho - 1), TOL)

    def test_geopotential_table(self):
        for H, T, p, rho in TABLE_I_GEOPOT:
            with self.subTest(H=H):
                self.check(isa.isa(H), T, p, rho)

    def test_geometric_table(self):
        for Z, T, p, rho in TABLE_I_GEOMETRIC:
            with self.subTest(Z=Z):
                self.check(isa.isa(Z, geometric=True), T, p, rho)

    def test_range(self):
        with self.assertRaises(ValueError):
            isa.isa(40000)

    def test_isa_dev(self):
        a, b = isa.isa(0), isa.isa(0, dT=15)
        self.assertEqual(a["p"], b["p"])
        self.assertAlmostEqual(b["rho"] / a["rho"], 288.15 / 303.15, places=12)


class TestHumid(unittest.TestCase):
    def test_iapws_check_values(self):  # IAPWS SR1-86(1992) Table 1
        self.assertLess(abs(humid.p_sat_water(273.16) / 611.657 - 1), 1e-6)
        self.assertLess(abs(humid.p_sat_water(373.1243) / 101325.0 - 1), 1e-6)

    def test_humid_lighter(self):
        dry, _ = humid.humid_density(101325, 293.15, 0.0)
        wet, ok = humid.humid_density(101325, 293.15, 1.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(dry, isa.density(101325, 293.15), places=12)
        self.assertLess(wet, dry)

    def test_cold_flag(self):
        with self.assertRaises(ValueError):
            humid.p_sat_water(263.15)
        _, ok = humid.humid_density(101325, 263.15, 0.5, extrapolate=True)
        self.assertFalse(ok)


class TestForces(unittest.TestCase):
    def test_definitions(self):
        self.assertAlmostEqual(forces.drag(0.3, 2.0, 1.225, 40.0), 0.5 * 1.225 * 1600 * 0.6)
        self.assertAlmostEqual(forces.lift(-0.1, 2.0, 1.225, 40.0), -0.5 * 1.225 * 1600 * 0.2)

    def test_v_cubed_power(self):
        p1 = forces.road_load(0.3, 2.2, 1.225, 20.0)["P_aero"]
        p2 = forces.road_load(0.3, 2.2, 1.225, 40.0)["P_aero"]
        self.assertAlmostEqual(p2 / p1, 8.0, places=12)

    def test_wind(self):
        head = forces.road_load(0.3, 2.2, 1.225, 30.0, wind_speed=5.0, wind_from_deg=0.0)
        self.assertAlmostEqual(head["V_rel"], 35.0)
        tail = forces.road_load(0.3, 2.2, 1.225, 30.0, wind_speed=5.0, wind_from_deg=180.0)
        self.assertAlmostEqual(tail["V_rel"], 25.0)
        cross = forces.apparent_wind(30.0, 10.0, 90.0)
        self.assertAlmostEqual(cross[1], math.degrees(math.atan2(10, 30)))

    def test_rolling_grade(self):
        r = forces.road_load(0.3, 2.2, 1.2, 10.0, crr=0.01, mass=1000.0, grade_rad=0.0)
        self.assertAlmostEqual(r["F_roll"], 0.01 * 1000 * 9.80665)
        with self.assertRaises(ValueError):
            forces.road_load(0.3, 2.2, 1.2, 10.0, crr=0.01)


class TestAhmed(unittest.TestCase):
    def test_values(self):
        self.assertEqual(ahmed.cd_exp(25, "AHMED1984"), 0.285)
        self.assertEqual(ahmed.cd_exp(35, "AHMED1984"), 0.258)
        self.assertEqual(ahmed.cd_exp(25), 0.299)
        self.assertEqual(ahmed.cd_exp(35), 0.279)

    def test_breakdown_sums(self):
        self.assertAlmostEqual(sum(ahmed.AHMED1984_25_BREAKDOWN.values()), 0.285, places=12)

    def test_sst_error(self):
        sst = ahmed.lookup(25, "cfd", "GUIL2018", "k-omega SST")[0]["cd"]
        self.assertAlmostEqual(ahmed.cd_error(sst, 25, "AHMED1984"), (0.3218 - 0.285) / 0.285)


class TestGust(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(gust.one_minus_cos(-1, 5, 20), 0.0)
        self.assertAlmostEqual(gust.one_minus_cos(10, 5, 20), 2.5)
        self.assertAlmostEqual(gust.one_minus_cos(20, 5, 20), 5.0)
        self.assertEqual(gust.one_minus_cos(50, 5, 20), 5.0)

    def test_dryden_variance(self):
        g = gust.DrydenU(sigma=1.5, L=50.0, seed=1)
        xs = [g.step(30.0, 0.05) for _ in range(200000)]
        m = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))
        self.assertLess(abs(sd / 1.5 - 1), 0.05)


if __name__ == "__main__":
    unittest.main()
