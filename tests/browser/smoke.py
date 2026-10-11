"""Real-browser smoke tests of the built site (run by hand; not part of the unit tests or the publish workflow).

    zensical build ... (the usual pipeline, so site/ exists)
    python tests/browser/smoke.py [--chromium /opt/pw-browsers/chromium]

Needs Playwright for Python and a Chromium. Serves site/ on a free local port and checks, at phone and desktop widths: no sideways
scrolling on the main pages, the App Centre filter, every control of How it works, the demo's flow, its keyboard tabs and the reset when the view changes,
and the no-JavaScript fallback. Prints one line per check and exits with status 1 when any fails.
"""

import argparse
import functools
import http.server
import sys
import threading
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

SITE = Path(__file__).resolve().parents[2] / "site"
PAGES = ("", "apps/", "demo/", "how-it-works/", "ecosystem/", "related-projects/", "guides/", "use/", "build/", "submit/")
WIDTHS = {"phone": 390, "desktop": 1280}
FAILURES: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    """Record and print one result."""
    print(("ok   " if ok else "FAIL ") + name + (f": {detail}" if detail and not ok else ""))
    if not ok:
        FAILURES.append(name)


def serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    """Serve site/ on a free port in a background thread; returns the server and its base address."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        """Serves site/ without logging each request."""

        def log_message(self, *args: object) -> None:
            """Say nothing."""

    handler = functools.partial(Quiet, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def open_page(browser: Browser, base: str, path: str, width: int, js: bool = True) -> tuple[Page, list[str]]:
    """A fresh page at the given width, its script errors collected in the returned list."""
    context = browser.new_context(viewport={"width": width, "height": 900}, java_script_enabled=js)
    page, errors = context.new_page(), []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + path, wait_until="load")
    return page, errors


def no_sideways_scroll(browser: Browser, base: str) -> None:
    """Every main page fits its width, without script errors, at phone and desktop widths."""
    for label, width in WIDTHS.items():
        for path in PAGES:
            page, errors = open_page(browser, base, path, width)
            wide = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(f"{label} {path or 'home'}: fits the width and runs without errors", wide <= 0 and not errors, f"overflow {wide}px, errors {errors}")
            page.context.close()


def app_filter(browser: Browser, base: str) -> None:
    """Typing in the App Centre search leaves fewer cards, and a word no app has leaves none and says so."""
    page, errors = open_page(browser, base, "apps/", 1280)
    total = page.locator("[data-app]").count() if page.locator("[data-app]").count() else page.locator(".lc-grid > li").count()
    field = page.locator("input[type=search], input[data-filter-q], #lc-q").first
    field.fill("zzzzqqqq")
    page.wait_for_timeout(300)
    visible = page.locator(".lc-grid > li:visible").count()
    check("App Centre: a word no app has shows no card", total > 0 and visible == 0, f"{total} cards, {visible} visible")
    field.fill("")
    page.wait_for_timeout(300)
    check("App Centre: clearing the search shows the cards again", page.locator(".lc-grid > li:visible").count() == total and not errors)
    page.context.close()


def how_controls(browser: Browser, base: str) -> None:
    """Every choice button of every How it works panel can be pressed and ends up pressed, with no script error."""
    page, errors = open_page(browser, base, "how-it-works/", 1280)
    page.evaluate("document.querySelectorAll('details.how__more').forEach(d => { d.open = true; })")   # the Go further chapters are folded
    check("How it works: following a Go further address opens its chapter", page.evaluate("(() => { history.replaceState(null, '', '#sync'); window.dispatchEvent(new HashChangeEvent('hashchange')); return document.getElementById('sync').open; })()"))
    buttons = page.locator(".how__panel [data-set], .how__panel [data-toggle]")
    for i in range(buttons.count()):
        button = buttons.nth(i)
        if not button.is_visible():
            continue   # a button of a state that is not showing yet
        button.scroll_into_view_if_needed()
        button.click()
        if button.get_attribute("data-set"):
            check(f"How it works: button {i + 1} is pressed after a click", button.get_attribute("aria-pressed") == "true")
    check("How it works: no script error while pressing every control", not errors, str(errors))
    page.context.close()


def demo_flow(browser: Browser, base: str) -> None:
    """The demo: launch the app, run the notebook to its result, see the keyboard tabs work, and reset when the view changes."""
    page, errors = open_page(browser, base, "demo/", 1280)
    check("Demo: it opens on the installed app, not on the installer", page.get_attribute("#demo-cat-tab-use", "aria-selected") == "true" and page.locator("#demo-cat-install").is_hidden())
    page.click("#demo-cat-tab-install")
    check("Demo: the Windows installer is one click away", page.locator("#demo-cat-install").is_visible())
    page.click("#demo-cat-tab-use")
    page.dblclick("#demo-panel-notebook [data-act=launch]")
    for selector in ('[data-act="run-welcome"]', '[data-act="open-app"]', '[data-act="run-init"]', '[data-act="run-step"][data-step="1"]'):
        page.locator("#demo-panel-notebook " + selector).first.click()
        page.wait_for_timeout(1200)
    check("Demo: the notebook reaches Step 1 and shows its widget", page.locator("#demo-panel-notebook [data-act=crop-mode]").first.is_visible())
    page.click("#demo-tab-napari")
    check("Demo: switching to napari resets the demo (no result shown)", page.locator("#demo-panel-napari .np__status").inner_text().strip() == "idle")
    page.focus("#demo-tab-napari")
    page.keyboard.press("ArrowRight")
    check("Demo: the arrow key moves to the Fiji tab", page.get_attribute("#demo-tab-fiji", "aria-selected") == "true")
    check("Demo: no script error", not errors, str(errors))
    page.context.close()


def no_javascript(browser: Browser, base: str) -> None:
    """Without JavaScript the demo shows its static figures and no working-looking controls, and How it works shows its plain lists."""
    page, _ = open_page(browser, base, "demo/", 1280, js=False)
    check("No JavaScript, demo: the static figures are shown", page.locator(".lc-demo__static img").first.is_visible() or page.locator("noscript").count() > 0)
    check("No JavaScript, demo: no simulated control is visible", page.locator("[data-demo-sim]:visible").count() == 0)
    page.context.close()
    page, _ = open_page(browser, base, "how-it-works/", 1280, js=False)
    check("No JavaScript, How it works: the plain summaries are shown", page.locator(".how__static:visible").count() > 0)
    check("No JavaScript, How it works: no inert simulated control is visible", page.locator(".how__panel [data-demo-sim]:visible").count() == 0)
    page.context.close()


def main() -> int:
    """Run every group of checks; return the exit status."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--chromium", default="/opt/pw-browsers/chromium", help="path of the Chromium executable")
    args = parser.parse_args()
    if not SITE.is_dir():
        print("smoke: build the site first (no site/)", file=sys.stderr)
        return 2
    server, base = serve()
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.chromium)
        for group in (no_sideways_scroll, app_filter, how_controls, demo_flow, no_javascript):
            group(browser, base)
        browser.close()
    server.shutdown()
    print(f"smoke: {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
