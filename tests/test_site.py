"""Registry loading, guide import rules and card output."""

import tempfile
import unittest
from pathlib import Path

from lcsite import cards, guides, registry
from lcsite.config import AppProblem, DATA

APP = {"slug": "demo", "repo": "o/demo", "html_url": "https://github.com/o/demo", "tier": "listed", "verified_version": None,
       "verified_on": None, "featured": False, "license": "MIT", "icon": None, "screenshots": [],
       "manifest": {"name": "Demo", "summary": "A demo <b>app</b>", "kind": "utility", "distribution": {"installer": True, "pip": "demo"}},
       "release": {"tag": "1.0.0", "published_at": "2026-10-01T00:00:00Z", "url": "u", "assets": [
           {"name": "x", "os": "windows", "arch": "x86_64", "ext": "exe", "size": 5, "url": "https://x", "primary": True}]}}


class RegistryTests(unittest.TestCase):
    def test_file_name_must_match_the_repo(self) -> None:
        """File name must match the repo."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong.yaml"
            path.write_text('repo: o/r\nrepo_id: 1\nowner_id: 2\nadded: "2026-10-09"\n')
            with self.assertRaises(AppProblem):
                registry.load_entry(path)


class GuideTests(unittest.TestCase):
    def test_index_sections_skip_duplicates_and_replaced_pages(self) -> None:
        """Index sections skip duplicates and replaced pages."""
        readme = "## A\n- [One](one.md)\n- [Install](download_executable.md)\n## B\n- [One again](one.md)\n- [Two](two_x.md)\n"
        sections = guides.parse_index(readme)
        self.assertEqual([(s["title"], [i["file"] for i in s["items"]]) for s in sections], [("A", ["one.md"]), ("B", ["two_x.md"])])

    def test_links_between_pages_and_to_other_files(self) -> None:
        """Links between pages and to other files."""
        text = guides.rewrite_links("[a](./one_x.md#h) [b](../../README.md)", {"one_x.md"})
        self.assertIn("(../one-x/index.md#h)", text)
        self.assertIn("https://github.com/CellMigrationLab/LabConstrictor/blob/main/README.md", text)

    def test_template_footer_navigation_is_removed(self) -> None:
        """Template footer navigation is removed."""
        body = 'Text\n<div align="center">\n\n[Previous](a.md) [Home](README.md)\n\n</div>\n'
        self.assertEqual(guides.NAV_BLOCK.sub("", body).strip(), "Text")


class CardTests(unittest.TestCase):
    def test_text_from_manifests_is_escaped(self) -> None:
        """Text from manifests is escaped."""
        self.assertIn("A demo &lt;b&gt;app&lt;/b&gt;", cards.card(APP))
        self.assertNotIn("<b>app", cards.card(APP))

    def test_verification_expires_with_a_newer_release(self) -> None:
        """Verification expires with a newer release."""
        self.assertFalse(cards.is_verified(APP))
        self.assertTrue(cards.is_verified({**APP, "verified_version": "1.0.0"}))
        self.assertFalse(cards.is_verified({**APP, "verified_version": "0.9.0"}))

    def test_only_the_recommended_installer_is_offered_per_system(self) -> None:
        """Only the recommended installer is offered per system."""
        self.assertEqual({k: len(v) for k, v in cards.downloads(APP).items()}, {"windows": 1, "macos": 0, "linux": 0})


class DataTests(unittest.TestCase):
    def test_install_steps_cover_the_three_systems(self) -> None:
        """Install steps cover the three systems."""
        from lcsite.config import load_yaml
        self.assertEqual([s["key"] for s in load_yaml(DATA / "install.yaml")["systems"]], ["windows", "macos", "linux"])


if __name__ == "__main__":
    unittest.main()


class RobotsTests(unittest.TestCase):
    """The site stays out of search engines until `extra.listed` is true."""

    def test_unlisted_robots_disallows_everything(self) -> None:
        """robots.txt for an unlisted site blocks all crawling and names no sitemap."""
        from write_sitemap import robots
        text = robots("https://example.org/", False)
        self.assertIn("Disallow: /", text)
        self.assertNotIn("Sitemap", text)

    def test_listed_robots_names_the_sitemap(self) -> None:
        """robots.txt for a listed site allows crawling and points to the sitemap."""
        from write_sitemap import robots
        text = robots("https://example.org/", True)
        self.assertIn("Allow: /", text)
        self.assertIn("Sitemap: https://example.org/sitemap.xml", text)
