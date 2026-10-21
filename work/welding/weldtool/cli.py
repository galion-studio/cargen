# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""Command line: python3 -m weldtool {suggest,params,haz,card,list,sources} ..."""
import argparse
import json
import sys

from . import core
from . import data as D


def _fmt(obj, indent=0):
    pad = "  " * indent
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                out.append(f"{pad}{k}:")
                out.extend(_fmt(v, indent + 1))
            else:
                out.append(f"{pad}{k}: {v}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, dict):
                if set(v) == {"id", "title", "url"}:
                    out.append(f"{pad}- [{v['id']}] {v['title']} <{v['url']}>")
                else:
                    out.append(f"{pad}-")
                    out.extend(_fmt(v, indent + 1))
            else:
                out.append(f"{pad}- {v}")
    else:
        out.append(f"{pad}{obj}")
    return out


def _emit(result, as_json):
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"*** {core.BANNER} ***")
        print("\n".join(_fmt(result)))


def _common(p, thickness=True, process=True):
    p.add_argument("--metal", required=True, help="see 'list'")
    if thickness:
        p.add_argument("--thickness", "-t", type=float, required=True, help="sheet thickness, mm")
    if process:
        p.add_argument("--process", "-p", required=True, choices=core.PROCESSES)
    p.add_argument("--json", action="store_true", help="machine-readable output")


def _card_args(p):
    p.add_argument("--uts", type=float, help="base metal UTS, MPa (steel; default only where cited)")
    p.add_argument("--nugget-factor", type=float, default=D.NUGGET_FACTOR_MIN, help="nugget d = k*sqrt(t); default 4")
    p.add_argument("--shear-kn", type=float, help="measured coupon shear (0 deg) strength, kN")
    p.add_argument("--normal-kn", type=float, help="measured coupon cross-tension (90 deg) strength, kN")
    p.add_argument("--density", type=float, help="t/mm3 (required for non-steel)")
    p.add_argument("--mat-id", type=int, default=1)
    p.add_argument("--out", help="write the card to this file")


def _card(a):
    return core.spotweld_card(a.metal, a.thickness, uts_mpa=a.uts, nugget_factor=a.nugget_factor,
                              shear_kN=a.shear_kn, normal_kN=a.normal_kn, mat_id=a.mat_id,
                              density_t_mm3=a.density)


def build_parser():
    ap = argparse.ArgumentParser(prog="weldtool", description=core.BANNER)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("suggest", help="parameters + HAZ knockdown (+ crash card for spot)")
    _common(s)
    _card_args(s)
    _common(sub.add_parser("params", help="starting parameter ranges"))
    h = sub.add_parser("haz", help="HAZ / joint strength knockdown")
    _common(h, thickness=False)
    h.add_argument("--thickness", "-t", type=float, help="mm (for HAZ width)")
    c = sub.add_parser("card", help="Radioss /MAT/LAW59 + /FAIL/CONNECT spot-weld snippet")
    _common(c, process=False)
    _card_args(c)
    sub.add_parser("list", help="metals and processes")
    sub.add_parser("sources", help="all cited sources")
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        if a.cmd == "list":
            for k, v in D.MATERIALS.items():
                print(f"{k:22s} {v['family']:10s} {v['desc']}")
            print("processes:", ", ".join(core.PROCESSES))
            return 0
        if a.cmd == "sources":
            for k, (t, u) in D.SOURCES.items():
                print(f"[{k}] {t}\n    {u}")
            return 0
        if a.cmd == "params":
            _emit(core.params(a.metal, a.thickness, a.process), a.json)
        elif a.cmd == "haz":
            _emit(core.haz(a.metal, a.process, a.thickness), a.json)
        elif a.cmd == "card":
            card = _card(a)
            if a.out:
                with open(a.out, "w") as fh:
                    fh.write(card["text"])
            if a.json:
                print(json.dumps({k: v for k, v in card.items()}, indent=2))
            else:
                sys.stdout.write(card["text"])
        elif a.cmd == "suggest":
            res = {"metal": a.metal, "thickness_mm": a.thickness, "process": a.process,
                   "parameters": core.params(a.metal, a.thickness, a.process),
                   "haz": core.haz(a.metal, a.process, a.thickness)}
            card_text = None
            if a.process == "spot":
                try:
                    card = _card(a)
                    card_text = card["text"]
                    if a.out:
                        with open(a.out, "w") as fh:
                            fh.write(card_text)
                    res["crash_card"] = {k: v for k, v in card.items() if k != "text"}
                    if a.json:
                        res["crash_card"]["text"] = card_text
                except core.WeldToolError as e:
                    res["crash_card"] = {"available": False, "reason": str(e)}
            _emit(res, a.json)
            if card_text and not a.json:
                print("\n--- crash card (OpenRadioss/OpenCourant starter format) ---")
                sys.stdout.write(card_text)
    except core.WeldToolError as e:
        print(f"weldtool: {e}", file=sys.stderr)
        return 2
    return 0
