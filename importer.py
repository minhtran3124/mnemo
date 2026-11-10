"""Find links in a browser bookmark export and in pasted text (F-06, IM-01 to IM-03).

Plain code, no Claude call and no network. See docs/feature-specs/import.md.
"""

from html.parser import HTMLParser
from urllib.parse import urlsplit

import intent
from urlclean import clean_url


class _BookmarkParser(HTMLParser):
    """Collect the href of every anchor in a Netscape bookmarks file."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.links.append(value)
                break


def _is_web(link: str) -> bool:
    """True for an http(s) link with a host; rejects about:, javascript:, file:."""
    try:
        parts = urlsplit(link)
    except ValueError:
        return False
    return parts.scheme.lower() in {"http", "https"} and bool(parts.hostname)


def _is_slack_archive(link: str) -> bool:
    try:
        parts = urlsplit(link)
    except ValueError:
        return False
    host = (parts.hostname or "").lower()
    return host.endswith(".slack.com") and parts.path.startswith("/archives/")


def _collect(links: list[str]) -> list[dict]:
    """Clean, reject non-web links and deduplicate on the cleaned link, in order."""
    found: list[dict] = []
    seen: set[str] = set()
    for link in links:
        cleaned = clean_url(link)
        if cleaned in seen or not _is_web(cleaned):
            continue
        seen.add(cleaned)
        found.append(
            {"url": link, "url_clean": cleaned, "slack": _is_slack_archive(cleaned)}
        )
    return found


def _text(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("input must be a string")  # noqa: TRY004 - ticket asks for ValueError
    return value


def links_from_browser_export(html: str) -> list[dict]:
    """Return the web links in a Netscape bookmarks HTML export."""
    parser = _BookmarkParser()
    parser.feed(_text(html))
    return _collect(parser.links)


def links_from_text(text: str) -> list[dict]:
    """Return the web links in pasted text such as a Slack message or notes."""
    return _collect(intent.find_links(_text(text)))
