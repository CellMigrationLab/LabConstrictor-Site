"""Check the built site against the design rules of DESIGN.md (run after `zensical build`, next to check_site.py).

    python scripts/check_design.py

Every page is read as HTML and checked for: its metadata (one h1, a unique description, canonical address, social tags, language),
heading order, link behaviour (outside links open in a new tab with rel noopener, inside links never do, no empty or generic link text),
buttons (a <button> only for an in-page action, a button-styled link only where a call to action belongs), images (alt text, and
the few places where it may be empty), nested links, and GitHub repository links (always the GitHub pill). Exit status 1 lists every problem.
"""

import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from lcsite.config import SITE_URL

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
GENERIC_LINK_TEXT = {"here", "click here", "link", "more", "read more", "this", "this link"}
DECORATIVE_IMAGE_PARENTS = ("lc-brand", "lc-footer__brand", "lc-icon", "lc-logo", "lc-shot__img", "lc-view__layer")   # lc-shot__img: its figcaption says what it shows; lc-view__layer: the picture stack carries one aria-label
DESCRIPTION_LENGTH = (20, 200)
# Known breaks of a rule in imported content we cannot change from here yet, each with the reason. A new break is never added silently.
KNOWN_EXCEPTIONS = {
    ("guides/template-synchronization/index.html", "this link"):
        "template_synchronization.md is tied to a migration resource of the template, so its wording changes with the next migration",
}
REPO_ROOT = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")


def attr(values: dict[str, str], key: str) -> str:
    """A value of a dict of strings, or an empty string when the key is not there (HTML attributes and meta tags are optional)."""
    return values[key] if key in values else ""


class Facts(HTMLParser):
    """What the rules need to know about one page."""

    def __init__(self) -> None:
        """Start empty."""
        super().__init__()
        self.headings: list[int] = []
        self.meta: dict[str, str] = {}
        self.title = ""
        self.lang = ""
        self.links: list[dict] = []
        self.images: list[dict] = []
        self.buttons: list[dict] = []
        self.nested_links = 0
        self.demo_root = False
        self._open_link: dict | None = None
        self._in_title = False
        self._in_main = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Collect the headings, meta tags, links, images and buttons."""
        a = {k: (v or "") for k, v in attrs}
        classes = attr(a, "class").split()
        self.demo_root = self.demo_root or "data-demo" in a
        if tag == "html":
            self.lang = attr(a, "lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta" and (a.get("name") or a.get("property")):
            self.meta[a.get("name") or a["property"]] = attr(a, "content")
        elif tag == "link" and a.get("rel") == "canonical":
            self.meta["canonical"] = attr(a, "href")
        elif tag == "main":
            self._in_main = True
        elif re.fullmatch(r"h[1-6]", tag) and self._in_main:
            self.headings.append(int(tag[1]))
        elif tag == "a" and a.get("href") is not None:
            self.nested_links += self._open_link is not None
            self._open_link = {"href": a["href"], "target": attr(a, "target"), "rel": attr(a, "rel"), "classes": classes, "text": "", "main": self._in_main,
                              "hidden": a.get("aria-hidden") == "true", "img_alt": False}
            self.links.append(self._open_link)
        elif tag == "img":
            self.images.append({"alt": a.get("alt"), "src": attr(a, "src"), "main": self._in_main, "classes": classes})
            if self._open_link is not None and a.get("alt"):
                self._open_link["img_alt"] = True
        elif tag == "button" or (tag == "a" and "lc-btn" in classes):
            demo = "act" if "data-demo-act" in a else "sim" if "data-demo-sim" in a else ""
            self.buttons.append({"tag": tag, "classes": classes, "copy": "data-copy" in a or "data-lc-reset" in a, "main": self._in_main,
                                 "demo": demo, "type": attr(a, "type")})

    def handle_endtag(self, tag: str) -> None:
        """Close the title, the main area and the current link."""
        self._in_title = self._in_title and tag != "title"
        self._in_main = self._in_main and tag != "main"
        if tag == "a":
            self._open_link = None

    def handle_data(self, data: str) -> None:
        """Collect the title and the text of the current link."""
        if self._in_title:
            self.title += data
        if self._open_link is not None:
            self._open_link["text"] += data


def read(page: Path) -> Facts:
    """The facts of one built page."""
    facts = Facts()
    facts.feed(page.read_text(encoding="utf-8"))
    return facts


def metadata_problems(name: str, f: Facts) -> list[str]:
    """One line per metadata rule a page breaks (not for redirect pages, which have no menu)."""
    found = []
    if f.headings.count(1) != 1:
        found.append(f"{name}: {f.headings.count(1)} h1 elements (exactly one)")
    if f.lang != "en":
        found.append(f"{name}: <html lang> is {f.lang!r}")
    for key in ("description", "canonical", "og:title", "og:description"):
        if not f.meta.get(key):
            found.append(f"{name}: no {key}")
    desc = attr(f.meta, "description")
    if desc and not DESCRIPTION_LENGTH[0] <= len(desc) <= DESCRIPTION_LENGTH[1]:
        found.append(f"{name}: description is {len(desc)} characters (allowed {DESCRIPTION_LENGTH[0]}-{DESCRIPTION_LENGTH[1]})")
    return found


def heading_problems(name: str, f: Facts) -> list[str]:
    """A heading may go one level deeper than the one before it, never two."""
    return [f"{name}: h{b} follows h{a} (a level is skipped)" for a, b in zip(f.headings, f.headings[1:]) if b > a + 1]


def link_problems(name: str, f: Facts) -> list[str]:
    """Outside links: new tab with rel noopener. Inside links: same tab. Link text: present and not generic. GitHub repository links: the pill."""
    found = []
    for link in f.links:
        href, text = link["href"], " ".join(link["text"].split())
        outside = href.startswith(("http://", "https://")) and not href.startswith(SITE_URL)
        if outside and (link["target"] != "_blank" or "noopener" not in link["rel"]):
            found.append(f"{name}: outside link {href} does not open in a new tab with rel=noopener")
        if not outside and link["target"] == "_blank":
            found.append(f"{name}: inside link {href} opens in a new tab")
        if link["main"] and not text and not link["img_alt"] and not link["hidden"]:
            found.append(f"{name}: link {href} has no text")
        if text.lower() in GENERIC_LINK_TEXT and (name, text.lower()) not in KNOWN_EXCEPTIONS:
            found.append(f"{name}: link text {text!r} does not say where it goes ({href})")
        if link["main"] and REPO_ROOT.match(href) and "lc-gh" not in link["classes"] and "lc-card__main" not in link["classes"] and not link["img_alt"]:
            found.append(f"{name}: GitHub repository link {href} is not a GitHub pill")
    return found + ([f"{name}: {f.nested_links} links inside links"] if f.nested_links else [])


def button_problems(name: str, f: Facts) -> list[str]:
    """A <button> only where nothing is navigated (copy); a filled button only inside the page's content, never in a card."""
    found = []
    for b in f.buttons:
        if "md-top" in b["classes"]:
            continue   # the theme's own "back to top" button
        if b["demo"] and not f.demo_root:
            found.append(f"{name}: a demo control outside a page with a data-demo root")
        if b["demo"] and b["tag"] == "button" and b["type"] != "button":
            found.append(f"{name}: a demo <button> without type=button")
        if b["tag"] == "button" and b["main"] and not b["copy"] and not b["demo"]:
            found.append(f"{name}: a <button> in the content that is neither a copy nor a clear-filters button nor a demo control")
        if b["tag"] == "button" and b["main"] and "lc-btn" not in b["classes"] and b["demo"] != "sim":
            found.append(f"{name}: a <button> in the content is not styled as a button")
    return found


