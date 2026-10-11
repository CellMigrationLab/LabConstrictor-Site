# Clean-install checklist (for the lab member who runs it; decision 24)

Purpose: confirm the lines the guides cannot state until someone has done it. Record the facts below in a pull request description or `planning/results/clean-installs.md`; no screenshot may show personal data.

For every run write: operating system and version, processor (Intel/AMD, Apple Silicon, ARM), browser, app and release, date, who ran it.

## A. Install an app on a clean computer (Windows, macOS Apple Silicon, macOS Intel if available, Linux)
1. Download the installer from the app's page on the site (NucleiSky is the suggested app). Note file name and size shown on the page vs the file on disk.
2. First run: write the exact text and button names of every warning (Windows "protected your PC", macOS "cannot be opened", Linux terminal). Screenshot each.
3. Installer pages: list every page title and option in order; compare with the demo's Windows steps (Welcome, License, Installation Type, Destination Folder, Advanced options, Installing, Finish).
4. Time from the start to "Finish" (and to the post-install command window closing). Was internet needed during install?
5. How do you start the app (Start menu entry name, Applications folder, applications menu)? What opens (terminal window, browser)? How long until the Welcome notebook?
6. Welcome notebook: what is shown after running its first cell; is the table as in the guide?
7. Uninstall: the exact route; does anything remain in the installed-apps list?
8. Anything that failed, with the log (`launcher_debug.log`, `menuinst_debug.log` in the install folder).

## B. First use of an example
9. Run the app's documented example (NucleiSky 2D with the demo image, CellTracksColab with its test dataset). Write the exact output and where results are saved; screenshot the result.
10. Note the hardware used and the run time.

## C. One throwaway author run (GitHub, any account)
11. Create a repository from the template (button labels), run the initialisation form (labels, the "Zzzz" sleep page), accept the pull request, add a small notebook and its `requirements.yaml` with the upload form (exact label: "Validate & Add Submission"?), create a release, watch the workflow, download the installers.
12. Time per stage, human work vs waiting. Which failure messages appeared, with text.

## D. napari, Fiji, QuPath (optional, for the plugin guides)
13. Menu path of each plugin, the first-run message when no app is registered, the host version used. Windows and macOS are untested in the Tools documentation: say which you ran.

Deliver the results; the guide lines that wait for them (macOS and Windows wording, durations, "check that it worked" texts, expected example outputs) will then be written from your notes.
