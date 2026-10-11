"""HTML snippets shared by several pages: app cards, badges and download data."""

from . import hosts, projects
from .config import fail
from .text import esc, long_date
from .validate import optional_list

KINDS = {"analysis": "Analysis", "segmentation": "Segmentation", "simulation": "Simulation",
         "game": "Game", "training": "Training", "utility": "Utility"}
HOSTS = {"notebook": "Notebook", "napari": "napari", "fiji": "Fiji", "qupath": "QuPath"}
ROUTES = {"installer": "Desktop", "colab": "Colab", "pip": "pip"}
ROUTE_LABELS = {"installer": "On my computer (Windows, macOS, Linux)", "colab": "In the browser (Colab)", "pip": "Python package (pip)"}
SYSTEM_LABELS = {("windows", "x86_64"): "Windows 64-bit (Intel/AMD, x86_64)", ("windows", "arm64"): "Windows (ARM)", ("macos", "arm64"): "macOS (Apple Silicon)",
                 ("macos", "x86_64"): "macOS (Intel)", ("linux", "x86_64"): "Linux 64-bit (x86_64)", ("linux", "arm64"): "Linux (ARM)"}
PLUGIN_STAGES = {"Experimental": "experimental", "Available": "available", "Install from GitHub": "install from GitHub", "Deprecated": "deprecated"}
SYSTEMS = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}   # one download tile each, in this order
CHIPS = {"arm64": "Apple Silicon (M1 or later)", "x86_64": "Intel"}     # macOS buttons are named by chip


def routes(app: dict) -> list[str]:
    """Route keys ("installer", "colab", "pip") the manifest offers, in display order."""
    dist = app["manifest"]["distribution"]
    return [r for r in ROUTES if dist.get(r)]


HOST_GUIDES = {"napari": "guides/napari/", "fiji": "guides/fiji/", "qupath": "guides/qupath/"}   # host key = guide slug; check_site finds a dead one


def badge(text: str, kind: str = "", href: str = "") -> str:
    """A small pill; `kind` adds a colour class (lc-badge--<kind>); with `href` the pill is a link."""
    cls = f'lc-badge{f" lc-badge--{kind}" if kind else ""}'
    return f'<a class="{cls}" href="{esc(href)}">{esc(text)}</a>' if href else f'<span class="{cls}">{esc(text)}</span>'


GITHUB_MARK = ('<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>')


def github_badge(repo: str, label: str = "") -> str:
    """A small pill with the GitHub mark that links straight to the repository; it shows the repository's name unless `label` says otherwise."""
    return (f'<a class="lc-gh" href="https://github.com/{esc(repo)}" title="{esc(repo)} on GitHub">'
            f'{GITHUB_MARK}<span>{esc(label or repo.split("/")[1])}</span></a>')


BOOK_MARK = ('<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path fill="currentColor" '
             'd="M2 2.75C2 1.78 2.78 1 3.75 1h9.5c.41 0 .75.34.75.75v10.5c0 .41-.34.75-.75.75H4.5a1 1 0 0 0 0 2h8.75a.75.75 0 0 1 0 1.5H4.5A2.5 2.5 0 0 1 2 13.5Zm1.5 8.9c.3-.1.62-.15.95-.15H12.5v-9h-8.75a.25.25 0 0 0-.25.25Z"/></svg>')


def link_pill(url: str, label: str, kind: str) -> str:
    """A pill for a page about the app: kind "docs" shows a book, "web" a plain label."""
    mark = BOOK_MARK if kind == "docs" else ""
    return f'<a class="lc-gh" href="{esc(url)}">{mark}<span>{esc(label)}</span></a>'


def plugin_stage(status: str, key: str) -> str:
    """"experimental", "available", ...: the plugin's stage in the site's one wording. Stops the build, naming the program, for a status it has no wording for."""
    if status not in PLUGIN_STAGES:
        fail(f"the {HOSTS[key]} plugin's project file has the status {status!r}; the site has wording only for {sorted(PLUGIN_STAGES)}")
    return PLUGIN_STAGES[status]


def host_phrase(key: str) -> str:
    """"napari plugin: experimental": what the site says about an app's host, taken from the plugin's own project file (never "soon")."""
    return f"{HOSTS[key]} plugin: {plugin_stage(projects.host_status(key), key)}"


def host_chip(key: str) -> str:
    """A program's logo as a small chip on an app card (the card is one link, so the chip is not one): the plugin's stage for screen readers and as a tooltip."""
    return (f'<span class="lc-badge lc-badge--host lc-badge--logo" title="{esc(host_phrase(key))}">{hosts.logo(key)}'
            f'<span class="lc-sr">{esc(host_phrase(key))}</span></span>')


