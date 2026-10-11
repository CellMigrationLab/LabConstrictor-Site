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
SNAPSHOT_FORMAT = 3                   # bump when the snapshot layout changes; build_site refuses other formats
RESERVED_SLUGS = {"index", "assets"}  # web addresses under /apps/ that an app may not take
REPO = "https://github.com/CellMigrationLab/LabConstrictor-Site"
TEMPLATE_REPO = "CellMigrationLab/LabConstrictor"
MANIFEST_NAME = "labconstrictor-app.yaml"

# Everything build_site.py writes into docs/ (deleted and rebuilt on every run). All git-ignored.
GENERATED = ["index.md", "apps", "guides", "use", "build", "ecosystem.md", "related-projects", "submit.md", "llms.txt",
             "demo", "assets/demo", "how-it-works", "assets/how", "assets/docs-img", "assets/hubs", "assets/hosts", "assets/icons", "assets/shots", "assets/images"]


FINAL_URL = "https://labconstrictor.cellmig.org/"   # the address the docs and schemas name; until the domain is live the site is served elsewhere


def _site_url() -> str:
    """`site_url` from mkdocs.yml, ending in a slash: the one place the site's address is set."""
    m = re.search(r"^site_url:\s*(\S+)", (ROOT / "mkdocs.yml").read_text(encoding="utf-8"), re.M)
    if not m:
        fail("mkdocs.yml has no site_url")
    return m.group(1).rstrip("/") + "/"


def _listed() -> bool:
    """`extra.listed` from mkdocs.yml: false keeps the site out of search engines (noindex, robots.txt, no sitemap)."""
    m = re.search(r"^  listed:\s*(true|false)\s*(#.*)?$", (ROOT / "mkdocs.yml").read_text(encoding="utf-8"), re.M)
    if not m:
        fail("mkdocs.yml needs `extra: listed: true` or `listed: false`")
    return m.group(1) == "true"


def fail(message: str) -> NoReturn:
    """Stop with a message that says which file to fix."""
    raise SystemExit(f"labconstrictor-site: {message}")


def load_yaml(path: Path) -> Any:
    """Parse a YAML file that must exist and must not be empty."""
    if not path.is_file():
        fail(f"missing file {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        fail(f"{path} is not valid YAML: {err}")
    if data is None:
        fail(f"{path} is empty")
    return data


def load_json(path: Path) -> Any:
    """Parse a JSON file that must exist."""
    if not path.is_file():
        fail(f"missing file {path}")
    return json.loads(path.read_text(encoding="utf-8"))


SITE_URL = _site_url()
LISTED = _listed()


class AppProblem(Exception):
    """One app cannot be listed (bad manifest, missing release, changed owner...).

    The catalogue records it in build/problems.md and leaves that app out; it
    never stops the other apps and is never swallowed (see catalogue.build)."""


class FetchError(Exception):
    """GitHub could not be reached or answered with an error (network, rate limit, server error).

    Unlike AppProblem this is not about one app, so it is never recorded and skipped: it stops the whole
    fetch. Dropping apps because GitHub had a bad minute would silently shrink the live site."""

# Manifest facts the site recommends (not requires): a missing one is a warning in build/problems.md, never a reason to unlist an app.
RECOMMENDED = ("status", "quickstart", "screenshots")
SCIENTIFIC_KINDS = ("analysis", "segmentation", "simulation")   # these also need inputs and outputs
