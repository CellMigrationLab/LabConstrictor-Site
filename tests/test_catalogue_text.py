"""The catalogue's own sentences follow the apps: they change when the apps change, and claim only what some app offers."""

import unittest

from lcsite import catalogue_text as ct


def app(section: str = "apps", routes: tuple[str, ...] = ("installer",), systems: tuple[str, ...] = ("windows",)) -> dict:
    """A minimal app record with the given routes and installer systems."""
    release = {"assets": [{"os": s} for s in systems]} if systems else None
    return {"section": section, "manifest": {"name": "App", "summary": "S", "kind": "utility", "distribution": {r: True for r in routes}}, "release": release}


class CatalogueTextTests(unittest.TestCase):
    """Counts, ways to get an app and systems are worked out from the apps."""

    def test_the_lead_counts_apps_and_testing_apps_separately(self) -> None:
        """Four apps and two for testing: both counts appear, and the singular is correct for one."""
        apps = [app() for _ in range(4)] + [app("testing") for _ in range(2)]
        self.assertTrue(ct.catalogue_lead(apps).startswith("4 apps built with LabConstrictor, and 2 for testing and maintenance."))
        self.assertTrue(ct.catalogue_lead([app()]).startswith("1 app built with LabConstrictor."))

    def test_colab_is_mentioned_only_when_some_app_offers_it(self) -> None:
        """No Colab route, no Colab sentence; one app with Colab is enough to mention it."""
        self.assertEqual(ct.get_sentence([app()]), "Install one in a few clicks.")
        both = [app(), app(routes=("colab",), systems=())]
        self.assertEqual(ct.get_sentence(both), "Install one in a few clicks or open it in Colab.")
        self.assertEqual(ct.get_sentence([app(routes=("colab",), systems=())]), "Open it in Colab.")

    def test_nothing_is_promised_without_an_app_or_an_installer(self) -> None:
        """An empty catalogue says so; the home choice promises installers only when one exists."""
        self.assertEqual(ct.catalogue_lead([]), "No app is listed yet.")
        self.assertNotIn("Install", ct.home_find_text([app(routes=("pip",), systems=())]))
        self.assertIn("Install in a few clicks", ct.home_find_text([app()]))

    def test_the_home_text_counts_only_apps_for_users_and_names_no_field(self) -> None:
        """Testing apps are not counted on the home page, and the text does not limit the catalogue to one field of science."""
        text = ct.home_find_text([app(), app(), app("testing")])
        self.assertIn("2 apps", text)
        self.assertNotIn("image analysis", text)

    def test_systems_come_from_the_releases(self) -> None:
        """Systems are listed in the site's order and only when an installer exists; the description follows."""
        apps = [app(systems=("linux", "windows")), app(systems=("macos",)), app(routes=("colab",), systems=())]
        self.assertEqual(ct.systems(apps), ["Windows", "macOS", "Linux"])
        self.assertEqual(ct.catalogue_description(apps), "Apps built with LabConstrictor: install them on Windows, macOS or Linux, or open them in Colab.")
        self.assertEqual(ct.catalogue_description([]), "Apps built with LabConstrictor.")


if __name__ == "__main__":
    unittest.main()


class FilterTests(unittest.TestCase):
    """The filter offers only what some app has, and the search reads what the card shows."""

    def test_options_exist_only_for_values_some_app_has_and_carry_counts(self) -> None:
        """A kind, route or program that no app has is not offered; the others show how many apps have them."""
        from collections import Counter
        from lcsite import filters
        self.assertEqual(filters.options({"a": "A", "b": "B"}, Counter({"a": 3})), {"a": "A (3)"})
        self.assertEqual(filters.select("kind", "Kind", {}), "")

    def test_every_offered_option_matches_a_card_of_the_page(self) -> None:
        """For the real build input shape: each route option is a route that one of the given apps offers."""
        from lcsite import filters
        apps = [app(), app(routes=("colab",), systems=())]
        html = filters.filter_bar(apps)
        self.assertIn('value="installer"', html)
        self.assertIn('value="colab"', html)
        self.assertNotIn('value="pip"', html)
        self.assertNotIn("data-lc-host", html)

    def test_the_search_text_includes_the_kind_routes_and_programs_the_card_shows(self) -> None:
        """Words on the card (kind, "Colab", "napari") find the app."""
        from lcsite import cards
        record = app(routes=("installer", "colab"))
        record["manifest"] |= {"name": "Tracker", "summary": "Follows cells", "kind": "analysis", "hosts": ["napari"]}
        text = cards.search_text(record)
        for word in ("tracker", "analysis", "colab", "desktop", "napari", "browser"):
            self.assertIn(word, text)
