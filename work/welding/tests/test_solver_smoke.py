# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Optional: run the generated card through OpenCourant (skipped if the solver is not present)."""
import csv
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "smoke"))
import make_smoke_deck as smk  # noqa: E402


@unittest.skipUnless(os.path.isfile(os.path.join(smk.OC, "exec", "starter_linux64_gf")), "OpenCourant not installed")
class TestSolverSmoke(unittest.TestCase):
    def test_card_runs_and_fails_at_card_values(self):
        with tempfile.TemporaryDirectory() as d:
            card, run_dir = smk.build(run_dir=d)
            smk.run(run_dir)
            with open(os.path.join(run_dir, "SW_0000.out")) as fh:
                self.assertIn(" 0 ERROR(S)", fh.read())
            with open(os.path.join(run_dir, "SW_0001.out")) as fh:
                out = fh.read()
            self.assertIn("NORMAL TERMINATION", open(os.path.join(run_dir, "engine.log")).read())
            self.assertIn("DELETE CONNECTION SOLID ELEMENT", out)
            rows = list(csv.reader(open(os.path.join(run_dir, "SWT01.csv"))))
            weld_cols = [i for i, h in enumerate(rows[0]) if h.startswith("weld")]
            data = [list(map(float, r)) for r in rows[1:] if r]
            pre = [r for r in data if 1.0e-4 < r[0] < 1.7e-3]  # plastic plateau, before failure
            post = [r for r in data if r[0] > 2.0e-3]  # after the 1.8 mm failure displacement
            # one brick stress column must sit on the card's shear yield stress (within 0.5 %)
            plateau = [i for i in weld_cols
                       if all(abs(abs(r[i]) / card["tau_MPa"] - 1.0) < 0.005 for r in pre)]
            self.assertEqual(len(plateau), 1)
            # and carry nothing once the weld is deleted
            self.assertTrue(all(abs(r[plateau[0]]) < 1e-6 for r in post))


if __name__ == "__main__":
    unittest.main()
