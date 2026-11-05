"""GitHub repo links: read the description and README through the official API.

The optional GITHUB_TOKEN is sent only to the API host, and redirects are not
followed, so it can never reach another host. A 429, or a 403 that GitHub marks
as exhausted (X-RateLimit-Remaining: 0 or Retry-After), is a rate limit: no
retry (PR-03). Any other 403 is reported as a refusal, not a guessed reason.
"""

import json
import logging
import re
import time
from urllib.parse import urlsplit

import httpx2

import config
from fetcher import guard
from fetcher.page import AttemptError, check_status, new_client, read_capped, with_retry
from fetcher.result import FetchFail, FetchOk

_log = logging.getLogger("mnemo.fetcher")
_GITHUB_HOSTS = ("github.com", "www.github.com")
_NAME = r"[A-Za-z0-9_.-]+"
# First path segments GitHub uses for its own pages, never a repo owner.
_RESERVED_OWNERS = frozenset(
    {
        "orgs",
        "topics",
        "settings",
        "sponsors",
        "marketplace",
        "features",
        "about",
        "pricing",
        "explore",
        "collections",
        "trending",
        "search",
        "login",
        "join",
        "notifications",
        "issues",
        "pulls",
        "new",
        "apps",
        "enterprise",
        "events",
        "readme",
        "security",
        "codespaces",
        "customer-stories",
        "organizations",
        "users",
        "site",
        "contact",
        "account",
        "dashboard",
    }
)
_RATE_LIMIT_REASON = "GitHub rate limit reached"
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
    if owner.lower() in _RESERVED_OWNERS:
        return None
    if not repo or repo in (".", "..") or owner in (".", ".."):
        return None
    return owner, repo


def _is_rate_limited(response: httpx2.Response) -> bool:
    """True only when GitHub's own headers say the limit is used up."""
    return (
        response.headers.get("X-RateLimit-Remaining") == "0"
        or "Retry-After" in response.headers
    )


def _get(
    client: httpx2.Client,
    path: str,
    accept: str,
    started: float,
    *,
    optional: bool = False,
    truncate: bool = False,
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
        if status == 429 or (status == 403 and _is_rate_limited(response)):
            raise AttemptError(_RATE_LIMIT_REASON)
        if status == 403:
            raise AttemptError("GitHub refused access (403)")
        if status == 404 and optional:
            return None
        if status == 404:
            raise AttemptError("repository not found")
        if 300 <= status < 400:
            raise AttemptError("repository moved")
        check_status(status)
        if truncate:
            return _read_truncated(response, started)
        return read_capped(response, started)


def _read_truncated(response: httpx2.Response, started: float) -> bytes:
    """Read the body up to the byte cap and drop the rest (no 'too large' error)."""
    cap = config.FETCH_MAX_BYTES
    chunks: list[bytes] = []
    size = 0
    for chunk in response.iter_bytes():
        chunks.append(chunk[: cap - size])
        size += len(chunk)
        if size >= cap:
            break
        if time.monotonic() - started > config.FETCH_ATTEMPT_SECONDS:
            raise AttemptError("the page took too long", transient=True)
    return b"".join(chunks)


def _get_readme(client: httpx2.Client, base: str) -> bytes | None:
    """Fetch the README, retrying only this call once on a transient error."""
    for number in (1, 2):
        try:
            return _get(
                client,
                f"{base}/readme",
                "application/vnd.github.raw+json",
                time.monotonic(),
                optional=True,
                truncate=True,
            )
        except (AttemptError, httpx2.TransportError) as err:
            if isinstance(err, httpx2.TimeoutException):
                err = AttemptError("the page timed out", transient=True)
            elif isinstance(err, httpx2.TransportError):
                err = AttemptError("could not connect to the page", transient=True)
            if err.transient and number == 1:
                _log.info("transient README error, retrying: %s", err.reason)
                time.sleep(config.FETCH_RETRY_DELAY)
                continue
            # Not transient any more: with_retry must not repeat the /repos call.
            raise AttemptError(err.reason) from None
    raise AssertionError("unreachable")


def _attempt(owner: str, repo: str, transport: httpx2.BaseTransport | None) -> FetchOk:
    started = time.monotonic()
    base = f"/repos/{owner}/{repo}"
    with new_client(transport) as client:
        info = _get(client, base, "application/vnd.github+json", started)
        try:
            description = (json.loads(info or b"{}").get("description") or "").strip()
        except (ValueError, AttributeError):
            raise AttemptError("GitHub answered with an unexpected response") from None
        # A repo with no README is a 404 and gives None. A README over the
        # byte cap is cut at the cap. Any other README failure (moved, 4xx,
        # 5xx or timeout after one retry, bad token, rate limit) stands, so it
        # is never mistaken for a repo with no README.
        readme = _get_readme(client, base)
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
