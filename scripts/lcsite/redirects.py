"""Old addresses that still work: a small page at the old address sends the visitor to the new one.

data/redirects.yaml maps each old address to its new one (both relative to the site root, ending in a slash). Add a line
when a page is renamed or moved, and anything that links to the old address keeps working. The build stops when the old
address is already a real page or the new one does not exist.
"""

from pathlib import Path

from .config import DATA, DOCS, fail, load_yaml
from .page import Page

REDIRECTS = DATA / "redirects.yaml"


def exists(address: str, docs: Path = DOCS) -> bool:
    """True when `address` ("guides/install/", "ecosystem/") is a generated page under docs/."""
    base = address.strip("/")
    return (docs / base / "index.md").is_file() or (docs / f"{base}.md").is_file()


def check(old: str, new: str, docs: Path = DOCS) -> list[str]:
    """Why a redirect from `old` to `new` is not allowed (empty when it is)."""
    found = []
    for label, address in (("old", old), ("new", new)):
        if address.startswith("/") or not address.endswith("/"):
            found.append(f"the {label} address {address!r} must be relative to the site root and end with a slash")
        if any(part in ("", ".", "..") for part in address.strip("/").split("/")):
            found.append(f"the {label} address {address!r} must not contain empty, . or .. parts")
    if exists(old, docs):
        found.append(f"{old} is a real page, so it cannot also be a redirect")
    if not exists(new, docs):
        found.append(f"{new} does not exist")
    return found


def write_all(redirects: dict[str, str], docs: Path = DOCS) -> None:
    """Write one redirect page per entry. Stops the build, naming the entry, when one is not allowed."""
    for old, new in redirects.items():
        problems = check(old, new, docs)
        if problems:
            fail(f"{REDIRECTS.name}: {old} -> {new}: " + "; ".join(problems))
        Page(f"{old}index.md", title="Moved", template="redirect.html", redirect_to=new).write()


def clean(docs: Path = DOCS) -> None:
    """Delete the redirect pages of the previous build (they sit at arbitrary addresses, so they are found by their template)."""
    for page in docs.rglob("index.md"):
        if "template: redirect.html" in page.read_text(encoding="utf-8")[:400]:
            page.unlink()


def load() -> dict[str, str]:
    """The redirects of data/redirects.yaml."""
    data = load_yaml(REDIRECTS)
    if not isinstance(data.get("redirects"), dict):
        fail(f"{REDIRECTS} needs a `redirects:` mapping (use `redirects: {{}}` for none)")
    return data["redirects"]
