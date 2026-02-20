"""Dependency resolution for XSOAR content."""

from networkx.classes import Graph


class DependencyResolver:
    """Resolves content item dependencies to their parent packs.

    This class builds an internal map of which packs contain which content items
    (automations, integrations, playbooks). When building a content graph, it uses
    this map to add edges between content items and their parent packs.
    """

    def __init__(self, installed_content: dict | None = None) -> None:
        self._map: dict | None = self._generate_map(installed_content)

    def _generate_map(self, installed_content: dict | None) -> dict | None:
        """Builds a lookup table from installed content metadata.

        The resulting map allows quick lookups to find which pack contains
        a given automation, integration command, or playbook.
        """
        if not installed_content:
            return None

        command_map = {}
        for pack in installed_content:
            pack_id = pack["id"]
            command_map[pack_id] = {
                "automations": [],
                "integrations": {},
                "playbooks": [],
            }

            try:
                command_map[pack_id]["automations"] = [automation["name"] for automation in pack["contentItems"]["automation"]]
            except TypeError:
                pass

            try:
                integrations = pack["contentItems"]["integration"]
                for integration in integrations:
                    integration_commands = [command["name"] for command in integration["commands"]]
                    command_map[pack_id]["integrations"][integration["id"]] = integration_commands
            except TypeError:
                pass

            try:
                command_map[pack_id]["playbooks"] = [playbook["name"] for playbook in pack["contentItems"]["playbook"]]
            except TypeError:
                pass

        return command_map

    def add_dependency_nodes(self, name: str, graph: Graph) -> None:
        """Searches for a content item across all packs and adds edges to the graph."""
        self._add_script_dependency(name, graph)
        self._add_playbook_dependency(name, graph)
        self._add_integration_dependency(name, graph)

    def _add_script_dependency(self, script_id: str, graph: Graph) -> None:
        """Adds a pack node and edge if the script exists in installed content."""
        if not self._map:
            return
        for pack in self._map:
            if script_id in self._map[pack]["automations"]:
                graph.add_node(pack, node_type="Content Pack")
                graph.add_edge(script_id, pack)

    def _add_playbook_dependency(self, playbook_id: str, graph: Graph) -> None:
        """Adds a pack node and edge if the playbook exists in installed content."""
        if not self._map:
            return
        for pack in self._map:
            if playbook_id in self._map[pack]["playbooks"]:
                graph.add_node(pack, node_type="Content Pack")
                graph.add_edge(playbook_id, pack)

    def _add_integration_dependency(self, command_id: str, graph: Graph) -> None:
        """Adds a pack node and edge if the integration command exists in installed content."""
        if not self._map:
            return
        import networkx as nx

        for pack in self._map:
            for integration in self._map[pack]["integrations"]:
                if command_id in self._map[pack]["integrations"][integration]:
                    graph.add_node(pack, node_type="Content Pack")
                    graph.add_edge(command_id, pack)
                    attributes = {
                        command_id: {
                            "node_type": "Integration Command",
                            "pack_name": pack,
                        }
                    }
                    nx.set_node_attributes(graph, attributes)
