"""Option A of the demo's notebook: the matcher settings come from the recorded defaults and are all shown."""

import re
import unittest
from unittest import mock

from lcsite import demo_option_a, pages_demo


def text() -> dict:
    """The real wording of the demo."""
    return pages_demo.load()["text"]


class OptionATests(unittest.TestCase):
    """The tabs are generated from matcher_config.json, nothing is typed by hand."""

    def test_every_setting_of_every_section_is_shown_once(self) -> None:
        """Each key of the recorded defaults has a labelled field in its own tab, and ids are unique."""
        shown = demo_option_a.values(text())["option_a_panels"]
        for section, settings in demo_option_a.load_config().items():
            for key in settings:
                self.assertIn(f'for="{demo_option_a.ident(section, key)}">{key}</label>', shown)
        ids = re.findall(r'\bid="([^"]+)"', shown)
        self.assertEqual(len(ids), len(set(ids)))

    def test_field_kinds_follow_the_value_type(self) -> None:
        """True/false is a checkbox, a number a number field, None the text None."""
        self.assertIn('type="checkbox" id="ns-a-x-y" checked', demo_option_a.field("x", "y", True))
        self.assertIn('type="number"', demo_option_a.field("x", "y", 5))
        self.assertIn('value="None"', demo_option_a.field("x", "y", None))

    def test_one_button_and_one_panel_per_tab_and_the_first_tab_is_the_state_default(self) -> None:
        """A button for each tab, a hidden panel for each tab, and the state starts on a tab that exists."""
        shown = demo_option_a.values(text())
        sections = set(demo_option_a.load_config())
        self.assertEqual(set(re.findall(r'data-tab="([^"]+)"', shown["option_a_buttons"])), sections)
        self.assertEqual(set(re.findall(r'data-a-panel="([^"]+)"', shown["option_a_panels"])), sections)
        self.assertIn("_common", sections)

    def test_wording_for_a_different_set_of_tabs_stops_the_build(self) -> None:
        """A tab without wording (or wording without a tab) is an error, not a blank tab."""
        broken = {"option_a": {"tabs": {"graph": {"title": "Graph", "description": "d"}}}}
        with self.assertRaises(SystemExit):
            demo_option_a.values(broken)

    def test_missing_config_file_stops_the_build(self) -> None:
        """No matcher_config.json: the build stops and names the tool that writes it."""
        with mock.patch.object(demo_option_a, "PATH", demo_option_a.PATH.with_name("absent.json")):
            with self.assertRaises(SystemExit):
                demo_option_a.load_config()


if __name__ == "__main__":
    unittest.main()
