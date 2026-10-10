"""The App Centre (apps/index.md) and one page per app (apps/<slug>/index.md)."""

import json

from .cards import CHIPS, HOSTS, KINDS, ROUTES, SYSTEM_LABELS, SYSTEMS, badge, card, downloads, icon, is_verified, release_line, tier_badge
from .page import Page
from .validate import optional_list
from .text import esc, long_date, megabytes, paragraphs, plural

LEGEND = ("<strong>Verified</strong>: a maintainer installed and ran this exact version. "
          "<strong>Community</strong>: public repository, valid manifest and downloads straight from GitHub, checked automatically.")


def select(name: str, label: str, options: dict[str, str]) -> str:
    """A filter drop-down whose first option ("All ...") means no filtering."""
    items = "".join(f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in options.items())
    return f'<label>{esc(label)}<select data-lc-{name}><option value="">All</option>{items}</select></label>'


def filter_bar() -> str:
    """Search box and drop-downs; lc.js filters the cards live and keeps the count."""
    return ('<form class="lc-filter" data-lc-filter role="search" onsubmit="return false">'
            '<label class="lc-filter__search">Search<input type="search" data-lc-search placeholder="Name, topic, what it does"></label>'
            + select("kind", "Kind", KINDS) + select("route", "Get it as", ROUTES) + select("host", "Works in", HOSTS) +
            '<p class="lc-filter__count" data-lc-count aria-live="polite"></p></form>')


def page_catalogue(apps: list[dict]) -> None:
    """apps/index.md: the filterable grid of every listed app."""
    p = Page("apps/index.md", title="Apps", description="Bioimage analysis apps built with LabConstrictor: install them on Windows, macOS or Linux, or open them in Colab.", layout="wide")
    cards = "\n".join(card(a) for a in apps)
    p.add('<section class="lc-pagehead"><h1>Apps</h1>',
          f'<p class="lc-lead">{plural(len(apps), "app")} built with LabConstrictor. Install one in a few clicks, or open it in Colab.</p></section>',
          filter_bar(), f'<ul class="lc-grid" data-lc-grid>\n{cards}\n</ul>',
          '<p class="lc-empty" data-lc-empty hidden>No app matches. Clear a filter or search for something broader.</p>',
          f'<p class="lc-small lc-legend">{LEGEND}</p>',
          '<p class="lc-cta"><a class="lc-btn" href="submit/">Add your app</a></p>')
    p.write()


def os_button(option: dict, system: str, first: bool) -> str:
    """One download button inside a system tile: macOS buttons are named by chip, others by system."""
    name = CHIPS[option["arch"]] if system == "macos" else f"{SYSTEMS[system]} installer"
    return (f'<a class="lc-btn{"" if first else " lc-btn--ghost"}" href="{esc(option["url"])}" data-arch="{option["arch"]}">'
            f'{esc(name)}<small>{megabytes(option["size"])} · .{option["ext"]}</small></a>')


def os_tile(system: str, options: list[dict]) -> str:
    """The tile for one system: its download buttons, or "not available" when the release has none (never hidden)."""
    body = ("".join(os_button(o, system, i == 0) for i, o in enumerate(options)) if options
            else '<p class="lc-small">No installer in this release.</p>')
    hint = {"macos": "Not sure? Apple menu, About This Mac: Intel, or M1 and later (Apple Silicon).",
            "linux": "Run it with: bash &lt;file name&gt;", "windows": "If Windows warns you, choose More info, then Run anyway."}[system]
    return f'<div class="lc-ostile" data-os="{system}"><h3>{SYSTEMS[system]}</h3>{body}<p class="lc-small">{hint}</p></div>'


