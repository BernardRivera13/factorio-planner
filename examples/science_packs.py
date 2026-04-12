"""
Science pack production planning example.

Computes what you need to sustain a target research rate
across all science pack tiers.
"""

from factorio_planner import Calculator
from factorio_planner.formatter import format_plan

SCIENCE_PACKS = [
    "automation-science-pack",
    "logistic-science-pack",
    "chemical-science-pack",
    "production-science-pack",
    "utility-science-pack",
]

calc = Calculator()

print("=" * 60)
print("  SCIENCE PACK PRODUCTION PLANS  (0.5 packs/second each)")
print("=" * 60)

combined_machines: dict = {}
combined_raw: dict = {}

for pack in SCIENCE_PACKS:
    plan = calc.compute(pack, rate=0.5)
    print(f"\n{'─'*60}")
    print(f"  {pack}  @ 0.5/s")
    print(f"{'─'*60}")
    print(plan.summary())

    for machine, count in plan.machine_totals.items():
        combined_machines[machine] = combined_machines.get(machine, 0) + count
    for item, rate in plan.raw_resources.items():
        combined_raw[item] = combined_raw.get(item, 0) + rate

print("\n" + "=" * 60)
print("  COMBINED TOTALS (all 5 packs at 0.5/s)")
print("=" * 60)
print("\nTotal machines:")
for machine, count in sorted(combined_machines.items()):
    import math
    print(f"  {machine:<32} {count:6.1f}  (≥ {math.ceil(count)})")

print("\nTotal raw resources:")
for item, rate in sorted(combined_raw.items()):
    print(f"  {item:<32} {rate:8.3f} /s")
