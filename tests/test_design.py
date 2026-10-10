"""The design rules as code: page descriptions, link pills, the finishing step and the checker itself."""

import unittest

from lcsite import page
from lcsite.config import DOCS
from lcsite.text import lead_paragraph


class DesignTests(unittest.TestCase):
    """The pieces of the design rules that are code."""

    def test_description_is_the_opening_paragraph_without_markup(self) -> None:
        """A guide's description is its first plain paragraph, with links and emphasis removed and a hard length limit."""
        text = "# Title\n\n!!! warning \"x\"\n    boxed\n\nOne **bold** [link](https://x.org) sentence.\n\nSecond paragraph."
        self.assertEqual(lead_paragraph(text, "t.md"), "One bold link sentence.")
        long = "# T\n\n" + "word " * 100
        self.assertLessEqual(len(lead_paragraph(long, "t.md")), 161)
        self.assertTrue(lead_paragraph(long, "t.md").endswith("…"))
        with self.assertRaises(ValueError):
            lead_paragraph("# T\n\n- only a list\n", "t.md")

    def test_links_to_repositories_and_programs_become_pills(self) -> None:
        """A Markdown link to a GitHub repository gets the GitHub pill and one to napari its logo; a link to a file or another site stays."""
        out = page.decorate_links("[r](https://github.com/o/r) [napari](https://napari.org) [f](https://github.com/o/r/blob/main/a.md) [x](https://example.org)")
        self.assertEqual(out.count('class="lc-gh"'), 1)
        self.assertIn("lc-gh--host", out)
        self.assertIn("[f](https://github.com/o/r/blob/main/a.md)", out)
        self.assertIn("[x](https://example.org)", out)

    def test_finish_makes_outside_links_new_tab_and_images_lazy(self) -> None:
        """finish_site opens outside links in a new tab and lazy-loads images in <main>, and leaves inside links and the header alone."""
        import finish_site
        html = '<img src="logo.png"><main><a href="https://example.org">x</a><a href="../a/">y</a><img src="s.png"></main>'
        out = finish_site.finish(html)
        self.assertIn('target="_blank"', out.split("</a>")[0])
        self.assertNotIn("target", out.split("<a href=\"../a/\"")[1].split(">")[0])
        self.assertIn('src="s.png" loading="lazy"', out)
        self.assertIn('<img src="logo.png">', out)

    def test_design_rules_catch_what_they_claim_to(self) -> None:
        """A page that breaks the rules is reported for each break; a clean page for none."""
        import check_design
        bad = ('<html lang="fr"><head><title>t</title></head><body><main><h1>a</h1><h1>b</h1><h3>c</h3>'
               '<a href="https://example.org">here</a><a href="../x/" target="_blank">go</a><a href="https://github.com/o/r">repo</a>'
               '<img src="a.png"><button class="x">b</button></main></body></html>')
        facts = check_design.Facts()
        facts.feed(bad)
        report = "\n".join(check_design.all_problems({"p/index.html": facts}))
        for expected in ("2 h1", "lang", "no description", "skipped", "new tab with rel", "opens in a new tab", "does not say where",
                         "not a GitHub pill", "no alt attribute", "neither a copy nor"):
            self.assertIn(expected, report)


class HeroTests(unittest.TestCase):
    """The home page's second line names the programs with pills."""

    def test_the_line_has_the_pills_and_the_experimental_badge(self) -> None:
        """The hero's second line shows the text, the three program pills and an "experimental" badge, with the text escaped."""
        from lcsite import pages_site
        out = pages_site.hero_also({"also": "Also in <b>"})
        self.assertEqual(out.count("lc-gh--host"), 3)
        self.assertIn("experimental", out)
        self.assertIn("&lt;b&gt;", out)


class StyleTests(unittest.TestCase):
    """Rules about the stylesheet that broke the site once."""

    def test_the_hidden_attribute_always_wins(self) -> None:
        """lc.css must make [hidden] beat every component's display rule, or the App Centre filter hides nothing."""
        css = (DOCS / "assets" / "stylesheets" / "lc.css").read_text(encoding="utf-8")
        self.assertIn("[hidden] { display: none !important; }", css)


if __name__ == "__main__":
    unittest.main()
