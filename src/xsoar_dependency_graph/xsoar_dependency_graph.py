from __future__ import annotations

from pathlib import Path

import networkx as nx

from .dependency_resolver import DependencyResolver
from .graph_builder import GraphBuilder
from .visualization import plot_graph


class ContentGraph:
    def __init__(self, *, upstream_repo_path: Path | None = None, repo_path: Path, installed_content: dict | None = None) -> None:
        self.custom_graph = nx.Graph()
        self.upstream_graph = nx.Graph()
        self.repo_path = repo_path
        self.pack_paths = list(repo_path.glob("Packs/*"))
        resolver = DependencyResolver(installed_content)
        self._builder = GraphBuilder(resolver)

        if upstream_repo_path:
            self.upstream_paths = [
                Path(upstream_repo_path / "Packs/Base"),
                Path(upstream_repo_path / "Packs/CommonPlaybooks"),
                Path(upstream_repo_path / "Packs/CommonScripts"),
            ]
        else:
            self.upstream_paths = []

    def _create_graph_from_upstream_packs(self) -> None:
        """Adds nodes to the graph from the upstream content packs Base, CommonPlaybooks, CommonScripts. Requires a valid
        path to the upstream content in class constructor. Will silently continue if class is instantiated without a path
        to the upstream content."""
        for pack in self.upstream_paths:
            try:
                print(f"Creating from {pack}")
                self._builder.create_nodes_from_pack(pack, self.upstream_graph)
            except Exception as ex:
                msg = f"Exception occurred when parsing pack {pack}"
                raise RuntimeError(msg) from ex

    def _create_graph_from_custom_packs(self, pack_paths: list[Path] | None, exclude_list: list[str] | None = None) -> None:
        """Adds nodes to the content graph from the local custom content repository."""
        if not pack_paths:
            pack_paths = self.pack_paths
        for pack in pack_paths:
            if (exclude_list and pack.stem in exclude_list) or pack.stem == "DeprecatedContent":
                # Ignore explicitly excluded content packs. Also exclude upstream "DeprecatedContent" in case
                # someone wants to plot the entire upstream content repo
                continue
            try:
                self._builder.create_nodes_from_pack(pack, self.custom_graph)
            except Exception as ex:
                msg = f"Exception occurred when parsing pack {pack}"
                raise RuntimeError(msg) from ex

    def create_content_graph(self, pack_paths: list[Path] | None, exclude_list: list[str] | None = None) -> None:
        self._create_graph_from_custom_packs(pack_paths=pack_paths, exclude_list=exclude_list)
        self._create_graph_from_upstream_packs()
        self._link_common_upstream_dependencies()

    def _link_common_upstream_dependencies(self) -> None:
        """Adds nodes for and edges to Base, Common Playbooks and Common Scripts if references to those packs
        are found in the custom dependency graph."""
        for node, data in self.upstream_graph.nodes(data=True):
            try:
                if self.custom_graph.has_node(node) and data["pack_name"] in ["Base", "Common Playbooks", "Common Scripts"]:
                    self.custom_graph.add_node(data["pack_name"], currentVersion="666", node_type="Content Pack")
                    self.custom_graph.add_edge(node, data["pack_name"])
            except KeyError:
                continue

        pack_nodes = [x[0] for x in self.upstream_graph.nodes(data="node_type") if x[1] == "Content Pack"]
        for pack_name in pack_nodes:
            self.custom_graph.add_node(pack_name, currentVersion="666", node_type="Content Pack")

    def _export_gml(self, output_path: Path) -> None:
        raise NotImplementedError

    def _export_graphml(self, output_path: Path) -> None:
        raise NotImplementedError

    def export(self, output_path: Path, fmt: str = "GraphML") -> None:
        """Exports the full graph (including isolated nodes) to `output_path`. Filenames ending in .gz or .bz2 will be compressed.
        Valid `fmt` options are one of ["GraphML, "JSON"]. Also see networkx.org for documentation on reading and writing graphs."""
        output_formats = ["GraphML", "GML"]
        if fmt not in output_formats:
            msg = f"Output format {fmt} not one of {','.join(output_formats)}"
            raise ValueError(msg)

        if fmt == "GraphML":
            self._export_graphml(output_path)
        elif fmt == "JSON":
            self._export_gml(output_path)
        else:
            msg = f"Invalid output format. Expected one of {','.join(output_formats)}"
            raise ValueError(msg)

    def plot_connected_components(self) -> None:
        """Plots the graph as a non-directional graph with interactive node inspection."""
        plot_graph(self.custom_graph)
