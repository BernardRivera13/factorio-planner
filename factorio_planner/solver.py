"""
Core solver: resolves the full dependency graph for a production target.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import math

from .recipes import RecipeBook, Recipe


# Items considered raw materials (no recipe needed)
DEFAULT_RAW = frozenset({
    "iron-ore",
    "copper-ore",
    "coal",
    "stone",
    "crude-oil",
    "water",
    "wood",
    "uranium-ore",
    "raw-fish",
})

# Default machine crafting speeds (Factorio vanilla)
MACHINE_SPEEDS: Dict[str, float] = {
    "assembling-machine": 0.75,   # assembling machine 1
    "assembling-machine-2": 1.50,
    "assembling-machine-3": 2.25,
    "furnace": 1.0,               # stone furnace
    "electric-furnace": 2.0,
    "chemical-plant": 1.25,
    "oil-refinery": 1.0,
    "rocket-silo": 1.0,
    "centrifuge": 0.75,
    "mining-drill": 1.0,
}

# Items per second per belt tier
BELT_THROUGHPUT: Dict[str, float] = {
    "yellow": 7.5,   # transport belt
    "red": 15.0,     # fast transport belt
    "blue": 22.5,    # express transport belt
}


@dataclass
class ProductionStep:
    """
    One node in the production plan: how much of `item` to produce,
    how many machines are needed, and what raw ingredients are consumed.
    """
    item: str
    rate: float                        # items/second needed
    recipe: Recipe
    machines_needed: float             # exact (use ceil for integer count)
    machine_type: str
    machine_speed: float
    ingredient_rates: Dict[str, float] = field(default_factory=dict)

    @property
    def machines_ceil(self) -> int:
        return math.ceil(self.machines_needed)

    @property
    def belts_needed(self) -> Dict[str, float]:
        """How many belts of each tier needed to feed this step's output."""
        return {tier: self.rate / speed for tier, speed in BELT_THROUGHPUT.items()}

    def __repr__(self) -> str:
        return (
            f"ProductionStep({self.item!r}, rate={self.rate:.3f}/s, "
            f"machines={self.machines_ceil}x {self.machine_type})"
        )


@dataclass
class ProductionPlan:
    """
    The full solved production plan: an ordered list of steps (leaves first,
    target last), plus a summary of raw material rates.
    """
    target: str
    target_rate: float
    steps: List[ProductionStep] = field(default_factory=list)
    raw_rates: Dict[str, float] = field(default_factory=dict)

    @property
    def total_machines(self) -> int:
        return sum(s.machines_ceil for s in self.steps)

    def summary(self) -> str:
        """Human-readable summary of the production plan."""
        lines = [
            f"Production plan: {self.target_rate:.3f} {self.target}/s",
            f"{'─' * 50}",
        ]
        lines.append("Steps (leaves → target):")
        for step in self.steps:
            lines.append(
                f"  {step.item:<30} {step.rate:>8.3f}/s  "
                f"{step.machines_ceil:>3}× {step.machine_type}"
            )
        lines.append(f"\nRaw materials required:")
        for item, rate in sorted(self.raw_rates.items()):
            lines.append(f"  {item:<30} {rate:>8.3f}/s")
        lines.append(f"\nTotal machines: {self.total_machines}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"ProductionPlan({self.target!r}, {self.target_rate}/s, "
            f"{len(self.steps)} steps, {self.total_machines} machines)"
        )


class Solver:
    """
    Resolves the full recursive production chain for a target item.

    Uses depth-first traversal on the recipe dependency graph, accumulating
    required production rates at each node. Handles diamonds (items needed by
    multiple parents) by accumulating rates before solving sub-trees.

    Args:
        book: RecipeBook to use
        raw_items: set of item names considered raw (no recipe needed)
        machine_tier: which assembling machine tier to use by default
    """

    def __init__(
        self,
        book: RecipeBook,
        raw_items: Optional[Set[str]] = None,
        machine_tier: int = 1,
    ):
        self.book = book
        self.raw_items: Set[str] = set(raw_items) if raw_items else set(DEFAULT_RAW)
        tier_map = {1: "assembling-machine", 2: "assembling-machine-2", 3: "assembling-machine-3"}
        self.default_machine = tier_map.get(machine_tier, "assembling-machine")

    def solve(self, target: str, rate: float = 1.0) -> ProductionPlan:
        """
        Compute the full production plan for `target` at `rate` items/second.

        Args:
            target: item name to produce
            rate: desired output rate in items per second

        Returns:
            A :class:`ProductionPlan` with all steps and raw material rates.

        Raises:
            KeyError: if `target` has no recipe and is not a raw material.
        """
        # Accumulate required rates across the whole graph first
        required: Dict[str, float] = {}
        self._accumulate(target, rate, required)

        # Build steps in topological order (BFS level-by-level, leaves first)
        order = self._topological_order(target)
        steps: List[ProductionStep] = []
        raw_rates: Dict[str, float] = {}

        for item in order:
            if item in self.raw_items or item not in self.book:
                raw_rates[item] = raw_rates.get(item, 0) + required.get(item, 0)
                continue

            recipe = self.book[item]
            item_rate = required.get(item, 0.0)
            machine = recipe.machine if recipe.machine in MACHINE_SPEEDS else self.default_machine
            speed = MACHINE_SPEEDS.get(machine, 1.0)
            machines = recipe.machines_needed(item_rate, speed)

            # Compute ingredient rates for this step
            ingredient_rates: Dict[str, float] = {}
            for ing in recipe.ingredients:
                # rate of ingredient needed = (item_rate / yield) * ingredient_amount
                ing_rate = (item_rate / recipe.yield_amount) * ing.amount
                ingredient_rates[ing.name] = ing_rate

            steps.append(ProductionStep(
                item=item,
                rate=item_rate,
                recipe=recipe,
                machines_needed=machines,
                machine_type=machine,
                machine_speed=speed,
                ingredient_rates=ingredient_rates,
            ))

        return ProductionPlan(
            target=target,
            target_rate=rate,
            steps=steps,
            raw_rates=raw_rates,
        )

    def _accumulate(
        self,
        item: str,
        rate: float,
        required: Dict[str, float],
        visited: Optional[Set[str]] = None,
    ) -> None:
        """DFS accumulation of required rates (handles diamonds)."""
        required[item] = required.get(item, 0.0) + rate

        if item in self.raw_items or item not in self.book:
            return

        recipe = self.book[item]
        for ing in recipe.ingredients:
            ing_rate = (rate / recipe.yield_amount) * ing.amount
            self._accumulate(ing.name, ing_rate, required)

    def _topological_order(self, target: str) -> List[str]:
        """
        Return items in topological order (dependencies first, target last).
        Uses iterative DFS with post-order collection + deduplication.
        """
        order: List[str] = []
        seen: Set[str] = set()

        def dfs(item: str) -> None:
            if item in seen:
                return
            seen.add(item)
            if item not in self.raw_items and item in self.book:
                recipe = self.book[item]
                for ing in recipe.ingredients:
                    dfs(ing.name)
            order.append(item)

        dfs(target)
        return order
