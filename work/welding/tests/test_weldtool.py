# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Unit tests for weldtool. Run: python3 -m unittest discover -s tests -v (from work/welding)."""
import io
import json
import math
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from weldtool import core, data as D  # noqa: E402
from weldtool.cli import main  # noqa: E402


class TestDataIntegrity(unittest.TestCase):
    def test_every_source_has_https_url(self):
        for k, (title, url) in D.SOURCES.items():
            self.assertTrue(url.startswith("https://"), k)
            self.assertTrue(title.strip(), k)

    def test_all_referenced_sources_exist(self):
        ids = {h["source"] for h in D.HAZ}
        ids |= {D.MIG_STEEL["source"], D.MIG_ALUMINIUM["source"], D.TIG_STEEL["source"], D.TIG_ALUMINIUM["source"]}
        ids |= {p["source"] for pts in D.REFERENCE_POINTS.values() for p in pts}
        ids |= {v[1] for v in D.HAZ_WIDTH_NOTES.values()} | {v[1] for v in D.PROCESS_NOTES.values()}
        self.assertTrue(ids <= set(D.SOURCES), ids - set(D.SOURCES))

    def test_haz_rows_reference_known_metals_and_sane_ratios(self):
        for h in D.HAZ:
            self.assertIn(h["metal"], D.MATERIALS)
            self.assertIn(h["kind"], ("code", "joint", "hardness"))
            for r in (h["rho_yield"], h["rho_uts"]):
                if r is not None:
                    self.assertGreater(r, 0.0)
                    self.assertLessEqual(r, 1.0)

    def test_spot_tables_consistent(self):
        n = len(D.RSW_LC_COMMON)
        for cls in D.RSW_LC_CLASS.values():
            self.assertEqual(len(cls["rows"]), n)
        # Class A uses the most force and shortest time at each thickness (as published).
        for i in range(n):
            a, b, c = (D.RSW_LC_CLASS[k]["rows"][i] for k in "ABC")
            self.assertGreater(a[1], b[1])
            self.assertGreater(b[1], c[1])
            self.assertLess(a[0], c[0])

    def test_gauges_monotonic(self):
        order = ["24 ga", "22 ga", "20 ga", "18 ga", "16 ga", "14 ga", "1/8 in", "3/16 in", "1/4 in", "5/16 in", "3/8 in"]
        vals = [D.GAUGE_IN[g] for g in order]
        self.assertEqual(vals, sorted(vals))


class TestTranscribedValues(unittest.TestCase):
    """Spot checks against the source documents (guards against later edits)."""

    def test_miller_values(self):
        self.assertEqual(D.MIG_STEEL["wires"]['.030"']["16 ga"], (17.0, 215))
        self.assertEqual(D.MIG_STEEL["wires"]['.035"']["1/8 in"], (19.0, 230))   # 240 V column
        self.assertEqual(D.MIG_ALUMINIUM["wires"]['ER4043 .035"']["3/8 in"], (25.0, 600))

    def test_ec9_values(self):
        row = [h for h in D.HAZ if h["metal"] == "al-6082-t6-extrusion" and h["process"] == "arc"][0]
        self.assertEqual((row["rho_yield"], row["rho_uts"]), (0.50, 0.64))

    def test_ti_ratios(self):
        r = [h for h in D.HAZ if h["metal"] == "ti-6al-4v" and h["process"] == "tig"][0]
        self.assertAlmostEqual(r["rho_uts"], 958 / 1021)


