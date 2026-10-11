"""Write the two pictures of the How it works page (content/how/figures/*.webp): crops of Figure 2 of the LabConstrictor preprint.

The preprint (Hidalgo-Cenalmor et al., 2026, doi:10.48550/arXiv.2603.10704) is licensed CC BY 4.0, so its figures may be adapted with credit.
Usage (needs Playwright with Chromium and Pillow; the figure is downloaded from arXiv first):
    curl -o Fig2.svg https://arxiv.org/html/2603.10704v1/Fig2.svg
    python tools/how_figures/crop_preprint_figure.py Fig2.svg

The boxes are in pixels of the figure drawn 1300 pixels wide; the pictures are saved at twice that size. The site numbers its steps 1 to 5 like the paper, so the paper's numbered circles are kept.
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
    "pipeline": (0, 50, 830, 950),    # part A without its heading: the five steps of the developer workflow, numbered 1 to 5 as on the site
    "end": (4, 1032, 1300, 1260),     # part B: what users get (installers, the app, the notebooks)
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
    """Draw the figure and save the crops."""
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
