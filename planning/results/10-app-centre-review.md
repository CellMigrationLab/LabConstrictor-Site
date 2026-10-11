# Review of the App Centre, citation, related-projects, docs-page and front-end changes (6a446f0..HEAD)

Read-only review. Nothing in the repo was edited, and `build/` was not touched; the only file written is this report. Evidence below comes from running code against `build/snapshot.json`, from the built `site/`, and from Playwright (Chromium, 1200, 390 and 320 px). Unit tests pass (149 OK) and `check_site.py` reports 0 problems, so every item below is something the existing checks cannot see.

Severity key: bug, honesty, security, rule, polish. Items are ranked within each group.

## Bugs and honesty problems (visible to visitors)

1. **honesty/bug: `platforms` makes the page say "No installer in this release." when the release has one.** `pages_get.py:40-46` (`os_tile`), with the filter in `cards.py:111` (`offered_assets`).
   - Evidence: NucleiSky with `distribution.platforms: [macos-arm64]` renders Windows and Linux tiles that say "No installer in this release." The release does have them; the authors just do not support them. The unsigned-installer hint for Windows and the `bash <file>` hint for Linux still print under that text.
   - The same case also leaves the macOS hint "Not sure which? ... Intel, or M1 and later" next to a single button and the Intel note.
   - Fix: `os_tile` should know why it is empty ("The authors do not offer an installer for this system" when `platforms` excludes it, "No installer in this release" otherwise), and should drop the hint when there are no buttons.

2. **honesty: the Colab note claims a desktop app that may not exist.** `pages_get.py:21-22` and `:66`.
   - Evidence: a Colab-only app (`release=None`, `distribution={colab: [...]}`) gets "...The desktop app runs on your computer." under its notebooks.
   - Fix: add that sentence only when `dist.get("installer")`. Also, for a Colab-only app the "Get it" section has no sentence that says there is no installer.

3. **honesty: "The installer is not code-signed" is stated as fact for every app.** `pages_get.py:16` (the Windows hint).
   - The only source is the template's install guide ("The installers are not code-signed yet"). An app's authors build and may sign their own installer. The macOS hint does not make the claim, while `using-apps.md:25` says "Windows and macOS warn".
   - Fix: say "Installers made with the LabConstrictor template are not code-signed yet, so Windows may warn you", or drop the claim and keep "Windows may warn you".

4. **honesty/bug: the catalogue description and JSON-LD overclaim systems and category.**
   - `catalogue_text.py:26-29` (`systems`) reads `release["assets"]` instead of `offered_assets`.
     - Evidence: with `platforms: [macos-arm64]`, `catalogue_text.systems([app])` returns `['Windows', 'macOS', 'Linux']`. The App Centre meta description would say "install them on Windows, macOS or Linux", while `jsonld()` for the same app says `"operatingSystem": "macOS"`.
     - Fix: use `offered_assets(a)`.
   - `pages_apps.py:75-76` sets `applicationCategory: "ScientificApplication"` for every non-testing app, including `kind: game`, `training` and `utility`. That is a claim the data does not support (a game is printed as a scientific application).
     - Fix: set the category only for `SCIENTIFIC_KINDS`, or map each kind to its own category.
     - Also `url` is the GitHub repo, not the page's own address; consider `sameAs` for the repo.

5. **honesty: the home hero now says more than the plugin stage supports, and three wordings disagree.**
   - `pages_site.py:41-45`: "Plugins let apps that declare tools work inside napari, Fiji and QuPath; the stage of each plugin is on the Ecosystem page."
   - `pages_site.py:68`: "Apps that declare tools also run inside napari, Fiji and QuPath" (no qualifier).
   - `data/hubs.yaml:24` and `:73` still say "(soon)".
   - AGENTS.md says "Soon in napari/Fiji/QuPath", while `cards.host_phrase` says "never soon".
   - All three plugins are "experimental" according to the plugin project files (the App Centre chips show it).
   - Fix: pick one wording and take the stage from `host_status` (for example "Experimental plugins let ..."). Update AGENTS.md.

6. **bug: the copy button fails silently.** `lc.js:118-127`.
   - Evidence: with `navigator.clipboard.writeText` rejecting (permission denied, or an insecure context where `navigator.clipboard` is undefined), the page logs an unhandled rejection (`denied`), the button stays "Copy", and the user is told nothing. "Copied" is also not announced (no live region), and the button name is just "Copy".
   - Fix: `try { await ... } catch (err) { btn.textContent = "Copy failed: select the text"; }` (naming the error types), add `aria-label="Copy pip command"`, and add a status element with `aria-live`.

