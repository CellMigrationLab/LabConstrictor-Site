"""The template's documentation (LabConstrictor/.tools/docs) turned into site guides.

The template repository stays the only place those pages are written. The build reads a
checkout of it (--template-dir) and of its doc_source branch (--doc-source-dir, where the
pictures live), so it needs no network. Anything that cannot be mapped stops the build.
"""

import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import unquote

from .config import CONTENT, DATA, DOCS, REPO, TEMPLATE_REPO, fail, load_yaml
from .page import Page
from .text import esc

SKIP = {"download_executable.md"}   # replaced by guides/install/, generated from data/install.yaml
LINK = re.compile(r"\]\(\s*(?!(?:[a-z][a-z0-9+.-]*:|#|/))(?:\./)?([A-Za-z0-9_./-]+\.[A-Za-z0-9]+)(#[^)\s]*)?\s*\)")
IMAGE = re.compile(rf"https://github\.com/{TEMPLATE_REPO}/(?:blob|raw)/doc_source/([^\s)\"'?]+)(?:\?raw=true)?")
NAV_BLOCK = re.compile(r'<div align="center">(?:(?!</div>).)*?(?:Previous|Next|Home)(?:(?!</div>).)*?</div>', re.S)
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


def pager(prev: dict | None, nxt: dict | None) -> str:
    """Previous / next links at the end of a guide (they replace the template's own footer)."""
    def side(item: dict | None, cls: str, label: str) -> str:
        """One link of the pager (an empty spacer at the ends)."""
        if not item:
            return "<span></span>"
        return f'<a class="{cls}" href="../{item["slug"]}/"><span>{label}</span><strong>{esc(item["title"])}</strong></a>'
    return f'<nav class="lc-pager">{side(prev, "lc-pager__prev", "&larr; Previous")}{side(nxt, "lc-pager__next", "Next &rarr;")}</nav>'


TRACKS = {"use": "Use an app", "build": "Build an app"}   # the two audiences; every guide section belongs to one


def nav_for(sections: list[dict]) -> list[dict]:
    """The sidebar: every section with its track and its items as title, path and id."""
    return [{"title": s["title"], "track": s["track"], "track_title": TRACKS[s["track"]],
             "items": [{"title": g["title"], "path": f"guides/{g['slug']}/", "id": g["slug"]} for g in s["items"]]}
            for s in sections]


def write_install(site_systems: list[dict], note: str, nav: list[dict], tail: str) -> None:
    """guides/install/index.md: how to install an app on each system (data/install.yaml)."""
    body = ["# Install an app", "", note, ""]
    for s in site_systems:
        body += [f"## {s['title']}", ""] + [f"{i}. {step}" for i, step in enumerate(s["steps"], 1)] + [""]
    body += ["Something went wrong? Open an issue in the app's repository, linked from its page in the [App Centre](../../apps/index.md).", ""]
    p = Page("guides/install/index.md", title="Install an app", guide_nav=nav, guide_id="install")
    p.add("\n".join(body), "", tail)
    p.write()


def write_own(item: dict, nav: list[dict], tail: str) -> None:
    """guides/<slug>/index.md from content/guides/<file> (hand-written Markdown with its own H1)."""
    src = CONTENT / "guides" / item["file"]
    if not src.is_file():
        fail(f"data/guides.yaml lists {item['file']}, which is not in content/guides/")
    p = Page(f"guides/{item['slug']}/index.md", guide_nav=nav, guide_id=item["slug"],
             edit_url=f"{REPO}/edit/main/content/guides/{item['file']}")
    p.add(src.read_text(encoding="utf-8").strip(), "", tail)
    p.write()


def track_block(track: str, nav: list[dict], intro: str) -> str:
    """One audience on the guides page: its heading, an introduction (HTML) and its sections with their guides."""
    lists = "".join(
        f'<h3>{esc(s["title"])}</h3><ul>' + "".join(f'<li><a href="{i["path"]}">{esc(i["title"])}</a></li>' for i in s["items"]) + "</ul>"
        for s in nav if s["track"] == track)
    return f'<section class="lc-guides__track" id="{track}"><h2>{esc(TRACKS[track])}</h2>{intro}{lists}</section>'


