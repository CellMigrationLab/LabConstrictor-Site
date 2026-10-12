"""What every group of the browser smoke tests shares: the built site, the local server, opening a page and recording a result."""

import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import Browser, Page

SITE = Path(__file__).resolve().parents[2] / "site"
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
