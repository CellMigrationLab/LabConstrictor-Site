"""The demo page: its files, numbers, windows, and the narrow button rule the design checker allows for it."""

import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import check_design
from lcsite import demo_media, demo_option_a, pages_demo


def example() -> dict:
    """The real content/demo/example.json."""
    return demo_media.load_example()


class MediaTests(unittest.TestCase):
    """The numbers and files the windows are built from."""

    def test_values_come_from_the_example_and_every_window_placeholder_has_one(self) -> None:
        """Every {{key}} used by a window partial is a value computed from example.json; none is left over."""
        shown = dict(demo_media.values(example()), footprint=demo_media.footprint_points(example()), **demo_option_a.values(pages_demo.load()["text"]))
        for name in ("notebook", "napari", "fiji"):
            html = demo_media.render(demo_media.read_window(name), shown, name)
            self.assertNotRegex(html, r"\{\{\w+\}\}")
        self.assertEqual(shown["matcher"], example()["result"]["matcher"])
        self.assertTrue(shown["rotation"].startswith("-49."))

    def test_unknown_placeholder_stops_the_build(self) -> None:
        """A placeholder without a value is an error that names the template (no silent blank)."""
        with self.assertRaises(SystemExit):
            demo_media.render("{{nope}}", {"a": "1"}, "windows/x.html")

    def test_window_with_a_blank_line_is_refused(self) -> None:
        """Markdown would cut a window at a blank line, so the build refuses such a partial."""
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "windows").mkdir()
            (Path(tmp) / "windows" / "x.html").write_text("<div>a</div>\n\n<div>b</div>", encoding="utf-8")
            with mock.patch.object(demo_media, "SOURCE", Path(tmp)), self.assertRaises(SystemExit):
                demo_media.read_window("x")

    def test_missing_example_key_is_named(self) -> None:
        """example.json without a required key stops the build and names the key."""
        with tempfile.TemporaryDirectory() as tmp:
            data = example()
            del data["result"]["scale"]
            (Path(tmp) / "example.json").write_text(json.dumps(data), encoding="utf-8")
            with mock.patch.object(demo_media, "SOURCE", Path(tmp)), self.assertRaises(SystemExit) as ctx:
                demo_media.load_example()
            self.assertIn("result.scale", str(ctx.exception))

    def test_oversized_image_stops_the_build(self) -> None:
        """An image above the size limit is refused rather than shipped."""
        with tempfile.TemporaryDirectory() as tmp:
            for name in demo_media.IMAGES + demo_media.CODE:
                (Path(tmp) / name).write_bytes(b"x")
            (Path(tmp) / demo_media.IMAGES[0]).write_bytes(b"x" * (demo_media.MAX_BYTES + 1))
            with mock.patch.object(demo_media, "SOURCE", Path(tmp)), mock.patch.object(demo_media, "OUT", Path(tmp) / "out"), self.assertRaises(SystemExit):
                demo_media.copy_assets()

    def test_footprint_has_four_corners_inside_the_region(self) -> None:
        """The outline is four points, all inside the exported square region."""
        pairs = [tuple(map(float, p.split(","))) for p in demo_media.footprint_points(example()).split()]
        size = example()["region"]["size_px"][0]
        self.assertEqual(len(pairs), 4)
        self.assertTrue(all(0 <= x <= size and 0 <= y <= size for x, y in pairs))


class PageTests(unittest.TestCase):
    """The page's own markup."""

    def test_tabs_have_tab_semantics_and_one_is_selected(self) -> None:
        """Three buttons with role=tab, each controlling a panel; exactly one aria-selected=true."""
        html = pages_demo.tab_buttons()
        self.assertEqual(html.count('role="tab"'), 3)
        self.assertEqual(html.count('aria-selected="true"'), 1)
        for key, _ in pages_demo.TABS:
            self.assertIn(f'aria-controls="demo-panel-{key}"', html)

    def test_static_figures_have_real_alt_text(self) -> None:
        """What a reader without JavaScript sees: every image has a description and a caption."""
        html = pages_demo.static_figures(pages_demo.load()["text"])
        self.assertEqual(len(re.findall(r'alt="[^"]{20,}"', html)), len(pages_demo.STATIC))
        self.assertEqual(html.count("<figcaption>"), len(pages_demo.STATIC))

    def test_experimental_notice_and_precomputed_wording_are_in_the_data(self) -> None:
        """The honesty wording the page must carry exists in data/demo.yaml."""
        text = pages_demo.load()["text"]
        self.assertIn("precomputed", text["notice"])
        self.assertIn("Experimental", text["experimental"])
        self.assertIn("does not connect", text["how"]["note"].replace("This website does not connect", "does not connect"))


