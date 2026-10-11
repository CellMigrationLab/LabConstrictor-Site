"""Build content/demo/: run the released NucleiSky code on the maintainers' images and masks, then write web images and example.json.

Usage (offline; needs numpy, scipy, pandas, tifffile, scikit-image, matplotlib, Pillow and the NucleiSky source):
    python tools/demo_assets/make_demo_assets.py --reference Image1.tif --query random_crop.tif \
        --masks-reference masks_full.tif --masks-query masks_crop.tif --nucleisky-src <NucleiSky>/src --nucleisky-commit <sha>
"""

import argparse
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import display  # noqa: E402
import registration  # noqa: E402

MARGIN_PX = 150
OUT = Path(__file__).resolve().parents[2] / "content" / "demo"


def sha256(path: Path) -> str:
    """SHA-256 of a file, so the record names exactly which inputs were used."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    """The command-line arguments (all required; there are no defaults to fall back on)."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("reference", "query", "masks-reference", "masks-query", "nucleisky-src", "nucleisky-commit", "work-dir"):
        p.add_argument("--" + name, required=True)
    return p.parse_args()


def load_inputs(args: argparse.Namespace, lib: dict) -> dict:
    """Images, masks, pixel sizes (from the TIFF tags) and the feature tables NucleiSky needs."""
    import tifffile
    data = {"full": tifffile.imread(args.reference), "crop": tifffile.imread(args.query)}
    masks = {"full": tifffile.imread(args.masks_reference), "crop": tifffile.imread(args.masks_query)}
    data["pix_full"] = registration.um_per_pixel(Path(args.reference))
    data["pix_crop"] = registration.um_per_pixel(Path(args.query))
    data["df_full"] = registration.extract_features(lib, masks["full"], data["pix_full"])
    data["df_crop"] = registration.extract_features(lib, masks["crop"], data["pix_crop"])
    data["masks"] = masks
    return data


def footprint(transform: dict, shape: tuple[int, int], origin: tuple[int, int]) -> list[list[float]]:
    """Corners (y, x) of the small image in the exported region's pixel grid: the crop's pixel edges mapped by NucleiSky's A and b."""
    a, b = np.array(transform["A_px"]), np.array(transform["b_px"])
    h, w = shape
    corners = np.array([[-0.5, -0.5], [-0.5, w - 0.5], [h - 0.5, w - 0.5], [h - 0.5, -0.5]])
    mapped = corners @ a.T + b
    return (mapped - np.array(origin)).round(2).tolist()


def write_images(data: dict, exports: dict, origin: tuple[int, int], out: Path) -> dict:
    """Write every web image; returns {file name: bytes} and the display windows used."""
    import tifffile
    stack = tifffile.imread(exports["stack"])
    roi, aligned = stack[0], stack[1]
    inside = aligned > 0
    win_roi, win_full = display.window(roi), display.window(data["full"])
    win_aligned, win_crop = display.window(aligned[inside]), display.window(data["crop"])
    r8, a8 = display.to_uint8(roi, *win_roi), display.to_uint8(aligned, *win_aligned)
    alpha = (inside * 255).astype(np.uint8)
    s = display.ROI_SCALE
    sizes = {
        "reference_roi.webp": display.save_webp(r8, out / "reference_roi.webp", s),
        "reference_roi_green.webp": display.save_webp(r8, out / "reference_roi_green.webp", s, tint=(0, 255, 0)),
        "aligned_roi.webp": display.save_webp(a8, out / "aligned_roi.webp", s, alpha=alpha),
        "aligned_roi_magenta.webp": display.save_webp(a8, out / "aligned_roi_magenta.webp", s, tint=(255, 0, 255), alpha=alpha),
        "query.webp": display.save_webp(display.to_uint8(data["crop"], *win_crop), out / "query.webp", display.CROP_SCALE),
    }
    sizes["reference_full.webp"] = write_full(data["full"], win_full, out)
    sizes["nuclei_outlines_roi.webp"] = write_outlines(data["masks"]["full"], roi.shape, origin, out)
    return {"sizes": sizes, "windows": {"reference_roi": win_roi, "reference_full": win_full, "aligned": win_aligned, "query": win_crop}}


def write_full(full, win: tuple[float, float], out: Path) -> int:
    """The whole reference field as one small grey WebP."""
    from PIL import Image
    im = Image.fromarray(display.to_uint8(full, *win))
    height = round(im.height * display.FULL_WIDTH / im.width)
    im.resize((display.FULL_WIDTH, height), Image.LANCZOS).save(out / "reference_full.webp", "WEBP", quality=display.QUALITY, method=6)
    return (out / "reference_full.webp").stat().st_size


