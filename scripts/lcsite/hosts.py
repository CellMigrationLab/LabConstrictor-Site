"""The programs LabConstrictor apps can run inside (napari, Fiji, QuPath): their logos and where each plugin lives.

data/hosts.yaml names them; the logos are downloaded by scripts/fetch_guides.py from the projects' own repositories and
shrunk into docs/assets/hosts/ by `prepare`. A missing or unreadable logo stops the build.
"""

import re
from pathlib import Path

from . import sources
from .config import DATA, DOCS, AppProblem, fail, load_yaml
from .github import MAX_FILE
from .images import shrink
from .text import esc

LOGO_PX = 64
FOLDER = DOCS / "assets" / "hosts"


def load() -> dict[str, dict]:
    """The hosts of data/hosts.yaml, keyed by their short name (which is also the slug of their guide)."""
    return load_yaml(DATA / "hosts.yaml")["hosts"]


def load_services() -> dict[str, dict]:
    """The services of data/hosts.yaml (Google Colab), keyed by short name."""
    return load_yaml(DATA / "hosts.yaml")["services"]


def logo_sources(hosts: dict[str, dict]) -> list[dict]:
    """The logo files for scripts/fetch_guides.py to download: {repo, path, limit}, for the programs and the services."""
    every = list(hosts.values()) + list(load_services().values())
    return [{"repo": h["logo"]["repo"], "path": h["logo"]["path"], "limit": MAX_FILE} for h in every]


PATH_DATA = re.compile(r'<path d="([0-9A-Za-z\s.,\-]+)"\s*/>')


def svg_logo(text: str, color: str, where: str) -> str:
    """A safe SVG made from an icon collection's file: only its single path is kept (letters, numbers and path punctuation),
    in the given colour. Stops the build, naming `where`, when the file is not a one-path 24x24 icon."""
    paths = PATH_DATA.findall(text)
    if len(paths) != 1 or 'viewBox="0 0 24 24"' not in text:
        fail(f"{where} is not a one-path 24x24 SVG icon, so it cannot be used as a logo")
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="{esc(color)}" d="{paths[0]}"/></svg>\n'


def prepare(hosts: dict[str, dict]) -> None:
    """Shrink every logo into docs/assets/hosts/<key>.png. Stops the build, naming the host, when one cannot be read."""
    for key, h in hosts.items():
        src = sources.local_path(h["logo"]["repo"], h["logo"]["path"])
        if not src.is_file():
            fail(f"data/hosts.yaml: the logo of {key} is missing ({src}): run scripts/fetch_guides.py")
        try:
            shrink(src, FOLDER / f"{key}.png", LOGO_PX, square=True)
        except AppProblem as err:
            fail(f"data/hosts.yaml: the logo of {key}: {err}")


def prepare_services() -> None:
    """Write docs/assets/hosts/<key>.svg for every service. Stops the build, naming the service, when a logo is missing or unsafe."""
    FOLDER.mkdir(parents=True, exist_ok=True)
    for key, h in load_services().items():
        src = sources.local_path(h["logo"]["repo"], h["logo"]["path"])
        if not src.is_file():
            fail(f"data/hosts.yaml: the logo of {key} is missing ({src}): run scripts/fetch_guides.py")
        (FOLDER / f"{key}.svg").write_text(svg_logo(src.read_text(encoding="utf-8"), h["color"], f"the logo of {key}"), encoding="utf-8")


def service_logo(key: str) -> str:
    """The <img> of a service's logo (decorative: its name is always written next to it)."""
    return f'<img class="lc-logo" src="assets/hosts/{esc(key)}.svg" alt="" width="18" height="18" loading="lazy">'


def logo(key: str) -> str:
    """The <img> of a host's logo (decorative: its name is always written next to it)."""
    return f'<img class="lc-logo" src="assets/hosts/{esc(key)}.png" alt="" width="18" height="18" loading="lazy">'


def pill(key: str, hosts: dict[str, dict], label: str = "") -> str:
    """The program pill: the program's logo and name, linked to the program's own website."""
    h = hosts[key]
    return f'<a class="lc-gh lc-gh--host" href="{esc(h["url"])}">{logo(key)}<span>{esc(label or h["name"])}</span></a>'


def host_of_plugin(repo: str, hosts: dict[str, dict]) -> str | None:
    """The host key of one of our plugin repositories (CellMigrationLab/LabConstrictor-napari -> napari), or None for any other repository."""
    return next((k for k, h in hosts.items() if h["plugin"] == repo), None)
