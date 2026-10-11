"""The page /how-it-works/: a quick overview of the whole process, one step at a time, from data/how-it-works.yaml.
No code and no panels: every step says what to do and what to remember, and links to the guides that show how."""

import shutil

from .config import CONTENT, DATA, DOCS, REPO, fail, load_yaml
from .images import pixel_size
from .page import Page
from .text import esc

SOURCE = CONTENT / "how"
OUT = DOCS / "assets" / "how"
TOP_KEYS = {"title", "lead", "steps_title", "steps", "figure_credit", "later", "handoff"}
STEP_KEYS = {"id", "title", "text", "figure", "customise", "know", "guides"}
FIGURE_KEYS = {"file", "alt", "caption"}
CREDIT_KEYS = {"text", "link", "href"}
SHOWN = 0.5   # a picture is saved at twice its drawn size and shown at that drawing size (as wide as fits), so the text in every picture has the same size
LINK_KEYS = {"href", "label"}
LATER_KEYS = {"title", "links"}
HANDOFF_KEYS = {"text", "link", "href"}


def check_keys(where: str, item: object, keys: set[str]) -> None:
    """Stop the build, naming the data file and the item, unless `item` is a mapping with exactly `keys`."""
    if not isinstance(item, dict) or set(item) != keys:
        fail(f"data/how-it-works.yaml: {where} needs exactly {sorted(keys)}, got {sorted(item) if isinstance(item, dict) else item!r}")


def check_links(where: str, links: object) -> None:
    """Stop the build unless `links` is a non-empty list of {href, label} items."""
    if not isinstance(links, list) or not links:
        fail(f"data/how-it-works.yaml: {where} needs a list of links")
    for link in links:
        check_keys(f"a link of {where}", link, LINK_KEYS)


def check_steps(steps: object) -> None:
    """Stop the build unless the steps are a list with unique ids, exact keys, at least one thing to remember, a list of things to customise and at least one guide."""
    if not isinstance(steps, list) or len(steps) < 2:
        fail("data/how-it-works.yaml: steps needs a list of at least two steps")
    ids = [s["id"] for s in steps if isinstance(s, dict) and "id" in s]
    if len(set(ids)) != len(steps):
        fail(f"data/how-it-works.yaml: step ids must be present and unique, got {ids}")
    for step in steps:
        check_keys(f"step {step['id']}", step, STEP_KEYS)
        if not isinstance(step["know"], list) or not step["know"] or not isinstance(step["customise"], list):
            fail(f"data/how-it-works.yaml: step {step['id']} needs a list of things to remember and a list (possibly empty) of things to customise")
        for line in step["know"] + step["customise"]:
            if not isinstance(line, str):
                fail(f"data/how-it-works.yaml: step {step['id']} has a line that is not plain text (a colon followed by a space in unquoted YAML makes a mapping): {line!r}")
        check_links(f"step {step['id']}", step["guides"])
        check_keys(f"the figure of step {step['id']}", step["figure"], FIGURE_KEYS)
        if not (SOURCE / "figures" / step["figure"]["file"]).is_file():
            fail(f"{SOURCE / 'figures' / step['figure']['file']} is missing (step {step['id']} of data/how-it-works.yaml)")


def load() -> dict:
    """data/how-it-works.yaml, checked: the exact keys everywhere, unique step ids, things to remember and guides for every step."""
    data = load_yaml(DATA / "how-it-works.yaml")
    check_keys("the top level", data, TOP_KEYS)
    check_keys("figure_credit", data["figure_credit"], CREDIT_KEYS)
    check_keys("later", data["later"], LATER_KEYS)
    check_keys("handoff", data["handoff"], HANDOFF_KEYS)
    check_steps(data["steps"])
    check_links("later", data["later"]["links"])
    return data


def copy_assets() -> None:
    """Copy the page's script and style into docs/assets/how/ (generated)."""
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ("how.js", "how.css"):
        shutil.copy2(SOURCE / name, OUT / name)
    shutil.copytree(SOURCE / "figures", OUT / "figures", dirs_exist_ok=True)


def links_html(links: list[dict], cls: str) -> str:
    """A list of links, each an action link to a page of the site."""
    return f'<ul class="{cls}">' + "".join(f'<li><a class="lc-go" href="{esc(l["href"])}">{esc(l["label"])}</a></li>' for l in links) + "</ul>"


