"""Small defects found by the code audit (issue #13): each test reproduces the failure and the fix keeps the good cases."""

import tempfile
import unittest
import warnings
from pathlib import Path

from PIL import Image

import finish_site
from lcsite import images, redirects, text, validate
from lcsite.config import AppProblem


class DateTests(unittest.TestCase):
    """A date that does not exist is an error, never another date."""

    def test_good_dates_and_timestamps_still_format(self) -> None:
        """A date and a timestamp format as before."""
        self.assertEqual(text.long_date("2026-09-21"), "21 September 2026")
        self.assertEqual(text.long_date("2026-10-08T10:00:00Z"), "8 October 2026")

    def test_impossible_dates_are_refused(self) -> None:
        """Month 00 once printed December; February 30 and a plain word are refused too."""
        for bad in ("2026-00-10", "2026-02-30", "2026-13-01", "soon"):
            with self.assertRaises(ValueError):
                text.long_date(bad)


class YamlTests(unittest.TestCase):
    """Anchors and aliases are both refused, as AGENTS.md promises."""

    def test_an_anchor_alone_is_refused(self) -> None:
        """`a: &x [1, 2]` used to pass because only the alias was looked for."""
        with self.assertRaises(AppProblem):
            validate.load_plain_yaml("a: &x [1, 2]\n", "m")

    def test_an_alias_is_refused_and_plain_yaml_passes(self) -> None:
        """An anchor with its alias is refused; ordinary YAML passes."""
        with self.assertRaises(AppProblem):
            validate.load_plain_yaml("a: &x [1]\nb: *x\n", "m")
        self.assertEqual(validate.load_plain_yaml("a: [1, 2]\n", "m"), {"a": [1, 2]})


class LazyImageTests(unittest.TestCase):
    """The image post-processor reads tags the way a browser does."""

    def lazy(self, tag: str) -> str:
        """The tag inside <main> after the processor."""
        return finish_site.lazy_images(f"<main>{tag}</main>").removeprefix("<main>").removesuffix("</main>")

    def test_a_greater_than_sign_inside_a_quoted_value_does_not_end_the_tag(self) -> None:
        """`alt="a > b"` used to be cut in the middle of the attribute."""
        self.assertEqual(self.lazy('<img src="t.png" alt="a > b">'), '<img src="t.png" alt="a > b" loading="lazy">')
        self.assertEqual(self.lazy("<img src='t.png' alt='a > b'/>"), "<img src='t.png' alt='a > b' loading=\"lazy\"/>")

    def test_an_image_that_says_how_it_loads_is_left_alone(self) -> None:
        """An existing loading attribute is kept, but a value that only mentions loading= does not count."""
        self.assertEqual(self.lazy('<img src="t.png" loading="eager">'), '<img src="t.png" loading="eager">')
        self.assertIn('loading="lazy"', self.lazy('<img src="t.png" alt="loading=eager">'))

    def test_images_outside_main_are_not_touched(self) -> None:
        """The theme's own images stay as they are."""
        self.assertEqual(finish_site.lazy_images('<img src="a.png"><main></main>'), '<img src="a.png"><main></main>')


class RedirectTests(unittest.TestCase):
    """Redirect addresses are plain relative routes."""

    def test_dot_dot_and_empty_parts_are_refused(self) -> None:
        """`../x/` and `a//b/` could write outside the page tree."""
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp)
            (docs / "guides" / "install").mkdir(parents=True)
            (docs / "guides" / "install" / "index.md").write_text("x", encoding="utf-8")
            for bad in ("../x/", "a//b/", "./x/"):
                self.assertTrue(any("must not contain" in p for p in redirects.check(bad, "guides/install/", docs)), bad)
            self.assertEqual(redirects.check("old/", "guides/install/", docs), [])


class ImageSizeTests(unittest.TestCase):
    """An image that would need too much memory is refused before it is decoded."""

    def test_a_large_image_is_refused_with_a_message_and_a_small_one_passes(self) -> None:
        """A 20 x 20 image passes; with the limit lowered to 300 pixels (400 pixels is in Pillow's warning range) it is refused, naming the file."""
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "a.png"
            Image.new("RGB", (20, 20)).save(src)
            images.shrink(src, Path(tmp) / "out.jpg", 10)
            old = Image.MAX_IMAGE_PIXELS
            Image.MAX_IMAGE_PIXELS = 300   # 400 pixels: in Pillow's warning range (above the limit, below twice it), which Pillow lets through
            try:
                warnings.simplefilter("ignore")
                with self.assertRaises(AppProblem) as gone:
                    images.shrink(src, Path(tmp) / "out2.jpg", 10)
                self.assertIn("a.png", str(gone.exception))
                with self.assertRaises(AppProblem):
                    images.pixel_size(src)
            finally:
                warnings.resetwarnings()
                Image.MAX_IMAGE_PIXELS = old


if __name__ == "__main__":
    unittest.main()
