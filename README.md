# LabConstrictor site

The website for [LabConstrictor](https://github.com/CellMigrationLab/LabConstrictor): the user guides, and an **App Centre** that lists the apps built with it. Built with [Zensical](https://zensical.org) like the other lab sites and published with GitHub Pages.

**Live site:** <https://cellmigrationlab.github.io/LabConstrictor-Site/> (a preview address; the site is not public yet, so it is hidden from search engines and not linked from the other repositories).

| Section | What it is | Where it comes from |
|---|---|---|
| Home | what LabConstrictor is, two paths (use / make), featured apps | `data/site.yaml`, `registry/` |
| Apps | filterable catalogue, one page per app, OS-aware downloads | each app's `labconstrictor-app.yaml` and latest GitHub release |
| Guides | install and use an app; plugins for napari, Fiji, QuPath; build an app | `data/install.yaml`, `content/guides/using-apps.md`; each plugin repository's `docs/user-guide.md`; the template's `.tools/docs` |
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
    python scripts/fetch_guides.py                  # the guides kept in the plugin repositories (add --ref BRANCH to preview an unmerged one)
    python scripts/build_site.py --template-dir ../LabConstrictor --doc-source-dir ../LabConstrictor-doc_source
    zensical serve

`fetch_catalogue.py --manifest-dir seed/manifests` previews the draft manifests in `seed/manifests/` before they are committed to the app repositories (development only).

## Layout

    registry/        one pointer file per listed app
    schema/          JSON Schemas (published at /schema/): app manifest, registry entry
    data/, content/  hand-written text
    seed/manifests/  drafts of labconstrictor-app.yaml for the six lab apps
    scripts/         fetch_catalogue.py, fetch_guides.py, build_site.py, submit_app.py, write_sitemap.py, lcsite/
    overrides/, docs/assets/   theme (adapted from cellmig.org)
    tests/           unit tests

## Setting up hosting (one-time)

1. Create the repository and push; in *Settings > Pages* choose *Source: GitHub Actions*.
2. Add the custom domain `labconstrictor.cellmig.org` there, and a `CNAME` record `labconstrictor` pointing to `cellmigrationlab.github.io` where the cellmig.org DNS is managed. Enable *Enforce HTTPS*.
3. Add the issue label `app-submission`, and allow Actions to create pull requests (*Settings > Actions > General*). Pull requests made with the default `GITHUB_TOKEN` do not start other workflows, so the submission workflow itself runs the full app check before it opens one; use a token or GitHub App for `peter-evans/create-pull-request` if you also want the build to run on them.
4. Pin the third-party actions (`peter-evans/create-pull-request`, `actions/*`) to commit SHAs before the repository is public.

See [AGENTS.md](AGENTS.md) for the coding rules.
