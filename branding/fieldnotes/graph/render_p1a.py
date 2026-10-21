# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Re-renders the README P1a graph (forge/docs/img/p1a-force-energy.png) in the Field Notes style,
light and dark. Data and honesty rules are the same as scripts/crush_plots.py::p1a(): the experiment
curve comes from forge/data/p1a/park2022_us2_fig3_digitized.csv, and a simulated curve is drawn ONLY
if a real P1a result file exists (same search paths). Only styling differs. Writes into
branding/fieldnotes/graph/ only."""
import glob, json, os, sys
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
G = "/usr/share/fonts/truetype/sand-box/google/"
sys.path.insert(0, os.path.join(HERE, "..", "src"))
try:  # make static IBM Plex Sans 400/600 instances from the OFL variable font (cached in src/.fontcache)
    from fn_lib import _font
    _font("sans"); _font("sans-semi")
except Exception as e:
    print("Plex Sans instances unavailable, falling back:", e)
CACHE = os.path.join(HERE, "..", "src", ".fontcache")
FONT_FILES = [os.path.join(CACHE, "IBMPlexSans-VariableFont_wdth,wght-wght400_wdth100.ttf"),
              os.path.join(CACHE, "IBMPlexSans-VariableFont_wdth,wght-wght600_wdth100.ttf"),
              G + "IBM Plex Mono/IBMPlexMono-Regular.ttf", G + "IBM Plex Mono/IBMPlexMono-Medium.ttf"]
for f in FONT_FILES:
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
MONO = "IBM Plex Mono"

def load():
    exp_csv = os.path.join(ROOT, "forge", "data", "p1a", "park2022_us2_fig3_digitized.csv")
    d, F = [], []
    with open(exp_csv) as fh:
        for l in fh:
            if l[0].isdigit():
                a, b = l.split(",")[:2]; d.append(float(a)); F.append(float(b))
    sim = None
    for cand in sorted(glob.glob(os.path.join(ROOT, "forge", "docs", "physics", "*.json")) +
                       glob.glob(os.path.join(ROOT, "forge", "results", "**", "*.json"), recursive=True) +
                       glob.glob(os.path.join(ROOT, "forge", "runs", "p1a*", "*.json"))):
        try:
            j = json.load(open(cand))
        except Exception:
            continue
        curve = j.get("force_displacement") or j.get("sim_curve") or j.get("curve")
        if curve:
            sim = (cand, curve); break
    return np.array(d), np.array(F), sim

def energy(d, F):
    return np.concatenate([[0], np.cumsum(0.5 * (F[1:] + F[:-1]) * np.diff(d))]) / 1e3  # kN*mm = J -> kJ

def render(dark=False):
    plt.rcdefaults()
    plt.style.use(os.path.join(HERE, "fieldnotes.mplstyle"))
    if dark:
        plt.style.use(os.path.join(HERE, "fieldnotes-dark.mplstyle"))
    rc = plt.rcParams
    test, simc, pend = rc["axes.prop_cycle"].by_key()["color"][:3]
    ink = rc["text.color"]; sub = "#B9B09C" if dark else "#5E5141"; line = rc["axes.edgecolor"]
    d, F, sim = load(); E = energy(d, F)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 6.2))
    fig.subplots_adjust(bottom=0.36, top=0.86, wspace=0.2, left=0.065, right=0.985)
    a1.plot(d, F, color=test, lw=1.4, label="Experiment US-2 (digitized Fig. 3)")
    a1.axhline(101.0, color=test, ls=(0, (5, 3)), lw=0.9, label="Experiment Pm = 101.0 kN (Table 4)")
    a2.plot(d, E, color=test, lw=1.6, label="Experiment US-2 (integrated digitized curve)")
    if sim:
        sd = np.array([p[0] for p in sim[1]]); sf = np.array([p[1] for p in sim[1]])
        a1.plot(sd, sf, color=simc, lw=1.4, label=f"OpenCourant P1a ({os.path.basename(sim[0])})")
        a2.plot(sd, energy(sd, sf), color=simc, lw=1.6, label="OpenCourant P1a")
    else:
        pending = Line2D([], [], color=pend, ls=(0, (1, 2.5)), lw=1.8, label="OpenCourant P1a: pending, no curve shown")
        for ax in (a1, a2):
            h, l = ax.get_legend_handles_labels()
            ax.legend(h + [pending], l + [pending.get_label()], loc="upper left")
    if sim:
        a1.legend(loc="upper left"); a2.legend(loc="upper left")
    a1.set_xlabel("Axial displacement [mm]"); a1.set_ylabel("Axial force [kN]")
    a2.set_xlabel("Axial displacement [mm]"); a2.set_ylabel("Energy absorbed [kJ]")
    a1.set_title("P1a: force vs displacement, 100×100×2.8 mm A500 tube")
    a2.set_title("P1a: energy absorbed vs displacement")
    a1.set_ylim(0, 360); a2.set_ylim(0, 38)
    for ax in (a1, a2):
        ax.set_xlim(0, 360)
        for lab in ax.get_xticklabels() + ax.get_yticklabels():
            lab.set_fontfamily(MONO); lab.set_fontsize(8.5)
    # plate header: figure number in mono, like a field-notebook plate
    fig.text(0.065, 0.945, "FIG. P1a", fontsize=9, color=sub, family=MONO, weight="medium")
    fig.text(0.13, 0.945, "Park et al. 2022, specimen US-2 (README Status, P1a)", fontsize=9, color=sub, family=MONO)
    # caption block (the evidence-plate title block): rule lines + Plex Mono key/value rows
    rows = [("SOURCE", "Park, Cho & Kim 2022, Materials 15:2107, CC BY 4.0, specimen US-2 (tests by Jung 1997), quasi-static 0.05 mm/s."),
            ("", "Curve digitized from Fig. 3 by forge/scripts/digitize_park2022_fig3.py (about ±1 mm, ±2 kN; initial spike under-resolved,"),
            ("", "Table 4 peak = 337.1 kN). Energy = trapezoidal integral of the digitized curve."),
            ("SOLVER", ("OpenCourant run, file named in legend." if sim else "OpenCourant P1a run not finished. Simulation: none yet (pending).")),
            ("MESH", ("as in the run report" if sim else "n/a, no run yet")),
            ("ERROR VS TEST", ("see report forge/docs/physics/p1a-tube-crush.md" if sim else "unvalidated: no simulated curve exists yet"))]
    y = 0.232
    fig.add_artist(Line2D([0.02, 0.985], [y + 0.035, y + 0.035], transform=fig.transFigure, color=line, lw=0.8))
    for k, v in rows:
        fig.text(0.02, y, k, fontsize=7.6, color=ink, family=MONO, weight="medium", va="center")
        fig.text(0.125, y, v, fontsize=7.6, color=sub, family=MONO, va="center")
        y -= 0.031
    fig.add_artist(Line2D([0.02, 0.985], [y + 0.012, y + 0.012], transform=fig.transFigure, color=line, lw=0.8))
    p = os.path.join(HERE, f"p1a-force-energy-fieldnotes-{'dark' if dark else 'light'}.png")
    fig.savefig(p); plt.close(fig); return p

if __name__ == "__main__":
    print(render()); print(render(dark=True))
