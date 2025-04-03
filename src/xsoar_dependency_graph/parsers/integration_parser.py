from pathlib import Path

from .basic_parser import BasicParser


class IntegrationParser(BasicParser):
    def __init__(self, integration_path: Path) -> None:
        super().__init__()
        self.data = super().load_yaml(integration_path)

    def get_integration_id(self) -> str:
        return self.data["commonfields"]["id"]

    def parse(self) -> list[tuple]:
        integration_id = self.get_integration_id()
        try:
            return [(integration_id, command["name"]) for command in self.data["script"]["commands"]]
        except KeyError:
            # No commands found in integration
            return []
