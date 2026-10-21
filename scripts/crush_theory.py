# SPDX-License-Identifier: MIT
# Copyright (c) 2026 galion-studio
"""Theory check for the axial-crush experiments in data/crush-experiments.csv.

Closed-form mean crushing force predictions (all from the cited papers, see
research/crush-experiments.md):
  WA83     Wierzbicki & Abramowicz 1983, square, symmetric:  Pm/M0 = 38.12 (c/h)^(1/3)
  AJ_S     Abramowicz & Jones 1984 eq.33 = 1986 eq.19, square symmetric with effective
           crushing distance 0.73*2H:                          Pm/M0 = 52.22 (c/h)^(1/3)
  AJ_B     A&J 1986 eq.22, square asymmetric mixed mode B:     Pm/M0 = 45.90 (c/h)^(1/3) + 1.75 (c/h)^(2/3) + 1.02
  AJ_EX    A&J 1986 eq.23, square extensional:                 Pm/M0 = 32.64 (c/h)^(1/2) + 8.16
  AJ_CIRC  A&J 1986 eq.46, circular axisymmetric (modified Alexander 1960):
           Pm/M0 = (25.23 (2R/h)^(1/2) + 15.09) / (0.86 - 0.568 (h/2R)^(1/2))
  M0 = sigma0 h^2 / 4 with sigma0 = sigma_u (A&J 1984 sec. 4.8 / 1986 sec. 5.1).
Cowper-Symonds (A&J 1984 eq.39/50, 1986 eq.32-35): factor 1 + (eps_dot/D)^(1/p),
  D = 6844 1/s, p = 3.91 (A&J eq.25, fit to ultimate stress of low-carbon steel),
  sensitivity: D = 802 1/s, p = 3.585 (A&J 1986 eq.26).
  eps_dot = 0.33 V/c (symmetric), 0.39 V/c (mode B), 0.25 V/c (extensional) [A&J 1986 eq.30-31];
  circular axisymmetric: 0.25 V / (R (0.86 - 0.568 (h/2R)^(1/2))) [A&J 1986 eq.53].
For quasi-static tests V is the crosshead speed, so the factor is ~1.01.
SEA (crushed-mass basis) = Pm / (rho * A), A = 4 c h (square) or pi c h (circular, c = 2R).
rho = 7850 kg/m^3 nominal carbon steel where the paper gives none (flagged in output).
"""
import csv, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, "data", "crush-experiments.csv")
OUT = os.path.join(ROOT, "data", "crush-theory-check.csv")
RHO_NOMINAL = 7850.0

def f(x):
    return float(x) if x not in ("", None) else None

def cs(eps, D, p):
    return 1.0 + (eps / D) ** (1.0 / p) if eps and eps > 0 else 1.0

def load():
    with open(IN) as fh:
        rows = [l for l in fh if not l.startswith("#")]
    return list(csv.DictReader(rows))

