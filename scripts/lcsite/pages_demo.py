"""The interactive demo page (/demo/) and its home-page tile. Everything shown comes from data/demo.yaml and content/demo/."""

from . import demo_media, demo_option_a
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


def category_tabs() -> str:
    """The two parts of the demo: the installed app (shown first) and, optionally, how installation works on Windows. Real buttons with tab semantics."""
    out = []
    for i, (key, label) in enumerate((("use", "Explore the installed app"), ("install", "See how installation works (Windows)"))):
        out.append(f'<button type="button" role="tab" id="demo-cat-tab-{key}" aria-controls="demo-cat-{key}" aria-selected="{"true" if i == 0 else "false"}" '
                   f'class="lc-btn lc-btn--small" data-demo-act="cat" data-cat="{key}">{label}</button>')
    return '<div class="lc-demo__tabs" role="tablist" aria-label="Part of the demo">' + "".join(out) + '</div>'


def panels(shown: dict[str, str], example: dict) -> str:
    """The three simulated windows, each from its partial with the numbers filled in, inside a tab panel."""
    shown = dict(shown, footprint=demo_media.footprint_points(example))
    out = []
    for i, (key, label) in enumerate(TABS):
        body = demo_media.render(demo_media.read_window(key), shown, f"windows/{key}.html")
        out.append(f'<div role="tabpanel" id="demo-panel-{key}" aria-labelledby="demo-tab-{key}" class="lc-demo__panel"{"" if i == 0 else " hidden"}>{body}</div>')
    return "".join(out)


def static_figures(text: dict) -> str:
    """What a reader without JavaScript sees: the three real images with captions and descriptions."""
    figs = "".join(f'<figure class="lc-demo__fig"><img src="assets/demo/{f}" alt="{esc(alt)}" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>'
                   for f, alt, cap in STATIC)
    return f'<noscript><p class="lc-demo__nojs">This is a static view. Turn on JavaScript to try the interactive version.</p><div class="lc-demo__static">{figs}</div>{how_plain(text)}</noscript>'


def about_and_features(text: dict) -> str:
    """The short note on the example app (NucleiSky) and the list of features the demo covers, each linked to its guide."""
    a, f = text["about"], text["features"]
    items = "".join(f'<li><strong>{esc(i["title"])}.</strong> {esc(i["text"])} <a href="{esc(i["href"])}">{esc(i["link"])}</a></li>' for i in f["items"])
    c = text["credit"]
    return (f'<section class="lc-demo__about"><h2>{esc(a["title"])}</h2><p>{esc(a["text"])} {github_badge(c["nucleisky_repo"])} '
            f'<a href="apps/nucleisky/">{esc(a["app_link"])}</a></p><details class="lc-disclosure"><summary>{esc(f["title"])}</summary><ul>{items}</ul></details></section>')


def how_it_works(text: dict) -> str:
    """The six steps of how the real bridge works, as a clickable list with a three-box diagram. Shown only for the napari and Fiji views."""
    steps = "".join(f'<li><button type="button" class="lc-how__step" data-demo-sim data-act="how" data-i="{i}" aria-pressed="{"true" if i == 1 else "false"}">{esc(s)}</button></li>'
                    for i, s in enumerate(text["how"]["steps"], 1))
    boxes = "".join(f'<span class="lc-how__box" data-box="{i}">{esc(label)}</span>' for i, label in enumerate(("Installed app and its Python environment", "LabConstrictor-Tools bridge", "napari, Fiji or QuPath")))
    hosts = "".join(f'<tr><th scope="row">{esc(h["name"])}</th><td><code>{esc(h["where"])}</code></td><td>{esc(h["detail"])}</td></tr>' for h in text["how"]["hosts"])
    return (f'<section class="lc-how" data-how hidden><h2>{esc(text["how"]["title"])}</h2><p class="lc-small">Click a step to see where it happens.</p>'
            f'<div class="lc-how__diagram" aria-hidden="true">{boxes}</div><ol>{steps}</ol>'
            f'<h3>{esc(text["how"]["hosts_title"])}</h3><table class="lc-how__hosts"><thead><tr><th scope="col">Program</th><th scope="col">Where to find it</th><th scope="col">What happens</th></tr></thead><tbody>{hosts}</tbody></table>'
            f'<p>{esc(text["how"]["note"])} {github_badge(text["credit"]["tools_repo"], "LabConstrictor-Tools")}</p></section>')


