# Plugin guide drafts (PLAN item 13), branch claude/festive-cannon-epptr4, no PRs opened

Each branch was restarted from origin/main (the earlier PRs from this branch name were merged). Only docs/user-guide.md was edited.

## napari-labconstrictor: edebc081fcdafad9547234607f27713039f2f32a
- Added to "What you need": napari version bullet. The project's automated type check runs against napari 0.9.2 and magicgui 0.10.2 (a type check only: napari is not run there). The tests install whichever napari pip picks, so no napari version is confirmed by a test run.
- Added to "Open it": "A first run needs an installed LabConstrictor app that declares tools. If none is registered, the app list shows "(none registered)" and there is nothing to run."
- Evidence: .github/workflows/ci.yml:72-77 (pins only in the `typecheck` job; comment "nothing is run"); ci.yml:23 and pyproject.toml:15 (`napari[pyqt5]` unpinned in the test job); napari_labconstrictor/_widget.py:300 ("(none registered)"), _widget.py:298-299 (apps shown only when their schema loaded). No other napari version is recorded anywhere in the repo.
- Left out on purpose: the phrase "tested with napari 0.9.2" (item 13 asked for it). The pin is in the mypy job only, and the test job is unpinned, so that phrase would overstate. The maintainer must decide: (a) keep this wording, (b) pin napari==0.9.2 in the test job and then say "tested with", or (c) say which napari version was used in the hand tests on Linux (not recorded). The "Under heavy construction" banner and "Tested on Linux. Windows and macOS are untested" are unchanged.

## LabConstrictor-Fiji: 022bda8f2467758c560016e9437f211cf9962e04
- Opening sentence: "One Fiji (ImageJ) command runs ..."
- Added to "Open it": "A first run needs an installed LabConstrictor app that declares tools. If none is registered, Fiji shows the message "No LabConstrictor apps are registered" and stops."
- Evidence: src/main/resources/org/cellmigrationlab/labconstrictor/LabConstrictor_Tools.groovy:353-358 (reportNoApps: IJ.error "No LabConstrictor apps are registered in <home>/apps." only when interactive, then finishes with error "no apps registered"; the script is in a repo whose guide already names it).
- No tested Fiji version added: nothing pins one (pom.xml has scijava.version 2.101.0 as build dependency and Java 8 bytecode; ci.yml only builds with Java 21 and lints; its header says "First run still pending", GUI cases need a Fiji install). The hard-coded jar name labconstrictor-fiji-0.1.0.jar (line 22) was left (item 13 suggests "the .jar in target/"; not requested in this task).

## LabConstrictor-Tools: 48d2e4bd48c63d68666eb95bc4811cb86d59872a (fast-forward of the merged branch tip e315320)
- Line 5: "Fiji (ImageJ) and QuPath need no Python at all" (the first body mention of Fiji; the opening paragraph does not mention Fiji, and the H1 and the Fiji bullet at line 16 are unchanged).
- Added after the "Three steps" list: "A first run needs step 1: an installed LabConstrictor app that declares tools. With none registered, the plugin has no app to list."
- Evidence: same napari _widget.py:300 and Fiji groovy:353-358 behaviour; step 1 already said the installer registers the app. QuPath behaviour was not checked (QuPath repo not in scope), hence the neutral "has no app to list". "Fiji (ImageJ)" is not otherwise checked beyond the Fiji repo using ImageJ's `IJ` API in the groovy script. Menu paths (line 15-17) untouched, as item 13 requires a real napari run first.

## Hard-coded site addresses in the three guides
- napari-labconstrictor/docs/user-guide.md:14: https://labconstrictor.cellmig.org/apps/?host=napari . Note: on origin/main this is already the custom domain labconstrictor.cellmig.org, NOT cellmigrationlab.github.io/LabConstrictor-Site/... as PLAN item 13 says. Nothing changed. site_url in /home/user/labconstrictor-site/mkdocs.yml:5 is still https://cellmigrationlab.github.io/LabConstrictor-Site/, so the maintainer should confirm which address is canonical (the guide and the three docs/labconstrictor-project.yaml `$schema` comment lines, line 1 in each repo, use cellmig.org).
- LabConstrictor-Fiji/docs/user-guide.md and LabConstrictor-Tools/docs/user-guide.md: none. No cellmigrationlab.github.io address in any of the three guides.

## Importer check
`grep -rn 'relative links' scripts/lcsite/sources.py` -> line 78 (`check_links`: relative links or pictures stop the build). Ran RELATIVE and check_links from scripts/lcsite/sources.py on the three changed files: no relative links; all 4 / 3 / 8 links are https:// (napari / Fiji / Tools). First H1 unchanged in each; "## If something does not work" headings unchanged; no use of the word "stable" beyond the pre-existing "unlikely to be stable" warning.

## Not done
- QuPath guide (not in this task), jar-name replacement, plain-symptom first bullets (need host maintainers' confirmation), menu-path check.
