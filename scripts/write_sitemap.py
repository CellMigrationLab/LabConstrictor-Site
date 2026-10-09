"""Write site/sitemap.xml and site/robots.txt after `zensical build`, and copy the schemas.

    python scripts/write_sitemap.py

(Adapted from the lab website.) Zensical's own sitemap only lists pages in the menu; this lists
every real page in site/, leaving out redirect pages and the 404 page, and points robots.txt at it.
Addresses use `site_url` from mkdocs.yml. The JSON schemas are published at /schema/ so that
editors can validate manifests against them.
"""

import re
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from lcsite.config import ROOT, SCHEMA, SITE_URL, fail

SITE = ROOT / "site"
REDIRECT = re.compile(r'<meta[^>]+http-equiv="refresh"', re.I)


def page_paths(site: Path) -> list[str]:
    """Site-relative directory addresses ("", "apps/", ...) of every real page."""
    paths = []
    for index in sorted(site.rglob("index.html")):
        head = index.read_text(encoding="utf-8", errors="ignore")[:2000]
        if head.lstrip().startswith("<?xml") or REDIRECT.search(head):
            continue
        rel = index.parent.relative_to(site).as_posix()
        paths.append("" if rel == "." else f"{rel}/")
    return paths


def sitemap(base: str, paths: list[str]) -> str:
    """sitemap.xml listing base + each path."""
    urls = "".join(f"<url><loc>{escape(base + p)}</loc></url>\n" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')


def robots(base: str) -> str:
    """robots.txt: everything may be crawled; says where the sitemap is."""
    return f"User-agent: *\nAllow: /\n\nSitemap: {base}sitemap.xml\n"


def main() -> None:
    """Replace Zensical's sitemap.xml, write robots.txt, publish the schemas."""
    if not (SITE / "index.html").is_file():
        fail("run `zensical build` first (no site/index.html)")
    paths = page_paths(SITE)
    (SITE / "sitemap.xml").write_text(sitemap(SITE_URL, paths), encoding="utf-8")
    (SITE / "robots.txt").write_text(robots(SITE_URL), encoding="utf-8")
    shutil.copytree(SCHEMA, SITE / "schema", dirs_exist_ok=True)
    print(f"sitemap.xml: {len(paths)} pages")


if __name__ == "__main__":
    main()
