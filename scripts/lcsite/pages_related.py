"""The related-projects page (/related-projects/) and its teaser on the Ecosystem page, from data/related-projects.yaml."""

from . import citation
from .cards import github_badge, link_pill
from .config import REPO
from .page import Page
from .text import esc


def entry_links(entry: dict) -> str:
    """The pills of one entry: GitHub for its repository, Documentation and Website for its pages (never a link inside prose)."""
    pills = [github_badge(entry["repo"])] if "repo" in entry else []
    if "docs" in entry:
        pills.append(link_pill(entry["docs"], "Documentation", "docs"))
    if "site" in entry:
        pills.append(link_pill(entry["site"], "Website", "web"))
    return f'<p class="lc-related__links">{"".join(pills)}</p>'


def entry_html(entry: dict, note: str) -> str:
    """One project as a text-first card: name (not a link), what it does, "A good fit when", its paper, the shared-authors note, the check date and the pills."""
    paper = (f'<p class="lc-small">{esc(entry["reference"])}, <a href="{esc(citation.doi_link(entry["doi"]))}">doi:{esc(entry["doi"])}</a></p>'
             if "doi" in entry else "")
    shared = f'<p class="lc-small">{esc(note)}</p>' if "shared_authors" in entry else ""
    return (f'<li class="lc-related__item"><strong>{esc(entry["name"])}</strong><p>{esc(entry["approach"])}</p>'
            f'<p><em>A good fit when</em> {esc(entry["fit"])}</p>{paper}{shared}'
            f'<p class="lc-small">Checked {entry["checked"].day} {entry["checked"]:%B %Y}</p>{entry_links(entry)}</li>')


def group_html(group: dict, note: str) -> str:
    """One approach group: an h2 with its anchor and its entries as cards, in the order of the file (alphabetical there; nothing is ranked)."""
    items = "".join(entry_html(e, note) for e in group["items"])
    return f'<section class="lc-related-group"><h2 id="related-{esc(group["key"])}">{esc(group["title"])}</h2><ul class="lc-related">{items}</ul></section>'


def category_tiles(groups: list[dict]) -> str:
    """The category tiles: ordinary links to the group sections of the same page, each with the names of its projects."""
    tiles = "".join(f'<li><a class="lc-cat" href="#related-{esc(g["key"])}"><strong>{esc(g["title"])}</strong>'
                    f'<span>{esc(", ".join(e["name"] for e in g["items"]))}</span></a></li>' for g in groups)
    return f'<nav aria-label="Categories"><ul class="lc-cats">{tiles}</ul></nav>'


def teaser(related: dict) -> str:
    """The one compact card at the end of the Ecosystem page (id="related", the address that older links use) pointing to the full page."""
    t = related["teaser"]
    return (f'<section class="lc-related-section" id="related"><a class="lc-tile lc-tile--text" href="related-projects/"><span class="lc-tile__body">'
            f'<strong>{esc(t["title"])}</strong><span>{esc(t["text"])}</span><span class="lc-go">{esc(t["link"])}</span></span></a></section>')


def page_related(related: dict) -> None:
    """related-projects/index.md: a way back to the Ecosystem page, the title and its kicker, the introduction, the visible disclosure,
    the category tiles, every group, the closing paragraph and the helper line (menu entry: Ecosystem)."""
    p = Page("related-projects/index.md", title=related["page_title"], description=related["intro"].split(". ")[0].strip() + ".", layout="wide",
             menu="ecosystem/", edit_url=f"{REPO}/edit/main/data/related-projects.yaml")
    edit = f"{REPO}/edit/main/data/related-projects.yaml"
    helper = (f'<p class="lc-small">{esc(related["helper"])} <a href="index.html#cite">Cite LabConstrictor</a> · '
              f'<a href="{esc(edit)}">Edit this list on GitHub</a> · <a href="{esc(REPO)}/issues">open an issue</a></p>')
    p.add(f'<p class="lc-crumb"><a href="ecosystem/">&larr; Ecosystem</a></p><section class="lc-pagehead"><p class="lc-kicker">{esc(related["title"])}</p>'
          f'<h1>{esc(related["page_title"])}</h1><p class="lc-lead">{esc(related["intro"])}</p><p><strong>{esc(related["disclosure"])}</strong></p></section>',
          category_tiles(related["groups"]),
          "".join(group_html(g, related["shared_authors_note"]) for g in related["groups"]),
          f'<p>{esc(related["closing"])}</p>{helper}')
    p.write()
