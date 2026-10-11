"""Run the released NucleiSky 2D code on prepared masks and return its own results (offline tool, not part of the site build).

It mirrors the notebook NucleiSky2DApp.ipynb: 'Load Existing Masks' (no rescaling) followed by Option B, adaptive matching.
"""

import json
import sys
from pathlib import Path

SEED = 0


def um_per_pixel(path: Path) -> float:
    """Pixel size in micrometres, read from the TIFF's own resolution tag; raises KeyError when the file has none."""
    import tifffile
    with tifffile.TiffFile(path) as tif:
        numerator, denominator = tif.pages[0].tags["XResolution"].value
    return denominator / numerator


def import_pipeline(nucleisky_src: Path) -> dict:
    """The NucleiSky functions this tool calls, imported from the given source folder (the released code); raises ImportError."""
    sys.path.insert(0, str(nucleisky_src))
    sys.dont_write_bytecode = True
    from nucleisky.nucleisky2d import config, features, pipeline, preprocess, visualization
    return {"config": config, "features": features, "pipeline": pipeline, "preprocess": preprocess, "visualization": visualization}


def extract_features(lib: dict, masks: "np.ndarray", pixel_um: float) -> "pandas.DataFrame":
    """Nucleus features of a label image at its original scale (rescale factor 1, as in the notebook's existing-masks path)."""
    table = lib["features"].extract_nuclear_features(masks, None, pixel_um, k_neighbors=10)
    return lib["features"].add_centroids_orig_px_columns(table, 1.0)


def match(lib: dict, data: dict, out_dir: Path, margin_px: int) -> dict:
    """Option B (adaptive matching) with the default configuration; exports the aligned region with `margin_px` around the footprint."""
    best, _ = lib["pipeline"].run_adaptive_matching_and_export(
        df_full=data["df_full"], df_crop=data["df_crop"], img_full=data["full"], img_crop=data["crop"],
        pixel_size_full_um=data["pix_full"], pixel_size_crop_um=data["pix_crop"], result_dir=str(out_dir),
        img_full_seg=data["full"], img_crop_seg=data["crop"], pixel_size_full_seg_um=data["pix_full"], pixel_size_crop_seg_um=data["pix_crop"],
        cfg_selected=lib["config"].DEFAULT_MATCHER_CONFIG, base_seed=SEED, margin_px=margin_px, store_full_out=False,
        max_total_time_s=None, ij_percentile_normalize=lib["preprocess"].ij_percentile_normalize)
    if not best.get("success"):
        raise RuntimeError("NucleiSky found no valid transform for these images")
    return best


def save_quality_figure(lib: dict, best: dict, data: dict, out_dir: Path) -> Path:
    """The notebook's own 8-panel alignment figure (original_overlay.png), written by NucleiSky itself."""
    lib["visualization"].show_alignment_original_and_rescaled(
        best, img_full_orig=data["full"], img_crop_orig=data["crop"],
        pixel_size_full_orig_um=data["pix_full"], pixel_size_crop_orig_um=data["pix_crop"], save_dir=str(out_dir))
    return out_dir / "original" / "original_overlay.png"


def read_exports(out_dir: Path) -> dict:
    """The transform JSON, the attempt history and the aligned-region stack that NucleiSky wrote."""
    export = out_dir / "matching" / "adaptive" / "exports_adaptive"
    transform = json.loads((export / "adaptive_best_transform_original.json").read_text(encoding="utf-8"))
    history = [json.loads(line) for line in (export / "history.jsonl").read_text(encoding="utf-8").splitlines()]
    stack = export / "adaptive_best_images_original_roi" / "aligned_on_full_px.tif"
    return {"transform": transform, "history": history, "stack": stack}


def run_each_matcher(lib: dict, data: dict) -> list[dict]:
    """Option A of the notebook: every matcher once with the default configuration (graph also gets the features), as NucleiSky reports it."""
    features = lib["features"]
    kwargs = {"centroids_crop_um": features.extract_centroids_um(data["df_crop"], name="df_crop"),
              "centroids_full_um": features.extract_centroids_um(data["df_full"], name="df_full")}
    rows = []
    for name in ("graph", "quad", "triangles", "hashing"):
        rows.append(one_matcher(lib, data, name, kwargs))
    return rows


def one_matcher(lib: dict, data: dict, name: str, kwargs: dict) -> dict:
    """One matcher's outcome: success flag, inlier fraction, mean error, scale and translation (None where NucleiSky returns none)."""
    extra = {}
    if name == "graph":
        extra = {"features_crop": lib["features"].stack_feature_vectors(data["df_crop"], name="df_crop"),
                 "features_full": lib["features"].stack_feature_vectors(data["df_full"], name="df_full")}
    result = lib["pipeline"].NucleiSky(
        img_full=data["full"], img_crop=data["crop"], ij_percentile_normalize=lib["preprocess"].ij_percentile_normalize,
        pixel_size_full_um=data["pix_full"], pixel_size_crop_um=data["pix_crop"], matcher=name, df_full=data["df_full"],
        df_crop=data["df_crop"], matcher_config=lib["config"].DEFAULT_MATCHER_CONFIG, **kwargs, **extra)
    quality = result.get("match_quality") or {}
    return {"matcher": name, "success": bool(result.get("success")), "inlier_fraction": quality.get("frac_inliers"),
            "mean_error_um": quality.get("mean_error_um"), "scale": result.get("best_scale")}
