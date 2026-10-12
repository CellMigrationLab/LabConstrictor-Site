"""The interactive demo page (/demo/) and its home-page tile. Everything shown comes from data/demo.yaml and content/demo/."""

from . import demo_media, demo_option_a, hosts
from .cards import github_badge
from .config import DATA, REPO, load_yaml
from .page import Page
from .text import esc

TABS = (("notebook", "Notebook"), ("napari", "napari"), ("fiji", "Fiji"))
PARTS = ("install", "use")   # the two parts of the demo, in their order on the page; /demo/?demo=use opens the second (demo.js reads it before the first drawing)
PART_LABELS = {"install": "See how installation works (Windows)", "use": "Explore the installed app"}


def tab_logo(key: str) -> str:
    """The logo in a view tab: JupyterLab for the notebook, the program's own logo for napari and Fiji."""
    return hosts.service_logo("jupyter") if key == "notebook" else hosts.logo(key)
STATIC = (("reference_full.webp", "The reference image: a tiled widefield image of DAPI-stained nuclei, many small round blobs on black.", "The whole reference field."),
          ("query.webp", "The small image to locate: a software-generated crop with about thirty nuclei, rotated and rescaled.", "The small image: a random crop generated from the reference (rotated and rescaled by NucleiSky's Generate Random Crop)."),
          ("reference_roi_green.webp", "The part of the reference where the small image was found, nuclei shown in green.", "The region of the reference where NucleiSky found it."))


def load() -> dict:
    """data/demo.yaml (wording) and content/demo/example.json (numbers), checked."""
    return {"text": load_yaml(DATA / "demo.yaml"), "example": demo_media.load_example()}


def tab_buttons() -> str:
    """The three view tabs, each with its program's logo: real buttons with tab semantics; the first is selected in the static HTML.
    They belong to the installed-app part, so they are hidden while the installation part shows."""
    out = []
    for i, (key, label) in enumerate(TABS):
        out.append(f'<button type="button" role="tab" id="demo-tab-{key}" aria-controls="demo-panel-{key}" aria-selected="{"true" if i == 0 else "false"}" '
                   f'tabindex="{0 if i == 0 else -1}" class="lc-btn lc-demo__view" data-demo-act="view" data-view="{key}">{tab_logo(key)}<span>{label}</span></button>')
    return '<div class="lc-demo__tabs lc-demo__views" role="tablist" aria-label="Interface" data-view-tabs hidden>' + "".join(out) + '</div>'


def category_tabs() -> str:
    """The two parts of the demo, in the order a colleague meets them: how installation works on Windows (shown first), then the installed
    app. Real buttons with tab semantics, as wide as the page."""
    out = []
    for i, key in enumerate(PARTS):
        out.append(f'<button type="button" role="tab" id="demo-cat-tab-{key}" aria-controls="demo-cat-{key}" aria-selected="{"true" if i == 0 else "false"}" '
                   f'class="lc-btn lc-demo__part" data-demo-act="cat" data-cat="{key}"><span class="lc-num">{i + 1}</span>{PART_LABELS[key]}</button>')
    return '<div class="lc-demo__tabs lc-demo__parts" role="tablist" aria-label="Part of the demo">' + "".join(out) + '</div>'


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
    return f'<noscript><p class="lc-demo__nojs">This is a static view. Turn on JavaScript to try the interactive version and the Windows installation walkthrough.</p><div class="lc-demo__static">{figs}</div>{how_plain(text)}</noscript>'


def about_and_features(text: dict) -> str:
    """The short note on the example app (NucleiSky)."""
    a, c = text["about"], text["credit"]
    return (f'<section class="lc-demo__about"><h2>{esc(a["title"])}</h2><p>{esc(a["text"])} {github_badge(c["nucleisky_repo"])} '
            f'<a href="apps/nucleisky/">{esc(a["app_link"])}</a></p></section>')