def write_outlines(labels, shape: tuple[int, int], origin: tuple[int, int], out: Path) -> int:
    """Outlines of the reference nuclei inside the exported region, white on transparent."""
    from PIL import Image
    y0, x0 = origin
    edge = display.outline_layer(labels[y0:y0 + shape[0], x0:x0 + shape[1]], display.ROI_SCALE)
    rgba = np.zeros(edge.shape + (4,), dtype=np.uint8)
    rgba[edge] = (255, 255, 255, 255)
    Image.fromarray(rgba).save(out / "nuclei_outlines_roi.webp", "WEBP", lossless=True, method=6)
    return (out / "nuclei_outlines_roi.webp").stat().st_size


def build_record(args: argparse.Namespace, data: dict, best: dict, exports: dict, images: dict, origin: tuple[int, int]) -> dict:
    """example.json: every number the page may show, with where it came from."""
    t, q = exports["transform"], best["match_quality"]
    roi = [int(v) for v in t["bbox_full_px_y0y1x0x1"]]
    return {
        "source": {"nucleisky_commit": args.nucleisky_commit, "entry_point": "nucleisky.nucleisky2d.pipeline.run_adaptive_matching_and_export",
                   "mode": "Load Existing Masks, then Option B (adaptive matching), default configuration, seed %d" % registration.SEED},
        "inputs": {name: {"file": Path(getattr(args, name)).name, "sha256": sha256(Path(getattr(args, name)))}
                   for name in ("reference", "query", "masks_reference", "masks_query")},
        "images": {"reference_px": list(data["full"].shape), "query_px": list(data["crop"].shape),
                   "reference_um_per_px": data["pix_full"], "query_um_per_px": data["pix_crop"]},
        "nuclei": {"reference": int(len(data["df_full"])), "query": int(len(data["df_crop"]))},
        "result": {"matcher": best["matcher"], "scale": t["scale"], "rotation_deg": t["rotation_deg"], "t_um_yx": t["t_um_yx"],
                   "A_px": t["A_px"], "b_px": t["b_px"], "inlier_fraction": q["frac_inliers"], "mean_error_um": q["mean_error_um"],
                   "inliers": int(round(q["frac_inliers"] * len(data["df_crop"]))), "bbox_reference_px_y0y1x0x1": roi},
        "each_matcher": data["each_matcher"],
        "attempts": [{k: h[k] for k in ("matcher", "success", "frac_inliers")} for h in exports["history"]],
        "region": {"origin_yx": list(origin), "size_px": list(data["roi_shape"]), "margin_px": MARGIN_PX, "display_scale": display.ROI_SCALE,
                   "footprint_corners_yx": footprint(t, data["crop"].shape, origin)},
        "display": {"windows_percentiles": [1.0, 99.8], "windows": images["windows"], "bytes": images["sizes"]},
    }


def write_log_and_figure(text: str, figure: Path, out: Path) -> None:
    """What NucleiSky printed (without its number matrices) and its own quality figure, as run_log.txt and qc_figure.webp."""
    from PIL import Image
    keep = [line.rstrip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith(("[", "R =", "ICP", "RANSAC (", "QUAD RANSAC", "QUAD ICP"))]
    (out / "run_log.txt").write_text("\n".join(keep) + "\n", encoding="utf-8")
    with Image.open(figure) as im:
        im.convert("RGB").resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS).save(out / "qc_figure.webp", "WEBP", quality=80, method=6)


def main() -> None:
    """Run NucleiSky, write the images and example.json into content/demo/."""
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    lib = registration.import_pipeline(Path(args.nucleisky_src))
    data = load_inputs(args, lib)
    work = Path(args.work_dir)
    data["each_matcher"] = registration.run_each_matcher(lib, data)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        best = registration.match(lib, data, work, MARGIN_PX)
        figure = registration.save_quality_figure(lib, best, data, work)
    write_log_and_figure(log.getvalue(), figure, OUT)
    exports = registration.read_exports(work)
    import tifffile
    stack = tifffile.imread(exports["stack"])
    origin = display.locate_roi(data["full"], stack[0])
    data["roi_shape"] = stack[0].shape
    images = write_images(data, exports, origin, OUT)
    (OUT / "example.json").write_text(json.dumps(build_record(args, data, best, exports, images, origin), indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
