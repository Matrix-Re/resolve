import json
from pathlib import Path
from typing import Any

from core.constants import JSON_EXTENSION


def load_json_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)

    if file_path.suffix != JSON_EXTENSION:
        file_path = Path(f"{file_path}{JSON_EXTENSION}")

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Invalid JSON file: root element must be an object")

    return data
