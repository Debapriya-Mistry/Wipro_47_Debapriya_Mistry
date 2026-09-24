from __future__ import annotations
from typing import Any,Dict,Iterable,List
import requests
from src.core.logger import get_logger

log=get_logger("assertions")

def _body_preview(response:requests.Response,limit:int=500)->str:
    text=response.text or "<empty body>"
    return text[:limit]+("..." if len(text)>limit else "")

#Hard Asserts
def assert_status_code(response:requests.Response,expected:int)->None:
    assert response.status_code == expected,(
        f"Expected status {expected} but got {response.status_code}"
        f"for {response.request.method} {response.url}\nBody: {_body_preview(response)}"
    )

def assert_status_in(response:requests.Response,expected:Iterable[int])->None:
    assert response.status_code in expected,(
        f"expected one of {expected}, got {response.status_code} for {response.url}"

    )

def assert_response_time(response:requests.Response,max_ms:float)->None:
    actual=getattr(response,"elapsed_ms",response.elapsed.total_seconds()*1000)
    assert actual<=max_ms,(
        f"Response took {actual:.0f} ms which exceeds the {max_ms:.0f} ms SLA"
    )

def assert_header_present(response: requests.Response, header: str) -> None:
    assert header.lower() in {k.lower() for k in response.headers}, (
        f"Header '{header}' missing. Present: {list(response.headers)}"
    )

def assert_content_type_json(response: requests.Response) -> None:
    ctype = response.headers.get("Content-Type", "")
    assert "application/json" in ctype.lower(), (
        f"Expected JSON content type, got '{ctype}'"
    )

def assert_json_field_equals(body: Dict[str, Any], path: str, expected: Any) -> None:
    actual = get_by_path(body, path)
    assert str(actual) == str(expected), (
        f"Field '{path}': expected '{expected}', got '{actual}'"
    )


def assert_field_not_empty(body: Dict[str, Any], path: str) -> None:
    value = get_by_path(body, path)
    assert value not in (None, "", [], {}), f"Field '{path}' is empty"

def assert_unique_ids(items: List[Dict[str, Any]], key: str = "id") -> None:
    ids = [item.get(key) for item in items]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"Duplicate '{key}' values found: {duplicates}"


#helper
def get_by_path(body: Any, path: str) -> Any:
    current = body
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        elif isinstance(current, dict):
            if part not in current:
                raise AssertionError(
                    f"Path '{path}' broke at '{part}'. Available keys: {list(current)}"
                )
            current = current[part]
        else:
            raise AssertionError(f"Cannot traverse '{part}' inside {type(current)}")
    return current


#soft assert
class SoftAssert:

    def __init__(self) -> None:
        self.errors: List[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            log.warning("Soft assertion failed: %s", message)
            self.errors.append(message)

    def equals(self, actual: Any, expected: Any, label: str) -> None:
        self.check(actual == expected, f"{label}: expected '{expected}', got '{actual}'")

    def assert_all(self) -> None:
        if self.errors:
            joined = "\n  - ".join(self.errors)
            self.errors = []
            raise AssertionError(f"{len(joined.splitlines())} soft assertion(s) failed:"
                                 f"\n  - {joined}")
