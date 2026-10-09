"""/llms.txt: the site as plain Markdown for LLMs (llmstxt.org convention), rebuilt on every build."""

from .cards import KINDS, routes
from .config import DOCS, SITE_URL


def app_line(app: dict) -> str:
    """"- [Name](page): summary. Kind; routes; version." for one app."""
    m, release = app["manifest"], app["release"]
    version = f"; latest release {release['tag']}" if release else ""
    return f"- [{m['name']}]({SITE_URL}apps/{app['slug']}/): {m['summary']} {KINDS[m['kind']]}; get it as {', '.join(routes(app))}{version}."


def write(site: dict, apps: list[dict]) -> None:
    """Write docs/llms.txt: what LabConstrictor is, the main pages, and every listed app."""
    lines = [f"# {site['name']}", "", f"> {site['hero']['text']}", "", "## Pages", "",
             f"- [App Centre]({SITE_URL}apps/): installable bioimage analysis apps built with LabConstrictor",
             f"- [Guides]({SITE_URL}guides/): install an app, or build your own from notebooks",
             f"- [Ecosystem]({SITE_URL}ecosystem/): napari, Fiji and QuPath hosts, the template and the tools library",
             f"- [Submit your app]({SITE_URL}submit/): how to list an app", "", "## Apps", ""]
    lines += [app_line(a) for a in apps]
    (DOCS / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
