"""The two hub pages, /use/ and /build/: cards with a picture, then every guide of the track."""

from pathlib import Path

from PIL import Image

from . import sources
from .cards import card
from .config import DOCS, REPO, fail
from .github import MAX_FILE
from .guides import TRACKS, guide_lists
from .images import shrink
from .page import Page
from .text import esc

HUB_PX = 1000   # widest picture on a hub page; larger ones are shrunk


def image_sources(hubs: dict) -> list[dict]:
    """The pictures kept in other repositories (`repo` + `path`), for scripts/fetch_guides.py to download."""
    found = [f["image"] for h in hubs.values() for f in h["cards"] if "image" in f]
    return [{"repo": i["repo"], "path": i["path"], "limit": MAX_FILE} for i in found if "repo" in i]


def source_file(spec: dict, doc_source: Path) -> Path:
    """Where a picture is on disk: the template's doc_source checkout, or a fetched file. Stops the build when it is not there."""
    if ("doc_source" in spec) == ("repo" in spec):
        fail(f"data/hubs.yaml: a picture needs either doc_source or repo and path, not both or neither: {spec}")
    path = doc_source / spec["doc_source"] if "doc_source" in spec else sources.local_path(spec["repo"], spec["path"])
    if not path.is_file():
        fail(f"data/hubs.yaml: picture {path} does not exist (run scripts/fetch_guides.py, or check the name)")
    return path


def prepare_image(spec: dict, doc_source: Path, alt: str | None, taken: dict[str, Path]) -> str:
    """Shrink one picture into docs/assets/hubs/ and return its <img> tag. A picture without alt text, or two different ones with one name, stops the build."""
    if not alt:
        fail(f"data/hubs.yaml: the picture {spec} has no alt text")
    src = source_file(spec, doc_source)
    name = f"{src.stem}.jpg"
    if taken.setdefault(name, src) != src:
        fail(f"data/hubs.yaml: two different pictures are both called {src.stem}")
    dest = DOCS / "assets" / "hubs" / name
    shrink(src, dest, HUB_PX)
    with Image.open(dest) as img:
        w, h = img.size
    wide = " data-wide" if w > 2.5 * h else ""
    return f'<img src="assets/hubs/{name}" alt="{esc(alt)}" width="{w}" height="{h}" loading="lazy"{wide}>'


def feature(item: dict, shot: str) -> str:
    """One card: its picture, a title, a sentence and a link to the guide that goes with it. A live app card
    (which is itself a link) is shown as it is; a picture is wrapped in a link to the guide."""
    wide = " lc-feature__shot--wide" if "data-wide" in shot else ""
    shot_html = shot if shot.startswith("<ul") else f'<a href="{esc(item["href"])}" tabindex="-1" aria-hidden="true">{shot}</a>'
    return (f'<li class="lc-feature"><div class="lc-feature__shot{wide}">{shot_html}</div>'
            f'<div class="lc-feature__body"><strong>{esc(item["title"])}</strong><span>{esc(item["text"])}</span>'
            f'<a href="{esc(item["href"])}">{esc(item["link"])} &rarr;</a></div></li>')


def live_shot(apps: list[dict]) -> str:
    """The "listed in the App Centre" picture: a real card of a featured app, so it cannot go out of date."""
    featured = [a for a in apps if a["featured"]]
    if not featured:
        fail("no app is featured, so the 'Others can find it' card has nothing to show")
    return f'<ul class="lc-grid lc-feature__live">{card(featured[0])}</ul>'


def features_html(items: list[dict], doc_source: Path, apps: list[dict], taken: dict[str, Path]) -> str:
    """The grid of feature cards."""
    cards = [feature(i, live_shot(apps) if i.get("live_card") else prepare_image(i["image"], doc_source, i.get("alt"), taken)) for i in items]
    return '<ul class="lc-features">' + "".join(cards) + "</ul>"


def flow_html(title: str, steps: list[dict]) -> str:
    """The numbered row of what you do to build an app, each step linking to its guide."""
    items = "".join(f'<li><strong>{esc(s["title"])}</strong><span>{esc(s["text"])}</span><a href="{esc(s["href"])}">{esc(s["link"])} &rarr;</a></li>' for s in steps)
    return f'<h2 class="lc-title">{esc(title)}</h2><ol class="lc-steps lc-steps--flow">{items}</ol>'


def write_hub(track: str, hub: dict, nav: list[dict], doc_source: Path, apps: list[dict], taken: dict[str, Path]) -> None:
    """<track>/index.md: the introduction, the picture cards, then every guide of the track."""
    p = Page(f"{track}/index.md", title=hub["title"], description=hub["lead"], guide_nav=nav, guide_id="", guide_track=track,
             guide_track_title=TRACKS[track], menu="guides/", edit_url=f"{REPO}/edit/main/data/hubs.yaml")
    p.add(f'<section class="lc-pagehead"><h1>{esc(hub["title"])}</h1><p class="lc-lead">{esc(hub["lead"])}</p></section>')
    p.add(features_html(hub["cards"], doc_source, apps, taken))
    if "help" in hub:
        h = hub["help"]
        p.add(f'<p class="lc-help"><strong>{esc(h["title"])}</strong> {esc(h["text"])} <a href="{esc(h["href"])}">{esc(h["link"])} &rarr;</a></p>')
    if "flow" in hub:
        p.add(flow_html(hub["flow_title"], hub["flow"]))
    p.write()


def write_docs_home(hubs: dict, nav: list[dict]) -> None:
    """guides/index.md: the front page of the docs (menu entry "Docs"): one card per track, then every guide."""
    p = Page("guides/index.md", title="Docs", description="Guides for using LabConstrictor apps and for building your own.",
             guide_nav=nav, guide_id="", docs_home=True, menu="guides/", edit_url=f"{REPO}/edit/main/data/hubs.yaml")
    cards = "".join(f'<a class="lc-choice{" lc-choice--make" if t == "build" else ""}" href="{t}/"><strong>{esc(hubs[t]["title"])}</strong>'
                    f'<span>{esc(hubs[t]["lead"])}</span><span class="lc-choice__go">Open &rarr;</span></a>' for t in TRACKS)
    p.add('<h1>Docs</h1><p class="lc-lead">Use an app someone built, or build your own.</p>',
          f'<div class="lc-choices">{cards}</div>',
          '<div class="lc-guides lc-guides--two">' + "".join(f'<section id="all-{t}"><h2>{esc(TRACKS[t])}</h2>{guide_lists(nav, t)}</section>' for t in TRACKS) + "</div>")
    p.write()


def write_all(hubs: dict, nav: list[dict], doc_source: Path, apps: list[dict]) -> None:
    """Write both hub pages."""
    taken: dict[str, Path] = {}
    for track in TRACKS:
        write_hub(track, hubs[track], nav, doc_source, apps, taken)
    write_docs_home(hubs, nav)
