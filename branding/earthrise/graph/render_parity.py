# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Re-renders the README crush-parity graph in the Earthrise style (light and dark).
Data and logic are the same as scripts/crush_plots.py::parity (data/crush-theory-check.csv);
only styling differs. Writes into branding/earthrise/graph/ only."""
import os, sys
sys.dont_write_bytecode = True  # do not leave __pycache__ in scripts/
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import crush_plots  # noqa: E402  (reuse rows(); its rcParams are replaced below)

G = "/usr/share/fonts/truetype/sand-box/google/"
for f in ("Inter/Inter-VariableFont_opsz,wght.ttf", "IBM Plex Mono/IBMPlexMono-Regular.ttf"):
    if os.path.exists(G + f):
        font_manager.fontManager.addfont(G + f)

def parity(R, dark=False):
    plt.rcdefaults()
    plt.style.use(os.path.join(HERE, "earthrise.mplstyle"))
    if dark:
        plt.style.use(os.path.join(HERE, "earthrise-dark.mplstyle"))
    c = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    ink = plt.rcParams["text.color"]
    sub_col = "#9FB3C8" if dark else "#4A5D73"
    band = "#1FB5A8" if dark else "#0E7C74"
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
    # the ±10 % band is drawn like a thin atmosphere around the 1:1 line
    ax.fill_between(xs, xs * 0.9, xs * 1.1, color=band, alpha=0.13 if not dark else 0.18, lw=0, label="±10 % band")
    ax.plot(xs, xs, color=ink, lw=0.9, alpha=0.85)
    for key, (lab, col, mk) in SRC.items():
        sub = [r for r in R if r["source_key"] == key]
        for load, fill in (("quasi-static", True), ("dynamic", False)):
            s = [r for r in sub if r["loading"] == load]
            if not s:
                continue
            x = [float(r["theory_CS6844_kN"]) for r in s]
            y = [float(r["mean_force_kN"]) for r in s]
            ax.scatter(x, y, s=40, marker=mk, facecolor=col if fill else bg, edgecolor=col, lw=1.4,
                       label=f"{lab}" + ("" if key in ("park2022", "aljawi2002") else f", {load}"), zorder=3)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_xlabel("Predicted mean crushing force, closed-form theory [kN]")
    ax.set_ylabel("Measured mean crushing force [kN]")
    within = sum(abs(float(r["err_CS6844_pct"])) <= 10 for r in R)
    fig.text(0.12, 0.945, "Axial crush of thin-walled steel tubes: measured vs theory", fontsize=13.5, color=ink, ha="left")
    fig.text(0.12, 0.912, f"{len(R)} tests, {within} within ±10 %", fontsize=10.5, color=sub_col, ha="left")
    # small brand cue: the sun dot marks the title, nothing else
    fig.patches.append(matplotlib.patches.Circle((0.095, 0.951), 0.0075, transform=fig.transFigure, color="#F5A524"))
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    fig.text(0.02, 0.015, "Data: Park, Cho & Kim 2022, Materials 15:2107 (Tables 1, 2, 4; tests by Jung 1997); Abramowicz & Jones 1984, IJIE 2:179 "
             "(Tables 1-4);\nAbramowicz & Jones 1986, IJIE 4:243 (Tables 1, 3-6); Aljawi 2002, 6th Saudi Eng. Conf.\nTheory: A&J 1984 eq.33 / 1986 eq.19 "
             "(square, symmetric), 1986 eq.22/23 (mode B / extensional),\n1986 eq.46 (circular); sigma0 = sigma_u; Cowper-Symonds D = 6844 1/s, p = 3.91 "
             "(A&J eq.25).\nComputed by scripts/crush_theory.py. Log axes. Hollow = dynamic drop-hammer test.",
             fontsize=7.2, color=sub_col, ha="left", va="bottom", linespacing=1.45)
    p = os.path.join(HERE, f"crush-parity-earthrise-{'dark' if dark else 'light'}.png")
    fig.savefig(p); plt.close(fig); return p

if __name__ == "__main__":
    R = crush_plots.rows()
    print(parity(R)); print(parity(R, dark=True))
