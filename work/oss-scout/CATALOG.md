<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# OSS scout: permissive repos for Forge

Snapshot 2026-10-21. Stars and "last push" (UTC date) come from the GitHub API. The licence column is from the repo's actual LICENSE/COPYING file, fetched raw. **MIT** = MIT. Anything else is marked non-MIT. Plug: R = Rust crate, Py = Python package, JS = web viewer.

## Top 5 that fit now

| # | Repo | Licence | Stars | Last push | Plug | Why / risk |
|---|------|---------|------:|-----------|------|-----------|
| 1 | [ricosjp/truck](https://github.com/ricosjp/truck) | Apache-2.0 (non-MIT) | 1661 | 2026-10-19 | R | Pure-Rust B-rep kernel (NURBS, sweeps, booleans, tessellation, STEP). **Spiked.** Risk: 0.x API; nom 3 and quick-xml 0.22 deps get future-incompat warnings. |
| 2 | [mrdoob/three.js](https://github.com/mrdoob/three.js) | **MIT** | 116723 | 2026-10-21 | JS | Web viewer for forge.galion.studio. **Spiked.** Risk: breaking changes on every minor release, so pin the version. |
| 3 | [mikedh/trimesh](https://github.com/mikedh/trimesh) | **MIT** | 3706 | 2026-10-20 | Py | Mesh I/O, watertight check, mass and inertia, ray tests. It fits the existing .venv. Risk: some backends are optional extras with their own licences. |
| 4 | [kinnala/scikit-fem](https://github.com/kinnala/scikit-fem) | BSD-3-Clause (non-MIT) | 664 | 2026-10-20 | Py | Small pure-Python FEM for linear-elastic part checks (bracket, arm) against closed-form cases. Risk: you write the weak forms yourself; it is not a crash solver. |
| 5 | [peterdsharpe/AeroSandbox](https://github.com/peterdsharpe/AeroSandbox) | **MIT** | 1369 | 2026-10-20 | Py | Low-order aero and optimisation (with [NeuralFoil](https://github.com/peterdsharpe/NeuralFoil), MIT) for wings and spoilers. Risk: aircraft-oriented, no car-body CFD. |

## Full catalog (permissive)

| Area | Repo | Licence | Stars | Last push | Plug | Note / risk |
|------|------|---------|------:|-----------|------|-------------|
| CAD kernel | [elalish/manifold](https://github.com/elalish/manifold) | Apache-2.0 | 2366 | 2026-10-21 | R (manifold3d crate, C++ FFI) / JS wasm / Py | Robust mesh booleans. Needs a C++ toolchain. |
| CAD kernel | [hannobraun/fornjot](https://github.com/hannobraun/fornjot) | 0BSD | 2552 | 2026-06-19 | R | **Archived.** Do not adopt. |
| CAD (script) | [CadQuery/cadquery](https://github.com/CadQuery/cadquery) | Apache-2.0 | 5973 | 2026-10-18 | Py | Built on OCCT (LGPL-2.1) via OCP, so the LGPL obligations follow. |
| CAD (script) | [gumyr/build123d](https://github.com/gumyr/build123d) | Apache-2.0 | 3489 | 2026-10-21 | Py | Same OCCT/LGPL caveat as CadQuery. |
| Mesh | [nschloe/meshio](https://github.com/nschloe/meshio) | MIT | 2334 | 2024-07-23 | Py | Converts between many FEM mesh formats. Stale (no push since 2024). |
| Mesh | [zeux/meshoptimizer](https://github.com/zeux/meshoptimizer) | MIT | 8586 | 2026-10-14 | R/JS | Mesh simplification and compression for the viewer. |
| Mesh/viz | [pyvista/pyvista](https://github.com/pyvista/pyvista) | MIT | 3857 | 2026-10-21 | Py | Post-processing for results. Wraps VTK (BSD-3). |
| FEM | [sfepy/sfepy](https://github.com/sfepy/sfepy) | BSD-3-Clause | 846 | 2026-10-20 | Py | Broader physics than scikit-fem, but heavier. |
| FEM | [mfem/mfem](https://github.com/mfem/mfem) | BSD-3-Clause | 2270 | 2026-10-21 | C++ lib / PyMFEM | High-order HPC FEM. Heavy build. |
| FEM | [febiosoftware/FEBio](https://github.com/febiosoftware/FEBio) | MIT | 290 | 2026-10-13 | CLI program | Nonlinear solid mechanics (biomechanics focus). Could run as a solver program, the same way as forge-crash. |
| Aero | [peterdsharpe/NeuralFoil](https://github.com/peterdsharpe/NeuralFoil) | MIT | 495 | 2026-10-07 | Py | Fast airfoil polars (learned model). |
| Web 3D | [gkjohnson/three-mesh-bvh](https://github.com/gkjohnson/three-mesh-bvh) | MIT | 3524 | 2026-10-18 | JS | Fast picking and raycasting on big meshes. |
| Web 3D | [pmndrs/react-three-fiber](https://github.com/pmndrs/react-three-fiber) | MIT | 33133 | 2026-10-21 | JS | Only if the dashboard is React. Add [drei](https://github.com/pmndrs/drei) (MIT, 10026 stars). |
| Web 3D | [google/model-viewer](https://github.com/google/model-viewer) | Apache-2.0 | 8286 | 2026-10-09 | JS | Drop-in glTF viewer tag. Not for CAE results. |
| Web 3D | [BabylonJS/Babylon.js](https://github.com/BabylonJS/Babylon.js) | Apache-2.0 | 26206 | 2026-10-21 | JS | Alternative to three.js. |
| Game/render | [bevyengine/bevy](https://github.com/bevyengine/bevy) | MIT OR Apache-2.0 | 49181 | 2026-10-21 | R | Play-layer engine. Rapier has Bevy plugins. Its API changes every release. |
| Formats | [gltf-rs/gltf](https://github.com/gltf-rs/gltf) | MIT OR Apache-2.0 | 644 | 2026-05-11 | R | glTF export from Rust to the viewer. |
| Geometry | [dimforge/parry](https://github.com/dimforge/parry) | Apache-2.0 | 885 | 2026-10-06 | R | Already pulled in by rapier3d. Distance and contact queries. |
| Math | [dimforge/nalgebra](https://github.com/dimforge/nalgebra) | Apache-2.0 | 4803 | 2026-09-30 | R | Linear algebra (rapier uses it). |
| Robotics | [openrr/k](https://github.com/openrr/k) | Apache-2.0 | 221 | 2026-06-19 | R | FK/IK chains for welding-robot arms. Pair with [urdf-rs](https://github.com/openrr/urdf-rs) (Apache-2.0, 50 stars). |
| Robotics | [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | Apache-2.0 | 15799 | 2026-10-21 | Py/C | Contact-rich robot simulation. |
| Robotics | [stack-of-tasks/pinocchio](https://github.com/stack-of-tasks/pinocchio) | BSD-2-Clause | 3804 | 2026-10-21 | Py/C++ | Rigid-body dynamics and derivatives. |
| Robotics | [petercorke/robotics-toolbox-python](https://github.com/petercorke/robotics-toolbox-python) | MIT | 3549 | 2026-10-21 | Py | Teaching-grade kinematics with many robot models. |
| Robotics | [Phylliade/ikpy](https://github.com/Phylliade/ikpy) | Apache-2.0 | 1038 | 2026-08-30 | Py | Simple IK from URDF. |
| Physics | [bulletphysics/bullet3](https://github.com/bulletphysics/bullet3) | zlib (except `Extras/`, `examples/ThirdPartyLibs`) | 14806 | 2026-10-09 | Py (pybullet) | Mature, but Rapier already covers this. |
| CNC | [GridSpace/grid-apps](https://github.com/GridSpace/grid-apps) | MIT | 923 | 2026-10-04 | JS | Kiri:Moto slicer and CAM (FDM, CNC, laser) in the browser. |
| CNC | [Michael-F-Bryan/gcode-rs](https://github.com/Michael-F-Bryan/gcode-rs) | MIT OR Apache-2.0 | 109 | 2026-08-09 | R | G-code parser (no_std). Use it to read and verify toolpaths. |
| CNC | [sameer/svg2gcode](https://github.com/sameer/svg2gcode) | MIT | 444 | 2026-10-15 | R | 2D profile to G-code (plasma, laser, router). |
| Welding | [BAMWelDX/weldx](https://github.com/BAMWelDX/weldx) | BSD-3-Clause | 31 | 2026-10-18 | Py | Welding experiment data format (weld seams, groove geometry, process params). Small community. |
| Materials | [materialsproject/pymatgen](https://github.com/materialsproject/pymatgen) | MIT | 2001 | 2026-10-20 | Py | Materials analysis and the Materials Project API client. Check the data terms separately from the code licence. |
| Materials | [hackingmaterials/matminer](https://github.com/hackingmaterials/matminer) | BSD-style (LBNL modified BSD) | 622 | 2026-10-19 | Py | Materials datasets and featurizers. |
| Materials | [pycalphad/pycalphad](https://github.com/pycalphad/pycalphad) | MIT | 423 | 2026-10-21 | Py | Already in .venv. |
| Topology opt. | [williamhunter/topy](https://github.com/williamhunter/topy) | MIT | 577 | 2022-08-31 | Py | Stale (no push since 2022). Use it as a reference only. |
| UI | [emilk/egui](https://github.com/emilk/egui) | MIT OR Apache-2.0 | 31645 | 2026-10-21 | R | Native and wasm tool UI. |
| UI | [cocopon/tweakpane](https://github.com/cocopon/tweakpane) | MIT | 4611 | 2026-03-15 | JS | Parameter panels for the viewer. |
| UI | [georgealways/lil-gui](https://github.com/georgealways/lil-gui) | MIT | 1649 | 2025-10-12 | JS | Minimal parameter panel (three.js examples use it). |
| UI | [pmndrs/leva](https://github.com/pmndrs/leva) | MIT | 6259 | 2025-11-09 | JS | React parameter panel. |
| State | [pmndrs/zustand](https://github.com/pmndrs/zustand) | MIT | 58848 | 2026-10-14 | JS | React state, if needed. |

## Important but copyleft: do not link. Run as a separate program, or skip.

| Repo | Licence (from file) | Stars | Last push | Use |
|------|---------------------|------:|-----------|-----|
| [Open-Cascade-SAS/OCCT](https://github.com/Open-Cascade-SAS/OCCT) | LGPL-2.1 (+ OCCT exception) | 3045 | 2026-10-20 | Industrial B-rep and STEP. Behind CadQuery and build123d. Dynamic linking only. |
| [FreeCAD/FreeCAD](https://github.com/FreeCAD/FreeCAD) | LGPL-2.1 | 34620 | 2026-10-21 | Full CAD, FEM workbench and CAM. Exchange files with it instead of linking. |
| [aewallin/opencamlib](https://github.com/aewallin/opencamlib) | LGPL-2.1 | 546 | 2026-10-17 | 3-axis CAM toolpaths (drop-cutter, waterline). |
| [su2code/SU2](https://github.com/su2code/SU2) | LGPL-2.1 | 1834 | 2026-10-21 | CFD solver, run as a separate program. |
| [FEniCS/dolfinx](https://github.com/FEniCS/dolfinx) | LGPL-3.0 | 1231 | 2026-10-21 | FEM framework. |
| [OpenFOAM/OpenFOAM-dev](https://github.com/OpenFOAM/OpenFOAM-dev) | GPL-3.0 | 2278 | 2026-10-21 | The reference open CFD for car bodies. Run as a separate program, like OpenCourant. |
| [ElmerCSC/elmerfem](https://github.com/ElmerCSC/elmerfem) | GPL-2.0 (LICENSE.md) | 1741 | 2026-10-20 | Multiphysics FEM, run as a separate program. |
| [openscad/openscad](https://github.com/openscad/openscad) | GPL-2.0 (+ CGAL exception) | 10480 | 2026-10-18 | Script CAD. Skip, because truck and manifold cover it. |

Not on GitHub, so not checked here: gmsh, CalculiX.
