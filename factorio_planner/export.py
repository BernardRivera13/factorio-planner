"""
Export utilities for ProductionPlan.
"""

from __future__ import annotations
import json
import csv
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .solver import ProductionPlan


def export_json(plan: "ProductionPlan", path: str) -> None:
    """
    Export a :class:`~factorio_calc.solver.ProductionPlan` to a JSON file.

    The output schema is::

        {
          "target": "electronic-circuit",
          "target_rate": 10.0,
          "steps": [
            {
              "item": "copper-cable",
              "rate_per_second": 30.0,
              "machines_exact": 6.666,
              "machines_ceil": 7,
              "machine_type": "assembling-machine",
              "ingredient_rates": {"copper-plate": 15.0}
            },
            ...
          ],
          "raw_materials": {
            "iron-plate": 10.0,
            "copper-ore": 15.0
          }
        }
    """
    data = {
        "target": plan.target,
        "target_rate": plan.target_rate,
        "steps": [
            {
                "item": s.item,
                "rate_per_second": round(s.rate, 6),
                "machines_exact": round(s.machines_needed, 4),
                "machines_ceil": s.machines_ceil,
                "machine_type": s.machine_type,
                "ingredient_rates": {k: round(v, 6) for k, v in s.ingredient_rates.items()},
            }
            for s in plan.steps
        ],
        "raw_materials": {k: round(v, 6) for k, v in plan.raw_rates.items()},
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_csv(plan: "ProductionPlan", path: str) -> None:
    """
    Export a :class:`~factorio_calc.solver.ProductionPlan` to a CSV file.

    Columns: item, rate_per_second, machines_exact, machines_ceil, machine_type
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["item", "rate_per_second", "machines_exact", "machines_ceil", "machine_type"],
        )
        writer.writeheader()
        for s in plan.steps:
            writer.writerow({
                "item": s.item,
                "rate_per_second": round(s.rate, 6),
                "machines_exact": round(s.machines_needed, 4),
                "machines_ceil": s.machines_ceil,
                "machine_type": s.machine_type,
            })


def export_markdown(plan: "ProductionPlan", path: str) -> None:
    """
    Export a :class:`~factorio_calc.solver.ProductionPlan` to a Markdown file.
    """
    lines = [
        f"# Production Plan: {plan.target}",
        f"",
        f"**Target:** {plan.target_rate:.3f} {plan.target}/s  ",
        f"**Total machines:** {plan.total_machines}",
        f"",
        f"## Production Steps",
        f"",
        f"| Item | Rate (items/s) | Machines (exact) | Machines (ceil) | Machine type |",
        f"|------|---------------|-----------------|----------------|-------------|",
    ]
    for s in plan.steps:
        lines.append(
            f"| `{s.item}` | {s.rate:.3f} | {s.machines_needed:.3f} "
            f"| {s.machines_ceil} | {s.machine_type} |"
        )

    lines += [
        f"",
        f"## Raw Materials",
        f"",
        f"| Material | Rate (items/s) |",
        f"|----------|---------------|",
    ]
    for item, rate in sorted(plan.raw_rates.items()):
        lines.append(f"| `{item}` | {rate:.3f} |")

    Path(path).write_text("\n".join(lines), encoding="utf-8")
