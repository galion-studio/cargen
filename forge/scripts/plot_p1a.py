# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Galion / galion-studio
"""Plot digitized experiment vs simulated force-displacement curves.
usage: plot_p1a.py OUT.png EXP.csv LABEL1=SIM1.csv [LABEL2=SIM2.csv ...]"""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out, exp = sys.argv[1], sys.argv[2]
load = lambda p: np.loadtxt(p, delimiter=",", comments="#", skiprows=0, usecols=(0, 1), ndmin=2) if False else np.genfromtxt(p, delimiter=",", comments="#", names=True)
fig, ax = plt.subplots(figsize=(10, 5))
e = load(exp)
ax.plot(e["displacement_mm"], e["force_kN"], "k-", lw=2, label="Experiment US-2 (digitized, Park et al. 2022 Fig. 3)")
for spec in sys.argv[3:]:
    lab, p = spec.split("=", 1)
    s = load(p)
    ax.plot(s["displacement_mm"], s["force_kN"], lw=1, label=f"OpenCourant: {lab} (simulation)")
ax.axhline(101.0, color="k", ls=":", lw=1, label="Measured P_m = 101.0 kN (Table 4)")
ax.axvline(343, color="gray", ls="--", lw=0.8)
ax.set_xlim(0, 360); ax.set_ylim(0, 400)
ax.set_xlabel("Platen displacement (mm)"); ax.set_ylabel("Force (kN)")
ax.set_title("P1a: square steel tube 100x100x2.8 mm, L=450 mm, axial crush")
ax.grid(alpha=0.3); ax.legend(fontsize=8, loc="upper right")
fig.tight_layout(); fig.savefig(out, dpi=130)
print("wrote", out)
