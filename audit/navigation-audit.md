# LabConstrictor website: navigation and usability audit

Date: 2026-10-10. Method: crawl of the built site (36 pages) plus scripted persona runs in a headless browser (desktop 1280 px, phone 390 px), screenshots of every changed page. Findings are marked FIXED (changed in this round), OPEN (needs a decision or work in another repository) or OK.

## 1. As a user

| # | Persona and task | Finding | Status |
|---|---|---|---|
| U1 | Biologist on a Mac: install NucleiSky | Home → "I want to use an app" → App Centre → app page: 2 clicks. The macOS tile is shown with two buttons (Intel first). A Mac cannot tell Intel from Apple Silicon in the browser, so the hint line stays necessary. The app page had **no link to the install guide** (only to the notebook guide). | FIXED: "Need help installing? See the install guide" under the downloads |
| U2 | Analyst: use an app in napari | The "Soon in napari/Fiji/QuPath" chips on an app page were plain text, a dead end. | FIXED: each chip links to its guide |
| U3 | Anyone: find all the documentation | The top menu had two items (Use, Build) that were separate landing pages without the docs sidebar the user liked; no single entry to "everything". | FIXED: one **Docs** menu entry; the Docs front page and the Use/Build pages all show the full docs sidebar (both tracks, collapsible); Use/Build stay reachable from the sidebar, the Docs page, the footer and the home page |
| U4 | Phone user in a guide | The docs menu was at the very bottom (2267 px down a 3209 px page): nobody would find it. | FIXED: folded "Docs menu" drawer above the content on phones |
| U5 | Phone user: top menu | Burger opens Home, Apps, Docs, Ecosystem, Submit. | OK |
| U6 | Stuck user searches "protected" / "colab" | Search works (24 results for "colab", all from the guides; the index also holds the app pages and hubs). | OK |
| U7 | User wants the testing/maintenance apps | Playground and Demo were mixed in with analysis apps. The lead said "4 apps" while the filter said "6 of 6". | FIXED: separate "Testing and maintenance" group with a Testing badge; lead says "4 apps ..., and 2 for testing and maintenance" |
| U8 | Visitor wants the GitHub repository of a part | Only the whole card linked out. | FIXED: GitHub badge (icon + repository name) on every ecosystem card and on every app page |
| U9 | Visitor in the Ecosystem looks for the Playground | Missing. | FIXED: "Test and maintain" group |
| U10 | Keyboard or screen-reader user | Skip link, one `main`, one `h1`, every image has alt text. The previous/next pager and the docs menu were unlabeled landmarks. | FIXED: labelled "Docs" and "Previous and next guide" |
| U11 | Reader of a guide page | Menu entry and page title disagreed on 15 of 22 build pages (e.g. menu "Upload your notebooks", page "Add or Update a Notebook"). | FIXED: menu and pager use the page's own first heading |
| U12 | Reader of a guide page | Menu and the footer called the same place "Use", "Use an app" or "Docs". | FIXED: menu *Docs*; footer lists Docs, Use an app, Build an app |
| U13 | Reader looks for the Ecosystem from the footer | Missing in the footer. | FIXED |
| U14 | Reader wants to correct a page | No "edit" link anywhere. The theme's own edit link would have pointed to generated files. | FIXED: "Edit this page on GitHub" on every page, pointing to the real source (template doc, plugin repo guide, the app's manifest, a data file); `check_site` fails if one points into generated files |
| U15 | Doc texts | The template docs mixed title case and sentence case, one H1 started with an emoji, and the actions overview was titled "Check Workflow Status & Troubleshooting". | FIXED: 14 titles normalised in the template (LabConstrictor#22) |
| U16 | Install guide | `data/install.yaml` was a hand-kept copy of the template's download guide. | FIXED: the template now has a generic `install.md`; the site imports it and the copy is deleted; app pages link to it instead of repeating the steps |
| U17 | Old addresses | No redirect mechanism; a template file renamed changed a public URL. | FIXED: `data/redirects.yaml` writes redirect pages; the build checks them |

## 2. As a developer or maintainer

| # | Finding | Status |
|---|---|---|
| D1 | Three places defined navigation labels. | FIXED: the footer is built from the menu in `mkdocs.yml`; menu titles of guides come from the pages' headings |
| D2 | The structure of the "Build" sidebar is the template README's structure; a docs page that the README does not list never reaches the site and nothing said so (`use_cases.md`). | FIXED: the build prints a WARNING for each unlisted template page; `use_cases.md` was reported, and is now listed in the template docs index (LabConstrictor#22) |
| D3 | The README had install and render commands and no map of "where do I edit this". | FIXED: README rewritten around what the site is and a table of where to edit each thing |
| D4 | The coding rules (annotations, docstrings, function and file length, no catch-all except, no `.get(key, default)`) were only written down. | FIXED: `tests/test_code_rules.py` enforces them on every test run and every build, and checks that the checker itself works |
| D5 | `page.edit_url` of the theme ignores a front-matter `edit_url`; any edit link rendered by the theme pointed at `docs/...` generated files. | FIXED (own link; theme button not used); regression check in `check_site.py` |
| D6 | The snapshot gained `section`; an old snapshot would have been accepted silently. | FIXED: `SNAPSHOT_FORMAT` is 2, `build_site.py` refuses other formats |
| D7 | `check_site.py` found dead links but not navigation rules. | FIXED: it now fails on a page without exactly one current menu entry (this caught app pages not highlighting Apps) and on a page not reachable from the home page in 3 clicks |
| D8 | A failed daily build notified nobody. | FIXED: it opens or updates an issue |
| D9 | Status text on ecosystem cards was free text. | FIXED: limited to Experimental, Available, Install from GitHub, Deprecated by the project schema (the value is still the project's claim) |
| D10 | Workflow actions were not pinned to commit SHAs. | FIXED: pinned, with monthly Dependabot updates |
| D11 | The site's default branch on GitHub is still the feature branch; scheduled workflows run from the default branch. | OPEN (a setting) |

## 3. Screenshots

`previews/qa/`: `guides-*` (Docs front page), `use-*`, `build-*`, `apps-*`, `ecosystem-*`, `guides__napari-mob.png` (phone drawer), `search2.png`.