def image_problems(name: str, f: Facts) -> list[str]:
    """Every image has an alt attribute; an empty one only for a logo or icon whose name is written next to it."""
    found = []
    for img in f.images:
        if img["alt"] is None:
            found.append(f"{name}: image {img['src']} has no alt attribute")
        elif img["alt"] == "" and not any(c in DECORATIVE_IMAGE_PARENTS for c in img["classes"]) and img["main"] and "lc-icon" not in img["classes"]:
            found.append(f"{name}: image {img['src']} has an empty alt but is not a logo or icon")
    return found


def duplicate_descriptions(pages: dict[str, Facts]) -> list[str]:
    """Two pages may not share a meta description."""
    counts = Counter(attr(f.meta, "description") for f in pages.values() if f.meta.get("description"))
    return [f"description used by {n} pages: {d[:70]!r}" for d, n in counts.items() if n > 1]


def all_problems(pages: dict[str, Facts]) -> list[str]:
    """Every rule, over every page."""
    found = duplicate_descriptions(pages)
    for name, f in pages.items():
        found += metadata_problems(name, f) + heading_problems(name, f) + link_problems(name, f) + button_problems(name, f) + image_problems(name, f)
    return found


def main() -> int:
    """Read every built page except the 404 and redirect pages, print the problems, return the exit status."""
    if not SITE.is_dir():
        print("check_design: run `zensical build` first (no site/)", file=sys.stderr)
        return 2
    pages = {}
    for page in sorted(SITE.rglob("*.html")):
        facts = read(page)
        if page.name != "404.html" and "refresh" not in page.read_text(encoding="utf-8")[:1500]:
            pages[str(page.relative_to(SITE))] = facts
    problems = all_problems(pages)
    for problem in problems:
        print(f"DESIGN {problem}", file=sys.stderr)
    print(f"check_design: {len(pages)} pages, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
