"""Real-browser smoke tests of the built site (run by hand; not part of the unit tests or the publish workflow).

    zensical build ... (the usual pipeline, so site/ exists)
    python tests/browser/smoke.py [--chromium /opt/pw-browsers/chromium]

Needs Playwright for Python and a Chromium. Serves site/ on a free local port and checks, at phone and desktop widths: no sideways
scrolling on the main pages, the App Centre filter, the steps of How it works, Home's make-an-app path, an app page's download and install steps,
the submit page's manifest form, the demo (smoke_demo.py: its flow, tabs, phone layout and address),
the no-JavaScript fallback, and that every role (titles, links, buttons, badges, tiles, tables, callouts) looks the same on every page. Prints one line per check and exits with status 1 when any fails.
"""

import argparse
import sys

from playwright.sync_api import Browser, sync_playwright

from smoke_common import FAILURES, SITE, check, open_page, serve
from smoke_demo import demo_address, demo_flow, demo_phone

PAGES = ("", "apps/", "demo/", "how-it-works/", "ecosystem/", "related-projects/", "guides/", "use/", "build/", "submit/")
ALL_PAGES = ("", "apps/", "apps/nucleisky/", "apps/celltrackscolab/", "demo/", "how-it-works/", "ecosystem/", "related-projects/", "guides/", "guides/notebook-upload/", "guides/image-software/", "use/", "build/", "submit/")
WIDTHS = {"phone": 390, "desktop": 1280}


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
    """How it works shows one step at a time: the first at first, the others after a click on their number or on Next, and the address names the step."""
    page, errors = open_page(browser, base, "how-it-works/", 1280)
    check("How it works: only the first step is shown at first", page.locator(".how__step:visible").count() == 1 and page.locator("#step-1").is_visible())
    page.click(".how__next")
    page.locator("#step-2").wait_for(state="visible")
    check("How it works: Next shows the second step and hides the first", page.locator("#step-2").is_visible() and not page.locator("#step-1").is_visible())
    check("How it works: the address names the step and its number is marked", page.evaluate("location.hash") == "#step-2" and page.locator(".how__tab.is-current").get_attribute("href") == "#step-2")
    page.click('.how__tab[href="#step-5"]')
    page.locator("#step-5").wait_for(state="visible")
    check("How it works: a click on a number shows that step", page.locator("#step-5").is_visible() and page.locator(".how__step:visible").count() == 1)
    page.go_back()
    page.locator("#step-2").wait_for(state="visible")
    check("How it works: the browser's Back button returns to the previous step", page.locator("#step-2").is_visible())
    page.goto(base + "how-it-works/#step-5")
    page.locator("#step-5").wait_for(state="visible")
    check("How it works: an address shows its step, with the hand-over to the demo", page.locator("#step-5").is_visible() and page.locator("#step-5 a[href$='demo/']").count() == 1)
    check("How it works: no script error", not errors, str(errors))
    page.context.close()


def home_paths(browser: Browser, base: str) -> None:
    """The home page: "I want to make an app" opens How it works, and the steps are not repeated on the home page."""
    page, errors = open_page(browser, base, "", 1280)
    check("Home: the make-an-app card opens How it works", page.locator("a.lc-choice--make").get_attribute("href") == "how-it-works/")
    check("Home: no step cards on the home page", page.locator("a.lc-stepcard").count() == 0)
    check("Home: no script error", not errors, str(errors))
    page.context.close()


def app_download(browser: Browser, base: str) -> None:
    """An app page on Windows: the Windows button is the strong one, the others light; clicking it downloads and opens the Windows steps."""
    context = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True,
                                  user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36")
    page, errors = context.new_page(), []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("**/releases/download/**", lambda r: r.fulfill(status=200, body="x", headers={"Content-Disposition": "attachment; filename=x.exe"}))
    page.goto(base + "apps/nucleisky/", wait_until="load")
    win = page.locator('[data-lc-download="windows"]').first
    check("App page: the visitor's system has the strong button, the others the light one",
          "lc-btn--soft" not in win.get_attribute("class") and "lc-btn--soft" in page.locator('[data-lc-download="linux"]').first.get_attribute("class"))
    check("App page: every install step is folded before a download", page.evaluate("[...document.querySelectorAll('[data-lc-steps]')].every(d => !d.open)"))
    with page.expect_download():
        win.click()
    page.wait_for_timeout(300)
    check("App page: downloading the Windows installer opens the Windows steps only",
          page.evaluate("[...document.querySelectorAll('[data-lc-steps]')].map(d => d.id + ':' + d.open).join()") == "steps-windows:true,steps-macos:false,steps-linux:false")
    check("App page: no script error", not errors, str(errors))
    context.close()


