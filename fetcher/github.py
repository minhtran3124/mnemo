"""GitHub repo links: read the description and README through the official API.

The optional GITHUB_TOKEN is sent only to the API host, and redirects are not
followed, so it can never reach another host. A 403 or 429 is a rate limit:
no retry (PR-03).
"""

import json
import re
import time
from urllib.parse import urlsplit

import httpx2

import config
from fetcher import guard
from fetcher.page import AttemptError, check_status, new_client, read_capped, with_retry
from fetcher.result import FetchFail, FetchOk

_GITHUB_HOSTS = ("github.com", "www.github.com")
_NAME = r"[A-Za-z0-9_.-]+"
_REPO_PATH = re.compile(rf"^/({_NAME})/({_NAME})/?$")


def parse_repo(url: str) -> tuple[str, str] | None:
    """Return (owner, repo) for a plain github.com/owner/repo link, else None."""
    try:
        parts = urlsplit(url)
    except ValueError:
        return None
    if (
        parts.scheme not in ("http", "https")
        or (parts.hostname or "").lower() not in _GITHUB_HOSTS
    ):
        return None
    match = _REPO_PATH.match(parts.path)
    if not match:
        return None
    owner, repo = match.groups()
    repo = repo.removesuffix(".git")
    if not repo or repo in (".", "..") or owner in (".", ".."):
        return None
    return owner, repo


def _get(
    client: httpx2.Client,
    path: str,
    accept: str,
    started: float,
    *,
    optional: bool = False,
) -> bytes | None:
    url = f"{config.GITHUB_API_BASE}{path}"
    refused = guard.check_url(url) or guard.check_host(url)
    if refused:
        raise AttemptError(refused)
    headers = {"Accept": accept, "X-GitHub-Api-Version": "2022-11-28"}
    token = config.get_github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with client.stream("GET", url, headers=headers) as response:
        status = response.status_code
        if status in (403, 429):
            raise AttemptError("GitHub rate limit reached")
        if status == 404 and optional:
            return None
        if status == 404:
            raise AttemptError("repository not found")
        if 300 <= status < 400:
            raise AttemptError("repository moved")
        check_status(status)
        return read_capped(response, started)


def _attempt(owner: str, repo: str, transport: httpx2.BaseTransport | None) -> FetchOk:
    started = time.monotonic()
    base = f"/repos/{owner}/{repo}"
    with new_client(transport) as client:
        info = _get(client, base, "application/vnd.github+json", started)
        readme = _get(
            client,
            f"{base}/readme",
            "application/vnd.github.raw+json",
            started,
            optional=True,
        )
    try:
        description = (json.loads(info or b"{}").get("description") or "").strip()
    except (ValueError, AttributeError):
        raise AttemptError("GitHub answered with an unexpected response") from None
    readme_text = (readme or b"").decode("utf-8", errors="replace").strip()
    text = "\n\n".join(part for part in (description, readme_text) if part)
    if not text:
        raise AttemptError("no readable text found")
    return FetchOk(text=text, source="github")


def fetch_repo(
    owner: str, repo: str, transport: httpx2.BaseTransport | None = None
) -> FetchOk | FetchFail:
    """Fetch a repo's description and README through the API."""
    return with_retry(lambda: _attempt(owner, repo, transport))
