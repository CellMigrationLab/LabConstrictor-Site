"""Paths, site-wide constants, and loading data files."""

import json
import re
from pathlib import Path
from typing import Any, NoReturn

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
CONTENT = ROOT / "content"            # hand-written pages, copied into docs/ by the build
REGISTRY = ROOT / "registry"
SCHEMA = ROOT / "schema"
BUILD = ROOT / "build"                # git-ignored: snapshot, problems report, downloaded files
SNAPSHOT = BUILD / "snapshot.json"
REPO = "https://github.com/CellMigrationLab/LabConstrictor-Site"
TEMPLATE_REPO = "CellMigrationLab/LabConstrictor"
MANIFEST_NAME = "labconstrictor-app.yaml"

# Everything build_site.py writes into docs/ (deleted and rebuilt on every run). All git-ignored.
GENERATED = ["index.md", "apps", "guides", "ecosystem.md", "submit.md", "llms.txt",
             "assets/docs-img", "assets/icons", "assets/shots"]


def _site_url() -> str:
    """`site_url` from mkdocs.yml, ending in a slash: the one place the site's address is set."""
    m = re.search(r"^site_url:\s*(\S+)", (ROOT / "mkdocs.yml").read_text(encoding="utf-8"), re.M)
    if not m:
        fail("mkdocs.yml has no site_url")
    return m.group(1).rstrip("/") + "/"


def fail(message: str) -> NoReturn:
    """Stop with a message that says which file to fix."""
    raise SystemExit(f"labconstrictor-site: {message}")


def load_yaml(path: Path) -> Any:
    """Parse a YAML file that must exist; an empty file gives {}."""
    if not path.is_file():
        fail(f"missing file {path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as err:
        fail(f"{path} is not valid YAML: {err}")


def load_json(path: Path) -> Any:
    """Parse a JSON file that must exist."""
    if not path.is_file():
        fail(f"missing file {path}")
    return json.loads(path.read_text(encoding="utf-8"))


SITE_URL = _site_url()


class AppProblem(Exception):
    """One app cannot be listed (bad manifest, missing release, changed owner...).

    The catalogue records it in build/problems.md and leaves that app out; it
    never stops the other apps and is never swallowed (see catalogue.build)."""
