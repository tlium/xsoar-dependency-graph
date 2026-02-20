"""Graph building logic for XSOAR content dependency graphs."""

from pathlib import Path

import networkx as nx
from networkx.exception import NetworkXNoPath

from .dependency_resolver import DependencyResolver
from .parsers.casetype_parser import CaseTypeParser
from .parsers.integration_parser import IntegrationParser
from .parsers.layout_parser import LayoutParser
from .parsers.pack_parser import PackParser
from .parsers.playbook_parser import PlaybookParser
from .parsers.script_parser import ScriptParser


class GraphBuilder:
    """Builds content graphs by parsing XSOAR content packs and creating nodes/edges."""

    def __init__(self, resolver: DependencyResolver) -> None:
        self._resolver = resolver

    def create_nodes_from_pack(self, packpath: Path, graph: nx.Graph) -> None:
        """Creates graph nodes from the contents of a content pack.

        Currently creates nodes for playbooks, scripts, layouts, casetypes and integrations.
        """
        try:
            parser = PackParser(packpath)
            parser.parse()
            pack_name = parser.get_pack_id()
            current_version = parser.get_current_version()
            graph.add_node(pack_name, currentVersion=current_version, node_type="Content Pack")
        except FileNotFoundError:
            print(f"WARNING: Failed to parse pack {packpath}. Ignoring pack.")
            return

        playbooks = list(packpath.glob("Playbooks/*.yml"))
        if playbooks:
            self._create_nodes_from_playbooks(pack_name, playbooks, graph)

        layouts = list(packpath.glob("Layouts/*.json"))
        if layouts:
            self._create_nodes_from_layouts(pack_name, layouts, graph)

        casetypes = list(packpath.glob("IncidentTypes/*.json"))
        if casetypes:
            self._create_nodes_from_casetypes(pack_name, casetypes, graph)

        integrations_paths = Path(packpath / "Integrations/")
        integrations = list(integrations_paths.rglob("*.yml"))
        if integrations:
            self._create_nodes_from_integrations(pack_name, integrations, graph)

        # Scripts are created last because other content items may reference them.
        # If they do, script nodes and edges are already created, and we don't want
        # to create edges from the pack node directly to scripts that already have edges.
        scripts_path = Path(packpath / "Scripts/")
        scripts = list(scripts_path.rglob("*.yml"))
        if scripts:
            self._create_nodes_from_scripts(pack_name, scripts, graph)

    def _create_nodes_from_playbooks(self, pack_name: str, playbooks: list[Path], graph: nx.Graph) -> None:
        """Creates nodes for playbooks and their referenced scripts/playbooks."""
        for playbook_path in playbooks:
            parser = PlaybookParser(playbook_path)
            playbook_id = parser.get_playbook_id()
            graph.add_edge(pack_name, playbook_id)
            attributes = {
                playbook_id: {
                    "node_type": "Playbook",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(graph, attributes)
            edges = parser.parse()
            script_edges = [(edge[0], edge[1]) for edge in edges if edge[2] == "Script"]
            playbook_edges = [(edge[0], edge[1]) for edge in edges if edge[2] == "Playbook"]

            attributes = {}
            for edge in script_edges:
                attributes[edge[1]] = {
                    "node_type": "Script",
                }
            graph.add_edges_from(script_edges)
            nx.set_node_attributes(graph, attributes)
            for edge in script_edges:
                self._resolver.add_dependency_nodes(edge[1], graph)

            attributes = {}
            for edge in playbook_edges:
                attributes[edge[1]] = {
                    "node_type": "Playbook",
                }
            graph.add_edges_from(playbook_edges)
            nx.set_node_attributes(graph, attributes)
            for edge in playbook_edges:
                self._resolver.add_dependency_nodes(edge[1], graph)

    def _create_nodes_from_scripts(self, pack_name: str, scripts: list[Path], graph: nx.Graph) -> None:
        """Creates nodes for scripts and their execute_command dependencies."""
        for script_path in scripts:
            parser = ScriptParser(script_path)
            if parser.is_bad_filepath(script_path):
                continue
            script_id = parser.get_script_id()
            graph.add_node(script_id, node_type="Script")
            try:
                nx.shortest_path(graph, source=pack_name, target=script_id)
            except NetworkXNoPath:
                graph.add_edge(pack_name, script_id)
            attributes = {
                script_id: {
                    "node_type": "Script",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(graph, attributes)
            edges = parser.parse()
            attributes = {}
            for edge in edges:
                attributes[edge[1]] = {
                    "node_type": "Script",
                }
            if edges:
                graph.add_edges_from(edges)
                nx.set_node_attributes(graph, attributes)
            for edge in edges:
                self._resolver.add_dependency_nodes(edge[1], graph)

    def _create_nodes_from_layouts(self, pack_name: str, layouts: list[Path], graph: nx.Graph) -> None:
        """Creates nodes for layouts and their referenced scripts."""
        for layout_path in layouts:
            parser = LayoutParser(layout_path)
            layout_id = parser.get_layout_id()
            graph.add_edge(pack_name, layout_id)
            attributes = {
                layout_id: {
                    "node_type": "Layout",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(graph, attributes)
            edges = parser.parse()
            if edges:
                graph.add_edges_from(edges)
            for edge in edges:
                self._resolver.add_dependency_nodes(edge[1], graph)

    def _create_nodes_from_casetypes(self, pack_name: str, casetypes: list[Path], graph: nx.Graph) -> None:
        """Creates nodes for casetypes and their referenced scripts/playbooks/layouts."""
        for casetype_path in casetypes:
            parser = CaseTypeParser(casetype_path)
            casetype_id = parser.get_casetype_id()
            graph.add_edge(pack_name, casetype_id)
            attributes = {
                casetype_id: {
                    "node_type": "CaseType",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(graph, attributes)
            edges = parser.parse()
            attributes = {}
            for edge in edges:
                graph.add_edge(edge[0], edge[1])
                attributes[edge[1]] = {
                    "node_type": edge[2],
                }
            if edges:
                nx.set_node_attributes(graph, attributes)
            for edge in edges:
                self._resolver.add_dependency_nodes(edge[1], graph)

    def _create_nodes_from_integrations(self, pack_name: str, integrations: list[Path], graph: nx.Graph) -> None:
        """Creates nodes for integrations and their commands."""
        for integration_path in integrations:
            parser = IntegrationParser(integration_path)
            integration_id = parser.get_integration_id()
            graph.add_edge(pack_name, integration_id)
            attributes = {
                integration_id: {
                    "node_type": "Integration",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(graph, attributes)
            edges = parser.parse()
            attributes = {}
            for edge in edges:
                attributes[edge[1]] = {
                    "node_type": "Integration Command",
                    "pack_name": pack_name,
                }
            if edges:
                graph.add_edges_from(edges)
                nx.set_node_attributes(graph, attributes)
