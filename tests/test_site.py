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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong.yaml"
            path.write_text('repo: o/r\nrepo_id: 1\nowner_id: 2\nadded: "2026-10-09"\n')
            with self.assertRaises(AppProblem):
                registry.load_entry(path)


class GuideTests(unittest.TestCase):
    def test_index_sections_skip_duplicates_and_replaced_pages(self) -> None:
        readme = "## A\n- [One](one.md)\n- [Install](download_executable.md)\n## B\n- [One again](one.md)\n- [Two](two_x.md)\n"
        sections = guides.parse_index(readme)
        self.assertEqual([(s["title"], [i["file"] for i in s["items"]]) for s in sections], [("A", ["one.md"]), ("B", ["two_x.md"])])

    def test_links_between_pages_and_to_other_files(self) -> None:
        text = guides.rewrite_links("[a](./one_x.md#h) [b](../../README.md)", {"one_x.md"})
        self.assertIn("(../one-x/index.md#h)", text)
        self.assertIn("https://github.com/CellMigrationLab/LabConstrictor/blob/main/README.md", text)

    def test_template_footer_navigation_is_removed(self) -> None:
        body = 'Text\n<div align="center">\n\n[Previous](a.md) [Home](README.md)\n\n</div>\n'
        self.assertEqual(guides.NAV_BLOCK.sub("", body).strip(), "Text")


class CardTests(unittest.TestCase):
    def test_text_from_manifests_is_escaped(self) -> None:
        self.assertIn("A demo &lt;b&gt;app&lt;/b&gt;", cards.card(APP))
        self.assertNotIn("<b>app", cards.card(APP))

    def test_verification_expires_with_a_newer_release(self) -> None:
        self.assertFalse(cards.is_verified(APP))
        self.assertTrue(cards.is_verified({**APP, "verified_version": "1.0.0"}))
        self.assertFalse(cards.is_verified({**APP, "verified_version": "0.9.0"}))

    def test_only_the_recommended_installer_is_offered_per_system(self) -> None:
        self.assertEqual(list(cards.downloads(APP)), ["windows"])


class DataTests(unittest.TestCase):
    def test_install_steps_cover_the_three_systems(self) -> None:
        from lcsite.config import load_yaml
        self.assertEqual([s["key"] for s in load_yaml(DATA / "install.yaml")["systems"]], ["windows", "macos", "linux"])


if __name__ == "__main__":
    unittest.main()
