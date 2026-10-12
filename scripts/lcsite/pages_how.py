"""The page /how-it-works/: a quick overview of the whole process, one step at a time, from data/how-it-works.yaml.
No code and no panels: every step is one numbered list of what to do, each action linked to the guide that shows how."""

import shutil

from .config import CONTENT, DATA, DOCS, REPO, fail, load_yaml
from .images import pixel_size
from .page import Page
from .text import esc

SOURCE = CONTENT / "how"
OUT = DOCS / "assets" / "how"
TOP_KEYS = {"title", "lead", "steps_title", "steps", "make_it_yours", "map", "figure_credit", "later", "handoff"}
STEP_KEYS = {"id", "title", "summary", "text", "region", "do"}
ACTION_KEYS = ({"text"}, {"text", "href", "label"})   # an action with the guide that shows how, or (when no guide is needed) text only
YOURS_KEYS = {"title", "items"}
MAP_KEYS = {"pipeline_file", "pipeline_alt", "caption"}
CREDIT_KEYS = {"text", "link", "href"}
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


def check_actions(where: str, actions: object) -> None:
    """Stop the build unless `actions` is a non-empty list of {text} or {text, href, label} items whose values are plain text, and at
    least one of them links to a guide."""
    if not isinstance(actions, list) or not actions:
        fail(f"data/how-it-works.yaml: {where} needs a list of actions")
    for action in actions:
        if not isinstance(action, dict) or set(action) not in ACTION_KEYS:
            fail(f"data/how-it-works.yaml: an action of {where} needs text, and href with label when it links to a guide; got {action!r}")
        if not all(isinstance(v, str) for v in action.values()):
            fail(f"data/how-it-works.yaml: an action of {where} is not plain text (a colon followed by a space in unquoted YAML makes a mapping): {action!r}")
    if not any("href" in a for a in actions):
        fail(f"data/how-it-works.yaml: {where} links to no guide")


def check_steps(steps: object) -> None:
    """Stop the build unless the steps are a list with unique ids, exact keys and a list of actions that links to at least one guide."""
    if not isinstance(steps, list) or len(steps) < 2:
        fail("data/how-it-works.yaml: steps needs a list of at least two steps")
    ids = [s["id"] for s in steps if isinstance(s, dict) and "id" in s]
    if len(set(ids)) != len(steps):
        fail(f"data/how-it-works.yaml: step ids must be present and unique, got {ids}")
    for step in steps:
        check_keys(f"step {step['id']}", step, STEP_KEYS)
        check_actions(f"step {step['id']}", step["do"])
        if not (isinstance(step["region"], list) and len(step["region"]) in (0, 4) and all(isinstance(n, int) for n in step["region"])):
            fail(f"data/how-it-works.yaml: the region of step {step['id']} must be [] (the end-user picture) or [x, y, width, height] in pixels of the pipeline picture")


def load() -> dict:
    """data/how-it-works.yaml, checked: the exact keys everywhere, unique step ids, actions linked to guides for every step."""
    data = load_yaml(DATA / "how-it-works.yaml")
    check_keys("the top level", data, TOP_KEYS)
    check_keys("map", data["map"], MAP_KEYS)
    check_keys("figure_credit", data["figure_credit"], CREDIT_KEYS)
    name = data["map"]["pipeline_file"]
    if not (SOURCE / "figures" / name).is_file():
        fail(f"{SOURCE / 'figures' / name} is missing (map of data/how-it-works.yaml)")
    check_keys("later", data["later"], LATER_KEYS)
    check_keys("handoff", data["handoff"], HANDOFF_KEYS)
    check_steps(data["steps"])
    check_keys("make_it_yours", data["make_it_yours"], YOURS_KEYS)
    check_actions("make_it_yours", data["make_it_yours"]["items"])
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


def step_cards(steps: list[dict]) -> str:
    """The steps as cards, for the home page and the Build hub: each whole card links to its step on How it works (number, title, one-line
    summary). The titles, summaries and ids are the ones of data/how-it-works.yaml, so every page shows the same steps."""
    cards = "".join(f'<li><a class="lc-stepcard" href="how-it-works/#{esc(s["id"])}"><span class="lc-num">{i}</span><h3 class="lc-stepcard__title">{esc(s["title"])}</h3>'
                    f'<span class="lc-stepcard__text">{esc(s["summary"])}</span></a></li>' for i, s in enumerate(steps, 1))
    return f'<ol class="lc-stepcards">{cards}</ol>'


def stepper(data: dict) -> str:
    """The numbered steps as one row of links to their sections; the current one is marked by the script (without it, all steps show)."""
    tabs = "".join(f'<li><a class="how__tab" href="#{esc(s["id"])}" aria-label="Step {i}: {esc(s["title"])}"><span class="lc-num">{i}</span>'
                   f'<span class="how__name">{esc(s["title"])}</span></a></li>' for i, s in enumerate(data["steps"], 1))
    return f'<nav class="how__stepper" aria-label="{esc(data["steps_title"])}"><ol>{tabs}</ol></nav>'


