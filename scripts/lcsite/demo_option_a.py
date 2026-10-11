"""The demo's notebook Option A widget: the matcher settings tabs, drawn from content/demo/matcher_config.json (the notebook's own defaults)."""

import json

from .config import CONTENT, fail
from .text import esc

PATH = CONTENT / "demo" / "matcher_config.json"


def load_config() -> dict:
    """matcher_config.json, checked for the sections the page names; stops the build naming the file or section that is missing."""
    if not PATH.is_file():
        fail(f"{PATH} is missing: run tools/demo_assets/matcher_config.py")
    return json.loads(PATH.read_text(encoding="utf-8"))["sections"]


def field(section: str, key: str, value: bool | int | float | str | None) -> str:
    """One setting as the notebook draws it: a checkbox for true/false, a number field for numbers, a text field (reading None) for the rest."""
    if isinstance(value, bool):
        return f'<input type="checkbox" id="{ident(section, key)}"{" checked" if value else ""}>'
    if isinstance(value, (int, float)):
        return f'<input type="number" class="ns-field" id="{ident(section, key)}" step="any" value="{value}">'
    return f'<input type="text" class="ns-field" id="{ident(section, key)}" value="{"None" if value is None else esc(str(value))}">'


def ident(section: str, key: str) -> str:
    """The id of a setting's field, from its tab and name."""
    return f"ns-a-{section}-{key}".replace("_", "-").replace("--", "-")


def panel(section: str, settings: dict, wording: dict) -> str:
    """One tab body: its description and a labelled row for each setting."""
    rows = "".join(f'<p class="ns-row"><label class="ns-flabel" for="{ident(section, k)}">{esc(k)}</label>{field(section, k, v)}</p>' for k, v in settings.items())
    return f'<div data-a-panel="{section}" hidden><p class="nb__note">{esc(wording["description"])}</p>{rows}</div>'


def values(text: dict) -> dict[str, str]:
    """The two placeholders of notebook.html: the tab buttons and the tab bodies. Every tab of the notebook needs wording in demo.yaml (option_a.tabs)."""
    sections, tabs = load_config(), text["option_a"]["tabs"]
    if set(sections) != set(tabs):
        fail(f"demo.yaml option_a.tabs {sorted(tabs)} do not match the sections of {PATH.name} {sorted(sections)}")
    buttons = "".join(f'<button type="button" class="ns-pill" data-demo-sim data-act="a-tab" data-tab="{s}" aria-pressed="false">{esc(tabs[s]["title"])}</button>' for s in sections)
    bodies = "".join(panel(s, sections[s], tabs[s]) for s in sections)
    return {"option_a_buttons": buttons, "option_a_panels": bodies}
