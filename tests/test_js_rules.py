"""AGENTS.md's code rules for the demo's JavaScript (content/demo/*.js): documented, contained, no silent fallbacks."""

import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted(p for folder in ("demo", "how") for p in (ROOT / "content" / folder).glob("*.js"))
MAX_FUNCTION_LINES, MAX_FILE_LINES = 30, 300
STRING = re.compile(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"")
COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)
NAMED = re.compile(r"^[ \t]*function (\w+)\(([^)]*)\)\s*\{", re.M)
ANY_FUNCTION = re.compile(r"function\s*(\w*)\s*\(([^)]*)\)\s*\{")
TYPE = r"\{(?:[^{}]|\{[^{}]*\})+\}"   # {type}, also {{a: string}}
SILENT = re.compile(r"\bcatch\b|\|\|\s*(0|''|\"\"|\[\]|\{\}|null|false)\b")


def blank(match: re.Match) -> str:
    """The same text with everything but line breaks replaced by spaces, so line numbers and braces stay meaningful."""
    return re.sub(r"[^\n]", " ", match.group(0))


def clean(text: str) -> str:
    """The source with comments and string contents blanked, ready for brace counting and pattern search."""
    return STRING.sub(lambda m: m.group(0)[0] + blank(m)[1:-1] + m.group(0)[-1], COMMENT.sub(blank, text))


def body_end(cleaned: str, open_brace: int) -> int:
    """The index just after the brace that closes the one at `open_brace`; raises ValueError when it never closes."""
    depth = 0
    for i in range(open_brace, len(cleaned)):
        depth += 1 if cleaned[i] == "{" else -1 if cleaned[i] == "}" else 0
        if depth == 0:
            return i + 1
    raise ValueError("unbalanced braces")


def doc_before(text: str, start: int) -> str:
    """The /** ... */ block that ends right before the function starting at `start` ('' when there is none)."""
    before = text[:start].rstrip()
    if not before.endswith("*/"):
        return ""
    return before[before.rindex("/**"):] if "/**" in before else ""


def problems(path: Path) -> list[str]:
    """Every way one JavaScript file breaks the rules, as "file:line message"."""
    text = path.read_text(encoding="utf-8")
    cleaned, name, found = clean(text), path.name, []
    if len(text.splitlines()) > MAX_FILE_LINES:
        found.append(f"{name}: {len(text.splitlines())} lines (limit {MAX_FILE_LINES})")
    for m in list(ANY_FUNCTION.finditer(cleaned))[1:]:   # the first function is the file's wrapper
        end = body_end(cleaned, m.end() - 1)
        lines = cleaned.count("\n", m.start(), end) + 1
        line = cleaned.count("\n", 0, m.start()) + 1
        if lines > MAX_FUNCTION_LINES:
            found.append(f"{name}:{line} function {m.group(1) or '(anonymous)'} is {lines} lines (limit {MAX_FUNCTION_LINES})")
    for m in NAMED.finditer(cleaned):
        found += named_problems(name, text, cleaned, m)
    for m in SILENT.finditer(cleaned):
        found.append(f"{name}:{cleaned.count(chr(10), 0, m.start()) + 1} '{m.group(0)}' hides a missing value or an error; check explicitly")
    return found


def named_problems(name: str, text: str, cleaned: str, m: re.Match) -> list[str]:
    """What a named function's comment must say: every parameter with a {type}, and @returns when the function returns a value."""
    line = cleaned.count("\n", 0, m.start()) + 1
    doc = doc_before(text, m.start())
    found = []
    if not doc:
        return [f"{name}:{line} function {m.group(1)} has no /** */ comment"]
    for param in [p.strip() for p in m.group(2).split(",") if p.strip()]:
        if not re.search(r"@param\s+" + TYPE + r"\s+" + re.escape(param) + r"\b", doc):
            found.append(f"{name}:{line} {m.group(1)}: the comment lacks '@param {{type}} {param}'")
    body = cleaned[m.end():body_end(cleaned, m.end() - 1)]
    if "@returns" not in doc:
        found.append(f"{name}:{line} {m.group(1)}: the comment lacks @returns")
    elif re.search(r"\breturn\s+[^;\s]", body) is None and "@returns {void}" not in doc:
        found.append(f"{name}:{line} {m.group(1)}: @returns names a value but the function returns none")
    return found


class JsRuleTests(unittest.TestCase):
    """The demo's scripts follow the same rules as the Python code."""

    def test_the_demo_scripts_follow_the_rules(self) -> None:
        """Comments with types, at most 30 lines per function, 300 per file, no catch and no `|| default`."""
        found = [line for path in FILES for line in problems(path)]
        self.assertEqual(found, [], "\n" + "\n".join(found))

    def test_the_checker_catches_what_it_claims_to(self) -> None:
        """A script that breaks the rules is reported for each one."""
        bad = ROOT / "tests" / "_probe.js"
        bad.write_text("function f(a) {\n  try { return a || 0; } catch (e) { }\n}\n" + "function g() {\n" + "  x();\n" * 31 + "}\n", encoding="utf-8")
        try:
            found = "\n".join(problems(bad))
        finally:
            bad.unlink()
        for expected in ("no /** */ comment", "hides a missing value", "g is 33 lines"):
            self.assertIn(expected, found)

    @unittest.skipUnless(shutil.which("node"), "node is not installed: the syntax check of the demo scripts is skipped")
    def test_the_demo_scripts_are_valid_javascript(self) -> None:
        """`node --check` accepts every demo script."""
        for path in FILES:
            run = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True, check=False)
            self.assertEqual(run.returncode, 0, f"{path.name}: {run.stderr}")


if __name__ == "__main__":
    unittest.main()
