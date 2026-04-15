"""Graph plotting helpers for benchmark instances."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx

from qubo_vqa.utils.io import ensure_directory


def plot_maxcut_partition(
    graph: nx.Graph,
    left_partition: list[int],
    right_partition: list[int],
    output_path: Path,
) -> None:
    """Plot a graph with nodes colored by the decoded cut partition."""
    ensure_directory(output_path.parent)
    positions = nx.spring_layout(graph, seed=7)
    colors = ["tab:blue" if node in left_partition else "tab:orange" for node in graph.nodes()]

    fig, axis = plt.subplots(figsize=(5, 5))
    nx.draw_networkx(graph, pos=positions, node_color=colors, ax=axis)
    axis.set_title("MaxCut partition")
    axis.set_axis_off()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
