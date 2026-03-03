from pathlib import Path

import networkx as nx

SUPPORTED_OUTPUT_FORMATS = ["GML", "GraphML"]


class Exporter:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph

    def export(self, output_path: Path, output_format: str) -> str:
        if output_format not in SUPPORTED_OUTPUT_FORMATS:
            msg = f"Output format {output_format} not one of {','.join(SUPPORTED_OUTPUT_FORMATS)}"
            raise ValueError(msg)

        if output_format == "GML":
            output_path = Path(output_path) / "output.gml"
            nx.write_gml(self.graph, output_path)
        elif output_format == "GraphML":
            output_path = Path(output_path) / "output.graphml"
            nx.write_graphml(self.graph, output_path)
        else:
            msg = f"Invalid output format. Expected one of {','.join(SUPPORTED_OUTPUT_FORMATS)}"
            raise ValueError(msg)
        return str(self.graph)
