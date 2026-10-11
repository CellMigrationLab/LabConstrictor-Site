"""The facts of an app page (works with, produces, limitations, stage) and the warnings for what a manifest leaves out."""

import unittest

from lcsite import completeness, pages_facts


def app(kind: str = "analysis", section: str = "apps", **extra: object) -> dict:
    """A minimal app record with the given manifest fields."""
    return {"section": section, "manifest": {"name": "X", "kind": kind} | extra}


class FactsTests(unittest.TestCase):
    """What the page says for a fact that is there, and for one that is not."""

    def test_inputs_and_outputs_are_listed_as_escaped_plain_text(self) -> None:
        """The authors' lines appear under Works with and Produces, and HTML in them is escaped."""
        html = pages_facts.works_with(app(inputs=["TIFF <img src=x>"], outputs=["A table of positions"]))
        self.assertIn("Works with", html)
        self.assertIn("Produces", html)
        self.assertIn("TIFF &lt;img src=x&gt;", html)
        self.assertNotIn("<img", html)

    def test_a_scientific_app_without_them_says_not_stated_and_others_say_nothing(self) -> None:
        """Analysis, segmentation and simulation apps get the muted line; a utility or testing app gets nothing."""
        self.assertIn("not stated by the author", pages_facts.works_with(app("segmentation")))
        self.assertEqual(pages_facts.works_with(app("utility")), "")
        self.assertEqual(pages_facts.works_with(app("analysis", section="testing")), "")

    def test_limitations_only_when_listed(self) -> None:
        """No limitations, no section and no placeholder."""
        self.assertEqual(pages_facts.limitations(app()), "")
        self.assertIn("Only 2D images", pages_facts.limitations(app(limitations=["Only 2D images"])))

    def test_status_is_what_the_authors_state_or_not_stated(self) -> None:
        """The row shows the status or "Not stated"; a chip appears only for Experimental and Deprecated."""
        self.assertEqual(pages_facts.status_row(app()), "Not stated")
        self.assertEqual(pages_facts.status_row(app(status="Available")), "Available")
        self.assertEqual(pages_facts.status_chip(app(status="Available")), "")
        self.assertIn("Experimental", pages_facts.status_chip(app(status="Experimental")))


class CompletenessTests(unittest.TestCase):
    """Missing facts are warnings, never a reason to leave an app out."""

    def test_a_bare_scientific_app_lacks_the_recommended_facts(self) -> None:
        """Status, quickstart, screenshots, inputs, outputs and a license are each reported once."""
        lacks = completeness.missing({"kind": "analysis"}, "apps", None)
        self.assertEqual(len(lacks), 6)
        for word in ("status", "quickstart", "screenshots", "inputs", "outputs", "license"):
            self.assertTrue(any(word in line for line in lacks))

    def test_other_kinds_do_not_need_inputs_and_testing_apps_are_not_checked(self) -> None:
        """A game is not asked for inputs and outputs; a testing app is not asked for anything."""
        self.assertFalse(any("inputs" in line for line in completeness.missing({"kind": "game"}, "apps", "MIT")))
        self.assertEqual(completeness.missing({"kind": "analysis"}, "testing", None), [])

    def test_a_complete_manifest_has_no_warning(self) -> None:
        """Nothing is reported when every recommended fact is there."""
        full = {"kind": "analysis", "status": "Available", "quickstart": ["x"], "screenshots": [], "inputs": ["a"], "outputs": ["b"]}
        self.assertEqual(completeness.missing(full, "apps", "MIT"), [])


if __name__ == "__main__":
    unittest.main()


class SampleManifestTests(unittest.TestCase):
    """The manifest sample on the Submit page is valid, and the new fields are checked."""

    def sample(self) -> dict:
        """The YAML block of content/submit.md with the schema line removed."""
        import re
        from pathlib import Path
        from lcsite.validate import load_plain_yaml
        text = (Path(__file__).resolve().parents[1] / "content" / "submit.md").read_text(encoding="utf-8")
        block = re.search(r"```yaml\n(.*?)```", text, re.S).group(1)
        return load_plain_yaml(block, "content/submit.md")

    def test_the_submit_page_sample_validates(self) -> None:
        """Copying the sample gives a valid manifest."""
        from lcsite.validate import check
        check(self.sample(), "labconstrictor-app.schema.json", "sample")

    def test_new_fields_have_limits_and_a_fixed_vocabulary(self) -> None:
        """Too many items, too long a line or an unknown status is refused with the field named."""
        from lcsite.validate import check
        from lcsite.config import AppProblem
        for field, value in (("inputs", ["x" * 201]), ("outputs", ["ok line"] * 7), ("limitations", []), ("status", "Soon")):
            with self.assertRaises(AppProblem) as ctx:
                check(self.sample() | {field: value}, "labconstrictor-app.schema.json", "t")
            self.assertIn(field, str(ctx.exception))
