# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Unit tests for mfgcheck. Run: python3 -m unittest discover -s tests -v"""
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from mfgcheck import check_part, flc0_keeler, flc_major_limit  # noqa: E402
from mfgcheck import data as D  # noqa: E402


def rules(findings, severity=None):
    return {f.rule for f in findings if severity is None or f.severity == severity}


def get(findings, rule):
    return [f for f in findings if f.rule == rule]


class TestData(unittest.TestCase):
    def test_every_source_has_url(self):
        for k, (title, url) in D.SOURCES.items():
            self.assertTrue(url.startswith("https://"), k)
            self.assertTrue(title, k)

    def test_faa_table_shape_and_order(self):
        for alloy, rows in D.FAA_AL_BEND_RT.items():
            self.assertEqual(len(rows), len(D.FAA_THICKNESS_IN), alloy)
            for lo, hi in rows:
                self.assertLessEqual(lo, hi, alloy)
            # radius never decreases with thickness in the FAA table
            self.assertEqual([r[0] for r in rows], sorted(r[0] for r in rows), alloy)

    def test_steel_sources_exist(self):
        for g, s in D.STEEL.items():
            self.assertIn(s["src"], D.SOURCES, g)

    def test_bonnell_table_monotonic(self):
        lows = [r[0] for r in D.BONNELL_MIN_WALL]
        self.assertEqual(lows, sorted(lows))
        for r in D.BONNELL_MIN_WALL:
            self.assertLess(r[2], r[3])  # hollows need thicker walls


class TestFLC(unittest.TestCase):
    def test_keeler_example(self):
        # (23.3 + 14.2*1.0) * 0.18 / 0.21 = 32.142857...
        self.assertAlmostEqual(flc0_keeler(1.0, 0.18), 32.142857, places=5)

    def test_keeler_at_reference_n(self):
        self.assertAlmostEqual(flc0_keeler(0.0001, 0.21), 23.3014, places=3)

    def test_right_side_slope(self):
        self.assertAlmostEqual(flc_major_limit(30.0, 10.0), 36.0)

    def test_left_side_constant_true_thinning(self):
        f0 = 30.0
        lim = flc_major_limit(f0, -10.0)
        # true major + true minor == true major at plane strain
        self.assertAlmostEqual(math.log(1 + lim / 100) + math.log(0.9), math.log(1.3), places=12)

    def test_continuous_at_plane_strain(self):
        self.assertAlmostEqual(flc_major_limit(25.0, -1e-9), flc_major_limit(25.0, 0.0), places=6)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            flc0_keeler(0, 0.2)

    def test_sheet_flc_zones(self):
        base = dict(kind="sheet", material="DC04", thickness_mm=1.0)
        f0 = flc0_keeler(1.0, 0.18)
        safe = check_part({**base, "strain_points": [{"major_pct": f0 - 15, "minor_pct": 0}]})
        self.assertFalse(rules(safe) & {"flc.above", "flc.marginal"})
        marg = check_part({**base, "strain_points": [{"major_pct": f0 - 5, "minor_pct": 0}]})
        self.assertIn("flc.marginal", rules(marg, "warning"))
        bad = check_part({**base, "strain_points": [{"major_pct": f0 + 1, "minor_pct": 0}]})
        f = get(bad, "flc.above")[0]
        self.assertEqual(f.severity, "error")
        self.assertLessEqual(f.suggestion["major_pct"], f0 - 10)

    def test_flc_refused_for_dp800_and_aluminium(self):
        for mat in ("DP800-UC", "6061-T6"):
            fs = check_part(dict(kind="sheet", material=mat, thickness_mm=1.5,
                                 strain_points=[{"major_pct": 5, "minor_pct": 0}]))
            self.assertIn("flc.not_applicable", rules(fs, "warning"), mat)

    def test_flc_extrapolation_warning(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=1.0,
                             strain_points=[{"major_pct": 10, "minor_pct": 25}]))
        self.assertIn("flc.extrapolated", rules(fs))


