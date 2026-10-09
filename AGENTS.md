# AGENTS.md

This repository is small on purpose. Keep it that way. (Conventions follow the lab website and the graduate-school site.)

## Sources of truth

- Hand-written pages: `content/*.md` (`submit.md`) and `data/*.yaml` (site text, install steps, ecosystem).
- Which apps are listed: `registry/<owner>__<repo>.yaml`, one pointer file per app. Nothing else about an app is stored here.
- What an app says about itself: `labconstrictor-app.yaml` in the app's own repository, checked against `schema/labconstrictor-app.schema.json`.
- Guides: written in the template repository (`LabConstrictor/.tools/docs`), imported at build time. Fix guide mistakes there.
- `docs/index.md`, `docs/apps/`, `docs/guides/`, `docs/ecosystem.md`, `docs/submit.md`, `docs/llms.txt`, `docs/assets/{icons,shots,docs-img}/`, `build/` and `site/` are generated and git-ignored. Fix the source or the generator, never the generated file.

## Two stages

1. `scripts/fetch_catalogue.py` is the only code that uses the network. It writes `build/snapshot.json` and `build/problems.md`.
2. `scripts/build_site.py` reads the snapshot and writes pages. It never goes online, so a build is repeatable.

## No silent fallbacks

If required input is missing, malformed, ambiguous or unsupported, raise a clear error that names the file or app. Do not substitute defaults, accept legacy aliases, skip files that should exist, or catch broad exceptions and continue.

The one deliberate exception is per-app: an app that cannot be resolved is left out of the site, but it is always named in `build/problems.md`, printed, and (on scheduled builds) opened as an issue. Optional manifest fields (icon, screenshots) may be absent; a broken optional icon becomes a reported warning and a monogram.

## Code

- Python 3.12, type annotations on every function, a short docstring on every function (purpose, input, output, how it fails).
- Functions do one job and stay short. A file that grows past about 300 lines is split by responsibility; none may pass 600.
- Pure functions for parsing and formatting; network and filesystem work at the edges (`github.py`, `catalogue.py`, `images.py`, `page.py`).
- `pathlib.Path` for paths; specific exceptions (`AppProblem` for one app's failure, `fail()` to stop the build).
- Everything from an app's manifest is untrusted text: escape it (`text.esc`), never render it as HTML or Markdown, never download from anywhere but the app's own GitHub release.
- Preserve public URLs (`/apps/<slug>/`, `/guides/<slug>/`) unless a redirect is added.

## Before you push

    PYTHONPATH=scripts python -m unittest discover -s tests
    python scripts/fetch_catalogue.py
    python scripts/build_site.py --template-dir <LabConstrictor checkout> --doc-source-dir <doc_source checkout>
    zensical build --strict
