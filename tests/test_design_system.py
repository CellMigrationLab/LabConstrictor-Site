"""The site's own CSS uses the type scale and nothing else: every font-size is a --fs-* token (the simulated program windows of the demo keep the look of the programs they imitate)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "docs" / "assets" / "stylesheets" / "lc.css", ROOT / "content" / "how" / "how.css"]
ALLOWED = ("var(--fs-", "0", "calc(var(--size)")   # 0 hides the search button's text; the monogram scales with its box
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
TOKENS = {"xs", "sm", "ui", "body", "lead", "h3", "h2", "h1", "hero", "numeral"}


class TypeScaleTests(unittest.TestCase):
    """What the stylesheets may say about font sizes."""

    def test_every_font_size_is_a_token(self) -> None:
        """No rem, px or em size in lc.css or how.css: only var(--fs-<token>)."""
        found = []
        for path in FILES:
            for sel, body in RULE.findall(re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)):
                for value in re.findall(r"(?<![\w-])font-size:\s*([^;}]+)", body):
                    if not value.strip().startswith(ALLOWED):
                        found.append(f"{path.name}: {sel.strip().splitlines()[-1][:60]} {{ font-size: {value.strip()} }}")
        self.assertEqual(found, [], "use a --fs-* token: " + "; ".join(found))

    def test_the_tokens_used_are_defined(self) -> None:
        """Every var(--fs-x) names a token that :root defines."""
        text = FILES[0].read_text(encoding="utf-8")
        defined = set(re.findall(r"--fs-(\w+):", text))
        used = set(re.findall(r"var\(--fs-(\w+)\)", "".join(p.read_text(encoding="utf-8") for p in FILES)))
        self.assertEqual(used - defined, set())
        self.assertEqual(defined, TOKENS)


if __name__ == "__main__":
    unittest.main()
