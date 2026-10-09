"""JSON-Schema checks for app manifests and registry entries."""

from functools import lru_cache
from typing import Any

from jsonschema import Draft202012Validator

from .config import SCHEMA, AppProblem, load_json

MANIFEST_SCHEMA = "labconstrictor-app.schema.json"
REGISTRY_SCHEMA = "registry-entry.schema.json"


@lru_cache(maxsize=None)
def _validator(schema_file: str) -> Draft202012Validator:
    """The validator for a file in schema/ (loaded once)."""
    return Draft202012Validator(load_json(SCHEMA / schema_file))


def describe(error: Any) -> str:
    """One schema error as "path: message" ("(top level)" for the whole document)."""
    where = "/".join(str(p) for p in error.absolute_path) or "(top level)"
    return f"{where}: {error.message}"


def check(instance: Any, schema_file: str, where: str) -> None:
    """Raise AppProblem listing every way `instance` breaks the schema; return when it is valid."""
    errors = sorted(_validator(schema_file).iter_errors(instance), key=lambda e: list(e.absolute_path))
    if errors:
        raise AppProblem(f"{where} is invalid: " + "; ".join(describe(e) for e in errors))