def manifest_form(browser: Browser, base: str) -> None:
    """The submit page's form: not ready until the required fields pass the schema; then it downloads labconstrictor-app.yaml."""
    context = browser.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
    page, errors = context.new_page(), []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(base + "submit/", wait_until="load")
    page.locator("[data-manifest-form]").wait_for(state="visible")
    check("Submit form: empty, the file is not ready", page.locator("[data-mf-download]").is_disabled())
    page.fill("#mf-name", "My App")
    page.fill("#mf-summary", "Counts nuclei in 2D microscopy images.")
    page.select_option("#mf-kind", "analysis")
    check("Submit form: with the required fields the file is ready", page.locator("[data-mf-download]").is_enabled())
    with page.expect_download() as download:
        page.click("[data-mf-download]")
    check("Submit form: it downloads labconstrictor-app.yaml", download.value.suggested_filename == "labconstrictor-app.yaml")
    page.fill("#mf-summary", "short")
    check("Submit form: a too short summary is named beside its field", "summary needs at least 20" in page.inner_text('[data-mf-error="summary"]'))
    check("Submit form: no script error", not errors, str(errors))
    context.close()


def no_javascript(browser: Browser, base: str) -> None:
    """Without JavaScript the demo shows its static figures and no working-looking controls, and How it works shows all its steps one under the other."""
    page, _ = open_page(browser, base, "demo/", 1280, js=False)
    check("No JavaScript, demo: the static figures are shown", page.locator(".lc-demo__static img").first.is_visible() or page.locator("noscript").count() > 0)
    check("No JavaScript, demo: no simulated control is visible", page.locator("[data-demo-sim]:visible").count() == 0)
    page.context.close()
    page, _ = open_page(browser, base, "how-it-works/", 1280, js=False)
    check("No JavaScript, How it works: every step is shown", page.locator(".how__step:visible").count() == 5)
    page.context.close()


ROLES = {   # a role: the elements that must look exactly alike on every page (font, size, weight, colour, spacing)
    "page title (h1)": ".md-content h1:not(.lc-hero h1)",
    "section title (h2)": ".md-content h2:not(.lc-docs__nav h2)",
    "sub-title (h3 in the text)": ".md-content .md-typeset > h3, .md-content .md-typeset > section > h3",
    "tile and card title": ".lc-card__title strong, .lc-feature__body strong, .lc-cat strong, .lc-choice strong, .lc-tile__title, .lc-related__title, .lc-stepcard__title",
    "card and tile description": ".lc-card__text, .lc-stepcard__text, .lc-feature__body span, .lc-cat span, .lc-related__item p:not(.lc-small)",
    "action link": "a.lc-go",
    "button": "a.lc-btn:not(.lc-btn--small), button.lc-btn:not(.lc-btn--small):not(.lc-demo__part)",
    "demo part button": "button.lc-demo__part",
    "small button": ".lc-btn--small",
    "badge": "span.lc-badge",
    "lead": "p.lc-lead",
    "small text": "p.lc-small",
    "label": ".lc-kicker, .lc-filter label, .lc-card__title small",
    "table head cell": ".md-typeset th",
    "table cell": ".md-typeset td",
    "callout": ".lc-help, .how__handoff",
    "breadcrumb": ".lc-crumb",
    "pill link": "a.lc-gh",
    "menu item": ".lc-menu a:not(.lc-menu__cta)",
    "footer link": ".lc-footer li a",
    "fact name": ".lc-facts dt",
    "fact value": ".lc-facts dd",
    "docs menu link": ".lc-docs__nav li a:not(.is-active)",
}
LOOK = ("fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing", "textTransform", "color")
BOXES = ("borderRadius", "paddingTop", "paddingLeft")   # for the boxes: tile, card, panel and callout
BOX_ROLES = {"tile": "a.lc-tile, a.lc-cat, a.lc-stepcard, .lc-choice, .lc-panel, .lc-related__item, .lc-ostile, .how__box:not(.how__box--custom)", "callout box": ".lc-help, .lc-demo__next, blockquote, .how__handoff"}
VARIANTS = {"button", "demo part button", "small button", "badge", "menu item", "docs menu link"}   # filled, ghost, status or host variants differ in colour only


def consistency(browser: Browser, base: str) -> None:
    """Every role in ROLES has one look across the whole site (the first of each differing look is named), and every tile or box has the same padding and corner."""
    seen: dict[str, dict[str, list[str]]] = {name: {} for name in list(ROLES) + list(BOX_ROLES)}
    page, _ = open_page(browser, base, "", 1280)
    for url in ALL_PAGES:
        page.goto(base + url)
        for name, selector in {**ROLES, **BOX_ROLES}.items():
            props = (tuple(p for p in LOOK if p != "color") if name in VARIANTS else LOOK) if name in ROLES else BOXES
            for look in page.evaluate("([sel, props]) => [...document.querySelectorAll(sel)].filter(e => e.offsetParent).map(e => { const c = getComputedStyle(e); return props.map(p => c[p]).join(' | '); })", [selector, list(props)]):
                seen[name].setdefault(look, []).append(url or "home")
    for name, looks in seen.items():
        check(f"Consistency: {name} has one look", len(looks) <= 1, "; ".join(f"{look} on {pages[:2]}" for look, pages in looks.items()))
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
        for group in (no_sideways_scroll, app_filter, how_controls, home_paths, app_download, manifest_form, demo_flow, demo_phone, demo_address, no_javascript, consistency):
            group(browser, base)
        browser.close()
    server.shutdown()
    print(f"smoke: {len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
