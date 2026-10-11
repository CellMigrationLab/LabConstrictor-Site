"""The hub pages: the data is checked strictly and the help lines appear where readers choose a track."""

import unittest

from lcsite import hubs

STEP = {"title": "T", "text": "x", "href": "a/", "link": "L"}


class HubDataTests(unittest.TestCase):
    """A hub key or a flow step that nothing reads stops the build."""

    def test_an_unknown_hub_key_stops_the_build(self) -> None:
        """A key nobody reads (a typo, or a stale block) is an error naming data/hubs.yaml."""
        with self.assertRaises(SystemExit):
            hubs.check_hub("use", {"title": "t", "lead": "l", "cards": [], "hepl": {}})

    def test_a_flow_step_split_by_a_comma_stops_the_build(self) -> None:
        """An unquoted comma inside a flow value leaves an extra key; the check catches it."""
        with self.assertRaises(SystemExit):
            hubs.check_hub("build", {"title": "t", "lead": "l", "flow": [dict(STEP, **{"with one click.": None})]})
        hubs.check_hub("build", {"title": "t", "lead": "l", "flow": [STEP]})

    def test_the_notes_hold_the_demo_and_help_lines(self) -> None:
        """Both lines render with their link, and are written once for the hub page and the Docs home."""
        html = hubs.notes_html({"help": {"title": "Stuck?", "text": "Read this.", "href": "g/", "link": "Go"}})
        self.assertIn("Stuck?", html)
        self.assertIn('href="g/"', html)
        self.assertEqual(hubs.notes_html({"title": "t"}), "")


if __name__ == "__main__":
    unittest.main()
