"""The Ecosystem page: each project describes itself in its own repository (docs/labconstrictor-project.yaml).

data/ecosystem.yaml only says which repositories to list and under which heading; adding a project is adding one
`- repo: owner/name` line. The files are downloaded by scripts/fetch_guides.py and checked against
schema/labconstrictor-project.schema.json; anything missing or invalid stops the build.
The one exception is a project whose repository is copied into every app (the template): its card is written
inline in data/ecosystem.yaml, with `name`, `text` and `status` next to `repo`.
"""

from typing import Any

from . import sources
from .config import DATA, fail, load_yaml
from .github import MAX_TEXT
from .validate import AppProblem, check, load_plain_yaml

PROJECT_FILE = "docs/labconstrictor-project.yaml"
PROJECT_SCHEMA = "labconstrictor-project.schema.json"
INLINE_KEYS = {"repo", "name", "text", "status"}


def listed_repos(ecosystem: dict) -> list[str]:
    """The repositories whose project file the site must download (inline cards have none)."""
    return [i["repo"] for t in ecosystem["tiers"] for i in t["items"] if "name" not in i]


def fetch_entries(ecosystem: dict) -> list[dict]:
    """The files for scripts/fetch_guides.py to download: {repo, path, limit}."""
    return [{"repo": r, "path": PROJECT_FILE, "limit": MAX_TEXT} for r in listed_repos(ecosystem)]


def load_project(repo: str) -> dict[str, Any]:
    """A repository's validated project file. Stops the build, naming the repository, when it is invalid."""
    where = f"{repo}/{PROJECT_FILE}"
    try:
        data = load_plain_yaml(sources.read(repo, PROJECT_FILE), where)
        check(data, PROJECT_SCHEMA, where)
    except AppProblem as err:
        fail(str(err))
    return data


def inline_card(item: dict) -> dict[str, Any]:
    """A card written in data/ecosystem.yaml. Stops the build when a key is missing or unknown."""
    if set(item) != INLINE_KEYS:
        fail(f"data/ecosystem.yaml: an inline card needs exactly {sorted(INLINE_KEYS)}, got {sorted(item)}")
    return {"name": item["name"], "summary": item["text"], "status": item["status"]}


def guide_slugs() -> dict[str, str]:
    """repository -> the slug of the guide kept in it (data/guides.yaml), to link each card to its guide."""
    sections = load_yaml(DATA / "guides.yaml")["sections"]
    return {g["repo"]: g["slug"] for s in sections for g in s["items"] if "repo" in g}


def resolve(ecosystem: dict) -> list[dict]:
    """The tiers with every card resolved to name, summary, status, link and (when the repository has one) guide slug."""
    slugs = guide_slugs()
    tiers = []
    for tier in ecosystem["tiers"]:
        cards = []
        for item in tier["items"]:
            data = inline_card(item) if "name" in item else load_project(item["repo"])
            link = data["url"] if "url" in data else f"https://github.com/{item['repo']}"
            cards.append(dict(data, link=link, guide=slugs[item["repo"]] if item["repo"] in slugs else None))
        tiers.append({"key": tier["key"], "title": tier["title"], "text": tier["text"], "cards": cards})
    return tiers
