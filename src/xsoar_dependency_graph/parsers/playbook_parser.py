from pathlib import Path

from .basic_parser import BasicParser


class PlaybookParser(BasicParser):
    def __init__(self, playbook_path: Path) -> None:
        super().__init__()
        self.data = super().load_yaml(playbook_path)

    def get_playbook_id(self) -> str:
        return self.data["id"]

    def parse(self) -> list[tuple]:
        playbook_id = self.data["id"]

        # NetworkX is able to add edges and nodes from a bunch of tuples
        edges = []
        tasks = self.data["tasks"]
        for item in tasks:
            task = self.data["tasks"][item]["task"]
            if "playbookId" in task:
                edges.append((playbook_id, task["playbookId"], "Playbook"))
            elif "playbookName" in task:
                edges.append((playbook_id, task["playbookName"], "Playbook"))

            elif "scriptName" in task and "Builtin" not in task["scriptName"]:
                parts = task["scriptName"].split("|||")
                # We know that `parts` will always be a list with at least one element. Therefore,
                # calling `parts[-1]` will not raise an exception
                edges.append((playbook_id, parts[-1], "Script"))

            elif "script" in task and "Builtin" not in task["script"]:
                parts = task["script"].split("|||")
                # We know that `parts` will always be a list with at least one element. Therefore,
                # calling `parts[-1]` will not raise an exception
                edges.append((playbook_id, parts[-1], "Script"))
        return edges
