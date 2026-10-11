"""Related projects: the file is checked strictly and the section renders only what the entries say."""

import copy
import datetime
import unittest

from lcsite import pages_related, related

ENTRY = {"name": "Tool", "approach": "Does one thing.", "fit": "you need that thing.", "repo": "o/tool", "docs": "https://tool.example/docs",
         "doi": "10.1000/abc", "reference": "A. Author et al. (2024), A Journal 1, 2-3", "shared_authors": True, "checked": datetime.date(2026, 10, 11)}
DATA = {"title": "Related", "page_title": "Other ways", "teaser": {"heading": "Related projects", "lead": "Independent projects.", "title": "Other ways to share", "text": "Other projects help.", "link": "Explore related projects"}, "intro": "Intro text.", "disclosure": "Some authors overlap.", "shared_authors_note": "Shares authors with LabConstrictor.",
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
        self.assertIn('<h3 class="lc-related__title">Tool &lt;b&gt;</h3>', html)
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

    def test_the_teaser_links_to_the_page_and_keeps_the_old_address(self) -> None:
        """The Ecosystem end has a heading with id="related" (older links), one sentence, and one card in the same grid as the tiers above, linking to the related-projects page."""
        html = pages_related.teaser(DATA)
        self.assertIn('<h2 class="lc-tier" id="related">Related projects</h2>', html)
        self.assertIn('<ul class="lc-grid">', html)
        self.assertEqual(html.count('href="related-projects/"'), 1)
        self.assertIn("Explore related projects", html)

    def test_every_category_tile_points_to_a_section_that_exists(self) -> None:
        """Each tile is an in-page link to the anchor of its group, with the names of its projects."""
        groups = DATA["groups"]
        tiles = pages_related.category_tiles(groups)
        sections = "".join(pages_related.group_html(g, DATA["shared_authors_note"]) for g in groups)
        for group in groups:
            self.assertIn(f'href="#related-{group["key"]}"', tiles)
            self.assertIn(f'id="related-{group["key"]}"', sections)
        self.assertIn("Tool", tiles)


class RealDataTests(unittest.TestCase):
    """The real file keeps the groups of the plan: repo2docker builds containers, Binder is browser and cloud, all eight projects are there."""

    def test_the_four_groups_hold_the_eight_projects(self) -> None:
        """Desktop tools, Containers, Browser and cloud, Related microscopy initiatives, with repo2docker among the containers."""
        groups = {g["key"]: [e["name"] for e in g["items"]] for g in related.load()["groups"]}
        self.assertEqual(groups, {"desktop": ["Album", "JupyterLab Desktop"], "containers": ["DL4MicEverywhere", "repo2docker"],
                                  "browser-cloud": ["Binder", "Voilà"], "microscopy": ["BiaPy", "ZeroCostDL4Mic"]})

    def test_the_page_pieces_carry_the_disclosure_data_and_every_project(self) -> None:
        """Every project name, the shared-authors note and each category link appear in the generated pieces."""
        data = related.load()
        html = pages_related.category_tiles(data["groups"]) + "".join(pages_related.group_html(g, data["shared_authors_note"]) for g in data["groups"])
        for group in data["groups"]:
            for entry in group["items"]:
                self.assertIn(entry["name"], html)
        self.assertIn(data["shared_authors_note"], html)


if __name__ == "__main__":
    unittest.main()
