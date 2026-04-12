"""
Graph visualisation example.
Requires: pip install "factorio-calc[graph]"
"""

from factorio_planner import Calculator
from factorio_planner.graph import draw, to_networkx
import matplotlib.pyplot as plt

calc = Calculator()

# --- 1. Electronic circuit chain ---
plan = calc.compute("electronic-circuit", rate=10)
fig = draw(plan, figsize=(12, 7), title="Electronic Circuit — 10/s")
fig.savefig("electronic_circuit_chain.png", dpi=150, bbox_inches="tight")
print("Saved: electronic_circuit_chain.png")

# --- 2. Chemical science pack (more complex) ---
plan2 = calc.compute("chemical-science-pack", rate=1)
fig2 = draw(plan2, figsize=(16, 10), title="Chemical Science Pack — 1/s")
fig2.savefig("chemical_science_chain.png", dpi=150, bbox_inches="tight")
print("Saved: chemical_science_chain.png")

# --- 3. Inspect the networkx graph directly ---
G = to_networkx(plan)
print(f"\nelectronic-circuit graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print("Nodes:", list(G.nodes(data=True)))