class TestSheetBend(unittest.TestCase):
    def test_5052_h32_zero_radius_at_1_6mm_fails(self):
        # 1.6 mm = 0.063 in -> 0.064 column, range 0.5-1t
        fs = check_part(dict(kind="sheet", material="5052-H32", thickness_mm=1.6,
                             bends=[{"inside_radius_mm": 0.0}]))
        f = get(fs, "sheet.bend.al.min_radius")[0]
        self.assertEqual(f.limit, 0.5)
        self.assertAlmostEqual(f.suggestion["inside_radius_mm"], 1.6)

    def test_5052_h32_1t_ok(self):
        fs = check_part(dict(kind="sheet", material="5052-H32", thickness_mm=1.6,
                             bends=[{"inside_radius_mm": 1.6}]))
        self.assertFalse(rules(fs) & {"sheet.bend.al.min_radius", "sheet.bend.al.marginal_radius"})

    def test_6061_t6_2mm_needs_3t(self):
        # 2.0 mm = 0.0787 in -> 0.128 column (conservative), range 1.5-3t
        fs = check_part(dict(kind="sheet", material="6061-T6", thickness_mm=2.0,
                             bends=[{"inside_radius_mm": 2.0}]))
        f = get(fs, "sheet.bend.al.min_radius")[0]
        self.assertEqual(f.limit, 1.5)
        self.assertAlmostEqual(f.suggestion["inside_radius_mm"], 6.0)

    def test_6061_t6_marginal(self):
        fs = check_part(dict(kind="sheet", material="6061-T6", thickness_mm=2.0,
                             bends=[{"inside_radius_mm": 4.0}]))
        self.assertIn("sheet.bend.al.marginal_radius", rules(fs, "warning"))

    def test_thick_aluminium_out_of_table(self):
        fs = check_part(dict(kind="sheet", material="5052-H32", thickness_mm=8.0,
                             bends=[{"inside_radius_mm": 12.0}]))
        self.assertIn("sheet.bend.al.table_range", rules(fs, "warning"))

    def test_dp800_free_and_tension(self):
        free = check_part(dict(kind="sheet", material="DP800-UC", thickness_mm=1.5,
                               bends=[{"inside_radius_mm": 0.75}]))
        f = get(free, "sheet.bend.steel.min_radius")[0]
        self.assertEqual(f.limit, 1.0)
        self.assertAlmostEqual(f.suggestion["inside_radius_mm"], 1.5)
        self.assertIn("sheet.bend.ahss_tension_note", rules(free, "info"))
        ok_free = check_part(dict(kind="sheet", material="DP800-UC", thickness_mm=1.5,
                                  bends=[{"inside_radius_mm": 3.0}]))
        self.assertNotIn("sheet.bend.steel.min_radius", rules(ok_free))
        tens = check_part(dict(kind="sheet", material="DP800-UC", thickness_mm=1.5,
                               bends=[{"inside_radius_mm": 3.0, "context": "tension"}]))
        f = get(tens, "sheet.bend.steel.min_radius")[0]
        self.assertEqual(f.limit, 5.0)
        self.assertIn("ahss-shear", f.sources)

    def test_coated_dp1000_needs_3t(self):
        fs = check_part(dict(kind="sheet", material="DP1000-GI", thickness_mm=1.2,
                             bends=[{"inside_radius_mm": 3.0}]))
        self.assertEqual(get(fs, "sheet.bend.steel.min_radius")[0].limit, 3.0)

    def test_dc04_designer_rule_only_warns(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=1.0,
                             bends=[{"inside_radius_mm": 0.5}]))
        self.assertIn("sheet.bend.designer_radius", rules(fs, "warning"))
        self.assertFalse(rules(fs, "error"))

    def test_unknown_material_info(self):
        fs = check_part(dict(kind="sheet", material="unobtanium", thickness_mm=1.0))
        self.assertIn("material.unknown", rules(fs, "info"))


