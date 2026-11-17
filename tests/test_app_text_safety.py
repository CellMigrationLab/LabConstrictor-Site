"""Text and pictures from an app's repository can neither change the site's markup nor stop the whole site build or a submission check."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

import check_design
import check_site
import submit_app
from lcsite import images, sources
from lcsite.config import AppProblem
from lcsite.github import GitHub
from lcsite.page import decorate_links
from lcsite.text import esc


def png(width: int, height: int) -> bytes:
    """A real PNG of the given size."""
    out = io.BytesIO()
    Image.new("L", (width, height)).save(out, format="PNG")
    return out.getvalue()


class LinkTests(unittest.TestCase):
    """Only the site's own Markdown links become pills."""

    def test_markdown_link_syntax_in_app_text_stays_text(self) -> None:
        """An app summary with "[docs](https://github.com/...)" is shown as written, also inside an attribute."""
        summary = esc("See [docs](https://github.com/evil/repo) now")
        html = decorate_links(f'<li data-search="{summary}"><p>{summary}</p></li>')
        self.assertNotIn("<a", html)
        self.assertEqual(html.count('"'), 2)

    def test_links_inside_code_are_left_as_written(self) -> None:
        """A link in a fenced block or inline code of a guide is code to copy; a link in the text still becomes a pill."""
        text = "Use [the repo](https://github.com/a/b).\n\n```md\n[x](https://github.com/a/b)\n```\n\nand `[y](https://github.com/a/b)`\n"
        html = decorate_links(text)
        self.assertEqual(html.count('class="lc-gh"'), 1)
        self.assertIn("[x](https://github.com/a/b)", html)
        self.assertIn("`[y](https://github.com/a/b)`", html)

    def test_a_guide_title_in_the_menu_has_no_markdown_marks(self) -> None:
        """The sidebar, pager and Docs list print the title as text: `code` and **bold** lose their marks."""
        self.assertEqual(sources.title_of("# Describe your app: the `labconstrictor-app.yaml` file\n", "x"),
                         "Describe your app: the labconstrictor-app.yaml file")
        self.assertEqual(sources.title_of("# A **bold** step\n", "x"), "A bold step")


class PictureTests(unittest.TestCase):
    """A picture that cannot be shrunk later is refused when it is downloaded."""

    def check(self, data: bytes) -> None:
        """Run images.check_decodes on `data` written to a file."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "shot.png"
            path.write_bytes(data)
            images.check_decodes(path)

    def test_a_small_file_with_too_many_pixels_is_refused(self) -> None:
        """7000 x 6000 pixels compress to a few KB but need more memory than the limit allows."""
        with self.assertRaises(AppProblem):
            self.check(png(7000, 6000))

    def test_a_broken_image_after_a_valid_header_is_refused(self) -> None:
        """The signature passes the first check; the decode does not."""
        noisy = io.BytesIO()
        Image.frombytes("L", (64, 64), bytes(range(256)) * 16).save(noisy, format="PNG")
        data = noisy.getvalue()
        with self.assertRaises(AppProblem):
            self.check(data[:len(data) // 2])

    def test_a_good_image_passes(self) -> None:
        """A normal screenshot raises nothing."""
        self.check(png(40, 30))

    def test_a_path_with_a_space_is_fetched_quoted(self) -> None:
        """"assets/my icon.png" is a valid manifest path: the address is quoted instead of crashing the fetch."""
        gh = GitHub()
        with mock.patch.object(gh, "_open", return_value=b"x") as opened:
            gh.raw("o/r", "main", "assets/my icon.png")
        self.assertEqual(opened.call_args.args[0], "https://raw.githubusercontent.com/o/r/main/assets/my%20icon.png")


class CheckTests(unittest.TestCase):
    """The checks after the build do not stop the publish because of what one app wrote."""

    def test_two_apps_with_the_same_summary_do_not_stop_the_build(self) -> None:
        """App pages are left out of the duplicate-description rule; the site's own pages are not."""
        def page(description: str) -> check_design.Facts:
            """Facts of a page with that meta description."""
            facts = check_design.Facts()
            facts.meta["description"] = description
            return facts
        apps = {"apps/a/index.html": page("Same words."), "apps/b/index.html": page("Same words.")}
        self.assertEqual(check_design.duplicate_descriptions(apps), [])
        own = {"guides/a/index.html": page("Same words."), "guides/b/index.html": page("Same words.")}
        self.assertEqual(len(check_design.duplicate_descriptions(own)), 1)

    def test_short_markup_like_text_is_not_reported_as_unescaped(self) -> None:
        """A category of '">' appears in every page's own markup; '<script>alert(1)</script>' is still checked."""
        snapshot = {"apps": [{"slug": "a", "manifest": {"categories": ['">', "<script>alert(1)</script>"]}}]}
        self.assertEqual([text for _, text in check_site.author_strings(snapshot)], ["<script>alert(1)</script>"])


class SubmissionTests(unittest.TestCase):
    """A submission is checked against the addresses and names the listed apps already use."""

    def test_the_listed_apps_reserve_their_address_and_name(self) -> None:
        """A listed app reserves its address and its display name; one whose manifest cannot be read reserves only its address."""
        entries = [{"repo": "CellMigrationLab/NucleiSky"}, {"repo": "o/Broken"}]

        def manifest(gh: GitHub, name: str, branch: str, folder: Path | None) -> dict:
            """NucleiSky's manifest; the other repository has none."""
            if name == "o/Broken":
                raise AppProblem("no manifest")
            return {"name": "NucleiSky"}

        gh = mock.Mock(repo=mock.Mock(return_value={"default_branch": "main"}))
        with mock.patch.object(submit_app.registry, "load_all", return_value=entries), \
                mock.patch.object(submit_app.catalogue, "read_manifest", side_effect=manifest):
            taken = submit_app.taken_names(gh)
        self.assertEqual(taken, {"nucleisky": "CellMigrationLab/NucleiSky", "broken": "o/Broken"})


if __name__ == "__main__":
    unittest.main()
