"""The "Related projects and alternative approaches" section of the Ecosystem page, from data/related-projects.yaml."""

from . import citation
from .cards import github_badge, link_pill
from .config import REPO
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
    """One project: name (not a link), what it does, "A good fit when", its paper, the shared-authors note, the check date and the pills."""
    paper = (f'<p class="lc-small">{esc(entry["reference"])}, <a href="{esc(citation.doi_link(entry["doi"]))}">doi:{esc(entry["doi"])}</a></p>'
             if "doi" in entry else "")
    shared = f'<p class="lc-small">{esc(note)}</p>' if "shared_authors" in entry else ""
    return (f'<li class="lc-related__item"><strong>{esc(entry["name"])}</strong><p>{esc(entry["approach"])}</p>'
            f'<p><em>A good fit when</em> {esc(entry["fit"])}</p>{paper}{shared}'
            f'<p class="lc-small">Checked {entry["checked"].day} {entry["checked"]:%B %Y}</p>{entry_links(entry)}</li>')


def group_html(group: dict, note: str) -> str:
    """One approach group: an h3 and its entries in the order of the file (alphabetical there; nothing is ranked)."""
    items = "".join(entry_html(e, note) for e in group["items"])
    return f'<h3 id="related-{esc(group["key"])}">{esc(group["title"])}</h3><ul class="lc-related">{items}</ul>'


def section(related: dict) -> str:
    """The whole section: intro, the visible disclosure, the groups, the closing paragraph and the helper line with its three links."""
    groups = "".join(group_html(g, related["shared_authors_note"]) for g in related["groups"])
    edit = f"{REPO}/edit/main/data/related-projects.yaml"
    helper = (f'<p class="lc-small">{esc(related["helper"])} <a href="index.html#cite">Cite LabConstrictor</a> · '
              f'<a href="{esc(edit)}">Edit this list on GitHub</a> · <a href="{esc(REPO)}/issues">open an issue</a></p>')
    return (f'<section class="lc-related-section"><h2 id="related">{esc(related["title"])}</h2><p>{esc(related["intro"])}</p>'
            f'<p><strong>{esc(related["disclosure"])}</strong></p>{groups}<p>{esc(related["closing"])}</p>{helper}</section>')
