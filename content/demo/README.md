# Demo assets (NucleiSky 2D registration on real images)

Everything in this folder is **generated** by `tools/demo_assets/make_demo_assets.py` and is committed so the site build never needs numpy or NucleiSky. Do not edit by hand: `example.json` records the SHA-256 of every input and the bytes of every image.

## What the example is

- **Reference**: a fluorescence image of nuclei, 1266 × 2970 px, calibrated 1.3205 µm/px (read from the TIFF's own resolution tag).
- **Query**: a 200 × 200 px image of nuclei, calibrated 1.1622 µm/px (also from its tag). It is the kind of file the NucleiSky notebook's *Generate Random Crop* makes; its exact origin is stated by the maintainers, not by this tool.
- **Masks**: label images supplied with the data (4387 nuclei in the reference, 30 in the query). Segmentation was **not** run again: the notebook's *Load Existing Masks* mode is replicated.
- **Registration**: the released NucleiSky 2D code (commit recorded in `example.json`), Option B (adaptive matching), default configuration, seed 0. Result: matcher *quad* after *triangles* and *graph* did not succeed; 26 of 30 nuclei are inliers; mean error 0.264 µm. The run is deterministic (two runs gave identical numbers).

## Files

| File | What it is |
|---|---|
| `reference_full.webp` | the whole reference field, grey, 633 px wide |
| `reference_roi.webp`, `reference_roi_green.webp` | the 549 × 549 px region NucleiSky exported around the match (exported by NucleiSky with a 150 px margin; its position in the reference is in `example.json`), grey and green, shown at 2× |
| `aligned_roi.webp`, `aligned_roi_magenta.webp` | the query warped onto that region by NucleiSky's transform, grey and magenta, transparent outside the footprint |
| `query.webp` | the query (a generated random crop), shown at 3× |
| `nuclei_outlines_roi.webp` | (generated, not used on the page) outlines of the reference nuclei in that region (from the supplied masks) |
| `example.json` | inputs (SHA-256), pixel sizes, transform, attempts, footprint corners, display windows |

Display only: intensities are stretched linearly between the 1st and 99.8th percentiles; images are enlarged with bicubic interpolation and saved as WebP. No value shown on the page is computed from these images.

## Provenance and rights

**Reference image = Dataset 1 of the NucleiSky paper**: a tiled widefield image of a DAPI-stained HUVEC monolayer (fixed with 4% paraformaldehyde, DAPI D1306; ibidi chamber). Nikon Eclipse Ti2-E, NIS-Elements AR v6.10, 10x/0.3 Plan Fluor, Hamamatsu Orca Flash4.0 V3, Lumencor Spectra X (395 nm line, DAPI filter set), 2x2 binning, 12-bit data in a 16-bit container. Stitched mosaic exported for analysis; the reference used here measures 1,266 x 2,970 px = 1,671.8 x 3,922.0 um at 1.3205 um/px. Nuclei were segmented with NucleiSky's threshold-and-watershed backend (4,387 nuclei). (Description supplied by the maintainer from the paper, 2026-10-11.)
**Deposit**: Zenodo, doi:10.5281/zenodo.20721416, "Data associated with NucleiSky enables cross-scale multimodal registration of microscopy data using nuclei constellations", published 2026-06-16, access open, **licence CC BY 4.0** (checked on the Zenodo record). Reuse needs attribution: cite the deposit and the NucleiSky paper (doi:10.1242/jcs.265152) wherever the images are shown.
**Query image**: made with NucleiSky's *Generate Random Crop* from this reference (maintainer's statement).
The TIFF headers contain instrument metadata that is deliberately not published (the WebP files carry none).

## What the page shows

The page shows **one** matcher, **quad**, which registers this crop (26 of 30 nuclei are inliers, mean error 0.264 um). It is not a benchmark. For transparency, `example.json` still records that, with NucleiSky's default settings, graph, triangles and hashing did not succeed on this crop; the page need not show that.

## Regenerate

See `tools/demo_assets/make_demo_assets.py` (arguments are required; there are no defaults). The raw TIFFs are not in this repository.
