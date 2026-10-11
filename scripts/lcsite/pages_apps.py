"""The App Centre (apps/index.md) and one page per app (apps/<slug>/index.md)."""

import json
import re

from .cards import CHIPS, HOST_GUIDES, HOSTS, KINDS, ROUTES, SYSTEM_LABELS, SYSTEMS, badge, card, downloads, plugin_stage, github_badge, host_badge, icon, link_pill, release_line, testing_badge
from . import catalogue_text, citation, filters, hosts, pages_facts, projects
from .page import Page
from .validate import optional_list
from .text import esc, long_date, megabytes, paragraphs

NOTICE = ("Apps are listed after automatic checks: a public repository, a valid manifest and downloads from the app's own GitHub release. "
          "That is not a security audit and not a test of the results: download only from an owner you trust.")


def grid(apps: list[dict], extra: str = "") -> str:
    """A grid of app cards (the filter acts on every grid on the page)."""
    return f'<ul class="lc-grid" data-lc-grid{extra}>\n' + "\n".join(card(a) for a in apps) + "\n</ul>"


def page_catalogue(all_apps: list[dict]) -> None:
    """apps/index.md: the filterable grid of the apps, then the apps for testing and maintenance listed apart."""
    apps = [a for a in all_apps if a["section"] == "apps"]
    testing = [a for a in all_apps if a["section"] == "testing"]
    p = Page("apps/index.md", title="Apps", description=catalogue_text.catalogue_description(all_apps), layout="wide")
    p.add('<section class="lc-pagehead"><h1>Apps</h1>',
          f'<p class="lc-lead">{esc(catalogue_text.catalogue_lead(all_apps))}</p></section>',
          filters.filter_bar(apps), f'<div data-lc-group>{grid(apps)}</div>',
          '<p class="lc-empty" data-lc-empty hidden><span data-lc-empty-text>No app matches.</span> Clear a filter or search for something broader, or <a href="submit/">add an app for this task</a>.</p>',
          (f'<div data-lc-group class="lc-testing"><h2 class="lc-title">Testing and maintenance</h2><p>Apps that check or '
           f'maintain LabConstrictor itself, not for analysing your data. Useful to see that your computer works, or what a template can do.</p>{grid(testing)}</div>' if testing else ""),
          f'<p class="lc-small lc-notice">{NOTICE}</p>',
          '<p class="lc-cta"><a class="lc-btn" href="submit/">Add your app</a></p>')
    p.write()


def os_button(option: dict, system: str, first: bool) -> str:
    """One download button inside a system tile: macOS buttons are named by chip, others by system."""
    name = CHIPS[option["arch"]] if system == "macos" else f"{SYSTEMS[system]} installer"
    emphasised = first and system != "macos"   # a Mac's chip is unknown until lc.js detects it: both buttons look the same
    return (f'<a class="lc-btn{"" if emphasised else " lc-btn--ghost"}" href="{esc(option["url"])}" data-arch="{option["arch"]}">'
            f'{esc(name)}<small>{megabytes(option["size"])} · .{option["ext"]}</small></a>')


def os_tile(system: str, options: list[dict]) -> str:
    """The tile for one system: its download buttons, or "not available" when the release has none (never hidden)."""
    body = ("".join(os_button(o, system, i == 0) for i, o in enumerate(options)) if options
            else '<p class="lc-small">No installer in this release.</p>')
    hint = {"macos": "Not sure? Apple menu, About This Mac: Intel, or M1 and later (Apple Silicon).",
            "linux": "Run it with: bash &lt;file name&gt;", "windows": "If Windows warns you, choose More info, then Run anyway."}[system]
    return f'<div class="lc-ostile" data-os="{system}"><h3>{SYSTEMS[system]}</h3>{body}<p class="lc-small">{hint}</p></div>'


COLAB_FILE = re.compile(r"^https://colab\.research\.google\.com/github/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$")


def github_view(colab_url: str) -> str:
    """The GitHub address of the notebook behind a Colab link (colab.research.google.com/github/o/r/blob/branch/path), or "" when the link is of another kind."""
    m = COLAB_FILE.match(colab_url)
    return f"https://github.com/{m.group(1)}/{m.group(2)}/blob/{m.group(3)}/{m.group(4)}" if m else ""


def notebook_row(link: dict) -> str:
    """One notebook the author chose to show: its name, "Open in Colab" with the logo, and "View on GitHub" when the link says where the file is."""
    view = github_view(link["url"])
    source = f'<a href="{esc(view)}">View on GitHub</a>' if view else ""
    return (f'<li><span class="lc-notebooks__name">{esc(link["label"])}</span>'
            f'<a class="lc-btn lc-btn--ghost lc-btn--small" href="{esc(link["url"])}">{hosts.service_logo("colab")}Open in Colab</a>{source}</li>')


def notebooks_list(links: list[dict]) -> str:
    """The notebooks listed in the manifest (`distribution.colab`): only what the author lists is shown."""
    return '<h3 id="notebooks">Notebooks to open in your browser</h3><ul class="lc-notebooks">' + "".join(notebook_row(l) for l in links) + "</ul>"


