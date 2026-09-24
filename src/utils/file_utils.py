
import json
from pathlib import Path
from typing import Any, Dict

from src.core.exceptions import TestDataError

TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "features" / "test_data"


def load_json(filename: str) -> Any:
    path = TEST_DATA_DIR / filename
    if not path.exists():
        raise TestDataError(f"Test data file not found: {path}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_user_fixture(key: str) -> Dict[str, Any]:
    data = load_json("users.json")
    if key not in data:
        raise TestDataError(f"No fixture '{key}'. Available: {list(data)}")
    return data[key]
