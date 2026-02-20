"""Visualization functions for XSOAR content dependency graphs."""

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .utils.plot_interaction import PlotInteractionHandler

# Color palette for node types in graph visualization.
# Uses colorblind-friendly colors from the Okabe-Ito palette.
NODE_PALETTE = {
    "Script": "#009E73",
    "Playbook": "#0072B2",
    "Content Pack": "#CC79A7",
    "Layout": "#E69F00",
    "CaseType": "#D55E00",
    "Integration": "#56B4E9",
    "Integration Command": "#F0E442",
}

# Display labels for node types in graph legend.
NODE_TYPE_LABELS = {
    "Script": "Scripts",
    "Playbook": "Playbooks",
    "Content Pack": "Content Packs",
    "Layout": "Layouts",
    "CaseType": "Case Types",
    "Integration": "Integrations",
    "Integration Command": "Integration Commands",
}


def _categorize_nodes_by_type(graph: nx.Graph) -> dict[str, list[str]]:
    """Groups graph nodes by their node_type attribute."""
    categorized: dict[str, list[str]] = {}
    for node, node_type in graph.nodes(data="node_type"):
        if node_type not in categorized:
            categorized[node_type] = []
        categorized[node_type].append(node)
    return categorized


def plot_graph(graph: nx.Graph) -> None:
    """Plots the graph as a non-directional graph with interactive node inspection."""
    fig = plt.figure("XSOAR content repository graph", figsize=(8, 8))
    axgrid = fig.add_gridspec(5, 4)
    ax0 = fig.add_subplot(axgrid[0:5, :])

    # Create a subgraph of all connected components. We don't care about isolated
    # nodes at this point.
    gcc = graph.subgraph(sorted(nx.connected_components(graph), key=len, reverse=True)[0])
    pos = nx.spring_layout(gcc, seed=10396953)

    # Draw all nodes first (provides base layer), then draw colored nodes by type
    nodes = nx.draw_networkx_nodes(gcc, pos, ax=ax0, node_size=30)

    categorized_nodes = _categorize_nodes_by_type(gcc)
    for node_type, node_list in categorized_nodes.items():
        if node_type not in NODE_PALETTE:
            continue
        nx.draw_networkx_nodes(
            gcc,
            pos,
            ax=ax0,
            nodelist=node_list,
            node_color=NODE_PALETTE[node_type],
            edgecolors="black",
            linewidths=0.8,
            label=NODE_TYPE_LABELS.get(node_type, node_type),
            node_size=30,
        )
    nx.draw_networkx_edges(gcc, pos, ax=ax0, alpha=0.4)

    plt.legend(scatterpoints=1)
    ax0.set_axis_off()
    fig.tight_layout()

    nodes_list = np.array(list(gcc.nodes()))

    # Define coordinates and styles of hover annotation
    annotation = ax0.annotate(
        "",
        xy=(0, 0),
        xytext=(20, 20),
        textcoords="offset points",
        bbox={"boxstyle": "round", "fc": "w"},
        arrowprops={"arrowstyle": "->"},
    )
    annotation.set_visible(False)

    # Set up interaction handler and connect events
    handler = PlotInteractionHandler(
        graph=graph,
        fig=fig,
        ax=ax0,
        pos=pos,
        nodes=nodes,
        nodes_list=nodes_list,
        annotation=annotation,
    )
    handler.connect()

    plt.show()
