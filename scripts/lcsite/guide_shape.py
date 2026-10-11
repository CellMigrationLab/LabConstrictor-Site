"""The shape of the critical guides: what a first-time reader needs to find in each (a report, for now only warnings).

A critical guide should say what you need before you start, how to check that it worked, and where to look if it does not.
The report reads the built pages; when the template's pages comply, `warnings` can become a failure.
"""

import re
from pathlib import Path

from .config import DATA, fail, load_yaml

WANTED = (("what you need", "before you start"), ("check that it worked",), ("if something does not work",))
H2 = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.S)
TAG = re.compile(r"<[^>]+>")


def headings(html: str) -> list[str]:
    """The lower-case texts of a page's level-2 headings (tags and the permalink mark removed)."""
    return [TAG.sub("", h).replace("¶", "").strip().lower() for h in H2.findall(html)]


def missing_sections(found: list[str], wanted: tuple[tuple[str, ...], ...] = WANTED) -> list[str]:
    """The wanted headings a guide lacks; each entry of `wanted` lists accepted wordings, and the first is reported."""
    return [options[0] for options in wanted if not any(h in options for h in found)]


def critical_slugs() -> list[str]:
    """The `critical:` list of data/guides.yaml; stops the build when it is missing or not a list of slugs."""
    data = load_yaml(DATA / "guides.yaml")
    if "critical" not in data or not isinstance(data["critical"], list) or not data["critical"]:
        fail("data/guides.yaml needs a `critical:` list of guide slugs")
    return data["critical"]


def warnings(site_dir: Path, slugs: list[str]) -> list[str]:
    """One "WARNING <guide>: missing section <heading>" line per missing section; an unknown slug stops the build (no silent skip)."""
    found = []
    for slug in slugs:
        page = site_dir / "guides" / slug / "index.html"
        if not page.is_file():
            fail(f"data/guides.yaml lists the critical guide {slug}, but {page} does not exist")
        found += [f"WARNING guides/{slug}: missing section '{m}'" for m in missing_sections(headings(page.read_text(encoding='utf-8')))]
    return found
