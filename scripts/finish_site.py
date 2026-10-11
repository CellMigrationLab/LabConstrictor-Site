"""Final touches on the built site, for pages whose content comes from Markdown written in other repositories.

    python scripts/finish_site.py

After `zensical build`: every link that leaves the site opens in a new tab with rel="noopener" (the Markdown of the guides
cannot say so itself), and every image in the page content loads lazily. Inside links are never changed. Run before check_design.py.
"""

import re
import sys
from pathlib import Path

from lcsite.page import new_tab_links

SITE = Path(__file__).resolve().parents[1] / "site"
MAIN = re.compile(r"(<main\b.*?</main>)", re.S)
IMG = re.compile(r"<img\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>")   # one img tag; a > inside a quoted value does not end it
QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'")


def lazy_tag(tag: str) -> str:
    """One <img ...> tag with loading="lazy" added before its closing bracket, unless it already has a loading attribute
    (looked for outside quoted values, so alt="loading=eager" does not count)."""
    if re.search(r"\sloading\s*=", QUOTED.sub('""', tag)):
        return tag
    slash = "/" if tag.endswith("/>") else ""
    return tag[: len(tag) - 1 - len(slash)].rstrip() + ' loading="lazy"' + slash + ">"


def lazy_images(html: str) -> str:
    """Add loading="lazy" to the images inside <main> that do not say how they load."""
    def in_main(m: re.Match) -> str:
        """The <main> element with its images made lazy."""
        return IMG.sub(lambda i: lazy_tag(i.group(0)), m.group(1))
    return MAIN.sub(in_main, html)


def finish(html: str) -> str:
    """One page with outside links in a new tab and content images lazy."""
    return lazy_images(new_tab_links(html))


def main() -> int:
    """Rewrite every built page that changes. Returns the exit status."""
    if not SITE.is_dir():
        print("finish_site: run `zensical build` first (no site/)", file=sys.stderr)
        return 2
    changed = 0
    for page in SITE.rglob("*.html"):
        before = page.read_text(encoding="utf-8")
        after = finish(before)
        if after != before:
            page.write_text(after, encoding="utf-8")
            changed += 1
    print(f"finish_site: {changed} pages changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
