"""The home page's sections after the hero: wording from the data files, only listed featured apps, an honest empty state, an optional plugin section."""

import unittest
from unittest import mock

from lcsite import pages_demo, pages_home as ph, pages_how, pages_site
from lcsite.config import load_yaml, DATA

SITE = {"steps_title": "From notebook to app",
        "how_tile": {"title": "How it works", "text": "See how to turn a notebook workflow into an app.", "link": "See the steps"},
        "plugins": {"title": "Make your workflow available in other software", "text": "Your notebook is still the main interface.", "link": "Explore the ecosystem"}}


class StepsTests(unittest.TestCase):
    """The home page's steps are the steps of How it works, written once in data/how-it-works.yaml."""

    def test_the_steps_mirror_how_it_works_in_order_and_link_to_each_step(self) -> None:
        """One numbered item per How it works step, in the same order, each title linked to its step and followed by its summary."""
        steps = pages_how.load()["steps"]
        html = ph.steps_band("From notebook to app", steps)
        self.assertIn("From notebook to app", html)
        self.assertEqual(html.count("<li>"), len(steps))
        positions = [html.index(f'href="how-it-works/#{s["id"]}"') for s in steps]
        self.assertEqual(positions, sorted(positions))
        for step in steps:
            self.assertIn(f'>{step["title"]}</a></strong><span>', html.replace("&#x27;", "'").replace("(s)", "(s)"))


class RealDataTests(unittest.TestCase):
    """The real data files fit the sections."""

    def test_the_real_site_data_builds_every_section(self) -> None:
        """data/site.yaml gives the steps, the How it works tile and the plugin section; the real wording promises nothing the issue rules out."""
        site = load_yaml(DATA / "site.yaml")
        html = ph.steps_band(site["steps_title"], pages_how.load()["steps"]) + ph.how_tile(site) + ph.plugins_band(site, "")
        for banned in ("Packaged once", "runs everywhere", "no coding", "turn any notebook into a plugin", "one click"):
            self.assertNotIn(banned.lower(), html.lower())
        self.assertIn("notebook", site["hero"]["text"].lower())

    def test_both_tiles_have_a_picture_a_title_a_sentence_and_a_link(self) -> None:
        """The How it works tile and the demo tile are built the same way, so they look equal."""
        site = load_yaml(DATA / "site.yaml")
        for tile in (ph.how_tile(site), pages_demo.home_tile()):
            for part in ('class="lc-tile"', "<img ", '<h3 class="lc-tile__title">', 'class="lc-go"'):
                self.assertIn(part, tile)

    def test_the_tiles_sit_under_their_own_heading(self) -> None:
        """The band has an h2 from site.yaml ("See it in action") before the tiles, whose titles are h3."""
        site = load_yaml(DATA / "site.yaml")
        html = ph.tiles_band(site["tiles_title"], [ph.how_tile(site)])
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
