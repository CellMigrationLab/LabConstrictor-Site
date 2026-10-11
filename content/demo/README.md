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
| `query.webp` | the query as acquired, shown at 3× |
| `nuclei_outlines_roi.webp` | outlines of the reference nuclei in that region (from the supplied masks) |
| `example.json` | inputs (SHA-256), pixel sizes, transform, attempts, footprint corners, display windows |

Display only: intensities are stretched linearly between the 1st and 99.8th percentiles; images are enlarged with bicubic interpolation and saved as WebP. No value shown on the page is computed from these images.

## Provenance and rights (to be completed by the maintainers)

The images and masks were supplied by the maintainer on 2026-10-11 for this demo. Source of the sample, acquisition details, who may reuse it and under which licence are **not recorded yet**; state them here before the site is listed. The TIFF headers contain instrument metadata that is deliberately not published (the WebP files carry none).

## Regenerate

See `tools/demo_assets/make_demo_assets.py` (arguments are required; there are no defaults). The raw TIFFs are not in this repository.
