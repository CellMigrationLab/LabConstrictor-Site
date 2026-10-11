"""Imported guides are written in other repositories, so the built page must not carry code that runs: scripts, frames, event handlers and script addresses."""

import re
from html.parser import HTMLParser

FORBIDDEN_TAGS = {"script", "iframe", "frame", "frameset", "object", "embed", "applet", "base", "meta", "link", "style", "form"}
ADDRESS_ATTRS = {"href", "src", "srcset", "action", "formaction", "poster", "data", "background", "xlink:href"}
ACTIVE_SCHEME = re.compile(r"^(javascript|vbscript|data):")


def scheme_of(value: str) -> str:
    """An address as a browser reads it: control characters and spaces removed, lower case (so `java\tscript:` is `javascript:`)."""
    return re.sub(r"[\x00-\x20]", "", value).lower()


def addresses(name: str, value: str) -> list[str]:
    """The addresses inside one attribute value: the candidates of a srcset, or the value itself."""
    if name == "srcset":
        return [part.strip().split(" ")[0] for part in value.split(",") if part.strip()]
    return [value]


class Scanner(HTMLParser):
    """Collects what is not allowed inside the article of a page (the part written by the guide's author)."""

    def __init__(self) -> None:
        """Start outside the article with no findings."""
        super().__init__()
        self.depth = 0
        self.found: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Track the article; inside it, record forbidden tags, event attributes and script addresses."""
        a = dict(attrs)
        if tag == "article" and "md-content__inner" in (a.get("class") or "").split():
            self.depth += 1
            return
        if not self.depth:
            return
        if tag in FORBIDDEN_TAGS:
            self.found.append(f"<{tag}> element")
        for name, value in attrs:
            if name.startswith("on"):
                self.found.append(f"event attribute {name}")
            if name in ADDRESS_ATTRS and value and any(ACTIVE_SCHEME.match(scheme_of(u)) for u in addresses(name, value)):
                self.found.append(f"script address in {name}: {value[:40]!r}")

    def handle_endtag(self, tag: str) -> None:
        """Leave the article when it ends."""
        if tag == "article" and self.depth:
            self.depth -= 1


def problems(html: str) -> list[str]:
    """What the article of one page contains that must not be there (an empty list for a clean page)."""
    scanner = Scanner()
    scanner.feed(html)
    return scanner.found
