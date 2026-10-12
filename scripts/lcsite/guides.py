"""The template's documentation (LabConstrictor/.tools/docs) turned into site guides.

The template repository stays the only place those pages are written. The build reads a
checkout of it (--template-dir) and of its doc_source branch (--doc-source-dir, where the
pictures live), so it needs no network. Anything that cannot be mapped stops the build.
"""

import posixpath
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

from .config import CONTENT, DATA, DOCS, FINAL_URL, REPO, SITE_URL, TEMPLATE_REPO, fail, load_yaml
from . import hosts, sources
from .page import Page
from .text import esc, lead_paragraph

SKIP = {"download_executable.md"}   # written per app (it carries one app's name); the generic install.md replaces it
LINK = re.compile(r"\]\(\s*(?!(?:[a-z][a-z0-9+.-]*:|#|/))(?:\./)?([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)(#[^)\s]*)?\s*\)")
IMAGE = re.compile(rf"https://github\.com/{TEMPLATE_REPO}/(?:blob|raw)/doc_source/([^\s)\"'?]+)(?:\?raw=true)?")
NAV_BLOCK = re.compile(r'<div align="center">(?:(?!</div>).)*?(?:Previous|Next|[Hh]ome)(?:(?!</div>).)*?</div>', re.S)
GUIDE_DEPTH = "../../"   # guides/<slug>/index.md -> the site root


def slug_of(filename: str) -> str:
    """"notebook_upload.md" -> "notebook-upload"."""
    return filename[:-3].replace("_", "-")


def parse_index(readme: str) -> list[dict]:
    """The sections of the template's docs README: [{"title", "items": [{"title", "file"}]}].
    A page listed twice appears once, under its first section; pages in SKIP are left out."""
    sections, seen = [], set(SKIP)
    for line in readme.splitlines():
        if line.startswith("## "):
            sections.append({"title": line[3:].strip(), "items": []})
        m = re.match(r"- \[([^\]]+)\]\(([A-Za-z0-9_-]+\.md)\)", line)
        if m and sections and m.group(2) not in seen:
            seen.add(m.group(2))
            sections[-1]["items"].append({"title": m.group(1), "file": m.group(2)})
    return [s for s in sections if s["items"]]


OWN_REPO_PATH = re.compile(r"\[`?([^\]`]+)`?\]\(\s*((?:\.\./)+[^)\s#]+)\s*\)")


def own_repo_paths(text: str) -> str:
    """A link whose text is the path it points to (`[.github/workflows/x.yml](../../.github/workflows/x.yml)`) names a file in the
    reader's own repository: on the website, where that file is not, it becomes plain code instead of a link to the template's copy."""
    def code(m: re.Match) -> str:
        """The path as code when the link text is the path; otherwise the link unchanged."""
        target = posixpath.normpath(posixpath.join(".tools/docs", m.group(2)))
        return f"`{target}`" if m.group(1) == target else m.group(0)
    return OWN_REPO_PATH.sub(code, text)


def localise(text: str) -> str:
    """Addresses of this site written with its final domain (in guides from other repositories) -> this site's own address,
    so the links work before the domain is live. When the two are the same this changes nothing."""
    return text.replace(FINAL_URL, SITE_URL)


def rewrite_links(text: str, known: set[str]) -> str:
    """Links to other docs pages -> site guide pages; every other relative link (a file of the template) -> that file on GitHub."""
    def link(m: re.Match) -> str:
        """The Markdown link rewritten for the site (guide page) or for GitHub (any other file)."""
        target = posixpath.normpath(posixpath.join(".tools/docs", m.group(1)))
        frag = m.group(2) if m.group(2) is not None else ""
        if posixpath.basename(m.group(1)) in known and posixpath.dirname(target) == ".tools/docs":
            return f"](../{slug_of(posixpath.basename(m.group(1)))}/index.md{frag})"
        return f"](https://github.com/{TEMPLATE_REPO}/blob/main/{target}{frag})"

    return LINK.sub(link, text)


