from pathlib import Path

import networkx as nx

SUPPORTED_OUTPUT_FORMATS = ["GML", "GraphML", "JSON"]


class Exporter:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph

    def export(self, output_path: Path, output_format: str) -> None:
        if output_format not in SUPPORTED_OUTPUT_FORMATS:
            msg = f"Output format {output_format} not one of {','.join(SUPPORTED_OUTPUT_FORMATS)}"
            raise ValueError(msg)

        if output_format == "GML":
            nx.write_gml(self.graph, output_path)
        elif output_format == "GraphML":
            nx.write_graphml(self.graph, output_path)
        else:
            msg = f"Invalid output format. Expected one of {','.join(SUPPORTED_OUTPUT_FORMATS)}"
            raise ValueError(msg)
