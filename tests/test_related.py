"""Related projects: the file is checked strictly and the section renders only what the entries say."""

import copy
import datetime
import unittest

from lcsite import pages_related, related

ENTRY = {"name": "Tool", "approach": "Does one thing.", "fit": "you need that thing.", "repo": "o/tool", "docs": "https://tool.example/docs",
         "doi": "10.1000/abc", "reference": "A. Author et al. (2024), A Journal 1, 2-3", "shared_authors": True, "checked": datetime.date(2026, 10, 11)}
DATA = {"title": "Related", "intro": "Intro text.", "disclosure": "Some authors overlap.", "shared_authors_note": "Shares authors with LabConstrictor.",
        "groups": [{"key": "g", "title": "A group", "items": [ENTRY]}], "closing": "Closing words.", "helper": "Edit the list."}


def bad(**changes: object) -> dict:
    """A copy of the valid entry with some keys changed (a value None removes the key)."""
    entry = copy.deepcopy(ENTRY)
    for key, value in changes.items():
        if value is None:
            del entry[key]
        else:
            entry[key] = value
    return entry


class ValidationTests(unittest.TestCase):
    """The build stops, naming the file and the entry, for each kind of mistake."""

    def test_the_real_file_is_valid(self) -> None:
        """data/related-projects.yaml passes its own checks."""
        related.load()

    def test_a_valid_entry_passes(self) -> None:
        """No error for the sample."""
        related.check_entry(ENTRY)

    def test_each_mistake_stops_the_build(self) -> None:
        """Unknown key, no link, link inside prose, a volatile word, a GitHub root as docs, doi without reference, a text date, shared_authors false."""
        mistakes = [bad(extra="x"), bad(repo=None, docs=None), bad(approach="See https://x.example"), bad(fit="it is the fastest option"), bad(fit="You need it"), bad(approach="Hosted at example.org"),
                    bad(docs="https://github.com/o/tool"), bad(reference=None), bad(checked="2026-10-11"), bad(shared_authors=False), bad(doi="nope")]
        for entry in mistakes:
            with self.subTest(entry=entry), self.assertRaises(SystemExit):
                related.check_entry(entry)

    def test_a_name_listed_twice_and_a_wrong_top_level_stop_the_build(self) -> None:
        """Duplicate names and missing or extra top-level keys are errors."""
        twice = copy.deepcopy(DATA)
        twice["groups"][0]["items"].append(copy.deepcopy(ENTRY))
        with self.assertRaises(SystemExit):
            related.check_top(twice)
        with self.assertRaises(SystemExit):
            related.check_top({k: v for k, v in DATA.items() if k != "closing"})


class SectionTests(unittest.TestCase):
    """What the page shows."""

    def test_the_name_is_not_a_link_and_text_is_escaped(self) -> None:
        """The name is bold text (links are pills), and author text is escaped."""
        html = pages_related.entry_html(bad(name="Tool <b>"), DATA["shared_authors_note"])   # not validated: the renderer escapes whatever it gets
        self.assertIn("<strong>Tool &lt;b&gt;</strong>", html)
        self.assertNotIn("<b>", html)

    def test_the_shared_authors_note_and_paper_appear_only_when_set(self) -> None:
        """An entry without them shows neither; with them it shows the note, the check date and a doi link."""
        plain = pages_related.entry_html(bad(shared_authors=None, doi=None, reference=None), DATA["shared_authors_note"])
        self.assertNotIn("Shares authors", plain)
        self.assertNotIn("doi.org", plain)
        full = pages_related.entry_html(ENTRY, DATA["shared_authors_note"])
        self.assertIn("Shares authors with LabConstrictor.", full)
        self.assertIn("https://doi.org/10.1000/abc", full)
        self.assertIn("Checked 11 October 2026", full)

    def test_the_section_has_the_disclosure_the_groups_and_the_helper_links(self) -> None:
        """Disclosure is visible text; the helper line links to the citation block, the file on GitHub and the issues."""
        html = pages_related.section(DATA)
        self.assertIn('id="related"', html)
        self.assertIn("Some authors overlap.", html)
        self.assertIn('id="related-g"', html)
        for link in ("index.html#cite", "edit/main/data/related-projects.yaml", "/issues"):
            self.assertIn(link, html)


if __name__ == "__main__":
    unittest.main()
