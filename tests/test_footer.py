"""The footer credits both labs, each linked to its own website."""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FooterCreditsTests(unittest.TestCase):
    """The layout names the Cell Migration Lab and the Henriques Lab and links both."""

    def test_both_labs_are_credited_with_a_link(self) -> None:
        """A page footer that drops a lab or its link would fail here."""
        layout = (ROOT / "overrides" / "main.html").read_text(encoding="utf-8")
        for name, url in (("Cell Migration Lab", "https://cellmig.org/"), ("Henriques Lab", "https://henriqueslab.org/")):
            self.assertIn(f'<a href="{url}" target="_blank" rel="noopener">{name}</a>', layout)

    def test_the_artwork_credit_names_its_creator_in_full(self) -> None:
        """The logo and comic are credited to Iván Hidalgo-Cenalmor (full name, as in the citation)."""
        layout = (ROOT / "overrides" / "main.html").read_text(encoding="utf-8")
        self.assertIn("Logo and comic by Iván Hidalgo-Cenalmor.", layout)

    def test_the_site_metadata_names_both_labs(self) -> None:
        """Author and copyright in mkdocs.yml match the footer."""
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        self.assertIn("site_author: Cell Migration Lab and Henriques Lab", config)
        self.assertIn("copyright: © Cell Migration Lab and Henriques Lab", config)


if __name__ == "__main__":
    unittest.main()
