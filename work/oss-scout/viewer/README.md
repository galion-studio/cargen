<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 3000 galion-studio -->
# viewer

This is a single-page [three.js](https://github.com/mrdoob/three.js) (MIT) STL viewer. It has no build step: an import map points at a local `node_modules/three` (pinned 0.186.1). The view is Z-up and the units are mm.

To run it, first run `npm install` here. Then run `python3 -m http.server 8765` from `oss-scout/` and open `http://127.0.0.1:8765/viewer/`.
By default it loads `../truck-spike/out/{plate,cylinder}.stl`. To load other files, use `?stl=a.stl,b.stl`.
When loading finishes, the page title ends with `[ready]` and `window.__forgeReady` lists the triangle counts. Headless tests can check either one.
