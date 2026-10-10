"""Home, ecosystem and submit pages."""

from .cards import card
from .config import CONTENT, DOCS
from .page import Page
from .text import esc, plural


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
            f'<div class="lc-comic__panels">{panels}</div><figcaption>The problem LabConstrictor was made for.</figcaption></figure>')


def choice(title: str, text: str, href: str, label: str, cls: str = "") -> str:
    """One of the two big "what do you want to do" cards on the home page."""
    return (f'<a class="lc-choice {cls}" href="{href}"><strong>{esc(title)}</strong><span>{esc(text)}</span>'
            f'<span class="lc-choice__go">{esc(label)} &rarr;</span></a>')


def page_home(site: dict, apps: list[dict]) -> None:
    """index.md: hero with the logo, the two paths (use / make), the comic, featured apps, how it works, where apps run."""
    hero = site["hero"]
    featured = [a for a in apps if a["featured"]]
    p = Page("index.md", title="LabConstrictor", head_title=f"{site['name']}: {hero['title']}", description=hero["text"], template="home.html")
    p.add(f'<section class="lc-hero"><div class="lc-hero__in"><div><h1>{esc(hero["title"])}</h1><p>{esc(hero["text"])}</p>'
          '<div class="lc-choices">'
          + choice("I want to use an app", f"Browse {plural(len(apps), 'app')} for image analysis. Install in a few clicks.", "apps/", "Open the App Centre")
          + choice("I want to make an app", "Turn your notebooks into installers for Windows, macOS and Linux.", "build/", "Why and how to build one", "lc-choice--make") +
          '</div></div><div class="lc-hero__art"><img src="assets/images/logo.png" alt="The LabConstrictor logo: a green snake coiled around an orange notebook" width="256" height="256"></div></div></section>')
    p.add(comic_figure())
    p.add('<section class="lc-band"><h2 class="lc-title">Featured apps</h2>',
          '<ul class="lc-grid">' + "\n".join(card(a) for a in featured) + '</ul>',
          '<p class="lc-more"><a href="apps/">See every app</a></p></section>')
    steps = "".join(f'<li><strong>{esc(s["title"])}</strong><span>{esc(s["text"])}</span></li>' for s in site["steps"])
    p.add(f'<section class="lc-band lc-band--soft"><h2 class="lc-title">How it works</h2><ol class="lc-steps">{steps}</ol>',
          f'<p class="lc-more"><a href="{esc(site["links"]["template"])}">Start from the template</a> · <a href="build/">Read the guides</a></p></section>')
    p.add('<section class="lc-band"><h2 class="lc-title">Works where you work</h2>',
          '<p class="lc-center">Desktop installers, Google Colab and pip. Apps that declare tools also run inside napari, Fiji and QuPath.</p>',
          '<p class="lc-more"><a href="guides/image-software/">Use apps in your image software</a> · <a href="ecosystem/">Explore the ecosystem</a></p></section>')
    p.write()


def guide_link(card: dict) -> str:
    """The guide footer of an ecosystem card (empty when the repository has no guide on this site)."""
    return f'<div class="lc-card__foot"><a href="guides/{esc(card["guide"])}/">Guide</a></div>' if card["guide"] else ""


def ecosystem_card(card: dict) -> str:
    """One project card: its name, summary and status, linked to its repository (or hosted app), with its guide."""
    return (f'<li class="lc-card lc-card--plain"><a class="lc-card__main" href="{esc(card["link"])}">'
            f'<span class="lc-card__title"><strong>{esc(card["name"])}</strong></span><span class="lc-card__text">{esc(card["summary"])}</span>'
            f'<span class="lc-card__badges"><span class="lc-badge">{esc(card["status"])}</span></span></a>{guide_link(card)}</li>')


def page_ecosystem(tiers: list[dict]) -> None:
    """ecosystem.md: the projects around LabConstrictor by tier, resolved from their own repositories (projects.resolve)."""
    p = Page("ecosystem.md", title="Ecosystem", description="Hosts, tools and templates around LabConstrictor.", layout="wide")
    p.add('<section class="lc-pagehead"><h1>Ecosystem</h1><p class="lc-lead">Everything around the apps: where they run and what builds them.</p></section>')
    for tier in tiers:
        items = "".join(ecosystem_card(c) for c in tier["cards"])
        p.add(f'<h2 class="lc-tier" id="{esc(tier["key"])}">{esc(tier["title"])}</h2><p>{esc(tier["text"])}</p><ul class="lc-grid">{items}</ul>')
    p.write()


def page_submit(site: dict, schema_url: str) -> None:
    """submit.md: content/submit.md with {{submit_issue}} and {{schema_url}} filled in from the site data."""
    text = (CONTENT / "submit.md").read_text(encoding="utf-8")
    text = text.replace("{{submit_issue}}", site["links"]["submit_issue"]).replace("{{schema_url}}", schema_url)
    (DOCS / "submit.md").write_text(text, encoding="utf-8")
