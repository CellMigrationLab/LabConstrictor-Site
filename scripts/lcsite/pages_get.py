"""The parts of an app page about getting and using it: download tiles, notebooks, the pip route, first steps and the table of all downloads."""

import re

from . import hosts
from .cards import CHIPS, SYSTEM_LABELS, SYSTEMS, downloads, offered_assets, release_line
from .text import esc, long_date, megabytes
from .validate import optional_list

def steps_link(system: str, label: str) -> str:
    """A link to the install guide's section for one system (the guide's own headings are Windows, macOS and Linux)."""
    return f'<a href="guides/install/#{system}">{label}</a>'


HINTS = {
    "windows": f"Installers built with LabConstrictor are not code-signed yet, so Windows may warn you. Run files only from this app's GitHub release. See the {steps_link('windows', 'Windows steps')}.",
    "macos": f"Not sure which? Apple menu, About This Mac: Intel, or M1 and later (Apple Silicon). If macOS refuses to open it, see the {steps_link('macos', 'macOS steps')}.",
    "linux": f"Needs a terminal. Run it with: bash &lt;file name&gt;. See the {steps_link('linux', 'Linux steps')}.",
}
COLAB_FILE = re.compile(r"^https://colab\.research\.google\.com/github/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$")
COLAB_NOTE = ("These run on Google's servers in Google Colab: you need an internet connection and a Google account, and any data you load into "
              "the notebook is handled by Google.")
DESKTOP_NOTE = " The desktop app runs on your computer."


def os_button(option: dict, system: str, first: bool, several: bool) -> str:
    """One download button inside a system tile: macOS buttons are named by chip, others by system (and architecture when the system has several)."""
    name = CHIPS[option["arch"]] if system == "macos" else f"{SYSTEM_LABELS[(system, option['arch'])]} installer" if several else f"{SYSTEMS[system]} installer"
    emphasised = first and system != "macos"   # a Mac's chip is unknown until lc.js detects it: both buttons look the same
    return (f'<a class="lc-btn{"" if emphasised else " lc-btn--ghost"}" href="{esc(option["url"])}" data-arch="{option["arch"]}">'
            f'{esc(name)}<small>{megabytes(option["size"])} · .{option["ext"]}</small></a>')


def intel_note(app: dict) -> str:
    """"Intel Macs: not supported..." when the manifest lists Apple Silicon but not Intel (distribution.platforms); "" otherwise."""
    platforms = app["manifest"]["distribution"]["platforms"] if "platforms" in app["manifest"]["distribution"] else []
    unsupported = "macos-arm64" in platforms and "macos-x86_64" not in platforms
    return '<p class="lc-small">Intel Macs: not supported by this app\'s authors.</p>' if unsupported else ""


def empty_text(app: dict, system: str) -> str:
    """Why a tile has no download: the authors do not offer that system (distribution.platforms), or the release has no installer for it."""
    dist = app["manifest"]["distribution"]
    listed = [p for p in (dist["platforms"] if "platforms" in dist else []) if p.startswith(system + "-")]
    return "No installer in this release." if "platforms" not in dist or listed else "Not offered by this app's authors."


def os_tile(system: str, options: list[dict], extra: str = "", empty: str = "No installer in this release.") -> str:
    """The tile for one system: its download buttons and hints, or the reason there are none (never hidden; no hint without a download)."""
    several = len({o["arch"] for o in options}) > 1
    body = "".join(os_button(o, system, i == 0, several) for i, o in enumerate(options)) if options else f'<p class="lc-small">{esc(empty)}</p>'
    hint = f'<p class="lc-small">{HINTS[system]}</p>' if options else ""
    arches = " ".join(sorted({o["arch"] for o in options}))
    return f'<div class="lc-ostile" data-os="{system}" data-arches="{arches}"><h3>{SYSTEMS[system]}</h3>{body}{extra}{hint}</div>'


def github_view(colab_url: str) -> str:
    """The GitHub address of the notebook behind a Colab link (colab.research.google.com/github/o/r/blob/branch/path), or "" when the link is of another kind
    or climbs out of the repository with ".."."""
    m = COLAB_FILE.match(colab_url)
    if not m or ".." in colab_url.split("/"):
        return ""
    return f"https://github.com/{m.group(1)}/{m.group(2)}/blob/{m.group(3)}/{m.group(4)}"


def notebook_row(link: dict) -> str:
    """One notebook the author chose to show: its name, "Open in Colab" with the logo, and "View on GitHub" when the link says where the file is."""
    view = github_view(link["url"])
    source = f'<a href="{esc(view)}">View on GitHub</a>' if view else ""
    return (f'<li><span class="lc-notebooks__name">{esc(link["label"])}</span>'
            f'<a class="lc-btn lc-btn--ghost lc-btn--small" href="{esc(link["url"])}">{hosts.service_logo("colab")}Open in Colab</a>{source}</li>')


