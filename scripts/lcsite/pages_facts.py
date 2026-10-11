"""The facts an app's manifest gives about itself on its page: what it works with, what it produces, its limits and its stage.
A recommended fact the author left out is said to be missing (never guessed)."""

from .cards import badge
from .config import DOCS, SCIENTIFIC_KINDS
from .images import pixel_size
from .text import esc
from .validate import optional_list

STATUS_CHIPS = ("Experimental", "Deprecated")   # "Available" is the normal case and needs no chip


def bullet(items: list[str]) -> str:
    """A plain-text list: every item escaped, none rendered as HTML or Markdown."""
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def works_with(app: dict) -> str:
    """"Works with" and "Produces" lists from the manifest's inputs and outputs. When a scientific app (analysis, segmentation,
    simulation) gives neither, one muted line says so; other kinds and testing apps show nothing."""
    m = app["manifest"]
    blocks = [f"<div><h2>{title}</h2><p class=\"lc-small\">The authors say it {verb}:</p>{bullet(m[key])}</div>"
              for key, title, verb in (("inputs", "Works with", "works with"), ("outputs", "Produces", "produces")) if key in m]
    if blocks:
        return '<section class="lc-works">' + "".join(blocks) + "</section>"
    if m["kind"] in SCIENTIFIC_KINDS and app["section"] != "testing":
        return '<p class="lc-small lc-works__none">Input and output formats: not stated by the author.</p>'
    return ""


def limitations(app: dict) -> str:
    """The "Limitations" section, only when the manifest lists some (nobody can be required to list limits)."""
    items = optional_list(app["manifest"], "limitations")
    return f'<h2 id="limitations">Limitations</h2><p class="lc-small">The authors say:</p>{bullet(items)}' if items else ""


def status_row(app: dict) -> str:
    """The Details value for development status: what the authors state, or "Not stated"."""
    m = app["manifest"]
    return esc(m["status"]) if "status" in m else "Not stated"


def status_chip(app: dict) -> str:
    """A grey chip in the header for an app the authors call Experimental or Deprecated; nothing otherwise."""
    m = app["manifest"]
    return badge(m["status"], "status") if "status" in m and m["status"] in STATUS_CHIPS else ""


def screenshot(app: dict, number: int, shot: dict) -> str:
    """One screenshot as a figure: the caption is also its alt text, and its size is written so the page does not shift while it loads."""
    width, height = pixel_size(DOCS / "assets" / "shots" / f"{app['slug']}-{number}.jpg")
    return (f'<figure class="lc-shot"><img class="lc-shot__img" src="assets/shots/{app["slug"]}-{number}.jpg" alt="{esc(shot["caption"])}" '
            f'width="{width}" height="{height}" loading="lazy"><figcaption>{esc(shot["caption"])}</figcaption></figure>')
