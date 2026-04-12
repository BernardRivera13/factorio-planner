"""
Rocket launch planning example.

Computes all production chains needed for a complete rocket launch:
100x rocket parts + 1x satellite.
"""

from factorio_planner import Calculator
from factorio_planner.formatter import format_plan
import math

calc = Calculator()

print("=" * 65)
print("  ROCKET LAUNCH PRODUCTION PLANNER")
print("=" * 65)

# Target: 1 rocket launch every 60 seconds = 100 rocket-parts in 60s
LAUNCH_INTERVAL_SECONDS = 60
PARTS_PER_ROCKET = 100

rocket_rate = PARTS_PER_ROCKET / LAUNCH_INTERVAL_SECONDS
print(f"\nTarget: 1 rocket launch every {LAUNCH_INTERVAL_SECONDS}s")
print(f"  => {rocket_rate:.4f} rocket-parts/s\n")

plan = calc.compute("rocket-part", rate=rocket_rate)
print(format_plan(plan, show_tree=False))

# Also plan satellite
print("\n--- Satellite (1 per launch) ---\n")
sat_rate = 1 / LAUNCH_INTERVAL_SECONDS
plan_sat = calc.compute("satellite", rate=sat_rate)
print(plan_sat.summary())

# Combined machine totals
print("\n--- Combined machines (rocket-part + satellite) ---")
combined = {}
for d in [plan.machine_totals, plan_sat.machine_totals]:
    for machine, count in d.items():
        combined[machine] = combined.get(machine, 0) + count

for machine, count in sorted(combined.items()):
    print(f"  {machine:<30} {count:6.2f}  (≥ {math.ceil(count)} buildings)")
