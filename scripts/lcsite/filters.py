"""The App Centre's search box and drop-downs. Options are built from the apps themselves, so an option that no app can match never appears."""

from collections import Counter

from .cards import HOSTS, KINDS, ROUTE_LABELS, routes
from .text import esc
from .validate import optional_list


def options(labels: dict[str, str], found: Counter) -> dict[str, str]:
    """The labels of the values at least one app has, each followed by how many apps have it: {"colab": "In the browser (Colab) (3)"}."""
    return {key: f"{label} ({found[key]})" for key, label in labels.items() if found[key]}


def select(name: str, label: str, choices: dict[str, str]) -> str:
    """A filter drop-down whose first option ("All") means no filtering; "" (nothing) when no app offers a choice."""
    if not choices:
        return ""
    items = "".join(f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in choices.items())
    return f'<label>{esc(label)}<select data-lc-{name}><option value="">All</option>{items}</select></label>'


def filter_bar(apps: list[dict]) -> str:
    """The search box and the Kind, run-it and Also-in drop-downs for these apps; lc.js filters the cards live and keeps the count."""
    kinds = Counter(a["manifest"]["kind"] for a in apps)
    ways = Counter(r for a in apps for r in routes(a))
    plugins = Counter(h for a in apps for h in set(optional_list(a["manifest"], "hosts")) if h in HOSTS and h != "notebook")
    return ('<form class="lc-filter" data-lc-filter role="search" onsubmit="return false" hidden>'
            '<label class="lc-filter__search">Search<input type="search" data-lc-search placeholder="Name, task, what it does"></label>'
            + select("kind", "Kind", options(KINDS, kinds)) + select("route", "How do you want to run it?", options(ROUTE_LABELS, ways))
            + select("host", "Also in", options(HOSTS, plugins)) +
            '<p class="lc-filter__count" data-lc-count aria-live="polite"></p>'
            '<button type="button" class="lc-btn lc-btn--ghost lc-btn--small" data-lc-reset>Clear filters</button></form>')
