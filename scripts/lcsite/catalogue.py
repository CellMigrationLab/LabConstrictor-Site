"""Registry + each app's manifest + its latest release -> build/snapshot.json.

This is the only module that reads the network (through github.GitHub). The site
build reads the snapshot and never goes online. An app that cannot be resolved is
left out and named in build/problems.md; it never silently disappears and it
never stops the other apps. A GitHub outage (FetchError) is different: it stops the whole fetch, so
the live site is never rebuilt from a half-empty catalogue.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .assets import check_image, parse_assets
from .config import BUILD, MANIFEST_NAME, RESERVED_SLUGS, SNAPSHOT_FORMAT, AppProblem
from .github import MAX_FILE, GitHub
from .images import check_square
from .text import slugify
from .validate import MANIFEST_SCHEMA, check, load_plain_yaml, optional_list


def check_identity(entry: dict, repo: dict) -> None:
    """The repo must still be the one that was reviewed: same ids, public, not archived."""
    if repo["id"] != entry["repo_id"] or repo["owner"]["id"] != entry["owner_id"]:
        raise AppProblem("repository or owner id changed since it was registered: re-review before listing")
    if repo["archived"] or repo["private"]:
        raise AppProblem("repository is archived or private")


def read_manifest(gh: GitHub, name: str, branch: str, manifest_dir: Path | None) -> dict:
    """The app's labconstrictor-app.yaml, validated. `manifest_dir` (a development flag)
    reads <repo-name>.yaml from that folder instead, so a manifest can be previewed
    before it is committed to the app's repository."""
    try:
        if manifest_dir:
            text = (manifest_dir / f"{name.split('/')[1]}.yaml").read_text(encoding="utf-8")
        else:
            text = gh.raw(name, branch, MANIFEST_NAME).decode("utf-8")
    except (OSError, UnicodeDecodeError) as err:
        raise AppProblem(f"cannot read {MANIFEST_NAME}: {err}") from err
    manifest = load_plain_yaml(text, MANIFEST_NAME)
    check(manifest, MANIFEST_SCHEMA, MANIFEST_NAME)
    return manifest


def read_release(gh: GitHub, name: str, manifest: dict) -> dict | None:
    """The latest release with its installers. A release is required when the manifest
    claims installers; otherwise an app without one simply has no release (optional)."""
    claims = bool(manifest["distribution"].get("installer"))
    raw = gh.latest_release(name)
    if raw is None:
        if claims:
            raise AppProblem("manifest promises installers but the repository has no release")
        return None
    assets = parse_assets(name, raw["tag_name"], raw["assets"])
    if claims and not assets:
        raise AppProblem(f"manifest promises installers but release {raw['tag_name']} has none")
    return {"tag": raw["tag_name"], "published_at": raw["published_at"], "url": raw["html_url"], "assets": assets}


def save_image(gh: GitHub, name: str, branch: str, path: str, slug: str, stem: str) -> str:
    """Download an image named in the manifest into build/media/<slug>/; return its file name."""
    data = gh.raw(name, branch, path, limit=MAX_FILE)
    check_image(data, MAX_FILE, path)
    out = BUILD / "media" / slug / f"{stem}.{path.rsplit('.', 1)[1].lower()}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return out.name


def read_icon(gh: GitHub, name: str, branch: str, path: str, slug: str, warnings: list[str]) -> str | None:
    """The icon file name, or None with a warning when the icon is unusable. An icon is decoration, so a bad
    one never unlists an app: the card shows a monogram and the warning is reported in build/problems.md."""
    try:
        file = save_image(gh, name, branch, path, slug, "icon")
        check_square(BUILD / "media" / slug / file)
        return file
    except AppProblem as err:
        warnings.append(f"icon {path}: {err}; the card uses a monogram instead")
        return None


def repo_license(repo: dict) -> str | None:
    """The SPDX identifier GitHub detected, or None when it detected no license (the page then says "Not stated")."""
    return repo["license"]["spdx_id"] if repo["license"] else None


def resolve(entry: dict, gh: GitHub, manifest_dir: Path | None) -> dict:
    """Everything the site shows about one registered app (raises AppProblem)."""
    name = entry["repo"]
    repo = gh.repo(name)
    check_identity(entry, repo)
    manifest = read_manifest(gh, name, repo["default_branch"], manifest_dir)
    slug, branch, warnings = slugify(name.split("/")[1]), repo["default_branch"], []
    icon = manifest.get("icon")
    return {"warnings": warnings,
        "slug": slug, "repo": name, "html_url": repo["html_url"], "tier": "verified" if entry.get("verified_version") else "listed",
        "verified_version": entry.get("verified_version"), "verified_on": entry.get("verified_on"),
        "featured": bool(entry.get("featured")), "manifest": manifest,
        "license": manifest["license"] if "license" in manifest else repo_license(repo),
        "release": read_release(gh, name, manifest),
        "icon": read_icon(gh, name, branch, icon, slug, warnings) if icon else None,
        "screenshots": [{"file": save_image(gh, name, branch, s["path"], slug, f"shot-{i}"), "caption": s["caption"]}
                        for i, s in enumerate(optional_list(manifest, "screenshots"), 1)],
    }


def check_unique(app: dict, taken: dict[str, str]) -> None:
    """Slugs (web addresses) and display names must be unique, and a slug may not be empty or reserved;
    the first app registered keeps them."""
    if not app["slug"] or app["slug"] in RESERVED_SLUGS:
        raise AppProblem(f"{app['slug']!r} cannot be used as a web address (empty or reserved)")
    for key in (app["slug"], app["manifest"]["name"].lower()):
        if key in taken:
            raise AppProblem(f"{key!r} is already used by {taken[key]}")
    taken[app["slug"]] = taken[app["manifest"]["name"].lower()] = app["repo"]


def build(entries: list[dict], gh: GitHub, manifest_dir: Path | None = None) -> dict:
    """Resolve every entry: {"apps": [...], "problems": [...], "warnings": [...], "fetched_at": ...}.
    A problem leaves the app out; a warning (a bad optional icon) keeps it listed."""
    apps, problems, warnings, taken = [], [], [], {}
    for entry in entries:
        try:
            app = resolve(entry, gh, manifest_dir)
            check_unique(app, taken)
            apps.append(app)
            warnings += [f"{entry['repo']}: {w}" for w in app.pop("warnings")]
        except AppProblem as err:
            problems.append(f"{entry['repo']}: {err}")
    return {"format": SNAPSHOT_FORMAT, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "apps": apps, "problems": problems, "warnings": warnings}


def bullet_list(items: list[str], when_empty: str) -> str:
    """The items as a Markdown bullet list, or `when_empty` (plain text) when there are none."""
    return "\n".join(f"- {item}" for item in items) if items else when_empty


def write(snapshot: dict) -> None:
    """Write build/snapshot.json and build/problems.md (the latter lists what was left out, or says nothing was)."""
    BUILD.mkdir(exist_ok=True)
    (BUILD / "snapshot.json").write_text(json.dumps(snapshot, indent=1, ensure_ascii=False), encoding="utf-8")
    problems = bullet_list(snapshot["problems"], "Every registered app was resolved.")
    warnings = bullet_list(snapshot["warnings"], "None.")
    report = f"# Catalogue problems\n\n{problems}\n\n## Warnings (apps still listed)\n\n{warnings}\n"
    (BUILD / "problems.md").write_text(report, encoding="utf-8")
