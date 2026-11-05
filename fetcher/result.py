"""Result types of the fetcher. Expected failures are values, not exceptions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchOk:
    """Page text the app saw. `source` is "web" or "github"."""

    text: str
    source: str


@dataclass(frozen=True)
class FetchFail:
    """The page could not be read. `reason` is short and safe to show."""

    reason: str


FetchResult = FetchOk | FetchFail
