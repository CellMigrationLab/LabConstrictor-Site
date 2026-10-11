"""Wording that comes from data: the host phrase, and the literal-Markdown report."""

import unittest

from lcsite import cards


class HostPhraseTests(unittest.TestCase):
    """What the site says about an app's host comes from the plugin's own status, in one wording everywhere."""

    def test_every_status_has_one_wording_and_the_same_phrase_is_used_everywhere(self) -> None:
        """Chip, header badge and Details row show the same phrase; an unknown status stops the build naming the program."""
        from unittest import mock
        from lcsite import pages_apps, projects
        with mock.patch.object(projects, "host_status", return_value="Experimental"):
            phrase = cards.host_phrase("napari")
            self.assertEqual(phrase, "napari plugin: experimental")
            self.assertIn(phrase, cards.host_chip("napari"))
            self.assertIn(phrase, cards.host_badge("napari"))
        with mock.patch.object(projects, "host_status", return_value="Install from GitHub"):
            self.assertEqual(cards.host_phrase("fiji"), "Fiji plugin: install from GitHub")
        with mock.patch.object(projects, "host_status", return_value="Soon"), self.assertRaises(SystemExit):
            cards.host_phrase("qupath")
        self.assertTrue(hasattr(pages_apps, "works_in"))

    def test_no_page_text_promises_soon(self) -> None:
        """The words "Soon in" are gone from the code and the data."""
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        hits = [str(p) for folder in ("scripts", "data") for p in (root / folder).rglob("*") if p.suffix in (".py", ".yaml") and "Soon in" in p.read_text(encoding="utf-8")]
        self.assertEqual(hits, [])


class LiteralMarkdownTests(unittest.TestCase):
    """A page that shows Markdown link syntax is reported."""

    def test_literal_link_syntax_outside_code_is_a_problem(self) -> None:
        """"](" in visible text fails; the same text inside <code> passes."""
        import tempfile
        from pathlib import Path
        import check_site
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "bad.html").write_text("<main><p>see [a](b/)</p></main>", encoding="utf-8")
            (site / "ok.html").write_text("<main><p><code>[a](b/)</code></p></main>", encoding="utf-8")
            old, check_site.SITE = check_site.SITE, site
            try:
                found = check_site.literal_markdown_problems()
            finally:
                check_site.SITE = old
        self.assertEqual(len(found), 1)
        self.assertIn("bad.html", found[0])
