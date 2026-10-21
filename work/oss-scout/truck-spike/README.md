<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# truck-spike

This spike checks that [truck](https://github.com/ricosjp/truck) (Apache-2.0) can serve as Forge's geometry kernel.

- `plate(w,d,h)` builds a solid by sweeping a vertex into an edge, then a face, then a solid. `cylinder(r,h)` revolves a point into a circle, caps it, and extrudes it.
- Each solid is tessellated with `triangulation(0.05)`. The mesh volume (divergence theorem) is checked against the closed-form volume, with relative error < 1e-2 as the pass bar.
- It writes binary STL to `out/`.

Run it with `cargo run --release`. It needs network access the first time, to pull the crates.
It is a standalone crate with its own `[workspace]`, so it is not part of `forge/`. To adopt it, add `truck-modeling = "0.6"` and `truck-meshalgo = "0.4"` to a new `forge-geom` crate.
Every transitive dependency is permissive (checked with `cargo metadata`).
