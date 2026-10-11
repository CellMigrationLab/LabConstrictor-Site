"""Turn the registration result into small web images (offline tool). Display only: no value on the page is computed here."""

from pathlib import Path

import numpy as np
from PIL import Image

ROI_SCALE = 2
CROP_SCALE = 3
FULL_WIDTH = 633
QUALITY = 82


def window(image, low: float = 1.0, high: float = 99.8) -> tuple[float, float]:
    """Display window as two percentiles of the pixels (raises ValueError for an empty image)."""
    lo, hi = np.percentile(image, [low, high])
    return float(lo), float(hi)


def to_uint8(image, lo: float, hi: float):
    """Linear stretch of `image` between lo and hi to 8 bits."""
    return (np.clip((image - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)


def locate_roi(full, roi) -> tuple[int, int]:
    """Top-left corner (y, x) of `roi` inside `full`, found by exact comparison; raises ValueError if it is not a sub-image."""
    h, w = roi.shape
    first = np.argwhere(full == roi[0, 0])
    for y, x in first:
        if y + h <= full.shape[0] and x + w <= full.shape[1] and np.array_equal(full[y:y + h, x:x + w], roi):
            return int(y), int(x)
    raise ValueError("the exported region is not a sub-image of the full image")


def save_webp(array, path: Path, scale: int = 1, tint: tuple[int, int, int] | None = None, alpha=None) -> int:
    """Write an 8-bit image (optionally tinted, optionally with an alpha mask) as WebP; returns its size in bytes."""
    im = Image.fromarray(array)
    if scale != 1:
        im = im.resize((im.width * scale, im.height * scale), Image.BICUBIC)
    if tint is not None:
        rgb = np.stack([np.asarray(im).astype(np.uint16) * c // 255 for c in tint], axis=-1).astype(np.uint8)
        im = Image.fromarray(rgb)
    if alpha is not None:
        mask = Image.fromarray(alpha).resize(im.size, Image.NEAREST)
        im = im.convert("RGBA")
        im.putalpha(mask)
    im.save(path, "WEBP", quality=QUALITY, method=6)
    return path.stat().st_size


def outline_layer(labels, scale: int):
    """RGBA outline (white, 1 display pixel) of a label image, drawn on the up-scaled grid."""
    big = np.kron(labels, np.ones((scale, scale), dtype=labels.dtype))
    edge = np.zeros(big.shape, dtype=bool)
    edge[:-1] |= big[:-1] != big[1:]
    edge[:, :-1] |= big[:, :-1] != big[:, 1:]
    edge &= big > 0
    return edge
