# AGENTS.md

This repository is small on purpose. Keep it that way. (Conventions follow the lab website and the graduate-school site.)

## Sources of truth

- Hand-written pages: `content/submit.md`, `content/guides/*.md` (listed in `data/guides.yaml`) and `data/*.yaml` (site text, install steps, ecosystem).
- Which apps are listed: `registry/<owner>__<repo>.yaml`, one pointer file per app. Nothing else about an app is stored here.
- What an app says about itself: `labconstrictor-app.yaml` in the app's own repository, checked against `schema/labconstrictor-app.schema.json`.
- Guides come in two tracks. "Build an app" is written in the template repository (`LabConstrictor/.tools/docs`) and imported at build time; fix those there. A template page that is really for users (`notebook_usage.md`, `troubleshooting_installed_app.md`) is placed under "Use an app" with `template: <file>` in `data/guides.yaml`; its text and title stay in the template, and the build stops if the template drops the file. The two hub pages (`/use/`, `/build/`: picture cards, the reasons to build, the build steps) are `data/hubs.yaml`; every picture there is a file in the template's `doc_source` branch or in another repository (fetched by `fetch_guides.py`) and must have alt text. The guide of each plugin (napari, Fiji, QuPath) and the overview of using apps in image software are `docs/user-guide.md` in the repository they describe (napari-labconstrictor, LabConstrictor-Fiji, LabConstrictor-QuPath, LabConstrictor-Tools): `scripts/fetch_guides.py` downloads them at build time, the title is their first heading, GitHub alerts become admonitions, and links and pictures must be absolute. Fix them there. To add a module, add one `{slug, repo, path}` line to `data/guides.yaml`. Only guides with no other home (`using-apps.md`, `submit.md`) and the generated install guide are written here.
- The Ecosystem page: each project describes itself (name, summary, status, optional url) in `docs/labconstrictor-project.yaml` in its own repository, checked against `schema/labconstrictor-project.schema.json`; `data/ecosystem.yaml` only lists the repositories and their headings (add a project = add one `- repo: owner/name` line). The template's card is inline there because its repository is copied into every app. Fix a project's card in that project.
- The logo and the comic come from the template's `doc_source` branch at build time.
- `docs/index.md`, `docs/apps/`, `docs/guides/`, `docs/use/`, `docs/build/`, `docs/ecosystem.md`, `docs/submit.md`, `docs/llms.txt`, `docs/assets/{icons,shots,docs-img,images,hubs}/`, `build/` and `site/` are generated and git-ignored. Fix the source or the generator, never the generated file.

## Two stages

1. `scripts/fetch_catalogue.py` and `scripts/fetch_guides.py` are the only code that uses the network. They write `build/snapshot.json`, `build/problems.md` and `build/sources/`.
2. `scripts/build_site.py` reads the snapshot and writes pages. It never goes online, so a build is repeatable.

## Untrusted input

Everything in an app's manifest, its release and its repository is written by someone we do not control.

- Text goes into pages only through `text.esc` (HTML) or `text.one_line` (plain files); the theme prints a front-matter `description` unescaped, so `Page` neutralises its quotes.
- Manifests are parsed with `validate.load_plain_yaml` (no anchors or aliases) and checked against the schema; downloads are size-capped; redirects to other hosts are refused (`github.py`).
- Web addresses come from `slugify`, may not be empty or reserved, and a file the guide importer copies must stay inside its source folder.
- `scripts/check_site.py` runs after the build and fails on dead links, author text that appears unescaped, and missing files.

## No silent fallbacks

If required input is missing, malformed, ambiguous or unsupported, raise a clear error that names the file or app. Do not substitute defaults, accept legacy aliases, skip files that should exist, or catch broad exceptions and continue.

A GitHub outage (`FetchError`) is not per-app: it stops the whole fetch (exit 4), so the live site is never rebuilt from a half-empty catalogue. `build_site.py` also refuses a snapshot with no apps.

The one deliberate exception is per-app: an app that cannot be resolved is left out of the site, but it is always named in `build/problems.md`, printed, and (on scheduled builds) opened as an issue. Optional manifest fields (icon, screenshots) may be absent; a broken optional icon becomes a reported warning and a monogram.

## Code

- Python 3.12, type annotations on every function, a short docstring on every function including nested ones and tests (purpose, input, output, how it fails). No `x or default`, `.get(key, default)` or broad `except` for required data: optional manifest fields are checked explicitly.
- Functions do one job and stay under about 30 lines. A file that grows past about 300 lines is split by responsibility; none may pass 600.
- Pure functions for parsing and formatting; network and filesystem work at the edges (`github.py`, `catalogue.py`, `images.py`, `page.py`).
- `pathlib.Path` for paths; specific exceptions (`AppProblem` for one app's failure, `fail()` to stop the build).
- Everything from an app's manifest is untrusted text: escape it (`text.esc`), never render it as HTML or Markdown, never download from anywhere but the app's own GitHub release.
- Preserve public URLs (`/apps/<slug>/`, `/guides/<slug>/`, `/use/`, `/build/`) unless a redirect is added.

## Before you push

    PYTHONPATH=scripts:tests python -m unittest discover -s tests
    python scripts/fetch_catalogue.py
    python scripts/fetch_guides.py
    python scripts/build_site.py --template-dir <LabConstrictor checkout> --doc-source-dir <doc_source checkout>
    zensical build --strict
    python scripts/write_sitemap.py && python scripts/check_site.py
