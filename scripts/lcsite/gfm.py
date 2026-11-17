"""Lists written for GitHub, rendered the same way on this site.

The guides are written in other repositories and read on GitHub first. GitHub's Markdown and the site's (Python-Markdown)
read two common habits differently, and the difference broke lists on the site:

1. A list right after a sentence, with no blank line between them. GitHub starts the list; Python-Markdown keeps the lines
   in the paragraph, markers and all.
2. The text of a list item indented to where the item's text starts (3 spaces after "1. ", 2 after "- "). GitHub reads it as
   part of the item; Python-Markdown wants 4 spaces, so a paragraph, code block or sub-list under the item fell out of the list
   and the numbering after it broke.

Inside a list item GitHub also lets a quote, a code block or the next item follow text directly; Python-Markdown needs a blank
line there, so one is added.

`lists` rewrites these habits into what Python-Markdown expects, so a page looks the same on GitHub and on the site. Nothing
else changes; code blocks are never touched inside (only moved right as a whole when they belong to a list item).
"""

import re
from dataclasses import dataclass

ITEM = re.compile(r"^( *)([-*+]|(\d{1,9})[.)])( +)(?=\S)")
FENCE = re.compile(r"^( *)(`{3,}|~{3,})")
QUOTE = re.compile(r"^ *>")
PY_MARKDOWN_INDENT = 4   # Python-Markdown: the content of a list item is indented 4 spaces past its marker's column


@dataclass
class Level:
    """One open list item: the column its text starts at in the source (GitHub), the column Python-Markdown needs, and whether
    a blank line came inside it (then its last paragraph swallows a next item that follows it with no blank line)."""
    source: int
    site: int
    loose: bool = False


@dataclass
class Fence:
    """An open code block: its fence, the fence's indent in the source, and how far the whole block moves right."""
    marker: str
    at: int
    shift: int


def _indent(line: str) -> int:
    """The number of spaces a line starts with."""
    return len(line) - len(line.lstrip(" "))


def _moved(line: str, new_indent: int) -> str:
    """The line with its leading spaces replaced by `new_indent` spaces."""
    return " " * new_indent + line.lstrip(" ")


class _Rewriter:
    """Walks the lines once, keeping the open list items (a stack) and the open code block."""

    def __init__(self) -> None:
        """Start outside any list or code block."""
        self.out: list[str] = []
        self.stack: list[Level] = []
        self.fence: Fence | None = None
        self.previous_blank = True

    def blank_line(self, loosen: bool = True) -> None:
        """Write an empty line; every open item now has a blank line inside."""
        self.out.append("")
        if loosen:
            for level in self.stack:
                level.loose = True

    def code_line(self, line: str) -> None:
        """A line inside a code block: moved with the block, never changed otherwise; the closing fence ends the block."""
        fence = self.fence
        assert fence is not None
        closing = FENCE.match(line)
        if closing and closing.group(2)[0] == fence.marker[0] and len(closing.group(2)) >= len(fence.marker) and not line.strip(" `~"):
            self.fence = None
        moves = fence.shift and _indent(line) >= fence.at and line.strip()
        self.out.append(" " * fence.shift + line if moves else line)

    def item_line(self, line: str, item: re.Match) -> None:
        """A list item: closes the deeper items, adds the blank line Python-Markdown needs before it, moves it under its parent."""
        indent, closed = _indent(line), []
        while self.stack and indent < self.stack[-1].source:
            closed.append(self.stack.pop())
        starts_list = not self.stack and not closed and not self.previous_blank and self.out and item.group(3) in (None, "1")
        after_paragraph = not self.previous_blank and any(level.loose for level in closed) and not ITEM.match(self.out[-1])
        if starts_list or after_paragraph:
            self.blank_line(loosen=False)   # GitHub starts a list (or the next item) here; Python-Markdown needs a blank line first
        top = self.stack[-1] if self.stack else None
        new_indent = top.site + (indent - top.source) if top else indent
        self.out.append(_moved(line, new_indent))
        self.stack.append(Level(source=indent + len(item.group(2)) + len(item.group(4)), site=new_indent + PY_MARKDOWN_INDENT))

    def text_line(self, line: str) -> None:
        """Any other line: inside an item it moves to 4 spaces past the item's marker; a quote or code block gets a blank line first."""
        indent, opening = _indent(line), FENCE.match(line)
        if self.stack and self.previous_blank:
            while self.stack and indent < self.stack[-1].source:
                self.stack.pop()
        new_indent = indent   # outside a list, or a line GitHub joins to the item's paragraph (it needs no indent)
        if self.stack and indent >= self.stack[-1].source:
            new_indent = self.stack[-1].site + (indent - self.stack[-1].source)
            if not self.previous_blank and (opening or QUOTE.match(line)):
                self.blank_line()
        if opening:
            self.fence = Fence(opening.group(2), indent, new_indent - indent)
        self.out.append(_moved(line, new_indent))

    def add(self, line: str) -> None:
        """Rewrite one source line."""
        if self.fence:
            self.code_line(line)
            return
        if not line.strip():
            self.out.append(line)
            for level in self.stack:
                level.loose = True
            self.previous_blank = True
            return
        item = ITEM.match(line)
        self.item_line(line, item) if item else self.text_line(line)
        self.previous_blank = False


def lists(text: str) -> str:
    """The text with lists written for GitHub turned into lists Python-Markdown reads the same way (see the module notes)."""
    rewriter = _Rewriter()
    for line in text.split("\n"):
        rewriter.add(line)
    return "\n".join(rewriter.out)
