"""JSON-Schema checks for app manifests and registry entries."""

from functools import lru_cache
from typing import Any

import yaml
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


def optional_list(manifest: dict[str, Any], key: str) -> list[Any]:
    """The value of an optional list field of a validated manifest; an empty list means the author left it out.
    The one place where "absent" is turned into "none", so optional fields are easy to find."""
    return manifest[key] if key in manifest else []


def load_plain_yaml(text: str, where: str) -> Any:
    """Parse untrusted YAML. Anchors and aliases are refused: a few lines of aliases can expand into a structure
    too large to validate. Raises AppProblem for invalid YAML, aliases or an empty document."""
    try:
        if any(isinstance(event, yaml.AliasEvent) or getattr(event, "anchor", None) is not None for event in yaml.parse(text, Loader=yaml.SafeLoader)):
            raise AppProblem(f"{where} uses YAML anchors or aliases, which are not allowed")
        data = yaml.safe_load(text)
    except yaml.YAMLError as err:
        raise AppProblem(f"{where} is not valid YAML: {err}") from err
    if data is None:
        raise AppProblem(f"{where} is empty")
    return data
