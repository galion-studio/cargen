<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 Galion / galion-studio -->
# data/calphad — third-party databases (NOT MIT)

- `mc_al_v2037.tdb` — MatCalc open thermodynamic database for Al alloys, v2.037 (2025-07-25),
  E. Povoden-Karadeniz et al., TU Wien / MatCalc Engineering. Source:
  https://www.matcalc.at/images/stories/Download/Database/mc_al_v2037.tdb
  Licence: **Open Database License (ODbL) 1.0** with **Database Contents License (DbCL) 1.0** (stated in the file header).
  Commercial use allowed. Redistribution must keep this attribution and the ODbL; any *derived database* we publish must also be ODbL (share-alike).
  The file is stored unmodified. `forge/scripts/calphad_mgal_smoke.py` filters MatCalc-only keywords in memory and does not write a derived database.
- Do **not** add pycalphad's bundled `Al-Mg_Zhong.tdb` example. Its header says "Copyright (C) NIMS 2008" (NIMS CPDDB lineage), which is a banned source family.
