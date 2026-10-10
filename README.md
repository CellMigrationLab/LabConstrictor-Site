# LabConstrictor website

**Live (preview address):** <https://cellmigrationlab.github.io/LabConstrictor-Site/>
It is not public yet: search engines are told to ignore it and the other LabConstrictor repositories do not link to it. The final address will be `labconstrictor.cellmig.org`.

## What it does

The site is the front door to [LabConstrictor](https://github.com/CellMigrationLab/LabConstrictor), which turns Jupyter notebooks into desktop apps. It has:

- an **App Centre**: apps built with LabConstrictor, each with a page and a download for every system;
- **Docs**: how to install and use an app, how to use apps in napari, Fiji and QuPath, and how to build and publish your own;
- an **Ecosystem** page: the projects around LabConstrictor, each with a link to its GitHub repository;
- a **Submit** page: how another lab lists its app.

No page is written twice. Each fact lives in the repository it describes, and the site collects them when it rebuilds.

## Where to edit what

Find the thing you want to change; edit it **there**, never in the site's generated pages.

| To change… | Edit | In repository |
|---|---|---|
| A guide for **building** an app (Docs → Build an app) | `.tools/docs/<page>.md`; the order and groups are in `.tools/docs/README.md` | [LabConstrictor](https://github.com/CellMigrationLab/LabConstrictor) |
| Two user pages that live in the template: *Notebook usage after installation*, *Troubleshooting an installed app* | `.tools/docs/notebook_usage.md`, `.tools/docs/troubleshooting_installed_app.md` | LabConstrictor |
| The **napari**, **Fiji** or **QuPath** guide | `docs/user-guide.md` | [napari-labconstrictor](https://github.com/CellMigrationLab/napari-labconstrictor), [LabConstrictor-Fiji](https://github.com/CellMigrationLab/LabConstrictor-Fiji), [LabConstrictor-QuPath](https://github.com/CellMigrationLab/LabConstrictor-QuPath) |
| The overview *Use apps inside napari, Fiji and QuPath* | `docs/user-guide.md` | [LabConstrictor-Tools](https://github.com/CellMigrationLab/LabConstrictor-Tools) |
| A card on the **Ecosystem** page (name, summary, status) | `docs/labconstrictor-project.yaml` | the project's own repository |
| What an **app says about itself** (name, summary, downloads, screenshots) | `labconstrictor-app.yaml` | the app's own repository |
| Which apps are listed; featured on the home page; verified; shown under *Testing and maintenance* | `registry/<owner>__<repo>.yaml` (`featured`, `verified_version`, `section: testing`) | this repository |
| The picture cards on the **Use** and **Build** pages | `data/hubs.yaml` | this repository |
| *Open and use an app* | `content/guides/using-apps.md` | this repository |
| *Install an app* (steps for each system) | `.tools/docs/install.md` | LabConstrictor |
| Home page text | `data/site.yaml` | this repository |
| The **Submit** page | `content/submit.md` | this repository |
| The **menu** | `nav:` in `mkdocs.yml` | this repository |
| The footer, page layout, colours | `overrides/`, `docs/assets/stylesheets/lc.css` | this repository |
| Which projects the Ecosystem page lists | `data/ecosystem.yaml` (one `- repo: owner/name` line each) | this repository |
| Add another guide kept in a repository | one line in `data/guides.yaml` | this repository |
| An address that moved (so old links keep working) | one line in `data/redirects.yaml` | this repository |

To **list an app**, the app's authors use the [submission form](https://github.com/CellMigrationLab/LabConstrictor-Site/issues/new?template=submit-app.yml) (or add a pointer file in `registry/`).

Files under `docs/` (`index.md`, `apps/`, `guides/`, `use/`, `build/`, `ecosystem.md`, `submit.md`, `llms.txt`, `assets/{icons,shots,docs-img,images,hubs}/`), `build/` and `site/` are **generated and git-ignored**. If you change one by hand, the next build deletes your change.

## When changes appear

The site rebuilds by itself, so you rarely need to do anything:

- when something is pushed to `main` of this repository (about a minute);
- every day (so edits in the other repositories, new app releases and new manifests show up within 24 hours);
- on demand: **Actions → Build and publish site → Run workflow**.

A build that fails leaves the previous site online, and a failed daily build opens an issue in this repository. A broken or missing guide, picture, project file or manifest stops the build and the error names the file to fix.

## Going public

In `mkdocs.yml`, `extra: listed: false` keeps the site out of search engines. Set it to `true` when the site launches, and update `site_url` once the domain is ready.

## For developers and agents

Read [AGENTS.md](AGENTS.md): how the site is built, the coding rules (they are checked by the tests), and how untrusted input is handled.