def copy_images(text: str, doc_source: Path, page_file: str) -> str:
    """Pictures hosted on the doc_source branch -> copies under assets/docs-img/ (a missing picture stops the build)."""
    def image(m: re.Match) -> str:
        """The copied picture's path relative to the guide; stops the build for a picture outside doc_source."""
        name = unquote(m.group(1))
        src = (doc_source / name).resolve()
        if not src.is_relative_to(doc_source.resolve()):
            fail(f"{page_file} uses {name}, which is outside {doc_source}")
        if not src.is_file():
            fail(f"{page_file} uses {name}, which is not in {doc_source}")
        dest = DOCS / "assets" / "docs-img" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        return f"{GUIDE_DEPTH}assets/docs-img/{m.group(1)}"

    return IMAGE.sub(image, text)


SYSTEM_HEADINGS = {"windows": re.compile(r"\bwindows\b", re.I), "macos": re.compile(r"\bmac(?:os)?\b", re.I), "linux": re.compile(r"\blinux\b", re.I)}


def install_sections(template_dir: Path, doc_source: Path) -> dict[str, str]:
    """The template's install guide (install.md) cut into its per-system sections, as Markdown with the pictures copied, keyed windows,
    macos and linux: an app page shows the steps of the system whose installer was just downloaded, without writing them a second time.
    A section is found by its heading naming the system ("Windows", "Install on a Mac", ...). The picture paths are relative to a page two
    folders deep (guides/<slug>/ and apps/<slug>/ both are). Stops the build when a system has no section."""
    src = template_dir / ".tools" / "docs" / "install.md"
    if not src.is_file():
        fail(f"{src} not found: pass --template-dir with a checkout of {TEMPLATE_REPO}")
    text = localise(copy_images(rewrite_links(own_repo_paths(src.read_text(encoding="utf-8")), set()), doc_source, "install.md"))
    parts = re.split(r"^## +(.+?)\s*$", text, flags=re.M)
    found: dict[str, str] = {}
    for title, body in zip(parts[1::2], parts[2::2]):
        for system, pattern in SYSTEM_HEADINGS.items():
            if pattern.search(title) and system not in found:
                found[system] = body.strip()
    missing = [k for k in SYSTEM_HEADINGS if not found.get(k)]
    if missing:
        fail(f"{src}: no section for {', '.join(missing)} (a '## ' heading naming the system), so app pages cannot show its install steps")
    return found


def describe(markdown: str, where: str) -> str:
    """The meta description of a guide: its opening paragraph. Stops the build, naming the guide, when it has none."""
    try:
        return lead_paragraph(markdown, where)
    except ValueError as err:
        fail(str(err))


def pager(prev: dict | None, nxt: dict | None) -> str:
    """Previous / next links at the end of a guide (they replace the template's own footer)."""
    def side(item: dict | None, cls: str, label: str) -> str:
        """One link of the pager (an empty spacer at the ends)."""
        if not item:
            return "<span></span>"
        return f'<a class="{cls}" href="../{item["slug"]}/"><span>{label}</span><strong>{esc(item["title"])}</strong></a>'
    return f'<nav class="lc-pager" data-search-exclude aria-label="Previous and next guide">{side(prev, "lc-pager__prev", "&larr; Previous")}{side(nxt, "lc-pager__next", "Next &rarr;")}</nav>'


HOSTS_BY_SLUG = hosts.load()   # a guide named after a host (napari, fiji, qupath) shows that program's logo
TRACKS = {"use": "Use an app", "build": "Build an app"}   # the two audiences; every guide section belongs to one


def nav_for(sections: list[dict]) -> list[dict]:
    """The sidebar: every section with its track and its items as title, path and id."""
    return [{"title": s["title"], "track": s["track"], "track_title": TRACKS[s["track"]],
             "items": [{"title": g["title"], "path": f"guides/{g['slug']}/", "id": g["slug"], "host": g["slug"] if g["slug"] in HOSTS_BY_SLUG else None}
                       for g in s["items"]]}
            for s in sections]