def notebooks_list(links: list[dict], desktop: bool) -> str:
    """The notebooks listed in the manifest (`distribution.colab`) and one sentence about the service (with a line about the desktop app only when there is one)."""
    return ('<h3 id="notebooks">Notebooks to open in your browser</h3><ul class="lc-notebooks">' + "".join(notebook_row(l) for l in links)
            + f'</ul><p class="lc-small">{COLAB_NOTE}{DESKTOP_NOTE if desktop else ""}</p>')


def pip_block(package: str) -> str:
    """The pip route, labelled as the advanced one, with the exact command and where the package lives."""
    return ('<h3 id="pip">Python package (advanced)</h3>'
            f'<div class="lc-code"><code>pip install {esc(package)}</code><button type="button" class="lc-btn lc-btn--ghost lc-btn--small" data-copy>Copy</button></div>'
            f'<p class="lc-small">The package named by the author on PyPI (<a href="https://pypi.org/project/{esc(package)}/">pypi.org/project/{esc(package)}</a>); '
            'its version may differ from the desktop app.</p>')


def get_section(app: dict) -> str:
    """The "Get it" block: the version line, a download tile per system, the Colab notebooks and the pip command."""
    dist = app["manifest"]["distribution"]
    parts = ['<h2 id="get">Get it</h2>']
    if app["release"] and dist.get("installer"):
        have = downloads(app)
        parts.append(f'<p class="lc-small">{release_line(app)} · files come from github.com/{esc(app["repo"])}/releases</p>')
        parts.append('<div class="lc-osgrid" data-lc-osgrid>' + "".join(os_tile(k, have[k], intel_note(app) if k == "macos" else "", empty_text(app, k)) for k in SYSTEMS) + "</div>")
        colab = " You can also open a notebook in Colab below." if optional_list(dist, "colab") else ""
        parts.append(f'<p class="lc-small" data-lc-nosystem hidden>These installers are for Windows, macOS and Linux computers.{colab}</p>')
    if optional_list(dist, "colab"):
        parts.append(notebooks_list(optional_list(dist, "colab"), bool(dist.get("installer"))))
    if dist.get("pip"):
        parts.append(pip_block(dist["pip"]))
    return "\n".join(parts)


def using_section(app: dict) -> str:
    """"Using it": the manifest's quick start (or a line saying there is none), how a desktop app starts, and the documentation link
    (the manifest's docs_url, else the README on GitHub; the label says which)."""
    m = app["manifest"]
    parts = ['<h2 id="use">Using it</h2>']
    parts.append("<ol>" + "".join(f"<li>{esc(step)}</li>" for step in m["quickstart"]) + "</ol>" if "quickstart" in m
                 else '<p>The authors have not given first-run steps.</p>')
    if m["distribution"].get("installer"):
        parts.append('<p><strong>For any LabConstrictor desktop app:</strong> after installing, open the app from your Start Menu or Applications folder. '
                     'Its Welcome notebook lists the app&#39;s notebooks; the <a href="guides/notebook-usage/">notebook usage guide</a> shows how to work with it.</p>')
    docs, label = (m["docs_url"], "Documentation") if m.get("docs_url") else (app["html_url"] + "#readme", "README on GitHub")
    parts.append(f'<p>Read more: <a href="{esc(docs)}">{label}</a>.</p>')
    return "\n".join(parts)


def asset_row(a: dict) -> str:
    """One row of the table of all downloads: system, format, size, file and its SHA-256 (or "not published")."""
    digest = f'<code class="lc-hash" data-search-exclude>{esc(a["sha256"])}</code>' if a["sha256"] else "not published"
    return (f'<tr><td>{SYSTEM_LABELS[(a["os"], a["arch"])]}</td><td>.{a["ext"]}</td><td>{megabytes(a["size"])}</td>'
            f'<td><a href="{esc(a["url"])}">{esc(a["name"])}</a></td><td>{digest}</td></tr>')


def downloads_table(app: dict) -> str:
    """Every installer the app offers from its latest release: system, format, size, direct link and checksum."""
    rows = "".join(asset_row(a) for a in offered_assets(app))
    return (f'<h2 id="downloads">All downloads</h2><p class="lc-small">Version {esc(app["release"]["tag"])}, '
            f'released {long_date(app["release"]["published_at"])}. Files come straight from the app\'s '
            f'<a href="{esc(app["release"]["url"])}">GitHub release</a>.</p>'
            '<div class="lc-scroll"><table class="lc-table"><caption class="lc-sr">Installers of the latest release</caption><thead><tr><th>System</th><th>Format</th><th>Size</th><th>File</th><th>SHA-256 (from GitHub)</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def install_help() -> str:
    """"How to install": a pointer to the install guide (the template's page, imported by the site), so the steps are written once."""
    return ('<h2 id="install">How to install</h2><p>Step by step for Windows, macOS and Linux, with the pictures: '
            '<a href="guides/install/">Install an app</a>.</p>')
