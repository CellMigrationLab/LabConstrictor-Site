"""The citation block on the home page and the "How to cite" section of app pages."""

import tempfile
import unittest
from pathlib import Path

from lcsite import citation
from lcsite.config import fail  # noqa: F401  (SystemExit is what fail raises)

FIELDS = {"lead": "Please cite <this>.", "authors": "A. Author and B. Author", "title": "A title", "venue": "arXiv preprint", "year": "2026", "doi": "10.48550/arXiv.2603.10704"}
SITE = {"citation": FIELDS}


def app(doi: str | None = None, section: str = "apps", release: bool = True) -> dict:
    """A minimal app record for the citation section."""
    manifest = {"name": "X"} | ({"doi": doi} if doi else {})
    rel = {"tag": "0.1.1", "published_at": "2026-10-08T10:00:00Z"} if release else None
    return {"manifest": manifest, "section": section, "release": rel}


class HomeBlockTests(unittest.TestCase):
    """The home block shows the README's wording and links to the preprint."""

    def test_the_block_has_the_doi_and_escapes_text(self) -> None:
        """The preprint link is there, once as text and once as the action link, and author text is escaped."""
        html = citation.cite_band(SITE)
        self.assertIn('id="cite"', html)
        self.assertEqual(html.count("https://doi.org/10.48550/arXiv.2603.10704"), 2)
        self.assertIn("Please cite &lt;this&gt;.", html)
        self.assertNotIn("zenodo", html.lower())

    def test_the_reference_is_formatted_as_authors_title_venue_year_doi(self) -> None:
        """One citation line in that order, the venue in italics, inside a blockquote of its own."""
        html = citation.cite_band(SITE)
        self.assertIn('<blockquote class="lc-cite"><p class="lc-cite__ref">A. Author and B. Author. A title. <em>arXiv preprint</em>, 2026. <a href=', html)

    def test_a_missing_or_empty_key_stops_the_build_naming_the_file(self) -> None:
        """No block, a missing key and an empty value are errors that name data/site.yaml."""
        for bad in ({}, {"citation": {"lead": "x", "title": "y"}}, {"citation": dict(FIELDS, authors=" ")}, {"citation": {k: v for k, v in FIELDS.items() if k != "year"}}):
            with self.assertRaises(SystemExit):
                citation.cite_band(bad)

    def test_the_template_readme_must_carry_the_doi(self) -> None:
        """A README without the DOI stops the build and names README.md; one with it passes."""
        with tempfile.TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text("no citation", encoding="utf-8")
            with self.assertRaises(SystemExit):
                citation.check_template_readme(SITE, Path(tmp))
            readme.write_text("see https://doi.org/10.48550/arXiv.2603.10704", encoding="utf-8")
            citation.check_template_readme(SITE, Path(tmp))


class AppSectionTests(unittest.TestCase):
    """The app page names what its manifest says to cite, and nothing else."""

    def test_with_a_doi_it_links_the_paper_and_names_the_version(self) -> None:
        """The DOI is a link, the action link says Read the paper, and the latest release is named."""
        html = citation.app_section(app("10.1242/jcs.265152"))
        self.assertIn("https://doi.org/10.1242/jcs.265152", html)
        self.assertIn("Read the paper", html)
        self.assertIn("latest release: v0.1.1", html)

    def test_without_a_doi_it_only_says_the_listing_names_none(self) -> None:
        """No invented reference; a testing app without a doi has no section; an app without a release has no version sentence."""
        self.assertIn("The authors name no publication to cite", citation.app_section(app()))
        self.assertEqual(citation.app_section(app(section="testing")), "")
        self.assertNotIn("Name the version", citation.app_section(app(release=False)))

    def test_a_hostile_doi_is_escaped_in_the_address(self) -> None:
        """Characters that could break out of the attribute are encoded or escaped."""
        html = citation.app_section(app('10.1/x"><script>'))
        self.assertNotIn("<script>", html)
        self.assertNotIn('"><', html)


if __name__ == "__main__":
    unittest.main()
