# Plan: an interactive section "How LabConstrictor works"

Status: PLAN with options. **Built on the recommended Option A without waiting for your choice** (the work is on the feature branch and reversible): the page `/how-it-works/` has chapters 1-7 of your list, in your order (portable notebooks, where the code lives, requirements, deposit with the web form, the plugin manifest (tool declarations), packaging with release workflows, then the App Centre manifest and the bridge). Not built: the suggested chapters A-E. The questions at the end still stand. Requested 2026-10-11. Every fact below was read in the template (`.tools/docs`, workflows), LabConstrictor-Tools (`docs/`), LabConstrictor_streamlit and the NucleiSky repo; each chapter must be re-checked against the code when it is built, and anything that cannot be verified from code stays out (clean-install facts wait for the lab's runs, decision 24).

## What it should do for the reader
Show, in order, what an author does and what the tool does for them, from a working notebook to an installed app that also runs in napari, Fiji and QuPath. Each step is small, shows the real file or screen, and lets the reader do one thing (toggle, click, type) that changes what is shown. Like the demo, it is a simulation of precomputed examples: no code runs, nothing is uploaded, and it says so.

## Chapters (your seven, in this order, plus the ones I suggest adding)
| # | Chapter | What the reader sees and does | Verified source |
|---|---|---|---|
| 1 | **Write notebooks that run in Colab and JupyterLab** | A notebook cell with a Colab-only line (`google.colab` import, Drive mount). Toggle "Colab" / "JupyterLab": the same cell shows which lines run where and the guard (`if 'google.colab' in sys.modules`) that keeps it portable. Second toggle: "Hide code" showing the `# @title` / `@markdown` trick that keeps explanations visible. | `notebook_portability.md` (six rules), NucleiSky notebook cell 3 (Step 0: Colab branch vs "Local environment detected") |
| 2 | **Where the code lives: `src/`, `pip install`, or both** | A small file tree with a notebook and two choices. "Code in `src/`": `src/<package>/__init__.py` appears, the notebook does `import <package>`, and `construct.yaml` lists it under `extra_files`. "pip package": the package name goes into `requirements.yaml`. "Both": NucleiSky's setup (package in `src/` and `pip install nucleisky` on Colab). The reader drags/selects, the tree and the import line update. | `external_code_upload.md`, NucleiSky `construct.yaml` and Step 0 cell, `requirements.yaml` format |
| 3 | **Requirements: get your `requirements.yaml`** | The three fields (`dependencies`, `python_version`, `description`). Two routes: automatic (the Requirements Generator notebook) and manual. Interaction: paste-free, choose a sample notebook's imports and see the generated list (a precomputed mapping for one or two sample notebooks, labelled as an example). | `notebook_requirements.md`, `.tools/templates/requirements.yaml` |
| 4 | **Deposit notebooks and requirements with the web form** | A mock of the Streamlit form: Upload/Update notebook, upload `.ipynb` + `requirements.yaml`, Validate & Add Submission, repository URL and token, Create pull request. Then a mock pull request and what the checking workflow does (success; failure undoes the merge). | `notebook_upload.md`, LabConstrictor_streamlit `app.py` labels (note: the guide says "Validate submission", the form says "Validate & Add Submission": fix in the template first, see template draft) |
| 5 | **Describe the app for the App Centre (and the plugin manifest)** | Two files side by side. `labconstrictor-app.yaml` (name, summary, kind, distribution, inputs/outputs...): fields light up the real app page preview below as you edit options (reuses the site's own app-page renderer on a sample). Plus the tools declaration (chapter 7). | `app_manifest.md`, `schema/labconstrictor-app.schema.json`, `docs/MANIFEST.md` (Tools) |
| 6 | **Actions package the installers** | A GitHub release timeline: Draft a release, Publish, the `release_constructor` workflow builds installers for Windows, macOS (Apple Silicon, Intel) and Linux; the installers appear as release files. The reader clicks each stage; a failed-run branch shows "how to read a failed workflow". Also shows the other workflows (`update_on_notebook_change`, `update_on_src_change`, `check_app_manifest`, `sync_template`) one line each. | `executable_creation.md`, `workflow_status.md`, `.github/workflows/*` |
| 7 | **Once installed: how the bridge works** | The six-step explainer already on the demo page, promoted and extended: installer registers the app (post-install hook finds `<package>_lc_tools`, installs `labconstrictor-tools`, runs `register`; failure never fails the install), tools are Python functions with type hints, the host builds its form from the schema, the tool runs in the app's own environment in a separate process, outputs come back as layers/overlays/points/tables. Interaction: edit a tool signature (change a type, add a Min) and watch the generated napari and Fiji forms change (a precomputed set of variants). Experimental labels stay. | `LABCONSTRICTOR_INTEGRATION.md`, `AUTHORING.md`, `MANIFEST.md`, `PROTOCOL.md` (Tools) |
| + A | **The installer on the user's computer** (suggested) | The steps of the Windows installer already built for the demo (SmartScreen, wizard pages, post-install window) linked to what the post-install hook does behind them (pip install of the requirements, tools registration). | demo installer, `construct.yaml`, `post_install.bat/.sh` |
| + B | **Make it yours: branding** (suggested) | Upload-free picture picker: logo, banner and header images appear in the installer wizard mock. | `installer_images.md` |
| + C | **Keep your app up to date** (suggested; decision 17 moves template sync here) | What the weekly sync does and the one-time setup (token, secret, actions), as an optional step after the first release. | `template_synchronization.md`, `sync_template.yml` |
| + D | **Share it** (suggested) | Submit form to listing: manifest check, pull request, appears at the next daily build. | `content/submit.md`, `scripts/submit_app.py` |
| + E | **Update notebooks in an installed app** (suggested) | The Welcome notebook's update check (already simulated in the demo). | demo Welcome notebook |

## Options for the form
**Option A: one guided page `/how-it-works/` (recommended).** A vertical sequence of chapters with a sticky chapter list (a progress rail) and one interactive panel per chapter, each panel small enough for a phone. Mobile: chapters stack, interactions stay (tap targets). Without JavaScript each panel shows a static figure and the text. Reuses the demo's engine (state object, strict DOM helpers, red hand-drawn guide) and the site's rules for simulated windows. Effort: about the demo's size, spread over chapters; build in two waves (1-4 first, 5-7 second).
**Option B: a "journey" with one persistent scene.** A single large scene (a repository file tree plus a browser, GitHub and a desktop) that transforms as you advance chapters, like a slide animation. Most striking and memorable, hardest to maintain and to make accessible; heavier JavaScript.
**Option C: lightweight explainer.** Static diagrams and annotated screenshots with only small toggles (Colab/JupyterLab, src/pip), no mock web form or installer. Cheapest, least engaging; good as a fallback or no-JS version of A.
**Combination I recommend:** build A; each chapter also exists as a plain text section (the C layer), which the no-JavaScript view and search use.

## Where it lives
- A new page `/how-it-works/` (not another top-level menu entry; reached from the home "How it works" band, the Docs home and the Build hub). The Docs guides stay the reference and each chapter links to its guide ("Read the full guide").
- Texts in `data/how-it-works.yaml`; chapter panels as partials in `content/how-it-works/` (same rules as the demo: one balanced element, no blank lines, placeholders filled from checked data); scripts as small documented parts under the same JS rules (`tests/test_js_rules.py`).
- Facts that could go stale are read from the repositories at build time where possible (labels from the form, workflow names, the schema's field list, the tools types table) and the build stops when a name used in a mock no longer exists.

## Accuracy and honesty rules (same as the demo)
- A visible note: this is an illustration with example files; nothing runs here and nothing is uploaded.
- Mock screens show only labels read from the real form or documentation; where a screenshot of the real web form is wanted, it comes from a clean run (checklist in `planning/CLEAN-INSTALL-CHECKLIST.md`).
- napari, Fiji and QuPath parts carry the experimental label; Windows hooks are marked as not yet run on Windows in the Tools docs (`LABCONSTRICTOR_INTEGRATION.md`).
- No claim about maintenance, speed or stability.

## Build order
1. Chapter list and wording (`data/how-it-works.yaml`), page shell, progress rail, no-JS layer.
2. Chapters 1-3 (notebook portability, code location, requirements): self-contained, only template facts.
3. Chapter 4 (web form) after the template label fixes are merged.
4. Chapters 6 and 7 (release workflow, bridge) reusing the demo's bridge explainer and installer.
5. Chapter 5 (manifest preview) reusing the app-page renderer; then A-E as time allows.
6. Tests: data and partial consistency, JS rules, every interaction in a browser at 390 and 1280 px, no console errors; design checker rule for the new simulated controls.

## Questions for you
1. Which form: A (recommended), B or C?
2. Order and extras: keep your seven in your order? Which of A-E (the "+" chapters) do you want?
3. Chapter 4 mocks the Streamlit form: acceptable to reproduce its labels (read from the app's code), or do you prefer a real screenshot from a clean run only?
4. Chapter 7: promote the demo's six-step bridge explainer into this page and leave a link in the demo, or keep both?
5. Where should the entry point sit: a card on the Docs home and the Build hub plus the home band, or also a menu entry?
