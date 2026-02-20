from dataclasses import dataclass, field
from typing import Any

import networkx as nx
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.text import Annotation


@dataclass
class PlotInteractionHandler:
    """Handles mouse interaction events for the graph plot."""

    graph: nx.Graph
    fig: Figure
    ax: Axes
    pos: dict[str, tuple[float, float]]
    nodes: Any  # matplotlib PathCollection
    nodes_list: np.ndarray
    annotation: Annotation
    pinned_annotations: dict[str, Annotation] = field(default_factory=dict)

    def _node_text(self, node: str) -> str:
        """Format node attributes as text for annotation display."""
        node_attr = {"node_name": node}
        node_attr.update(self.graph.nodes[node])
        return "\n".join(f"{k}: {v}" for k, v in node_attr.items())

    def _make_annotation(self, *, xy: tuple[float, float], text: str) -> Annotation:
        """Create a new pinned annotation at the given position."""
        ann = self.ax.annotate(
            text,
            xy=xy,
            xytext=(20, 20),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "w"},
            arrowprops={"arrowstyle": "->"},
        )
        ann.set_visible(True)
        return ann

    def _node_from_ind(self, ind: dict) -> str:
        """Get node identifier from matplotlib event index."""
        index = int(ind["ind"][0])
        return str(self.nodes_list[index])

    def _update_annotation(self, ind: dict) -> None:
        """Update the hover annotation text and position."""
        node = self._node_from_ind(ind)
        xy = self.pos[node]
        self.annotation.xy = xy
        self.annotation.set_text(self._node_text(node))

    def on_hover(self, event: Any) -> None:
        """Handle mouseover hover events to show node annotations."""
        vis = self.annotation.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.nodes.contains(event)
            if cont:
                node = self._node_from_ind(ind)
                if node in self.pinned_annotations:
                    if vis:
                        self.annotation.set_visible(False)
                        self.fig.canvas.draw_idle()
                    return

                self._update_annotation(ind)
                self.annotation.set_visible(True)
                self.fig.canvas.draw_idle()
            elif vis:
                self.annotation.set_visible(False)
                self.fig.canvas.draw_idle()

    def on_click(self, event: Any) -> None:
        """Handle click events to pin/unpin node annotations."""
        if event.inaxes != self.ax:
            return

        # Right-click: clear all pinned annotations
        if event.button == 3:
            if self.pinned_annotations:
                for ann in self.pinned_annotations.values():
                    ann.remove()
                self.pinned_annotations.clear()
                self.annotation.set_visible(False)
                self.fig.canvas.draw_idle()
            return

        # Only handle left-click for pin/unpin
        if event.button != 1:
            return

        cont, ind = self.nodes.contains(event)
        if not cont:
            return

        node = self._node_from_ind(ind)

        # Toggle pinned annotation off if already pinned
        if node in self.pinned_annotations:
            self.pinned_annotations[node].remove()
            del self.pinned_annotations[node]
            self.fig.canvas.draw_idle()
            return

        # Pin a new persistent annotation for this node
        xy = self.pos[node]
        self.pinned_annotations[node] = self._make_annotation(xy=xy, text=self._node_text(node))
        self.annotation.set_visible(False)
        self.fig.canvas.draw_idle()

    def connect(self) -> None:
        """Connect event handlers to the figure canvas."""
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
