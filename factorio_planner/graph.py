"""
Optional graph/visualisation helpers.
Requires: networkx  (pip install factorio-calc[graph])
          matplotlib (pip install factorio-calc[graph])
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .models import ProductionPlan, ProductionNode


def _requires_networkx():
    try:
        import networkx as nx
        return nx
    except ImportError as e:
        raise ImportError(
            "Graph features require networkx. "
            "Install with: pip install factorio-calc[graph]"
        ) from e


def _requires_matplotlib():
    try:
        import matplotlib.pyplot as plt
        return plt
    except ImportError as e:
        raise ImportError(
            "Graph features require matplotlib. "
            "Install with: pip install factorio-calc[graph]"
        ) from e


def to_networkx(plan: "ProductionPlan"):
    """
    Convert a ProductionPlan to a directed networkx DiGraph.

    Nodes have attributes: rate, machines_needed, machine_type, is_raw
    Edges have attribute: rate (items/sec flowing along that edge)
    """
    nx = _requires_networkx()
    G = nx.DiGraph()

    def _add_node(node: "ProductionNode"):
        G.add_node(
            node.item,
            rate=round(node.rate, 4),
            machines=math.ceil(node.machines_needed),
            machine_type=node.machine_type,
            is_raw=node.is_raw(),
        )
        for child in node.children:
            _add_node(child)
            G.add_edge(child.item, node.item, rate=round(child.rate, 4))

    _add_node(plan.root)
    return G


def draw(plan: "ProductionPlan", figsize=(14, 8), title: str | None = None):
    """
    Draw the production chain using matplotlib + networkx.

    Returns the matplotlib Figure object so callers can save or display it.
    """
    nx = _requires_networkx()
    plt = _requires_matplotlib()

    G = to_networkx(plan)

    # Hierarchical layout via graphviz if available, else spring
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    except Exception:
        try:
            pos = nx.drawing.nx_pydot.graphviz_layout(G, prog="dot")
        except Exception:
            pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=figsize)

    raw_nodes = [n for n, d in G.nodes(data=True) if d.get("is_raw")]
    mid_nodes = [n for n, d in G.nodes(data=True) if not d.get("is_raw") and n != plan.target_item]
    top_nodes = [plan.target_item] if plan.target_item in G.nodes else []

    nx.draw_networkx_nodes(G, pos, nodelist=raw_nodes, node_color="#b5d4f4", node_size=1200, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=mid_nodes, node_color="#9fe1cb", node_size=1400, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=top_nodes, node_color="#f5c4b3", node_size=1800, ax=ax)

    nx.draw_networkx_edges(G, pos, edge_color="#888", arrows=True,
                           arrowsize=20, width=1.5, ax=ax,
                           connectionstyle="arc3,rad=0.05")

    labels = {}
    for node, data in G.nodes(data=True):
        m = data.get("machines", 0)
        r = data.get("rate", 0)
        if data.get("is_raw"):
            labels[node] = f"{node}\n{r:.1f}/s"
        else:
            labels[node] = f"{node}\n{r:.1f}/s  ×{m}"

    nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

    edge_labels = {(u, v): f"{d['rate']:.1f}/s" for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7, ax=ax)

    title = title or f"Production chain: {plan.target_item} @ {plan.target_rate}/s"
    ax.set_title(title, fontsize=13, pad=12)
    ax.axis("off")
    fig.tight_layout()
    return fig
