# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Re-render forge/docs/img/crush-parity.png in the Strata style. Same data
(data/crush-theory-check.csv), same axes, same captions as scripts/crush_plots.py;
only the styling changes. Writes graph/crush-parity-strata-{light,dark}.png."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
G = "/usr/share/fonts/truetype/sand-box/google/"
def _static_plex():
    """Matplotlib cannot pick weights from a variable font, so cut static 400/600
    instances (OFL permits this) into a temp dir at run time; nothing is stored in the repo."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont
    import tempfile
    out = os.path.join(tempfile.gettempdir(), "strata-fonts"); os.makedirs(out, exist_ok=True)
    for w, name in ((400, "Regular"), (600, "SemiBold")):
        p = os.path.join(out, f"IBMPlexSans-{name}.ttf")
        if not os.path.exists(p):
            f = instantiateVariableFont(TTFont(G + "IBM Plex Sans/IBMPlexSans-VariableFont_wdth,wght.ttf"), {"wght": w, "wdth": 100}, updateFontNames=True)
            f.save(p)
        font_manager.fontManager.addfont(p)
    font_manager.fontManager.addfont(G + "IBM Plex Mono/IBMPlexMono-Regular.ttf")
_static_plex()
MONO = font_manager.FontProperties(fname=G + "IBM Plex Mono/IBMPlexMono-Regular.ttf")

def rows():
    with open(os.path.join(REPO, "data", "crush-theory-check.csv")) as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))

# one hue family for measured data (blue = physical test), told apart by marker
SRC = {"park2022": ("Park et al. 2022 (data: Jung 1997), quasi-static", 0, "o"),
       "aj1984": ("Abramowicz & Jones 1984", 1, "s"),
       "aj1986": ("Abramowicz & Jones 1986", 2, "D"),
       "aljawi2002": ("Aljawi 2002, quasi-static", 3, "^")}

def parity(R, dark):
    styles = [os.path.join(HERE, "strata.mplstyle")] + ([os.path.join(HERE, "strata-dark.mplstyle")] if dark else [])
    with plt.style.context(styles):
        cyc = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        ink = plt.rcParams["text.color"]; sec = "#8E97A1" if dark else "#5A6470"
        bg = plt.rcParams["axes.facecolor"]
        fig, ax = plt.subplots(figsize=(7.6, 7.0))
        fig.subplots_adjust(bottom=0.25, top=0.88, right=0.95)
        hi = max(max(float(r["mean_force_kN"]), float(r["theory_CS6844_kN"])) for r in R) * 1.12
        lo = 8
        xs = np.geomspace(lo, hi, 50)
        # the corridor: +-10 % band drawn as two thin walls with a faint fill (the brand device)
        ax.fill_between(xs, xs * 0.9, xs * 1.1, color=sec, alpha=0.13, lw=0, label="±10 % band")
        for k in (0.9, 1.1):
            ax.plot(xs, xs * k, color=sec, lw=0.8)
        ax.plot(xs, xs, color=ink, lw=1.1, ls=(0, (5, 3)), label="1:1 (theory = measured)")
        for key, (lab, ci, mk) in SRC.items():
            col = cyc[ci]
            sub = [r for r in R if r["source_key"] == key]
            for load, fill in (("quasi-static", True), ("dynamic", False)):
                s = [r for r in sub if r["loading"] == load]
                if not s:
                    continue
                x = [float(r["theory_CS6844_kN"]) for r in s]
                y = [float(r["mean_force_kN"]) for r in s]
                ax.scatter(x, y, s=42, marker=mk, facecolor=col if fill else bg, edgecolor=col, lw=1.4,
                           label=f"{lab}" + ("" if key in ("park2022", "aljawi2002") else f", {load}"), zorder=3)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
        ax.set_xlabel("Predicted mean crushing force, closed-form theory [kN]")
        ax.set_ylabel("Measured mean crushing force [kN]")
        within = sum(abs(float(r["err_CS6844_pct"])) <= 10 for r in R)
        ax.set_title(f"Axial crush of thin-walled steel tubes: measured vs theory\n"
                     f"{len(R)} tests, {within} within ±10 %", fontsize=12)
        ax.legend(loc="upper left")
        fig.text(0.015, 0.012, "Data: Park, Cho & Kim 2022, Materials 15:2107 (Tables 1, 2, 4; tests by Jung 1997);\n"
                 "Abramowicz & Jones 1984, IJIE 2:179 (Tables 1-4); Abramowicz & Jones 1986, IJIE 4:243 (Tables 1, 3-6);\n"
                 "Aljawi 2002, 6th Saudi Eng. Conf.\nTheory: A&J 1984 eq.33 / 1986 eq.19 (square, symmetric), 1986 eq.22/23 (mode B / extensional),\n"
                 "1986 eq.46 (circular); sigma0 = sigma_u; Cowper-Symonds D = 6844 1/s, p = 3.91 (A&J eq.25).\n"
                 "Computed by scripts/crush_theory.py. Log axes. Hollow = dynamic drop-hammer test.",
                 fontsize=6.9, color=sec, ha="left", va="bottom", fontproperties=MONO)
        # provenance chip: status of this figure under the colour rule
        fig.text(0.975, 0.955, "PUBLISHED TESTS vs THEORY · no simulation shown", fontproperties=MONO, fontsize=7.4,
                 color=sec, ha="right", va="bottom")
        p = os.path.join(HERE, f"crush-parity-strata-{'dark' if dark else 'light'}.png")
        fig.savefig(p); plt.close(fig); return p

if __name__ == "__main__":
    R = rows()
    print(parity(R, False)); print(parity(R, True))