class TestLookup(unittest.TestCase):
    def test_bracket(self):
        rows = [(1.0,), (2.0,), (3.0,)]
        self.assertEqual(core.bracket(rows, 2.04)[1], "nearest-row (within 5%)")
        self.assertEqual(core.bracket(rows, 1.5), ([(1.0,), (2.0,)], "between-rows"))
        self.assertEqual(core.bracket(rows, 0.2)[1], "below-table")
        self.assertEqual(core.bracket(rows, 9.0)[1], "above-table")

    def test_mig_steel_16ga(self):
        r = core.params("mild-steel", 1.52, "mig")
        w = [x for x in r["by_wire"] if x["wire"] == '.030"'][0]
        self.assertEqual(w["settings"][0]["volts"], 17.0)
        self.assertEqual(w["settings"][0]["wfs_ipm"], 215)
        self.assertEqual(r["rule_of_thumb"]["amps"], 60)          # 1.52 mm = 0.0598 in -> 60 A

    def test_mig_rule_of_thumb_1_8_inch(self):
        r = core.params("mild-steel", 3.175, "mig")
        self.assertEqual(r["rule_of_thumb"]["amps"], 125)        # Miller's own example
        self.assertEqual(r["rule_of_thumb"]["wfs_ipm"]['.030"'], 250)

    def test_tig_aluminium_between(self):
        r = core.params("al-6061-t6", 3.0, "tig")
        self.assertEqual(r["match"], "between-rows")
        self.assertEqual([s["amps"] for s in r["settings"]], [(85, 110), (120, 135)])

    def test_tig_ti_has_no_table_but_tungsten_note(self):
        r = core.params("ti-6al-4v", 2.0, "tig")
        self.assertFalse(r["available"])
        self.assertIn("lanthanated", r["tungsten"])

    def test_spot_mild_steel_1mm(self):
        r = core.params("mild-steel", 1.0, "spot")
        a = r["schedules"][0]["classes"]["A"]
        self.assertEqual(a["current_kA"], 9.2)
        self.assertEqual(a["weld_time_cycles_60Hz"], 10)
        self.assertAlmostEqual(a["force_kN"], 500 * core.LB_TO_KN, places=2)
        self.assertAlmostEqual(r["nugget_min_mm"], 4.0)

    def test_spot_aluminium_ranges_only(self):
        r = core.params("al-5754-h14", 1.5, "spot")
        self.assertIn("ranges only", r["kind"])
        self.assertEqual(r["aluminium"]["current_kA_up_to"], 40)

    def test_unsupported_combo_is_explicit(self):
        self.assertFalse(core.params("ti-6al-4v", 2.0, "spot")["available"])
        self.assertFalse(core.params("mild-steel", 2.0, "fsw")["available"])

    def test_bad_inputs(self):
        with self.assertRaises(core.WeldToolError):
            core.params("unobtainium", 1, "mig")
        with self.assertRaises(core.WeldToolError):
            core.params("mild-steel", 0, "mig")
        with self.assertRaises(core.WeldToolError):
            core.params("mild-steel", 1, "gas")


class TestHAZ(unittest.TestCase):
    def test_arc_rows_apply_to_mig_and_tig(self):
        for p in ("mig", "tig"):
            r = core.haz("al-6082-t6-sheet", p, 3)
            self.assertEqual(r["knockdowns"][0]["rho_uts"], 0.60)

    def test_bhaz(self):
        self.assertEqual(core.haz("al-6082-t6-sheet", "mig", 3)["haz_width_mm"]["b_haz_each_side"], 20.0)
        self.assertEqual(core.haz("al-6082-t6-sheet", "tig", 3)["haz_width_mm"]["b_haz_each_side"], 30.0)
        self.assertIsNone(core.haz("al-6082-t6-sheet", "tig", 10)["haz_width_mm"]["b_haz_each_side"])

    def test_thick_warning(self):
        notes = " ".join(core.haz("al-6082-t6-extrusion", "mig", 8)["notes"])
        self.assertIn("t < 5 mm", notes)

    def test_missing_knockdown_does_not_default_to_one(self):
        r = core.haz("mild-steel", "mig")
        self.assertFalse(r["available"])
        self.assertEqual(r["knockdowns"], [])

    def test_dp980_process_dependence(self):
        spot = core.haz("dp980", "spot")["knockdowns"][0]["rho_uts"]
        mig = core.haz("dp980", "mig")["knockdowns"][0]["rho_uts"]
        self.assertGreater(spot, mig)   # arc heat input softens more than RSW (source)


