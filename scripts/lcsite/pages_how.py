"""The interactive page /how-it-works/ (the author's journey): four stages first, then optional "Go further" parts, from data/how-it-works.yaml.
Each chapter has a small panel, content/how/<id>.html; a chapter keeps its address (#portable, #code, ...) wherever it sits on the page."""

import shutil

from . import demo_media
from .config import CONTENT, DATA, DOCS, REPO, fail, load_yaml
from .page import Page
from .text import esc

SOURCE = CONTENT / "how"
OUT = DOCS / "assets" / "how"
TOP_KEYS = {"title", "lead", "notice", "stages_title", "stages", "handoff", "further_title", "further_text", "further", "chapters"}
STAGE_KEYS = {"id", "title", "outcome", "text", "chapters"}
GROUP_KEYS = {"title", "chapters"}
HANDOFF_KEYS = {"text", "link", "href"}
CHAPTER_KEYS = {"id", "title", "text", "guide", "guide_label", "static"}
SHARED = "demo-dom.js"   # the strict DOM helpers, shared with the demo
SCRIPTS = (f"assets/demo/{SHARED}", "assets/how/how.js")


def check_keys(where: str, item: dict, keys: set[str]) -> None:
    """Stop the build, naming the data file and the item, unless `item` has exactly `keys`."""
    if not isinstance(item, dict) or set(item) != keys:
        fail(f"data/how-it-works.yaml: {where} needs exactly {sorted(keys)}, got {sorted(item) if isinstance(item, dict) else item!r}")


def label(item: object, key: str) -> str:
    """How an item is named in an error message: its `key` when it has one, otherwise a question mark."""
    return str(item[key]) if isinstance(item, dict) and key in item else "?"


def check_placement(data: dict) -> None:
    """Every chapter is shown exactly once, in a stage or in "Go further"; a name that is not a chapter is an error."""
    ids = [c["id"] for c in data["chapters"]]
    placed = [c for s in data["stages"] for c in s["chapters"]] + [c for g in data["further"] for c in g["chapters"]]
    unknown = sorted(set(placed) - set(ids))
    twice = sorted({c for c in placed if placed.count(c) > 1})
    unplaced = sorted(set(ids) - set(placed))
    if unknown or twice or unplaced:
        fail(f"data/how-it-works.yaml: unknown chapters {unknown}, chapters placed twice {twice}, chapters not placed {unplaced}")


def load() -> dict:
    """data/how-it-works.yaml, checked: the exact keys everywhere, unique chapter ids, a plain summary for every chapter, and every chapter placed once."""
    data = load_yaml(DATA / "how-it-works.yaml")
    check_keys("the top level", data, TOP_KEYS)
    check_keys("handoff", data["handoff"], HANDOFF_KEYS)
    seen: set[str] = set()
    for chapter in data["chapters"]:
        check_keys(f"chapter {label(chapter, 'id')}", chapter, CHAPTER_KEYS)
        if chapter["id"] in seen or not chapter["static"]:
            fail(f"data/how-it-works.yaml: chapter {chapter['id']} is listed twice or has no static summary")
        seen.add(chapter["id"])
    for stage in data["stages"]:
        check_keys(f"stage {label(stage, 'id')}", stage, STAGE_KEYS)
    for group in data["further"]:
        check_keys(f"group {label(group, 'title')}", group, GROUP_KEYS)
    check_placement(data)
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
    """Copy the page's script and style into docs/assets/how/ (generated), and the one helper script it shares with the demo (demo-dom.js)
    into docs/assets/demo/. Nothing else of the demo is copied, so this page never depends on the demo's images or numbers."""
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("how.js", "how.css"):
        shutil.copy2(SOURCE / name, OUT / name)
    demo_media.OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(demo_media.SOURCE / SHARED, demo_media.OUT / SHARED)


def chapter_body(chapter: dict) -> str:
    """The inside of a chapter: its text, the panel (live with JavaScript), the plain summary (without it) and the link to the full guide."""
    static = "".join(f"<li>{esc(s)}</li>" for s in chapter["static"])
    return (f'<p>{esc(chapter["text"])}</p>{read_panel(chapter["id"])}<ul class="how__static">{static}</ul>'
            f'<p><a class="lc-go" href="{esc(chapter["guide"])}">{esc(chapter["guide_label"])}</a></p>')


def stage_chapter(chapter: dict) -> str:
    """A chapter inside a stage: an h3 and its body, always open."""
    return f'<section class="how__chapter" id="{esc(chapter["id"])}"><h3>{esc(chapter["title"])}</h3>{chapter_body(chapter)}</section>'


def further_chapter(chapter: dict) -> str:
    """A chapter under "Go further": a native disclosure (closed), so the page stays short; how.js opens it when its address is followed."""
    return (f'<details class="how__more" id="{esc(chapter["id"])}"><summary>{esc(chapter["title"])}</summary>'
            f'<div class="how__more-body">{chapter_body(chapter)}</div></details>')


def stage_tiles(data: dict) -> str:
    """The four stage tiles: number, title and outcome, each a link to its stage on this page."""
    tiles = "".join(f'<li><a class="how__tile" href="#{esc(s["id"])}"><span class="how__num">{i}</span><strong>{esc(s["title"])}</strong>'
                    f'<span>{esc(s["outcome"])}</span></a></li>' for i, s in enumerate(data["stages"], 1))
    return f'<nav aria-label="{esc(data["stages_title"])}"><ol class="how__tiles">{tiles}</ol></nav>'


def stages_html(data: dict) -> str:
    """Every stage as a section with its short text and its chapters, then the hand-over to the demo."""
    by_id = {c["id"]: c for c in data["chapters"]}
    out = []
    for i, stage in enumerate(data["stages"], 1):
        chapters = "".join(stage_chapter(by_id[c]) for c in stage["chapters"])
        out.append(f'<section class="how__stage" id="{esc(stage["id"])}"><h2><span class="how__num">{i}</span> {esc(stage["title"])}</h2><p class="how__lead">{esc(stage["text"])}</p>{chapters}</section>')
    h = data["handoff"]
    out.append(f'<aside class="how__handoff"><p>{esc(h["text"])}</p><a class="lc-btn lc-btn--primary" href="{esc(h["href"])}">{esc(h["link"])}</a></aside>')
    return "".join(out)


def further_html(data: dict) -> str:
    """The "Go further" section: its groups, each with its chapters as closed disclosures."""
    by_id = {c["id"]: c for c in data["chapters"]}
    groups = "".join(f'<h3>{esc(g["title"])}</h3>{"".join(further_chapter(by_id[c]) for c in g["chapters"])}' for g in data["further"])
    return f'<section class="how__further" id="further"><h2>{esc(data["further_title"])}</h2><p>{esc(data["further_text"])}</p>{groups}</section>'


def page_how() -> None:
    """how-it-works/index.md: the introduction, the four stage tiles, the stages, the hand-over to the demo and "Go further"."""
    data = load()
    copy_assets()
    p = Page("how-it-works/index.md", title=data["title"], description=data["lead"], layout="wide", menu="how-it-works/",
             page_css=["assets/how/how.css"], page_js=list(SCRIPTS), edit_url=f"{REPO}/edit/main/data/how-it-works.yaml")
    p.add(f'<section class="lc-pagehead"><h1>{esc(data["title"])}</h1><p class="lc-lead">{esc(data["lead"])}</p></section>',
          f'<p class="lc-demo__notice" role="note"><strong>Interactive illustration.</strong> {esc(data["notice"].removeprefix("Interactive illustration with example files. "))}</p>',
          stage_tiles(data), stages_html(data), further_html(data))
    p.write()
