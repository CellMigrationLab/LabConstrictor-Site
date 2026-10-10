"""HTML snippets shared by several pages: app cards, badges and download data."""

from . import hosts
from .text import esc, long_date
from .validate import optional_list

KINDS = {"analysis": "Analysis", "segmentation": "Segmentation", "simulation": "Simulation",
         "game": "Game", "training": "Training", "utility": "Utility"}
HOSTS = {"notebook": "Notebook", "napari": "napari", "fiji": "Fiji", "qupath": "QuPath"}
ROUTES = {"installer": "Desktop", "colab": "Colab", "pip": "pip"}
SYSTEM_LABELS = {("windows", "x86_64"): "Windows", ("macos", "arm64"): "macOS (Apple Silicon)",
                 ("macos", "x86_64"): "macOS (Intel)", ("linux", "x86_64"): "Linux"}
SYSTEMS = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}   # one download tile each, in this order
CHIPS = {"arm64": "Apple Silicon (M1 or later)", "x86_64": "Intel"}     # macOS buttons are named by chip


def routes(app: dict) -> list[str]:
    """Route keys ("installer", "colab", "pip") the manifest offers, in display order."""
    dist = app["manifest"]["distribution"]
    return [r for r in ROUTES if dist.get(r)]


def is_verified(app: dict) -> bool:
    """True when a maintainer verified exactly the version that is now the latest release."""
    release = app["release"]
    return bool(app["verified_version"] and release and release["tag"] == app["verified_version"])


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


def tier_badge(app: dict) -> str:
    """"Verified" only when it applies to the latest release; every other app is "Community"."""
    return badge("Verified", "verified") if is_verified(app) else badge("Community")


def host_badge(key: str) -> str:
    """"Soon in napari" with the program's logo, linked to our guide for it."""
    return (f'<a class="lc-badge lc-badge--host" href="{esc(HOST_GUIDES[key])}">{hosts.logo(key)}'
            f'<span>Soon in {esc(HOSTS[key])}</span></a>')


def testing_badge(app: dict) -> str:
    """"Testing" for apps that check or maintain LabConstrictor itself (registry `section: testing`); nothing for the others."""
    return badge("Testing", "testing") if app["section"] == "testing" else ""


def route_badges(app: dict) -> str:
    """One badge per way to get the app (Desktop, Colab, pip)."""
    return "".join(badge(ROUTES[r]) for r in routes(app))


def icon(app: dict, size: int = 48) -> str:
    """The app's icon at `size` px, or a monogram tile when the manifest names none (icon is optional)."""
    if app["icon"]:
        return f'<img class="lc-icon" src="assets/icons/{esc(app["slug"])}.png" alt="" width="{size}" height="{size}" loading="lazy">'
    return f'<span class="lc-icon lc-icon--mono" style="--size:{size}px" aria-hidden="true">{esc(app["manifest"]["name"][0].upper())}</span>'


def release_line(app: dict) -> str:
    """"v0.1.5 · 8 October 2026", or "No release yet" for an app that has none (pip or Colab only)."""
    release = app["release"]
    return f'v{esc(release["tag"])} · {long_date(release["published_at"])}' if release else "No release yet"


def downloads(app: dict) -> dict[str, list[dict]]:
    """The recommended installer per system and architecture, grouped by system, for the buttons.
    {"windows": [{"label", "arch", "url", "size", "ext"}], "macos": [...], "linux": [...]}"""
    out: dict[str, list[dict]] = {system: [] for system in SYSTEMS}   # every system is present, possibly empty
    if app["release"] is None:
        return out   # an app without a release (Colab or pip only) has no installers
    for a in app["release"]["assets"]:
        if a["primary"]:
            label = SYSTEM_LABELS[(a["os"], a["arch"])]
            out[a["os"]].append({"label": label, "arch": a["arch"], "url": a["url"], "size": a["size"], "ext": a["ext"]})
    return out


def search_text(app: dict) -> str:
    """Lower-case text the live filter searches: name, summary and categories."""
    m = app["manifest"]
    return " ".join([m["name"], m["summary"], *optional_list(m, "categories")]).lower()


def card(app: dict) -> str:
    """One app card for the App Centre grid and the home page."""
    m, slug = app["manifest"], app["slug"]
    attrs = (f'data-kind="{esc(m["kind"])}" data-routes="{" ".join(routes(app))}" '
             f'data-hosts="{" ".join(optional_list(m, "hosts"))}" data-search="{esc(search_text(app))}"')
    return (f'<li class="lc-card" {attrs}><a class="lc-card__main" href="apps/{slug}/">'
            f'<span class="lc-card__head">{icon(app)}<span class="lc-card__title"><strong>{esc(m["name"])}</strong>'
            f'<small>{KINDS[m["kind"]]}</small></span></span><span class="lc-card__text">{esc(m["summary"])}</span>'
            f'<span class="lc-card__badges">{tier_badge(app)}{testing_badge(app)}{route_badges(app)}</span>'
            f'<span class="lc-card__foot lc-card__foot--in">{release_line(app)}</span></a></li>')
