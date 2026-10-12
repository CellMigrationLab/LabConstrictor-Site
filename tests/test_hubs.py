"""The hub pages: the data is checked strictly and the demo and how-it-works lines appear where readers choose a track."""

import unittest

from lcsite import hubs, pages_how

class HubDataTests(unittest.TestCase):
    """A hub key that nothing reads stops the build; the Build hub shows the steps of How it works."""

    def test_an_unknown_hub_key_stops_the_build(self) -> None:
        """A key nobody reads (a typo, or a stale block) is an error naming data/hubs.yaml."""
        with self.assertRaises(SystemExit):
            hubs.check_hub("use", {"title": "t", "lead": "l", "cards": [], "hepl": {}})

    def test_the_build_flow_is_the_steps_of_how_it_works(self) -> None:
        """The Build hub shows the steps of How it works as cards, each linking to its step there."""
        steps = pages_how.load()["steps"]
        html = hubs.flow_html("From notebook to app", steps)
        self.assertEqual(html.count('<a class="lc-stepcard"'), len(steps))
        for step in steps:
            self.assertIn(f'href="how-it-works/#{step["id"]}"', html)

    def test_steps_and_card_heading_come_together(self) -> None:
        """A hub with steps needs the heading of the cards under them (and the reverse): the Build page opens with the steps."""
        with self.assertRaises(SystemExit):
            hubs.check_hub("build", {"title": "t", "lead": "l", "cards": [], "flow_title": "Steps"})
        hubs.check_hub("build", {"title": "t", "lead": "l", "cards": [], "flow_title": "Steps", "why_title": "Why"})

    def test_the_notes_hold_the_demo_and_how_lines_and_no_help_line(self) -> None:
        """The demo and how-it-works lines render with their link; a help line is no longer shown; no notes give an empty string."""
        html = hubs.notes_html({"how": {"title": "Inside?", "text": "Read this.", "href": "g/", "link": "Go"}, "help": {"title": "Stuck?", "text": "x", "href": "h/", "link": "Help"}})
        self.assertIn("Inside?", html)
        self.assertIn('href="g/"', html)
        self.assertNotIn("Stuck?", html)
        self.assertEqual(hubs.notes_html({"title": "t"}), "")


if __name__ == "__main__":
    unittest.main()
