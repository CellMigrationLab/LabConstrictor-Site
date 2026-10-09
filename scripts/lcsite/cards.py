"""HTML snippets shared by several pages: app cards, badges and download data."""

from .text import esc, long_date

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


def badge(text: str, kind: str = "") -> str:
    """A small pill; `kind` adds a colour class (lc-badge--<kind>)."""
    return f'<span class="lc-badge{f" lc-badge--{kind}" if kind else ""}">{esc(text)}</span>'


def tier_badge(app: dict) -> str:
    """"Verified" only when it applies to the latest release; every other app is "Community"."""
    return badge("Verified", "verified") if is_verified(app) else badge("Community")


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
    out: dict[str, list[dict]] = {}
    for a in (app["release"] or {"assets": []})["assets"]:
        if a["primary"]:
            label = SYSTEM_LABELS[(a["os"], a["arch"])]
            out.setdefault(a["os"], []).append({"label": label, "arch": a["arch"], "url": a["url"], "size": a["size"], "ext": a["ext"]})
    return out


def search_text(app: dict) -> str:
    """Lower-case text the live filter searches: name, summary and categories."""
    m = app["manifest"]
    return " ".join([m["name"], m["summary"], *m.get("categories", [])]).lower()


def card(app: dict) -> str:
    """One app card for the App Centre grid and the home page."""
    m, slug = app["manifest"], app["slug"]
    attrs = (f'data-kind="{esc(m["kind"])}" data-routes="{" ".join(routes(app))}" '
             f'data-hosts="{" ".join(m.get("hosts", []))}" data-search="{esc(search_text(app))}"')
    get = f'<a class="lc-card__get" href="apps/{slug}/#get">Get</a>' if routes(app) else ""
    return (f'<li class="lc-card" {attrs}><a class="lc-card__main" href="apps/{slug}/">'
            f'<span class="lc-card__head">{icon(app)}<span class="lc-card__title"><strong>{esc(m["name"])}</strong>'
            f'<small>{KINDS[m["kind"]]}</small></span></span><span class="lc-card__text">{esc(m["summary"])}</span>'
            f'<span class="lc-card__badges">{tier_badge(app)}{route_badges(app)}</span></a>'
            f'<div class="lc-card__foot"><span>{release_line(app)}</span>{get}</div></li>')
