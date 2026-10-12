"""The demo's groups of the browser smoke tests (run from smoke.py): its flow and tabs, the phone layout of its windows, and its address."""

from playwright.sync_api import Browser

from smoke_common import check, open_page


def demo_flow(browser: Browser, base: str) -> None:
    """The demo: it opens on the installation, the part buttons come before the hint line, then launch the app, run the notebook to its
    result, see the keyboard tabs work, reset when the view changes, and pick a step of the connection by its diagram box."""
    page, errors = open_page(browser, base, "demo/", 1280)
    check("Demo: it opens on the installation (the first part), with the program tabs hidden", page.get_attribute("#demo-cat-tab-install", "aria-selected") == "true"
          and page.locator("#demo-cat-use").is_hidden() and page.locator("[data-view-tabs]").is_hidden())
    check("Demo: the part buttons come before the hint line", page.evaluate("!!(document.querySelector('.lc-demo__parts').compareDocumentPosition(document.querySelector('[data-next]')) & Node.DOCUMENT_POSITION_FOLLOWING)"))
    page.click("#demo-cat-tab-use")
    check("Demo: the installed app shows its program tabs, each with a logo", page.locator("[data-view-tabs]").is_visible() and page.locator(".lc-demo__view .lc-logo").count() == 3)
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
    page.click('.lc-how__box[data-box="1"]')
    check("Demo: a diagram box of How the connection works selects its step", page.get_attribute('.lc-how__step[data-i="3"]', "aria-pressed") == "true")
    check("Demo: no script error", not errors, str(errors))
    page.context.close()


def demo_phone(browser: Browser, base: str) -> None:
    """The demo on a phone: the whole notebook runs to its result, and every window fits its panel with no value squeezed into a narrow
    column (the fixed label column of the real widgets, the six-column notebook table)."""
    page, errors = open_page(browser, base, "demo/?demo=use", 390)
    for _ in range(30):
        guide = page.locator("#demo-panel-notebook .is-next")
        if not guide.count():
            break
        target = guide.first
        target.scroll_into_view_if_needed()
        (target.dblclick if target.get_attribute("data-act") == "launch" else target.click)()
        page.wait_for_timeout(1300)
    check("Demo on a phone: the notebook runs to the end (no step left to click)", page.locator("#demo-panel-notebook .is-next").count() == 0)
    squeezed = """sel => [...document.querySelectorAll(sel + ' .ns-input, ' + sel + ' .fj__field, ' + sel + ' .nb__table td, ' + sel + ' .np__field')]
        .filter(e => e.getClientRects().length && e.getBoundingClientRect().width < 90 && e.textContent.trim().length > 6).map(e => e.textContent.trim())"""
    for tab in ("notebook", "napari", "fiji"):
        page.click(f"#demo-tab-{tab}") if tab != "notebook" else None
        panel = f"#demo-panel-{tab}"
        if tab == "notebook":
            page.evaluate("document.querySelectorAll('#demo-panel-notebook [data-from-welcome]').forEach(e => e.hidden = false)")
        wide = page.evaluate("sel => { const p = document.querySelector(sel); return [...p.querySelectorAll('*')].filter(e => e.scrollWidth > e.clientWidth + 1 && getComputedStyle(e).overflowX !== 'visible' && getComputedStyle(e).textOverflow !== 'ellipsis' && !e.matches('.nb__log, pre, .lc-sr')).map(e => e.className) }", panel)
        check(f"Demo on a phone: the {tab} window fits its panel (no sideways scroll inside)", not wide, str(wide))
        check(f"Demo on a phone: no value of the {tab} window is squeezed into a narrow column", not page.evaluate(squeezed, panel), str(page.evaluate(squeezed, panel)))
    check("Demo on a phone: no script error", not errors, str(errors))
    page.context.close()


def demo_address(browser: Browser, base: str) -> None:
    """The two demo tiles of the home page open the right part of the demo, and the address keeps it through a tab change, a reload and Back."""
    page, errors = open_page(browser, base, "", 1280)
    installed = "#demo-cat-use:not([hidden])"
    install = "#demo-cat-install:not([hidden])"
    page.click('a.lc-tile[href$="demo/?demo=use"]')
    page.locator(installed).wait_for(state="visible")
    check("Demo address: the installed-app tile opens the installed app", page.get_attribute("#demo-cat-tab-use", "aria-selected") == "true")
    page.reload()
    page.locator(installed).wait_for(state="visible")
    check("Demo address: a reload keeps the installed app", page.locator(install).count() == 0)
    page.click("#demo-cat-tab-install")
    check("Demo address: choosing the installation writes ?demo=install", page.evaluate("location.search") == "?demo=install")
    page.reload()
    page.locator(install).wait_for(state="visible")
    check("Demo address: a reload keeps the installation", page.get_attribute("#demo-cat-tab-install", "aria-selected") == "true")
    page.go_back()
    check("Demo address: Back returns to the home page (changing the part adds no history entry)", page.evaluate("location.pathname") == "/")
    page.goto(base + "demo/")
    page.locator(install).wait_for(state="visible")
    check("Demo address: the plain page opens the installation", page.get_attribute("#demo-cat-tab-install", "aria-selected") == "true")
    check("Demo address: no script error", not errors, str(errors))
    page.context.close()
