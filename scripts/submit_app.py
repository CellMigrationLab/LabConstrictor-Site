"""Check an app submission (a GitHub issue) and, when it passes, write its registry entry.

    ISSUE_BODY="..." python scripts/submit_app.py

Reads the issue text from the ISSUE_BODY environment variable (never from the command line or a
shell), finds the repository named in it, runs the same checks the site build runs, and writes
build/submission.md (the comment to post). Exit status: 0 = passed and registry/<owner>__<repo>.yaml
written, 1 = not ready (the comment says what to fix). The submitted code is never checked out or run.
"""

import os
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from lcsite import catalogue, registry
from lcsite.config import BUILD, REGISTRY, AppProblem
from lcsite.github import GitHub
from lcsite.text import one_line

FIELD = re.compile(r"###\s*Repository\s+(\S+)")
REPO = re.compile(r"^(?:https://github\.com/)?(?!\.+/)([A-Za-z0-9_.-]+)/(?!\.+(?:/|$))([A-Za-z0-9_.-]+?)(?:\.git)?/?$")


def code(text: str) -> str:
    """Untrusted text made safe inside an inline code span of a comment (no backticks or line breaks, so no @mentions or links)."""
    return one_line(text).replace("`", "'")


def parse_repo(body: str) -> str:
    """"owner/name" from the issue form's Repository field (a GitHub address or owner/name). Raises AppProblem."""
    m = FIELD.search(body)
    found = REPO.match(m.group(1)) if m else None
    if not found:
        raise AppProblem("The Repository field must hold a GitHub address such as https://github.com/owner/name")
    return f"{found.group(1)}/{found.group(2)}"


def new_entry(repo: dict, today: str) -> dict:
    """The registry entry for a repository: ids are recorded so a later owner change is noticed."""
    return {"repo": repo["full_name"], "repo_id": repo["id"], "owner_id": repo["owner"]["id"], "added": today}


def check(body: str, gh: GitHub, today: str) -> tuple[dict | None, list[str]]:
    """(registry entry or None, report lines). The entry is returned only when every check passed."""
    try:
        name = parse_repo(body)
        if any(e["repo"].lower() == name.lower() for e in registry.load_all()):
            raise AppProblem(f"{name} is already in the registry")
        entry = new_entry(gh.repo(name), today)
        app = catalogue.resolve(entry, gh, None)
    except AppProblem as err:
        return None, [f"- ✘ {one_line(err)}"]
    lines = [f"- ✔ `{code(app['manifest']['name'])}`: manifest is valid", f"- ✔ latest release: {app['release']['tag'] if app['release'] else 'none (Colab or pip only)'}"]
    lines += [f"- ⚠ {one_line(w)}" for w in app["warnings"]]
    return entry, lines


def main() -> int:
    """Run the checks on $ISSUE_BODY, write the comment and, on success, the registry file."""
    body = os.environ.get("ISSUE_BODY")
    if not body:
        print("ISSUE_BODY is not set", file=sys.stderr)
        return 2
    entry, lines = check(body, GitHub(), date.today().isoformat())
    verdict = ("All checks passed. A pull request adds your app to the registry; a maintainer will review it."
               if entry else "Not ready yet. Fix the points marked ✘, then edit this issue to run the checks again.")
    BUILD.mkdir(exist_ok=True)
    (BUILD / "submission.md").write_text("\n".join(["### Submission checks", "", *lines, "", verdict, ""]), encoding="utf-8")
    if entry:
        (REGISTRY / registry.expected_name(entry["repo"])).write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    return 0 if entry else 1


if __name__ == "__main__":
    raise SystemExit(main())
