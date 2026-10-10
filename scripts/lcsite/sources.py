"""Guides that live in other repositories: fetched once, converted for the site.

A guide is one Markdown file kept in the repository it describes (`docs/user-guide.md`). data/guides.yaml
lists it as `{slug, repo, path}`; adding a module to the site is adding one such line. `fetch` downloads
the files (the only network step for guides); the rest reads them from build/sources/ and works offline.
Anything that cannot be converted (no title, a relative link or picture) stops the build.
"""

import re
from pathlib import Path

from .config import BUILD, fail
from .github import GitHub, NotFound

SOURCES = BUILD / "sources"
HEADING = re.compile(r"^# (.+?)\s*$", re.M)
ALERT = re.compile(r"^> \[!(?P<kind>NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\n(?P<body>(?:>.*\n?)+)", re.M)
ALERT_TITLE = re.compile(r"^\*\*(.+?)\.?\*\*\s*")
RELATIVE = re.compile(r"!?\[[^\]]*\]\(\s*(?!(?:[a-z][a-z0-9+.-]*:|#|/))([^)\s]+)")
BLOB = re.compile(r"\]\(https://github\.com/([\w.-]+/[\w.-]+)/blob/(?:main|HEAD)/([^)\s#]+)(#[^)\s]*)?\)")
KINDS = {"NOTE": "note", "TIP": "tip", "IMPORTANT": "warning", "WARNING": "warning", "CAUTION": "danger"}


def local_path(repo: str, path: str) -> Path:
    """Where a fetched guide is stored: build/sources/<owner>__<repo>/<path>."""
    return SOURCES / repo.replace("/", "__") / path


def fetch(entries: list[dict], github: GitHub, ref: str) -> None:
    """Download every guide to build/sources/. A missing file stops with its repository and path (never skipped)."""
    for e in entries:
        try:
            data = github.raw(e["repo"], ref, e["path"])
        except NotFound:
            fail(f"data/guides.yaml lists {e['path']} in {e['repo']} at {ref}, which does not exist: add it there first")
        target = local_path(e["repo"], e["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def read(repo: str, path: str) -> str:
    """The fetched text of a guide; stops the build when fetch has not been run for it."""
    target = local_path(repo, path)
    if not target.is_file():
        fail(f"{target} is missing: run scripts/fetch_guides.py first")
    return target.read_text(encoding="utf-8")


def title_of(text: str, where: str) -> str:
    """The first `# Heading` of a guide: its title on the site. Stops the build when there is none."""
    m = HEADING.search(text)
    if not m:
        fail(f"{where} has no '# Title' line")
    return m.group(1)


def admonitions(text: str) -> str:
    """GitHub alerts (`> [!WARNING]` + quoted lines) -> the site's `!!! warning "Title"` boxes.
    A leading **bold sentence** in the alert becomes the box title; otherwise the title is the kind."""
    def box(m: re.Match) -> str:
        """One alert rewritten as an indented admonition."""
        lines = [re.sub(r"^> ?", "", line) for line in m.group("body").splitlines()]
        first = ALERT_TITLE.match(lines[0])
        title = first.group(1) if first else m.group("kind").capitalize()
        if first:
            lines[0] = lines[0][first.end():]
            lines = lines if lines[0] else lines[1:]
        body = "\n".join(f"    {line}" if line else "" for line in lines).strip("\n")
        return f'!!! {KINDS[m.group("kind")]} "{title}"\n{body}\n'
    return ALERT.sub(box, text)


def check_links(text: str, where: str) -> None:
    """A guide may only use absolute links and pictures (it is read on GitHub and on the site); a relative one stops the build."""
    bad = RELATIVE.findall(text)
    if bad:
        fail(f"{where} uses relative links or pictures {sorted(set(bad))}; use absolute https:// addresses")


def site_links(text: str, pages: dict[tuple[str, str], str]) -> str:
    """Links to another imported guide's file on GitHub -> that guide on the site (`pages` maps (repo, path) to a slug)."""
    def link(m: re.Match) -> str:
        """The site address when the link points at an imported guide, otherwise the link unchanged."""
        slug = pages.get((m.group(1), m.group(2)))
        return f"](../{slug}/index.md{m.group(3) or ''})" if slug else m.group(0)
    return BLOB.sub(link, text)
