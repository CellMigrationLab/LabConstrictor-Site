"""What the site says about citing: the LabConstrictor block on the home page and the "How to cite" section of each app page."""

from pathlib import Path
from urllib.parse import quote

from .cards import release_line
from .config import fail
from .text import esc

KEYS = ("lead", "reference", "doi")


def doi_link(doi: str) -> str:
    """The resolver address of a DOI, with the characters that need it percent-encoded."""
    return f"https://doi.org/{quote(doi, safe='/')}"


def load(site: dict) -> dict:
    """data/site.yaml `citation`, checked: it must hold a non-empty lead, reference and doi (stops the build naming the file)."""
    block = site["citation"] if "citation" in site else fail("data/site.yaml has no `citation` block")
    for key in KEYS:
        if key not in block or not str(block[key]).strip():
            fail(f"data/site.yaml: citation.{key} is missing or empty")
    return block


def cite_band(site: dict) -> str:
    """The home page's "Cite LabConstrictor" band: the template README's sentence and reference, and a link to the preprint."""
    c = load(site)
    return ('<section class="lc-band lc-band--soft"><h2 class="lc-title" id="cite">Cite LabConstrictor</h2>'
            f'<p class="lc-center">{esc(c["lead"])}</p><p class="lc-center">{esc(c["reference"])} <a href="{esc(doi_link(c["doi"]))}">doi:{esc(c["doi"])}</a></p>'
            '<p class="lc-more"><a class="lc-go" href="' + esc(doi_link(c["doi"])) + '">Read the preprint</a></p>'
            '<p class="lc-small lc-center">Each app page says what its authors ask you to cite.</p></section>')


def check_template_readme(site: dict, template_dir: Path) -> None:
    """Stop the build, naming the template's README.md, when it no longer carries the DOI this site shows (so the two cannot drift apart)."""
    readme = template_dir / "README.md"
    if not readme.is_file():
        fail(f"{readme} is missing")
    if load(site)["doi"] not in readme.read_text(encoding="utf-8"):
        fail(f"{readme} does not contain the citation DOI {load(site)['doi']} that data/site.yaml shows; update one of them")


def version_sentence(app: dict) -> str:
    """"Name the version you used (latest release: v0.1.1 · 8 October 2026)." for an app with a release, "" for one without."""
    return f"<p>Name the version you used (latest release: {release_line(app)}).</p>" if app["release"] else ""


def app_section(app: dict) -> str:
    """The "How to cite" section of an app page, from the manifest's `doi`; "" for a testing app that has none."""
    doi = app["manifest"]["doi"] if "doi" in app["manifest"] else ""
    if doi:
        link = esc(doi_link(doi))
        return (f'<h2 id="cite">How to cite</h2><p>The authors give this publication to cite: <a href="{link}">doi:{esc(doi)}</a></p>'
                f'<p><a class="lc-go" href="{link}">Read the paper</a></p>{version_sentence(app)}')
    if app["section"] == "testing":
        return ""
    return '<h2 id="cite">How to cite</h2><p>This app\'s listing names no publication to cite.</p>' + version_sentence(app)
