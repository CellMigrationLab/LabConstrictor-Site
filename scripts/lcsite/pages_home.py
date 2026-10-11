"""The home page's sections after the hero: the three steps, the comic with its two tiles, the featured apps and the optional plugin section.
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
    return f'<section class="lc-band"><h2 class="lc-title">{esc(site["steps_title"])}</h2><ol class="lc-steps">{items}</ol></section>'


def how_tile(site: dict) -> str:
    """The "How it works" tile, built like the demo tile: a picture, a title, a sentence and a link to the author tour."""
    t = site["how_tile"]
    return (f'<a class="lc-tile" href="how-it-works/"><img class="lc-icon" src="assets/images/logo.png" alt="" width="88" height="88" loading="lazy">'
            f'<span class="lc-tile__body"><strong>{esc(t["title"])}</strong><span>{esc(t["text"])}</span><span class="lc-go">{esc(t["link"])}</span></span></a>')


def intro_band(comic: str, tiles: list[str]) -> str:
    """The comic (smaller, centred) with the two equal tiles directly under it; tiles and the section titles share one left edge."""
    return f'<section class="lc-band lc-band--tight"><div class="lc-intro__comic">{comic}</div><div class="lc-tiles">{"".join(tiles)}</div></section>'


def featured_band(featured: list[str], empty_text: str) -> str:
    """"Featured apps": the given card HTML, or `empty_text` when no listed app is featured, then the link to every app."""
    body = '<ul class="lc-grid">' + "\n".join(featured) + "</ul>" if featured else f"<p>{esc(empty_text)}</p>"
    return f'<section class="lc-band"><h2 class="lc-title">Featured apps</h2>{body}<p class="lc-more"><a class="lc-go" href="apps/">See every app</a></p></section>'


def plugins_band(site: dict, stage: str, pills: str) -> str:
    """The optional-integration section: what a plugin is, its stage (from the plugins' own status) and the programs, with one link to the Ecosystem page."""
    p = site["plugins"]
    return (f'<section class="lc-band lc-band--soft"><h2 class="lc-title">{esc(p["title"])}</h2><div class="lc-prose"><p class="lc-lead-text">{esc(p["text"])}</p>'
            f'<p><span class="lc-badge lc-badge--status">{esc(stage)}</span> {esc(p["note"])}</p>{pills}'
            f'<p class="lc-more"><a class="lc-go" href="ecosystem/">{esc(p["link"])}</a></p></div></section>')
