from pathlib import Path

from parsers.basic_parser import BasicParser


class PackParser(BasicParser):
    def __init__(self, packpath: Path) -> None:
        # print(f"Parsing pack {packpath}")
        super().__init__()
        self.packpath = packpath
        metadata_path = Path(packpath / "pack_metadata.json")
        self.metadata = super().load_json(metadata_path)

    def get_pack_id(self) -> str:
        return self.metadata["name"]

    def get_current_version(self) -> str:
        return self.metadata["currentVersion"]

    def parse(self) -> list[tuple] | None:
        return None