7. **bug: the ARM warning prints an empty list.** `lc.js:44-52`.
   - Evidence: `lcWarnArm` on a tile with `data-arches=""` (a system without an installer, see item 1) on an ARM device gives "This release has  installers only; this device looks like ARM."
   - Also, Windows-on-ARM runs x64 installers by emulation, so the note is unhelpful there.
   - Fix: return early when `offered` is empty, and phrase the note per system.

8. **bug (polish): filter URL parameters with no matching option leave the select blank.** `lc.js:99`.
   - Evidence: `apps/?route=bogus` and `apps/?kind=game` give `selectedIndex === -1` (an empty-looking select) and the parameter is silently dropped from the URL (`params.get(key) || ""`). The page would be correct, but the control shows nothing.
   - Fix: after setting a select, if `el.selectedIndex < 0` set `el.value = ""` and say so in the count line (or leave it unselected explicitly).
   - Related: `history.replaceState` at `lc.js:110` strips the hash and every unknown parameter on load (`apps/?q=nuclei&route=pip#cite` becomes `?q=nuclei&route=pip`). Use `location.hash` and only touch our own keys.

9. **bug (polish): the count line misleads in two cases.** `lc.js:79-82`.
   - "Showing 1 of 1 apps" (no singular).
   - `?q=playground` gives "Showing 0 of 4 apps, and 1 more for testing and maintenance" while the main group is hidden and no empty message is shown. Verified in the browser at 390 px: only the heading "Testing and maintenance" is visible below the filter.
   - Fix: use "Showing N of M apps" with plural(), and when `shown === 0 && testingShown > 0` say "No main app matches; 1 for testing and maintenance below".

10. **bug (polish): the "Links" row can start with a separator.** `pages_apps.py:47-49`.
    - Evidence: an app with no homepage, no docs_url and `has_issues=False` (VLab4Mic without its homepage): `<dd> · No issue tracker on GitHub</dd>`.
    - Fix: build the list, then append the no-tracker note as an item.

11. **bug (polish): release tags get a doubled "v".** `cards.py:105-108`.
    - Evidence: a release with tag `v1.0` prints "vv1.0 · 7 July 2026" in the card, on the app page and in the cite sentence. `downloads_table` prints "Version v1.0", so the two disagree for the same release.
    - Fix: `tag if tag.startswith("v") else "v" + tag`, or print the tag verbatim everywhere.

12. **honesty: the help page and hub notes promise an issue tracker that may not exist.** `content/guides/help.md:3`, `data/hubs.yaml` (use `help`).
    - "open an issue in the app's repository" is unconditional, but VLab4Mic has `has_issues=False` (the app page says "No issue tracker on GitHub"; `using-apps.md` is already conditional).
    - Fix: make the sentence conditional ("if it has one; otherwise follow the link on the app's page").
    - Also `help.md` "Your own app" link text "Check workflow status and troubleshooting" does not match the target's first heading "Check the status of GitHub workflows" (AGENTS: titles never disagree).

13. **honesty: wording problems in the related-projects data.**
    - Against the project's own rule ("no maintenance/popularity/superiority", "no address in prose", "describe each project in its own terms, never by what it lacks", `data/related-projects.yaml` header):
      - Binder approach: "mybinder.org is a free-to-use BinderHub deployment". It contains a bare domain in prose (the banned regex only matches `http(s)://` and `www.`) and "free-to-use" is a volatile service claim.
      - `closing`: "Cloud notebooks ... are not an option when data cannot leave an institution or are very large. Containers encapsulate the runtime more fully but add setup work ...". This describes other projects by their limits and compares them. It is labelled "our views", but the data-file header forbids the style.
    - `related.py` accepts `fit` text that `pages_related.py:25` lower-cases at the first letter: a `fit` starting with a proper noun ("BiaPy users ...") becomes "biaPy". Also "A good fit when collaborators should open a repository's notebooks..." reads badly.
    - Fix: ban `\b[\w-]+\.(org|com|io|net)\b` in prose, add "free", "widely", "leading", "maintained", "actively", "mature" to `BANNED_IN_PROSE`, and do not lower-case the first letter if the second is upper-case or the first word is a project name.

