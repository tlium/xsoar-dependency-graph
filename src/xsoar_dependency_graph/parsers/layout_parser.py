from pathlib import Path

from .basic_parser import BasicParser


class LayoutParser(BasicParser):
    def __init__(self, layout_path: Path) -> None:
        super().__init__()
        self.data = super().load_json(layout_path)

    def get_layout_id(self) -> str:
        return f"Layout-{self.data['id']}"

    def parse(self) -> list[tuple]:  # noqa: C901
        """Creates a node for the layout. Also parses the layout file and creates script
        nodes for any script such as buttons or dynamic section scripts refrenced in the layout."""
        layout_id = self.get_layout_id()
        edges = []
        if "detailsV2" not in self.data:
            return edges
        # Should really fix this issue properly. The case where "tabs" was not in the data was found
        # when I first tried to create a graph of the upstream content repository. Need to isolate
        # the issue and fix it
        if "tabs" not in self.data["detailsV2"]:
            return edges
        for tab in self.data["detailsV2"]["tabs"]:
            if "sections" in tab:
                for section in tab["sections"]:
                    if "queryType" in section:
                        if section["queryType"] == "script" and section["query"]:
                            script = section["query"]
                            edges.append((layout_id, script))

                    elif "items" in section:
                        for item in section["items"]:
                            if "scriptId" in item:
                                script = item["scriptId"]
                                edges.append((layout_id, script))
        return edges
