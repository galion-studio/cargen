# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""pycalphad smoke test: equilibrium phase fractions of binary Mg-Al
(AZ91-like Mg-9Al and AZ31-like Mg-3Al, wt%) from the open MatCalc database.

Database: mc_al_v2.037.tdb, E. Povoden-Karadeniz, TU Wien / MatCalc,
https://www.matcalc.at/index.php/databases/open-databases
Licence: ODbL 1.0 (database) + DbCL 1.0 (contents). Attribution required.
The file is an Al-alloy database (tested by its authors for 2xxx/6xxx/7xxx);
its Mg-rich side is NOT validated for Mg alloys by us. Output = solver result,
"unvalidated estimate" until checked against a measured Mg-Al solvus.

pycalphad cannot parse MatCalc-only keywords, so this script filters them
IN MEMORY (no modified database is written or distributed):
  drops REFERENCE_ELEMENT / ATTACH_CONTRIBUTION / ADD_COMPOSITION_SET,
  drops PARAMETER types other than G, L, TC, BMAGN (e.g. HMVA mobility-like
  terms), strips trailing 'REF:xxx' tags and MatCalc '> comment' text on PHASE.
Run: /workspace/cargen/.venv/bin/python forge/scripts/calphad_mgal_smoke.py
"""
import re, sys, warnings
from pathlib import Path
from pycalphad import Database, equilibrium, variables as v

ROOT = Path(__file__).resolve().parents[2]
TDB = ROOT / "data" / "calphad" / "mc_al_v2037.tdb"
KEEP_PARAMS = {"G", "L", "TC", "BMAGN"}
DROP_CMDS = {"REFERENCE_ELEMENT", "ATTACH_CONTRIBUTION", "ADD_COMPOSITION_SET"}
PHASES = ["LIQUID", "FCC_A1", "HCP_A3", "G_AL12MG17", "BETA_AL3MG2", "E_AL30MG23"]
M_AL, M_MG = 26.98154, 24.305  # g/mol, as given in the TDB ELEMENT lines


def clean_tdb(text: str) -> str:
    lines = [l for l in text.splitlines() if not l.lstrip().startswith("$")]
    out = []
    for cmd in "\n".join(lines).split("!"):
        s = cmd.strip()
        if not s:
            continue
        kw = s.split()[0].upper()
        if kw in DROP_CMDS or kw.startswith("REF"):
            continue
        if kw == "PARAMETER":
            m = re.match(r"PARAMETER\s+([A-Z0-9_]+)\(", s, re.I)
            if not m or m.group(1).upper() not in KEEP_PARAMS:
                continue
            s = re.sub(r"\s+REF:?\s*\S*\s*$", "", s)
        if kw == "PHASE":
            s = s.split(">")[0]
        out.append(s)
    return " !\n".join(out) + " !\n"


def x_al(w_al: float) -> float:
    return (w_al / M_AL) / (w_al / M_AL + (1 - w_al) / M_MG)


def main() -> int:
    warnings.filterwarnings("ignore")
    db = Database(clean_tdb(TDB.read_text(encoding="latin-1")))
    print(f"# {TDB.name}: {len(db.phases)} phases parsed; Mg-Al subset {PHASES}")
    print("alloy,w_Al,T_C,phase,mole_fraction_of_phase,X_Al_in_phase")
    for name, w in (("Mg-9Al(AZ91-like)", 0.09), ("Mg-3Al(AZ31-like)", 0.03)):
        for t_c in (200.0, 300.0, 400.0):
            eq = equilibrium(db, ["AL", "MG", "VA"], PHASES,
                             {v.X("AL"): x_al(w), v.T: t_c + 273.15, v.P: 101325, v.N: 1})
            ph = eq.Phase.values.squeeze()
            npf = eq.NP.values.squeeze()
            xal = eq.X.sel(component="AL").values.squeeze()
            for p, f, xa in zip(ph, npf, xal):
                if p:
                    print(f"{name},{w},{t_c:.0f},{p},{float(f):.4f},{float(xa):.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
