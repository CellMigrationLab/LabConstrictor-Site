"""Catalogue rules: what is listed, what is left out, and that nothing is hidden."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lcsite import assets, catalogue, validate
from lcsite.config import AppProblem
from lcsite.github import NotFound

OK = {"schema": 1, "name": "Demo", "summary": "A demo app that does something useful.", "kind": "analysis",
      "distribution": {"installer": True}}
REPO = "o/demo-app"
ALLOWED = assets.identities(REPO, "Demo")
ENTRY = {"repo": REPO, "repo_id": 7, "owner_id": 9, "added": "2026-10-09"}


def release(url_repo: str = REPO, name: str = "Demo-1.0.0-Windows-x86_64.exe") -> dict:
    """A GitHub release payload with one asset."""
    return {"tag_name": "1.0.0", "published_at": "2026-10-01T00:00:00Z", "html_url": "u",
            "assets": [{"name": name, "size": 10, "browser_download_url": f"https://github.com/{url_repo}/releases/download/1.0.0/{name}"}]}


class FakeGitHub:
    """Stands in for github.GitHub: serves one repo, one manifest and one release."""

    def __init__(self, repo_id: int = 7, rel: bool = True, manifest: str | None = None) -> None:
        """Serve repo `repo_id`, a release when `rel`, and `manifest` as the manifest text."""
        self.repo_id, self.rel, self.manifest = repo_id, rel, manifest

    def repo(self, name: str) -> dict:
        """Repository metadata."""
        return {"id": self.repo_id, "owner": {"id": 9}, "archived": False, "private": False, "default_branch": "main",
                "html_url": "https://github.com/" + name, "license": {"spdx_id": "MIT"}, "has_issues": True}

    def latest_release(self, name: str) -> dict | None:
        """The release, or None."""
        return release(name) if self.rel else None

    def raw(self, name: str, ref: str, path: str, limit: int = 0) -> bytes:
        """The manifest text."""
        return (self.manifest or "").encode()


MANIFEST = "schema: 1\nname: Demo\nsummary: A demo app that does something useful.\nkind: analysis\ndistribution:\n  installer: true\n"


class AssetTests(unittest.TestCase):
    def test_installer_names_are_parsed(self) -> None:
        """Installer names are parsed."""
        a = assets.parse_asset(REPO, "1.0.0", release()["assets"][0], ALLOWED)
        self.assertEqual((a["os"], a["arch"], a["ext"], a["primary"]), ("windows", "x86_64", "exe", True))

    def test_non_installer_assets_are_ignored(self) -> None:
        """Non installer assets are ignored."""
        raw = {"name": "checksums.txt", "size": 1, "browser_download_url": "x"}
        self.assertIsNone(assets.parse_asset(REPO, "1.0.0", raw, ALLOWED))

    def test_download_from_another_repo_is_refused(self) -> None:
        """Download from another repo is refused."""
        with self.assertRaises(AppProblem):
            assets.parse_assets(REPO, "1.0.0", release("evil/repo")["assets"], ALLOWED)

    def test_an_installer_for_another_project_or_version_is_refused(self) -> None:
        """OtherProgram-1.0.0 in this app's release, or Demo-0.9.0 in release 1.0.0, is a problem naming the file; a leading v on the tag is ignored."""
        other = dict(release()["assets"][0], name="OtherProgram-1.0.0-Windows-x86_64.exe")
        old = dict(release()["assets"][0], name="Demo-0.9.0-Windows-x86_64.exe")
        for raw in (other, old):
            raw["browser_download_url"] = f"https://github.com/{REPO}/releases/download/1.0.0/{raw['name']}"
            with self.assertRaises(AppProblem):
                assets.parse_asset(REPO, "1.0.0", raw, ALLOWED)
        tagged = dict(release()["assets"][0], browser_download_url=f"https://github.com/{REPO}/releases/download/v1.0.0/Demo-1.0.0-Windows-x86_64.exe")
        self.assertIsNotNone(assets.parse_asset(REPO, "v1.0.0", tagged, ALLOWED))

    def test_names_that_differ_from_the_repository_are_allowed_when_documented(self) -> None:
        """VLab4Mic installers from LabConstrictor-VLab4Mic, and a manifest name with spaces, match; an unrelated name does not."""
        self.assertIn("vlab4mic", assets.identities("o/LabConstrictor-VLab4Mic", "VLab4Mic"))
        self.assertIn("guessthecondition", assets.identities("o/GuessTheCondition", "Guess the Condition"))
        self.assertIn("labconstrictorplayground", assets.identities("o/LabConstrictor-Playground", "LabConstrictor Playground"))
        self.assertNotIn("other", assets.identities("o/LabConstrictor-VLab4Mic", "VLab4Mic"))

    def test_images_must_be_png_jpeg_or_gif(self) -> None:
        """Images must be png jpeg or gif."""
        with self.assertRaises(AppProblem):
            assets.check_image(b"<svg onload=alert(1)>", 100, "icon.svg")


