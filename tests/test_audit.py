"""Regression tests for the security and robustness audit: each test names a failure that was found or considered."""

import json
import tempfile
import unittest
import urllib.request
from pathlib import Path

import yaml

import check_site
import submit_app
from lcsite import catalogue, config, guides, pages_apps, registry, text, validate
from lcsite.config import AppProblem, FetchError
from lcsite.github import GitHub, NotFound, SameHostRedirects
from lcsite.page import Page

from test_catalogue import ENTRY, MANIFEST, FakeGitHub


class EscapingTests(unittest.TestCase):
    """Text written by an app's author must never reach a page as markup."""

    def test_a_quote_cannot_close_the_description_meta_attribute(self) -> None:
        """The theme prints the description inside a quoted attribute without escaping it."""
        page = Page("x/index.md", description='x"><script>alert(1)</script>')
        self.assertNotIn('"', page.meta["description"])

    def test_json_ld_cannot_close_its_script_block(self) -> None:
        """< > & are written as \\u escapes so that </script> or <!-- cannot appear."""
        app = {"manifest": {"name": "A</script><!--", "summary": "s", "distribution": {}}, "html_url": "u", "release": None, "section": "apps"}
        out = pages_apps.jsonld(app)
        self.assertNotIn("<", out)
        self.assertEqual(json.loads(out)["name"], "A</script><!--")

    def test_untrusted_text_in_plain_files_has_no_link_or_tag_characters(self) -> None:
        """llms.txt and issue comments get one line of text without [ ] ( ) < >."""
        self.assertEqual(text.one_line("a\n[b](c) <d>"), "a bc d")

    def test_the_site_checker_flags_author_text_that_appears_unescaped(self) -> None:
        """check_site compares each manifest string containing < > or a quote with the built page."""
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp)
            (site / "apps/demo").mkdir(parents=True)
            (site / "apps/demo/index.html").write_text('<meta content="x"><script>alert(1)</script>', encoding="utf-8")
            snapshot = {"apps": [{"slug": "demo", "manifest": {"summary": 'x"><script>alert(1)</script>'}}]}
            original, check_site.SITE = check_site.SITE, site
            try:
                self.assertEqual(len(check_site.escaping_problems(snapshot)), 1)
            finally:
                check_site.SITE = original


class NetworkTests(unittest.TestCase):
    """A bad minute at GitHub must stop the fetch, not shrink the site."""

    def test_a_redirect_to_another_host_is_refused(self) -> None:
        """The token and requests never follow a redirect off GitHub's hosts."""
        request = urllib.request.Request("https://api.github.com/repos/o/r")
        with self.assertRaises(FetchError):
            SameHostRedirects().redirect_request(request, None, 302, "Found", {}, "https://evil.example/x")

    def test_a_missing_release_is_none_but_other_errors_are_not(self) -> None:
        """Only a 404 means "no release"; a rate limit or server error propagates."""
        class Missing(GitHub):
            def json(self, path: str) -> dict:
                """Always answer 404."""
                raise NotFound("404")

        class Broken(GitHub):
            def json(self, path: str) -> dict:
                """Always fail like a rate limit."""
                raise FetchError("HTTP 403")

        self.assertIsNone(Missing(token="").latest_release("o/r"))
        with self.assertRaises(FetchError):
            Broken(token="").latest_release("o/r")

    def test_a_fetch_error_is_not_recorded_as_an_app_problem(self) -> None:
        """catalogue.build lets FetchError through instead of listing the app as left out."""
        class Down(FakeGitHub):
            def repo(self, name: str) -> dict:
                """Always fail like a server error."""
                raise FetchError("HTTP 503")

        with self.assertRaises(FetchError):
            catalogue.build([ENTRY], Down(manifest=MANIFEST))


class InputTests(unittest.TestCase):
    """Untrusted manifests, names and paths."""

    def test_yaml_aliases_are_refused(self) -> None:
        """A few lines of aliases can expand into a structure too large to validate."""
        with self.assertRaises(AppProblem):
            validate.load_plain_yaml("a: &x [1, 2]\nb: *x\n", "m")

    def test_an_empty_manifest_is_refused(self) -> None:
        """An empty file is an error, not an empty manifest."""
        with self.assertRaises(AppProblem):
            validate.load_plain_yaml("", "m")

    def test_empty_and_reserved_web_addresses_are_refused(self) -> None:
        """A repository called "___" would otherwise overwrite apps/index.md."""
        for slug in ("", "index", "assets"):
            with self.assertRaises(AppProblem):
                catalogue.check_unique({"slug": slug, "repo": "o/r", "manifest": {"name": "N"}}, {})

    def test_an_empty_data_file_stops_the_build(self) -> None:
        """load_yaml no longer turns an empty file into {}."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.yaml"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(SystemExit):
                config.load_yaml(path)

    def test_the_oldest_registration_keeps_a_contested_name(self) -> None:
        """Registry entries are processed by date added, not by file name."""
        with tempfile.TemporaryDirectory() as tmp:
            for repo, added in (("a/zzz", "2026-03-01"), ("z/aaa", "2026-01-01")):
                body = {"repo": repo, "repo_id": 1, "owner_id": 2, "added": added}
                (Path(tmp) / registry.expected_name(repo)).write_text(yaml.safe_dump(body), encoding="utf-8")
            self.assertEqual([e["repo"] for e in registry.load_all(Path(tmp))], ["z/aaa", "a/zzz"])

    def test_a_picture_outside_doc_source_is_refused(self) -> None:
        """A guide naming ../../x must not copy files from the build machine into the site."""
        url = "https://github.com/CellMigrationLab/LabConstrictor/blob/doc_source/..%2F..%2Fsecret.txt"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                guides.copy_images(f"![x]({url})", Path(tmp) / "doc_source", "demo.md")

    def test_repository_names_made_of_dots_are_refused(self) -> None:
        """"o/.." must not reach the GitHub API as a path."""
        for bad in ("https://github.com/o/..", "../..", "https://github.com/../x"):
            with self.assertRaises(AppProblem):
                submit_app.parse_repo(f"### Repository\n\n{bad}\n")

    def test_a_comment_cannot_mention_or_link(self) -> None:
        """Manifest text in a submission comment is a code span without @mentions or links."""
        self.assertNotIn("`", submit_app.code("a`b"))
        self.assertNotIn("\n", submit_app.code("a\n@org/team"))


if __name__ == "__main__":
    unittest.main()
