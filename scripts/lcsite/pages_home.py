"""The home page's own sections: the comic with its two side tiles, and the "Packaged once, easy to install" tiles. Wording comes from the apps and data files."""

from . import catalogue_text
from .text import esc


def join_and(items: list[str]) -> str:
    """["a"] -> "a"; ["a", "b"] -> "a and b"; ["a", "b", "c"] -> "a, b and c"."""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def how_tile(steps: list[dict]) -> str:
    """The "How it works" tile: the titles of data/site.yaml `steps` as one sentence, linked to the How it works page."""
    titles = [s["title"] for s in steps]
    sentence = ", ".join([titles[0]] + [t[0].lower() + t[1:] for t in titles[1:]]) + "."
    return (f'<a class="lc-tile" href="how-it-works/"><span class="lc-tile__body"><strong>How it works</strong>'
            f'<span>{esc(sentence)}</span><span class="lc-go">See it step by step</span></span></a>')


def intro_row(comic: str, side: list[str]) -> str:
    """The comic on the left and the tiles on its right (stacked under it on a phone)."""
    return f'<section class="lc-intro"><div class="lc-intro__in"><div class="lc-intro__comic">{comic}</div><div class="lc-intro__side">{"".join(side)}</div></div></section>'


def fact(title: str, text: str, href: str, link: str, extra: str = "") -> str:
    """One tile of the "Packaged once" row: title, a sentence, optional extra HTML and a link."""
    return f'<div class="lc-fact"><h3>{esc(title)}</h3><p>{esc(text)}</p>{extra}<a class="lc-go" href="{esc(href)}">{esc(link)}</a></div>'


def install_fact(apps: list[dict]) -> str:
    """The installers tile, with the systems that some app really has an installer for ("" when no app has an installer)."""
    users = catalogue_text.listed(apps)
    if "installer" not in catalogue_text.ways(users):
        return ""
    systems = catalogue_text.systems(users)
    where = f" for {join_and(systems)}" if systems else ""
    return fact("Install in a few clicks", f"Desktop installers{where}. No Python or pip needed.", "guides/install/", "How to install")


def notebook_fact(apps: list[dict]) -> str:
    """The Colab and pip tile, naming only the ways that some app really offers ("" when none does)."""
    found = [w for w in catalogue_text.ways(catalogue_text.listed(apps)) if w != "installer"]
    names = {"colab": "Google Colab", "pip": "pip"}
    phrases = {"colab": "open the notebooks in Google Colab", "pip": "install the package with pip"}
    if not found:
        return ""
    text = " or ".join(phrases[w] for w in found)
    return fact(join_and([names[w] for w in found]), text[0].upper() + text[1:] + ".", "apps/", "See the apps")


def host_fact(plugin_kind: str, pills: str) -> str:
    """The image software tile: the plugin stage (taken from the plugins' own status) and the programs as pills."""
    return fact("In your image software", f"{plugin_kind} let apps that declare tools run inside:", "guides/image-software/", "Use apps in your image software", pills)


def works_band(apps: list[dict], plugin_kind: str, pills: str) -> str:
    """The "Packaged once, easy to install" band: one tile per place an app is available."""
    tiles = "".join([install_fact(apps), notebook_fact(apps), host_fact(plugin_kind, pills)])
    return f'<section class="lc-band lc-band--soft"><h2 class="lc-title">Packaged once, easy to install, available where you need it</h2><div class="lc-facts">{tiles}</div></section>'
