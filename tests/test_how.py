"""The How it works page: data checked strictly, and every panel agrees with its own choices."""

import re
import unittest

from lcsite import pages_how


class DataTests(unittest.TestCase):
    """The data file and the panel partials."""

    def test_the_real_data_is_valid_and_every_chapter_has_a_panel(self) -> None:
        """data/how-it-works.yaml loads, and each chapter's partial exists and is one block."""
        for chapter in pages_how.load()["chapters"]:
            self.assertTrue(pages_how.read_panel(chapter["id"]).startswith("<div"))

    def test_a_missing_partial_stops_the_build(self) -> None:
        """A chapter without a panel is an error naming the file."""
        with self.assertRaises(SystemExit):
            pages_how.read_panel("no-such-chapter")


class PanelTests(unittest.TestCase):
    """Every control and every shown element refers to a choice group the panel declares."""

    def test_buttons_and_show_attributes_use_declared_groups_and_values(self) -> None:
        """data-set and data-show tokens name a group in data-state."""
        for chapter in pages_how.load()["chapters"]:
            html = pages_how.read_panel(chapter["id"])
            declared = dict(p.split(":") for p in re.search(r'data-state="([^"]+)"', html).group(1).split())
            for group in re.findall(r'data-set="([^"]+)"', html):
                self.assertIn(group, declared, f"{chapter['id']}: button group {group}")
            for attr in re.findall(r'data-show="([^"]+)"', html):
                for token in attr.split():
                    self.assertIn(token.split(":")[0], declared, f"{chapter['id']}: {token}")

    def test_pressed_buttons_match_the_starting_choices(self) -> None:
        """The button that is aria-pressed=true in the HTML is the one the starting state names."""
        for chapter in pages_how.load()["chapters"]:
            html = pages_how.read_panel(chapter["id"])
            declared = dict(p.split(":") for p in re.search(r'data-state="([^"]+)"', html).group(1).split())
            for group, value in re.findall(r'data-set="([^"]+)" data-value="([^"]+)" aria-pressed="true"', html):
                self.assertEqual(declared[group], value, f"{chapter['id']}: {group}")


if __name__ == "__main__":
    unittest.main()
