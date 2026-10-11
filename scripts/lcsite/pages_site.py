"""Home, ecosystem and submit pages."""

from . import catalogue_text, citation, hosts, pages_demo, pages_home, pages_how, pages_related, projects
from .cards import card, github_badge
from .config import CONTENT, DOCS, REPO, fail
from .page import Page
from .text import esc


COMIC_ALT = ("A three-panel comic. Panel 1: a delighted scientist says \"Finally, my ultimate notebook is ready!\" "
             "Panel 2: a worried colleague beside a computer showing a warning says \"Sorry, not even able to install it.\" "
             "Panel 3: the LabConstrictor snake coiled around an orange notebook glows, with the words \"LabConstrictor will solve it!\"")


PANEL_ALTS = ("A delighted scientist says: Finally, my ultimate notebook is ready!",
              "A worried colleague beside a computer showing a warning says: Sorry, not even able to install it.",
              "The LabConstrictor snake coiled around an orange notebook glows: LabConstrictor will solve it!")


def comic_figure() -> str:
    """The comic: the whole strip on wide screens, three stacked panels (cropped by CSS from the same image) on phones."""
    panels = "".join(f'<span class="lc-comic__panel" role="img" aria-label="{esc(alt)}" style="--i:{i}"></span>'
                     for i, alt in enumerate(PANEL_ALTS))
    return (f'<figure class="lc-comic"><img class="lc-comic__strip" src="assets/images/comic.png" alt="{esc(COMIC_ALT)}" loading="lazy">'
            f'<div class="lc-comic__panels">{panels}</div></figure>')


def choice(title: str, text: str, href: str, label: str, cls: str = "") -> str:
    """One of the two big "what do you want to do" cards on the home page."""
    return (f'<a class="lc-choice {cls}" href="{href}"><strong>{esc(title)}</strong><span>{esc(text)}</span>'
            f'<span class="lc-go">{esc(label)}</span></a>')


def program_pill_row(stage: str) -> str:
    """The plugins' stage as a chip, then the program pills (logo + name, linked to each program's website), as one row."""
    table = hosts.load()
    return f'<p class="lc-pills"><span class="lc-badge lc-badge--status">{esc(stage)}</span>' + "".join(hosts.pill(k, table) for k in table) + "</p>"


def plugin_stage() -> str:
    """The stage every plugin of data/hosts.yaml has ("Experimental", "Available", ...), taken from the plugins' own project files;
    "Stages vary" when they differ."""
    stages = {projects.host_status(key) for key in hosts.load()}
    return next(iter(stages)) if len(stages) == 1 else "Stages vary"


def page_home(site: dict, apps: list[dict]) -> None:
    """index.md: hero with the logo and the two paths (use / make), then the comic (the problem), the five steps of How it works (the solution), the How it works and demo tiles, the optional plugin section, featured apps and the citation."""
    hero = site["hero"]
    featured = pages_home.featured_apps(apps)
    p = Page("index.md", title="LabConstrictor", head_title=f"{site['name']}: {hero['title']}", description=hero["text"], template="home.html")
    p.add(f'<section class="lc-hero"><div class="lc-hero__in"><div><h1>{esc(hero["title"])}</h1><p>{esc(hero["text"])}</p>'
          '<div class="lc-choices">'
          + choice("I want to find an app", catalogue_text.home_find_text(apps), "apps/", "Open the App Centre")
          + choice("I want to make an app", "Turn your notebooks into installers for Windows, macOS and Linux.", "build/", "Why and how to build one", "lc-choice--make") +
          '</div></div><div class="lc-hero__art"><img src="assets/images/logo.png" alt="The LabConstrictor logo: a green snake coiled around an orange notebook" width="256" height="256" loading="eager" fetchpriority="high"></div></div></section>')
    p.add(pages_home.comic_band(comic_figure()))
    p.add(pages_home.steps_band(site["steps_title"], pages_how.load()["steps"]))
    p.add(pages_home.tiles_band(site["tiles_title"], [pages_home.how_tile(site), pages_demo.home_tile()]))
    p.add(pages_home.plugins_band(site, program_pill_row(plugin_stage())))
    p.add(pages_home.featured_band([card(a) for a in featured], "No app is featured yet."))
    p.add(citation.cite_band(site))
    p.write()


def card_foot(card: dict) -> str:
    """The footer of an ecosystem card: a GitHub badge for its repository and, when it has one, a link to its guide here."""
    guide = f'<a class="lc-go" href="guides/{esc(card["guide"])}/">Guide</a>' if card["guide"] else ""
    program = hosts.pill(card["host"], hosts.load()) if card["host"] else ""
    return f'<div class="lc-card__foot">{github_badge(card["repo"])}{program}{guide}</div>'


def ecosystem_card(card: dict) -> str:
    """One project card: its name, summary and status, linked to its repository (or hosted app), with its guide. The card of a plugin is
    titled "Plugin for <program>" (the project's own name is the program's, so the card says what the project is)."""
    title = f'Plugin for {card["name"]}' if card["host"] else card["name"]
    return (f'<li class="lc-card lc-card--plain"><a class="lc-card__main" href="{esc(card["link"])}">'
            f'<span class="lc-card__title">{hosts.logo(card["host"]) if card["host"] else ""}<strong>{esc(title)}</strong></span><span class="lc-card__text">{esc(card["summary"])}</span>'
            f'<span class="lc-card__badges"><span class="lc-badge">{esc(card["status"])}</span></span></a>{card_foot(card)}</li>')


def page_ecosystem(tiers: list[dict], related: dict) -> None:
    """ecosystem.md: the projects around LabConstrictor by tier, resolved from their own repositories (projects.resolve), then one tile that leads to the related-projects page."""
    p = Page("ecosystem.md", title="Ecosystem", description="Hosts, tools and templates around LabConstrictor, and a link to other open-source ways to share notebooks and scientific tools.", layout="wide",
             edit_url=f"{REPO}/edit/main/data/ecosystem.yaml")
    p.add('<section class="lc-pagehead"><h1>Ecosystem</h1><p class="lc-lead">Everything around the apps: where they run and what builds them.</p></section>')
    for tier in tiers:
        items = "".join(ecosystem_card(c) for c in tier["cards"])
        p.add(f'<h2 class="lc-tier" id="{esc(tier["key"])}">{esc(tier["title"])}</h2><p>{esc(tier["text"])}</p><ul class="lc-grid">{items}</ul>')
    p.add(pages_related.teaser(related))
    names = [h["name"] for h in hosts.load().values()] + [s["name"] for s in hosts.load_services().values()]
    p.add(f'<p class="lc-small">The logos of {", ".join(names[:-1])} and {names[-1]} belong to their owners and are shown only to identify them.</p>')
    p.write()


def page_submit(site: dict, schema_url: str) -> None:
    """submit.md: content/submit.md with {{submit_issue}} and {{schema_url}} filled in from the site data."""
    text = (CONTENT / "submit.md").read_text(encoding="utf-8")
    text = text.replace("{{submit_issue}}", site["links"]["submit_issue"]).replace("{{schema_url}}", schema_url)
    (DOCS / "submit.md").write_text(text, encoding="utf-8")
