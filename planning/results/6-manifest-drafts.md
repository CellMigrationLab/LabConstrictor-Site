# Manifest drafts for six apps ("I draft, owners confirm")

Every app: branch `claude/festive-cannon-epptr4`, one commit on top of origin/main (NucleiSky: on top of the 2 unmerged commits already on the branch), pushed with `git push -u origin claude/festive-cannon-epptr4`. No pull request opened, no other branch touched. Only `labconstrictor-app.yaml` changed; existing fields and comments are untouched (NucleiSky: only the `screenshots` list replaced). All six manifests pass the site validator ("valid"). No `status` was added anywhere, no `authors`, no `distribution.platforms`, nothing about Intel Macs. Every statement below is a close copy of the cited source; owners should confirm.

Branch states found: NucleiSky's branch held 2 unmerged commits (smart microscopy guide, 8b7a258 and caee760) on top of current main, so they were kept and the commit added after them. In the other five repos the branch existed but was fully merged (its pull request merged into main), so it was restarted from origin/main; the push was a fast-forward, no force needed.

Important note on VLab4Mic: the local clone's `origin` pointed at `HenriquesLab/LabConstrictor-VLab4Mic`, an older copy (main be5f6b4, tag 0.1.3, no manifest). The registry and the site use `CellMigrationLab/LabConstrictor-VLab4Mic` (main f0dbfad, release 0.1.5, with a manifest). I changed the local `origin` URL to the CellMigrationLab repository (local git config only) and worked and pushed there.

## NucleiSky (CellMigrationLab/NucleiSky), commit 383ace6

Added (sources: `docs/limitations.md` = L, `docs/2D/data_preparation.md` = D, `docs/exports.md` = E, `docs/qc.md` = Q, `notebooks/NucleiSky2DApp/NucleiSky2DApp.ipynb` = N, cell number):
- `screenshots`: replaced the banner by `docs/assets/2D_QC.jpg` (exists, jpg, 4276 x 1983 px, 800 KB, listed as is; checked by eye: 2 x 4 panels). Caption "2D quality-control figure: the crop, the matching region of the full image, their overlay and an error map (1-SSIM), both ways". Source: Q:109-117 (figure and the panel table: Crop (source), Full ROI (target), Overlay, Error (1-SSIM); second row reverse direction).
- `inputs`:
  - "2D app: two 2D images, a reference image and a partial view (ROI) to place into it": D:8, D:20-23.
  - "Pixel size (µm/px) of each image: read from TIFF metadata, otherwise you must enter it": D:14, D:54, D:226; N cell 4 ("If pixel size metadata is missing ... you must manually enter").
  - "Image files: TIFF / OME-TIFF, NPY, Zarr / OME-Zarr, or standard image formats such as PNG / JPEG": D:82-87.
  - "Nuclei label masks: built-in segmentation (threshold, Cellpose, InstanSeg) or your own masks": D:140-150, D:156-158.
- `outputs`:
  - saved transform (JSON / JSONL) with scale, rotation, translation and match quality: E:47-52, E:161-188.
  - aligned image as TIFF (aligned_on_full_px.tif) or OME-Zarr (aligned_on_full_px.zarr): E:98-101.
  - quality-control overlay figure with an error map (1-SSIM): E:22-23, Q:75, Q:101-105.
  - optional nuclei segmentation masks (TIFF): E:53.
- `limitations`:
  - similarity transform only, no shear, non-uniform scaling or local elastic warping: L:9-15.
  - 2D input must be a single 2D plane, Z-stacks and time series raise an error, RGB converted to grayscale: L:24; D:123-129.
  - at least about 10 points in practice: L:37.
  - crop and full image must truly overlap: L:31-32; D:190.
  - repetitive patterns give a high inlier score but a wrong location: L:41-42.
  - 3D: single uniform scale factor, cannot correct anisotropic shrinkage; at least 4 non-degenerate nuclei: L:61-62, L:67.
