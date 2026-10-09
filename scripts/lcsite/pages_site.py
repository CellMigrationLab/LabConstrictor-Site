"""Home, ecosystem and submit pages."""

from .cards import card
from .config import CONTENT, DOCS
from .page import Page
from .text import esc, plural


def choice(title: str, text: str, href: str, label: str) -> str:
    """One of the two big "what do you want to do" cards on the home page."""
    return (f'<a class="lc-choice" href="{href}"><strong>{esc(title)}</strong><span>{esc(text)}</span>'
            f'<span class="lc-choice__go">{esc(label)} &rarr;</span></a>')


def page_home(site: dict, apps: list[dict]) -> None:
    """index.md: hero, the two paths (use / make), featured apps, how it works, and where apps run."""
    hero = site["hero"]
    featured = [a for a in apps if a["featured"]]
    p = Page("index.md", title="LabConstrictor", head_title=f"{site['name']}: {hero['title']}", description=site["hero"]["text"], template="home.html")
    p.add(f'<section class="lc-hero"><div class="lc-hero__in"><h1>{esc(hero["title"])}</h1><p>{esc(hero["text"])}</p>'
          '<div class="lc-choices">'
          + choice("I want to use an app", f"Browse {plural(len(apps), 'app')} for image analysis. Install in a few clicks.", "apps/", "Open the App Centre")
          + choice("I want to make an app", "Turn your notebooks into installers for Windows, macOS and Linux.", "guides/", "Read the guides") +
          '</div></div></section>')
    p.add('<section class="lc-band"><h2 class="lc-title">Featured apps</h2>',
          '<ul class="lc-grid">' + "\n".join(card(a) for a in featured) + '</ul>',
          '<p class="lc-more"><a href="apps/">See every app</a></p></section>')
    steps = "".join(f'<li><strong>{esc(s["title"])}</strong><span>{esc(s["text"])}</span></li>' for s in site["steps"])
    p.add(f'<section class="lc-band lc-band--soft"><h2 class="lc-title">How it works</h2><ol class="lc-steps">{steps}</ol>',
          f'<p class="lc-more"><a href="{esc(site["links"]["template"])}">Start from the template</a> · <a href="guides/">Read the guides</a></p></section>')
    p.add('<section class="lc-band"><h2 class="lc-title">Works where you work</h2>',
          '<p class="lc-center">Desktop installers, Google Colab and pip, plus napari, Fiji and QuPath for apps that expose tools.</p>',
          '<p class="lc-more"><a href="ecosystem/">Explore the ecosystem</a></p></section>')
    p.write()


def page_ecosystem(ecosystem: dict) -> None:
    """ecosystem.md: the projects around LabConstrictor, by tier (data/ecosystem.yaml)."""
    p = Page("ecosystem.md", title="Ecosystem", description="Hosts, tools and templates around LabConstrictor.", layout="wide")
    p.add('<section class="lc-pagehead"><h1>Ecosystem</h1><p class="lc-lead">Everything around the apps: where they run and what builds them.</p></section>')
    for tier in ecosystem["tiers"]:
        items = "".join(
            f'<li class="lc-card lc-card--plain"><a class="lc-card__main" href="{esc(i.get("url") or "https://github.com/" + i["repo"])}">'
            f'<span class="lc-card__title"><strong>{esc(i["name"])}</strong></span><span class="lc-card__text">{esc(i["text"])}</span>'
            f'<span class="lc-card__badges"><span class="lc-badge">{esc(i["status"])}</span></span></a></li>' for i in tier["items"])
        p.add(f'<h2 class="lc-tier" id="{esc(tier["key"])}">{esc(tier["title"])}</h2><p>{esc(tier["text"])}</p><ul class="lc-grid">{items}</ul>')
    p.write()


def page_submit(site: dict, schema_url: str) -> None:
    """submit.md: content/submit.md with {{submit_issue}} and {{schema_url}} filled in from the site data."""
    text = (CONTENT / "submit.md").read_text(encoding="utf-8")
    text = text.replace("{{submit_issue}}", site["links"]["submit_issue"]).replace("{{schema_url}}", schema_url)
    (DOCS / "submit.md").write_text(text, encoding="utf-8")
