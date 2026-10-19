"""The macOS installer walkthrough of the demo: its page, its record, its flow, and that it says nothing it cannot back up."""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lcsite import demo_media, pages_demo, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "demo_assets"))
import installer_record  # noqa: E402


def mac_html() -> str:
    """The macOS installer partial with every placeholder filled from the stored record."""
    return demo_media.render(demo_media.read_window("installer", "macos"), demo_media.installer_values(), "macos/installer.html")


def pages() -> dict[str, str]:
    """The partial's pages, each as its HTML, by data-page value."""
    parts = re.split(r'<div class="mi__page" data-page="', demo_media.read_window("installer", "macos"))[1:]
    return {p.split('"', 1)[0]: p for p in parts}


class RecordTests(unittest.TestCase):
    """The package the walkthrough names comes from the stored record, never from a current release."""

    def test_the_values_come_from_the_stored_record(self) -> None:
        """The package name, its size and the disk space it asks for are filled from content/demo/installer.json."""
        got = demo_media.installer_values()
        self.assertTrue(got["pkg_name"].endswith("-MacOSX-arm64.pkg"))
        self.assertTrue(got["pkg_name"].startswith(f"{got['app_name']}-{got['app_version']}-"))
        self.assertEqual(got["pkg_size"], "191.7 MB")
        self.assertEqual(got["pkg_install_gb"], "1.3")
        self.assertEqual(got["install_home"], "~/nucleisky")

    def test_gigabytes_are_kibibytes_times_1024_over_10_to_the_9(self) -> None:
        """installKBytes counts units of 1024 bytes: 1307878 is 1.34 GB, shown as 1.3; a small number keeps its decimal."""
        self.assertEqual(text.gigabytes_from_kbytes(1307878), "1.3")
        self.assertEqual(text.gigabytes_from_kbytes(2_000_000), "2.0")

    def test_a_record_without_the_package_fields_stops_the_build_naming_them(self) -> None:
        """An installer.json written before the macOS walkthrough (no pkg fields) is an error that names the missing keys."""
        old = {"app_name": "X", "app_version": "1", "exe_name": "x.exe", "exe_size_bytes": 1, "source": {}}
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "installer.json").write_text(json.dumps(old), encoding="utf-8")
            with mock.patch.object(demo_media, "SOURCE", Path(tmp)), self.assertRaises(SystemExit) as err:
                demo_media.installer_values()
        self.assertIn("pkg_name", str(err.exception))
        self.assertIn("pkg_install_kbytes", str(err.exception))

    def test_the_recording_tool_picks_the_arm64_package_and_refuses_what_is_missing(self) -> None:
        """installer_record reads the one Windows .exe and the one arm64 .pkg of the release, and stops when one is absent or the disk space is not positive."""
        assets = [{"name": "A-1-Windows-x86_64.exe", "os": "windows", "arch": "x86_64", "size": 5}, {"name": "A-1-Windows-x86_64.msi", "os": "windows", "arch": "x86_64", "size": 4},
                  {"name": "A-1-MacOSX-arm64.pkg", "os": "macos", "arch": "arm64", "size": 3}, {"name": "A-1-MacOSX-x86_64.pkg", "os": "macos", "arch": "x86_64", "size": 2}]
        snap = {"apps": [{"slug": "nucleisky", "manifest": {"name": "A"}, "release": {"tag": "1", "url": "u", "assets": assets}}]}
        record = installer_record.build_record(snap, "2026-01-01", 1000)
        self.assertEqual((record["exe_name"], record["pkg_name"], record["pkg_size_bytes"], record["pkg_install_kbytes"]), ("A-1-Windows-x86_64.exe", "A-1-MacOSX-arm64.pkg", 3, 1000))
        with self.assertRaises(SystemExit):
            installer_record.build_record(snap, "2026-01-01", 0)
        snap["apps"][0]["release"]["assets"] = assets[:2]
        with self.assertRaises(SystemExit) as err:
            installer_record.build_record(snap, "2026-01-01", 1000)
        self.assertIn(".pkg", str(err.exception))


class FlowTests(unittest.TestCase):
    """Every page of the walkthrough exists, leads somewhere that exists, and can be reached from the first one."""

    def test_the_pages_are_the_ones_the_real_flow_has_in_order(self) -> None:
        """Download, the two warnings and Privacy & Security, the seven installer pages (with the licence sheet), the Bin prompt and Finder."""
        self.assertEqual(list(pages()), ["mac-download", "mac-blocked", "mac-settings", "mac-confirm", "mac-intro", "mac-readme", "mac-licence", "mac-agree",
                                         "mac-dest", "mac-type", "mac-installing", "mac-summary", "mac-keep", "mac-finder"])

    def test_every_button_goes_to_an_existing_page_and_the_whole_flow_is_reachable(self) -> None:
        """Following the buttons from the download reaches Finder and every page; no data-go names a page that is not there."""
        edges = {name: set(re.findall(r'data-go="([^"]+)"', body)) for name, body in pages().items()}
        for name, targets in edges.items():
            self.assertLessEqual(targets, set(edges), f"{name} goes to a page that does not exist")
        seen, todo = set(), ["mac-download"]
        while todo:
            page = todo.pop()
            if page not in seen:
                seen.add(page)
                todo += sorted(edges[page])
        self.assertEqual(seen, set(edges))
        self.assertIn("open-start", pages()["mac-finder"])

    def test_the_forward_path_has_one_main_control_per_page_in_the_guide(self) -> None:
        """demo-guide.js names a control to circle for every macOS page (a page without one would throw when it is shown)."""
        guide = (demo_media.SOURCE / "demo-guide.js").read_text(encoding="utf-8")
        named = set(re.findall(r"'(mac-[a-z]+)':\s*'[^']+'", guide.split("var MAC_HINTS")[0]))
        self.assertEqual(named, set(pages()))

    def test_the_installing_page_waits_for_the_install_and_the_two_sheets_are_inert_behind(self) -> None:
        """Continue on the progress page is disabled until the install ends; behind the licence sheet nothing can be focused."""
        self.assertRegex(pages()["mac-installing"], r'<button[^>]*data-needs-install[^>]*>Continue</button>')
        self.assertRegex(pages()["mac-agree"], r'class="mi__behind" aria-hidden="true" inert')
        self.assertIn('role="progressbar"', pages()["mac-installing"])


