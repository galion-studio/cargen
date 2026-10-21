<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# oss-scout

The permissive-licence repo scout is in [CATALOG.md](CATALOG.md). This folder also holds two spikes that run together:

1. `truck-spike/` (Rust, truck, Apache-2.0) builds exact B-rep parts, tessellates them, checks the mesh volume against the closed-form volume, and writes STL.
2. `viewer/` (three.js, MIT) is a web page that loads those STLs with orbit controls.

```bash
cd truck-spike && cargo run --release        # writes out/plate.stl, out/cylinder.stl; exit 0 = PASS
cd ../viewer && npm install                  # pins three 0.186.1 locally
cd .. && python3 -m http.server 8765         # then open http://127.0.0.1:8765/viewer/
```

Measured output on the box, 2026-10-21 (tolerance 0.05 mm):

```
plate     tris=    12 mesh_vol=    100000.0 mm3 exact=    100000.0 mm3 rel_err=1.46e-16 PASS
cylinder  tris=  3760 mesh_vol=    125385.4 mm3 exact=    125663.7 mm3 rel_err=2.21e-3 PASS
```

The cylinder error is the chord error of the tessellation (the mesh volume is smaller than the true circle's), not kernel error. A headless Chrome render is in `viewer/screenshot.png`.
Build artefacts (`target/`, `out/`, `node_modules/`) are listed in `.gitignore`.