def host_badge(key: str) -> str:
    """"napari plugin: experimental" with the program's logo, linked to our guide for it."""
    return (f'<a class="lc-badge lc-badge--host" href="{esc(HOST_GUIDES[key])}">{hosts.logo(key)}'
            f'<span>{esc(host_phrase(key))}</span></a>')


def testing_badge(app: dict) -> str:
    """"Testing" for apps that check or maintain LabConstrictor itself (registry `section: testing`); nothing for the others."""
    return badge("Testing", "testing") if app["section"] == "testing" else ""


def host_chips(app: dict) -> str:
    """The logos of the programs the app's manifest says it works in (notebook has none)."""
    return "".join(host_chip(h) for h in optional_list(app["manifest"], "hosts") if h in HOST_GUIDES)


def route_badges(app: dict) -> str:
    """One badge per way to get the app (Desktop, Colab, pip)."""
    return "".join(colab_badge() if r == "colab" else badge(ROUTES[r]) for r in routes(app))


def colab_badge() -> str:
    """The "Colab" route badge, with Google Colab's logo."""
    return f'<span class="lc-badge">{hosts.service_logo("colab")}<span>{ROUTES["colab"]}</span></span>'


def icon(app: dict, size: int = 48) -> str:
    """The app's icon at `size` px, or a monogram tile when the manifest names none (icon is optional)."""
    if app["icon"]:
        return f'<img class="lc-icon" src="assets/icons/{esc(app["slug"])}.png" alt="" width="{size}" height="{size}" loading="lazy">'
    return f'<span class="lc-icon lc-icon--mono" style="--size:{size}px" aria-hidden="true">{esc(app["manifest"]["name"][0].upper())}</span>'


def release_line(app: dict) -> str:
    """"v0.1.5 · 8 October 2026", or "No release yet" for an app that has none (pip or Colab only)."""
    release = app["release"]
    return f'v{esc(release["tag"])} · {long_date(release["published_at"])}' if release else "No release yet"


def offered_assets(app: dict) -> list[dict]:
    """The installers of the latest release the app offers: all of them, or only the platforms its manifest lists (distribution.platforms)."""
    if app["release"] is None:
        return []   # an app without a release (Colab or pip only) has no installers
    dist = app["manifest"]["distribution"]
    if "platforms" not in dist:
        return app["release"]["assets"]
    return [a for a in app["release"]["assets"] if f"{a['os']}-{a['arch']}" in dist["platforms"]]


def downloads(app: dict) -> dict[str, list[dict]]:
    """The recommended installer per system and architecture, grouped by system, for the buttons.
    {"windows": [{"label", "arch", "url", "size", "ext"}], "macos": [...], "linux": [...]}"""
    out: dict[str, list[dict]] = {system: [] for system in SYSTEMS}   # every system is present, possibly empty
    for a in offered_assets(app):
        if a["primary"]:
            out[a["os"]].append({"label": SYSTEM_LABELS[(a["os"], a["arch"])], "arch": a["arch"], "url": a["url"], "size": a["size"], "ext": a["ext"]})
    return out


def search_text(app: dict) -> str:
    """Lower-case text the live filter searches: what the card shows (name, summary, kind, ways to get it, programs) and the longer description and categories."""
    m = app["manifest"]
    shown = [m["name"], m["summary"], KINDS[m["kind"]], *optional_list(m, "inputs"), *optional_list(m, "outputs"), *(ROUTES[r] + " " + ROUTE_LABELS[r] for r in routes(app)), *(HOSTS[h] for h in optional_list(m, "hosts") if h in HOSTS)]
    return " ".join([*shown, m["description"] if "description" in m else "", *optional_list(m, "categories")]).lower()


def card(app: dict) -> str:
    """One app card for the App Centre grid and the home page."""
    m, slug = app["manifest"], app["slug"]
    attrs = (f'data-kind="{esc(m["kind"])}" data-routes="{" ".join(routes(app))}" '
             f'data-hosts="{" ".join(optional_list(m, "hosts"))}" data-search="{esc(search_text(app))}"')
    return (f'<li class="lc-card" {attrs}><a class="lc-card__main" href="apps/{slug}/">'
            f'<span class="lc-card__head">{icon(app)}<span class="lc-card__title"><strong>{esc(m["name"])}</strong>'
            f'<small>{KINDS[m["kind"]]}</small></span></span><span class="lc-card__text">{esc(m["summary"])}</span>'
            f'<span class="lc-card__badges">{testing_badge(app)}{route_badges(app)}{host_chips(app)}</span>'
            f'<span class="lc-card__foot lc-card__foot--in">{release_line(app)}</span></a></li>')
