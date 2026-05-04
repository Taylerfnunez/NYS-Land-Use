"""Graph construction utilities."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np


def build_graph_from_config(graph_cfg: dict) -> nx.Graph:
    """Build a NetworkX graph from graph.json settings."""
    graph_type = graph_cfg.get("graph_type", "path")
    n = int(graph_cfg.get("num_nodes", 6))

    if graph_type == "path":
        G = nx.path_graph(n)
    elif graph_type == "cycle":
        G = nx.cycle_graph(n)
    elif graph_type == "complete":
        G = nx.complete_graph(n)
    elif graph_type == "star":
        # NetworkX star_graph(m) has m+1 nodes.
        G = nx.star_graph(n - 1)
    elif graph_type == "erdos_renyi":
        p = float(graph_cfg.get("p", 0.3))
        seed = graph_cfg.get("seed", None)
        G = nx.erdos_renyi_graph(n, p, seed=seed)
    elif graph_type == "from_edges":
        G = nx.Graph()
        G.add_nodes_from(range(n))
        edges = graph_cfg.get("edges", [])
        weighted = bool(graph_cfg.get("weighted", False))
        for edge in edges:
            if weighted:
                i, j, w = edge
                G.add_edge(int(i), int(j), weight=float(w))
            else:
                i, j = edge[:2]
                G.add_edge(int(i), int(j), weight=1.0)
    elif graph_type == "from_adjacency_csv":
        path = Path(graph_cfg["adjacency_csv"])
        A = np.loadtxt(path, delimiter=",")
        G = nx.from_numpy_array(A)
    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    return G


def adjacency_matrix(G: nx.Graph) -> np.ndarray:
    """Return dense weighted adjacency matrix."""
    return nx.to_numpy_array(G, weight="weight", dtype=float)


def save_graph_outputs(G: nx.Graph, output_dir: Path) -> None:
    """Save adjacency and edge list to output folder."""
    A = adjacency_matrix(G)
    np.savetxt(output_dir / "adjacency.csv", A, delimiter=",", fmt="%.8g")

    with open(output_dir / "edge_list.csv", "w", encoding="utf-8") as f:
        f.write("source,target,weight\n")
        for i, j, data in G.edges(data=True):
            f.write(f"{i},{j},{data.get('weight', 1.0)}\n")
