"""Save a link: fetch the page, summarise it, store it (F-01, F-02).

An unreadable or too-short page is saved as link only with a null summary.
The app never writes a summary of text it did not see (NF-04,
docs/solutions/honest-failure.md). All writes go through store.py.
"""

import logging
import re
from pathlib import Path
from typing import Literal, get_args
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
    type: Literal[
        "github_repo", "article", "video_page", "tool", "pdf", "image", "note"
    ]
    summary: str
    tags: list[str]
    reason: str


# Keep the Literal in step with store.TYPES (checked at import).
assert set(get_args(SaveOutput.model_fields["type"].annotation)) == store.TYPES

# 408 request timeout, 409 conflict, 529 overloaded, and every 5xx are transient.
_TRANSIENT_STATUS = {408, 409, 529}
_PAGE_TAG = re.compile(r"<(\s*/?\s*page\s*)>", re.IGNORECASE)


def _is_transient(err: anthropic.APIError) -> bool:
    if isinstance(err, anthropic.APIConnectionError | anthropic.RateLimitError):
        return True  # APITimeoutError is a subclass of APIConnectionError
    if isinstance(err, anthropic.APIStatusError):
        return err.status_code >= 500 or err.status_code in _TRANSIENT_STATUS
    return False


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
    """Ask Claude, with one retry. None means link only.

    Transient API errors and invalid output are retried once, then None.
    Permanent API errors (4xx other than 408/409/429) and a missing key
    propagate so a revoked key never looks like an unreadable page.
    """
    system = PROMPT_FILE.read_text(encoding="utf-8")
    # A literal <page> or </page> in the text must not close or open the wrapper.
    safe = _PAGE_TAG.sub(r"&lt;\1>", text)
    messages = [{"role": "user", "content": f"<page>\n{safe}\n</page>"}]
    for attempt in range(1, ATTEMPTS + 1):
        try:
            out = client.parse(messages, SaveOutput, system=system)
        except anthropic.APIError as err:
            if isinstance(err, anthropic.APIStatusError) and not _is_transient(err):
                raise
            reason = f"{type(err).__name__} status={getattr(err, 'status_code', None)}"
        except (client.InvalidOutput, ValidationError) as err:
            reason = type(err).__name__
        else:
            checked = _check(out)
            if checked is not None:
                return checked
            reason = "failed checks"
        if attempt < ATTEMPTS:
            _log.warning(
                "claude save attempt %s failed, retrying once: %s", attempt, reason
            )
        else:
            _log.warning("claude save failed twice, saving link only: %s", reason)
    return None


def _link_only(url: str, url_clean: str) -> tuple[dict, str | None]:
    host = urlsplit(url).hostname or url
    return {
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
    }, None


def save(url: str, pasted_text: str | None = None) -> dict:
    """Save a bookmark and return the stored record. See prepare for the rules."""
    fields, page_text = prepare(url, pasted_text)
    return store.add_bookmark(fields, page_text=page_text)


def prepare(url: str, pasted_text: str | None = None) -> tuple[dict, str | None]:
    """Read and summarise a link; return (record fields, page text). Writes nothing.

    pasted_text skips the fetcher and must reach MIN_TEXT_CHARS_PASTED (a
    one-character paste must not produce an invented summary). Without it, the
    page is fetched. If the page cannot be read, is too short, or Claude gives
    invalid output or a transient error twice, the link is saved with
    page_status unreadable and no summary. Permanent API errors and a missing
    key propagate (see _summarise).
    """
    url_clean = urlclean.clean_url(url)

    if pasted_text is not None:
        raw = pasted_text
        floor = config.MIN_TEXT_CHARS_PASTED
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

    # One string: the text Claude sees is the text that is stored.
    text = " ".join(raw.split())[: config.MAX_PAGE_CHARS]
    if not text or len(text) < floor:
        return _link_only(url, url_clean)

    out = _summarise(text)
    if out is None:
        return _link_only(url, url_clean)

    return {
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
    }, text
