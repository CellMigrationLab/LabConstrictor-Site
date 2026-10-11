"""Release assets: which files are LabConstrictor installers, and for which system."""

import re

from .config import AppProblem

INSTALLER = re.compile(
    r"^(?P<project>.+)-(?P<version>[^-]+)-(?P<os>Windows|Linux|MacOSX)-(?P<arch>x86_64|arm64)\.(?P<ext>exe|msi|pkg|sh)$")
OS_NAMES = {"Windows": "windows", "Linux": "linux", "MacOSX": "macos"}
PREFERRED = {"windows": "exe", "macos": "pkg", "linux": "sh"}   # the graphical or simplest route per system
IMAGE_SIGNATURES = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"GIF87a", b"GIF89a")


def download_prefix(repo: str, tag: str) -> str:
    """The only address installers may be downloaded from: this repo's release `tag`."""
    return f"https://github.com/{repo}/releases/download/{tag}/"


def sha256_of(raw: dict) -> str | None:
    """The SHA-256 digest GitHub lists for a release asset ("sha256:<hex>"), or None when GitHub gives none (older releases)."""
    digest = raw["digest"] if "digest" in raw and raw["digest"] else ""
    return digest.removeprefix("sha256:") if digest.startswith("sha256:") else None


def parse_asset(repo: str, tag: str, raw: dict) -> dict | None:
    """One release asset as an installer record, or None when its name is not an installer
    (checksums and notes may sit beside installers). Raises AppProblem if the download
    address is not on github.com for this repo and tag."""
    m = INSTALLER.match(raw["name"])
    if not m:
        return None
    url = raw["browser_download_url"]
    if not url.lower().startswith(download_prefix(repo, tag).lower()):
        raise AppProblem(f"asset {raw['name']} is not served from {download_prefix(repo, tag)}")
    system = OS_NAMES[m["os"]]
    return {"name": raw["name"], "os": system, "arch": m["arch"], "ext": m["ext"], "size": raw["size"],
            "url": url, "primary": m["ext"] == PREFERRED[system], "sha256": sha256_of(raw)}


def parse_assets(repo: str, tag: str, raws: list[dict]) -> list[dict]:
    """Every installer among a release's assets, sorted by system, architecture, then format."""
    parsed = [a for a in (parse_asset(repo, tag, r) for r in raws) if a]
    return sorted(parsed, key=lambda a: (a["os"], a["arch"], not a["primary"], a["ext"]))


def check_image(data: bytes, limit: int, where: str) -> None:
    """Raise AppProblem unless `data` is a PNG, JPEG or GIF within `limit` bytes (SVG is refused: it can carry scripts)."""
    if len(data) > limit:
        raise AppProblem(f"{where} is {len(data) // 1024} KB; the limit is {limit // 1024} KB")
    if not data.startswith(IMAGE_SIGNATURES):
        raise AppProblem(f"{where} is not a PNG, JPEG or GIF image")