def get_section(app: dict) -> str:
    """The "Get it" block: a download tile per system, Colab buttons and the pip command."""
    dist = app["manifest"]["distribution"]
    parts = ['<h2 id="get">Get it</h2>']
    if app["release"] and dist.get("installer"):
        have = downloads(app)
        parts.append('<div class="lc-osgrid" data-lc-osgrid>' + "".join(os_tile(k, have[k]) for k in SYSTEMS) + "</div>")
        parts.append('<p class="lc-small">Need help installing? See the <a href="guides/install/">install guide</a>.</p>')
    if optional_list(dist, "colab"):
        parts.append(notebooks_list(optional_list(dist, "colab")))
    if dist.get("pip"):
        parts.append(f'<div class="lc-code"><code>pip install {esc(dist["pip"])}</code><button type="button" class="lc-btn lc-btn--ghost lc-btn--small" data-copy>Copy</button></div>')
    return "\n".join(parts)


def using_section(app: dict) -> str:
    """"Using it": the manifest's quick start (optional), how a desktop app starts, and the documentation link
    (the manifest's docs_url, else the README on GitHub; the label says which)."""
    m = app["manifest"]
    parts = ['<h2 id="use">Using it</h2>']
    if m.get("quickstart"):
        parts.append("<ol>" + "".join(f"<li>{esc(step)}</li>" for step in m["quickstart"]) + "</ol>")
    if m["distribution"].get("installer"):
        parts.append('<p>After installing, open the app from your Start Menu or Applications folder. Its Welcome notebook lists what it can do; '
                     'the <a href="guides/notebook-usage/">notebook usage guide</a> shows how to work with it.</p>')
    docs, label = (m["docs_url"], "Documentation") if m.get("docs_url") else (app["html_url"] + "#readme", "README on GitHub")
    parts.append(f'<p>Read more: <a href="{esc(docs)}">{label}</a>.</p>')
    return "\n".join(parts)


def downloads_table(app: dict) -> str:
    """Every installer of the latest release: system, format, size, direct link."""
    rows = "".join(
        f'<tr><td>{SYSTEM_LABELS[(a["os"], a["arch"])]}</td><td>.{a["ext"]}</td><td>{megabytes(a["size"])}</td>'
        f'<td><a href="{esc(a["url"])}">{esc(a["name"])}</a></td></tr>' for a in app["release"]["assets"])
    return (f'<h2 id="downloads">All downloads</h2><p class="lc-small">Version {esc(app["release"]["tag"])}, '
            f'released {long_date(app["release"]["published_at"])}. Files come straight from the app\'s '
            f'<a href="{esc(app["release"]["url"])}">GitHub release</a>.</p>'
            f'<div class="lc-scroll"><table class="lc-table"><thead><tr><th>System</th><th>Format</th><th>Size</th><th>File</th></tr></thead><tbody>{rows}</tbody></table></div>')


def install_help() -> str:
    """"How to install": a pointer to the install guide (the template's page, imported by the site), so the steps are written once."""
    return ('<h2 id="install">How to install</h2><p>Step by step for Windows, macOS and Linux, with the pictures: '
            '<a href="guides/install/">Install an app</a>.</p>')


def details_list(app: dict) -> str:
    """The facts: kind, version, license, authors, categories, links (the citation has its own section)."""
    m = app["manifest"]
    rows = [("Kind", KINDS[m["kind"]]), ("Development status (stated by the authors)", pages_facts.status_row(app)), ("Latest release", release_line(app)),
            ("License", esc(app["license"] or "Not stated"))]
    if works_in(app):
        rows.append(("Also in (plugins)", works_in(app)))
    if m.get("authors"):
        rows.append(("Authors", ", ".join(esc(a["name"]) for a in m["authors"])))
    if m.get("categories"):
        rows.append(("Topics", ", ".join(esc(c) for c in m["categories"])))
    links = [("Report a problem", app["html_url"] + "/issues"), ("Homepage", m.get("homepage")), ("Documentation", m.get("docs_url"))]
    rows.append(("Links", " · ".join(f'<a href="{esc(u)}">{t}</a>' for t, u in links if u)))
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
    data = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": m["name"], "description": m["summary"],
            "applicationCategory": "ScientificApplication", "url": app["html_url"]}
    if app["release"]:
        data["softwareVersion"] = app["release"]["tag"]
    if m["distribution"].get("installer"):
        data["operatingSystem"] = "Windows, macOS, Linux"
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
    p.add(pages_facts.works_with(app), get_section(app))
    if m.get("description"):
        p.add('<h2 id="about">About</h2>', paragraphs(m["description"]))
    for i, s in enumerate(app["screenshots"], 1):
        p.add(pages_facts.screenshot(app, i, s))
    p.add(using_section(app), pages_facts.limitations(app), citation.app_section(app))
    if app["release"] and m["distribution"].get("installer"):
        p.add(downloads_table(app), install_help())
    p.add(details_list(app))
    p.write()
