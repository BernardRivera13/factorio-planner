"""
Custom / modded recipe example.

Shows how to extend the base-game recipe database
with your own items (e.g. from a Factorio mod).
"""

import json
import tempfile
import os
from factorio_planner import Calculator, RecipeDB
from factorio_planner.models import Recipe
from factorio_planner.formatter import format_plan

# ── Option A: add recipes programmatically ──────────────────────────────────
db = RecipeDB()

# Fictional "Space Exploration" mod items
db.add(Recipe(
    name="data-storage-substrate",
    ingredients={"processing-unit": 2, "stone": 5},
    products={"data-storage-substrate": 1},
    crafting_time=3.0,
    machine="assembling-machine-2",
))
db.add(Recipe(
    name="space-science-pack",
    ingredients={"rocket-part": 1, "satellite": 1},
    products={"space-science-pack": 1000},
    crafting_time=40.0,
    machine="rocket-silo",
))

calc = Calculator(db=db)
print("=== Custom recipe: data-storage-substrate (2/s) ===")
plan = calc.compute("data-storage-substrate", rate=2)
print(format_plan(plan))

# ── Option B: load from JSON ─────────────────────────────────────────────────
custom_recipes = [
    {
        "name": "quantum-chip",
        "ingredients": {"processing-unit": 10, "advanced-circuit": 5},
        "products": {"quantum-chip": 1},
        "time": 8.0,
        "category": "crafting",
        "machine": "assembling-machine-3"
    }
]

with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
    json.dump(custom_recipes, f)
    tmp_path = f.name

# Load on top of base game
db2 = RecipeDB.from_json(tmp_path)
os.unlink(tmp_path)

calc2 = Calculator(db=db2)
print("\n=== Mod recipe loaded from JSON: quantum-chip (1/s) ===")
plan2 = calc2.compute("quantum-chip", rate=1)
print(format_plan(plan2))
