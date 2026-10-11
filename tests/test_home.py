"""The home page's sections after the hero: wording from the data files, only listed featured apps, an honest empty state, an optional plugin section."""

import unittest

from lcsite import pages_demo, pages_home as ph, pages_site
from lcsite.config import load_yaml, DATA

SITE = {"steps_title": "From notebook to app",
        "steps": [{"title": "Develop in a notebook", "text": "Run it step by step."}, {"title": "Package it", "text": "Start from the template."}, {"title": "Share the app", "text": "Publish a release."}],
        "how_tile": {"title": "How it works", "text": "See how to turn a notebook workflow into an app.", "link": "See the steps"},
        "plugins": {"title": "Use parts of your workflow in other software", "text": "Your notebook is still the main interface.", "note": "An entire notebook does not become a plugin.", "link": "Explore the ecosystem"}}


class StepsTests(unittest.TestCase):
    """The three steps come from data/site.yaml."""

    def test_the_steps_are_a_numbered_list_with_their_title_and_text(self) -> None:
        """Three steps in an ordered list under the band title."""
        html = ph.steps_band(SITE)
        self.assertIn("From notebook to app", html)
        self.assertEqual(html.count("<li>"), 3)
        self.assertIn("<strong>Package it</strong><span>Start from the template.</span>", html)

    def test_a_step_with_a_missing_or_extra_key_stops_the_build(self) -> None:
        """A step without text, or with an unknown key, is an error."""
        for bad in ({"title": "x"}, {"title": "x", "text": "y", "icon": "z"}):
            with self.assertRaises(SystemExit):
                ph.steps_band(dict(SITE, steps=[bad]))


class RealDataTests(unittest.TestCase):
    """The real data files fit the sections."""

    def test_the_real_site_data_builds_every_section(self) -> None:
        """data/site.yaml gives the steps, the How it works tile and the plugin section; the real wording promises nothing the issue rules out."""
        site = load_yaml(DATA / "site.yaml")
        html = ph.steps_band(site) + ph.how_tile(site) + ph.plugins_band(site, "Experimental", "")
        for banned in ("Packaged once", "runs everywhere", "no coding", "turn any notebook into a plugin", "one click"):
            self.assertNotIn(banned.lower(), html.lower())
        self.assertIn("notebook", site["hero"]["text"].lower())

    def test_both_tiles_have_a_picture_a_title_a_sentence_and_a_link(self) -> None:
        """The How it works tile and the demo tile are built the same way, so they look equal."""
        site = load_yaml(DATA / "site.yaml")
        for tile in (ph.how_tile(site), pages_demo.home_tile()):
            for part in ('class="lc-tile"', "<img ", "<strong>", 'class="lc-go"'):
                self.assertIn(part, tile)


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
        """The stage badge, the note and one link to the Ecosystem page."""
        html = ph.plugins_band(SITE, "Experimental", '<p class="lc-pills"></p>')
        self.assertIn(">Experimental<", html)
        self.assertIn("An entire notebook does not become a plugin.", html)
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
