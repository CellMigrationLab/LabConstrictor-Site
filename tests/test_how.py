"""The How it works page: data checked strictly, and every panel agrees with its own choices."""

import copy
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


OLD_ADDRESSES = ("portable", "code", "requirements", "deposit", "tools", "branding", "packaging", "installer", "update", "sync", "manifest", "share", "bridge")


class StructureTests(unittest.TestCase):
    """Four stages first, then "Go further"; every chapter is shown once and keeps its address."""

    def test_the_four_stages_and_the_hand_over_to_the_demo(self) -> None:
        """Four stage tiles link to four stage sections; the hand-over points to the installed-app demo."""
        data = pages_how.load()
        self.assertEqual(len(data["stages"]), 4)
        tiles, body = pages_how.stage_tiles(data), pages_how.stages_html(data)
        for stage in data["stages"]:
            self.assertIn(f'href="#{stage["id"]}"', tiles)
            self.assertIn(f'id="{stage["id"]}"', body)
        self.assertIn(f'href="{data["handoff"]["href"]}"', body)
        self.assertEqual(data["handoff"]["href"], "demo/")

    def test_every_old_chapter_address_still_exists_and_the_new_one_is_added(self) -> None:
        """#portable, #code, ... keep working (shown in a stage or folded under Go further); #project is new."""
        data = pages_how.load()
        html = pages_how.stages_html(data) + pages_how.further_html(data)
        for chapter_id in OLD_ADDRESSES + ("project",):
            self.assertIn(f'id="{chapter_id}"', html, chapter_id)

    def test_further_chapters_are_folded_and_stage_chapters_are_open(self) -> None:
        """Go further uses closed native disclosures; the stages show their chapters."""
        data = pages_how.load()
        further_ids = {c for g in data["further"] for c in g["chapters"]}
        html = pages_how.further_html(data)
        for chapter_id in further_ids:
            self.assertIn(f'<details class="how__more" id="{chapter_id}">', html)
        self.assertNotIn("<details", pages_how.stages_html(data))

    def test_a_chapter_missing_from_the_layout_or_placed_twice_stops_the_build(self) -> None:
        """Unknown, doubled and unplaced chapter ids are errors that name them."""
        data = pages_how.load()
        for change in (lambda d: d["stages"][0]["chapters"].append("nope"), lambda d: d["further"][0]["chapters"].append("portable"),
                       lambda d: d["stages"][0]["chapters"].remove("portable")):
            broken = copy.deepcopy(data)
            change(broken)
            with self.assertRaises(SystemExit):
                pages_how.check_placement(broken)

    def test_wrong_keys_stop_the_build(self) -> None:
        """A stage without an outcome, or with an unknown key, is an error."""
        with self.assertRaises(SystemExit):
            pages_how.check_keys("stage x", {"id": "a"}, pages_how.STAGE_KEYS)
        with self.assertRaises(SystemExit):
            pages_how.check_keys("handoff", {"text": "t", "link": "l", "href": "h", "extra": 1}, pages_how.HANDOFF_KEYS)


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