def guide_meta(nav: list[dict], slug: str) -> dict:
    """Front matter that gives a guide its sidebar: the sections, which page this is, and which track it is in."""
    track = next(s["track"] for s in nav if any(g["id"] == slug for g in s["items"]))
    return {"guide_nav": nav, "guide_id": slug, "guide_track": track, "guide_track_title": TRACKS[track], "menu": "guides/"}


def write_own(item: dict, nav: list[dict], tail: str) -> None:
    """guides/<slug>/index.md from content/guides/<file> (hand-written Markdown with its own H1)."""
    src = CONTENT / "guides" / item["file"]
    if not src.is_file():
        fail(f"data/guides.yaml lists {item['file']}, which is not in content/guides/")
    text = localise(src.read_text(encoding="utf-8").strip())
    p = Page(f"guides/{item['slug']}/index.md", **guide_meta(nav, item["slug"]), description=describe(text, item["file"]),
             edit_url=f"{REPO}/edit/main/content/guides/{item['file']}")
    p.add(text, "", tail)
    p.write()


def guide_lists(nav: list[dict], track: str) -> str:
    """The sections of one track with a link to each guide (HTML for a hub page)."""
    return "".join(
        f'<h3>{esc(s["title"])}</h3><ul>' + "".join(f'<li><a href="{i["path"]}">{hosts.logo(i["host"]) if i["host"] else ""}{esc(i["title"])}</a></li>' for i in s["items"]) + "</ul>"
        for s in nav if s["track"] == track)


def write_source_guide(g: dict, nav: list[dict], tail: str, pages: dict[tuple[str, str], str]) -> None:
    """guides/<slug>/index.md from a guide kept in another repository (fetched by scripts/fetch_guides.py)."""
    where = f"{g['repo']}/{g['path']}"
    text = sources.read(g["repo"], g["path"])
    sources.check_links(text, where)
    text = localise(sources.admonitions(sources.site_links(text, pages)))
    p = Page(f"guides/{g['slug']}/index.md", **guide_meta(nav, g["slug"]), description=describe(text, where),
             edit_url=f"https://github.com/{g['repo']}/edit/main/{g['path']}")
    p.add(text.strip(), "", tail)
    p.write()


def write_template_guide(g: dict, docs_dir: Path, doc_source: Path, nav: list[dict], known: set[str], tail: str) -> None:
    """guides/<slug>/index.md from one page of the template's .tools/docs."""
    src = docs_dir / g["file"]
    if not src.is_file():
        fail(f"README of the template lists {g['file']}, which does not exist")
    text = NAV_BLOCK.sub("", src.read_text(encoding="utf-8"))
    text = localise(copy_images(rewrite_links(own_repo_paths(text), known), doc_source, g["file"]))
    edit = f"https://github.com/{TEMPLATE_REPO}/edit/main/.tools/docs/{g['file']}"
    p = Page(f"guides/{g['slug']}/index.md", **guide_meta(nav, g["slug"]), description=describe(text, g["file"]), edit_url=edit)
    p.add(text.strip(), "", tail)
    p.write()


def write_guide(g: dict, nav: list[dict], tail: str, template: tuple, pages: dict[tuple[str, str], str]) -> None:
    """Write one guide from wherever it lives: the template, another repository or this repository."""
    if g["from_template"]:
        write_template_guide(g, template[0], template[1], nav, template[2], tail)
    elif "repo" in g:
        write_source_guide(g, nav, tail, pages)
    else:
        write_own(g, nav, tail)


def warn_unlisted(docs_dir: Path, theirs: list[dict], own: list[dict]) -> None:
    """Print a WARNING for each page in the template's docs that its README does not list (so it is not on the site)."""
    listed = {g["file"] for s in theirs + own for g in s["items"] if "file" in g} | SKIP | {"README.md"}
    for name in sorted(p.name for p in docs_dir.glob("*.md") if p.name not in listed):
        print(f"WARNING: {docs_dir.name}/{name} is not listed in the README of the template's docs, so it is not on the site", file=sys.stderr)


