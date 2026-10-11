# Notebook widget audit (demo, NucleiSky2DApp and Welcome)

Compared the simulated notebooks (`content/demo/windows/notebook.html`) with the real code cells of `NucleiSky/notebooks/NucleiSky2DApp/NucleiSky2DApp.ipynb` (17 cells) and `app/menuinst/Welcome.ipynb`.
Rule used: a control may be made interactive only if it changes what is shown honestly. The only precomputed result is: random crop, supplied masks, Option B adaptive matching with default settings, quad matcher. A control that would change that result must not appear to compute a new one.

| Widget (real notebook) | Now in the demo | Proposal | Value / cost |
|---|---|---|---|
| Welcome: table, Open the notebook, Test Connection, update scenario | Interactive | Keep | Done |
| Welcome: token field and Load Private GitHub Repo | Disabled field, explained | Keep | Not useful for a visitor |
| Step 0 cell "Initialize Environment" (local Jupyter: skips installs) | Missing: notebook jumps to Step 1 | Add the cell and its short status output (copy the saved output text from the notebook) | High fidelity, low cost |
| Step 1: Crop Strategy toggle (Load External Crop / Generate Random Crop) | Static pill | Make it a real toggle: "Load External Crop" shows Crop Path and the manual Full/Crop µm/px fields; Load & Process stays enabled only for the recorded Random mode, with a line saying why | Medium, low cost |
| Step 1: Random Generator (height, width, max angle, zoom min/max) | Read-only text | Keep read-only (editing would imply a different crop) | Keep |
| Step 1: Fixed Seed checkbox enabling Seed Value (42) | Missing | Add: checkbox enables the seed field (pure UI behaviour, no result change) | Low |
| Step 1: output folder | Read-only text | Keep | Keep |
| Step 2: source toggle (Run New Segmentation / Load Existing Masks) | Static pill, masks only | Make interactive: "Run New Segmentation" shows method dropdown (Cellpose, InstanSeg, Auto-threshold), the method description and the settings panels | **High**: shows the real segmentation features |
| Step 2: method dropdown + InstanSeg panel (Model, Target, Advanced accordion: Mode, Cleanup, Override µm/px, Verbosity) and Auto-threshold panel (Algorithm, Channel, Blur sigma, Min area, Watershed, Peak dist) | Missing | Add as browse-only with the real defaults (read from cell 8); Load button works only in Masks mode, other modes say "no result is precomputed for this option" | High, medium cost |
| Step 2 widgets: Cellpose parameters | Not read yet | Read cell 8 and show only what the code defines | Needed before building |
| Step 3 Option A (Pipeline Overview, Use default settings, per-matcher tabs Graph/Quad/Triangles/Hashing, Run NucleiSky2D) | Missing (Option B only) | Optional: show Option A read-only, default settings checkbox revealing the matcher tabs with default parameters; Run disabled because only quad succeeded on this crop and only the adaptive run is recorded | Medium, medium cost; skip if time is short |
| Step 3 Option B: seed, export margin, Enable Time Limit + Max Seconds, Advanced accordion | Static rows | Make the accordion and the time-limit checkbox work (checkbox enables Max Seconds); numeric fields stay read-only | Medium, low cost |
| Step 3 Option B: Run adaptive button, log, QC figure, overlay | Interactive (delay, precomputed) | Keep | Done |
| Step 3 (Apply saved transform): Transform dropdown, Large Img, Crop Img, Out Dir, Inspect & Validate, axes, µm/px, confirm metadata, export grids | Missing | Optional later: re-apply the recorded transform to the same crop and show the aligned image; label as "same image, no second channel in the preview" | Medium, higher cost; shows reuse across channels |

Suggested order: Step 0 cell; Step 2 toggle with methods and settings; Step 1 crop-strategy toggle and seed; Option B accordion and time limit; then Option A and the apply-transform step only if wanted.
Everything stays static HTML plus `demo.js`; no new result is ever computed.

## Built (this pass)
Step 0 cell and output; Step 1 crop-strategy toggle (starts on Load External Crop as in the real notebook, so the guide leads to Generate Random Crop) with Fixed Seed; Step 2 source toggle (starts on Run New Segmentation) with the method dropdown, the InstanSeg and Auto-threshold settings and their accordions (defaults read from cell 8; Cellpose has no settings panel in the notebook); Option B Advanced Constraints accordion and time-limit checkbox. Controls change only what the widget shows; Run Segmentation stays disabled and the load buttons work only for the recorded options. Not built: Option A, apply-saved-transform.
