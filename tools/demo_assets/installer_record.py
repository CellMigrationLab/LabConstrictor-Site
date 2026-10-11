"""Write content/demo/installer.json: the Windows installer example the demo's Install part shows (name, version, installer file and size of one NucleiSky release).

Usage (offline; reads build/snapshot.json written by scripts/fetch_catalogue.py, runs nothing else):
    python tools/demo_assets/installer_record.py [--snapshot build/snapshot.json]

The site build reads only the stored file, so it never depends on NucleiSky's current release.
"""

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "content" / "demo" / "installer.json"
SLUG = "nucleisky"


def build_record(snapshot: dict, today: str) -> dict:
    """The record for the NucleiSky app in the snapshot: its name, the release tag, the Windows .exe and its size; stops naming what is missing."""
    app = next((a for a in snapshot["apps"] if a["slug"] == SLUG), None)
    if app is None or app["release"] is None:
        raise SystemExit(f"the snapshot has no {SLUG} app with a release")
    exe = next((x for x in app["release"]["assets"] if x["os"] == "windows" and x["name"].endswith(".exe")), None)
    if exe is None:
        raise SystemExit(f"the latest {SLUG} release has no Windows .exe installer")
    return {"app_name": app["manifest"]["name"], "app_version": app["release"]["tag"], "exe_name": exe["name"], "exe_size_bytes": exe["size"],
            "source": {"repo": "CellMigrationLab/NucleiSky", "release_url": app["release"]["url"], "recorded": today}}


def main() -> None:
    """Read the snapshot and write the record."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--snapshot", default=str(ROOT / "build" / "snapshot.json"))
    args = p.parse_args()
    record = build_record(json.loads(Path(args.snapshot).read_text(encoding="utf-8")), date.today().isoformat())
    OUT.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
