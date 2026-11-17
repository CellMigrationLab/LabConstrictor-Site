"""Lists written for GitHub render on the site as they do on GitHub (lcsite.gfm), checked through the site's own Markdown extensions."""

import re
import unittest

import markdown
import yaml

from lcsite import gfm
from lcsite.config import ROOT


def site_extensions() -> list:
    """The Markdown extensions of mkdocs.yml, as Python-Markdown takes them."""
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    return [next(iter(e)) if isinstance(e, dict) else e for e in config["markdown_extensions"]]


def render(text: str) -> str:
    """The HTML the site makes of `text`, after the GitHub list habits are rewritten."""
    return markdown.markdown(gfm.lists(text), extensions=site_extensions())


def shape(html: str) -> str:
    """Only the list, paragraph, quote and code tags, to compare structure."""
    html = re.sub(r'<div class="highlight"><pre>.*?</pre></div>|<pre>.*?</pre>', "<pre/>", html, flags=re.S)
    return "".join(re.findall(r"</?(?:ol|ul|li|p|blockquote)>|<pre/>", html))


class GithubListTests(unittest.TestCase):
    """Each habit that broke a page on the site, as a small example."""

    def test_a_list_right_after_a_sentence_is_a_list(self) -> None:
        """use-cases, microscope, notebook-upload: no blank line between the sentence and the list."""
        html = render("Here are the tools:\n - [VLab4Mic](#vlab4mic)\n - NucleiSky\n")
        self.assertEqual(shape(html), "<p></p><ul><li></li><li></li></ul>")
        self.assertNotIn("- ", re.sub(r"<[^>]+>", "", html))

    def test_a_code_block_inside_a_numbered_item_stays_in_it_and_the_numbering_goes_on(self) -> None:
        """tools-bridge: text and code under "1." indented 3 spaces, then "2." straight after the item's last paragraph."""
        text = ("1. Add a module:\n\n   ```python\n   @tool(\"Blur\")\n   def blur(image):\n       return image\n   ```\n\n"
                "   Keep it light.\n2. Import it late.\n3. Name the programs.\n")
        html = render(text)
        self.assertNotIn("```", html)
        self.assertEqual(shape(html), "<ol><li><p></p><pre/><p></p></li><li><p></p></li><li></li></ol>")
        self.assertIn("    return image", re.sub(r"<[^>]+>", "", html))   # the code keeps its own indentation

    def test_a_sub_list_indented_two_spaces_is_nested(self) -> None:
        """GitHub nests "  - b" under "- a"; Python-Markdown needs 4 spaces."""
        self.assertEqual(shape(render("- a\n  - b\n  - c\n- d\n")), "<ul><li><ul><li></li><li></li></ul></li><li></li></ul>")

    def test_a_quote_right_after_an_items_text_is_a_quote_inside_the_item(self) -> None:
        """notebook-requirements, executable-creation: "  > **Note**" on the line after the item's text."""
        html = render("* **Locally:** download it.\n  > **Note**: use the same environment.\n* **Colab:** open it.\n")
        self.assertIn("<blockquote>", html)
        self.assertNotIn("&gt;", html)

    def test_a_tight_list_stays_tight(self) -> None:
        """Items with no blank line between them get no paragraphs (no blank line is added between them)."""
        self.assertEqual(gfm.lists("1. a\n2. b\n3. c\n"), "1. a\n2. b\n3. c\n")
        self.assertEqual(shape(render("- a\n- b\n")), "<ul><li></li><li></li></ul>")

    def test_code_outside_a_list_is_never_changed(self) -> None:
        """List-like lines inside a code block stay exactly as written."""
        text = "Run:\n\n```text\n- not a list\n1. not either\n   indented\n```\n"
        self.assertEqual(gfm.lists(text), text)

    def test_text_without_lists_is_unchanged(self) -> None:
        """Headings, paragraphs, tables and admonitions pass through as they are."""
        text = "# Title\n\nSome text.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n!!! note \"Box\"\n    Inside the box.\n"
        self.assertEqual(gfm.lists(text), text)

    def test_a_number_inside_a_sentence_does_not_start_a_list(self) -> None:
        """GitHub only lets an ordered list that starts at 1 break a paragraph, so "2026. was" on its own line stays text."""
        self.assertEqual(gfm.lists("It happened in\n2026. Then more.\n"), "It happened in\n2026. Then more.\n")

    def test_a_heading_right_after_an_item_ends_the_list(self) -> None:
        """GitHub ends the list at "## Heading"; the text after it is a paragraph, not a code block made by a 4-space indent."""
        html = render("- item\n## Heading\n\n  Some text\n")
        self.assertIn("<h2", html)
        self.assertEqual(shape(html), "<ul><li></li></ul><p></p>")

    def test_a_list_of_another_kind_right_after_a_list_is_a_second_list(self) -> None:
        """Bullets then numbers with no blank line, and a bullet under a numbered item but less indented than its text: two lists."""
        self.assertEqual(shape(render("- a\n- b\n1. one\n2. two\n")), "<ul><li></li><li></li></ul><ol><li></li><li></li></ol>")
        self.assertEqual(shape(render("1. Step one\n  - detail\n")), "<ol><li></li></ol><ul><li></li></ul>")

    def test_a_list_already_written_for_python_markdown_still_renders_the_same(self) -> None:
        """A list with 4-space continuation (the site's own hand-written guides) keeps its structure."""
        text = "1. First step.\n\n    More about it.\n\n2. Second step.\n"
        before = shape(markdown.markdown(text, extensions=site_extensions()))
        self.assertEqual(shape(render(text)), before)


if __name__ == "__main__":
    unittest.main()
