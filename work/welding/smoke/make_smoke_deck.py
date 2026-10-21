# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Build a one-spot-weld shear smoke deck around a weldtool card and (optionally) run OpenCourant.

Geometry: two coincident-in-plan square shells (side = sqrt(nugget area)), 1 mm apart, joined by one
/PROP/TYPE43 brick that shares their nodes. Bottom shell clamped; top-shell nodes pulled in +X at
1 m/s. Purpose: prove the card parses and the solver reproduces the card's yield stress and deletes
the weld near the failure displacement. It is NOT a validation of spot-weld strength.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from weldtool import core  # noqa: E402

OC = os.path.abspath(os.path.join(HERE, "..", "..", "..", "third_party", "OpenCourant"))


def build(t_mm=1.0, metal="mild-steel", run_dir=os.path.join(HERE, "run")):
    card = core.spotweld_card(metal, t_mm)
    s = math.sqrt(card["area_mm2"])
    body = [l for l in card["text"].splitlines() if not l.startswith("#RADIOSS")]
    n = lambda i, x, y, z: f"{i:10d}{x:20.6f}{y:20.6f}{z:20.6f}"
    deck = ["#RADIOSS STARTER", "/BEGIN", "SW", "      2026         0",
            "                  Mg                  mm                   s",
            "                  Mg                  mm                   s",
            "/TITLE", "weldtool spot-weld shear smoke test"] + body + [
        "/MAT/ELAST/2", "sheet steel (elastic, smoke test only)", f"{7.85e-9:20.6g}",
        f"{210000.0:20.6g}{0.3:20.6g}",
        "/PROP/SHELL/1", "sheet", "#   Ishell    Ismstr     Ish3n    Idrill    Ipinch                  P_Thick_Fail",
        "        24         0         0         0         0                           0.0",
        "                 0.0                 0.0                 0.0                 0.0                 0.0",
        f"{0:10d}{'':10s}{t_mm:20.6g}{0.0:20.6g}{1:20d}{1:10d}{0:10d}",
        "/PROP/TYPE43/2", "spotweld", "#   Ismstr                                                                            True_thickness",
        f"{0:10d}" + " " * 70 + f"{0.0:20.6g}",
        "/PART/1", "bottom sheet", "         1         2",
        "/PART/2", "top sheet", "         1         2",
        "/PART/3", "spotweld", "         2         1",
        "/NODE",
        n(1, 0, 0, 0), n(2, s, 0, 0), n(3, s, s, 0), n(4, 0, s, 0),
        n(5, 0, 0, 1), n(6, s, 0, 1), n(7, s, s, 1), n(8, 0, s, 1),
        "/SHELL/1", f"{1:10d}{1:10d}{2:10d}{3:10d}{4:10d}",
        "/SHELL/2", f"{2:10d}{5:10d}{6:10d}{7:10d}{8:10d}",
        "/BRICK/3", "".join(f"{v:10d}" for v in (3, 1, 2, 3, 4, 5, 6, 7, 8)),
        "/GRNOD/NODE/1", "bottom", "".join(f"{v:10d}" for v in (1, 2, 3, 4)),
        "/GRNOD/NODE/2", "top", "".join(f"{v:10d}" for v in (5, 6, 7, 8)),
        "/BCS/1", "clamp bottom", "#  Tra rot   skew_ID  grnod_ID", "   111 111         0         1",
        "/BCS/2", "top: only X free", "#  Tra rot   skew_ID  grnod_ID", "   011 111         0         2",
        "/FUNCT/9", "unit", "                 0.0                 1.0", "                 1.0                 1.0",
        "/IMPVEL/1", "pull top in X",
        "#funct_IDT       Dir   skew_ID sensor_ID  grnod_ID  frame_ID     Icoor",
        "         9         X         0         0         2         0         0",
        "#            Scale_x             Scale_y              Tstart               Tstop",
        "                 1.0              1000.0                 0.0                 0.0",
        "/TH/BRIC/1", "weld", "#var", "DEF", "#obj", "         3",
        "/TH/NODE/2", "top node", "#var", "DEF", "#  node_ID   Iskew", "         5         0",
        "/END"]
    engine = ["/RUN/SW/1", f"{3.0e-3:20.6g}", "/TFILE/4", f"{1.0e-5:20.6g}", "/PRINT/-1000", "/END"]
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "SW_0000.rad"), "w") as fh:
        fh.write("\n".join(deck) + "\n")
    with open(os.path.join(run_dir, "SW_0001.rad"), "w") as fh:
        fh.write("\n".join(engine) + "\n")
    return card, run_dir


def run(run_dir):
    env = dict(os.environ, RAD_CFG_PATH=os.path.join(OC, "hm_cfg_files"),
               LD_LIBRARY_PATH=os.path.join(OC, "extlib", "hm_reader", "linux64") + ":" +
               os.path.join(OC, "extlib", "h3d", "lib", "linux64"),
               OMP_STACKSIZE="400m", OMP_NUM_THREADS="1")
    ex = os.path.join(OC, "exec")
    for cmd, log in (([os.path.join(ex, "starter_linux64_gf"), "-i", "SW_0000.rad", "-np", "1"], "starter.log"),
                     ([os.path.join(ex, "engine_linux64_gf"), "-i", "SW_0001.rad"], "engine.log"),
                     ([os.path.join(ex, "th_to_csv_linux64_gf"), "SWT01"], "th2csv.log")):
        with open(os.path.join(run_dir, log), "w") as fh:
            subprocess.run(cmd, cwd=run_dir, env=env, stdout=fh, stderr=subprocess.STDOUT, timeout=600)


if __name__ == "__main__":
    card, d = build()
    print(f"card tau={card['tau_MPa']} MPa sigma_n={card['sigma_n_MPa']} MPa area={card['area_mm2']} mm2")
    if os.path.isdir(OC) and "--no-run" not in sys.argv:
        run(d)
        print("ran OpenCourant in", d)