class TestSheetFeatures(unittest.TestCase):
    def test_hole_min_by_process(self):
        part = dict(kind="sheet", material="DC04", thickness_mm=4.0, holes=[{"diameter_mm": 3.0}])
        self.assertNotIn("sheet.hole.min_diameter", rules(check_part({**part, "process": "laser"})))
        fs = check_part({**part, "process": "plasma"})
        f = get(fs, "sheet.hole.min_diameter")[0]
        self.assertAlmostEqual(f.suggestion["diameter_mm"], 4.0)
        self.assertIn("hypertherm-holes", f.sources)
        self.assertIn("sheet.hole.min_diameter", rules(check_part({**part, "process": "fabricated"})))

    def test_plasma_truehole_window(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=6.0, process="plasma",
                             holes=[{"diameter_mm": 9.0}]))
        self.assertIn("sheet.hole.plasma_truehole", rules(fs, "info"))

    def test_unknown_process_raises(self):
        with self.assertRaises(ValueError):
            check_part(dict(kind="sheet", material="DC04", thickness_mm=1.0, process="waterjet"))

    def test_edge_distance_thin_and_thick(self):
        thin = check_part(dict(kind="sheet", material="DC04", thickness_mm=0.8,
                               holes=[{"diameter_mm": 2.0, "edge_distance_mm": 1.6}]))
        self.assertNotIn("sheet.hole.edge_distance", rules(thin))
        thick = check_part(dict(kind="sheet", material="DC04", thickness_mm=1.0,
                                holes=[{"diameter_mm": 2.0, "edge_distance_mm": 1.6}]))
        f = get(thick, "sheet.hole.edge_distance")[0]
        self.assertAlmostEqual(f.limit, 3.175)
        self.assertAlmostEqual(f.suggestion["edge_distance_mm"], 3.2)

    def test_hole_near_bend(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=2.0,
                             holes=[{"diameter_mm": 5.0, "bend_distance_mm": 6.0}]))
        self.assertIn("sheet.hole.near_bend", rules(fs, "warning"))
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=2.0,
                             holes=[{"diameter_mm": 5.0, "bend_distance_mm": 10.0}]))
        self.assertIn("sheet.hole.designer_bend_distance", rules(fs, "info"))

    def test_flange_min(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=2.0,
                             bends=[{"inside_radius_mm": 3.0, "flange_mm": 6.0}]))
        self.assertAlmostEqual(get(fs, "sheet.flange.min")[0].suggestion["flange_mm"], 8.0)


class TestPressBrake(unittest.TestCase):
    def test_die_too_narrow(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=3.0, die_opening_mm=12.0))
        f = get(fs, "pressbrake.die_min")[0]
        self.assertAlmostEqual(f.suggestion["die_opening_mm"], 24.0)

    def test_flange_vs_die(self):
        # Fabricator example: 0.125 in sheet, 1 in die needs >= 0.77 in flange; 0.625 in die fits 0.5 in.
        t, V, fl = 0.125 * 25.4, 1.0 * 25.4, 0.5 * 25.4
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=t, die_opening_mm=V,
                             bends=[{"inside_radius_mm": 4.0, "flange_mm": fl}]))
        f = get(fs, "pressbrake.flange_vs_die")[0]
        self.assertAlmostEqual(f.limit, 0.77 * V)
        self.assertGreaterEqual(f.suggestion["die_opening_mm"], 5 * t)
        self.assertLessEqual(f.suggestion["die_opening_mm"], fl / 0.77)

    def test_predicted_radius_info(self):
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=3.175, die_opening_mm=25.4,
                             bends=[{"inside_radius_mm": 4.064}]))
        f = get(fs, "pressbrake.predicted_radius")[0]
        self.assertAlmostEqual(f.value, 0.16 * 25.4)

    def test_tonnage_matches_noramark_example(self):
        # Noramark: 1/8 in mild steel over 1 in die = 8.98 US tons per foot (60 ksi = 414 MPa).
        t, V, L = 3.175, 25.4, 304.8
        fs = check_part(dict(kind="sheet", material="DC04", thickness_mm=t, die_opening_mm=V,
                             bend_length_mm=L, press_capacity_t=100, uts_mpa=414))
        metric_t = get(fs, "pressbrake.tonnage.ok")[0].value
        us_tons = metric_t * 1000 / 907.18474
        self.assertAlmostEqual(us_tons, 8.98, delta=0.05)

    def test_tonnage_over_capacity(self):
        fs = check_part(dict(kind="sheet", material="DP600-UC", thickness_mm=3.0, bend_length_mm=1000,
                             press_capacity_t=20))
        f = get(fs, "pressbrake.tonnage")[0]
        self.assertEqual(f.severity, "error")
        # suggested die or length brings the estimate under capacity
        V2 = f.suggestion["die_opening_mm"]
        self.assertLessEqual(67.4 * 9 / V2 * 700 / 414, 20 + 1e-6)
        self.assertLess(f.suggestion["bend_length_mm"], 1000)

    def test_tonnage_needs_uts_for_aluminium(self):
        fs = check_part(dict(kind="sheet", material="5052-H32", thickness_mm=2.0, bend_length_mm=500,
                             press_capacity_t=20))
        self.assertIn("pressbrake.tonnage.no_uts", rules(fs, "info"))


