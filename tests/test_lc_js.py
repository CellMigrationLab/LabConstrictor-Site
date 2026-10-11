"""The site script's system detection, run in node against the real docs/assets/javascripts/lc.js."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

LC_JS = Path(__file__).resolve().parents[1] / "docs" / "assets" / "javascripts" / "lc.js"
MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
CASES = [  # (user agent, platform, touch points, expected system)
    (MAC + " Chrome/120", "macOS", 0, "macos"), (MAC + " Safari/605", "MacIntel", 0, "macos"), (MAC + " Firefox/120", "MacIntel", 0, "macos"),
    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120", "Windows", 0, "windows"), ("Mozilla/5.0 (Windows NT 10.0; ARM64) Edge/120", "Windows", 10, "windows"),
    ("Mozilla/5.0 (X11; Linux x86_64) Firefox/120", "Linux x86_64", 0, "linux"), ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64) Chrome/120", "Linux", 0, "linux"),
    ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", "iPhone", 5, None), ("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)", "iPad", 5, None),
    (MAC + " Version/17 Safari/605", "MacIntel", 5, None),   # an iPad that reports a Mac
    ("Mozilla/5.0 (Linux; Android 14; Pixel 8) Chrome/120", "Linux armv8l", 5, None), ("Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) Chrome/120", "Linux", 0, None),
    ("Mozilla/5.0 (X11; FreeBSD amd64) Firefox/120", "FreeBSD amd64", 0, None), ("Mozilla/5.0", "", 0, None),
]
SCRIPT = """
const vm = require('vm'), fs = require('fs');
const ctx = { document: { addEventListener() {} }, navigator: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const cases = JSON.parse(process.argv[2]);
console.log(JSON.stringify(cases.map(([ua, p, t]) => vm.runInContext(`lcSystemFrom(${JSON.stringify(ua)}, ${JSON.stringify(p)}, ${t})`, ctx))));
"""


@unittest.skipUnless(shutil.which("node"), "node is not installed: the detection table is not run")
class SystemDetectionTests(unittest.TestCase):
    """Which system the page offers first, for browsers on computers, phones, tablets and unusual systems."""

    def test_every_case_gives_the_expected_system(self) -> None:
        """Computers give their system; phones, tablets (also an iPad posing as a Mac), Chromebooks and unknown systems give none."""
        run = subprocess.run(["node", "-e", SCRIPT, str(LC_JS), json.dumps(CASES)], capture_output=True, text=True, check=True)
        got = json.loads(run.stdout)
        self.assertEqual(got, [case[3] for case in CASES])


if __name__ == "__main__":
    unittest.main()
