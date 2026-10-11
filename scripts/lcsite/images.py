"""Shrink downloaded images for the site (adapted from the lab website's thumbnails)."""

from pathlib import Path

from PIL import Image

from .config import AppProblem

ICON_PX, SHOT_PX = 192, 1200      # icons are square and small; screenshots are as wide as the app page
Image.MAX_IMAGE_PIXELS = 40_000_000   # Pillow raises on larger images (decompression bombs)


def check_pixels(img: Image.Image, name: str) -> None:
    """Raise AppProblem when an image (still undecoded: only its header was read) would need more than MAX_IMAGE_PIXELS pixels in memory.
    Pillow itself only warns between the limit and twice the limit, so the limit is enforced here."""
    if img.width * img.height > Image.MAX_IMAGE_PIXELS:
        raise AppProblem(f"image {name} is {img.width} x {img.height} pixels; the limit is {Image.MAX_IMAGE_PIXELS}")


def shrink(src: Path, dest: Path, max_side: int, square: bool = False) -> None:
    """Write `src` to `dest` (PNG for icons, JPEG for screenshots) no larger than `max_side`.
    Re-encoding drops any metadata or trailing data in the original. Raises AppProblem for
    an image Pillow cannot read."""
    try:
        with Image.open(src) as img:
            check_pixels(img, src.name)
            img = img.convert("RGBA" if square else "RGB")
            if square:
                img.thumbnail((max_side, max_side))
            elif img.width > max_side:
                img = img.resize((max_side, round(img.height * max_side / img.width)))
            dest.parent.mkdir(parents=True, exist_ok=True)
            img.save(dest, optimize=True)
    except (OSError, Image.DecompressionBombError) as err:
        raise AppProblem(f"cannot read image {src.name}: {err}") from err


def pixel_size(path: Path) -> tuple[int, int]:
    """(width, height) of an image file, for the width and height attributes that stop the page from shifting while it loads.
    Raises AppProblem for a file Pillow cannot read."""
    try:
        with Image.open(path) as img:
            check_pixels(img, path.name)
            return img.size
    except (OSError, Image.DecompressionBombError) as err:
        raise AppProblem(f"cannot read image {path.name}: {err}") from err


def check_square(path: Path, tolerance: float = 1.35) -> None:
    """Raise AppProblem unless the image is roughly square (the longer side at most `tolerance` times the shorter)."""
    try:
        with Image.open(path) as img:
            w, h = img.size
    except OSError as err:
        raise AppProblem(f"cannot read image {path.name}: {err}") from err
    if max(w, h) > tolerance * min(w, h):
        raise AppProblem(f"{w}x{h} is not square enough for an icon (a wide logo?)")