def heading_title(text: str, where: str) -> str:
    """The title of a template page as its sidebar and pager show it: its first heading, without a leading emoji.
    The page and its menu entry can then never say different things. Stops the build when there is no heading."""
    return re.sub(r"^[^\w(]+", "", sources.title_of(text, where))


def title_template_pages(sections: list[dict], docs_dir: Path) -> None:
    """Give every page that comes from the template the title of its own first heading (the README's link text only orders and groups)."""
    for s in sections:
        for g in (g for g in s["items"] if g["from_template"]):
            g["title"] = heading_title((docs_dir / g["file"]).read_text(encoding="utf-8"), g["file"])


def claim_template_pages(own: list[dict], theirs: list[dict]) -> None:
    """Move into our own sections the template pages they name (`template: file.md`), taking the title from the template.
    A page the template no longer has stops the build: the placement never drifts silently."""
    by_file = {g["file"]: g for s in theirs for g in s["items"]}
    for item in (g for s in own for g in s["items"] if "template" in g):
        page = by_file.get(item["template"])
        if page is None:
            fail(f"data/guides.yaml places {item['template']}, which is not in the README of the template's docs")
        item.update(file=page["file"], title=page["title"], slug=page["slug"])
        for s in theirs:
            s["items"] = [g for g in s["items"] if g is not page]


def read_sections(docs_dir: Path) -> tuple[list[dict], list[dict]]:
    """Our own sections (data/guides.yaml, track "use") and the template's (its docs README, track "build"), each guide
    with its slug and where it comes from. Guides kept in other repositories are titled by their first heading."""
    own = load_yaml(DATA / "guides.yaml")["sections"]
    theirs = parse_index((docs_dir / "README.md").read_text(encoding="utf-8"))
    for s in theirs:
        s["track"] = "build"
        for g in s["items"]:
            g.update(slug=slug_of(g["file"]), from_template=True)
    for s in own:
        s["track"] = "use"
        s["items"] = [dict(g, from_template="template" in g) for g in s["items"]]
        for g in (g for g in s["items"] if "repo" in g):
            g["title"] = sources.title_of(sources.read(g["repo"], g["path"]), f"{g['repo']}/{g['path']}")
    return own, theirs


def build(template_dir: Path, doc_source: Path) -> list[dict]:
    """Write guides/: our own sections (data/guides.yaml, track "use"), then the template's .tools/docs as track "build".
    Returns the sidebar sections (title, track, items) for the hub pages."""
    docs_dir = template_dir / ".tools" / "docs"
    if not docs_dir.is_dir():
        fail(f"{docs_dir} not found: pass --template-dir with a checkout of {TEMPLATE_REPO}")
    own, theirs = read_sections(docs_dir)
    pages = {(g["repo"], g["path"]): g["slug"] for s in own for g in s["items"] if "repo" in g}
    known = {g["file"] for s in theirs for g in s["items"]}
    claim_template_pages(own, theirs)
    clash = {g["slug"] for s in own for g in s["items"] if not g["from_template"]} & {g["slug"] for s in theirs for g in s["items"]}
    if clash:
        fail(f"guide address used twice (data/guides.yaml and the template): {sorted(clash)}")
    sections = own + [s for s in theirs if s["items"]]
    title_template_pages(sections, docs_dir)
    warn_unlisted(docs_dir, theirs, own)
    nav = nav_for(sections)
    for track in TRACKS:
        flat = [g for s in sections if s["track"] == track for g in s["items"]]
        for i, g in enumerate(flat):
            tail = pager(flat[i - 1] if i else None, flat[i + 1] if i + 1 < len(flat) else None)
            write_guide(g, nav, tail, (docs_dir, doc_source, known), pages)
    return nav