def step_nav(steps: list[dict], i: int) -> str:
    """Back and Next links to the neighbouring steps (the last step has the hand-over to the demo instead of Next)."""
    back = f'<a class="how__back" href="#{esc(steps[i - 1]["id"])}">&larr; Back: {esc(steps[i - 1]["title"])}</a>' if i > 0 else "<span></span>"
    nxt = f'<a class="how__next lc-go" href="#{esc(steps[i + 1]["id"])}">Next: {esc(steps[i + 1]["title"])}</a>' if i + 1 < len(steps) else ""
    return f'<p class="how__nav">{back}{nxt}</p>'


def actions_html(actions: list[dict], cls: str) -> str:
    """A numbered list of actions, each followed by the action link to the guide that shows how (when it has one)."""
    items = "".join(f'<li>{esc(a["text"])}' + (f' <a class="lc-go" href="{esc(a["href"])}">{esc(a["label"])}</a>' if "href" in a else "") + "</li>"
                    for a in actions)
    return f'<ol class="{cls}">{items}</ol>'


def last_step_extras(data: dict) -> str:
    """What closes the last step: what can be customised (once for the whole process), the optional later parts as links to guides, and
    the hand-over to the demo."""
    h, later, yours = data["handoff"], data["later"], data["make_it_yours"]
    title = yours["title"].replace(" (optional)", "")
    return (f'<section class="how__box how__box--custom"><h3>{esc(title)} <span>(optional)</span></h3>{actions_html(yours["items"], "how__do how__do--plain")}</section>'
            f'<h3>{esc(later["title"])}</h3>{links_html(later["links"], "how__guides how__guides--wide")}'
            f'<aside class="how__handoff"><p>{esc(h["text"])}</p><a class="lc-btn lc-btn--primary" href="{esc(h["href"])}">{esc(h["link"])}</a></aside>')


def map_html(data: dict) -> str:
    """The picture at the side: the developer workflow of the preprint (a CC BY 4.0 figure) with a hand-drawn red loop (as in the demo) round the block of the step being read, the rest faded. The script sets data-current; each step's frame is a box given in percent of the picture."""
    m, c = data["map"], data["figure_credit"]
    width, height = pixel_size(SOURCE / "figures" / m["pipeline_file"])
    boxes = [(i, x, y, w, h) for i, s in enumerate(data["steps"], 1) if s["region"] for x, y, w, h in [s["region"]]]
    frames = {kind: "".join(f'<span class="{kind}" data-for="{i}" style="--l:{x * 2 / width * 100:.2f}%;--t:{y * 2 / height * 100:.2f}%;--w:{w * 2 / width * 100:.2f}%;--h:{h * 2 / height * 100:.2f}%"></span>'
                            for i, x, y, w, h in boxes) for kind in ("how__hl", "how__loop")}
    return (f'<aside class="how__map" data-current="1"><div class="how__stage"><div class="how__crop"><img src="assets/how/figures/{esc(m["pipeline_file"])}" alt="{esc(m["pipeline_alt"])}" width="{width}" height="{height}">{frames["how__hl"]}</div>{frames["how__loop"]}</div>'
            f'<p class="how__caption">{esc(m["caption"])}</p><p class="how__credit">{esc(c["text"])} <a href="{esc(c["href"])}">{esc(c["link"])}</a></p></aside>')


def step_html(data: dict, i: int) -> str:
    """One step: its number and title, one sentence on what it is, then one "What to do" list (each action with its guide), and the way on.
    The last step also lists what can be customised, the later parts and the hand-over to the demo."""
    steps = data["steps"]
    s = steps[i]
    extras = last_step_extras(data) if i + 1 == len(steps) else ""
    return (f'<section class="how__step" id="{esc(s["id"])}"><h2 tabindex="-1"><span class="lc-num">{i + 1}</span> {esc(s["title"])}</h2>'
            f'<p class="how__text">{esc(s["text"])}</p><section class="how__box"><h3>What to do</h3>{actions_html(s["do"], "how__do")}</section>'
            f'{extras}{step_nav(steps, i)}</section>')


def page_how() -> None:
    """how-it-works/index.md: the heading and lead, the row of numbered steps, then the picture at the left and the steps (one shown at a time with JavaScript, all without) at the right."""
    data = load()
    copy_assets()
    p = Page("how-it-works/index.md", title=data["title"], description=data["lead"], layout="wide", menu="how-it-works/",
             page_css=["assets/how/how.css"], page_js=["assets/how/how.js"], edit_url=f"{REPO}/edit/main/data/how-it-works.yaml")
    steps = "".join(step_html(data, i) for i in range(len(data["steps"])))
    p.add(f'<section class="lc-pagehead"><h1>{esc(data["title"])}</h1><p class="lc-lead">{esc(data["lead"])}</p></section>', stepper(data),
          f'<div class="how__layout">{map_html(data)}<div class="how__steps">{steps}</div></div>')
    p.write()
