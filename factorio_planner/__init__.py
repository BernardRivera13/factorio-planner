"""
factorio-planner: Production chain calculator for Factorio.

Given a target item and production rate, computes the full
dependency tree: machines, belts, inserters, and raw resources.
"""

from .calculator import Calculator
from .recipe_db import RecipeDB
from .models import ProductionNode, ProductionPlan
from .formatter import format_plan, format_tree

__version__ = "0.1.0"
__author__ = "factorio-planner contributors"

__all__ = [
    "Calculator",
    "RecipeDB",
    "ProductionNode",
    "ProductionPlan",
    "format_plan",
    "format_tree",
]
