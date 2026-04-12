"""Basic factorio-calc usage examples."""

from factorio_planner import Calculator
from factorio_planner.formatter import format_plan, to_dict
import json

calc = Calculator()

# Example 1: iron plate
print("=== Iron plate 1/s ===")
plan = calc.compute("iron-plate", rate=1.0)
print(plan.summary())

# Example 2: electronic circuits
print("\n=== Electronic circuit 10/s ===")
plan = calc.compute("electronic-circuit", rate=10)
print(format_plan(plan))

# Example 3: with productivity modules
print("\n=== Advanced circuit 5/s with +40% productivity ===")
calc_prod = Calculator(productivity_bonus=0.4)
plan_prod = calc_prod.compute("advanced-circuit", rate=5)
print(plan_prod.summary())

# Example 4: JSON output
print("\n=== JSON export (iron-plate 3/s) ===")
plan_json = calc.compute("iron-plate", rate=3)
print(json.dumps(to_dict(plan_json), indent=2))
