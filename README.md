# LabConstrictor site

The website for [LabConstrictor](https://github.com/CellMigrationLab/LabConstrictor): the user guides, and an **App Centre** that lists the apps built with it. Built with [Zensical](https://zensical.org) like the other lab sites and published with GitHub Pages.

| Section | What it is | Where it comes from |
|---|---|---|
| Home | what LabConstrictor is, two paths (use / make), featured apps | `data/site.yaml`, `registry/` |
| Apps | filterable catalogue, one page per app, OS-aware downloads | each app's `labconstrictor-app.yaml` and latest GitHub release |
| Guides | install an app; build an app | `data/install.yaml`; the template's `.tools/docs` |
| Ecosystem | napari, Fiji, QuPath, template, Tools library | `data/ecosystem.yaml` |
| Submit your app | how to be listed | `content/submit.md`, `.github/ISSUE_TEMPLATE/submit-app.yml` |

## How an app gets listed

1. The author adds `labconstrictor-app.yaml` to their repository ([schema](schema/labconstrictor-app.schema.json); routes: installer, Colab, pip).
2. They open the *Submit an app* issue form with their repository address.
3. `validate-submission.yml` checks it with the same code the build uses, comments the result, and opens a pull request adding `registry/<owner>__<repo>.yaml` (ids only: no version, no description).
4. A maintainer merges. A daily build reads each app's latest release and manifest. To mark an app **Verified**, add `verified_version` and `verified_on` to its registry file after installing and running that version.

## Build locally

    python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
    git clone --depth 1 https://github.com/CellMigrationLab/LabConstrictor ../LabConstrictor
    git clone --depth 1 --branch doc_source https://github.com/CellMigrationLab/LabConstrictor ../LabConstrictor-doc_source
    export GITHUB_TOKEN=...      # optional; avoids the anonymous rate limit
    python scripts/fetch_catalogue.py
    python scripts/build_site.py --template-dir ../LabConstrictor --doc-source-dir ../LabConstrictor-doc_source
    zensical serve

`fetch_catalogue.py --manifest-dir seed/manifests` previews the draft manifests in `seed/manifests/` before they are committed to the app repositories (development only).

## Layout

    registry/        one pointer file per listed app
    schema/          JSON Schemas (published at /schema/): app manifest, registry entry
    data/, content/  hand-written text
    seed/manifests/  drafts of labconstrictor-app.yaml for the six lab apps
    scripts/         fetch_catalogue.py, build_site.py, submit_app.py, write_sitemap.py, lcsite/
    overrides/, docs/assets/   theme (adapted from cellmig.org)
    tests/           unit tests

## Setting up hosting (one-time)

1. Create the repository and push; in *Settings > Pages* choose *Source: GitHub Actions*.
2. Add the custom domain `labconstrictor.cellmig.org` there, and a `CNAME` record `labconstrictor` pointing to `cellmigrationlab.github.io` where the cellmig.org DNS is managed. Enable *Enforce HTTPS*.
3. Add the issue label `app-submission`, and allow Actions to create pull requests (*Settings > Actions > General*).

See [AGENTS.md](AGENTS.md) for the coding rules.
