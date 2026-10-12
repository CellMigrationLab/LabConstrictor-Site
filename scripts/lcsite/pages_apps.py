"""The App Centre (apps/index.md) and one page per app (apps/<slug>/index.md)."""

import json

from .cards import KINDS, SYSTEMS, badge, card, github_badge, host_badge, icon, link_pill, offered_assets, plugin_stage, release_line, testing_badge
from . import catalogue_text, citation, filters, hosts, pages_facts, pages_get, projects
from .config import SCIENTIFIC_KINDS
from .page import Page
from .validate import optional_list
from .text import esc, long_date, paragraphs

NOTICE = ("Apps are listed after automatic checks: a public repository, a valid description file (labconstrictor-app.yaml) and downloads from the app's own GitHub release. "
          "That is not a security audit and not a test of the results: download only from an owner you trust.")


def grid(apps: list[dict], extra: str = "") -> str:
    """A grid of app cards (the filter acts on every grid on the page)."""
    return f'<ul class="lc-grid" data-lc-grid{extra}>\n' + "\n".join(card(a) for a in apps) + "\n</ul>"


def page_catalogue(all_apps: list[dict]) -> None:
    """apps/index.md: the filterable grid of the apps, then the apps for testing and maintenance listed apart."""
    apps = [a for a in all_apps if a["section"] == "apps"]
    testing = [a for a in all_apps if a["section"] == "testing"]
    p = Page("apps/index.md", title="App Centre", head_title="App Centre – LabConstrictor", description=catalogue_text.catalogue_description(all_apps), layout="wide")
    p.add('<section class="lc-pagehead"><h1>App Centre</h1>',
          f'<p class="lc-lead">{esc(catalogue_text.catalogue_lead(all_apps))}</p></section>',
          filters.filter_bar(apps), f'<div data-lc-group>{grid(apps)}</div>',
          '<p class="lc-empty" data-lc-empty hidden><span data-lc-empty-text>No app matches.</span> Clear a filter or search for something broader, or <a href="submit/">add an app for this task</a>.</p>',
          (f'<div data-lc-group class="lc-testing"><h2 class="lc-title">Testing and maintenance</h2><p>Apps for checking LabConstrictor and showing what it makes, '
           f'not for analysing your data: use them to check that your computer is ready, or to see what an app built from the template looks like.</p>{grid(testing)}</div>' if testing else ""),
          f'<p class="lc-small lc-notice">{NOTICE}</p>',
          '<p class="lc-cta"><a class="lc-btn" href="submit/">Add your app</a></p>')
    p.write()


def details_list(app: dict) -> str:
    """The facts: kind, version, license, authors, categories, links (the citation has its own section)."""
    m = app["manifest"]
    rows = [("Kind", KINDS[m["kind"]]), ("Development status", pages_facts.status_row(app)), ("Latest release", release_line(app)),
            ("License", esc(app["license"] or "Not stated")), ("Repository owner", esc(app["repo"].split("/")[0]))]
    if works_in(app):
        rows.append(("Also in (plugins)", works_in(app)))
    if m.get("authors"):
        rows.append(("Authors", ", ".join(esc(a["name"]) for a in m["authors"])))
    if m.get("categories"):
        rows.append(("Topics", ", ".join(esc(c) for c in m["categories"])))
    links = [("Report a problem", app["html_url"] + "/issues" if app["has_issues"] else ""), ("Homepage", m.get("homepage")), ("Documentation", m.get("docs_url"))]
    shown = [f'<a href="{esc(u)}">{t}</a>' for t, u in links if u] + ([] if app["has_issues"] else ["No issue tracker on GitHub"])
    rows.append(("Links", " · ".join(shown)))
    return '<h2 id="details">Details</h2><dl class="lc-facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl>"


def header_links(app: dict) -> str:
    """The pills under the summary: the repository, then the app's documentation and website when its manifest gives them."""
    m = app["manifest"]
    pills = [github_badge(app["repo"])]
    if m.get("docs_url"):
        pills.append(link_pill(m["docs_url"], "Documentation", "docs"))
    if m.get("homepage"):
        pills.append(link_pill(m["homepage"], "Website", "web"))
    return "".join(pills)


def works_in(app: dict) -> str:
    """The programs the app declares a plugin for, each a pill with its logo linked to the program's website and the plugin's stage (empty when only a notebook)."""
    table = hosts.load()
    return " ".join(f'{hosts.pill(h, table)} <span class="lc-small">plugin: {plugin_stage(projects.host_status(h), h)}</span>'
                    for h in optional_list(app["manifest"], "hosts") if h in table)


def jsonld(app: dict) -> str:
    """schema.org SoftwareApplication data for search engines, as JSON in which < > & are escaped so that no
    manifest text can close the <script> block or start an HTML comment."""
    m = app["manifest"]
    data = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": m["name"], "description": m["summary"], "url": app["html_url"]}
    if m["kind"] in SCIENTIFIC_KINDS and app["section"] != "testing":
        data["applicationCategory"] = "ScientificApplication"
    if app["release"]:
        data["softwareVersion"] = app["release"]["tag"]
    systems = [SYSTEMS[k] for k in SYSTEMS if any(a["os"] == k for a in offered_assets(app))]
    if systems:
        data["operatingSystem"] = ", ".join(systems)
    return json.dumps(data).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def page_app(app: dict) -> None:
    """apps/<slug>/index.md: everything a visitor needs to decide, install, cite and report a problem."""
    m = app["manifest"]
    p = Page(f"apps/{app['slug']}/index.md", title=m["name"], description=m["summary"], jsonld=jsonld(app), layout="wide", menu="apps/",
             edit_url=f"{app['html_url']}/edit/HEAD/labconstrictor-app.yaml")
    plugins = [h for h in optional_list(m, "hosts") if h != "notebook"]
    p.add('<p class="lc-crumb"><a href="apps/">&larr; All apps</a></p>',
          f'<header class="lc-apphead"><div class="lc-apphead__name">{icon(app, 56)}<h1>{esc(m["name"])}</h1></div>'
          f'<p class="lc-lead">{esc(m["summary"])}</p><p>{badge(KINDS[m["kind"]])}{pages_facts.status_chip(app)}'
          f'{"".join(host_badge(h) for h in plugins)}{testing_badge(app)}</p><p>{header_links(app)}</p></header>')
    p.add(pages_facts.works_with(app), pages_get.get_section(app))
    for i, shot in enumerate(app["screenshots"], 1):
        p.add(pages_facts.screenshot(app, i, shot))
    p.add(pages_get.using_section(app), pages_facts.limitations(app), citation.app_section(app))
    if m.get("description"):
        p.add('<h2 id="about">About</h2>', paragraphs(m["description"]))
    if app["release"] and m["distribution"].get("installer"):
        p.add(pages_get.downloads_table(app), pages_get.install_help())
    p.add(details_list(app))
    p.write()
