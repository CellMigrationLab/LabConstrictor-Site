"""A small GitHub API client that never hides a failure.

A missing repository, file or release is a NotFound (a problem with one app). Anything else that goes
wrong (network, rate limit, server error, an answer that is too big or not JSON, a redirect to another
host) is a FetchError that stops the whole fetch.
"""

import json
import os
from email.message import Message
from typing import IO
import urllib.error
import urllib.request
from urllib.parse import urlsplit

from .config import AppProblem, FetchError

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
TIMEOUT = 30
MAX_JSON, MAX_TEXT, MAX_FILE = 5 * 2**20, 100 * 2**10, 8 * 2**20   # largest answers read, in bytes


class NotFound(AppProblem):
    """GitHub answered 404: the repository, file or release does not exist (or is private)."""


class SameHostRedirects(urllib.request.HTTPRedirectHandler):
    """Refuse a redirect to another host, so the token and requests never leave GitHub's own hosts."""

    def redirect_request(self, req: urllib.request.Request, fp: IO[bytes], code: int, msg: str,
                         headers: Message, newurl: str) -> urllib.request.Request | None:
        """Follow the redirect only when it stays on the same host; raise FetchError otherwise."""
        if urlsplit(newurl).hostname != urlsplit(req.full_url).hostname:
            raise FetchError(f"GET {req.full_url} redirected to another host: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(SameHostRedirects)


class GitHub:
    """Reads public repositories. GITHUB_TOKEN (optional) raises the rate limit; it is never printed."""

    def __init__(self, token: str | None = None) -> None:
        """Use `token` or, when None, the GITHUB_TOKEN environment variable (which may be unset)."""
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN")

    def _open(self, url: str, accept: str, limit: int) -> bytes:
        """GET a URL and return at most `limit` bytes. Raises NotFound on 404, AppProblem when the answer is
        larger than `limit`, and FetchError on every other failure (with a rate-limit hint)."""
        headers = {"Accept": accept, "User-Agent": "labconstrictor-site"}
        if self.token and url.startswith(API):
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            with OPENER.open(urllib.request.Request(url, headers=headers), timeout=TIMEOUT) as response:
                data = response.read(limit + 1)
        except urllib.error.HTTPError as err:
            if err.code == 404:
                raise NotFound(f"GET {url}: not found (missing, or the repository is private)") from err
            hint = " (rate limited? set GITHUB_TOKEN)" if err.code in (403, 429) else ""
            raise FetchError(f"GET {url} failed: HTTP {err.code}{hint}") from err
        except (urllib.error.URLError, TimeoutError) as err:
            raise FetchError(f"GET {url} failed: {err}") from err
        if len(data) > limit:
            raise AppProblem(f"GET {url}: answer is larger than {limit // 1024} KB")
        return data

    def json(self, path: str) -> dict:
        """GET an API path ("/repos/o/r") and parse the JSON object. Raises FetchError for anything but a JSON object."""
        data = self._open(API + path, "application/vnd.github+json", MAX_JSON)
        try:
            parsed = json.loads(data)
        except ValueError as err:
            raise FetchError(f"GET {API + path}: the answer is not JSON") from err
        if not isinstance(parsed, dict):
            raise FetchError(f"GET {API + path}: expected a JSON object")
        return parsed

    def repo(self, full_name: str) -> dict:
        """Repository metadata (id, owner id, default branch, archived flag, license)."""
        return self.json(f"/repos/{full_name}")

    def latest_release(self, full_name: str) -> dict | None:
        """The latest published release (not a draft or pre-release), or None when the repository has no release."""
        try:
            return self.json(f"/repos/{full_name}/releases/latest")
        except NotFound:
            return None

    def raw(self, full_name: str, ref: str, path: str, limit: int = MAX_TEXT) -> bytes:
        """A file from the repository at a branch or tag, at most `limit` bytes (larger files raise AppProblem)."""
        return self._open(f"{RAW}/{full_name}/{ref}/{path}", "*/*", limit)
