from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from networkx.exception import NetworkXNoPath

from parsers.casetype_parser import CaseTypeParser
from parsers.integration_parser import IntegrationParser
from parsers.layout_parser import LayoutParser
from parsers.pack_parser import PackParser
from parsers.playbook_parser import PlaybookParser
from parsers.script_parser import ScriptParser


class ContentGraph:
    def __init__(self, *, repo_path: Path) -> None:
        """Class constructor."""
        self.G = nx.Graph()
        self.repo_path = repo_path
        self.pack_nodes = []
        self.script_nodes = []
        self.playbook_nodes = []
        self.layout_nodes = []
        self.casetype_nodes = []

        self.pack_paths = list(repo_path.glob("Packs/*"))

        self.dependency_dict = {}

    def _create_nodes_from_playbooks(self, pack_name: str, playbooks: list[Path]) -> None:
        """Creates a node for each playbook in playbooks list. Also parses the playbook yaml
        and creates playbook or script nodes for any playbooks or scripts that are called from
        the playbook."""
        for playbook_path in playbooks:
            parser = PlaybookParser(playbook_path)
            playbook_id = parser.get_playbook_id()
            self.G.add_edge(pack_name, playbook_id)
            attributes = {
                playbook_id: {
                    "node_type": "Playbook",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(self.G, attributes)
            edges = parser.parse()
            script_edges = [(edge[0], edge[1]) for edge in edges if edge[2] == "Script"]
            playbook_edges = [(edge[0], edge[1]) for edge in edges if edge[2] == "Playbook"]
            attributes = {}
            for edge in script_edges:
                attributes[edge[1]] = {
                    "node_type": "Script",
                    "pack_name": "Unknown",
                }
            self.G.add_edges_from(script_edges)
            nx.set_node_attributes(self.G, attributes)

            attributes = {}
            for edge in playbook_edges:
                attributes[edge[1]] = {
                    "node_type": "Playbook",
                    "pack_name": "Unknown",
                }
            self.G.add_edges_from(playbook_edges)
            nx.set_node_attributes(self.G, attributes)

    def _create_nodes_from_scripts(self, pack_name: str, scripts: list[Path]) -> None:
        """Adds a graph node for the script itself. Also parses the script with AST and finds
        any reference to execute_command or demisto.executeCommand and creates script nodes for
        whatever commands are executed in the script."""
        for script_path in scripts:
            parser = ScriptParser(script_path)
            if parser.is_bad_filepath(script_path):
                continue
            script_id = parser.get_script_id()
            self.G.add_node(script_id, node_type="Script")
            try:
                nx.shortest_path(self.G, source=pack_name, target=script_id)
            except NetworkXNoPath:
                self.G.add_edge(pack_name, script_id)
            attributes = {
                script_id: {
                    "node_type": "Script",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(self.G, attributes)
            edges = parser.parse()
            attributes = {}
            for edge in edges:
                attributes[edge[1]] = {
                    "node_type": "Script",
                    "pack_name": pack_name,
                }
            if edges:
                self.G.add_edges_from(edges)
                nx.set_node_attributes(self.G, attributes)

    def _create_nodes_from_layouts(self, pack_name: str, layouts: list[Path]) -> None:
        """Creates a node for the layout. Also parses the layout file and creates script
        nodes for any script such as buttons or dynamic section scripts refrenced in the layout."""
        for layout_path in layouts:
            parser = LayoutParser(layout_path)
            layout_id = parser.get_layout_id()
            self.G.add_edge(pack_name, layout_id)
            attributes = {
                layout_id: {
                    "node_type": "Layout",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(self.G, attributes)
            edges = parser.parse()
            if edges:
                self.G.add_edges_from(edges)

    def _create_nodes_from_casetypes(self, pack_name: str, casetypes: list[Path]) -> None:
        """Creates a node for each casetype in casetypes. Also parses the casetype json file and
        creates script, playbook or layout nodes if refrenced by the casetype."""
        for casetype_path in casetypes:
            parser = CaseTypeParser(casetype_path)
            casetype_id = parser.get_casetype_id()
            self.G.add_edge(pack_name, casetype_id)
            attributes = {
                casetype_id: {
                    "node_type": "CaseType",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(self.G, attributes)
            edges = parser.parse()
            attributes = {}
            for edge in edges:
                self.G.add_edge(edge[0], edge[1])
                attributes[edge[1]] = {
                    "node_type": edge[2],
                    "pack_name": "Unknown",
                }
            if edges:
                nx.set_node_attributes(self.G, attributes)

    def _create_nodes_from_integrations(self, pack_name: str, integrations: list[Path]) -> None:
        """Creates a node for each integration in `integrations`. Also parses the integration yaml
        and creates nodes for each command defined in the integration."""
        for integration_path in integrations:
            parser = IntegrationParser(integration_path)
            integration_id = parser.get_integration_id()
            self.G.add_edge(pack_name, integration_id)
            attributes = {
                integration_id: {
                    "node_type": "Integration",
                    "pack_name": pack_name,
                },
            }
            nx.set_node_attributes(self.G, attributes)
            edges = parser.parse()
            attributes = {}
            for edge in edges:
                attributes[edge[1]] = {
                    "node_type": "Integration Command",
                    "pack_name": pack_name,
                }
            if edges:
                self.G.add_edges_from(edges)
                nx.set_node_attributes(self.G, attributes)

    def _create_nodes_from_pack(self, packpath: Path) -> None:
        """Creates graph nodes from the contents of a content pack given by packpath.
        Currently creates nodes for playbooks, scripts, layouts and casetypes."""
        try:
            parser = PackParser(packpath)
            parser.parse()
            pack_name = parser.get_pack_id()
            current_version = parser.get_current_version()
            self.G.add_node(pack_name, currentVersion=current_version, node_type="Content Pack")
            self.pack_nodes.append(pack_name)
        except FileNotFoundError:
            print(f"WARNING: Failed to parse pack {packpath}. Ignoring pack.")
            return

        playbooks = list(packpath.glob("Playbooks/*.yml"))
        if playbooks:
            self._create_nodes_from_playbooks(pack_name=pack_name, playbooks=playbooks)

        layouts = list(packpath.glob("Layouts/*.json"))
        if layouts:
            self._create_nodes_from_layouts(pack_name=pack_name, layouts=layouts)

        casetypes = list(packpath.glob("IncidentTypes/*.json"))
        if casetypes:
            self._create_nodes_from_casetypes(pack_name=pack_name, casetypes=casetypes)

        integrations_paths = Path(packpath / "Integrations/")
        integrations = list(integrations_paths.rglob("*.yml"))
        if integrations:
            self._create_nodes_from_integrations(pack_name=pack_name, integrations=integrations)

        # We need to create nodes from scripts last. The reason for this is that the other content items
        # above may reference scripts. If they do then script nodes and edges are created, and we don't want to
        # create edges from the root Pack node directly to scripts when the scripts already have 1 or more edges.
        scripts_path = Path(packpath / "Scripts/")
        scripts = list(scripts_path.rglob("*.yml"))
        if scripts:
            self._create_nodes_from_scripts(pack_name=pack_name, scripts=scripts)

    def create_content_graph(self, pack_name: str = "", exclude_list: list[str] | None = None) -> None:
        """Iterates over a list of pack paths and creates nodes from the pack contents."""
        pack_paths = [Path(f"{self.repo_path}/Packs/{pack_name}")] if pack_name else self.pack_paths
        for pack in pack_paths:
            if (exclude_list and pack.stem in exclude_list) or pack.stem == "DeprecatedContent":
                # Ignore explicitly excluded content packs. Also exclude upstream "DeprecatedContent" in case
                # someone wants to plot the entire upstream content repo
                continue
            try:
                self._create_nodes_from_pack(pack)
            except Exception as ex:
                msg = f"Exception occurred when parsing pack {pack}"
                raise RuntimeError(msg) from ex

    def remove_node_by_degree(self, n: int) -> None:
        to_remove = [node for node in self.G.nodes() if self.G.degree(node) < n]  # pyright: ignore  # noqa: PGH003
        self.G.remove_nodes_from(to_remove)

    def _export_gml(self, output_path: Path) -> None:
        """Internal class method to export graph to GML file."""
        try:
            nx.write_gml(self.G, output_path)
        except Exception as e:
            msg = f"Failed to write graph to {output_path}"
            raise RuntimeError(msg) from e

    def _export_graphml(self, output_path: Path) -> None:
        """Internal class method to export graph as GraphML file."""
        try:
            nx.write_graphml(self.G, output_path)
        except Exception as e:
            msg = f"Failed to write graph to {output_path}"
            raise RuntimeError(msg) from e

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

    def plot_connected_components(self) -> None:  # noqa: PLR0915
        """Plots the Graph as a non-directional graph."""
        G = self.G  # noqa: N806

        fig = plt.figure("XSOAR content repository graph", figsize=(8, 8))
        # Create a gridspec for adding the possibility subplots of different sizes. This is done
        # in case we want to create subplots with e.g degree and rank histograms in the future.
        axgrid = fig.add_gridspec(5, 4)
        ax0 = fig.add_subplot(axgrid[0:5, :])

        # Create a subgraph of all connected components. We don't care about isolated
        # nodes at this point
        gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
        pos = nx.spring_layout(gcc, seed=10396953)

        playbook_nodes = []
        script_nodes = []
        layout_nodes = []
        pack_nodes = []
        casetype_nodes = []

        for node in G.nodes:
            data = {}
            data["num_edges"] = str(len(self.G.edges(node)))
            attrs = {node: data}
            nx.set_node_attributes(G, attrs)

        # We want to draw the various nodes with different colors depending on type. It may be a better way to deal
        # with this, but the following block kind of works...
        nodes_list = gcc.nodes(data="node_type")
        playbook_nodes = [node[0] for node in nodes_list if node[1] == "Playbook"]
        script_nodes = [node[0] for node in nodes_list if node[1] == "Script"]
        pack_nodes = [node[0] for node in nodes_list if node[1] == "Content Pack"]
        layout_nodes = [node[0] for node in nodes_list if node[1] == "Layout"]
        casetype_nodes = [node[0] for node in nodes_list if node[1] == "CaseType"]
        integration_nodes = [node[0] for node in nodes_list if node[1] == "Integration"]
        integration_commands = [node[0] for node in nodes_list if node[1] == "Integration Command"]

        nodes = nx.draw_networkx_nodes(gcc, pos, ax=ax0, node_size=20)
        nx.draw_networkx_nodes(gcc, pos, ax=ax0, nodelist=pack_nodes, node_color="tab:pink", label="Content Packs", node_size=20)
        nx.draw_networkx_nodes(gcc, pos, ax=ax0, nodelist=script_nodes, node_color="tab:green", label="Scripts", node_size=20)
        nx.draw_networkx_nodes(gcc, pos, ax=ax0, nodelist=playbook_nodes, node_color="tab:blue", label="Playbooks", node_size=20)
        nx.draw_networkx_nodes(gcc, pos, ax=ax0, nodelist=layout_nodes, node_color="tab:orange", label="Layouts", node_size=20)
        nx.draw_networkx_nodes(gcc, pos, ax=ax0, nodelist=casetype_nodes, node_color="tab:olive", label="Case Types", node_size=20)
        nx.draw_networkx_nodes(gcc, pos, ax=ax0, nodelist=integration_nodes, node_color="tab:red", label="Integrations", node_size=20)
        nx.draw_networkx_nodes(
            gcc,
            pos,
            ax=ax0,
            nodelist=integration_commands,
            node_color="yellow",
            label="Integration Commands",
            node_size=20,
        )
        nx.draw_networkx_edges(gcc, pos, ax=ax0, alpha=0.4)

        plt.legend(scatterpoints=1)
        ax0.set_axis_off()
        fig.tight_layout()

        nodes_list = np.array(list(gcc.nodes()))

        # Define coordinates and styles of annotations
        annotation = ax0.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "w"},
            arrowprops={"arrowstyle": "->"},
        )
        annotation.set_visible(False)

        def _update_annotation(ind) -> None:  # noqa: ANN001
            """Updates the annotation text. This function is called from mouseover hover events."""
            index = int(ind["ind"][0])
            node = nodes_list[index]
            xy = pos[node]
            annotation.xy = xy
            node_attr = {"node_name": node}
            node_attr.update(G.nodes[node])
            text = "\n".join(f"{k}: {v}" for k, v in node_attr.items())
            annotation.set_text(text)

        def _hover(event) -> None:  # noqa: ANN001
            """Mouseover hover event. Updates and shows the annotation of a node the mouse pointer
            is hovering over."""
            vis = annotation.get_visible()
            if event.inaxes == ax0:
                cont, ind = nodes.contains(event)
                if cont:
                    _update_annotation(ind)
                    annotation.set_visible(True)
                    fig.canvas.draw_idle()
                elif vis:
                    annotation.set_visible(False)
                    fig.canvas.draw_idle()

        def _onclick(event) -> None:  # noqa: ANN001
            """Button click event. Prings out node neighbors to the console when a node is clicked."""
            if event.inaxes == ax0:
                cont, ind = nodes.contains(event)
                if cont:
                    print(f"Clicked node {ind}")
                    index = int(ind["ind"][0])
                    node = nodes_list[index]
                    node_neighbors = nx.neighbors(gcc, node)
                    print(f"Node neighbors: {list(node_neighbors)}")

        fig.canvas.mpl_connect("motion_notify_event", _hover)
        fig.canvas.mpl_connect("button_press_event", _onclick)

        plt.show()
