"""
Core calculation engine.

Resolves the full production dependency tree for a target item,
computing machine counts and raw resource requirements.
"""

from __future__ import annotations
from typing import Dict, Optional
from .models import Recipe, ProductionNode, ProductionPlan
from .recipe_db import RecipeDB


class Calculator:
    """
    Compute production chains for Factorio.

    Parameters
    ----------
    db : RecipeDB, optional
        Recipe database to use. Defaults to the base-game DB.
    productivity_bonus : float
        Global productivity bonus (0.0 = none, 0.4 = +40 %).
    speed_bonus : float
        Global speed beacon bonus multiplier applied to all machines.

    Example
    -------
    >>> calc = Calculator()
    >>> plan = calc.compute("electronic-circuit", rate=10)
    >>> print(plan.summary())
    """

    def __init__(
        self,
        db: Optional[RecipeDB] = None,
        productivity_bonus: float = 0.0,
        speed_bonus: float = 0.0,
    ) -> None:
        self.db = db or RecipeDB()
        self.productivity_bonus = productivity_bonus  # e.g. 0.4 for +40%
        self.speed_bonus = speed_bonus                # e.g. 0.5 for +50% beacon

    # ------------------------------------------------------------------
    def compute(self, item: str, rate: float = 1.0) -> ProductionPlan:
        """
        Compute the full production plan for *item* at *rate* items/second.

        Parameters
        ----------
        item : str
            The target item name (e.g. ``"electronic-circuit"``).
        rate : float
            Desired production rate in items per second.

        Returns
        -------
        ProductionPlan
            Complete plan with machine counts, totals, and raw resources.
        """
        totals: Dict[str, float] = {}
        machine_totals: Dict[str, float] = {}

        root = self._build_node(item, rate, totals, machine_totals, depth=0)

        raw_resources = {
            item: r for item, r in totals.items()
            if self.db.get(item) is None
        }

        return ProductionPlan(
            target_item=item,
            target_rate=rate,
            root=root,
            totals=totals,
            machine_totals=machine_totals,
            raw_resources=raw_resources,
        )

    # ------------------------------------------------------------------
    def _build_node(
        self,
        item: str,
        rate: float,
        totals: Dict[str, float],
        machine_totals: Dict[str, float],
        depth: int,
        visited: Optional[set] = None,
    ) -> ProductionNode:
        if visited is None:
            visited = set()

        # Accumulate totals
        totals[item] = totals.get(item, 0.0) + rate

        recipe = self.db.get(item)

        if recipe is None or depth > 50:
            # Raw resource or cycle guard
            return ProductionNode(item=item, rate=rate, recipe=None)

        # How many items does one craft cycle yield?
        yield_per_craft = recipe.products.get(item, 1.0)
        effective_yield = yield_per_craft * (1.0 + self.productivity_bonus)

        # Crafts per second needed
        crafts_per_second = rate / effective_yield

        # Machine speed (base + beacon bonus)
        base_speed = self.db.machine_speed(recipe.machine)
        effective_speed = base_speed * (1.0 + self.speed_bonus)

        # Machines needed  = crafts_per_second * crafting_time / machine_speed
        machines = (crafts_per_second * recipe.crafting_time) / effective_speed

        machine_totals[recipe.machine] = (
            machine_totals.get(recipe.machine, 0.0) + machines
        )

        # Recurse on ingredients
        children = []
        if item not in visited:
            visited = visited | {item}
            for ingredient, qty_per_craft in recipe.ingredients.items():
                ingredient_rate = crafts_per_second * qty_per_craft
                child = self._build_node(
                    ingredient, ingredient_rate, totals, machine_totals,
                    depth + 1, visited,
                )
                children.append(child)

        node = ProductionNode(
            item=item,
            rate=rate,
            recipe=recipe,
            machines_needed=machines,
            machine_type=recipe.machine,
            children=children,
        )
        return node

    # ------------------------------------------------------------------
    def scale(self, plan: ProductionPlan, new_rate: float) -> ProductionPlan:
        """Return a rescaled copy of an existing plan."""
        factor = new_rate / plan.target_rate
        return self.compute(plan.target_item, new_rate)

    def machines_for(self, item: str, rate: float) -> float:
        """Shortcut: return only the number of machines for the top-level item."""
        plan = self.compute(item, rate)
        return plan.root.machines_needed
