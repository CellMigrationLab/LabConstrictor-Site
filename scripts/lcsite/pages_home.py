"""The home page's sections after the hero, in the order of the story: the problem (the comic), the solution (the steps of How it works, as cards), the two demo tiles, the optional plugin section, the featured apps.
Wording is in data/site.yaml and data/demo.yaml; the apps shown are the ones the catalogue marks as featured."""

from . import pages_how
from .text import esc



def featured_apps(apps: list[dict]) -> list[dict]:
    """The apps the home page features: marked `featured` in the registry and listed for users (never the ones kept apart under testing)."""
    return [a for a in apps if a["featured"] and a["section"] == "apps"]


def steps_band(site: dict, steps: list[dict]) -> str:
    """"How it works": the five steps of the How it works page as cards (pages_how.step_cards, one source for every page), then a link to
    the full walkthrough."""
    return (f'<section class="lc-band lc-band--soft"><h2 class="lc-title">{esc(site["steps_title"])}</h2>{pages_how.step_cards(steps)}'
            f'<p class="lc-more"><a class="lc-go" href="how-it-works/">{esc(site["steps_link"])}</a></p></section>')


def comic_band(comic: str) -> str:
    """The problem: the comic across the full width of the content, in a band of its own."""
    return f'<section class="lc-band lc-band--comic">{comic}</section>'


def tiles_band(title: str, tiles: list[str]) -> str:
    """The two demo tiles under their heading, next to each other (stacked on a phone), equal in size and look: the installed app and the
    simulated Windows installation, two parts of the same /demo/ page."""
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
