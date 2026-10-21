# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Re-render the README crush parity graph (forge/docs/img/crush-parity.png) in the Wind & Shell style.
Reads data/crush-theory-check.csv through scripts/crush_plots.rows(); no number, caption or source changes.
Run from the repo root:  .venv/bin/python branding/windshell/graph/render_parity.py
Writes crush-parity-windshell-light.png and -dark.png next to this file."""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import crush_plots  # noqa: E402  (only rows() is used; its rcParams are reset below)

G = "/usr/share/fonts/truetype/sand-box/google/"
for f in ("IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf", "IBM Plex Mono/IBMPlexMono-Regular.ttf"):
    if os.path.exists(G + f):
        font_manager.fontManager.addfont(G + f)

def parity(R, dark=False):
    plt.rcdefaults()
    plt.style.use([os.path.join(HERE, "windshell.mplstyle")] + ([os.path.join(HERE, "windshell-dark.mplstyle")] if dark else []))
    c = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    ink = plt.rcParams["text.color"]
    sub = "#9AA3AD" if dark else "#5A6470"
    edge = "#7FA8D6" if dark else "#2F5F8F"           # corridor edges: measured-test colour
    fill = "#24323F" if dark else "#E9DFCB"           # corridor fill: shell sand / shell graphite
    model = "#F26B1D" if dark else "#B5470C"          # the model line: orange
    bg = plt.rcParams["axes.facecolor"]
    SRC = {"park2022": ("Park et al. 2022 (data: Jung 1997), quasi-static", c[0], "o"),
           "aj1984": ("Abramowicz & Jones 1984", c[1], "s"),
           "aj1986": ("Abramowicz & Jones 1986", c[2], "D"),
           "aljawi2002": ("Aljawi 2002, quasi-static", c[3], "^")}
    fig, ax = plt.subplots(figsize=(7.6, 7.0))
    fig.subplots_adjust(bottom=0.23, top=0.88, left=0.12, right=0.96)
    hi = max(max(float(r["mean_force_kN"]), float(r["theory_CS6844_kN"])) for r in R) * 1.12
    lo = 8
    xs = np.geomspace(lo, hi, 50)
    # the ±10 % band is drawn as the brand's corridor: two thin edges, a quiet fill, the model line inside
    ax.fill_between(xs, xs * 0.9, xs * 1.1, color=fill, alpha=0.9 if not dark else 1.0, lw=0, label="±10 % band", zorder=1)
    ax.plot(xs, xs * 0.9, color=edge, lw=0.8, zorder=2); ax.plot(xs, xs * 1.1, color=edge, lw=0.8, zorder=2)
    ax.plot(xs, xs, color=model, lw=1.4, zorder=2)
    for key, (lab, col, mk) in SRC.items():
        sub_rows = [r for r in R if r["source_key"] == key]
        for load, filled in (("quasi-static", True), ("dynamic", False)):
            s = [r for r in sub_rows if r["loading"] == load]
            if not s:
                continue
            x = [float(r["theory_CS6844_kN"]) for r in s]
            y = [float(r["mean_force_kN"]) for r in s]
            ax.scatter(x, y, s=40, marker=mk, facecolor=col if filled else bg, edgecolor=col, lw=1.4,
                       label=f"{lab}" + ("" if key in ("park2022", "aljawi2002") else f", {load}"), zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("Predicted mean crushing force, closed-form theory [kN]")
    ax.set_ylabel("Measured mean crushing force [kN]")
    within = sum(abs(float(r["err_CS6844_pct"])) <= 10 for r in R)
    fig.text(0.12, 0.945, "Axial crush of thin-walled steel tubes: measured vs theory", fontsize=13.5, color=ink, ha="left")
    fig.text(0.12, 0.912, f"{len(R)} tests, {within} within ±10 %", fontsize=10.5, color=sub, ha="left", family="monospace")
    # brand cue: a short orange crush-cap bar left of the title, nothing else
    fig.patches.append(matplotlib.patches.FancyBboxPatch((0.088, 0.941), 0.012, 0.024, boxstyle="round,pad=0,rounding_size=0.004",
                                                        transform=fig.transFigure, color=model))
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    # caption = the evidence plate: unchanged text from scripts/crush_plots.py, set in Plex Mono
    fig.text(0.02, 0.015, "Data: Park, Cho & Kim 2022, Materials 15:2107 (Tables 1, 2, 4; tests by Jung 1997); Abramowicz & Jones 1984, IJIE 2:179 "
             "(Tables 1-4);\nAbramowicz & Jones 1986, IJIE 4:243 (Tables 1, 3-6); Aljawi 2002, 6th Saudi Eng. Conf.\nTheory: A&J 1984 eq.33 / 1986 eq.19 "
             "(square, symmetric), 1986 eq.22/23 (mode B / extensional),\n1986 eq.46 (circular); sigma0 = sigma_u; Cowper-Symonds D = 6844 1/s, p = 3.91 "
             "(A&J eq.25).\nComputed by scripts/crush_theory.py. Log axes. Hollow = dynamic drop-hammer test.",
             fontsize=6.1, color=sub, ha="left", va="bottom", linespacing=1.5, family="monospace")
    p = os.path.join(HERE, f"crush-parity-windshell-{'dark' if dark else 'light'}.png")
    fig.savefig(p); plt.close(fig); return p

if __name__ == "__main__":
    R = crush_plots.rows()
    print(parity(R)); print(parity(R, dark=True))
