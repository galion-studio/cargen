<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# weldtool: welding start parameters, HAZ knockdowns and spot-weld crash cards

> **STARTING POINT ONLY. VERIFY WITH TEST COUPONS** before any structural or safety use. Every value comes from a cited public table (see [welding.md](welding.md)). Nothing is interpolated or invented. When no source exists, the tool says so.

Pure Python 3 standard library, MIT. Run it from this folder.

```bash
python3 -m weldtool list                                    # metals and processes
python3 -m weldtool suggest --metal al-6082-t6-sheet -t 3 -p mig   # parameters + HAZ
python3 -m weldtool params  --metal mild-steel -t 1 -p spot        # NSRW class A/B/C schedule
python3 -m weldtool haz     --metal dp980 -p spot                  # knockdown factors
python3 -m weldtool card    --metal mild-steel -t 1 --out sw.rad   # Radioss LAW59 + FAIL/CONNECT
python3 -m weldtool card    --metal al-6082-t6-sheet -t 2 --shear-kn 3 --normal-kn 1 --density 2.7e-9
python3 -m weldtool sources                                 # source ids and URLs
```

Add `--json` to any command for machine-readable output. Processes are `mig`, `tig`, `spot`, `laser` and `fsw`. Errors exit with code 2.

## What it does

- **params** finds the nearest table row(s) for your thickness: Miller 211 MIG, Lincoln TIG, NSRW spot or EAA Al spot.
  - A row within 5 % is labelled `nearest-row (within 5%)`.
  - Otherwise it shows both neighbouring rows (`between-rows`), or flags `below-table` / `above-table`.
  - Laser and FSW have no tables. It returns only cited reference results.
- **haz** returns ρ(yield) and ρ(UTS) knockdowns, either from a code (EN 1999) or measured (hardness or tensile ratio). It adds the b_haz width each side and process notes.
- **card** writes `/MAT/LAW59` + `/FAIL/CONNECT` + two flat `/FUNCT` yield curves for a `/PROP/TYPE43` spotweld brick.
  - Nugget = 4√t. Shear is the AWS C1.1 minimum. Normal = TWI CTS/TSS × shear. Stress = force / nugget area.
  - E, G and failure displacements are Altair example values. **Calibrate them.**
  - For non-steel metals you must pass `--shear-kn`, `--normal-kn` and `--density`, because no open source formula exists.
  - The property, brick and `/INTER/TYPE2` tie are not generated.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Result on 2026-10-21 (Europe/Zagreb): **34 tests, OK** (about 2.5 s).
- 33 unit tests cover data integrity, spot checks against the source tables, lookups, HAZ, the card's numbers and column format, and the CLI.
- 1 solver smoke test builds `smoke/make_smoke_deck.py` and runs it in local OpenCourant (`third_party/OpenCourant`). It is skipped if the solver is absent. The test pulls one 1 mm mild-steel weld in shear and checks four things:
  - the starter reports 0 errors;
  - the engine ends in normal termination;
  - the shear stress plateau equals the card's τ (168.8 MPa);
  - the weld is deleted at u_maxT = 1.8 mm.

## Limitations

- Machine-specific charts (Millermatic 211, Lincoln Square Wave) are not general laws.
- Gauge columns are mapped with the steel gauge system.
- There is no Al spot schedule by thickness, no Mg/Ti TIG table and no Mg MIG data. No mild-steel HAZ knockdown was found.
- Flat yield curves and example stiffness and failure values are a simplification. The card passes the solver smoke test, but its strength is not validated.
