import json
from pathlib import Path

import yaml


class BasicParser:
    def __init__(self) -> None:
        pass

    def load_json(self, filepath: Path):  # noqa: ANN201
        with filepath.open("r") as f:
            return json.load(f)

    def load_yaml(self, filepath: Path):  # noqa: ANN201
        """Loads a YAML file and produce the corresponding Python object."""
        with filepath.open("r") as f:
            try:
                return yaml.safe_load(f)
            except yaml.YAMLError as e:
                msg = f"Failed to parse yaml file {filepath}"
                raise RuntimeError(msg) from e

    def is_bad_filepath(self, filepath: Path) -> bool:
        if "test" in filepath.stem.lower():
            # Try to ignore files like Packs/CommunityCommonScripts/Scripts/DateTimeNowToEpoch/TestPlaybooks/DateTimeNowToEpoch_test.yml
            return True
        if "test_data" in str(filepath):  # noqa: SIM103
            # Try to ignore test_data like Packs/Sigma/Scripts/CreateSigmaRuleIndicator/test_data/sigma_rule.yml
            return True
        return False
