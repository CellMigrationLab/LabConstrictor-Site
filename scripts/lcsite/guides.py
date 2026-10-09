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

from .config import DOCS, TEMPLATE_REPO, fail
from .page import Page
from .text import esc

SKIP = {"download_executable.md"}   # replaced by guides/install/, generated from data/install.yaml
LINK = re.compile(r"\]\(\s*(?:\./)?([A-Za-z0-9_./-]+\.md)(#[^)\s]*)?\s*\)")
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
    """Links to other docs pages -> site guide pages; other relative .md links -> the file on GitHub."""
    def link(m: re.Match) -> str:
        target = posixpath.normpath(posixpath.join(".tools/docs", m.group(1)))
        frag = m.group(2) or ""
        if posixpath.basename(m.group(1)) in known and posixpath.dirname(target) == ".tools/docs":
            return f"](../{slug_of(posixpath.basename(m.group(1)))}/index.md{frag})"
        return f"](https://github.com/{TEMPLATE_REPO}/blob/main/{target}{frag})"

    return LINK.sub(link, text)


def copy_images(text: str, doc_source: Path, page_file: str) -> str:
    """Pictures hosted on the doc_source branch -> copies under assets/docs-img/ (a missing picture stops the build)."""
    def image(m: re.Match) -> str:
        name = unquote(m.group(1))
        src = doc_source / name
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
        if not item:
            return "<span></span>"
        return f'<a class="{cls}" href="../{item["slug"]}/"><span>{label}</span><strong>{esc(item["title"])}</strong></a>'
    return f'<nav class="lc-pager">{side(prev, "lc-pager__prev", "&larr; Previous")}{side(nxt, "lc-pager__next", "Next &rarr;")}</nav>'


def nav_for(own: list[dict], built: list[dict]) -> list[dict]:
    """The sidebar: our own guides first, then the template's sections (each item: title, path, id)."""
    def item(g: dict) -> dict:
        return {"title": g["title"], "path": f"guides/{g['slug']}/", "id": g["slug"]}
    sections = [{"title": "Use an app", "items": [item(g) for g in own]}]
    for s in built:
        sections.append({"title": s["title"], "items": [item(g) for g in s["items"]]})
    return sections


def write_install(site_systems: list[dict], note: str, nav: list[dict]) -> None:
    """guides/install/index.md: how to install an app on each system (data/install.yaml)."""
    body = ["# Install an app", "", note, ""]
    for s in site_systems:
        body += [f"## {s['title']}", ""] + [f"{i}. {step}" for i, step in enumerate(s["steps"], 1)] + [""]
    body += ["Something went wrong? Open an issue in the app's repository, linked from its page in the [App Centre](../../apps/index.md).", ""]
    p = Page("guides/install/index.md", title="Install an app", guide_nav=nav, guide_id="install")
    p.add("\n".join(body))
    p.write()


def write_landing(nav: list[dict]) -> None:
    """guides/index.md: the two ways in, and every guide listed by section."""
    lists = "".join(
        f'<h2>{esc(s["title"])}</h2><ul>' + "".join(f'<li><a href="{i["path"]}">{esc(i["title"])}</a></li>' for i in s["items"]) + "</ul>"
        for s in nav)
    p = Page("guides/index.md", title="Guides", description="How to install LabConstrictor apps and how to build your own.", layout="wide")
    p.add('<section class="lc-pagehead"><h1>Guides</h1><p class="lc-lead">Install an app, or build one from your notebooks.</p></section>',
          f'<div class="lc-guides">{lists}</div>')
    p.write()


def build(template_dir: Path, doc_source: Path, systems: list[dict], note: str) -> None:
    """Write guides/ from the template's .tools/docs and data/install.yaml."""
    docs_dir = template_dir / ".tools" / "docs"
    if not docs_dir.is_dir():
        fail(f"{docs_dir} not found: pass --template-dir with a checkout of {TEMPLATE_REPO}")
    sections = parse_index((docs_dir / "README.md").read_text(encoding="utf-8"))
    own = [{"title": "Install an app", "slug": "install"}]
    for s in sections:
        for g in s["items"]:
            g["slug"] = slug_of(g["file"])
    flat = own + [g for s in sections for g in s["items"]]
    nav, known = nav_for(own, sections), {g["file"] for s in sections for g in s["items"]}
    write_install(systems, note, nav)
    for i, g in enumerate(flat[1:], 1):
        src = docs_dir / g["file"]
        if not src.is_file():
            fail(f"README of the template lists {g['file']}, which does not exist")
        text = NAV_BLOCK.sub("", src.read_text(encoding="utf-8"))
        text = copy_images(rewrite_links(text, known), doc_source, g["file"])
        edit = f"https://github.com/{TEMPLATE_REPO}/edit/main/.tools/docs/{g['file']}"
        p = Page(f"guides/{g['slug']}/index.md", guide_nav=nav, guide_id=g["slug"], edit_url=edit)
        p.add(text.strip(), "", pager(flat[i - 1], flat[i + 1] if i + 1 < len(flat) else None))
        p.write()
    write_landing(nav)