class TestSpotWeldCard(unittest.TestCase):
    def test_aws_formula(self):
        # hand calc: S=300, t=1 -> (-0.07947+0.402+1.514)*300*4/1000 = 2.20383 kN
        self.assertAlmostEqual(core.aws_min_shear_kN(300, 1.0), 2.20383, places=4)

    def test_aws_minimum_below_nsrw_average(self):
        # AWS gives a minimum; NSRW Class A average for 0.040 in (1.016 mm) is 1305 lb.
        self.assertLess(core.aws_min_shear_kN(290, 1.016), 1305 * core.LB_TO_KN)

    def test_cts_bins(self):
        self.assertEqual(core.cts_ratio(300), 0.70)
        self.assertEqual(core.cts_ratio(600), 0.50)
        self.assertEqual(core.cts_ratio(1000), 0.30)

    def test_card_numbers_and_format(self):
        c = core.spotweld_card("mild-steel", 1.0)
        d = 4.0
        area = math.pi * d * d / 4
        self.assertAlmostEqual(c["area_mm2"], round(area, 3))
        self.assertAlmostEqual(c["tau_MPa"], round(core.aws_min_shear_kN(290, 1.0) * 1000 / area, 1))
        self.assertAlmostEqual(c["normal_kN"] / c["shear_kN"], 0.70, places=2)
        t = c["text"]
        for kw in ("/MAT/LAW59/1/1", "/FAIL/CONNECT/1", "/FUNCT/1", "/FUNCT/2", "VERIFY WITH TEST COUPONS"):
            self.assertIn(kw, t)
        # data lines (not comments/headers) must fit the 100-column Radioss format
        for line in t.splitlines():
            if not line.startswith("#"):
                self.assertLessEqual(len(line), 100, line)

    def test_card_coupon_override_and_non_steel(self):
        with self.assertRaises(core.WeldToolError):
            core.spotweld_card("al-6061-t6", 2.0)
        with self.assertRaises(core.WeldToolError):
            core.spotweld_card("al-6061-t6", 2.0, shear_kN=3.0, normal_kN=1.0)   # density missing
        c = core.spotweld_card("al-6061-t6", 2.0, shear_kN=3.0, normal_kN=1.0, density_t_mm3=2.7e-9)
        self.assertEqual(c["shear_kN"], 3.0)
        self.assertIn("coupon", " ".join(c["origin"]))

    def test_card_needs_uts_when_no_cited_default(self):
        with self.assertRaises(core.WeldToolError):
            core.spotweld_card("dp590", 1.2)
        self.assertGreater(core.spotweld_card("dp590", 1.2, uts_mpa=600)["shear_kN"], 0)


class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_suggest_spot_json(self):
        code, out, _ = self.run_cli("suggest", "--metal", "mild-steel", "-t", "1.0", "-p", "spot", "--json")
        self.assertEqual(code, 0)
        res = json.loads(out)
        self.assertIn("/MAT/LAW59", res["crash_card"]["text"])
        self.assertEqual(res["parameters"]["schedules"][0]["classes"]["C"]["current_kA"], 5.6)

    def test_text_output_has_banner(self):
        code, out, _ = self.run_cli("haz", "--metal", "dp980", "-p", "laser")
        self.assertEqual(code, 0)
        self.assertIn("VERIFY WITH TEST COUPONS", out)

    def test_card_to_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sw.rad")
            code, _, _ = self.run_cli("card", "--metal", "dp980", "-t", "1.4", "--out", path)
            self.assertEqual(code, 0)
            with open(path) as fh:
                self.assertIn("/FAIL/CONNECT", fh.read())

    def test_error_exit_code(self):
        code, _, err = self.run_cli("card", "--metal", "al-6061-t6", "-t", "2")
        self.assertEqual(code, 2)
        self.assertIn("coupons", err)

    def test_list_and_sources(self):
        self.assertEqual(self.run_cli("list")[0], 0)
        code, out, _ = self.run_cli("sources")
        self.assertEqual(code, 0)
        self.assertIn("AWS_C11", out)


if __name__ == "__main__":
    unittest.main()