## Security and untrusted input

14. **security (low): trailing newline passes every schema pattern, and the value reaches an href.** `schema/labconstrictor-app.schema.json` patterns `pip`, `doi`, `https`, `repoPath`, `orcid` use `$`, and Python's `re` lets `$` match before a final `\n`.
    - Evidence (validated with the real `validate.check`): `pip: "pkg\n"`, `docs_url: "https://x.org/a\n"`, `doi: "10.1234/abc\n"` and `icon: "a.png\n"` are all accepted. `pip_block("pkg\n")` renders `<code>pip install pkg\n</code>` and `href="https://pypi.org/project/pkg\n/"`.
    - Not exploitable (esc, `quote()` and browsers strip it), but it breaks the "checked against schema" promise and the copy button copies a newline.
    - Fix: validate with `fullmatch` in `validate.check` after schema validation (or use `(?!\n)\z`-style patterns), or add `strip` checks.

15. **security (low): `docs_url`, `homepage`, notebook and DOI addresses accept credentials, and no check forbids other schemes in the built HTML.**
    - Evidence: `docs_url: "https://user:pw@evil.example/"` passes the schema and is shown as the "Documentation" pill.
    - `check_site.link_problems` skips every href that has a scheme (`check_site.py:93-94`), so a `javascript:` or `data:` href elsewhere on a page would pass. This does not currently happen: `https://` is forced by the schema, `docs`/`site` in related-projects are `startswith("https://")`, and `github_view` only builds `https://github.com/...`.
    - Fix: in the schema `https` pattern exclude `@` in the authority (`^https://[^\s/@]+(/[^\s]*)?$`), and add one `check_site` rule: every `href` is relative, `#`, `mailto:` or `https://`.

16. **security (low): `github_view` can point outside the notebook's repository.** `pages_get.py:49-52`.
    - Evidence: `https://colab.research.google.com/github/../x/blob/main/a.ipynb` becomes `https://github.com/../x/blob/main/a.ipynb`, which browsers normalise to `https://github.com/x/blob/main/a.ipynb`.
    - Still github.com, so no escalation. Fix: require `[A-Za-z0-9_.-]+` and reject `.`/`..` segments in `COLAB_FILE`.

17. **security (info): `check_site.escaping_problems` is narrower than the rule.** `check_site.py:104-121`.
    - It only compares manifest strings containing `<`, `>` or `"`, against the app page. The release `tag`, asset names, `app["repo"]`, related-projects text and `site.yaml` citation also reach HTML (all go through `esc`, I checked each), but nothing would catch a future regression for them. `'` and `&` are not in `UNSAFE` either.
    - The `<title>` is built with `page.title | striptags` (not `| e`) in `overrides/main.html:7-8`, while `og:title` uses `| e`. A name such as `A < b & "c"` is printed raw in `<title>`. I could not turn that into script execution (title is RCDATA and `striptags` removes whole tags), but use `| e` for consistency.

Everything else that carries author text goes through `esc` or `json.dumps` with `<`, `>`, `&` escaped: the pip name and PyPI href, `github.com/{repo}` text, `citation.doi_link` (verified: `10.1234/a b<c>"'#?%` becomes `a%20b%3Cc%3E%22%27%23%3F%25`), search words (`data-search` attribute and the JS empty-state text via `textContent`; the query `<img src=x onerror=alert(1)>` renders as text with no error), JSON-LD, `data-arch`, `data-os` and the screenshot attributes.

## Rule violations the tests cannot see

18. **rule: `lc.js` is outside every rule check, and breaks the rules in AGENTS.md.** `tests/test_js_rules.py` reads only `content/demo` and `content/how`.
    - `lc.js:30` has a `catch` (re-throws, but the rule says no `catch`), `lc.js:99` has `params.get(key) || ""`, and `lc.js:31` returns null on `NotAllowedError`.
    - Eight functions have no `/** */` comment with `{type}` and `@returns` (`lcFold`, `lcInitDownloads`, `lcInitFilter`, `lcInitCopy`, `lcInit`, `lcInitDrawer` and others).
    - Unhandled rejections: `lcInitDownloads` calls `lcInitSystem()` without handling its promise (`lc.js:68`); `lcArchitecture` re-throws unknown errors (`:32`). A `TypeError` from `getHighEntropyValues` becomes an uncaught rejection.
    - Fix: add `docs/assets/javascripts/lc.js` to `FILES` in `test_js_rules.py` and fix what it reports; at least JSDoc and a documented decision about the one `catch`.
    - Latent: `lcInitMenu` has no ready guard. I called it twice and the Enter key then toggled the menu twice (net no change). It is not hit today (`mkdocs.yml` has no `navigation.instant`, though `lc.js:3` says it re-runs after instant navigation), but would be if that feature is enabled.

