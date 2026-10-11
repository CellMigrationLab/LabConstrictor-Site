"""What the site says about its own catalogue (counts, ways to get an app, systems), worked out from the apps themselves.

Nothing here is written by hand: when an app is added, removed or loses its Colab link, the sentences change at the next build.
"""

from .cards import SYSTEMS, routes
from .text import plural


def join_or(items: list[str]) -> str:
    """["a"] -> "a"; ["a", "b"] -> "a or b"; ["a", "b", "c"] -> "a, b or c"."""
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " or " + items[-1]


def listed(apps: list[dict]) -> list[dict]:
    """The apps for users (not the ones kept apart under "Testing and maintenance")."""
    return [a for a in apps if a["section"] == "apps"]


def ways(apps: list[dict]) -> list[str]:
    """The route keys ("installer", "colab", "pip") that at least one of the given apps offers, in the site's display order."""
    offered = {r for a in apps for r in routes(a)}
    return [r for r in ("installer", "colab", "pip") if r in offered]


def systems(apps: list[dict]) -> list[str]:
    """The operating systems (Windows, macOS, Linux) for which at least one app has an installer in its latest release."""
    present = {x["os"] for a in apps if a["release"] is not None for x in a["release"]["assets"]}
    return [label for key, label in SYSTEMS.items() if key in present]


def get_sentence(apps: list[dict]) -> str:
    """"Install one in a few clicks, or open it in Colab." with only the ways that some app really offers ("" when none does)."""
    phrases = {"installer": "install one in a few clicks", "colab": "open it in Colab", "pip": "install it with pip"}
    found = [phrases[r] for r in ways(apps)]
    if not found:
        return ""
    text = ", ".join(found[:-1]) + (", or " if len(found) > 2 else " or " if len(found) == 2 else "") + found[-1]
    return text[0].upper() + text[1:] + "."


def catalogue_lead(apps: list[dict]) -> str:
    """The sentence under the App Centre heading: how many apps, how many for testing, and the ways to get them."""
    users, testing = listed(apps), [a for a in apps if a["section"] == "testing"]
    if not users:
        return "No app is listed yet."
    count = f"{plural(len(users), 'app')} built with LabConstrictor" + (f", and {len(testing)} for testing and maintenance" if testing else "") + "."
    return f"{count} {get_sentence(users)}".strip()


def home_find_text(apps: list[dict]) -> str:
    """The text of the home page's "I want to find an app" choice: the number of apps and, if installers exist, the few-clicks promise."""
    users = listed(apps)
    if not users:
        return "The App Centre has no app yet."
    install = " Install in a few clicks." if "installer" in ways(users) else ""
    return f"Browse {plural(len(users), 'app')} built with LabConstrictor.{install}"


def catalogue_description(apps: list[dict]) -> str:
    """The App Centre's page description for search results and link previews."""
    users, parts = listed(apps), []
    if systems(users):
        parts.append(f"install them on {join_or(systems(users))}")
    if "colab" in ways(users):
        parts.append("open them in Colab")
    return "Apps built with LabConstrictor" + (": " + ", or ".join(parts) + "." if parts else ".")
