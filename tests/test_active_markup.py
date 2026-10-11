"""Imported guides cannot carry code that runs: each way of smuggling it in is refused, and ordinary guide content is left alone."""

import unittest

import check_site
from lcsite import active_markup


def page(body: str, outside: str = "") -> str:
    """A built page: the theme's own markup outside, the guide's text inside the article."""
    return f'<html><head>{outside}</head><body><main><article class="md-content__inner md-typeset">{body}</article></main></body></html>'


class RefusedTests(unittest.TestCase):
    """Every way of getting script into a guide is found."""

    def test_each_attack_is_found(self) -> None:
        """Script, frame, handler, script addresses (with entities and hidden characters), srcset, svg handler, meta refresh."""
        attacks = {
            "script": "<script>alert(1)</script>",
            "frame": '<iframe srcdoc="<p>x</p>"></iframe>',
            "handler": '<img src="a.png" alt="" onerror="alert(1)">',
            "javascript link": '<a href="javascript:alert(1)">x</a>',
            "entity scheme": '<a href="&#106;avascript:alert(1)">x</a>',
            "tab in scheme": '<a href="java&#9;script:alert(1)">x</a>',
            "data page": '<a href="data:text/html;base64,AAAA">x</a>',
            "srcset": '<img srcset="a.png 1x, javascript:alert(1) 2x" alt="">',
            "svg handler": '<svg onload="alert(1)"></svg>',
            "meta refresh": '<meta http-equiv="refresh" content="0;url=https://evil.example">',
            "object": '<object data="x.swf"></object>',
            "form": '<form action="https://evil.example"><input name="p"></form>',
        }
        for name, html in attacks.items():
            with self.subTest(name):
                self.assertTrue(active_markup.problems(page(html)), name)


class AllowedTests(unittest.TestCase):
    """Ordinary guide content passes."""

    def test_ordinary_content_and_the_theme_are_left_alone(self) -> None:
        """Links, pictures, tables, code, details and admonitions pass, and the theme's scripts outside the article are not the guide's."""
        body = ('<h1>Title</h1><p><a href="https://example.org/x">x</a> <a href="../other/#a">y</a></p><img src="../../assets/docs-img/a.png" alt="a">'
                '<table><tr><td>1</td></tr></table><pre><code>print(1)</code></pre><details><summary>s</summary>t</details><div class="admonition">n</div>'
                '<p>Text that mentions &lt;script&gt; and onclick= in prose.</p>')
        self.assertEqual(active_markup.problems(page(body, outside="<script>var theme=1</script>")), [])


class BuiltSiteTests(unittest.TestCase):
    """check_site applies the scan to the guide, use and build pages."""

    def test_the_check_reads_the_built_pages(self) -> None:
        """With no site built the function returns a list (empty or not) and never raises."""
        self.assertIsInstance(check_site.imported_markup_problems(), list)


if __name__ == "__main__":
    unittest.main()
