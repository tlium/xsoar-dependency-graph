from pathlib import Path

from parsers.basic_parser import BasicParser


class CaseTypeParser(BasicParser):
    def __init__(self, casetype_path: Path) -> None:
        super().__init__()
        self.data = super().load_json(casetype_path)

    def get_casetype_id(self) -> str:
        return f"CaseType-{self.data['id']}"

    def parse(self) -> list[tuple]:
        casetype_id = self.get_casetype_id()
        edges = []
        if "closureScript" in self.data and self.data["closureScript"] is not None:
            edges.append((casetype_id, self.data["closureScript"], "Script"))
        if "playbookId" in self.data and self.data["playbookId"] is not None:
            edges.append((casetype_id, self.data["playbookId"], "Playbook"))
        if "layout" in self.data and self.data["layout"] is not None:
            edges.append((casetype_id, f"Layout-{self.data['layout']}", "Playbook"))
        return edges
