
import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft7Validator

from src.core.exceptions import SchemaValidationError
from src.core.logger import get_logger

log = get_logger("schema")
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"


def load_schema(name: str) -> Dict[str, Any]:
    if not name.endswith(".json"):
        name += ".json"
    path = SCHEMA_DIR / name
    if not path.exists():
        raise SchemaValidationError(
            f"Schema '{name}' not found in {SCHEMA_DIR}. "
            f"Available: {[p.name for p in SCHEMA_DIR.glob('*.json')]}"
        )
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_schema(payload: Any, schema_name: str) -> None:
    schema = load_schema(schema_name)
    errors = sorted(Draft7Validator(schema).iter_errors(payload), key=lambda e: e.path)
    if errors:
        details = "\n  - ".join(
            f"{'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}"
            for err in errors
        )
        raise SchemaValidationError(
            f"Response does not match schema '{schema_name}':\n  - {details}"
        )
    log.info("Schema '%s' validated successfully", schema_name)
