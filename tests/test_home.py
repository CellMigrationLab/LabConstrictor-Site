"""The home page's own sections: tiles that follow the apps and the steps, and say nothing no app offers."""

import unittest

from lcsite import pages_home as ph
from test_catalogue_text import app


class FactTests(unittest.TestCase):
    """The "Packaged once" tiles are worked out from the apps."""

    def test_the_install_tile_names_the_systems_with_an_installer(self) -> None:
        """Windows and macOS installers: both named; no installer at all: no tile."""
        html = ph.install_fact([app(systems=("windows", "macos"))])
        self.assertIn("Desktop installers for Windows and macOS.", html)
        self.assertEqual(ph.install_fact([app(routes=("pip",), systems=())]), "")

    def test_the_notebook_tile_names_only_the_routes_some_app_offers(self) -> None:
        """Colab only, then Colab and pip, then neither."""
        self.assertIn("Open the notebooks in Google Colab.", ph.notebook_fact([app(routes=("colab",), systems=())]))
        both = ph.notebook_fact([app(routes=("colab", "pip"), systems=())])
        self.assertIn("<h3>Google Colab and pip</h3>", both)
        self.assertIn("Open the notebooks in Google Colab or install the package with pip.", both)
        self.assertEqual(ph.notebook_fact([app()]), "")

    def test_the_band_leaves_out_a_tile_nothing_backs_and_keeps_the_host_tile(self) -> None:
        """An installer-only catalogue has the install tile and the image software tile, nothing about Colab or pip."""
        html = ph.works_band([app()], "Experimental plugins", '<p class="lc-pills"></p>')
        self.assertIn("Install in a few clicks", html)
        self.assertIn("In your image software", html)
        self.assertNotIn("Colab", html)


class TileTests(unittest.TestCase):
    """The How it works tile repeats the steps of data/site.yaml, nothing more."""

    def test_the_sentence_is_the_step_titles(self) -> None:
        """Three titles become one sentence, the later ones in lower case."""
        steps = [{"title": "Write notebooks"}, {"title": "Publish a release"}, {"title": "Share it"}]
        self.assertIn("Write notebooks, publish a release, share it.", ph.how_tile(steps))

    def test_join_and(self) -> None:
        """One, two and three items."""
        self.assertEqual((ph.join_and(["a"]), ph.join_and(["a", "b"]), ph.join_and(["a", "b", "c"])), ("a", "a and b", "a, b and c"))


if __name__ == "__main__":
    unittest.main()
