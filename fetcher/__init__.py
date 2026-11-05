"""Fetcher: get the text of a page, or an honest failure."""

from fetcher.page import fetch_page
from fetcher.result import FetchFail, FetchOk, FetchResult

__all__ = ["FetchFail", "FetchOk", "FetchResult", "fetch", "fetch_page"]


def fetch(url: str) -> FetchResult:
    """Return FetchOk(text, source) or FetchFail(reason). Does not raise for expected failures.

    The text is not cut to MAX_PAGE_CHARS and not checked against the minimum
    length here: save.py does both.
    """
    return fetch_page(url)
