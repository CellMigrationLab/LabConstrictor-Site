"""Download the guides and pictures that live in other repositories into build/sources/ (a network step, like fetch_catalogue.py).

    python scripts/fetch_guides.py [--ref BRANCH]

Reads the `repo` / `path` entries of data/guides.yaml (guides) and data/hubs.yaml (pictures). By default each file is read from the repository's
default branch (HEAD). --ref reads another branch or tag from every repository (to preview a change before it is merged).
A file that does not exist stops with its repository and path (exit 1); a GitHub outage stops with status 4.
"""

import argparse
import sys

from lcsite import hubs, projects, sources
from lcsite.config import DATA, FetchError, load_yaml
from lcsite.github import MAX_TEXT, GitHub


def entries() -> list[dict]:
    """Everything kept in other repositories: the guides of data/guides.yaml, the pictures of data/hubs.yaml and the project files of data/ecosystem.yaml."""
    guides = [{"repo": g["repo"], "path": g["path"], "limit": MAX_TEXT}
              for s in load_yaml(DATA / "guides.yaml")["sections"] for g in s["items"] if "repo" in g]
    return guides + hubs.image_sources(load_yaml(DATA / "hubs.yaml")) + projects.fetch_entries(load_yaml(DATA / "ecosystem.yaml"))


def main() -> int:
    """Fetch every listed guide. Returns the exit status."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--ref", default="HEAD", help="branch or tag to read in every repository (default: HEAD)")
    args = parser.parse_args()
    listed = entries()
    try:
        sources.fetch(listed, GitHub(), args.ref)
    except FetchError as err:
        print(f"GitHub could not be read: {err}", file=sys.stderr)
        return 4
    print(f"Fetched {len(listed)} files from {len({e['repo'] for e in listed})} repositories (ref {args.ref}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