class ScriptConsistencyTests(unittest.TestCase):
    """demo.js and the window partials must agree (the script itself has no browser test here)."""

    def test_every_data_act_in_the_windows_has_a_handler(self) -> None:
        """A control marked data-act that demo.js does not handle would be dead, so each value must be a key of its actions map."""
        script = "".join((demo_media.SOURCE / name).read_text(encoding="utf-8") for name in demo_media.SCRIPTS)
        handled = set(re.findall(r"^    '([a-z-]+)':", script, re.M))
        used = set()
        for name in ("notebook", "napari", "fiji", "installer"):
            used |= set(re.findall(r'data-act="([a-z-]+)"', demo_media.read_window(name)))
        self.assertEqual(used - handled, set())

    def test_tab_panels_and_controls_reference_existing_ids(self) -> None:
        """Every aria-controls in the windows names an element that exists, and tab ids are unique."""
        shown = dict(demo_media.values(example()), footprint=demo_media.footprint_points(example()), **demo_option_a.values(pages_demo.load()["text"]))
        html = pages_demo.tab_buttons() + pages_demo.category_tabs() + '<div id="demo-cat-install"></div><div id="demo-cat-use"></div>' + pages_demo.panels(shown, example())
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)))
        for target in re.findall(r'aria-controls="([^"]+)"', html):
            self.assertIn(target, ids)

    def test_installer_values_come_from_the_stored_record_and_cover_the_placeholders(self) -> None:
        """Every {{placeholder}} of the installer window has a value taken from content/demo/installer.json, with no release needed."""
        got = demo_media.installer_values()
        shown = dict(demo_media.values(example()), **got)
        html = demo_media.render(demo_media.read_window("installer"), shown, "installer.html")
        self.assertIn("317.5 MB", html)
        self.assertNotIn("{{", html)

    def test_a_missing_or_incomplete_installer_record_stops_the_build_naming_it(self) -> None:
        """No file, or a file without a key, is an error that names content/demo/installer.json."""
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(demo_media, "SOURCE", Path(tmp)):
                with self.assertRaises(SystemExit) as gone:
                    demo_media.installer_values()
                self.assertIn("installer.json", str(gone.exception))
                (Path(tmp) / "installer.json").write_text(json.dumps({"app_name": "X"}), encoding="utf-8")
                with self.assertRaises(SystemExit) as partial:
                    demo_media.installer_values()
                self.assertIn("app_version", str(partial.exception))

    def test_the_state_typedef_names_every_field_that_fresh_returns(self) -> None:
        """The documented DemoState matches the object `fresh()` builds, field for field (they had drifted by nine fields)."""
        code = (demo_media.SOURCE / "demo-state.js").read_text(encoding="utf-8")
        documented = set(re.findall(r"@property \{[^}]+\} (\w+) -", code[: code.index("@typedef {Object} DemoContext")]))
        body = code[code.index("return {", code.index("function fresh")): code.index("};", code.index("function fresh"))]
        body = re.sub(r"\{[^{}]*\}", "{}", body)       # nested objects (acc, vis, opacity) count as one value
        returned = set(re.findall(r"(\w+):", body))
        self.assertEqual(returned - documented, set())
        self.assertEqual(documented - returned, set())

    def test_no_window_uses_a_heading_element(self) -> None:
        """Simulated-window titles are not headings, so the page's own outline stays clean."""
        for name in ("notebook", "napari", "fiji", "installer"):
            self.assertNotRegex(demo_media.read_window(name), r"<h[1-6][ >]")


class CheckerTests(unittest.TestCase):
    """The design checker's demo rule is narrow."""

    def problems(self, html: str) -> list[str]:
        """Button problems of a small page."""
        facts = check_design.Facts()
        facts.feed(f"<html><body><main>{html}</main></body></html>")
        return check_design.button_problems("t.html", facts)

    def test_demo_controls_are_allowed_only_inside_a_demo_root(self) -> None:
        """A demo button inside data-demo is fine; the same button elsewhere is a problem."""
        button = '<button type="button" class="lc-btn" data-demo-act="reset">Reset</button>'
        self.assertEqual(self.problems(f"<div data-demo>{button}</div>"), [])
        self.assertTrue(any("outside a page with a data-demo root" in p for p in self.problems(button)))

    def test_simulated_window_button_waives_only_the_site_button_style(self) -> None:
        """A control inside a simulated window need not look like a site button, but must have type=button."""
        sim = '<button type="button" data-demo-sim>Run</button>'
        self.assertEqual(self.problems(f"<div data-demo>{sim}</div>"), [])
        self.assertTrue(any("type=button" in p for p in self.problems('<div data-demo><button data-demo-sim>Run</button></div>')))

    def test_plain_buttons_are_still_refused(self) -> None:
        """A button that is neither copy, clear-filters nor a demo control still fails, even on a demo page."""
        self.assertTrue(self.problems('<div data-demo><button type="button" class="lc-btn">Go</button></div>'))


if __name__ == "__main__":
    unittest.main()
