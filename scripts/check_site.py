"""Check the built site (site/) before it is published.

    python scripts/check_site.py

Fails (exit status 1) and lists every problem when:
  - a link between pages of the site points to a page, file or anchor that does not exist,
  - text written by an app's author appears unescaped in a page (a sign of HTML injection),
  - an "edit this page" link points at a generated file instead of its source,
  - a file that must exist is missing (sitemap, robots.txt, llms.txt, the schemas).
Run it after `zensical build` and `write_sitemap.py`.
"""

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from lcsite.config import ROOT, SNAPSHOT, load_json

SITE = ROOT / "site"
REQUIRED = ("index.html", "sitemap.xml", "robots.txt", "llms.txt", "schema/labconstrictor-app.schema.json", "404.html")
UNSAFE = re.compile(r'[<>"]')


class PageParts(HTMLParser):
    """Collects the links and the element ids of one HTML page."""

    def __init__(self) -> None:
        """Start with no links and no ids."""
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Remember hrefs, srcs and ids."""
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.links.append(value)
            if name == "id" and value:
                self.ids.add(value)


def parse(page: Path) -> PageParts:
    """The links and ids of an HTML file."""
    parts = PageParts()
    parts.feed(page.read_text(encoding="utf-8"))
    return parts


def target_file(page: Path, address: str) -> Path | None:
    """The file in site/ that a relative link from `page` points to (a folder means its index.html);
    None for external links, mailto:, and fragments within the page."""
    link = urlsplit(address)
    if link.scheme or link.netloc or not link.path:
        return None   # external, or a fragment within the page
    target = (page.parent / unquote(link.path)).resolve()
    return target / "index.html" if target.is_dir() else target


def one_link_problems(page: Path, address: str, pages: dict[Path, PageParts]) -> list[str]:
    """The problems of one internal link: its file is missing, or its #anchor is not on the target page."""
    target = target_file(page, address) or page
    where = f"{page.relative_to(SITE)}: {address}"
    if not target.exists():
        return [f"{where} (no such file)"]
    fragment = urlsplit(address).fragment
    if fragment and target in pages and fragment not in pages[target].ids and fragment != "__skip":
        return [f"{where} (no such anchor)"]
    return []


def link_problems(pages: dict[Path, PageParts]) -> list[str]:
    """One line per internal link whose file or anchor does not exist."""
    problems = []
    for page, parts in pages.items():
        for address in parts.links:
            if urlsplit(address).scheme or urlsplit(address).netloc:
                continue   # external links are not checked here
            problems += one_link_problems(page, address, pages)
    return problems


def author_strings(snapshot: dict) -> list[tuple[str, str]]:
    """(app page, text) for every piece of manifest text that contains < > or a quote."""
    found = []
    for app in snapshot["apps"]:
        texts = json.dumps(app["manifest"], ensure_ascii=False)
        for value in re.findall(r'"((?:[^"\\]|\\.)*)"', texts):
            decoded = json.loads(f'"{value}"')
            if UNSAFE.search(decoded):
                found.append((f"apps/{app['slug']}/index.html", decoded))
    return found


def escaping_problems(snapshot: dict) -> list[str]:
    """One line per piece of manifest text that appears raw in its app page."""
    problems = []
    for page, text in author_strings(snapshot):
        if text in (SITE / page).read_text(encoding="utf-8"):
            problems.append(f"{page}: author text appears unescaped: {text[:60]!r}")
    return problems


GENERATED_EDIT = re.compile(r"LabConstrictor-Site/edit/[^/]+/docs/")


def edit_link_problems(pages: dict[Path, PageParts]) -> list[str]:
    """One line per "edit this page" link that points into the generated docs/ folder (edits there are lost on the next build)."""
    return [f"{page.relative_to(SITE)}: edit link {a} points into generated files"
            for page, parts in pages.items() for a in parts.links if GENERATED_EDIT.search(a)]


def missing_files() -> list[str]:
    """One line per required file that is missing from site/."""
    return [f"missing {name}" for name in REQUIRED if not (SITE / name).is_file()]


def main() -> int:
    """Run every check; print the problems; return the exit status."""
    if not SITE.is_dir():
        print("check_site: run `zensical build` first (no site/)", file=sys.stderr)
        return 2
    # The 404 page uses absolute addresses on purpose (it is served from any depth), so it is not link-checked.
    pages = {p.resolve(): parse(p) for p in sorted(SITE.rglob("*.html")) if p.name != "404.html"}
    problems = missing_files() + link_problems(pages) + edit_link_problems(pages) + escaping_problems(load_json(SNAPSHOT))
    for problem in problems:
        print(f"PROBLEM {problem}", file=sys.stderr)
    print(f"check_site: {len(pages)} pages, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
