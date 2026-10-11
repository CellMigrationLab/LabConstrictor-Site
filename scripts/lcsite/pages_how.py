"""The interactive page /how-it-works/: chapters from data/how-it-works.yaml, each with a small panel from content/how/<id>.html."""

import shutil

from . import demo_media
from .config import CONTENT, DATA, DOCS, REPO, fail, load_yaml
from .page import Page
from .text import esc

SOURCE = CONTENT / "how"
OUT = DOCS / "assets" / "how"
TOP_KEYS = {"title", "lead", "notice", "chapters"}
CHAPTER_KEYS = {"id", "title", "text", "guide", "guide_label", "static"}
SCRIPTS = ("assets/demo/demo-dom.js", "assets/how/how.js")


def load() -> dict:
    """data/how-it-works.yaml, checked: the exact keys, unique chapter ids and a non-empty static summary for every chapter."""
    data = load_yaml(DATA / "how-it-works.yaml")
    if set(data) != TOP_KEYS:
        fail(f"data/how-it-works.yaml: the top level needs exactly {sorted(TOP_KEYS)}, got {sorted(data)}")
    seen: set[str] = set()
    for chapter in data["chapters"]:
        if set(chapter) != CHAPTER_KEYS:
            fail(f"data/how-it-works.yaml: a chapter needs exactly {sorted(CHAPTER_KEYS)}, got {sorted(chapter)}")
        if chapter["id"] in seen or not chapter["static"]:
            fail(f"data/how-it-works.yaml: chapter {chapter['id']} is listed twice or has no static summary")
        seen.add(chapter["id"])
    return data


def read_panel(chapter_id: str) -> str:
    """content/how/<id>.html: one element with no blank line (Markdown would cut it); stops the build otherwise."""
    path = SOURCE / f"{chapter_id}.html"
    if not path.is_file():
        fail(f"{path} is missing (chapter {chapter_id} of data/how-it-works.yaml)")
    text = path.read_text(encoding="utf-8").strip()
    if "\n\n" in text:
        fail(f"{path} has a blank line; Markdown would cut the panel in pieces")
    return text


def copy_assets() -> None:
    """Copy the page's script and style into docs/assets/how/ (generated); the shared helper script comes from the demo."""
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("how.js", "how.css"):
        shutil.copy2(SOURCE / name, OUT / name)
    demo_media.copy_assets()


def chapter_html(number: int, chapter: dict) -> str:
    """One chapter: heading, text, the panel (live with JavaScript), the plain summary (without it) and the link to the full guide."""
    static = "".join(f"<li>{esc(s)}</li>" for s in chapter["static"])
    return (f'<section class="how__chapter" id="{esc(chapter["id"])}"><h2>{number}. {esc(chapter["title"])}</h2><p>{esc(chapter["text"])}</p>'
            f'{read_panel(chapter["id"])}<ul class="how__static">{static}</ul>'
            f'<p><a class="lc-go" href="{esc(chapter["guide"])}">{esc(chapter["guide_label"])}</a></p></section>')


def page_how() -> None:
    """how-it-works/index.md: the introduction, the chapter list and every chapter."""
    data = load()
    copy_assets()
    p = Page("how-it-works/index.md", title=data["title"], description=data["lead"], layout="wide", menu="how-it-works/",
             page_css=["assets/how/how.css"], page_js=list(SCRIPTS), edit_url=f"{REPO}/edit/main/data/how-it-works.yaml")
    rail = "".join(f'<li><a href="#{esc(c["id"])}">{esc(c["title"])}</a></li>' for c in data["chapters"])
    p.add(f'<section class="lc-pagehead"><h1>{esc(data["title"])}</h1><p class="lc-lead">{esc(data["lead"])}</p></section>',
          f'<p class="lc-demo__notice" role="note"><strong>Interactive illustration.</strong> {esc(data["notice"].removeprefix("Interactive illustration with example files. "))}</p>',
          f'<nav aria-label="Chapters"><ol class="how__rail">{rail}</ol></nav>')
    for i, chapter in enumerate(data["chapters"], 1):
        p.add(chapter_html(i, chapter))
    p.write()
