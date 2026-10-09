"""The registry: one small YAML file per listed app (registry/<owner>__<repo>.yaml)."""

from pathlib import Path

from .config import REGISTRY, AppProblem, fail, load_yaml
from .validate import REGISTRY_SCHEMA, check


def expected_name(repo: str) -> str:
    """File name for a repo: "CellMigrationLab/NucleiSky" -> "CellMigrationLab__NucleiSky.yaml"."""
    return repo.replace("/", "__") + ".yaml"


def load_entry(path: Path) -> dict:
    """Read and validate one registry file; its name must match the repo it points to."""
    entry = load_yaml(path)
    check(entry, REGISTRY_SCHEMA, f"registry/{path.name}")
    if path.name != expected_name(entry["repo"]):
        raise AppProblem(f"registry/{path.name} must be named {expected_name(entry['repo'])}")
    return entry


def load_all(folder: Path = REGISTRY) -> list[dict]:
    """Every registry entry, oldest first (so the first app registered keeps a contested name), then by repo. A bad file or a repeated repo stops the build:
    the registry is reviewed in pull requests, so mistakes are fixed there."""
    entries, seen = [], {}
    for path in sorted(folder.glob("*.yaml")):
        try:
            entry = load_entry(path)
        except AppProblem as err:
            fail(str(err))
        key = entry["repo"].lower()
        if key in seen:
            fail(f"registry/{path.name} repeats {entry['repo']} (already in registry/{seen[key]})")
        seen[key] = path.name
        entries.append(entry)
    if not entries:
        fail(f"no registry entries in {folder}")
    return sorted(entries, key=lambda e: (e["added"], e["repo"].lower()))
