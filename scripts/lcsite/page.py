"""One generated Markdown page, with links made relative to where it lives."""

import re

import yaml

from .config import DOCS, SITE_URL
from .text import is_external, opens_new_tab

NEW_TAB = 'target="_blank" rel="noopener"'


def new_tab_links(text: str) -> str:
    """Outbound web links (<a href=...>) open in a new tab; internal links,
    fragments and mailto: are left alone, as are links that already set a target."""
    def link(m: re.Match) -> str:
        """The tag with target and rel added when its address leaves the site."""
        tag = m.group(0)
        if "target=" in tag or not opens_new_tab(m.group(1), SITE_URL):
            return tag
        return tag[:-1] + f" {NEW_TAB}>"

    return re.sub(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>', link, text)


class Page:
    """Collects HTML/Markdown chunks and writes docs/<path> with front matter.

    Chunks write links as site paths ("apps/", "assets/x.png"); write() turns
    them into paths relative to this page, so the site works under any path.
    """

    def __init__(self, path: str, **meta: object) -> None:
        """`path` is the file under docs/ ("apps/nucleisky/index.md"); `meta` becomes its front matter.
        A description is made safe for the theme, which prints it inside a quoted HTML attribute unescaped."""
        self.path = path
        if "description" in meta:
            meta["description"] = str(meta["description"]).replace('"', "\u201d")
        self.meta = {k: v for k, v in meta.items() if v not in (None, "", [])}
        self.parts: list[str] = []
        self.depth = path.count("/")

    def u(self, target: str) -> str:
        """Site path -> path relative to this page (external and empty addresses unchanged)."""
        if not target or is_external(target):
            return target
        return "../" * self.depth + target.lstrip("/") if self.depth else (target.lstrip("/") or "./")

    def add(self, *chunks: str) -> None:
        """Append chunks of HTML/Markdown (joined with newlines on write)."""
        self.parts.extend(chunks)

    def fix_links(self, text: str) -> str:
        """Make href/src site paths relative to this page; outbound links open a new tab."""
        def repl(m: re.Match) -> str:
            """The attribute with its site path made relative to this page."""
            attr, url = m.group(1), m.group(2)
            if is_external(url) or url.startswith(("../", "./")):
                return m.group(0)
            return f'{attr}="{self.u(url)}"'

        return new_tab_links(re.sub(r'\b(href|src)="([^"]*)"', repl, text))

    def write(self) -> None:
        """Write docs/<path> (front matter + body)."""
        out = DOCS / self.path
        out.parent.mkdir(parents=True, exist_ok=True)
        front = yaml.safe_dump(self.meta, allow_unicode=True, sort_keys=False, width=10**9).strip()
        body = self.fix_links("\n".join(self.parts))
        out.write_text(f"---\n{front}\n---\n\n{body}\n", encoding="utf-8")
