"""The programs LabConstrictor apps can run inside (napari, Fiji, QuPath): their logos and where each plugin lives.

data/hosts.yaml names them; the logos are downloaded by scripts/fetch_guides.py from the projects' own repositories and
shrunk into docs/assets/hosts/ by `prepare`. A missing or unreadable logo stops the build.
"""

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


def logo_sources(hosts: dict[str, dict]) -> list[dict]:
    """The logo files for scripts/fetch_guides.py to download: {repo, path, limit}."""
    return [{"repo": h["logo"]["repo"], "path": h["logo"]["path"], "limit": MAX_FILE} for h in hosts.values()]


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


def logo(key: str) -> str:
    """The <img> of a host's logo (decorative: its name is always written next to it)."""
    return f'<img class="lc-logo" src="assets/hosts/{esc(key)}.png" alt="" width="18" height="18" loading="lazy">'


def host_of_plugin(repo: str, hosts: dict[str, dict]) -> str | None:
    """The host key of one of our plugin repositories (CellMigrationLab/napari-labconstrictor -> napari), or None for any other repository."""
    return next((k for k, h in hosts.items() if h["plugin"] == repo), None)
