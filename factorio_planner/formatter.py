"""
Text and tree formatters for production plans.
"""

from __future__ import annotations
import math
from .models import ProductionNode, ProductionPlan


def format_tree(node: ProductionNode, prefix: str = "", connector: str = "") -> str:
    """
    Return a Unicode tree view of the production node.

    Example output::

        electronic-circuit  ×10.00/s  [×5.0 assembling-machine-1]
        ├── iron-plate  ×10.00/s  [×1.6 stone-furnace]
        │   └── iron-ore  ×10.00/s  [RAW]
        └── copper-cable  ×30.00/s  [×7.5 assembling-machine-1]
            └── copper-plate  ×15.00/s  [×2.4 stone-furnace]
                └── copper-ore  ×15.00/s  [RAW]
    """
    if node.is_raw():
        machine_str = "[RAW]"
    else:
        count = math.ceil(node.machines_needed * 100) / 100
        machine_str = f"[×{count:.1f} {node.machine_type}]"

    lines = [f"{connector}{node.item}  ×{node.rate:.2f}/s  {machine_str}"]

    for i, child in enumerate(node.children):
        is_last = i == len(node.children) - 1
        child_connector = prefix + ("└── " if is_last else "├── ")
        child_prefix    = prefix + ("    " if is_last else "│   ")
        lines.append(format_tree(child, child_prefix, child_connector))

    return "\n".join(lines)


def format_plan(plan: ProductionPlan, show_tree: bool = True) -> str:
    """Return a full formatted production plan as a string."""
    sep = "─" * 60
    lines = [
        sep,
        f"  FACTORIO PRODUCTION PLAN",
        f"  Target: {plan.target_rate:.2f} × {plan.target_item} / second",
        sep,
    ]

    if show_tree:
        lines += ["", "Production tree:", ""]
        lines.append(format_tree(plan.root))

    lines += ["", sep, "  Machines required (ceil = actual buildings needed)", sep]
    for machine, count in sorted(plan.machine_totals.items()):
        lines.append(f"  {machine:<30}  {count:6.2f}  (≥ {math.ceil(count)})")

    lines += ["", sep, "  Raw resources  (items / second)", sep]
    for item, rate in sorted(plan.raw_resources.items()):
        lines.append(f"  {item:<30}  {rate:8.3f} /s")

    lines += [sep, ""]
    return "\n".join(lines)


def to_dict(plan: ProductionPlan) -> dict:
    """Serialize a ProductionPlan to a plain dict (JSON-serialisable)."""

    def node_to_dict(node: ProductionNode) -> dict:
        return {
            "item": node.item,
            "rate": round(node.rate, 6),
            "machines_needed": round(node.machines_needed, 4),
            "machine_type": node.machine_type,
            "is_raw": node.is_raw(),
            "children": [node_to_dict(c) for c in node.children],
        }

    return {
        "target_item": plan.target_item,
        "target_rate": plan.target_rate,
        "machine_totals": {k: round(v, 4) for k, v in plan.machine_totals.items()},
        "raw_resources": {k: round(v, 6) for k, v in plan.raw_resources.items()},
        "tree": node_to_dict(plan.root),
    }
