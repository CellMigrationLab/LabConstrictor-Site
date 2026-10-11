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


class SearchIndexTests(unittest.TestCase):
    """The hub cards stay out of the search index."""

    def test_a_card_text_in_the_index_is_reported(self) -> None:
        """If the index holds a card's text (the exclusion stopped working) the check names the hub and the card."""
        import json
        import tempfile
        from pathlib import Path
        import check_site
        from lcsite.config import DATA, load_yaml
        card = load_yaml(DATA / "hubs.yaml")["use"]["cards"][0]
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "search.json").write_text(json.dumps({"items": [{"location": "use/", "text": card["text"]}, {"location": "build/", "text": "Build an app"}]}), encoding="utf-8")
            old, check_site.SITE = check_site.SITE, site
            try:
                found = check_site.search_index_problems()
                (site / "search.json").write_text(json.dumps({"items": [{"location": "use/", "text": "Use an app"}, {"location": "build/", "text": "Build an app"}]}), encoding="utf-8")
                clean = check_site.search_index_problems()
            finally:
                check_site.SITE = old
        self.assertEqual(len(found), 1)
        self.assertEqual(clean, [])


class GuideFooterTests(unittest.TestCase):
    """The template's own Previous/Next footers are removed (the site writes its own pager)."""

    def test_a_footer_with_a_lower_case_home_link_is_removed_too(self) -> None:
        """"Documentation home" (lower case h) marks a footer block just like "Home"."""
        from lcsite import guides
        text = 'Body.\n\n---\n\n<div align="center">\n\n[← A](a.md)\n[🏠 Documentation home](README.md)\n[B →](b.md)\n\n</div>\n'
        self.assertNotIn("](", guides.NAV_BLOCK.sub("", text))
        self.assertIn("Body.", guides.NAV_BLOCK.sub("", text))


class UnsafeLinkTests(unittest.TestCase):
    """A script address in a link is reported."""

    def test_javascript_and_data_addresses_are_problems(self) -> None:
        """check_site names the page and the address; ordinary addresses pass."""
        from pathlib import Path
        import check_site
        parts = check_site.PageParts()
        parts.feed('<a href="javascript:alert(1)">x</a><a href=" DATA:text/html,x">y</a><a href="https://ok.example/">z</a><img src="a.png">')
        found = check_site.unsafe_link_problems({check_site.SITE / "p.html": parts})
        self.assertEqual(len(found), 2)
        self.assertNotIn("ok.example", " ".join(found))