def get_section(app: dict) -> str:
    """The "Get it" block: a download tile per system, Colab buttons and the pip command."""
    dist = app["manifest"]["distribution"]
    parts = ['<h2 id="get">Get it</h2>']
    if app["release"] and dist.get("installer"):
        have = downloads(app)
        parts.append('<div class="lc-osgrid" data-lc-osgrid>' + "".join(os_tile(k, have[k]) for k in SYSTEMS) + "</div>")
    colab = "".join(f'<a class="lc-btn lc-btn--ghost" href="{esc(l["url"])}">Open in Colab: {esc(l["label"])}</a>' for l in optional_list(dist, "colab"))
    if colab:
        parts.append(f'<div class="lc-routes">{colab}</div>')
    if dist.get("pip"):
        parts.append(f'<div class="lc-code"><code>pip install {esc(dist["pip"])}</code><button type="button" data-copy>Copy</button></div>')
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
    parts.append(f'<p><a class="lc-btn lc-btn--ghost" href="{esc(docs)}">{label}</a></p>')
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


def install_help(systems: list[dict]) -> str:
    """Collapsible per-system install steps (from data/install.yaml); lc.js opens the visitor's own system."""
    items = "".join(
        f'<details class="lc-os" data-os="{s["key"]}"><summary>{esc(s["title"])}</summary><ol>'
        + "".join(f"<li>{esc(step)}</li>" for step in s["steps"]) + "</ol></details>" for s in systems)
    return f'<h2 id="install">How to install</h2>{items}'


def details_list(app: dict) -> str:
    """The facts: kind, version, license, authors, categories, links, verification."""
    m = app["manifest"]
    verified = (f"Verified for {esc(app['verified_version'])}" + (f" on {long_date(app['verified_on'])}" if app["verified_on"] else "")
                if is_verified(app) else "Community listing (not verified by a maintainer)")
    rows = [("Kind", KINDS[m["kind"]]), ("Latest release", release_line(app)), ("License", esc(app["license"] or "Not stated")), ("Status", verified)]
    if m.get("authors"):
        rows.append(("Authors", ", ".join(esc(a["name"]) for a in m["authors"])))
    if m.get("categories"):
        rows.append(("Topics", ", ".join(esc(c) for c in m["categories"])))
    if m.get("doi"):
        rows.append(("Cite", f'<a href="https://doi.org/{esc(m["doi"])}">doi:{esc(m["doi"])}</a>'))
    links = [("Source code", app["html_url"]), ("Report a problem", app["html_url"] + "/issues"), ("Homepage", m.get("homepage")), ("Documentation", m.get("docs_url"))]
    rows.append(("Links", " · ".join(f'<a href="{esc(u)}">{t}</a>' for t, u in links if u)))
    return '<h2 id="details">Details</h2><dl class="lc-facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl>"


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


def page_app(app: dict, systems: list[dict]) -> None:
    """apps/<slug>/index.md: everything a visitor needs to decide, install, cite and report a problem."""
    m = app["manifest"]
    p = Page(f"apps/{app['slug']}/index.md", title=m["name"], description=m["summary"], jsonld=jsonld(app), layout="wide")
    hosts = [HOSTS[h] for h in optional_list(m, "hosts") if h != "notebook"]
    p.add('<p class="lc-crumb"><a href="apps/">&larr; All apps</a></p>',
          f'<header class="lc-apphead">{icon(app, 72)}<div><h1>{esc(m["name"])}</h1>'
          f'<p class="lc-lead">{esc(m["summary"])}</p><p>{tier_badge(app)}{badge(KINDS[m["kind"]])}'
          f'{"".join(badge(f"Soon in {h}", "host") for h in hosts)}</p></div></header>')
    p.add(get_section(app))
    if m.get("description"):
        p.add('<h2 id="about">About</h2>', paragraphs(m["description"]))
    for i, s in enumerate(app["screenshots"], 1):
        p.add(f'<figure class="lc-shot"><img src="assets/shots/{app["slug"]}-{i}.jpg" alt="{esc(s["caption"])}" loading="lazy"><figcaption>{esc(s["caption"])}</figcaption></figure>')
    p.add(using_section(app))
    if app["release"] and m["distribution"].get("installer"):
        p.add(downloads_table(app), install_help(systems))
    p.add(details_list(app))
    p.write()
