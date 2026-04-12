"""
Command-line interface for factorio-calc.

Usage:
    factorio-calc electronic-circuit --rate 10
    factorio-calc utility-science-pack --rate 1 --productivity 0.4
    factorio-calc iron-plate --rate 5 --no-tree
"""

import argparse
import sys
import json as _json
from .calculator import Calculator
from .formatter import format_plan, to_dict
from . import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="factorio-calc",
        description="Compute Factorio production chains from the command line.",
    )
    parser.add_argument("item", help="Item to produce (e.g. electronic-circuit)")
    parser.add_argument("--rate", "-r", type=float, default=1.0,
                        help="Target production rate in items/second (default: 1.0)")
    parser.add_argument("--productivity", "-p", type=float, default=0.0,
                        help="Productivity module bonus, e.g. 0.4 for +40%% (default: 0)")
    parser.add_argument("--speed", "-s", type=float, default=0.0,
                        help="Speed beacon bonus multiplier (default: 0)")
    parser.add_argument("--no-tree", action="store_true",
                        help="Skip the tree view, show only totals")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON instead of human-readable text")
    parser.add_argument("--version", action="version", version=f"factorio-calc {__version__}")

    args = parser.parse_args()

    calc = Calculator(
        productivity_bonus=args.productivity,
        speed_bonus=args.speed,
    )

    try:
        plan = calc.compute(args.item, rate=args.rate)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(_json.dumps(to_dict(plan), indent=2))
    else:
        print(format_plan(plan, show_tree=not args.no_tree))


if __name__ == "__main__":
    main()
