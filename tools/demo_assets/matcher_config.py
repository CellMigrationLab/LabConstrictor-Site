"""Write content/demo/matcher_config.json: the default matcher settings the NucleiSky 2D notebook shows in Option A.

Usage (offline; reads one stdlib-only file of the NucleiSky source, runs nothing else):
    python tools/demo_assets/matcher_config.py --nucleisky-src <NucleiSky>/src --nucleisky-commit <sha>
"""

import argparse
import importlib.util
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "content" / "demo" / "matcher_config.json"
SECTIONS = ("_common", "graph", "quad", "triangles", "hashing")   # the order of the notebook's tabs


def load_defaults(src: Path) -> dict:
    """DEFAULT_MATCHER_CONFIG from nucleisky/nucleisky2d/config.py, loaded as a plain file (it imports only the standard library)."""
    path = src / "nucleisky" / "nucleisky2d" / "config.py"
    if not path.is_file():
        raise SystemExit(f"{path} is missing")
    spec = importlib.util.spec_from_file_location("nucleisky_config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.DEFAULT_MATCHER_CONFIG


def build_record(defaults: dict, commit: str) -> dict:
    """The settings of each tab with the keys sorted, as the notebook lists them; a section the notebook shows but the file lacks stops the run."""
    missing = [s for s in SECTIONS if s not in defaults]
    if missing:
        raise SystemExit(f"config.py has no section {missing}")
    return {"source": {"nucleisky_commit": commit, "file": "src/nucleisky/nucleisky2d/config.py", "name": "DEFAULT_MATCHER_CONFIG"},
            "sections": {s: {k: defaults[s][k] for k in sorted(defaults[s])} for s in SECTIONS}}


def main() -> None:
    """Read the defaults and write the JSON record."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nucleisky-src", required=True)
    p.add_argument("--nucleisky-commit", required=True)
    args = p.parse_args()
    record = build_record(load_defaults(Path(args.nucleisky_src)), args.nucleisky_commit)
    OUT.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
