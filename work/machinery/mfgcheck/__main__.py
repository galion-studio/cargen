# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""CLI: python -m mfgcheck part.json [--json]. Exit 1 if any error is found."""
import argparse
import json
import sys

from .checks import check_part
from .data import SOURCES


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="mfgcheck", description=__doc__)
    ap.add_argument("part", help="JSON file with one part (or a list of parts)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)
    with open(a.part, encoding="utf-8") as fh:
        parts = json.load(fh)
    if isinstance(parts, dict):
        parts = [parts]
    report, n_err = [], 0
    for part in parts:
        fs = check_part(part)
        n_err += sum(f.severity == "error" for f in fs)
        report.append({"name": part.get("name", part.get("kind")), "findings": [f.to_dict() for f in fs]})
    if a.json:
        json.dump(report, sys.stdout, indent=2)
        print()
    else:
        for r in report:
            print(f"== {r['name']}")
            if not r["findings"]:
                print("   no findings")
            for f in r["findings"]:
                print(f"   [{f['severity'].upper():7}] {f['rule']}: {f['message']}")
                if f["suggestion"]:
                    print(f"             suggest: {f['suggestion']}")
                for s in f["sources"]:
                    print(f"             source: {s['url']}")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