class TestTube(unittest.TestCase):
    def test_tight_clr(self):
        fs = check_part(dict(kind="tube", material="DOM", od_mm=38.1, wall_mm=2.4,
                             bends=[{"clr_mm": 57.15}]))
        f = get(fs, "tube.clr.production_min")[0]
        self.assertAlmostEqual(f.suggestion["clr_mm"], 76.2)
        self.assertIn("tube.clr.no_mandrel", rules(fs, "warning"))

    def test_mandrel_allows_2d(self):
        fs = check_part(dict(kind="tube", od_mm=25.4, wall_mm=1.65, mandrel=True,
                             bends=[{"clr_mm": 50.8}]))
        self.assertFalse(rules(fs) & {"tube.clr.production_min", "tube.clr.no_mandrel"})

    def test_whole_multiple_info(self):
        fs = check_part(dict(kind="tube", od_mm=25.4, wall_mm=1.65, bends=[{"clr_mm": 88.9}]))
        self.assertIn("tube.clr.whole_multiple", rules(fs, "info"))

    def test_short_straight(self):
        fs = check_part(dict(kind="tube", od_mm=25.4, wall_mm=1.65, straights_mm=[50, 100]))
        self.assertEqual(len(get(fs, "tube.straight.min")), 1)

    def test_jd2_limits(self):
        base = dict(kind="tube", bender="jd2_model32", bends=[])
        fs = check_part({**base, "od_mm": 50.8, "wall_mm": 6.35})
        self.assertIn("tube.bender.needs_hydraulic", rules(fs, "error"))
        fs = check_part({**base, "od_mm": 50.8, "wall_mm": 6.35, "hydraulic": True})
        self.assertFalse(rules(fs, "error"))
        fs = check_part({**base, "od_mm": 50.8, "wall_mm": 7.0, "hydraulic": True})
        self.assertIn("tube.bender.wall_rating", rules(fs, "error"))
        fs = check_part({**base, "od_mm": 76.2, "wall_mm": 3.0, "hydraulic": True})
        self.assertIn("tube.bender.od_range", rules(fs, "error"))
        fs = check_part({**base, "od_mm": 44.45, "wall_mm": 2.41})
        self.assertFalse(rules(fs, "error"))

    def test_bad_wall(self):
        with self.assertRaises(ValueError):
            check_part(dict(kind="tube", od_mm=20, wall_mm=10))


class TestExtrusion(unittest.TestCase):
    def test_solid_min_wall(self):
        # CCD 100 mm = 3.94 in -> 3-4 in row: 0.050 in = 1.27 mm
        fs = check_part(dict(kind="extrusion", alloy="6063", ccd_mm=100, walls_mm=[1.2, 1.5]))
        f = get(fs, "extrusion.min_wall")[0]
        self.assertAlmostEqual(f.limit, 1.27)
        self.assertEqual(f.severity, "error")

    def test_crash_box_class3_warns_not_errors(self):
        fs = check_part(dict(kind="extrusion", alloy="6061", ccd_mm=120, walls_mm=[1.8, 2.0],
                             hollow_class=3))
        self.assertIn("extrusion.hollow_class", rules(fs, "warning"))
        self.assertEqual(get(fs, "extrusion.min_wall")[0].severity, "warning")

    def test_class2_ok(self):
        fs = check_part(dict(kind="extrusion", alloy="6061", ccd_mm=100, walls_mm=[2.0, 2.5],
                             hollow_class=2))
        self.assertFalse(rules(fs, "error"))

    def test_wall_ratio_and_ccd(self):
        fs = check_part(dict(kind="extrusion", alloy="6082", ccd_mm=400, walls_mm=[2.0, 5.0]))
        self.assertIn("extrusion.wall_ratio", rules(fs, "warning"))
        self.assertIn("extrusion.ccd_range", rules(fs, "warning"))

    def test_non_6xxx_scope(self):
        fs = check_part(dict(kind="extrusion", alloy="7003", ccd_mm=100, walls_mm=[2.0]))
        self.assertIn("extrusion.alloy_scope", rules(fs, "info"))


