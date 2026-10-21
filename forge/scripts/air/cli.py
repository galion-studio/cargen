# SPDX-License-Identifier: MIT
# Copyright (c) 3000 Galion / galion-studio
"""Small CLI: python -m air.cli isa 1500 | drag --cd 0.3 --area 2.2 --v 33.3 --h 0"""
import argparse, json
from . import isa as _isa, forces, ahmed, humid


def main(argv=None):
    ap = argparse.ArgumentParser(prog="air")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("isa"); a.add_argument("h", type=float); a.add_argument("--geometric", action="store_true"); a.add_argument("--dT", type=float, default=0.0)
    d = sub.add_parser("drag")
    for k in ("cd", "area", "v"):
        d.add_argument("--" + k, type=float, required=True)
    d.add_argument("--h", type=float, default=0.0); d.add_argument("--dT", type=float, default=0.0)
    d.add_argument("--rh", type=float, default=None); d.add_argument("--wind", type=float, default=0.0); d.add_argument("--wind-from", type=float, default=0.0)
    d.add_argument("--crr", type=float); d.add_argument("--mass", type=float)
    s = sub.add_parser("ahmed"); s.add_argument("slant", type=int); s.add_argument("--kind", default="exp")
    args = ap.parse_args(argv)
    if args.cmd == "isa":
        out = _isa.isa(args.h, args.geometric, args.dT)
    elif args.cmd == "drag":
        st = _isa.isa(args.h, dT=args.dT)
        rho = st["rho"] if args.rh is None else humid.humid_density(st["p"], st["T"], args.rh, extrapolate=True)[0]
        out = forces.road_load(args.cd, args.area, rho, args.v, args.wind, args.wind_from, args.crr, args.mass)
        out["rho"] = rho
    else:
        out = ahmed.lookup(args.slant, args.kind)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