def predict(r):
    c, h, V = f(r["c_mm"]), f(r["t_mm"]), f(r["speed_m_s"]) or 0.0
    su = f(r["sigma_u_MPa"]); sy = f(r["sigma_y_MPa"])
    sigma0 = su if su else sy
    basis = "sigma_u" if su else "sigma_y (sigma_u not reported)"
    M0 = sigma0 * h * h / 4.0  # N*mm/mm -> N
    mode = r["mode_reported"]
    out = {"sigma0_MPa": sigma0, "sigma0_basis": basis}
    if r["section"] == "square":
        x = c / h
        out["WA83_kN"] = 38.12 * M0 * x ** (1 / 3) / 1e3
        out["AJ_S_kN"] = 52.22 * M0 * x ** (1 / 3) / 1e3
        out["AJ_B_kN"] = (45.90 * x ** (1 / 3) + 1.75 * x ** (2 / 3) + 1.02) * M0 / 1e3
        out["AJ_EX_kN"] = (32.64 * x ** 0.5 + 8.16) * M0 / 1e3
        if mode == "EX":
            key, k = "AJ_EX_kN", 0.25
        elif mode == "A":
            key, k = "AJ_B_kN", 0.39   # A&J: mode B and symmetric nearly identical for these c/h
        else:
            key, k = "AJ_S_kN", 0.33
        eps = k * V / (c * 1e-3)
        out["formula"] = {"AJ_S_kN": "A&J1984 eq33 / 1986 eq19 (symmetric)",
                          "AJ_B_kN": "A&J1986 eq22 (asym. mode B)",
                          "AJ_EX_kN": "A&J1986 eq23 (extensional)"}[key]
        static = out[key]
        A = 4 * c * h
    else:
        R = c / 2.0
        den = 0.86 - 0.568 * (h / c) ** 0.5
        static = (25.23 * (c / h) ** 0.5 + 15.09) / den * M0 / 1e3
        out["AJ_CIRC_kN"] = static
        out["formula"] = "A&J1986 eq46 (circular axisymmetric, modified Alexander)"
        eps = 0.25 * V / (R * 1e-3 * den)
        A = math.pi * c * h
    out["strain_rate_1_s"] = eps
    out["theory_static_kN"] = static
    out["theory_CS6844_kN"] = static * cs(eps, 6844.0, 3.91)
    out["theory_CS802_kN"] = static * cs(eps, 802.0, 3.585)
    rho = f(r["rho_kg_m3"]) or RHO_NOMINAL
    out["rho_used"] = rho
    out["rho_basis"] = "paper" if f(r["rho_kg_m3"]) else "nominal 7850 (assumed)"
    Pm = f(r["mean_force_kN"])
    out["SEA_kJ_kg"] = Pm * 1e3 / (rho * A * 1e-6) / 1e3  # (N)/(kg/m) = J/kg -> kJ/kg
    pk = f(r["peak_force_kN"])
    out["CFE"] = Pm / pk if pk else None
    L, d = f(r["L_mm"]), f(r["crush_distance_mm"])
    out["stroke_ratio"] = d / L if (d and L) else None
    out["err_static_pct"] = 100 * (static - Pm) / Pm
    out["err_CS6844_pct"] = 100 * (out["theory_CS6844_kN"] - Pm) / Pm
    return out

def main():
    rows = load()
    cols = ["id", "source_key", "section", "loading", "mode_reported", "c_mm", "t_mm", "c_over_t",
            "sigma0_MPa", "sigma0_basis", "speed_m_s", "strain_rate_1_s", "mean_force_kN",
            "peak_force_kN", "formula", "theory_static_kN", "theory_CS6844_kN", "theory_CS802_kN",
            "err_static_pct", "err_CS6844_pct", "WA83_kN", "paper_theory_kN", "SEA_kJ_kg",
            "rho_used", "rho_basis", "CFE", "stroke_ratio"]
    res = []
    for r in rows:
        p = predict(r)
        d = {k: r.get(k, "") for k in cols}
        d.update(p)
        d["c_over_t"] = f(r["c_mm"]) / f(r["t_mm"])
        res.append(d)
    with open(OUT, "w", newline="") as fh:
        fh.write("# Generated by scripts/crush_theory.py from data/crush-experiments.csv. Theory = published closed-form formulas (see script header). Do not edit by hand.\n")
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for d in res:
            w.writerow({k: (f"{v:.4g}" if isinstance(v, float) else ("" if v is None else v)) for k, v in d.items() if k in cols})
    return res

if __name__ == "__main__":
    res = main()
    for d in res:
        print(f'{d["id"]:11s} {d["loading"][:5]} mode={d["mode_reported"]:3s} exp={float(d["mean_force_kN"]):7.2f} '
              f'th={d["theory_static_kN"]:7.2f} thCS={d["theory_CS6844_kN"]:7.2f} err={d["err_CS6844_pct"]:6.1f}% '
              f'paper={d["paper_theory_kN"] or "-":>6} SEA={d["SEA_kJ_kg"]:5.1f}')
