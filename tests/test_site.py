"""Registry loading, guide import rules and card output."""

import tempfile
import unittest
from pathlib import Path

from lcsite import cards, guides, hubs, projects, registry, sources
from lcsite.config import AppProblem, DATA

APP = {"slug": "demo", "repo": "o/demo", "html_url": "https://github.com/o/demo", "tier": "listed", "verified_version": None,
       "verified_on": None, "featured": False, "section": "apps", "license": "MIT", "icon": None, "screenshots": [],
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


class ClaimTests(unittest.TestCase):
    """Template pages that are for users are placed under our own track."""

    def test_claimed_page_moves_and_keeps_its_title(self) -> None:
        """A page named with `template:` leaves the template's sections and takes the template's title."""
        own = [{"items": [{"template": "a.md"}]}]
        theirs = [{"items": [{"file": "a.md", "title": "A page", "slug": "a"}, {"file": "b.md", "title": "B", "slug": "b"}]}]
        guides.claim_template_pages(own, theirs)
        self.assertEqual(own[0]["items"][0]["title"], "A page")
        self.assertEqual([g["file"] for g in theirs[0]["items"]], ["b.md"])

    def test_missing_template_page_stops_the_build(self) -> None:
        """A placement for a page the template no longer has fails, naming the file."""
        with self.assertRaises(SystemExit) as ctx:
            guides.claim_template_pages([{"items": [{"template": "gone.md"}]}], [{"items": []}])
        self.assertIn("gone.md", str(ctx.exception))


class SourceGuideTests(unittest.TestCase):
    """Guides kept in other repositories are converted for the site, or the build stops."""

    def test_alert_becomes_an_admonition_with_its_title(self) -> None:
        """A GitHub alert with a bold lead sentence becomes a titled admonition; the rest is its body."""
        text = "> [!WARNING]\n> **Under heavy construction.** Not stable.\n>\n> Second paragraph.\n\nAfter\n"
        out = sources.admonitions(text)
        self.assertIn('!!! warning "Under heavy construction"', out)
        self.assertIn("    Not stable.", out)
        self.assertIn("    Second paragraph.", out)
        self.assertTrue(out.endswith("After\n"))

    def test_relative_link_or_picture_stops_the_build(self) -> None:
        """A relative link or picture would break on the site, so it fails and names the guide."""
        with self.assertRaises(SystemExit) as ctx:
            sources.check_links("See [x](other.md) and ![p](shot.png)", "repo/docs/user-guide.md")
        self.assertIn("repo/docs/user-guide.md", str(ctx.exception))
        sources.check_links("[ok](https://example.org/a) [here](#top)", "x")

    def test_link_to_an_imported_guide_points_at_the_site_page(self) -> None:
        """A link to another imported guide's file on GitHub becomes a site link; other links stay."""
        pages = {("o/r", "docs/user-guide.md"): "r"}
        text = "[a](https://github.com/o/r/blob/main/docs/user-guide.md#x) [b](https://github.com/o/r/blob/main/README.md)"
        out = sources.site_links(text, pages)
        self.assertIn("[a](../r/index.md#x)", out)
        self.assertIn("[b](https://github.com/o/r/blob/main/README.md)", out)

    def test_title_is_the_first_heading_or_the_build_stops(self) -> None:
        """The title of a guide is its first '# ' line; a guide without one fails."""
        self.assertEqual(sources.title_of("intro\n# The title\n## Part", "x"), "The title")
        with self.assertRaises(SystemExit):
            sources.title_of("no heading here", "x")


class HubTests(unittest.TestCase):
    """Pictures on the hub pages are checked, not guessed."""

    def test_picture_needs_exactly_one_source(self) -> None:
        """A picture with both or neither of doc_source and repo stops the build."""
        for spec in ({}, {"doc_source": "a.png", "repo": "o/r", "path": "p.png"}):
            with self.assertRaises(SystemExit):
                hubs.source_file(spec, Path("."))

    def test_missing_picture_stops_the_build(self) -> None:
        """A named picture that is not in the checkout fails, naming the path."""
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(SystemExit) as ctx:
            hubs.source_file({"doc_source": "nope.png"}, Path(tmp))
        self.assertIn("nope.png", str(ctx.exception))

    def test_picture_without_alt_text_stops_the_build(self) -> None:
        """Every picture needs alt text."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.png").write_bytes(b"x")
            with self.assertRaises(SystemExit) as ctx:
                hubs.prepare_image({"doc_source": "a.png"}, Path(tmp), None, {})
        self.assertIn("alt", str(ctx.exception))

    def test_pictures_kept_elsewhere_are_listed_for_fetching(self) -> None:
        """Only pictures with repo + path are fetched; doc_source ones come from the checkout."""
        hubs_data = {"use": {"cards": [{"image": {"repo": "o/r", "path": "a.png"}}, {"image": {"doc_source": "b.png"}}, {"live_card": True}]}}
        self.assertEqual([(e["repo"], e["path"]) for e in hubs.image_sources(hubs_data)], [("o/r", "a.png")])


class ProjectTests(unittest.TestCase):
    """The Ecosystem page is built from each project's own file, or the build stops."""

    def test_inline_card_needs_exactly_its_keys(self) -> None:
        """An inline card (the template) with a missing or extra key fails; a complete one becomes a card."""
        card = projects.inline_card({"repo": "o/r", "name": "N", "text": "A sentence.", "status": "Available"})
        self.assertEqual(card, {"name": "N", "summary": "A sentence.", "status": "Available"})
        with self.assertRaises(SystemExit):
            projects.inline_card({"repo": "o/r", "name": "N", "text": "x"})

    def test_only_cards_without_inline_text_are_fetched(self) -> None:
        """The files to download are the project files of the `- repo:` entries, not of inline cards."""
        eco = {"tiers": [{"items": [{"repo": "o/a"}, {"repo": "o/b", "name": "B", "text": "t", "status": "s"}]}]}
        self.assertEqual([e["repo"] for e in projects.fetch_entries(eco)], ["o/a"])

    def test_invalid_project_file_names_its_repository(self) -> None:
        """A project file that breaks the schema stops the build and says which repository to fix."""
        from unittest import mock
        with mock.patch.object(sources, "read", return_value="name: X\nsummary: short\nstatus: ok\n"), self.assertRaises(SystemExit) as ctx:
            projects.load_project("o/r")
        self.assertIn("o/r/docs/labconstrictor-project.yaml", str(ctx.exception))


class NavigationTests(unittest.TestCase):
    """Menu titles, badges and the testing group behave as documented."""

    def test_menu_title_is_the_pages_own_heading_without_an_emoji(self) -> None:
        """A template page is titled by its first heading, minus a leading emoji, so page and menu agree."""
        self.assertEqual(guides.heading_title("# 📋 Before Getting Started\ntext", "x.md"), "Before Getting Started")
        self.assertEqual(guides.heading_title("# Accept a Pull Request (PR)\n", "x.md"), "Accept a Pull Request (PR)")
        with self.assertRaises(SystemExit):
            guides.heading_title("no heading", "x.md")

    def test_badge_is_a_link_only_when_given_an_address(self) -> None:
        """A badge with an href is an <a>; without one it is a plain <span>."""
        self.assertIn('<a class="lc-badge lc-badge--host" href="guides/napari/">', cards.badge("Soon in napari", "host", "guides/napari/"))
        self.assertTrue(cards.badge("Community").startswith("<span"))

    def test_github_badge_names_the_repository_and_links_to_it(self) -> None:
        """The GitHub pill links to the repository and shows its name."""
        html = cards.github_badge("o/r-name")
        self.assertIn('href="https://github.com/o/r-name"', html)
        self.assertIn("<span>r-name</span>", html)

    def test_only_testing_apps_get_the_testing_badge(self) -> None:
        """`section: testing` shows a Testing badge; any other app shows none."""
        self.assertIn("Testing", cards.testing_badge({"section": "testing"}))
        self.assertEqual(cards.testing_badge({"section": "apps"}), "")