class WordingTests(unittest.TestCase):
    """What the mock says: the real macOS wording, and only claims the project can back up."""

    def test_the_real_macos_wording_is_there(self) -> None:
        """The labels a colleague will look for appear exactly as macOS prints them."""
        html = mac_html()
        for phrase in ("Not Opened", "Apple could not verify", "Done", "Move to Bin", "Privacy &amp; Security", "Open Anyway", "Introduction", "Read Me", "Licence",
                       "Destination Select", "Installation Type", "Install for me only", "Install on a specific disk...", "requires about 1.3 GB of space",
                       "Standard Install on", "Install", "Installing", "completed successfully", "Close", "Keep", "Applications"):
            self.assertIn(phrase, html)

    def test_it_states_only_what_is_sourced(self) -> None:
        """Unsigned and Apple silicon are said (install guide; the package's own architecture and file name); nothing is said about Intel Macs (planning/DECISIONS.md 18)."""
        html = mac_html()
        self.assertIn("not code-signed", html)
        self.assertIn("Apple silicon", html)
        self.assertNotIn("Intel", html)
        self.assertNotIn("x86", html)
        self.assertNotIn("Applications/NucleiSky", html)

    def test_the_unconfirmed_old_shortcut_note_is_not_on_the_page(self) -> None:
        """The tester guide's claim that an old ~/Applications shortcut blocks the 0.1.7 installer is unconfirmed, so no part of it is shown."""
        html = mac_html().lower()
        for pattern in (r"\bolder\b", "old shortcut", "blocks creation", "reinstall", "upgrad"):
            self.assertNotRegex(html, pattern)

    def test_it_holds_no_personal_data_and_no_screenshot(self) -> None:
        """No user name or home path, and the only picture is the app icon the Windows walkthrough also uses."""
        html = demo_media.read_window("installer", "macos")
        self.assertNotRegex(html, r"/Users/|/home/|@[a-z]+\.[a-z]")
        self.assertEqual(set(re.findall(r'<img src="([^"]+)"', html)), {"assets/demo/nucleisky-icon.png"})
        self.assertNotRegex(html, r"<h[1-6][ >]")

    def test_the_placeholders_are_all_filled(self) -> None:
        """No {{placeholder}} is left once the stored record is applied."""
        self.assertNotIn("{{", mac_html())


class PageTests(unittest.TestCase):
    """The switch and the two installer panels in the page."""

    def test_the_switch_is_two_tabs_with_windows_selected_first(self) -> None:
        """Windows | macOS are real tab buttons, Windows selected and in the tab order, macOS reachable by arrow keys."""
        html = pages_demo.system_tabs()
        self.assertEqual(html.count('role="tab"'), 2)
        self.assertEqual(re.findall(r'data-os="(\w+)"', html), ["windows", "macos"])
        self.assertEqual(re.findall(r'aria-selected="(\w+)"', html), ["true", "false"])
        self.assertEqual(re.findall(r'tabindex="(-?\d)"', html), ["0", "-1"])

    def test_each_system_has_a_panel_and_only_windows_is_shown(self) -> None:
        """Both installers are in the page; the macOS panel is hidden until its tab is chosen; the other-systems line stays."""
        html = pages_demo.install_part({"windows": "<p>W</p>", "macos": "<p>M</p>"}, {"text": "On Linux.", "href": "guides/install/", "link": "Guide"})
        self.assertRegex(html, r'id="demo-os-windows"[^>]*data-os-panel="windows"><div')
        self.assertRegex(html, r'id="demo-os-macos"[^>]*data-os-panel="macos" hidden>')
        self.assertIn("On Linux.", html)

    def test_the_demo_loads_the_macos_style_and_scripts(self) -> None:
        """macos.css and the two new scripts are copied with the others, in an order where each file's dependencies come first."""
        self.assertIn("macos.css", demo_media.CODE)
        order = list(demo_media.SCRIPTS)
        self.assertLess(order.index("demo-os.js"), order.index("demo.js"))
        self.assertLess(order.index("demo-render-macos.js"), order.index("demo.js"))
        self.assertLess(order.index("demo-dom.js"), order.index("demo-os.js"))

    def test_the_tab_text_does_not_say_windows_only(self) -> None:
        """The first part is no longer a Windows-only walkthrough, in its button, its tile and the data file."""
        self.assertNotIn("(Windows)", pages_demo.PART_LABELS["install"])
        self.assertNotIn("(Windows)", pages_demo.home_tiles()[0])


if __name__ == "__main__":
    unittest.main()
