"""
Built-in recipe database for Factorio base game (1.1).
Can be extended with custom recipes or loaded from a JSON file.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional
from .models import Recipe

# ---------------------------------------------------------------------------
# Base-game recipes (hand-crafted subset covering the most common chains)
# ---------------------------------------------------------------------------
_BASE_RECIPES: list[dict] = [
    # --- Raw / Mining (no recipe – handled as terminals) ---
    # iron-ore, copper-ore, coal, stone, water, crude-oil  => no entry

    # --- Smelting ---
    {"name": "iron-plate",    "ingredients": {"iron-ore": 1},   "products": {"iron-plate": 1},    "time": 3.2,  "category": "smelting",  "machine": "stone-furnace"},
    {"name": "copper-plate",  "ingredients": {"copper-ore": 1}, "products": {"copper-plate": 1},  "time": 3.2,  "category": "smelting",  "machine": "stone-furnace"},
    {"name": "steel-plate",   "ingredients": {"iron-plate": 5}, "products": {"steel-plate": 1},   "time": 16.0, "category": "smelting",  "machine": "stone-furnace"},
    {"name": "stone-brick",   "ingredients": {"stone": 2},      "products": {"stone-brick": 1},   "time": 3.2,  "category": "smelting",  "machine": "stone-furnace"},

    # --- Basic components ---
    {"name": "iron-gear-wheel",  "ingredients": {"iron-plate": 2},                              "products": {"iron-gear-wheel": 1},  "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "copper-cable",     "ingredients": {"copper-plate": 1},                            "products": {"copper-cable": 2},     "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "iron-stick",       "ingredients": {"iron-plate": 1},                              "products": {"iron-stick": 2},       "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},

    # --- Circuits ---
    {"name": "electronic-circuit",  "ingredients": {"iron-plate": 1, "copper-cable": 3},        "products": {"electronic-circuit": 1},  "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "advanced-circuit",    "ingredients": {"electronic-circuit": 3, "plastic-bar": 2, "copper-cable": 4}, "products": {"advanced-circuit": 1}, "time": 6.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "processing-unit",     "ingredients": {"electronic-circuit": 20, "advanced-circuit": 2, "sulfuric-acid": 5}, "products": {"processing-unit": 1}, "time": 10.0, "category": "crafting", "machine": "assembling-machine-2"},

    # --- Oil products ---
    {"name": "plastic-bar",    "ingredients": {"coal": 1, "petroleum-gas": 20},  "products": {"plastic-bar": 2},  "time": 1.0, "category": "chemistry", "machine": "chemical-plant"},
    {"name": "sulfur",         "ingredients": {"water": 30, "petroleum-gas": 30},"products": {"sulfur": 2},        "time": 1.0, "category": "chemistry", "machine": "chemical-plant"},
    {"name": "sulfuric-acid",  "ingredients": {"iron-plate": 1, "sulfur": 5, "water": 100}, "products": {"sulfuric-acid": 50}, "time": 1.0, "category": "chemistry", "machine": "chemical-plant"},
    {"name": "lubricant",      "ingredients": {"heavy-oil": 10},                 "products": {"lubricant": 10},   "time": 1.0, "category": "chemistry", "machine": "chemical-plant"},

    # --- Intermediate products ---
    {"name": "pipe",           "ingredients": {"iron-plate": 1},                 "products": {"pipe": 1},          "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "steel-chest",    "ingredients": {"steel-plate": 8},                "products": {"steel-chest": 1},   "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "engine-unit",    "ingredients": {"steel-plate": 1, "iron-gear-wheel": 1, "pipe": 2}, "products": {"engine-unit": 1}, "time": 10.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "electric-engine-unit", "ingredients": {"engine-unit": 1, "electronic-circuit": 2, "lubricant": 15}, "products": {"electric-engine-unit": 1}, "time": 10.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "battery",        "ingredients": {"iron-plate": 1, "copper-plate": 1, "sulfuric-acid": 20}, "products": {"battery": 1}, "time": 4.0, "category": "chemistry", "machine": "chemical-plant"},
    {"name": "flying-robot-frame", "ingredients": {"electric-engine-unit": 1, "battery": 2, "steel-plate": 1, "electronic-circuit": 3}, "products": {"flying-robot-frame": 1}, "time": 20.0, "category": "crafting", "machine": "assembling-machine-2"},

    # --- Science packs ---
    {"name": "automation-science-pack", "ingredients": {"copper-plate": 1, "iron-gear-wheel": 1}, "products": {"automation-science-pack": 1}, "time": 5.0, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "logistic-science-pack",   "ingredients": {"science-pack-1": 1, "inserter": 1, "transport-belt": 1}, "products": {"logistic-science-pack": 1}, "time": 6.0, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "military-science-pack",   "ingredients": {"piercing-rounds-magazine": 1, "grenade": 1, "stone-wall": 2}, "products": {"military-science-pack": 2}, "time": 10.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "chemical-science-pack",   "ingredients": {"advanced-circuit": 3, "engine-unit": 2, "sulfur": 1}, "products": {"chemical-science-pack": 2}, "time": 24.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "production-science-pack", "ingredients": {"electric-mining-drill": 1, "electric-furnace": 1, "rail": 30}, "products": {"production-science-pack": 3}, "time": 21.0, "category": "crafting", "machine": "assembling-machine-3"},
    {"name": "utility-science-pack",    "ingredients": {"processing-unit": 2, "flying-robot-frame": 1, "low-density-structure": 3}, "products": {"utility-science-pack": 3}, "time": 21.0, "category": "crafting", "machine": "assembling-machine-3"},

    # --- Infrastructure ---
    {"name": "transport-belt",    "ingredients": {"iron-plate": 1, "iron-gear-wheel": 1},       "products": {"transport-belt": 2},   "time": 0.5,  "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "fast-transport-belt","ingredients": {"transport-belt": 1, "iron-gear-wheel": 5},  "products": {"fast-transport-belt": 1},"time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "inserter",          "ingredients": {"iron-plate": 1, "iron-gear-wheel": 1, "electronic-circuit": 1}, "products": {"inserter": 1}, "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "fast-inserter",     "ingredients": {"inserter": 1, "iron-plate": 2, "electronic-circuit": 2}, "products": {"fast-inserter": 1}, "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},

    # --- Mining drills ---
    {"name": "burner-mining-drill", "ingredients": {"iron-plate": 3, "iron-gear-wheel": 3, "stone-brick": 3}, "products": {"burner-mining-drill": 1}, "time": 2.0, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "electric-mining-drill","ingredients": {"iron-plate": 10, "iron-gear-wheel": 5, "electronic-circuit": 3}, "products": {"electric-mining-drill": 1}, "time": 2.0, "category": "crafting", "machine": "assembling-machine-1"},

    # --- Power ---
    {"name": "small-electric-pole", "ingredients": {"copper-plate": 2, "iron-stick": 2},         "products": {"small-electric-pole": 2}, "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "solar-panel",         "ingredients": {"steel-plate": 5, "electronic-circuit": 15, "copper-plate": 5}, "products": {"solar-panel": 1}, "time": 10.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "accumulator",         "ingredients": {"iron-plate": 2, "battery": 5},               "products": {"accumulator": 1},         "time": 10.0, "category": "crafting", "machine": "assembling-machine-2"},

    # --- Combat ---
    {"name": "grenade",              "ingredients": {"coal": 10, "iron-plate": 5},                "products": {"grenade": 1},              "time": 8.0,  "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "piercing-rounds-magazine", "ingredients": {"copper-plate": 5, "steel-plate": 1, "firearm-magazine": 1}, "products": {"piercing-rounds-magazine": 1}, "time": 3.0, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "firearm-magazine",     "ingredients": {"iron-plate": 4},                            "products": {"firearm-magazine": 1},     "time": 1.0,  "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "stone-wall",           "ingredients": {"stone-brick": 5},                           "products": {"stone-wall": 1},           "time": 0.5,  "category": "crafting", "machine": "assembling-machine-1"},

    # --- High-tier ---
    {"name": "low-density-structure","ingredients": {"steel-plate": 10, "copper-plate": 20, "plastic-bar": 5}, "products": {"low-density-structure": 1}, "time": 20.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "rocket-fuel",          "ingredients": {"solid-fuel": 10, "light-oil": 10},          "products": {"rocket-fuel": 1},          "time": 30.0, "category": "chemistry", "machine": "chemical-plant"},
    {"name": "solid-fuel",           "ingredients": {"light-oil": 10},                            "products": {"solid-fuel": 1},           "time": 2.0,  "category": "chemistry", "machine": "chemical-plant"},
    {"name": "rocket-control-unit",  "ingredients": {"processing-unit": 1, "speed-module": 1},    "products": {"rocket-control-unit": 1},  "time": 30.0, "category": "crafting", "machine": "assembling-machine-3"},
    {"name": "speed-module",         "ingredients": {"electronic-circuit": 5, "advanced-circuit": 5}, "products": {"speed-module": 1},     "time": 15.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "rocket-part",          "ingredients": {"rocket-fuel": 10, "low-density-structure": 10, "rocket-control-unit": 10}, "products": {"rocket-part": 1}, "time": 3.0, "category": "crafting", "machine": "rocket-silo"},
    {"name": "satellite",            "ingredients": {"processing-unit": 100, "low-density-structure": 100, "rocket-fuel": 50, "solar-panel": 100, "accumulator": 100, "radar": 5}, "products": {"satellite": 1}, "time": 5.0, "category": "crafting", "machine": "assembling-machine-3"},
    {"name": "radar",                "ingredients": {"iron-plate": 10, "iron-gear-wheel": 5, "electronic-circuit": 5}, "products": {"radar": 1}, "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},
    {"name": "electric-furnace",     "ingredients": {"steel-plate": 10, "advanced-circuit": 5, "stone-brick": 10}, "products": {"electric-furnace": 1}, "time": 5.0, "category": "crafting", "machine": "assembling-machine-2"},
    {"name": "rail",                 "ingredients": {"stone": 1, "steel-plate": 1, "iron-stick": 1}, "products": {"rail": 2}, "time": 0.5, "category": "crafting", "machine": "assembling-machine-1"},

    # legacy name for logistic science pack ingredient
    {"name": "science-pack-1", "ingredients": {"copper-plate": 1, "iron-gear-wheel": 1}, "products": {"science-pack-1": 1}, "time": 5.0, "category": "crafting", "machine": "assembling-machine-1"},
]

# Crafting speeds per machine type
MACHINE_SPEEDS: Dict[str, float] = {
    "assembling-machine-1": 0.5,
    "assembling-machine-2": 0.75,
    "assembling-machine-3": 1.25,
    "stone-furnace":        1.0,
    "steel-furnace":        2.0,
    "electric-furnace":     2.0,
    "chemical-plant":       1.0,
    "oil-refinery":         1.0,
    "rocket-silo":          1.0,
}


class RecipeDB:
    """
    Registry of Factorio recipes.

    Usage::

        db = RecipeDB()                  # loads base-game recipes
        db = RecipeDB.from_json("path")  # load custom / modded recipes
        recipe = db.get("electronic-circuit")
        db.add(my_recipe)
    """

    def __init__(self) -> None:
        self._recipes: Dict[str, Recipe] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        for r in _BASE_RECIPES:
            recipe = Recipe(
                name=r["name"],
                ingredients=r["ingredients"],
                products=r["products"],
                crafting_time=r["time"],
                category=r.get("category", "crafting"),
                machine=r.get("machine", "assembling-machine-1"),
            )
            self._recipes[r["name"]] = recipe

    # ------------------------------------------------------------------
    def get(self, item: str) -> Optional[Recipe]:
        """Return the recipe that produces *item*, or None if it's a raw resource."""
        # direct name match
        if item in self._recipes:
            return self._recipes[item]
        # search by product
        for recipe in self._recipes.values():
            if item in recipe.products:
                return recipe
        return None

    def add(self, recipe: Recipe) -> None:
        """Register a custom recipe (overwrites existing with same name)."""
        self._recipes[recipe.name] = recipe

    def remove(self, name: str) -> None:
        """Remove a recipe by name."""
        self._recipes.pop(name, None)

    def list_items(self) -> list[str]:
        """Return all craftable item names."""
        items = set()
        for recipe in self._recipes.values():
            items.update(recipe.products.keys())
        return sorted(items)

    def machine_speed(self, machine: str) -> float:
        return MACHINE_SPEEDS.get(machine, 1.0)

    # ------------------------------------------------------------------
    @classmethod
    def from_json(cls, path: str | Path) -> "RecipeDB":
        """
        Load a recipe DB from a JSON file.

        Expected format::

            [
              {
                "name": "my-item",
                "ingredients": {"iron-plate": 2},
                "products": {"my-item": 1},
                "time": 1.5,
                "category": "crafting",
                "machine": "assembling-machine-2"
              },
              ...
            ]
        """
        db = cls()
        with open(path) as f:
            data = json.load(f)
        for r in data:
            recipe = Recipe(
                name=r["name"],
                ingredients=r["ingredients"],
                products=r["products"],
                crafting_time=r["time"],
                category=r.get("category", "crafting"),
                machine=r.get("machine", "assembling-machine-1"),
            )
            db._recipes[r["name"]] = recipe
        return db

    def to_json(self, path: str | Path) -> None:
        """Export the current recipe DB to JSON."""
        data = []
        for recipe in self._recipes.values():
            data.append({
                "name": recipe.name,
                "ingredients": recipe.ingredients,
                "products": recipe.products,
                "time": recipe.crafting_time,
                "category": recipe.category,
                "machine": recipe.machine,
            })
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
