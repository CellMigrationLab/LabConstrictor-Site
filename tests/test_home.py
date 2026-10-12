"""The home page's sections after the hero: wording from the data files, only listed featured apps, an honest empty state, an optional plugin section."""

import unittest
from unittest import mock

from lcsite import pages_demo, pages_home as ph, pages_site
from lcsite.config import load_yaml, DATA

SITE = {"plugins": {"title": "Make your workflow available in other software", "text": "Your notebook is still the main interface.", "link": "Explore the ecosystem"}}


class RealDataTests(unittest.TestCase):
    """The real data files fit the sections."""

    def test_the_real_site_data_builds_every_section(self) -> None:
        """data/site.yaml gives the plugin section; the real wording promises nothing the issue rules out."""
        site = load_yaml(DATA / "site.yaml")
        html = ph.plugins_band(site, "")
        for banned in ("Packaged once", "runs everywhere", "no coding", "turn any notebook into a plugin", "one click", "few clicks"):
            self.assertNotIn(banned.lower(), html.lower())
        self.assertIn("notebook", site["hero"]["text"].lower())

    def test_two_demo_tiles_without_pictures_open_the_two_parts_of_the_demo(self) -> None:
        """The installation tile comes first and opens /demo/ (its first part), the installed-app tile /demo/?demo=use; both are built the same way and have no picture."""
        tiles = pages_demo.home_tiles()
        self.assertEqual(len(tiles), 2)
        self.assertIn('href="demo/"', tiles[0])
        self.assertIn("(Windows)", tiles[0])
        self.assertIn('href="demo/?demo=use"', tiles[1])
        for tile in tiles:
            for part in ('class="lc-tile"', '<h3 class="lc-tile__title">', 'class="lc-go"'):
                self.assertIn(part, tile)
            self.assertNotIn("<img", tile)

    def test_a_tile_naming_an_unknown_part_stops_the_build(self) -> None:
        """Only the two parts of the demo can be named."""
        with self.assertRaises(ValueError):
            pages_demo.part_url("napari")

    def test_the_tiles_sit_under_their_own_heading(self) -> None:
        """The band has an h2 from site.yaml ("See it in action") before the tiles, whose titles are h3."""
        site = load_yaml(DATA / "site.yaml")
        html = ph.tiles_band(site["tiles_title"], pages_demo.home_tiles())
        self.assertTrue(html.startswith('<section class="lc-band"><h2 class="lc-title">See it in action</h2>'))


class FeaturedTests(unittest.TestCase):
    """Only listed, featured apps; and none is a statement, not an empty grid."""

    def test_testing_apps_are_never_featured(self) -> None:
        """A featured app kept apart under testing is not shown."""
        apps = [{"featured": True, "section": "apps", "n": 1}, {"featured": True, "section": "testing", "n": 2}, {"featured": False, "section": "apps", "n": 3}]
        self.assertEqual([a["n"] for a in ph.featured_apps(apps)], [1])

    def test_no_featured_app_says_so_and_still_links_to_every_app(self) -> None:
        """No card, a plain sentence, and the link to the App Centre."""
        html = ph.featured_band([], "No app is featured yet.")
        self.assertIn("No app is featured yet.", html)
        self.assertNotIn("<ul", html)
        self.assertIn('href="apps/"', html)


class PluginTests(unittest.TestCase):
    """The plugin section is optional, experimental and has one link."""

    def test_the_section_names_the_stage_and_links_to_the_ecosystem_once(self) -> None:
        """The stage chip (in the row of pills), no claim about operating systems, and one link to the Ecosystem page."""
        from lcsite import pages_site
        with mock.patch.object(pages_site.hosts, "load", return_value={}):
            row = pages_site.program_pill_row("Experimental")
        html = ph.plugins_band(SITE, row)
        self.assertIn(">Experimental<", html)
        self.assertNotIn("Linux", html)
        self.assertEqual(html.count('href="ecosystem/"'), 1)


class EcosystemCardTests(unittest.TestCase):
    """The card of a plugin says what the project is."""

    CARD = {"name": "napari", "summary": "One dock widget.", "status": "Experimental", "link": "https://github.com/o/n", "repo": "o/n", "guide": None}

    def test_a_plugin_card_is_titled_plugin_for_the_program_and_other_cards_keep_their_name(self) -> None:
        """"napari" becomes "Plugin for napari" (the logo stays); a card with no program keeps the name its project gave it."""
        plugin = pages_site.ecosystem_card(dict(self.CARD, host="napari"))
        self.assertIn("<strong>Plugin for napari</strong>", plugin)
        self.assertIn("lc-logo", plugin)
        other = pages_site.ecosystem_card(dict(self.CARD, name="LabConstrictor-Tools", host=None))
        self.assertIn("<strong>LabConstrictor-Tools</strong>", other)
        self.assertNotIn("Plugin for", other)


if __name__ == "__main__":
    unittest.main()
