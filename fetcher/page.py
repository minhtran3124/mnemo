"""Plain page fetch: guarded streamed GET, manual redirects, one retry.

Redirects are followed by hand (follow_redirects=False) so the scheme and
address checks run on every hop. Known gap: DNS could change between the
address check and the connection (DNS rebinding). Accepted for phase 1, a
local single-user app; see docs/feature-specs/page-reading.md.
"""

import logging
import time
from collections.abc import Callable
from urllib.parse import urljoin

import httpx2
import trafilatura

import config
from fetcher import guard
from fetcher.result import FetchFail, FetchOk

_log = logging.getLogger("mnemo.fetcher")

REDIRECT_STATUSES = (301, 302, 303, 307, 308)


class AttemptError(Exception):
    """One attempt failed. `transient` says whether a retry is allowed (PR-03)."""

    def __init__(self, reason: str, transient: bool = False) -> None:
        super().__init__(reason)
        self.reason = reason
        self.transient = transient


def new_client(transport: httpx2.BaseTransport | None = None) -> httpx2.Client:
    """A fresh client: no env proxy, no cookies kept, no automatic redirects."""
    return httpx2.Client(
        transport=transport,
        trust_env=False,
        follow_redirects=False,
        timeout=httpx2.Timeout(
            connect=config.FETCH_CONNECT_TIMEOUT,
            read=config.FETCH_READ_TIMEOUT,
            write=config.FETCH_WRITE_TIMEOUT,
            pool=config.FETCH_POOL_TIMEOUT,
        ),
        headers={"User-Agent": config.USER_AGENT},
    )


def read_capped(response: httpx2.Response, started: float) -> bytes:
    """Read the body, stopping at the byte cap and the per-attempt time cap."""
    declared = response.headers.get("content-length", "")
    if declared.isdigit() and int(declared) > config.FETCH_MAX_BYTES:
        raise AttemptError("page is too large")
    chunks: list[bytes] = []
    size = 0
    for chunk in response.iter_bytes():
        size += len(chunk)
        if size > config.FETCH_MAX_BYTES:
            raise AttemptError("page is too large")
        if time.monotonic() - started > config.FETCH_ATTEMPT_SECONDS:
            raise AttemptError("the page took too long", transient=True)
        chunks.append(chunk)
    return b"".join(chunks)


def check_status(status: int) -> None:
    """Raise for a non-success status. 5xx is transient; 4xx and 429 are not."""
    if status in (500, 502, 503, 504):
        raise AttemptError(f"server error {status}", transient=True)
    if status == 429:
        raise AttemptError("too many requests")
    if status >= 400:
        raise AttemptError(f"server answered {status}")


def with_retry(attempt: Callable[[], FetchOk]) -> FetchOk | FetchFail:
    """Run an attempt; retry once after a delay if it fails with a transient error."""
    for number in (1, 2):
        try:
            return attempt()
        except AttemptError as err:
            if err.transient and number == 1:
                _log.info("transient fetch error, retrying: %s", err.reason)
                time.sleep(config.FETCH_RETRY_DELAY)
                continue
            return FetchFail(err.reason)
        except httpx2.TimeoutException:
            error = AttemptError("the page timed out", transient=True)
        except httpx2.TransportError:
            error = AttemptError("could not connect to the page", transient=True)
        except httpx2.HTTPError:
            return FetchFail("the request failed")
        if number == 1:
            _log.info("transient fetch error, retrying: %s", error.reason)
            time.sleep(config.FETCH_RETRY_DELAY)
            continue
        return FetchFail(error.reason)
    return FetchFail("the request failed")  # unreachable; keeps the type checker calm


def _is_text_type(content_type: str) -> bool:
    media = content_type.split(";", 1)[0].strip().lower()
    return media in config.FETCH_CONTENT_TYPES


def _attempt(url: str, transport: httpx2.BaseTransport | None) -> FetchOk:
    started = time.monotonic()
    with new_client(transport) as client:
        current = url
        for hop in range(config.FETCH_MAX_REDIRECTS + 1):
            refused = guard.check_url(current) or guard.check_host(current)
            if refused:
                raise AttemptError(refused)
            with client.stream("GET", current) as response:
                if response.status_code in REDIRECT_STATUSES:
                    location = response.headers.get("location")
                    if not location:
                        raise AttemptError("redirect without a target")
                    if hop == config.FETCH_MAX_REDIRECTS:
                        raise AttemptError("too many redirects")
                    current = urljoin(current, location)
                    continue
                check_status(response.status_code)
                content_type = response.headers.get("content-type", "")
                if not _is_text_type(content_type):
                    raise AttemptError("not a web page")
                body = read_capped(response, started)
                break
        else:  # pragma: no cover - the loop always breaks or raises
            raise AttemptError("too many redirects")
    if content_type.split(";", 1)[0].strip().lower() == "text/plain":
        text = body.decode("utf-8", errors="replace")
    else:
        text = trafilatura.extract(body) or ""
    text = text.strip()
    if not text:
        raise AttemptError("no readable text found")
    return FetchOk(text=text, source="web")


def fetch_page(
    url: str, transport: httpx2.BaseTransport | None = None
) -> FetchOk | FetchFail:
    """Fetch a plain page and return its text, or a failure. Never raises for expected failures."""
    return with_retry(lambda: _attempt(url, transport))
