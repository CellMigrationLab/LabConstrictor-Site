# Template drafts (LabConstrictor, branch `claude/festive-cannon-epptr4`)

Status: pushed, no pull request opened. The branch had been merged before (PR #25), so it was restarted from `origin/main` (0066f5e) with `git checkout -B`; the remote branch was a fast-forward. Nothing outside `.tools/docs/*`, `.github/PULL_REQUEST_TEMPLATE.md` and `.github/CONTRIBUTING.md` was touched. The template's own tests (`python3 -m unittest discover -s tests`, 32 tests) pass. A link and anchor check of every `.tools/docs/*.md` (script in the scratchpad) reports 0 problems before and after. I also ran the site's `guides.parse_index` and `NAV_BLOCK` against the new README: no page is unlisted, and the footers match the site pager for the whole Build path except the pages named under "Decide" below.

Verifying sources: "form" is `/home/user/LabConstrictor_streamlit` `app.py` at `origin/main` (8cbef3f); "sync" is `.github/workflows/sync_template.yml` in the template.

## Commits

| Hash | Subject |
|---|---|
| c21f131 | Docs: fix wrong UI labels and typos in the template guides |
| bd10c7e | Docs: make template synchronisation an optional guide after the first release |
| 9759ea3 | Docs: name the install guide headings by system |
| cfa02c6 | Docs: link to the VLab4Mic Bluesky post instead of showing a screenshot of it |
| 94af5a5 | Docs: add a pull request checklist for user-visible label changes |

## 1. Labels and typos (c21f131)

- `notebook_upload.md`: "Validate submission" becomes "**➕ Validate & Add Submission**" (form `app.py:1029`); the notebook then appears in the "**📃 Submission list**" (`app.py:1085`), steps 3 and 4 can be repeated to add several notebooks (`app.py:1002`); step 5 names the "**⬆️ Upload it to GitHub**" section (`app.py:1106`); step 6 is "**🚀 Create pull request**" (`app.py:1125-1129`, label with icon). The other labels on that page already matched (`Upload/Update notebook` `app.py:850`, file uploaders `app.py:1009,1020`). Note: the initialiser form's own button is still "Validate submission" (`app.py:915`), so that wording is correct for that form and was not changed.
- `notebook_usage.md`: "Ctrl + C or Cmd + C" becomes "press `Ctrl+C`" in the terminal window (no macOS-specific wording); "Open the Notebook" becomes "Open the notebook" (`.tools/templates/Welcome_template.ipynb:76`); "finnisehd", "LabConstrisctor" and "need so guidance" fixed.
- `workflow_status.md`: the log is a plain `.log` file, nothing to unzip (`archive: false` in `release_constructor.yml:79,182` and `update_on_notebook_change.yml:136`).
- `personal_access_token.md`: one classic-token recipe with "tick **repo**"; the `contents` sub-bullets, the "Resource owner" step and the "Read-Only Access" recipe are removed; added that the repository form accepts only a classic `ghp_` token and rejects `github_pat_` (`app.py:972-977`, `1137-1142`). The headings "For Read & Write Access" and "For Read-Only Access" no longer exist; nothing links to them (grep of the template, the site's content/data/scripts/tests and the form).
- `initialise_repository.md`: example version `0.1.0` becomes `0.0.1` (`app.py:869,882`; `executable_creation.md:14`); "Initialise a repository" becomes "Initialise GitHub repository" (`app.py:838`); the parenthesis promising a GIF was removed because the page has no GIF (this is the plan's item 6a "delete" option).
- `before_getting_started.md`: the garbled sentence is repaired (duplicate sentence and dangling "private or public" fragment; the repository can be private or public is the only thing the fragment can mean).
- Typos: bellow (3 pages), Got to, intialisation (`code_hiding.md`, not in the plan).

Not done from plan item 1, and why:
- `executable_creation.md` "line 21 garbled": already fixed on `origin/main`; nothing to change.
- `template_synchronization.md` ("the following video", footer): **blocked**, see "Decide" 1.
- `.tools/templates/Welcome_template.ipynb:17,21`: "Test Connection" should read "Load Private GitHub Repo" (`:599` is the real button text). Outside the allowed files (not `.tools/docs`), so left; a one-line fix for the maintainer.
- The Streamlit sleep-page button "Yes, get this app back up!" is Streamlit's own wording, not in the form's code; left as written.

## 2. Synchronisation moved after the first release (bd10c7e)

- Template file names are unchanged, so no redirect and no change to the site's `data/guides.yaml` or `data/redirects.yaml` is needed: `template_synchronization.md` keeps its address `/guides/template-synchronization/` (the only site reference is the `KNOWN_EXCEPTIONS` entry in `scripts/check_design.py`, still valid).
- New short page `keep_app_up_to_date.md` ("Keep your app up to date", address `/guides/keep-app-up-to-date/`). Facts from sync: weekly cron Monday 09:00 UTC (`:6`), manual start (`:7`), pull request title "Sync template to version ..." (`:166`), the step "Check synchronization token setup" fails with "Synchronization setup required" when a newer template version exists (`:115-132`), the pull request is created with the secret (`:162`). It says no update pull request is created and the repository stays on its template version; it does not call this harmless and gives no time estimate. It links to the existing step page and to its "Renewing an expired token" anchor, to `troubleshooting.md#synchronisation-is-failing-on-github-actions` and to `workflow_status.md`.
- Early path: the gate in `create_repository.md` is now the one recommending sentence ("Without the update token, the weekly Sync with Template Repository run stops with the error 'Synchronization setup required' as soon as a newer template version exists, and your repository receives no update pull request."). The gates in `before_getting_started.md` and `initialise_repository.md` are removed; `executable_creation.md` has one line under "After the release".
- README order: Before, Create, Initialise, Accept a pull request, Requirements, Upload, Create installers, Install an app, Download (skipped by the site), Notebook usage, Troubleshooting an installed app; then "Customise and share (optional)" (images, App Centre, external code); "Keep your app up to date (optional)" (new page, step page); tips; examples; "GitHub management" (workflow overview, troubleshooting, personal access token). "Accept a pull request" left "GitHub management".
- Footers updated: `create_repository`, `initialise_repository`, `accept_pull_request`, `notebook_requirements`, `executable_creation` (Next now goes to `installer_images`, as on the site pager), `external_code_upload`, `workflow_status`, `personal_access_token`; new footers for `installer_images`, `troubleshooting` and `keep_app_up_to_date`.

## 3. Install headings (9759ea3)

Renamed to "Install on Windows", "Install on a Mac", "Install on Linux" (anchors `#install-on-windows`, `#install-on-a-mac`, `#install-on-linux`). No link to `#windows`, `#macos` or `#linux` exists in the template (incl. workflows and `.template_sync/` outside the frozen resources), the form, the Welcome notebook, the site's `content`, `data`, `scripts`, `tests`, `mkdocs.yml`, `DESIGN.md`, `AGENTS.md`, or any sibling repository under `/home/user`. The only mentions are the planning notes (PLAN.json items 2 and 3, written for a future site change); the site's planned deep links must use the new anchors.

## 4. use_cases.md (cfa02c6)

The linked screenshot of the Bluesky post is replaced by "A Bluesky post about VLab4Mic: [VLab4Mic on Bluesky](https://bsky.app/profile/henriqueslab.bsky.social/post/3mnw2p2j5pk24)." The address was already in the page. Nothing else removed. The file `Use_Cases/VLab4Mic_Bluesky.png` still sits on `doc_source`; removing it is up to the maintainer (it stays in that branch's history anyway).

## 5. Pull request template (94af5a5)

`.github/PULL_REQUEST_TEMPLATE.md` with the three checkboxes worded as in the plan, plus an HTML comment telling the reader that repositories created from the template inherit the file. `.github/CONTRIBUTING.md` line "Update documentation as needed" now carries the same prompt (file keeps its CRLF line endings, so the diff is one line).

## 6. CREDITS draft

`/home/user/labconstrictor-site/planning/doc_source-CREDITS.draft.md`: one empty block each for the logo and the comic (creator named only if they agree, rights holder, licence, generative tools, master file, reuse by apps built from the template) plus notes. Nothing filled in. The `doc_source` branch was not touched.

## Left out on purpose (could not be verified in code)

- Any macOS or Windows dialog wording ("SmartScreen", "unidentified developer"), install durations, "expected output" lines, "Check that it worked" paragraphs for install and for synchronisation (what the "Run workflow" run prints), macOS and "browser stays empty" troubleshooting. These wait for the clean installs (decision 24).
- Plan items 5 (apart from the headings), 6 (apart from the GIF sentence), 8's "Next to /submit/" and the other items of plan 6 and 8 that were not in this task's list.
- "Run the bottom cell" in `notebook_upload.md` ("which notebook is meant" needs the authors).

## Decide / needs the maintainer

1. **Two template pages are byte-locked by migration resources and tests, so they were not edited.** `.tools/docs/template_synchronization.md` must equal `.template_sync/resources/v0_1_11_to_v0_1_12/.tools/docs/template_synchronization.md` (`tests/test_template_sync_token_integration.py:133-150`), and `.tools/docs/app_manifest.md` must equal its 0.1.15 resource (`tests/test_template_sync_0_1_15.py:27-37`, `MANAGED_FILES` in `.template_sync/migrations/v0_1_14_to_v0_1_15.py`). Consequences: (a) the title of the step page stays "Enable automatic LabConstrictor template updates", which is why "Keep your app up to date" is a separate short page; (b) the plan's fixes to `template_synchronization.md` ("the following video", the footer) are not applied, and its footer ("Create repository" / "Documentation home" / "Initialise repository") still prints as literal text on the site and points to the old neighbours on GitHub; (c) the "Previous" link of `app_manifest.md` still points to `initialise_repository.md` (its "Next" is already right), and the plan's "Next to /submit/" is not added. Options: a future template migration that refreshes both resources together with the tests (the clean way), or a site-side fix for (b): extend `NAV_BLOCK` in `scripts/lcsite/guides.py` so it also strips a centred block that contains "Documentation home" (today it matches only the capitalised words Previous, Next, Home), keeping the `check_design` exception.
2. **The root `README.md` still treats synchronisation as step 2 of the Quick Start** and says "Complete the one-time ... setup after creating your repository" (lines 39 and 50). I could not change it (outside the allowed files, and the site's `citation.check_template_readme` reads that README). It now disagrees with the docs.
3. **Installer images are chosen in the initialisation form** (`app.py:892-910`), yet the README and pager now list "Customise the installer images" after "Create installer files", as the plan asks. `initialise_repository.md` still links to it. Likewise "Upload external code" is now after the first release; no workflow needs `src` at upload time (only `update_on_src_change.yaml` reacts to it), but a notebook that imports that code is not checked by me. Confirm that this order is wanted.
4. **The pull request template is inherited by every repository created from the template** (nothing removes `.github/` files at initialisation), as `CONTRIBUTING.md` already is. I added a deletable comment saying so. Decide whether app repositories should get it or whether the initialiser should drop it.
5. `Welcome_template.ipynb:21` "Test Connection" fix (see above) needs the maintainers' go-ahead because it propagates to apps via template sync.
6. The reference pages (tips, examples) have no hand-written footers, so GitHub readers do not see the site's pager chain through them; this was already so.
