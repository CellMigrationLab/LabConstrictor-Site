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


def slugify(text: str) -> str:
    """ASCII, lowercase, dash-separated: "Iván Hidalgo" -> "ivan-hidalgo"."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def long_date(iso: str) -> str:
    """"2026-09-21" (or a longer ISO timestamp) -> "21 September 2026"."""
    y, m, d = (int(x) for x in str(iso)[:10].split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def megabytes(size: int) -> str:
    """A byte count as whole megabytes: 217506050 -> "207 MB"."""
    return f"{round(size / 2**20)} MB"


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
