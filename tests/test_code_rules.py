"""The coding rules of AGENTS.md, checked on every test run (and so on every build): a rule that is only written down is not enforced."""

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_FUNCTION_LINES, MAX_FILE_LINES = 30, 300
SOURCES = sorted(p for folder in ("scripts", "tests", "tools") for p in (ROOT / folder).rglob("*.py") if "__pycache__" not in p.parts)


def functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Every function and method in a parsed file, nested ones included."""
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def unannotated(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """The parameters of a function that have no annotation, plus "return" when it has none (self and cls need none)."""
    a = fn.args
    params = a.posonlyargs + a.args + a.kwonlyargs + [x for x in (a.vararg, a.kwarg) if x]
    missing = [p.arg for p in params if p.annotation is None and p.arg not in ("self", "cls")]
    return missing + (["return"] if fn.returns is None else [])


def problems(path: Path) -> list[str]:
    """Every way one file breaks the rules, as "file:line message" (empty when it follows them)."""
    text = path.read_text(encoding="utf-8")
    tree, found = ast.parse(text), []
    name = path.relative_to(ROOT)
    if len(text.splitlines()) > MAX_FILE_LINES:
        found.append(f"{name}: {len(text.splitlines())} lines; split it by responsibility (limit {MAX_FILE_LINES})")
    for fn in functions(tree):
        if not ast.get_docstring(fn):
            found.append(f"{name}:{fn.lineno} {fn.name} has no docstring")
        if unannotated(fn):
            found.append(f"{name}:{fn.lineno} {fn.name} is missing annotations for {unannotated(fn)}")
        if fn.end_lineno - fn.lineno + 1 > MAX_FUNCTION_LINES:
            found.append(f"{name}:{fn.lineno} {fn.name} is {fn.end_lineno - fn.lineno + 1} lines (limit {MAX_FUNCTION_LINES})")
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and (node.type is None or getattr(node.type, "id", "") in ("Exception", "BaseException")):
            found.append(f"{name}:{node.lineno} catches every exception; name the ones you expect")
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "get" and len(node.args) == 2:
            found.append(f"{name}:{node.lineno} .get(key, default) hides a missing value; check the key explicitly")
    return found


class CodeRuleTests(unittest.TestCase):
    """AGENTS.md "Code" and "No silent fallbacks", enforced on scripts/, tests/ and tools/."""

    def test_every_source_file_follows_the_rules(self) -> None:
        """Annotations, docstrings, function and file length, no catch-all except, no .get(key, default): none is broken anywhere."""
        found = [line for path in SOURCES for line in problems(path)]
        self.assertEqual(found, [], "\n" + "\n".join(found))

    def test_the_checker_catches_what_it_claims_to(self) -> None:
        """A file that breaks every rule is reported for each one (so a passing run means something)."""
        bad = ROOT / "tests" / "_rule_probe.py"
        body = "def f(a):\n    try:\n        return {}.get(a, 1)\n    except Exception:\n        pass\n" + "    x = 1\n" * 30
        bad.write_text(body, encoding="utf-8")
        try:
            report = "\n".join(problems(bad))
        finally:
            bad.unlink()
        for expected in ("no docstring", "missing annotations", "catches every exception", ".get(key, default)", "lines (limit"):
            self.assertIn(expected, report)


if __name__ == "__main__":
    unittest.main()
