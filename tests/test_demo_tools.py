"""The offline demo-asset tools refuse images they cannot draw honestly (they need numpy, which the site build does not)."""

import sys
import unittest
from pathlib import Path

try:
    import numpy as np
except ImportError as err:
    raise unittest.SkipTest(f"numpy is not installed ({err}); these tests cover the offline tools in tools/demo_assets") from err

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "demo_assets"))
import display  # noqa: E402


class WindowTests(unittest.TestCase):
    """A display window must have a width, and every pixel must be a number."""

    def test_a_valid_image_keeps_its_percentile_window(self) -> None:
        """A ramp gives the two percentiles and stretches to the full 8-bit range."""
        image = np.arange(1000, dtype=float).reshape(10, 100)
        lo, hi = display.window(image)
        self.assertLess(lo, hi)
        out = display.to_uint8(image, lo, hi)
        self.assertEqual((int(out.min()), int(out.max())), (0, 255))

    def test_constant_empty_and_nonfinite_images_are_refused(self) -> None:
        """A constant image used to become black with a division warning; NaN pixels and an empty array are named too."""
        for bad in (np.full((4, 4), 7.0), np.zeros((0, 3)), np.array([[1.0, np.nan], [2.0, 3.0]])):
            with self.assertRaises(ValueError):
                display.window(bad)
        with self.assertRaises(ValueError):
            display.to_uint8(np.ones((2, 2)), 1.0, 1.0)
        with self.assertRaises(ValueError):
            display.to_uint8(np.ones((2, 2)), 0.0, float("nan"))


if __name__ == "__main__":
    unittest.main()