def how_plain(text: dict) -> str:
    """The same steps as a plain list, for readers without JavaScript."""
    items = "".join(f"<li>{esc(s)}</li>" for s in text["how"]["steps"])
    hosts = "".join(f'<li><strong>{esc(h["name"])}</strong> (<code>{esc(h["where"])}</code>): {esc(h["detail"])}</li>' for h in text["how"]["hosts"])
    return f'<h2>{esc(text["how"]["title"])}</h2><ol>{items}</ol><h3>{esc(text["how"]["hosts_title"])}</h3><ul>{hosts}</ul><p>{esc(text["how"]["note"])}</p>'


def credits(text: dict) -> str:
    """Where the images and the method come from: the data deposit, the paper and the NucleiSky repository, with their licences."""
    c = text["credit"]
    return (f'<p class="lc-small">{esc(c["data"])} Data: <a href="https://doi.org/{c["dataset_doi"]}">doi:{c["dataset_doi"]}</a>, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. '
            f'Method: NucleiSky, <a href="https://doi.org/{c["paper_doi"]}">doi:{c["paper_doi"]}</a>, {github_badge(c["nucleisky_repo"])}. '
            'The result was computed offline with the released NucleiSky 2D code; how is recorded in <code>content/demo/README.md</code>.</p>')


def page_demo(apps: list[dict]) -> None:
    """demo/index.md: notice, tabs, the three windows (or the static figures without JavaScript), the explanation and the credits."""
    d = load()
    text, example = d["text"], d["example"]
    shown = dict(demo_media.values(example), **demo_media.installer_values(), **demo_option_a.values(text))
    demo_media.copy_assets()
    p = Page("demo/index.md", title=text["title"], description=text["description"], layout="wide", menu="demo/",
             page_css=["assets/demo/demo.css", "assets/demo/installer.css"], page_js=[f"assets/demo/{name}" for name in demo_media.SCRIPTS], edit_url=f"{REPO}/edit/main/data/demo.yaml")
    p.add(f'<section class="lc-pagehead"><h1>{esc(text["title"])}</h1>'
          f'<p class="lc-lead">{esc(text["lead"])}</p><p>{esc(text["packaging"]["text"])} <a class="lc-go" href="{esc(text["packaging"]["href"])}">{esc(text["packaging"]["link"])}</a></p></section>')
    p.add(about_and_features(text))
    installer = demo_media.render(demo_media.read_window("installer"), shown, "windows/installer.html")
    p.add(f'<div class="lc-demo" data-demo data-search-exclude><p class="lc-demo__notice" role="note"><strong>Interactive preview</strong>{esc(text["notice"].removeprefix("Interactive preview"))}</p>'
          f'<div class="lc-demo__live"><p class="lc-demo__next" data-next></p>{category_tabs()}<button type="button" class="lc-btn lc-btn--small lc-btn--ghost" data-demo-act="reset">Reset demo</button>'
          f'<div role="tabpanel" id="demo-cat-install" aria-labelledby="demo-cat-tab-install" data-cat-panel="install" class="lc-demo__panel" hidden>{installer}</div>'
          f'<div role="tabpanel" id="demo-cat-use" aria-labelledby="demo-cat-tab-use" data-cat-panel="use">{tab_buttons()}'
          f'<p class="lc-demo__experimental" data-demo-experimental hidden>{esc(text["experimental"])}</p>{panels(shown, example)}{how_it_works(text)}</div></div>{static_figures(text)}</div>')
    p.add(credits(text))
    p.write()


def tile_html(text: dict) -> str:
    """The home-page tile: one card-sized link to the demo, with a picture and a short line."""
    t = text["tile"]
    return (f'<a class="lc-tile" href="demo/"><img src="assets/demo/reference_roi_green.webp" alt="{esc(t["alt"])}" width="320" height="320" loading="lazy">'
            f'<div class="lc-tile__body"><h3 class="lc-tile__title">{esc(t["title"])}</h3><span>{esc(t["text"])}</span><span class="lc-go">{esc(t["link"])}</span></div></a>')


def home_tile() -> str:
    """The home page's demo tile (wording from data/demo.yaml)."""
    return tile_html(load_yaml(DATA / "demo.yaml"))
