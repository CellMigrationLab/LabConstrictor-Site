"""The interactive demo page (/demo/) and its home-page tile. Everything shown comes from data/demo.yaml and content/demo/."""

from . import demo_media
from .cards import github_badge
from .config import DATA, REPO, load_yaml
from .page import Page
from .text import esc

TABS = (("notebook", "Notebook"), ("napari", "napari"), ("fiji", "Fiji"))
STATIC = (("reference_full.webp", "The reference image: a tiled widefield image of DAPI-stained nuclei, many small round blobs on black.", "The whole reference field."),
          ("query.webp", "The small image to locate: a software-generated crop with about thirty nuclei, rotated and rescaled.", "The small image: a random crop generated from the reference (rotated and rescaled by NucleiSky's Generate Random Crop)."),
          ("reference_roi_green.webp", "The part of the reference where the small image was found, nuclei shown in green.", "The region of the reference where NucleiSky found it."))


def load() -> dict:
    """data/demo.yaml (wording) and content/demo/example.json (numbers), checked."""
    return {"text": load_yaml(DATA / "demo.yaml"), "example": demo_media.load_example()}


def tab_buttons() -> str:
    """The three view tabs: real buttons with tab semantics; the first is selected in the static HTML."""
    out = []
    for i, (key, label) in enumerate(TABS):
        out.append(f'<button type="button" role="tab" id="demo-tab-{key}" aria-controls="demo-panel-{key}" aria-selected="{"true" if i == 0 else "false"}" '
                   f'tabindex="{0 if i == 0 else -1}" class="lc-btn lc-btn--small" data-demo-act="view" data-view="{key}">{label}</button>')
    return '<div class="lc-demo__tabs" role="tablist" aria-label="Interface">' + "".join(out) + '</div>'


def panels(shown: dict[str, str], example: dict) -> str:
    """The three simulated windows, each from its partial with the numbers filled in, inside a tab panel."""
    shown = dict(shown, footprint=demo_media.footprint_points(example))
    out = []
    for i, (key, label) in enumerate(TABS):
        body = demo_media.render(demo_media.read_window(key), shown, f"windows/{key}.html")
        out.append(f'<div role="tabpanel" id="demo-panel-{key}" aria-labelledby="demo-tab-{key}" class="lc-demo__panel"{"" if i == 0 else " hidden"}>{body}</div>')
    return "".join(out)


def static_figures() -> str:
    """What a reader without JavaScript sees: the three real images with captions and descriptions."""
    figs = "".join(f'<figure class="lc-demo__fig"><img src="assets/demo/{f}" alt="{esc(alt)}" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>'
                   for f, alt, cap in STATIC)
    return f'<div class="lc-demo__static">{figs}</div>'


def about_and_features(text: dict) -> str:
    """The short note on the example app (NucleiSky) and the list of features the demo covers, each linked to its guide."""
    a, f = text["about"], text["features"]
    items = "".join(f'<li><strong>{esc(i["title"])}.</strong> {esc(i["text"])} <a href="{esc(i["href"])}">{esc(i["link"])}</a></li>' for i in f["items"])
    c = text["credit"]
    return (f'<section class="lc-demo__about"><h2>{esc(a["title"])}</h2><p>{esc(a["text"])} {github_badge(c["nucleisky_repo"])} '
            f'<a href="apps/nucleisky/">{esc(a["app_link"])}</a></p><h2>{esc(f["title"])}</h2><ul>{items}</ul></section>')


def how_it_works(text: dict) -> str:
    """The collapsible explanation of how the real bridge works, and what this page is not."""
    steps = "".join(f"<li>{esc(s)}</li>" for s in text["how"]["steps"])
    return (f'<details class="lc-demo__how"><summary>{esc(text["how"]["title"])}</summary><ol>{steps}</ol><p>{esc(text["how"]["note"])} '
            f'{github_badge(text["credit"]["tools_repo"], "LabConstrictor-Tools")}</p></details>')


def credits(text: dict) -> str:
    """Where the images and the method come from: the data deposit, the paper and the NucleiSky repository, with their licences."""
    c = text["credit"]
    return (f'<p class="lc-small">{esc(c["data"])} Data: <a href="https://doi.org/{c["dataset_doi"]}">doi:{c["dataset_doi"]}</a>, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. '
            f'Method: NucleiSky, <a href="https://doi.org/{c["paper_doi"]}">doi:{c["paper_doi"]}</a>, {github_badge(c["nucleisky_repo"])}. '
            'The result was computed offline with the released NucleiSky 2D code; how is recorded in <code>content/demo/README.md</code>.</p>')


def page_demo() -> None:
    """demo/index.md: notice, tabs, the three windows (or the static figures without JavaScript), the explanation and the credits."""
    d = load()
    text, example = d["text"], d["example"]
    shown = demo_media.values(example)
    demo_media.copy_assets()
    p = Page("demo/index.md", title=text["title"], description=text["description"], layout="wide", menu="demo/",
             page_css=["assets/demo/demo.css"], page_js=["assets/demo/demo.js"], edit_url=f"{REPO}/edit/main/data/demo.yaml")
    p.add(f'<section class="lc-pagehead"><h1>{esc(text["title"])}</h1>'
          f'<p class="lc-lead">{esc(text["lead"])}</p></section>')
    p.add(about_and_features(text))
    p.add(f'<div class="lc-demo" data-demo data-search-exclude><p class="lc-demo__notice" role="note"><strong>Interactive preview</strong>{esc(text["notice"].removeprefix("Interactive preview"))}</p>'
          f'<div class="lc-demo__live">{tab_buttons()}<button type="button" class="lc-btn lc-btn--small lc-btn--ghost" data-demo-act="reset">Reset demo</button>'
          f'<p class="lc-demo__experimental" data-demo-experimental hidden>{esc(text["experimental"])}</p>{panels(shown, example)}</div>{static_figures()}</div>')
    p.add(how_it_works(text), credits(text))
    p.write()


def tile_html(text: dict) -> str:
    """The home-page tile: one card-sized link to the demo, with a picture and a short line."""
    t = text["tile"]
    return (f'<a class="lc-tile" href="demo/"><img src="assets/demo/reference_roi_green.webp" alt="{esc(t["alt"])}" width="320" height="320" loading="lazy">'
            f'<span class="lc-tile__body"><strong>{esc(t["title"])}</strong><span>{esc(t["text"])}</span><span class="lc-go">{esc(t["link"])}</span></span></a>')


def tile_band() -> str:
    """The home-page band that holds the demo tile (wording from data/demo.yaml)."""
    return f'<section class="lc-band">{tile_html(load_yaml(DATA / "demo.yaml"))}</section>'
