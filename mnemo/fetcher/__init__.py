"""Fetcher: get the text of a page, or an honest failure."""

from mnemo.fetcher.github import fetch_repo, parse_repo
from mnemo.fetcher.page import fetch_page
from mnemo.fetcher.result import FetchFail, FetchOk, FetchResult

__all__ = ["FetchFail", "FetchOk", "FetchResult", "fetch", "fetch_page", "fetch_repo"]


def fetch(url: str) -> FetchResult:
    """Return FetchOk(text, source) or FetchFail(reason). Does not raise for expected failures.

    The text is not cut to MAX_PAGE_CHARS and not checked against the minimum
    length here: mnemo/save/pipeline.py does both.
    """
    repo = parse_repo(url)
    if repo:
        return fetch_repo(*repo)
    return fetch_page(url)
