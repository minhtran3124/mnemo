"""Save a link: fetch the page, summarise it, store it (F-01, F-02).

An unreadable or too-short page is saved as link only with a null summary.
The app never writes a summary of text it did not see (NF-04,
docs/solutions/honest-failure.md). All writes go through store.py.
"""

import logging
from pathlib import Path
from urllib.parse import urlsplit

import anthropic
from pydantic import BaseModel, ValidationError

import client
import config
import fetcher
import store
import urlclean

PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "save_system.txt"
ATTEMPTS = 2

_log = logging.getLogger("mnemo.save")


class SaveOutput(BaseModel):
    """What Claude returns for one page."""

    title: str
    type: str
    summary: str
    tags: list[str]
    reason: str


def _check(out: SaveOutput) -> SaveOutput | None:
    """Return the output with lowercased, deduplicated tags if the code checks pass, else None."""
    tags = list(dict.fromkeys(t.strip().lower() for t in out.tags if t.strip()))
    if not store.MIN_TAGS <= len(tags) <= store.MAX_TAGS:
        return None
    if not out.summary.strip() or len(out.summary.split()) > store.MAX_SUMMARY_WORDS:
        return None
    if out.type not in store.TYPES or not out.title.strip():
        return None
    return out.model_copy(update={"tags": tags})


def _summarise(text: str) -> SaveOutput | None:
    """Ask Claude, with one retry. None means link only."""
    system = PROMPT_FILE.read_text(encoding="utf-8")
    messages = [
        {
            "role": "user",
            "content": f"<page>\n{text[: config.MAX_PAGE_CHARS]}\n</page>",
        }
    ]
    for _ in range(ATTEMPTS):
        try:
            out = client.parse(messages, SaveOutput, system=system)
        except anthropic.APIError as err:
            _log.warning(
                "claude call failed, will retry or save link only: %s",
                type(err).__name__,
            )
            continue
        except (RuntimeError, ValidationError):
            continue
        checked = _check(out)
        if checked is not None:
            return checked
    return None


def _link_only(url: str, url_clean: str) -> dict:
    host = urlsplit(url).hostname or url
    return store.add_bookmark(
        {
            "url": url,
            "url_clean": url_clean,
            "type": "article",
            "title": host,
            "page_status": "unreadable",
            "summary": None,
            "tags": [],
            "reason": "",
            "reason_source": "guess",
            "folder": None,
            "opened_count": 0,
        },
        page_text=None,
    )


def save(url: str, pasted_text: str | None = None) -> dict:
    """Save a bookmark and return the stored record.

    pasted_text skips the fetcher and uses the shortest floor (a one-character
    paste must not produce an invented summary). Without it, the page is
    fetched. If the page cannot be read, is too short, or Claude gives invalid
    output twice, the link is saved with page_status unreadable and no summary.
    """
    url_clean = urlclean.clean_url(url)

    if pasted_text is not None:
        raw = pasted_text
        floor = config.MIN_TEXT_CHARS_GITHUB
    else:
        result = fetcher.fetch(url)
        if isinstance(result, fetcher.FetchFail):
            return _link_only(url, url_clean)
        raw = result.text
        floor = (
            config.MIN_TEXT_CHARS_GITHUB
            if result.source == "github"
            else config.MIN_TEXT_CHARS_HTML
        )

    text = " ".join(raw.split())
    if not text or len(text) < floor:
        return _link_only(url, url_clean)

    out = _summarise(text)
    if out is None:
        return _link_only(url, url_clean)

    return store.add_bookmark(
        {
            "url": url,
            "url_clean": url_clean,
            "type": out.type,
            "title": out.title.strip(),
            "page_status": "ok",
            "summary": out.summary.strip(),
            "tags": out.tags,
            "reason": out.reason.strip(),
            "reason_source": "guess",
            "folder": None,
            "opened_count": 0,
        },
        page_text=raw.strip()[: config.MAX_PAGE_CHARS],
    )
