"""Small string helpers used everywhere."""

import html
import re
import unicodedata
from urllib.parse import urlsplit

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")


def esc(value: object) -> str:
    """HTML-escape a value (None becomes an empty string)."""
    return html.escape(str(value if value is not None else ""), quote=True)


def paragraphs(text: str) -> str:
    """Plain text with blank-line separated paragraphs -> escaped <p> elements."""
    return "".join(f"<p>{esc(p.strip())}</p>" for p in text.split("\n\n") if p.strip())


def one_line(text: str) -> str:
    """Text on a single line with no link or tag characters: whitespace runs become one space and [ ] ( ) < > are removed.
    For untrusted text placed in plain-text or Markdown-like files (llms.txt, comments)."""
    return re.sub(r"[\[\]()<>]", "", " ".join(str(text).split()))


BLOCK_START = re.compile(r"^(#|!|>|\||-|\*|\d+[.)]|<|```|\s{4})")


def lead_paragraph(markdown: str, where: str, limit: int = 160) -> str:
    """The first plain paragraph of a Markdown page, as one line of at most `limit` characters (cut at a word, with an
    ellipsis): the page's meta description. Raises ValueError, naming `where`, when the page has no such paragraph."""
    for block in re.split(r"\n\s*\n", markdown):
        lines = block.strip().splitlines()
        if lines and not BLOCK_START.match(lines[0]):
            plain = re.sub(r"[*_`]", "", re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", " ".join(lines)))
            plain = " ".join(plain.split())
            return plain if len(plain) <= limit else plain[:limit].rsplit(" ", 1)[0].rstrip(",;:.") + "\u2026"
    raise ValueError(f"{where} has no opening paragraph to use as its description")


def slugify(text: str) -> str:
    """ASCII, lowercase, dash-separated: "Iván Hidalgo" -> "ivan-hidalgo"."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def long_date(iso: str) -> str:
    """"2026-09-21" (or a longer ISO timestamp) -> "21 September 2026"."""
    y, m, d = (int(x) for x in str(iso)[:10].split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def megabytes(size: int) -> str:
    """A byte count in megabytes (10**6 bytes, as GitHub and file managers show them): 317528492 -> "317.5 MB"."""
    return f"{size / 10**6:.1f} MB"


def plural(n: int, word: str) -> str:
    """plural(1, "app") -> "1 app"; plural(2, "app") -> "2 apps"."""
    return f"{n} {word}{'' if n == 1 else 's'}"


def is_external(url: str) -> bool:
    """True for absolute URLs, mailto:, fragments and protocol-relative links."""
    return bool(re.match(r"^([a-z][a-z0-9+.-]*:|#|//)", str(url), flags=re.I))


def opens_new_tab(url: str, site_url: str) -> bool:
    """Web links that leave the site open in a new tab; site pages, fragments
    and other schemes do not. Compared by host name, not by text prefix."""
    link, site = urlsplit(str(url)), urlsplit(site_url)
    return link.scheme.lower() in ("http", "https") and link.hostname != site.hostname
