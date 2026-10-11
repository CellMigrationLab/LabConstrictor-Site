# LabConstrictor website

**Preview:** <https://cellmigrationlab.github.io/LabConstrictor-Site/>

The preview is accessible but has not been officially launched. Its pages tell search engines not to index them; this is not an access restriction. The intended public address is `https://labconstrictor.cellmig.org/`. Some LabConstrictor guides already link to that address, and app manifests reference its schema URL. Check that the domain works before announcing the launch.

## What it does

[LabConstrictor](https://github.com/CellMigrationLab/LabConstrictor) packages workflows developed in Jupyter notebooks as installable desktop apps. The notebooks remain the main interface. Authors can also expose selected Python functions in napari, Fiji or QuPath through optional, experimental plugins.

This repository contains the website, not the packaging template or the plugins. It includes:

- an **App Centre** listing apps built with LabConstrictor, with project pages and downloads for the systems each app supports;
- a **How it works** guide, from notebook workflow to installer;
- an interactive **Demo** of an installed app, using a precomputed NucleiSky example (no analysis runs in the browser);
- **Docs** for installing and using apps, connecting them to image-analysis software, and building and publishing your own;
- an **Ecosystem** page with the supporting projects and links to related approaches;
- a **Submit** page explaining how to propose an app for listing.

Most content is edited at its source and imported when the site builds. There are deliberate exceptions: for example, the home-page citation in `data/site.yaml` repeats the template's citation. The build checks its DOI against the template README, not the entire reference.

## Where to edit what

Find the thing you want to change; edit it **there**, never in the site's generated pages.

| To change… | Edit | In repository |
|---|---|---|
| A guide for **building** an app (Docs → Build an app) | `.tools/docs/<page>.md`; the order and groups are in `.tools/docs/README.md` | [LabConstrictor](https://github.com/CellMigrationLab/LabConstrictor) |
| The **How it works** steps and explanations | `data/how-it-works.yaml` | this repository |
| The **How it works** figure and interactive stepper | `content/how/`, `tools/how_figures/crop_preprint_figure.py` | this repository |
| Two user pages that live in the template: *Notebook usage after installation*, *Troubleshooting an installed app* | `.tools/docs/notebook_usage.md`, `.tools/docs/troubleshooting_installed_app.md` | LabConstrictor |
| The **napari**, **Fiji** or **QuPath** guide | `docs/user-guide.md` | [napari-labconstrictor](https://github.com/CellMigrationLab/napari-labconstrictor), [LabConstrictor-Fiji](https://github.com/CellMigrationLab/LabConstrictor-Fiji), [LabConstrictor-QuPath](https://github.com/CellMigrationLab/LabConstrictor-QuPath) |
| The overview *Use apps inside napari, Fiji and QuPath* | `docs/user-guide.md` | [LabConstrictor-Tools](https://github.com/CellMigrationLab/LabConstrictor-Tools) |
| The **Connect to a microscope** guide | `docs/smart_microscopy/smart_microscopy.md` | [NucleiSky](https://github.com/CellMigrationLab/NucleiSky) |
| A card on the **Ecosystem** page (name, summary, status) | `docs/labconstrictor-project.yaml` (the template's card is inline in `data/ecosystem.yaml`) | the project's own repository; template exception in this repository |
| An **app's description**, declared distribution, supported hosts, icon and screenshots | `labconstrictor-app.yaml` | the app's own repository |
| **Actual installer files**, download URLs and released version | assets and tag of the latest published GitHub Release (resolved by `scripts/lcsite/catalogue.py`) | the app's own repository; resolved in this repository |
| Which apps are listed; featured on the home page; shown under *Testing and maintenance* | `registry/<owner>__<repo>.yaml` (`featured`, `section: testing`) | this repository |
| The **Related projects** section of the Ecosystem page | `data/related-projects.yaml` | this repository |
| The picture cards on the **Use** and **Build** pages | `data/hubs.yaml` | this repository |
| Linked image-analysis software and service logos | `data/hosts.yaml` | this repository |
| *Open and use an app* | `content/guides/using-apps.md` | this repository |
| *Find your problem* help page | `content/guides/help.md` | this repository |
| *Install an app* (steps for each system) | `.tools/docs/install.md` | LabConstrictor |
| Home page text and the copied LabConstrictor citation | `data/site.yaml` | this repository |
| The **Submit** page | `content/submit.md` | this repository |
| The **demo** page and its home tile (wording) | `data/demo.yaml` | this repository |
| The demo's notebook, napari, Fiji and installer views, interactions and styles | `content/demo/windows/`, `content/demo/demo*.js`, `content/demo/demo.css`, `content/demo/installer.css` | this repository |
| The demo's measured result and microscopy images | `content/demo/example.json` and images; regenerate with `tools/demo_assets/make_demo_assets.py`; provenance in `content/demo/README.md` | this repository |
| The demo's example installer and matcher settings | `content/demo/installer.json` and `matcher_config.json`; regenerate with `tools/demo_assets/installer_record.py` and `matcher_config.py` | this repository |
| The **menu** | `nav:` in `mkdocs.yml` | this repository |
| The footer, page layout, colours | `overrides/`, `docs/assets/stylesheets/lc.css` | this repository |
| Which projects the Ecosystem page lists | `data/ecosystem.yaml` (one `- repo: owner/name` line each) | this repository |
| Add another guide kept in a repository | one line in `data/guides.yaml` | this repository |
| An address that moved (so old links keep working) | one line in `data/redirects.yaml` | this repository |

To **list an app**, the app's authors use the [submission form](https://github.com/CellMigrationLab/LabConstrictor-Site/issues/new?template=submit-app.yml) (or add a pointer file in `registry/`).

The `build/` and `site/` directories are generated. These paths under `docs/` are also generated and git-ignored: `index.md`, `apps/`, `guides/`, `use/`, `build/`, `how-it-works/`, `ecosystem.md`, `submit.md`, `demo/`, `llms.txt` and `assets/{icons,shots,docs-img,images,hubs,hosts,demo,how}/`. Do not edit them by hand: the next build replaces them.

Not everything under `docs/` is generated. For example, `docs/assets/stylesheets/lc.css`, `docs/assets/javascripts/lc.js` and `docs/assets/fonts/` are tracked source files.

## When changes appear

The [publish workflow](.github/workflows/publish.yml) runs:

- when changes are pushed to `main` (pull requests build a preview artifact but do not deploy);
- daily (currently scheduled for 05:23 UTC), to pick up new app releases and changes in other repositories;
- on demand: **Actions → Build and publish site → Run workflow**.

Successful `main` and scheduled builds deploy the site; the time it takes depends on GitHub Actions. If a build fails, the previous version stays online. A failed scheduled build opens or updates a GitHub issue.

A missing or invalid guide, required picture or ecosystem project file stops the build. **App catalogue failures are different:** if an individual app's manifest or release cannot be resolved, that app is omitted and the reason is recorded in `build/problems.md`. Pull-request builds fail when any registered app is omitted; `main` and scheduled builds can publish the remaining apps. A scheduled build also opens or updates an issue about omitted apps.

## Going public

In `mkdocs.yml`, `extra: listed: false` adds `noindex` instructions to the pages, creates an empty sitemap and writes a disallowing `robots.txt`. These are indexing instructions, not access controls. On the GitHub Pages project URL, the generated `robots.txt` is not at the host root, so the page-level `noindex` instruction is especially important.

At launch, confirm the custom domain and the links already pointing to it, update `site_url`, and set `extra: listed: true`.

## For developers and agents

Read [AGENTS.md](AGENTS.md): how the site is built, the coding rules (they are checked by the tests), and how untrusted input is handled. [DESIGN.md](DESIGN.md) says how every kind of title, link, button, card and image must look and behave.

## Licence

- **Site code** (`scripts/`, `tests/`, `tools/`, `overrides/`, styles and scripts): MIT, see [LICENSE](LICENSE).
- **Original text written for this site:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), where the site's authors own the rights.
- **Microscopy images in the demo:** derived from a [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) dataset. Its attribution, modifications and provenance are described in [`content/demo/README.md`](content/demo/README.md). This does not automatically license other artwork in the demo.
- **LabConstrictor logo and comic:** licensing terms have not yet been stated. The NucleiSky app icon used in the demo also has rights still to be confirmed; do not assume it shares the microscopy dataset's licence.
- **Material imported from other repositories** retains its original licensing and attribution requirements. An image or logo does not necessarily share its repository's code licence.
- **Fonts:** Inter and Bricolage Grotesque are under the SIL Open Font License; see `docs/assets/fonts/`. Logos of other software and services belong to their respective owners and are shown to identify them.
