"""The critical guides' shape report and the literal-Markdown check."""

import tempfile
import unittest
from pathlib import Path

from lcsite import guide_shape


class ShapeTests(unittest.TestCase):
    """What is reported, and what stops the build."""

    def test_a_guide_with_all_three_sections_passes(self) -> None:
        """Either wording of the first section is accepted."""
        for first in ("What you need", "Before you start"):
            html = f"<h2>{first}</h2><h2 id='x'>Check that it worked</h2><h2>If something does not work</h2>"
            self.assertEqual(guide_shape.missing_sections(guide_shape.headings(html)), [])

    def test_a_missing_section_is_named(self) -> None:
        """The report names the heading that is missing, once."""
        found = guide_shape.headings("<h2>What you need</h2><h2>Steps</h2>")
        self.assertEqual(guide_shape.missing_sections(found), ["check that it worked", "if something does not work"])

    def test_an_unknown_critical_guide_stops_the_build(self) -> None:
        """A slug without a page is an error naming it, not a skipped line."""
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit):
            guide_shape.warnings(Path(tmp), ["no-such-guide"])

    def test_warnings_read_the_built_page(self) -> None:
        """A built guide lacking sections gives WARNING lines naming it."""
        with tempfile.TemporaryDirectory() as tmp:
            page = Path(tmp) / "guides" / "g" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text("<h2>Intro</h2>", encoding="utf-8")
            lines = guide_shape.warnings(Path(tmp), ["g"])
        self.assertEqual(len(lines), 3)
        self.assertIn("guides/g", lines[0])


if __name__ == "__main__":
    unittest.main()
