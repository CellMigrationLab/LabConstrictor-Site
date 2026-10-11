"""The "Get it" part of an app page: tiles, platforms, checksums, the pip and Colab routes, first steps, sizes."""

import unittest

from lcsite import assets, cards, catalogue, pages_apps, pages_get, text
from lcsite.config import AppProblem

ASSET = {"name": "A-1.0.0-Windows-x86_64.exe", "os": "windows", "arch": "x86_64", "ext": "exe", "size": 317528492, "url": "https://github.com/o/a/releases/download/1.0.0/x.exe",
         "primary": True, "sha256": "ab" * 32}
MAC = dict(ASSET, name="A-1.0.0-MacOSX-arm64.pkg", os="macos", arch="arm64", ext="pkg", sha256=None)
INTEL = dict(MAC, arch="x86_64")


def app(assets_list: list[dict], **dist: object) -> dict:
    """A minimal app with a release of the given assets and the given distribution fields."""
    return {"slug": "a", "repo": "o/a", "html_url": "https://github.com/o/a", "section": "apps", "has_issues": True, "license": "MIT", "icon": None, "screenshots": [],
            "manifest": {"name": "A", "summary": "s", "kind": "utility", "distribution": {"installer": True} | dist},
            "release": {"tag": "1.0.0", "published_at": "2026-10-01T00:00:00Z", "url": "https://github.com/o/a/releases/tag/1.0.0", "assets": assets_list}}


class PlatformTests(unittest.TestCase):
    """distribution.platforms limits what is offered; absent, everything is."""

    def test_unlisted_installers_are_not_offered_and_intel_gets_a_line(self) -> None:
        """With only macos-arm64 listed, the Intel installer is hidden from tiles and table and the tile says so."""
        a = app([ASSET, MAC, INTEL], platforms=["windows-x86_64", "macos-arm64"])
        have = cards.downloads(a)
        self.assertEqual([o["arch"] for o in have["macos"]], ["arm64"])
        self.assertNotIn("macOS (Intel)", pages_get.downloads_table(a))
        self.assertIn("Intel Macs: not supported by this app's authors.", pages_get.get_section(a))

    def test_the_schema_checks_platforms(self) -> None:
        """An unknown platform, or platforms without an installer route, is refused."""
        from lcsite.validate import check
        base = {"schema": 1, "name": "Aa", "summary": "A sufficiently long summary here", "kind": "utility"}
        check(base | {"distribution": {"installer": True, "platforms": ["macos-arm64"]}}, "labconstrictor-app.schema.json", "t")
        for dist in ({"installer": True, "platforms": ["beos-x86_64"]}, {"pip": "x", "platforms": ["macos-arm64"]}, {"platforms": ["macos-arm64"]}):
            with self.assertRaises(AppProblem):
                check(base | {"distribution": dist}, "labconstrictor-app.schema.json", "t")

    def test_without_platforms_everything_is_offered_and_nothing_is_added(self) -> None:
        """Absent platforms: both Mac installers, and no Intel line."""
        a = app([ASSET, MAC, INTEL])
        self.assertEqual(len(cards.downloads(a)["macos"]), 2)
        self.assertNotIn("not supported", pages_get.get_section(a))

    def test_a_listed_platform_without_an_installer_stops_that_app(self) -> None:
        """The error names the app and the platform."""
        with self.assertRaises(AppProblem) as ctx:
            catalogue.check_platforms("o/a", {"distribution": {"platforms": ["linux-x86_64"]}}, [ASSET])
        self.assertIn("o/a", str(ctx.exception))
        self.assertIn("linux-x86_64", str(ctx.exception))

    def test_json_ld_names_only_the_offered_systems_and_testing_apps_have_no_category(self) -> None:
        """operatingSystem follows what is offered; a testing app is not called a scientific application."""
        import json
        out = json.loads(pages_apps.jsonld(app([ASSET])))
        self.assertEqual(out["operatingSystem"], "Windows")
        self.assertEqual(out["applicationCategory"], "ScientificApplication")
        self.assertNotIn("applicationCategory", json.loads(pages_apps.jsonld(dict(app([ASSET]), section="testing"))))


class DownloadBlockTests(unittest.TestCase):
    """Checksums, sizes, routes and first steps."""

    def test_digests_are_read_from_github_and_shown_or_marked_not_published(self) -> None:
        """A "sha256:" digest is kept without the prefix; others and missing ones give None, and the table says "not published"."""
        self.assertEqual(assets.sha256_of({"digest": "sha256:" + "a" * 64}), "a" * 64)
        self.assertIsNone(assets.sha256_of({"digest": "md5:abc"}))
        self.assertIsNone(assets.sha256_of({}))
        table = pages_get.downloads_table(app([ASSET, MAC]))
        self.assertIn("ab" * 32, table)
        self.assertIn("not published", table)

    def test_sizes_are_decimal_megabytes(self) -> None:
        """317528492 bytes is 317.5 MB (not 303 MiB printed as MB)."""
        self.assertEqual(text.megabytes(317528492), "317.5 MB")

    def test_the_colab_and_pip_routes_are_labelled(self) -> None:
        """A Colab list carries the one sentence about the service; pip is labelled advanced with its command and PyPI link."""
        a = app([ASSET], colab=[{"label": "N", "url": "https://colab.research.google.com/x"}], pip="my-app")
        html = pages_get.get_section(a)
        self.assertIn("handled by Google", html)
        self.assertIn("Python package (advanced)", html)
        self.assertIn("pip install my-app", html)
        self.assertIn("https://pypi.org/project/my-app/", html)
        self.assertIn("v1.0.0", html)
        self.assertIn("github.com/o/a/releases", html)

    def test_without_first_steps_the_page_says_so(self) -> None:
        """No quickstart: one plain line, and the generic paragraph is labelled as generic."""
        html = pages_get.using_section(app([ASSET]))
        self.assertIn("The authors have not given first-run steps.", html)
        self.assertIn("For any LabConstrictor desktop app:", html)
        a = app([ASSET])
        a["manifest"]["quickstart"] = ["Open it"]
        self.assertNotIn("have not given", pages_get.using_section(a))

    def test_details_show_the_owner_and_the_issue_tracker_only_when_there_is_one(self) -> None:
        """Repository owner is always there; Report a problem only with an issue tracker."""
        html = pages_apps.details_list(app([ASSET]))
        self.assertIn("Repository owner</dt><dd>o", html)
        self.assertIn("Report a problem", html)
        quiet = pages_apps.details_list(dict(app([ASSET]), has_issues=False))
        self.assertNotIn("Report a problem", quiet)
        self.assertIn("No issue tracker on GitHub", quiet)


if __name__ == "__main__":
    unittest.main()


class TileLinkTests(unittest.TestCase):
    """Each system tile links to its own section of the install guide."""

    def test_each_tile_has_its_own_steps_link(self) -> None:
        """Windows, macOS and Linux tiles point at their own anchors."""
        html = pages_get.get_section(app([ASSET, MAC]))
        for system in ("windows", "macos", "linux"):
            self.assertIn(f'guides/install/#{system}"', html)