19. **rule: `test_code_rules.py` misses `.get(key)` with one argument and `x or default`.** `tests/test_code_rules.py:44`.
    - Not flagged, and present: `m.get("authors")`, `m.get("description")`, `m.get("docs_url")` (`pages_apps.py:43-58,99`), `dist.get("installer")` (`pages_get.py:81,89,101`, `cards.py:23`, `catalogue.py:61`), `esc(app["license"] or "Not stated")` (`pages_apps.py:39`), `entry.get("featured")`, `manifest.get("icon")` (`catalogue.py:111-114`), `(a.get("class") or "")` (`check_site.py:50-54`).
    - These are optional fields, so each is defensible, but the sibling code uses `"x" in m` / `optional_list`, and the rule text says optional fields are "checked explicitly with `optional_list` or `in`".
    - Fix: make the test flag one-argument `.get` and `or "<literal>"` outside an explicit allow-list, and change those lines.
    - The checker also misses `except (Exception, X)` and `except builtins.Exception` (`getattr(node.type, "id", "")`).

20. **rule: silent fallbacks in `check_site.py`.**
    - `search_index_problems` (`check_site.py:190`) accepts two index layouts (`items["items"] if "items" in items else items["docs"]`), which is the "legacy alias" the rules forbid. It also skips a hub silently when its location is not in the index (`if track + "/" in texts and ...`), so the check would pass vacuously if the index format changed. I confirmed that today `use/` and `build/` are present and the card text is not (the check works now), and the substring check does work for raw text. It compares only the first 40 characters of each card.
    - `literal_markdown_problems` (`check_site.py:171-180`) returns an empty `main` for a page without `<main` and skips it silently.
    - `guide_shape.warnings` is a printed list on every run (15 lines, stderr, exit code 0). Its match is exact (`h in options`), so "What you need before you start" would be reported missing. The `install` guide reports all three missing because it only has Windows/macOS/Linux/Next headings.
    - Fix: fail on an unknown index layout and on a missing hub location; use `startswith` or a regex for the guide headings; decide the date on which the warnings become failures.

21. **rule (polish): other items.**
    - `related.py` does not enforce what DESIGN.md says about order ("entries alphabetical within a group", "`h3` groups in a fixed order"): swapping two entries or two groups still builds. Add a check (`names == sorted(names, key=str.casefold)`) and a test.
    - `related.py` also does not check that `group["key"]` is a unique slug (it becomes `id="related-<key>"`), that `reference` is a non-empty string, that `docs`/`site`/`repo` are strings (non-strings crash with `AttributeError` instead of naming the entry) or that `checked` is not in the future.
    - `pages_related.py:26` uses `strftime("%-d ...")`, which is glibc-only; `text.long_date` exists.
    - `hubs.py:82`: `- ({"lead"} if name == "docs" else set())` is dead, since `lead` is already in `HUB_KEYS`; and `check_hub` does not check required keys.
    - `hero_also()` (`pages_site.py:41-45`) produces "inside  and X" if only one program is in `data/hosts.yaml`.
    - `citation.check_template_readme` compares only the DOI string, though `site.yaml` says the whole block is "copied" from the README; the author list and title can drift. (They match today: I compared them with `/home/user/LabConstrictor/README.md`.)
    - AGENTS.md is stale in two places: "the OS tile's short hint lines are in `pages_apps.os_tile`" (now `pages_get.os_tile`) and "Host chips ... (Soon in ...)". `content/guides/help.md` is missing from the "Hand-written here" list.

## Correctness and logic

22. **bug (low): schema cannot express ARM platforms.** `labconstrictor-app.schema.json` `platforms` enum has only `windows-x86_64`, `macos-arm64`, `macos-x86_64`, `linux-x86_64`.
    - `assets.INSTALLER` and `SYSTEM_LABELS` handle `windows-arm64` and `linux-arm64`. An author who releases ARM installers and sets `platforms` cannot list them, so `offered_assets` drops them. Add the two values (and a test), or document the limit.
    - The `dependentRequired` and `anyOf` rules are right: `{}` is rejected, `{platforms: [...]}` without `installer` is rejected, `installer: false` is rejected, duplicates are rejected, and `colab + pip` is accepted.