class TestCasting(unittest.TestCase):
    def test_nadca_example_draft(self):
        # NADCA example: aluminium inside wall, 25 mm deep -> 1.9 deg
        fs = check_part(dict(kind="casting", alloy="aluminum",
                             features=[{"depth_mm": 25, "draft_deg": 1.0, "side": "inside"}]))
        f = get(fs, "casting.draft")[0]
        self.assertAlmostEqual(f.limit, 1.909, places=3)
        self.assertAlmostEqual(f.suggestion["draft_deg"], 2.0)

    def test_outside_half_of_inside_and_mg(self):
        fs = check_part(dict(kind="casting", alloy="magnesium",
                             features=[{"depth_mm": 25, "draft_deg": 0.0, "side": "outside"},
                                       {"depth_mm": 25, "draft_deg": 0.0, "side": "inside"}]))
        out_, in_ = [f.limit for f in get(fs, "casting.draft")]
        self.assertAlmostEqual(in_, 2 * out_, places=6)
        self.assertAlmostEqual(in_, 57.2738 / 35, places=3)

    def test_walls(self):
        fs = check_part(dict(kind="casting", alloy="aluminum", walls_mm=[0.4, 0.8, 6.0]))
        r = rules(fs)
        self.assertTrue({"casting.wall.min", "casting.wall.thin", "casting.wall.thick", "casting.wall.range"} <= r)

    def test_cores_and_radii(self):
        fs = check_part(dict(kind="casting", alloy="aluminum", fillet_radius_mm=1.0, corner_radius_mm=0.2,
                             cored_holes=[{"diameter_mm": 5, "length_mm": 30},
                                          {"diameter_mm": 20, "length_mm": 150}]))
        r = rules(fs)
        self.assertTrue({"casting.fillet", "casting.corner", "casting.core.min_d", "casting.core.ld"} <= r)
        self.assertEqual(len(get(fs, "casting.core.ld")), 1)  # 20 mm at L/D 7.5 is fine (<= 10)

    def test_bad_alloy(self):
        with self.assertRaises(ValueError):
            check_part(dict(kind="casting", alloy="zinc"))


class TestMachined(unittest.TestCase):
    def test_walls_holes_pockets(self):
        fs = check_part(dict(kind="machined", walls_mm=[0.4, 0.6, 1.0],
                             holes=[{"diameter_mm": 0.8}, {"diameter_mm": 2.0, "depth_mm": 30},
                                    {"diameter_mm": 3.0, "depth_mm": 150}],
                             pockets=[{"depth_mm": 30, "width_mm": 6, "corner_radius_mm": 3}]))
        self.assertIn("cnc.wall.min", rules(fs, "error"))
        self.assertIn("cnc.wall.thin", rules(fs, "warning"))
        self.assertIn("cnc.hole.min_d", rules(fs, "error"))
        sev = [f.severity for f in get(fs, "cnc.hole.depth")]
        self.assertEqual(sev, ["warning", "error"])
        self.assertIn("cnc.pocket.depth", rules(fs))
        self.assertAlmostEqual(get(fs, "cnc.pocket.corner")[0].suggestion["corner_radius_mm"], 10.0)

    def test_tolerance_desktop(self):
        fs = check_part(dict(kind="machined", tolerance_mm=0.03, machine="desktop"))
        self.assertIn("cnc.desktop.tolerance", rules(fs, "error"))
        self.assertIn("cnc.tolerance", rules(fs, "warning"))
        fs = check_part(dict(kind="machined", tolerance_mm=0.01))
        self.assertIn("cnc.tolerance", rules(fs, "error"))

    def test_turning_ld(self):
        def sev(ld):
            fs = check_part(dict(kind="machined", turned={"length_mm": ld * 10, "diameter_mm": 10}))
            return [f.severity for f in get(fs, "turning.ld")]
        self.assertEqual(sev(2), [])
        self.assertEqual(sev(4), ["info"])
        self.assertEqual(sev(8), ["warning"])
        self.assertEqual(sev(15), ["warning"])
        self.assertEqual(sev(25), ["error"])


class TestGeneral(unittest.TestCase):
    def test_bad_kind(self):
        with self.assertRaises(ValueError):
            check_part({"kind": "forging"})

    def test_all_findings_cite_known_sources(self):
        parts = json.load(open(os.path.join(ROOT, "examples", "parts.json")))
        n = 0
        for p in parts:
            for f in check_part(p):
                n += 1
                self.assertIn(f.severity, ("error", "warning", "info"))
                if f.severity != "info" or f.sources:
                    self.assertTrue(f.sources, f.rule)
                for s in f.sources:
                    self.assertIn(s, D.SOURCES)
                json.dumps(f.to_dict())
        self.assertGreater(n, 10)

    def test_cli_exit_codes(self):
        ex = os.path.join(ROOT, "examples", "parts.json")
        r = subprocess.run([sys.executable, "-m", "mfgcheck", ex, "--json"], cwd=ROOT,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertTrue(json.loads(r.stdout))
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump({"kind": "sheet", "material": "5052-H32", "thickness_mm": 1.6,
                       "bends": [{"inside_radius_mm": 1.6, "flange_mm": 10}]}, fh)
        r = subprocess.run([sys.executable, "-m", "mfgcheck", fh.name], cwd=ROOT,
                           capture_output=True, text=True)
        os.unlink(fh.name)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