- `quickstart` (5 steps, taken from the 2D app notebook's own steps): N cell 2 (Step 0, run the cell to initialize the environment; Colab installs automatically), cell 4 (Step 1, images, pixel size), cell 6 (segment or load masks, centroids), cell 12 (adaptive matching "the recommended starting point for most datasets"), cell 14-15 (Step 3, reuse the saved transform for other channels).

Left out: `status` (nothing in README or docs says experimental / available / deprecated; README:71 only says "3D workflows should be reviewed with manual QC before downstream use"). 3D inputs and outputs (only 2D docs were on the list; 3D facts appear only through the 3D limitation). The README:71 3D-QC sentence (limit of 6 limitations reached). `3D_QC.jpg` (the maintainer asked for the 2D figure only).
To confirm: the quickstart is written from the 2D app notebook, not from the Welcome notebook (which only lists notebooks and offers update checks) or the README Quickstart (which is a choice of setups, not steps). Inputs are prefixed "2D app:" because the manifest covers both apps. Is a 4276-px-wide JPG acceptable for the site, or should a smaller copy be added?

## CellTracksColab (CellMigrationLab/CellTracksColab), commit 35ee25e

Added (all from `README.md`):
- `docs_url: https://github.com/CellMigrationLab/CellTracksColab/wiki` (was not set): README:254 ("Visit the comprehensive wiki").
- `inputs`: TrackMate results as CSV or XML files, and TrackMate CSV in a plate format: README:158, README:235, README:246. CSV files from CellProfiler, ICY, ilastik or Fiji Manual Tracker: README:167-168. Data in the CellTracksColab format (Viewer and advanced notebooks): README:178, README:189. Two-tiered folder hierarchy: README:247.
- `limitations`: "Does not yet support track merging or splitting": README:248.
- `quickstart` (5 steps): desktop app steps README:119-122 (install, launch, "Open the Notebook" in the Welcome dashboard, paste the folder path); Colab steps README:108-111 (Open in Colab, run "Load key dependencies" cell section 1.1, point to Drive data `/content/gdrive/MyDrive/`).
- `screenshots` (3, captions are the README's own figure captions beside each image; I looked at the images and they match): `Wiki/Screenshot1.png` "Compile your data" (README:319-321), `Wiki/Screenshot2.png` "Visualise your tracks" (README:324-326), `Wiki/Screenshot4.png` "Plot track parameters" (README:336-338). All three exist on origin/main.

Left out: `outputs` (the README lists features, e.g. track visualisation, metrics, clustering, UMAP, but never says what files or tables the app produces); `status` (not stated).
To confirm: the quickstart mixes desktop and Colab steps; owners may prefer one route.

## GuessTheCondition (CellMigrationLab/GuessTheCondition), commit 67e07df

Added (README.md = R; notebook `notebooks/GuessTheCondition/GuessTheCondition.ipynb` = N, cell number):
- `inputs`: TIFF images in condition/repeat folders: R:29. 2D, multi-channel, z-stacks / time series as maximum projection: R:41.
- `outputs`: whether conditions can be told apart across repeats with n and 95% interval: R:19; accuracy per repeat and per condition against chance, confusion matrix, decision times (SuperPlot): R:20-22; PDF report: R:23; `game_results.csv` and `session.json` in a folder with your name: R:45.
- `limitations`: each channel contrast-stretched on its own, so no overall-brightness differences: R:41. One or two repeats give no verdict, randomization test exploratory and does not generalise: R:96. Pooled-image test exploratory, false-positive chance higher: R:98.
- `quickstart` (4 steps): R:29 (prepare the images); N cell 4 (Step 1, name, experiment folder, results folder, share of images), cell 6 (Step 2, Start / continue, Submit guess), cell 8 (Step 3, run the analysis).

Left out: `status`, `docs_url` (not stated); the Intel Mac sentence (R:49) on purpose.
To confirm: the "demo experiment" tool (R:61) exists only as a Napari/Fiji/command-line tool, so it is not in the quickstart.

## LabConstrictor_Demo (CellMigrationLab/LabConstrictor_Demo), commit e951e24

The README is only the template stub, so the facts come from the notebook `notebooks/Image_Preview/Image_Preview.ipynb` (N) and `src/labconstrictor_demo/` code:
- `inputs`: "One image file at a time, chosen from disk with the Upload image button": N cell 0 ("request an image file"), N cell 3 (`description="Upload image"`, tooltip "Pick an image from disk"), `widget_utils.py:17` (`multiple: bool = False`), `widget_utils.py:28` (`accept="image/*"`).
- `outputs`: preview in the notebook plus a status line with name, size in pixels and mode: N cell 0 ("displays it inline"), N cell 3 (the "Loaded <name> (<w>x<h>px, mode ...)" message and the preview image).
- `quickstart` (3 steps): the "Run this cell to ..." lines of N cells 1, 2 and 3.

Left out: `limitations` (none stated), `status`, `docs_url`.

## LabConstrictor-Playground (CellMigrationLab/LabConstrictor-Playground), commit fd818b3

Added (README.md = R):
- `inputs`: device chosen in a dropdown (cpu, cuda:0, mps): R:24-25; Feature tour with an image or none (built-in demo image): R:27.
- `outputs`: readout with tick / warning / cross per layer and what to do: R:15, R:42-46; `report.json`, `summary.txt`, `benchmark.png` when there is a benchmark: R:15 and `src/labconstrictor_playground/checks.py:65-70` (docstring of `write_report`); test data files: R:26.
- `limitations`: "OpenCL on macOS is deprecated by Apple and ROCm (AMD) works on Linux only", "this first version checks PyTorch only; TensorFlow is checked inside the apps that use it": R:48.
- `quickstart` (4 steps): R:15 (install, press Check everything), R:42-46 (read the answer), R:15 (attach report.json), R:34 (Napari and Fiji menu paths).

Left out: `status`. Not in the README, but `docs/labconstrictor-project.yaml` (the Ecosystem card file, line 4) says `status: Available` with the comment "Keep the status true". Not copied because the maintainer said testing apps only need inputs/outputs/limitations/quickstart; if you want it, `status: Available` has a source. Also left out: everything about Intel Macs (R:32) and `distribution.platforms`.

## LabConstrictor-VLab4Mic (CellMigrationLab/LabConstrictor-VLab4Mic), commit e72092c

Added (README.md = R, at main f0dbfad):
- `doi: 10.64898/2026.06.02.729521` (as instructed; it is also in the README citation, R:143).
- `inputs`: "A molecular structure from a PDB ID, or your own structure file (.cif or .pdb)": R:21, R:111.
- `outputs`: simulated and noiseless image plus the pixel size: R:95 (also R:67).
- `limitations`: Napari and Fiji tools return a single frame; multi-frame acquisitions and parameter sweeps are only in the notebook: R:112. Default 1000 nm field gives a widefield image of only 10 x 10 pixels at 100 nm per pixel, raise Sample size XY: R:107 (also R:85).

Left out: `status` (R:89 says "Use VLab4Mic from Napari and Fiji (experimental)", which labels the Napari/Fiji tools, not the app, so it was not turned into a status; the maintainer must decide); `quickstart` (decision 2 asked only for the DOI and inputs/outputs/limitations; the README has a literal how-to at R:44-77 that could be used on request); `docs_url` (homepage is already set); screenshots (the README pictures `docs/img/howto_*.png` are screenshots of the Napari/Fiji forms; not asked).

## Things the maintainer must confirm or decide
1. VLab4Mic: repository identity (HenriquesLab copy versus CellMigrationLab); I pushed only to CellMigrationLab.
2. Whether the "experimental" wording in the VLab4Mic README (Napari/Fiji tools) or `status: Available` in the Playground's `docs/labconstrictor-project.yaml` should become a manifest `status`; none was added.
3. NucleiSky quickstart derived from the 2D app notebook; 4276-px figure; 3D inputs and outputs not drafted.
4. CellTracksColab has no stated outputs; Demo has no stated limitations.
5. All texts are drafts for the owners; the YAML strings that contain a colon are quoted.
