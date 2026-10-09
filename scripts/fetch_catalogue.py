"""Resolve the registry into build/snapshot.json (the only step that uses the network).

    python scripts/fetch_catalogue.py [--strict] [--manifest-dir seed/manifests]

Reads registry/*.yaml, each app's labconstrictor-app.yaml and latest GitHub release.
Writes build/snapshot.json, build/problems.md and build/media/<app>/ (icons, screenshots).
Apps that cannot be resolved are left out and listed in problems.md; --strict makes the
command exit with status 3 when there are any (use it in pull-request checks).
--manifest-dir previews manifests that are not yet in the app repositories (development only).
"""

import argparse
import sys
from pathlib import Path

from lcsite import catalogue, registry
from lcsite.github import GitHub


def main() -> int:
    """Fetch, write the snapshot, print what was left out. Returns the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="exit 3 if any app could not be resolved")
    parser.add_argument("--manifest-dir", type=Path, help="development only: read manifests from this folder")
    args = parser.parse_args()
    if args.manifest_dir:
        print(f"NOTE: manifests are read from {args.manifest_dir}, not from the app repositories")
    snapshot = catalogue.build(registry.load_all(), GitHub(), args.manifest_dir)
    catalogue.write(snapshot)
    print(f"Resolved {len(snapshot['apps'])} apps; {len(snapshot['problems'])} left out.")
    for problem in snapshot["problems"]:
        print(f"  PROBLEM {problem}", file=sys.stderr)
    for warning in snapshot["warnings"]:
        print(f"  WARNING {warning}", file=sys.stderr)
    return 3 if args.strict and snapshot["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
