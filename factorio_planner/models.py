"""Data models for production planning."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Recipe:
    """A Factorio crafting recipe."""
    name: str
    ingredients: Dict[str, float]   # item_name -> quantity per craft
    products: Dict[str, float]       # item_name -> quantity per craft
    crafting_time: float             # seconds per craft cycle
    category: str = "crafting"       # crafting, smelting, chemical, etc.
    machine: str = "assembling-machine-1"


@dataclass
class ProductionNode:
    """One node in the production tree."""
    item: str
    rate: float                      # items/second needed
    recipe: Optional[Recipe]
    machines_needed: float = 0.0
    machine_type: str = ""
    children: List["ProductionNode"] = field(default_factory=list)

    def is_raw(self) -> bool:
        """True if this item has no recipe (ore, water, etc.)."""
        return self.recipe is None


@dataclass
class ProductionPlan:
    """Full production plan for a target item."""
    target_item: str
    target_rate: float               # items/second
    root: ProductionNode
    totals: Dict[str, float] = field(default_factory=dict)         # item -> items/sec
    machine_totals: Dict[str, float] = field(default_factory=dict) # machine_type -> count
    raw_resources: Dict[str, float] = field(default_factory=dict)  # raw item -> items/sec

    def summary(self) -> str:
        lines = [
            f"Production plan: {self.target_rate:.2f} {self.target_item}/s",
            "",
            "Machines required:",
        ]
        for machine, count in sorted(self.machine_totals.items()):
            lines.append(f"  {machine}: {count:.1f}")
        lines += ["", "Raw resources (per second):"]
        for item, rate in sorted(self.raw_resources.items()):
            lines.append(f"  {item}: {rate:.2f}/s")
        return "\n".join(lines)
