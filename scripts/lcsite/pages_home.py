"""The home page's sections after the hero, in the order of the story: the problem (the comic), the solution (the steps of How it works), the two tiles, the optional plugin section, the featured apps.
Wording is in data/site.yaml and data/demo.yaml; the apps shown are the ones the catalogue marks as featured."""

from .text import esc



def featured_apps(apps: list[dict]) -> list[dict]:
    """The apps the home page features: marked `featured` in the registry and listed for users (never the ones kept apart under testing)."""
    return [a for a in apps if a["featured"] and a["section"] == "apps"]


def steps_band(title: str, steps: list[dict]) -> str:
    """"From notebook to app": the steps of How it works (data/how-it-works.yaml, already checked), each with its title, linked to its step on that
    page, and its one-line summary; the same steps in the same order, written once."""
    items = "".join(f'<li><strong><a href="how-it-works/#{esc(s["id"])}">{esc(s["title"])}</a></strong><span>{esc(s["summary"])}</span></li>' for s in steps)
    return f'<section class="lc-band lc-band--soft"><h2 class="lc-title">{esc(title)}</h2><ol class="lc-steps">{items}</ol></section>'


def how_tile(site: dict) -> str:
    """The "How it works" tile, built like the demo tile: a picture, a title, a sentence and a link to the author tour."""
    t = site["how_tile"]
    return (f'<a class="lc-tile" href="how-it-works/"><img class="lc-icon" src="assets/images/logo.png" alt="" width="88" height="88" loading="lazy">'
            f'<div class="lc-tile__body"><h3 class="lc-tile__title">{esc(t["title"])}</h3><span>{esc(t["text"])}</span><span class="lc-go">{esc(t["link"])}</span></div></a>')


def comic_band(comic: str) -> str:
    """The problem: the comic across the full width of the content, in a band of its own."""
    return f'<section class="lc-band lc-band--comic">{comic}</section>'


def tiles_band(title: str, tiles: list[str]) -> str:
    """The two tiles under their heading, next to each other (stacked on a phone): the author tour and the installed-app demo, equal in size and look."""
    return f'<section class="lc-band"><h2 class="lc-title">{esc(title)}</h2><div class="lc-tiles">{"".join(tiles)}</div></section>'


def featured_band(featured: list[str], empty_text: str) -> str:
    """"Featured apps": the given card HTML, or `empty_text` when no listed app is featured, then the link to every app."""
    body = '<ul class="lc-grid">' + "\n".join(featured) + "</ul>" if featured else f"<p>{esc(empty_text)}</p>"
    return f'<section class="lc-band"><h2 class="lc-title">Featured apps</h2>{body}<p class="lc-more"><a class="lc-go" href="apps/">See every app</a></p></section>'


def plugins_band(site: dict, pills: str) -> str:
    """The optional-integration section: one full-width panel, built like the tiles around it, with a sentence, a row of the plugins' stage
    (from their own status) and the programs, and one link to the Ecosystem page."""
    p = site["plugins"]
    return (f'<section class="lc-band lc-band--soft"><h2 class="lc-title">{esc(p["title"])}</h2><div class="lc-panel">'
            f'<p class="lc-lead-text">{esc(p["text"])}</p>{pills}'
            f'<a class="lc-go" href="ecosystem/">{esc(p["link"])}</a></div></section>')
