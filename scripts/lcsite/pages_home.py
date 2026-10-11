"""The home page's sections after the hero, in the order of the story: the problem (the comic), the solution (three steps), the two tiles, the optional plugin section, the featured apps.
Wording is in data/site.yaml and data/demo.yaml; the apps shown are the ones the catalogue marks as featured."""

from .text import esc

STEP_KEYS = {"title", "text"}


def featured_apps(apps: list[dict]) -> list[dict]:
    """The apps the home page features: marked `featured` in the registry and listed for users (never the ones kept apart under testing)."""
    return [a for a in apps if a["featured"] and a["section"] == "apps"]


def steps_band(site: dict) -> str:
    """"From notebook to app": the three steps of data/site.yaml as a numbered row (the interactive version is the How it works page)."""
    for step in site["steps"]:
        if set(step) != STEP_KEYS:
            raise SystemExit(f"data/site.yaml: a step needs exactly {sorted(STEP_KEYS)}, got {sorted(step)}")
    items = "".join(f'<li><strong>{esc(s["title"])}</strong><span>{esc(s["text"])}</span></li>' for s in site["steps"])
    return f'<section class="lc-band lc-band--soft"><h2 class="lc-title">{esc(site["steps_title"])}</h2><ol class="lc-steps">{items}</ol></section>'


def how_tile(site: dict) -> str:
    """The "How it works" tile, built like the demo tile: a picture, a title, a sentence and a link to the author tour."""
    t = site["how_tile"]
    return (f'<a class="lc-tile" href="how-it-works/"><img class="lc-icon" src="assets/images/logo.png" alt="" width="88" height="88" loading="lazy">'
            f'<span class="lc-tile__body"><strong>{esc(t["title"])}</strong><span>{esc(t["text"])}</span><span class="lc-go">{esc(t["link"])}</span></span></a>')


def comic_band(comic: str) -> str:
    """The problem: the comic across the full width of the content, in a band of its own."""
    return f'<section class="lc-band lc-band--comic">{comic}</section>'


def tiles_band(tiles: list[str]) -> str:
    """The two tiles next to each other (stacked on a phone): the author tour and the installed-app demo, equal in size and look."""
    return f'<section class="lc-band"><div class="lc-tiles">{"".join(tiles)}</div></section>'


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
