"""Write the pictures of the How it works steps (content/how/figures/*.webp): crops of Figure 2 of the LabConstrictor preprint.

The preprint (Hidalgo-Cenalmor et al., 2026, doi:10.48550/arXiv.2603.10704) is licensed CC BY 4.0, so its figures may be adapted with credit.
Usage (needs Playwright with Chromium and Pillow; the figure is downloaded from arXiv first):
    curl -o Fig2.svg https://arxiv.org/html/2603.10704v1/Fig2.svg
    python tools/how_figures/crop_preprint_figure.py Fig2.svg

The boxes are in pixels of the figure drawn 1300 pixels wide; the pictures are saved at twice that size. The numbered circles and titles of the
paper are left out of the crops because the site numbers its steps differently.
"""

import argparse
import io
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "content" / "how" / "figures"
WIDTH = 1300
SCALE = 2
BOXES = {   # file name: (left, top, right, bottom) in the 1300-pixel drawing
    "step-1": (78, 140, 810, 236),    # the notebook, the helper code and the icon (paper step 1)
    "step-2": (56, 482, 826, 656),    # the requirements generator and requirements.yaml (paper step 3)
    "step-3": (56, 272, 832, 438),    # the template, the initialiser form and the pull request (paper step 2)
    "step-4": (56, 695, 832, 806),    # the two uploads and the pull request (paper step 4)
    "step-5": (88, 858, 802, 942),    # the release and its assets (paper step 5)
    "step-6": (4, 1032, 1300, 1260),  # what users get: installers, the app and the notebooks (paper part B)
}


def render(svg: Path, chromium: str | None) -> Image.Image:
    """The figure drawn `WIDTH * SCALE` pixels wide, as an image, in the given Chromium (None: Playwright's own); fails when the browser cannot start."""
    page_html = f'<body style="margin:0;background:#fff"><img src="{svg.resolve().as_uri()}" width="{WIDTH}"></body>'
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        html = Path(tmp) / "figure.html"
        html.write_text(page_html, encoding="utf-8")
        page = p.chromium.launch(executable_path=chromium).new_page(viewport={"width": WIDTH, "height": 900}, device_scale_factor=SCALE)
        page.goto(html.as_uri())
        page.wait_for_timeout(1500)
        return Image.open(io.BytesIO(page.locator("img").screenshot(timeout=120000))).convert("RGB")


def main() -> None:
    """Draw the figure and save one crop per step."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("svg", type=Path, help="Fig2.svg of the preprint")
    parser.add_argument("--chromium", help="path of a Chromium executable (default: the one Playwright installed)")
    args = parser.parse_args()
    image = render(args.svg, args.chromium)
    OUT.mkdir(parents=True, exist_ok=True)
    for name, box in BOXES.items():
        image.crop(tuple(v * SCALE for v in box)).save(OUT / f"{name}.webp", quality=88, method=6)
        print("wrote", OUT / f"{name}.webp")


if __name__ == "__main__":
    main()
