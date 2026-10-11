"""The demo's files: copy them into docs/, read example.json, and turn its numbers into the text the three windows show."""

import json
import re
import shutil
from pathlib import Path

from .config import CONTENT, DOCS, fail
from .text import esc

SOURCE = CONTENT / "demo"
OUT = DOCS / "assets" / "demo"
IMAGES = ("install-banner.webp", "install-header.webp", "nucleisky-icon.png", "qc_figure.webp", "seg_figure.webp", "reference_full.webp", "reference_roi.webp", "reference_roi_green.webp", "aligned_roi.webp", "aligned_roi_magenta.webp",
          "query.webp")
SCRIPTS = ("demo-dom.js", "demo-state.js", "demo-render-host.js", "demo-render-notebook.js", "demo-guide.js", "demo-actions.js", "demo.js")   # load order
CODE = SCRIPTS + ("demo.css", "installer.css")
MAX_BYTES = 400_000          # one image above this stops the build: the page must stay light
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")
REQUIRED = {"images": ("reference_px", "query_px", "reference_um_per_px", "query_um_per_px"), "nuclei": ("reference", "query"),
            "result": ("matcher", "scale", "rotation_deg", "b_px", "inliers", "mean_error_um", "bbox_reference_px_y0y1x0x1"),
            "region": ("origin_yx", "size_px", "display_scale", "footprint_corners_yx")}


def copy_assets() -> None:
    """Copy the demo's images, script and style into docs/assets/demo/ (generated). A missing or oversized file stops the build."""
    OUT.mkdir(parents=True, exist_ok=True)
    for name in IMAGES + CODE:
        src = SOURCE / name
        if not src.is_file():
            fail(f"{src} is missing: run tools/demo_assets/make_demo_assets.py or restore the file")
        if name in IMAGES and src.stat().st_size > MAX_BYTES:
            fail(f"{src} is {src.stat().st_size} bytes; the limit is {MAX_BYTES}")
        shutil.copy2(src, OUT / name)


def load_example() -> dict:
    """content/demo/example.json, checked for every key the page uses; raises SystemExit naming the missing key."""
    path = SOURCE / "example.json"
    if not path.is_file():
        fail(f"{path} is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    for section, keys in REQUIRED.items():
        for key in keys:
            if section not in data or key not in data[section]:
                fail(f"{path} has no {section}.{key}")
    return data


def number(value: float, digits: int) -> str:
    """A number rounded for display, with the minus sign kept as a plain hyphen (as NucleiSky prints it)."""
    return f"{value:.{digits}f}"


def values(example: dict) -> dict[str, str]:
    """Every number or phrase a window shows, as display strings, all taken from example.json."""
    r, im, n, region = example["result"], example["images"], example["nuclei"], example["region"]
    y0, y1, x0, x1 = r["bbox_reference_px_y0y1x0x1"]
    log = (SOURCE / "run_log.txt")
    if not log.is_file():
        fail(f"{log} is missing")
    return {
        "run_log": esc(log.read_text(encoding="utf-8").strip()),
        "rotation": number(r["rotation_deg"], 4), "rotation_short": number(r["rotation_deg"], 1), "scale": number(r["scale"], 4),
        "offset_y": number(r["b_px"][0], 4), "offset_x": number(r["b_px"][1], 4), "bbox": f"[{y0}, {y1}, {x0}, {x1}]",
        "matcher": r["matcher"], "inliers": str(r["inliers"]), "n_query": str(n["query"]), "n_reference": str(n["reference"]),
        "mean_error": number(r["mean_error_um"], 3), "pix_reference": number(im["reference_um_per_px"], 4), "pix_query": number(im["query_um_per_px"], 4),
        "reference_size": f"{im['reference_px'][1]} x {im['reference_px'][0]}", "query_size": f"{im['query_px'][1]} x {im['query_px'][0]}",
        "region_px": str(region["size_px"][0]), "query_width_pct": number(100 * im["query_px"][1] * im["query_um_per_px"] / im["reference_um_per_px"] / region["size_px"][1], 2),
    }


def installer_values(apps: list[dict]) -> dict[str, str]:
    """What the Windows installer pages show about the example app: its name, version and installer file (from its latest release) and its licence text."""
    app = next((a for a in apps if a["slug"] == "nucleisky"), None)
    if app is None or app["release"] is None:
        fail("the demo's Install part needs the NucleiSky app and its release in the snapshot")
    exe = next((x for x in app["release"]["assets"] if x["os"] == "windows" and x["name"].endswith(".exe")), None)
    if exe is None:
        fail("the latest NucleiSky release has no Windows .exe installer")
    licence = SOURCE / "license.txt"
    if not licence.is_file():
        fail(f"{licence} is missing")
    return {"app_name": esc(app["manifest"]["name"]), "app_version": esc(app["release"]["tag"]), "exe_name": esc(exe["name"]),
            "exe_size": f"{exe['size'] / 1048576:.0f} MB", "license_text": esc(licence.read_text(encoding="utf-8").strip())}


def footprint_points(example: dict) -> str:
    """The small image's outline in the 549-pixel region, as an SVG `points` string in region pixels."""
    return " ".join(f"{x},{y}" for y, x in example["region"]["footprint_corners_yx"])


def render(template: str, shown: dict[str, str], name: str) -> str:
    """Fill {{key}} placeholders from `shown`; a placeholder without a value stops the build, naming the template."""
    def fill(m: re.Match) -> str:
        """The value for one placeholder."""
        if m.group(1) not in shown:
            fail(f"{name} uses {{{{{m.group(1)}}}}} but demo_media.values() has no such value")
        return shown[m.group(1)]
    return PLACEHOLDER.sub(fill, template)


def read_window(name: str) -> str:
    """content/demo/windows/<name>.html; it must be one element with no blank lines (Markdown would break it)."""
    path = SOURCE / "windows" / f"{name}.html"
    if not path.is_file():
        fail(f"{path} is missing")
    text = path.read_text(encoding="utf-8").strip()
    if "\n\n" in text:
        fail(f"{path} has a blank line; Markdown would cut the window in pieces")
    return text
