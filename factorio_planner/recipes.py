"""
Recipe and ingredient data structures for factorio-calc.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from pathlib import Path


@dataclass
class Ingredient:
    """A single ingredient in a recipe."""
    name: str
    amount: float

    def __repr__(self) -> str:
        return f"Ingredient({self.name!r}, {self.amount})"


@dataclass
class Recipe:
    """
    A Factorio recipe: produces `yield_amount` of `name` in `craft_time` seconds
    using a list of ingredients, in the given `machine`.
    """
    name: str
    craft_time: float
    ingredients: List[Ingredient]
    yield_amount: float = 1.0
    machine: str = "assembling-machine"

    @property
    def ingredients_dict(self) -> Dict[str, float]:
        return {i.name: i.amount for i in self.ingredients}

    def machines_needed(self, target_rate: float, machine_speed: float = 1.0) -> float:
        """
        How many machines are required to achieve `target_rate` items/second.

        Args:
            target_rate: desired output in items per second
            machine_speed: crafting speed multiplier of the machine (default 1.0)

        Returns:
            Number of machines (float — ceil to get whole machines)
        """
        rate_per_machine = (self.yield_amount / self.craft_time) * machine_speed
        return target_rate / rate_per_machine

    def __repr__(self) -> str:
        return (
            f"Recipe({self.name!r}, time={self.craft_time}s, "
            f"yield={self.yield_amount}, ingredients={self.ingredients})"
        )


class RecipeBook:
    """
    A collection of recipes. Can be loaded from the built-in Factorio dataset
    or from a custom JSON file.

    Example::

        book = RecipeBook.default()
        recipe = book["electronic-circuit"]
    """

    def __init__(self, recipes: Optional[Dict[str, Recipe]] = None):
        self._recipes: Dict[str, Recipe] = recipes or {}

    # ------------------------------------------------------------------
    # Loading helpers
    # ------------------------------------------------------------------

    @classmethod
    def default(cls) -> "RecipeBook":
        """Load the built-in vanilla Factorio recipe dataset."""
        data_path = Path(__file__).parent / "data" / "recipes.json"
        return cls.from_json(data_path)

    @classmethod
    def from_json(cls, path) -> "RecipeBook":
        """
        Load recipes from a JSON file.

        The file must be a list of recipe objects::

            [
              {
                "name": "iron-gear-wheel",
                "craft_time": 0.5,
                "yield": 1,
                "machine": "assembling-machine",
                "ingredients": [{"name": "iron-plate", "amount": 2}]
              },
              ...
            ]
        """
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        recipes: Dict[str, Recipe] = {}
        for entry in raw:
            ingredients = [
                Ingredient(i["name"], float(i["amount"]))
                for i in entry.get("ingredients", [])
            ]
            r = Recipe(
                name=entry["name"],
                craft_time=float(entry["craft_time"]),
                ingredients=ingredients,
                yield_amount=float(entry.get("yield", 1)),
                machine=entry.get("machine", "assembling-machine"),
            )
            recipes[r.name] = r
        return cls(recipes)

    @classmethod
    def from_dict(cls, data: List[dict]) -> "RecipeBook":
        """Build a RecipeBook from a list of recipe dicts (same schema as JSON)."""
        import tempfile, json as _json
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            _json.dump(data, f)
            tmp = f.name
        return cls.from_json(tmp)

    # ------------------------------------------------------------------
    # Access helpers
    # ------------------------------------------------------------------

    def __getitem__(self, name: str) -> Recipe:
        if name not in self._recipes:
            raise KeyError(
                f"Recipe {name!r} not found. "
                f"Available: {sorted(self._recipes)[:10]} ..."
            )
        return self._recipes[name]

    def __contains__(self, name: str) -> bool:
        return name in self._recipes

    def __len__(self) -> int:
        return len(self._recipes)

    def __repr__(self) -> str:
        return f"RecipeBook({len(self._recipes)} recipes)"

    def names(self) -> List[str]:
        """Return all recipe names sorted alphabetically."""
        return sorted(self._recipes.keys())

    def search(self, query: str) -> List[str]:
        """Case-insensitive substring search over recipe names."""
        q = query.lower()
        return [n for n in self._recipes if q in n.lower()]
