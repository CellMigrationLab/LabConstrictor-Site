"""The How it works page: the data is checked strictly, and the page is one step at a time with a guide behind every step."""

import copy
import unittest

from lcsite import pages_how


class DataTests(unittest.TestCase):
    """The data file."""

    def test_the_real_data_is_valid(self) -> None:
        """data/how-it-works.yaml loads: five steps, each with things to remember and at least one guide."""
        data = pages_how.load()
        self.assertEqual(len(data["steps"]), 5)
        for step in data["steps"]:
            self.assertTrue(step["know"] and step["guides"], step["id"])

    def test_wrong_keys_stop_the_build(self) -> None:
        """A step without its keys, or with an unknown key, is an error that names the data file."""
        with self.assertRaises(SystemExit):
            pages_how.check_keys("step x", {"id": "a"}, pages_how.STEP_KEYS)
        with self.assertRaises(SystemExit):
            pages_how.check_keys("handoff", {"text": "t", "link": "l", "href": "h", "extra": 1}, pages_how.HANDOFF_KEYS)

    def test_repeated_ids_and_empty_lists_stop_the_build(self) -> None:
        """Two steps with one id, a step with nothing to remember and a step without guides are each an error."""
        steps = pages_how.load()["steps"]
        for change in (lambda s: s[1].update(id=s[0]["id"]), lambda s: s[0].update(know=[]), lambda s: s[0].update(guides=[])):
            broken = copy.deepcopy(steps)
            change(broken)
            with self.assertRaises(SystemExit):
                pages_how.check_steps(broken)


class PageTests(unittest.TestCase):
    """What the page shows."""

    def test_every_step_has_a_numbered_link_a_section_and_its_guides(self) -> None:
        """The row of numbered links and the sections agree, and each section links to its guides."""
        data = pages_how.load()
        row = pages_how.stepper(data)
        for i, step in enumerate(data["steps"]):
            html = pages_how.step_html(data, i)
            self.assertIn(f'href="#{step["id"]}"', row)
            self.assertIn(f'id="{step["id"]}"', html)
            for guide in step["guides"]:
                self.assertIn(f'href="{guide["href"]}"', html)

    def test_the_steps_lead_to_each_other_and_the_last_hands_over_to_the_demo(self) -> None:
        """The first step has no Back, the middle ones have both, and the last step has the hand-over to the demo instead of Next."""
        data = pages_how.load()
        first, middle, last = (pages_how.step_html(data, i) for i in (0, 1, len(data["steps"]) - 1))
        self.assertNotIn("how__back", first)
        self.assertIn("how__next", first)
        self.assertTrue("how__back" in middle and "how__next" in middle)
        self.assertNotIn("how__next", last)
        self.assertIn(f'href="{data["handoff"]["href"]}"', last)
        self.assertEqual(data["handoff"]["href"], "demo/")

    def test_customisation_is_shown_only_where_there_is_something_to_customise(self) -> None:
        """Steps 1, 2 and 5 have a "Make it yours" tile; a step with an empty list has none."""
        data = pages_how.load()
        for i, step in enumerate(data["steps"]):
            self.assertEqual("Make it yours" in pages_how.step_html(data, i), bool(step["customise"]), step["id"])
        self.assertEqual([bool(s["customise"]) for s in data["steps"]], [True, True, False, False, True])

    def test_the_picture_at_the_side_frames_each_of_the_first_five_steps_and_shows_the_end_for_the_last(self) -> None:
        """One loop and one fade per step 1 to 5, and the end-user picture of the same figure (shown at the last step); alt texts, sizes, caption and the CC BY credit are there; a missing picture stops the build."""
        data = pages_how.load()
        html = pages_how.map_html(data)
        for i in range(1, 6):
            self.assertIn(f'class="how__loop" data-for="{i}"', html)
            self.assertIn(f'class="how__hl" data-for="{i}"', html)
        self.assertNotIn('data-for="6"', html)   # there are five steps
        self.assertRegex(html, r'alt="[^"]{80,}" width="\d+" height="\d+"')
        self.assertIn(data["figure_credit"]["href"], html)
        self.assertIn("CC BY 4.0", data["figure_credit"]["text"])
        self.assertIn('class="how__end"', html)

    def test_a_region_that_is_not_four_numbers_or_empty_stops_the_build(self) -> None:
        """A step's region is [x, y, width, height] or []; anything else is an error naming the step."""
        for bad in ([1, 2, 3], ["a", 1, 2, 3], "none"):
            steps = copy.deepcopy(pages_how.load()["steps"])
            steps[0]["region"] = bad
            with self.assertRaises(SystemExit):
                pages_how.check_steps(steps)

    def test_a_line_that_yaml_turned_into_a_mapping_stops_the_build(self) -> None:
        """An unquoted "a: b" in a list is read as a mapping; the build names the step instead of printing a dict."""
        steps = copy.deepcopy(pages_how.load()["steps"])
        steps[0]["know"].append({"The notebook is your app's interface": "its text is yours."})
        with self.assertRaises(SystemExit):
            pages_how.check_steps(steps)

    def test_there_is_no_code_and_no_interactive_control(self) -> None:
        """The overview shows no code block and no button: the guides do the detail."""
        data = pages_how.load()
        html = pages_how.stepper(data) + "".join(pages_how.step_html(data, i) for i in range(len(data["steps"])))
        for banned in ("<pre", "<code", "<button", "data-demo-sim"):
            self.assertNotIn(banned, html)


if __name__ == "__main__":
    unittest.main()
