"""The notebooks an author lists, and the Colab logo."""

import unittest

from lcsite import hosts, pages_apps


class NotebookTests(unittest.TestCase):
    """Only what the author lists is shown, with the right links."""

    def test_github_address_is_derived_from_a_colab_github_link(self) -> None:
        """A Colab link into a GitHub repository gives the notebook's GitHub address; any other Colab link gives none."""
        url = "https://colab.research.google.com/github/o/r/blob/main/notebooks/App/App.ipynb"
        self.assertEqual(pages_apps.github_view(url), "https://github.com/o/r/blob/main/notebooks/App/App.ipynb")
        self.assertEqual(pages_apps.github_view("https://colab.research.google.com/drive/abc"), "")

    def test_each_listed_notebook_gets_a_row_and_nothing_else_does(self) -> None:
        """One row per listed notebook with Open in Colab and View on GitHub; a Drive notebook has no GitHub link; the label is escaped."""
        html = pages_apps.notebooks_list([
            {"label": "2D <b>", "url": "https://colab.research.google.com/github/o/r/blob/main/a.ipynb"},
            {"label": "3D", "url": "https://colab.research.google.com/drive/abc"}])
        self.assertEqual(html.count("<li>"), 2)
        self.assertEqual(html.count("Open in Colab"), 2)
        self.assertEqual(html.count("View on GitHub"), 1)
        self.assertIn("2D &lt;b&gt;", html)

    def test_logo_svg_keeps_one_checked_path_only(self) -> None:
        """An icon file is reduced to its one path in the brand colour (anything else in it is dropped); several paths, another size or odd characters stop the build."""
        ok = '<svg role="img" viewBox="0 0 24 24" xmlns="x"><title>T</title><path d="M1 2l3.5-4Z"/></svg>'
        out = hosts.svg_logo(ok, "#F9AB00", "t.svg")
        self.assertIn('d="M1 2l3.5-4Z"', out)
        self.assertNotIn("title", out)
        dropped = hosts.svg_logo('<svg viewBox="0 0 24 24"><script>x</script><path d="M1 2Z"/></svg>', "#F9AB00", "t.svg")
        self.assertNotIn("script", dropped)
        for bad in ('<svg viewBox="0 0 24 24"><path d="M1 2Z"/><path d="M3 4Z"/></svg>',
                    '<svg viewBox="0 0 16 16"><path d="M1 2Z"/></svg>',
                    '<svg viewBox="0 0 24 24"><path d="M1 2Z&quot; onload=&quot;x"/></svg>'):
            with self.assertRaises(SystemExit):
                hosts.svg_logo(bad, "#F9AB00", "t.svg")


if __name__ == "__main__":
    unittest.main()