23. **polish: the "no system" sentence is ungrammatical.** `pages_get.py:84`: "Installers are for Windows, macOS and Linux computers or open a notebook in Colab below." Fix: "...computers. Open a notebook in Colab below instead." Also, `.lc-ostile.is-yours::after` ("Your system") is generated content only, so it is not reliably read by screen readers, and the label asserts a guess (a Windows ARM or Linux tablet in desktop mode is "your system").

24. **polish: "SHA-256" column honesty and validation.** `assets.py:19-22`, `pages_get.py:109-114`.
    - The digest is GitHub's asset digest, not one the authors publish, but the cell says "not published" when absent and the intro says nothing about the source. A hash served on the same page as the file does not prove who made it. Say "listed by GitHub".
    - `sha256_of` does not check that the value is 64 hex characters (`sha256:zz` is shown as is) and silently returns `None` for other algorithms.
    - `text.megabytes` docstring claims 10**6 "as GitHub and file managers show them". Windows Explorer labels MiB as "MB", so Windows users will see about 303 MB for the 317.5 MB NucleiSky file. I could not verify the GitHub claim from here; drop it from the docstring or say "decimal megabytes".

25. **polish: other wording points.**
    - `pages_get.py:99-102`: "after installing, open the app from your Start Menu or Applications folder. Its Welcome notebook lists what it can do" is shown for every app with an installer. Linux has neither, and `using-apps.md` says "run its first cell" (the template guide agrees: "Once you run the welcome notebook, a dashboard will show a list").
    - `pages_apps.py` `NOTICE` sits below the whole grid and the testing group, after the cards a visitor would click. The words "Apps are listed after automatic checks" omit that a maintainer adds the registry entry. Both are acceptable; consider placing it before the grid.
    - `catalogue_text.get_sentence`: "Install one in a few clicks, open it in Colab, or install it with pip." mixes "one" and "it". Home hero "No Python or pip needed." sits next to a pip route.
    - Home "Works where you work: Desktop installers, Google Colab and pip." (`pages_site.py:67-68`) is hard-coded, while the rest of the catalogue wording is computed by `catalogue_text`. When no app offers pip, this sentence will be wrong.

## Accessibility and layout

26. **a11y (polish): `aria-expanded` on a checkbox.** `overrides/main.html:44`, `lc.js:135`.
    - `aria-expanded` is not a supported attribute for `role=checkbox`, so validators flag it and some AT ignores it. Fix: make the control a `<button aria-expanded aria-controls>` with the same CSS, or drop the attribute and use `aria-controls` only.
    - On phones (390 px) the search button is not available at all: `.md-search` computes to `display: none`, width 0 (Material hides it below 60em and the custom header has no mobile search button). This is not new (the CSS lines are identical at 6a446f0), but it means search is unreachable by touch or keyboard on a phone.

27. **a11y (polish): smaller points.**
    - The App Centre filter is drawn before `lc.js` runs (`.lc-js .lc-filter[hidden] { display:flex }`) and `lc-js` is set by an inline script, not by `lc.js` itself. If `lc.js` fails to load or throws before `lcInitFilter`, a live-looking filter does nothing. Typing before init is overwritten when `el.value = params.get(key)` runs. Set `lc-js` from `lc.js` (and keep it a one-line change), or keep `hidden`.
    - Screenshot `<img alt>` and `<figcaption>` are the same text (`pages_facts.screenshot`), so screen readers read it twice; use `alt=""` when the figcaption says it, or a shorter alt (the DECORATIVE list change in `check_design.py` now forces an alt, so this needs a small rule).
    - Screenshots are placed after the pip block with no heading, so they sit under the "Python package (advanced)" h3 in the outline.
    - The downloads table has no `<caption>`, and no `scope` on its `th`; the `lc-scroll` wrapper is not given `tabindex="0"` and a label (Chromium and Firefox focus scrollers by default, Safari does not).
    - The `aria-live` count is set on page load as well, so a screen reader announces "Showing 4 of 4 apps..." on arrival.
    - Each app card is a single link whose accessible name is the whole text of the card (name, kind, summary, badges, release).
    - The search index (`site/search.json`) holds the filter UI text on `apps/` ("SearchKindAllAnalysis (2)..."), and the 64-character SHA-256 values on each app page; add `data-search-exclude` to the form and the hash cell.