def benefits(items: list[dict]) -> str:
    """"Why build an app": each benefit with a link to the guide that shows it from the user's side."""
    rows = "".join(f'<li><strong>{esc(b["title"])}</strong> {esc(b["text"])} <a href="{esc(b["href"])}">{esc(b["link"])}</a></li>' for b in items)
    return f'<p>Why turn a notebook into an app?</p><ul class="lc-benefits">{rows}</ul><p>How to build one:</p>'


def write_landing(nav: list[dict], why_build: list[dict]) -> None:
    """guides/index.md: the guides in two tracks, using an app and building one (which starts with the reasons to build)."""
    p = Page("guides/index.md", title="Guides", description="How to install and use LabConstrictor apps, use them in napari, Fiji and QuPath, and build your own.", layout="wide")
    p.add('<section class="lc-pagehead"><h1>Guides</h1><p class="lc-lead">Use an app someone built, or build your own. <a href="#use">Use an app</a> · <a href="#build">Build an app</a></p></section>',
          '<div class="lc-guides">' + track_block("use", nav, "") + track_block("build", nav, benefits(why_build)) + "</div>")
    p.write()


def write_template_guide(g: dict, docs_dir: Path, doc_source: Path, nav: list[dict], known: set[str], tail: str) -> None:
    """guides/<slug>/index.md from one page of the template's .tools/docs."""
    src = docs_dir / g["file"]
    if not src.is_file():
        fail(f"README of the template lists {g['file']}, which does not exist")
    text = NAV_BLOCK.sub("", src.read_text(encoding="utf-8"))
    text = copy_images(rewrite_links(text, known), doc_source, g["file"])
    edit = f"https://github.com/{TEMPLATE_REPO}/edit/main/.tools/docs/{g['file']}"
    p = Page(f"guides/{g['slug']}/index.md", guide_nav=nav, guide_id=g["slug"], edit_url=edit)
    p.add(text.strip(), "", tail)
    p.write()


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


def build(template_dir: Path, doc_source: Path, systems: list[dict], note: str, why_build: list[dict]) -> None:
    """Write guides/: our own sections (data/guides.yaml, track "use"), then the template's .tools/docs as track "build"."""
    docs_dir = template_dir / ".tools" / "docs"
    if not docs_dir.is_dir():
        fail(f"{docs_dir} not found: pass --template-dir with a checkout of {TEMPLATE_REPO}")
    own = load_yaml(DATA / "guides.yaml")["sections"]
    theirs = parse_index((docs_dir / "README.md").read_text(encoding="utf-8"))
    for s in theirs:
        s["track"] = "build"
        for g in s["items"]:
            g.update(slug=slug_of(g["file"]), from_template=True)
    for s in own:
        s["track"] = "use"
        s["items"] = [dict(g, from_template="template" in g) for g in s["items"]]
    known = {g["file"] for s in theirs for g in s["items"]}
    claim_template_pages(own, theirs)
    clash = {g["slug"] for s in own for g in s["items"] if not g["from_template"]} & {g["slug"] for s in theirs for g in s["items"]}
    if clash:
        fail(f"guide address used twice (data/guides.yaml and the template): {sorted(clash)}")
    sections = own + [s for s in theirs if s["items"]]
    nav = nav_for(sections)
    flat = [g for s in sections for g in s["items"]]
    for i, g in enumerate(flat):
        tail = pager(flat[i - 1] if i else None, flat[i + 1] if i + 1 < len(flat) else None)
        if g.get("generated"):
            write_install(systems, note, nav, tail)
        elif g["from_template"]:
            write_template_guide(g, docs_dir, doc_source, nav, known, tail)
        else:
            write_own(g, nav, tail)
    write_landing(nav, why_build)