class ValidationTests(unittest.TestCase):
    def test_a_route_is_required(self) -> None:
        """A route is required."""
        with self.assertRaises(AppProblem):
            validate.check({**OK, "distribution": {}}, validate.MANIFEST_SCHEMA, "m")

    def test_unknown_kind_is_refused(self) -> None:
        """Unknown kind is refused."""
        with self.assertRaises(AppProblem):
            validate.check({**OK, "kind": "magic"}, validate.MANIFEST_SCHEMA, "m")

    def test_svg_icons_are_refused(self) -> None:
        """Svg icons are refused."""
        with self.assertRaises(AppProblem):
            validate.check({**OK, "icon": "logo.svg"}, validate.MANIFEST_SCHEMA, "m")

    def test_colab_links_must_be_colab(self) -> None:
        """Colab links must be colab."""
        bad = {**OK, "distribution": {"colab": [{"label": "x1", "url": "https://evil.example/x"}]}}
        with self.assertRaises(AppProblem):
            validate.check(bad, validate.MANIFEST_SCHEMA, "m")


class ResolveTests(unittest.TestCase):
    def test_a_good_app_resolves(self) -> None:
        """A good app resolves."""
        app = catalogue.resolve(ENTRY, FakeGitHub(manifest=MANIFEST), None, {})
        self.assertEqual((app["slug"], app["release"]["tag"]), ("demo-app", "1.0.0"))

    def test_changed_repo_id_needs_re_review(self) -> None:
        """Changed repo id needs re review."""
        with self.assertRaises(AppProblem):
            catalogue.resolve(ENTRY, FakeGitHub(repo_id=8, manifest=MANIFEST), None, {})

    def test_promised_installers_need_a_release(self) -> None:
        """Promised installers need a release."""
        with self.assertRaises(AppProblem):
            catalogue.resolve(ENTRY, FakeGitHub(rel=False, manifest=MANIFEST), None, {})

    def test_one_bad_app_is_reported_and_does_not_stop_the_others(self) -> None:
        """One bad app is reported and does not stop the others."""
        bad = {**ENTRY, "repo": "o/other", "repo_id": 8}
        snapshot = catalogue.build([ENTRY, bad], FakeGitHub(manifest=MANIFEST))
        self.assertEqual([a["repo"] for a in snapshot["apps"]], [REPO])
        self.assertEqual(len(snapshot["problems"]), 1)
        self.assertIn("o/other", snapshot["problems"][0])

    def test_duplicate_names_are_reported(self) -> None:
        """Duplicate names are reported."""
        twin = {**ENTRY, "repo": "p/demo-app2", "repo_id": 7}
        snapshot = catalogue.build([ENTRY, twin], FakeGitHub(manifest=MANIFEST))
        self.assertEqual(len(snapshot["apps"]), 1)
        self.assertIn("already used", snapshot["problems"][0])

    def test_a_rejected_duplicate_never_overwrites_the_media_of_the_app_that_kept_the_address(self) -> None:
        """Two valid apps with the same repository name from different owners: the second is refused before it downloads anything,
        so the first app's published picture is unchanged (also when the second fails later)."""
        shot = "schema: 1\nname: Demo\nsummary: A demo app that does something useful.\nkind: analysis\ndistribution:\n  installer: true\nscreenshots:\n  - path: s.png\n    caption: A caption\n"

        class Pictures(FakeGitHub):
            """Serves a different picture to each owner."""

            def repo(self, name: str) -> dict:
                """Repository metadata with this repository's own id."""
                return dict(super().repo(name), id=7)

            def latest_release(self, name: str) -> dict | None:
                """A release carrying installers named for the app."""
                return release(name)

            def raw(self, name: str, ref: str, path: str, limit: int = 0) -> bytes:
                """The manifest, or a picture whose bytes name the owner."""
                return shot.encode() if path.endswith(".yaml") else b"\x89PNG\r\n\x1a\n" + name.encode()

        twin = {**ENTRY, "repo": "p/demo-app"}
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(catalogue, "BUILD", Path(tmp)):
            snapshot = catalogue.build([ENTRY, twin], Pictures())
            written = (Path(tmp) / "media" / "demo-app" / "shot-1.png").read_bytes()
        self.assertEqual([a["repo"] for a in snapshot["apps"]], [REPO])
        self.assertTrue(written.endswith(REPO.encode()), written)
        self.assertIn("already used", snapshot["problems"][0])

    def test_a_missing_manifest_says_what_to_add_and_where(self) -> None:
        """A repository without labconstrictor-app.yaml gets a message that names the file, the branch and the way forward."""
        class NoManifest(FakeGitHub):
            """A repository that has no manifest file."""

            def raw(self, name: str, ref: str, path: str, limit: int = 0) -> bytes:
                """Always 404, as GitHub does for a missing file."""
                raise NotFound("404")

        with self.assertRaises(AppProblem) as ctx:
            catalogue.resolve(ENTRY, NoManifest(), None, {})
        self.assertIn("labconstrictor-app.yaml", str(ctx.exception))
        self.assertIn("default branch (main)", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