## Checked and found fine

- Escaping: every author-controlled string rendered by `pages_get`, `pages_apps`, `pages_facts`, `citation`, `filters`, `cards`, `pages_related`, `hubs` (hub texts are repo-owned) and `catalogue_text` goes through `esc`; JSON-LD escapes `<`, `>`, `&` (and `json.dumps` escapes non-ASCII, so U+2028 cannot appear). The front-matter description neutralises `"`. `data-arch`, `data-os`, `data-arches` and `data-kind` take only enum or regex-constrained values. The PyPI name is limited to `[A-Za-z0-9._-]` and is safe in the href (apart from the trailing newline, item 14). DOI links are percent-encoded. No `javascript:` or protocol-relative URL is possible through `docs_url`, `homepage`, notebooks, DOI, related `docs`/`site`, and no built page contains one (`https://` is enforced by schema or `startswith`).
- `files come from github.com/<repo>/releases` is supported: `assets.parse_asset` requires each installer URL to start with `https://github.com/<repo>/releases/download/<tag>/`.
- `check_platforms` (a listed platform without a primary installer fails the app loudly), `read_release` (installer claimed but no release or no assets fails), and the `dependentRequired` / `anyOf` rules of the schema work as intended (tested above).
- System detection: `lcSystemFrom` handles iPad-as-Mac, Android, ChromeOS, FreeBSD and empty platform; the node test covers it. `lcMarkChip`, `lcInitSystem` and the unknown-system sentence work in the browser. The filter handles the empty query, whitespace-only query, multiple words, accented input, a query only matching testing apps (see item 9), unknown URL parameters, a hostile query string (no HTML injection, no script error) and repeated parameters.
- Layout at 390 and 320 px: no horizontal overflow on home, apps, three app pages, ecosystem, docs home, help, using-apps, use and submit. Heading order on app pages and the Ecosystem page is h1, h2, h3 with no skips; no duplicate ids. Keyboard order on desktop is skip link, brand, search, menu items, then content; on phones skip link, brand, menu button, content (menu items after the button when open); Enter and Escape on the menu button work.
- Contrast of the new CSS: `--lc-muted` #5b6a61 on #f3f8f1 is 5.3:1, on white 5.7:1; the filter border (#5b6a61 on white) is 5.7:1 (it was #cfcfcf, 1.6:1); the testing and status chip #3b4650 on #e9ecef is 8.1:1; the host chip #8c4d0d on #fff0de is 5.9:1; the filter focus ring and footer ring are fine.
- Completeness warnings: testing apps are exempt; `inputs` and `outputs` are required only for analysis, segmentation and simulation; the license warning is raised only when neither the manifest nor GitHub gives one. (The wording "no license in the manifest" in `problems.md` is slightly off when GitHub is also checked.) The "Not stated" lines appear on the page as the text claims. `has_issues` handling, the Intel note logic, `offered_assets` for `release=None`, and `megabytes` formatting (317.5 MB) all behave as written.
- Citation: `data/site.yaml` author list, title and DOI match the template README's Citation section; `check_template_readme` stops the build if the DOI is gone. The app "How to cite" section shows only the manifest's `doi` and says so otherwise; the version sentence follows `release_line`.
- Docs pages: every row of `help.md` points to a page and section that exist (install `#windows`/`#macos`/`#linux`; "Open Anyway" and the ASN.1 certificate text are present; the napari, Fiji and QuPath guides do end with "If something does not work"). The Welcome-notebook alt text (orange header cells, blue button) matches the picture. The unsigned-installer statement in `using-apps.md` matches the template install guide. The "Colab handled by Google" sentence matches how Colab works.
- Related projects: the disclosure sentence is visible (not a footnote); the shared-authors flags match the disclosure sentence (DL4MicEverywhere, ZeroCostDL4Mic, BiaPy); entries and groups are in alphabetical order today; names are not links; the helper line has its three links; the DOIs and references I know (DL4MicEverywhere, ZeroCostDL4Mic, Binder) look right. I could not check each paper against Crossref from here.
- Code size rules hold for all changed Python files (tests pass); `lc.js` functions are each under 30 lines, and the file is 150 lines.
