"""Write content/demo/installer.json: the installer example the demo's Install part shows (name, version, the Windows .exe and the macOS Apple-silicon .pkg
with their sizes, and the disk space the .pkg asks for, all of one NucleiSky release).

Usage (offline; reads build/snapshot.json written by scripts/fetch_catalogue.py, runs nothing else):
    python tools/demo_assets/installer_record.py --pkg-install-kbytes N [--snapshot build/snapshot.json]

N is the `installKBytes` of the .pkg's `Distribution` file (the disk space the macOS Installer announces). The snapshot does not hold it: read it from the
package itself (a .pkg is a xar archive; its table of contents lists `Distribution`, a small XML file), for the release the snapshot names.

The site build reads only the stored file, so it never depends on NucleiSky's current release.
"""

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "content" / "demo" / "installer.json"
SLUG = "nucleisky"


def find_installer(assets: list[dict], os_name: str, extension: str, arch: str | None) -> dict:
    """The one release asset for a system, file extension and (when `arch` is given) chip; raises SystemExit naming what is missing."""
    found = [a for a in assets if a["os"] == os_name and a["name"].endswith(extension) and (arch is None or a["arch"] == arch)]
    if len(found) != 1:
        raise SystemExit(f"expected one {os_name} {arch or ''} {extension} installer in the latest release, found {len(found)}")
    return found[0]


def build_record(snapshot: dict, today: str, pkg_install_kbytes: int) -> dict:
    """The record for the NucleiSky app in the snapshot: its name, the release tag, the Windows .exe and the macOS arm64 .pkg with their sizes,
    and the disk space the .pkg announces (`pkg_install_kbytes`, read from the package); stops naming what is missing."""
    app = next((a for a in snapshot["apps"] if a["slug"] == SLUG), None)
    if app is None or app["release"] is None:
        raise SystemExit(f"the snapshot has no {SLUG} app with a release")
    exe = find_installer(app["release"]["assets"], "windows", ".exe", None)
    pkg = find_installer(app["release"]["assets"], "macos", ".pkg", "arm64")
    if pkg_install_kbytes <= 0:
        raise SystemExit("--pkg-install-kbytes must be a positive number")
    return {"app_name": app["manifest"]["name"], "app_version": app["release"]["tag"], "exe_name": exe["name"], "exe_size_bytes": exe["size"],
            "pkg_name": pkg["name"], "pkg_size_bytes": pkg["size"], "pkg_install_kbytes": pkg_install_kbytes,
            "source": {"repo": "CellMigrationLab/NucleiSky", "release_url": app["release"]["url"], "recorded": today,
                       "pkg_install_kbytes_from": "installKBytes of the package's Distribution file"}}


def main() -> None:
    """Read the snapshot and write the record."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--snapshot", default=str(ROOT / "build" / "snapshot.json"))
    p.add_argument("--pkg-install-kbytes", type=int, required=True, help="installKBytes of the .pkg's Distribution file")
    args = p.parse_args()
    record = build_record(json.loads(Path(args.snapshot).read_text(encoding="utf-8")), date.today().isoformat(), args.pkg_install_kbytes)
    OUT.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
