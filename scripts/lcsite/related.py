"""data/related-projects.yaml: our wording about other people's projects, checked before it reaches a page.

Everything is validated by Python (not a JSON schema, because schema/ is published for outside authors). A problem stops the build
and names the file and the entry. Nothing has a default: a missing key, an unknown key or a link written inside prose is an error.
"""

import re
from datetime import date

from .config import DATA, fail, load_yaml

FILE = "data/related-projects.yaml"
TOP_KEYS = {"title", "page_title", "teaser", "intro", "disclosure", "shared_authors_note", "groups", "closing", "helper"}
TEASER_KEYS = {"heading", "lead", "title", "text", "link"}
GROUP_KEYS = {"key", "title", "items"}
REQUIRED = {"name", "approach", "fit", "checked"}
OPTIONAL = {"repo", "docs", "site", "doi", "reference", "shared_authors"}
PROSE = ("title", "page_title", "intro", "disclosure", "shared_authors_note", "closing", "helper")
BANNED_IN_PROSE = re.compile(r"https?://|www\.|\b[a-z0-9-]+\.(org|com|io|net|dev)\b|[\[\]<>]|\b(popular|most used|fastest|faster|best|superior|stars|downloads)\b", re.I)
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
GITHUB_ROOT = re.compile(r"^https://github\.com/[^/]+/[^/]+/?$")
DOI = re.compile(r"^10\.\d{4,9}/\S+$")


def load() -> dict:
    """The file, checked: returns the data, or stops the build naming the file and the problem."""
    data = load_yaml(DATA / "related-projects.yaml")
    check_top(data)
    return data


def check_top(data: dict) -> None:
    """The exact top-level keys, readable prose in each text, and every group."""
    if set(data) != TOP_KEYS:
        fail(f"{FILE}: the top level needs exactly {sorted(TOP_KEYS)}, got {sorted(data)}")
    for key in PROSE:
        check_text(f"{key}", data[key])
    if not isinstance(data["teaser"], dict) or set(data["teaser"]) != TEASER_KEYS:
        fail(f"{FILE}: teaser needs exactly {sorted(TEASER_KEYS)}")
    for key in TEASER_KEYS:
        check_text(f"teaser {key}", data["teaser"][key])
    names: set[str] = set()
    for group in data["groups"]:
        check_group(group, names)
        order = [e["name"].casefold() for e in group["items"]]
        if order != sorted(order):
            fail(f"{FILE}: the entries of group {group['key']} must be in alphabetical order (nothing is ranked)")


def check_text(where: str, value: object) -> None:
    """A text must be a non-empty string without a link, a bracket or a volatile word (popular, fastest, ...)."""
    if not isinstance(value, str) or not value.strip():
        fail(f"{FILE}: {where} must be a non-empty text")
    found = BANNED_IN_PROSE.search(value)
    if found:
        fail(f"{FILE}: {where} contains {found.group(0)!r}; links come from repo/docs/site, and no popularity or speed claims are made")


def check_group(group: dict, names: set[str]) -> None:
    """A group has exactly key, title and items; every item is checked and names are unique across the file."""
    if set(group) != GROUP_KEYS:
        fail(f"{FILE}: a group needs exactly {sorted(GROUP_KEYS)}, got {sorted(group)}")
    check_text(f"group {group['key']} title", group["title"])
    for entry in group["items"]:
        check_entry(entry)
        if entry["name"] in names:
            fail(f"{FILE}: the name {entry['name']} is listed twice")
        names.add(entry["name"])


def check_entry(entry: dict) -> None:
    """Required and optional keys only, a date, at least one link, doi and reference together, and clean prose."""
    keys = set(entry)
    if not REQUIRED <= keys or not keys <= REQUIRED | OPTIONAL:
        fail(f"{FILE}: an entry ({entry['name'] if 'name' in entry else 'no name'}) needs {sorted(REQUIRED)} and may add {sorted(OPTIONAL)}; got {sorted(keys)}")
    name = entry["name"]
    for key in ("name", "approach", "fit"):
        check_text(f"{name}: {key}", entry[key])
    if not entry["fit"][0].islower():
        fail(f"{FILE}: {name}: fit continues the sentence 'A good fit when ...', so it starts with a lower-case letter")
    if not isinstance(entry["checked"], date):
        fail(f"{FILE}: {name}: checked must be a date like 2026-10-11")
    if "shared_authors" in entry and entry["shared_authors"] is not True:
        fail(f"{FILE}: {name}: shared_authors is either true or left out")
    check_links(entry)


def check_links(entry: dict) -> None:
    """repo is owner/name, docs and site are https addresses that are not a GitHub repository root, and the DOI comes with its reference."""
    name = entry["name"]
    if not ({"repo", "docs", "site"} & set(entry)):
        fail(f"{FILE}: {name} needs at least one of repo, docs, site")
    if "repo" in entry and not REPO.match(entry["repo"]):
        fail(f"{FILE}: {name}: repo must look like owner/name")
    for key in ("docs", "site"):
        if key in entry and (not entry[key].startswith("https://") or GITHUB_ROOT.match(entry[key])):
            fail(f"{FILE}: {name}: {key} must be an https address that is not a GitHub repository (use repo for that)")
    if ("doi" in entry) != ("reference" in entry):
        fail(f"{FILE}: {name}: doi and reference come together")
    if "doi" in entry and not DOI.match(entry["doi"]):
        fail(f"{FILE}: {name}: the doi {entry['doi']!r} is malformed")