def stepper(data: dict) -> str:
    """The numbered steps as one row of links to their sections; the current one is marked by the script (without it, all steps show)."""
    tabs = "".join(f'<li><a class="how__tab" href="#{esc(s["id"])}" aria-label="Step {i}: {esc(s["title"])}"><span class="how__num">{i}</span>'
                   f'<span class="how__name">{esc(s["title"])}</span></a></li>' for i, s in enumerate(data["steps"], 1))
    return f'<nav class="how__stepper" aria-label="{esc(data["steps_title"])}"><ol>{tabs}</ol></nav>'


def step_nav(steps: list[dict], i: int) -> str:
    """Back and Next links to the neighbouring steps (the last step has the hand-over to the demo instead of Next)."""
    back = f'<a class="how__back" href="#{esc(steps[i - 1]["id"])}">&larr; Back: {esc(steps[i - 1]["title"])}</a>' if i > 0 else "<span></span>"
    nxt = f'<a class="how__next lc-go" href="#{esc(steps[i + 1]["id"])}">Next: {esc(steps[i + 1]["title"])}</a>' if i + 1 < len(steps) else ""
    return f'<p class="how__nav">{back}{nxt}</p>'


def last_step_extras(data: dict) -> str:
    """What closes the last step: the optional later parts, as links to guides, and the hand-over to the installed-app demo."""
    h, later = data["handoff"], data["later"]
    return (f'<h3>{esc(later["title"])}</h3>{links_html(later["links"], "how__guides how__guides--wide")}'
            f'<aside class="how__handoff"><p>{esc(h["text"])}</p><a class="lc-btn lc-btn--primary" href="{esc(h["href"])}">{esc(h["link"])}</a></aside>')


def figure_html(data: dict, step: dict) -> str:
    """The step's picture (a crop of a figure of the preprint, which is CC BY 4.0) with what it shows and the credit under it; its size is read from the file."""
    width, height = pixel_size(SOURCE / "figures" / step["figure"]["file"])
    c = data["figure_credit"]
    f = step["figure"]
    return (f'<figure class="how__figure"><img src="assets/how/figures/{esc(f["file"])}" alt="{esc(f["alt"])}" width="{width}" height="{height}" style="--w:{round(width * SHOWN)}" loading="lazy">'
            f'<figcaption><span class="how__caption">{esc(f["caption"])}</span> <span class="how__credit">{esc(c["text"])} <a href="{esc(c["href"])}">{esc(c["link"])}</a></span></figcaption></figure>')


def customise(step: dict) -> str:
    """The "Make it yours" box of a step: what the author can customise there, or nothing when there is nothing to customise."""
    if not step["customise"]:
        return ""
    items = "".join(f"<li>{esc(c)}</li>" for c in step["customise"])
    return f'<div class="how__custom"><h3>Make it yours <span>(optional)</span></h3><ul>{items}</ul></div>'


def step_html(data: dict, i: int) -> str:
    """One step: its number and title, what you do, the picture, then two columns (what to remember; what to customise and the guides) and the way on."""
    steps = data["steps"]
    s = steps[i]
    know = "".join(f"<li>{esc(k)}</li>" for k in s["know"])
    extras = last_step_extras(data) if i + 1 == len(steps) else ""
    return (f'<section class="how__step" id="{esc(s["id"])}"><h2 tabindex="-1"><span class="how__num">{i + 1}</span> {esc(s["title"])}</h2>'
            f'<p class="how__text">{esc(s["text"])}</p>{figure_html(data, s)}<div class="how__cols"><div><h3>Good to know</h3><ul class="how__know">{know}</ul></div>'
            f'<div>{customise(s)}<h3>Guides</h3>{links_html(s["guides"], "how__guides")}</div></div>{extras}{step_nav(steps, i)}</section>')


def page_how() -> None:
    """how-it-works/index.md: the heading and lead, the row of numbered steps and the steps (one shown at a time with JavaScript, all without)."""
    data = load()
    copy_assets()
    p = Page("how-it-works/index.md", title=data["title"], description=data["lead"], layout="wide", menu="how-it-works/",
             page_css=["assets/how/how.css"], page_js=["assets/how/how.js"], edit_url=f"{REPO}/edit/main/data/how-it-works.yaml")
    p.add(f'<section class="lc-pagehead"><h1>{esc(data["title"])}</h1><p class="lc-lead">{esc(data["lead"])}</p></section>', stepper(data),
          *(step_html(data, i) for i in range(len(data["steps"]))))
    p.write()