def how_it_works(text: dict) -> str:
    """The six steps of how the real bridge works, as a clickable list with a three-box diagram. Shown only for the napari and Fiji views."""
    steps = "".join(f'<li><button type="button" class="lc-how__step" data-demo-sim data-act="how" data-i="{i}" aria-pressed="{"true" if i == 1 else "false"}">{esc(s)}</button></li>'
                    for i, s in enumerate(text["how"]["steps"], 1))
    boxes = "".join(f'<button type="button" class="lc-how__box" data-demo-sim data-act="how" data-i="{step}" data-box="{i}">{esc(label)}</button>'
                    for i, (label, step) in enumerate((("Installed app and its Python environment", 1), ("LabConstrictor-Tools bridge", 3), ("napari, Fiji or QuPath", 4))))
    hosts = "".join(f'<tr><th scope="row">{esc(h["name"])}</th><td><code>{esc(h["where"])}</code></td><td>{esc(h["detail"])}</td></tr>' for h in text["how"]["hosts"])
    return (f'<section class="lc-how" id="demo-how" data-how hidden><h2>{esc(text["how"]["title"])}</h2><p class="lc-small">Click a box or a step to see where it happens.</p>'
            f'<div class="lc-how__diagram">{boxes}</div><ol>{steps}</ol>'
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
            f'The result was computed offline with the released NucleiSky 2D code (method: <a href="{REPO}/blob/main/content/demo/README.md">the demo&#39;s README on GitHub</a>).</p>')


def page_demo(apps: list[dict]) -> None:
    """demo/index.md: heading and lead (with the precomputed-result sentence), tabs, the three windows (or the static figures without JavaScript), then the note on the example with two guide links, and the credits."""
    d = load()
    text, example = d["text"], d["example"]
    shown = dict(demo_media.values(example), **demo_media.installer_values(), **demo_option_a.values(text))
    demo_media.copy_assets()
    p = Page("demo/index.md", title=text["title"], description=text["description"], layout="wide", menu="demo/",
             page_css=["assets/demo/demo.css", "assets/demo/installer.css"], page_js=[f"assets/demo/{name}" for name in demo_media.SCRIPTS], edit_url=f"{REPO}/edit/main/data/demo.yaml")
    p.add(f'<section class="lc-pagehead"><h1>{esc(text["title"])}</h1>'
          f'<p class="lc-lead">{esc(text["lead"])}</p><p>{esc(text["packaging"]["text"])} <a class="lc-go" href="{esc(text["packaging"]["href"])}">{esc(text["packaging"]["link"])}</a></p></section>')
    installer = demo_media.render(demo_media.read_window("installer"), shown, "windows/installer.html")
    os_note = text["other_systems"]
    p.add(f'<div class="lc-demo" data-demo data-search-exclude><div class="lc-demo__live">{category_tabs()}{tab_buttons()}<p class="lc-demo__next" data-next></p>'
          f'<div role="tabpanel" id="demo-cat-install" aria-labelledby="demo-cat-tab-install" data-cat-panel="install"><div class="lc-demo__panel">{installer}</div>'
          f'<p class="lc-small lc-demo__os">{esc(os_note["text"])} <a href="{esc(os_note["href"])}">{esc(os_note["link"])}</a></p></div>'
          f'<div role="tabpanel" id="demo-cat-use" aria-labelledby="demo-cat-tab-use" data-cat-panel="use" hidden>'
          f'<p class="lc-demo__experimental" data-demo-experimental hidden>{esc(text["experimental"])} <a href="#demo-how">{esc(text["how"]["title"])} &darr;</a></p>{panels(shown, example)}{how_it_works(text)}</div></div>{static_figures(text)}</div>')
    p.add(about_and_features(text))
    p.add(credits(text))
    p.write()


def part_url(part: str) -> str:
    """The address of one part of the demo: the plain page for the installation (the first part), ?demo=use for the installed app."""
    if part not in PARTS:
        raise ValueError(f"data/demo.yaml: a tile names the part {part!r}, not one of {PARTS}")
    return "demo/" if part == PARTS[0] else f"demo/?demo={part}"


def tile_html(tile: dict) -> str:
    """One home-page tile: a card-sized link, with no picture, to one part of the demo."""
    return (f'<a class="lc-tile" href="{part_url(tile["part"])}"><div class="lc-tile__body"><h3 class="lc-tile__title">{esc(tile["title"])}</h3>'
            f'<span>{esc(tile["text"])}</span><span class="lc-go">{esc(tile["link"])}</span></div></a>')


def home_tiles() -> list[str]:
    """The home page's two demo tiles (wording from data/demo.yaml): the simulated Windows installation and the installed app."""
    return [tile_html(t) for t in load_yaml(DATA / "demo.yaml")["tiles"]]
