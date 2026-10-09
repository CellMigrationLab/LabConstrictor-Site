"""A small GitHub API client. Every failure becomes an AppProblem that names the URL."""

import json
import os
import urllib.error
import urllib.request

from .config import AppProblem

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
TIMEOUT = 30


class GitHub:
    """Reads public repositories. GITHUB_TOKEN (optional) raises the rate limit; it is never printed."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN")

    def _open(self, url: str, accept: str) -> bytes:
        """GET a URL; raise AppProblem with the status (and rate-limit hint) on any failure."""
        headers = {"Accept": accept, "User-Agent": "labconstrictor-site"}
        if self.token and url.startswith(API):
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=TIMEOUT) as r:
                return r.read()
        except urllib.error.HTTPError as err:
            hint = " (rate limited? set GITHUB_TOKEN)" if err.code in (403, 429) else ""
            raise AppProblem(f"GET {url} failed: HTTP {err.code}{hint}") from err
        except (urllib.error.URLError, TimeoutError) as err:
            raise AppProblem(f"GET {url} failed: {err}") from err

    def json(self, path: str) -> dict:
        """GET an API path ("/repos/o/r") and parse the JSON."""
        return json.loads(self._open(API + path, "application/vnd.github+json"))

    def repo(self, full_name: str) -> dict:
        """Repository metadata (id, owner id, default branch, archived flag, license)."""
        return self.json(f"/repos/{full_name}")

    def latest_release(self, full_name: str) -> dict:
        """The latest published release (not a draft or pre-release)."""
        return self.json(f"/repos/{full_name}/releases/latest")

    def raw(self, full_name: str, ref: str, path: str) -> bytes:
        """A file from the repository at a branch or tag."""
        return self._open(f"{RAW}/{full_name}/{ref}/{path}", "*/*")
