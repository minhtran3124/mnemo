"""Save a link: fetch the page, summarise it, store it (F-01, F-02).

An unreadable or too-short page is saved as link only with a null summary.
The app never writes a summary of text it did not see (NF-04,
docs/solutions/honest-failure.md). All writes go through store.py.
"""

import contextlib
import logging
import re
from pathlib import Path
from typing import Literal, get_args
from urllib.parse import urlsplit

import anthropic
from pydantic import BaseModel, ValidationError

from mnemo import fetcher
from mnemo.core import client, config, store, urlclean

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def prompt_file(version: str | None = None) -> Path:
    """The prompt file for one version, or the default from config.py."""
    return PROMPTS_DIR / f"{version or config.SAVE_PROMPT_VERSION}.txt"


PROMPT_FILE = prompt_file()
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
    folder: str = config.UNSORTED


# Keep the Literal in step with store.TYPES (checked at import).
assert set(get_args(SaveOutput.model_fields["type"].annotation)) == store.TYPES

# 408 request timeout, 409 conflict, 529 overloaded, and every 5xx are transient.
_TRANSIENT_STATUS = {408, 409, 529}
_PAGE_TAG = re.compile(r"<(\s*/?\s*page\s*)>", re.IGNORECASE)


def normalise_text(raw: str) -> str:
    """The one rule for page text: collapse whitespace, cap at MAX_PAGE_CHARS.

    The text Claude sees is the text that is stored, so every path uses this.
    """
    return " ".join(raw.split())[: config.MAX_PAGE_CHARS]


def _is_transient(err: anthropic.APIError) -> bool:
    if isinstance(err, anthropic.APIConnectionError | anthropic.RateLimitError):
        return True  # APITimeoutError is a subclass of APIConnectionError
    if isinstance(err, anthropic.APIStatusError):
        return err.status_code >= 500 or err.status_code in _TRANSIENT_STATUS
    return False


def is_permanent_error(err: BaseException) -> bool:
    """True for auth and config errors: a missing key or a non-transient 4xx from Claude.

    These are never a problem with one link, so callers must not hide them.
    """
    if isinstance(err, client.MissingKey):
        return True
    return isinstance(err, anthropic.APIStatusError) and not _is_transient(err)


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


def resolve_folder(name: str) -> tuple[str | None, str | None]:
    """Return (stored folder, rejected name).

    A starter folder is stored as its name; Unsorted is stored as null. Any
    other name is rejected by code and the bookmark goes to Unsorted, so the
    rejected name is returned for the log (FO-03, D-005).
    """
    if name == config.UNSORTED:
        return None, None
    if config.is_allowed_folder(name):
        return name, None
    return None, name


def _summarise(text: str, prompt_version: str | None = None) -> SaveOutput | None:
    """Ask Claude, with one retry. None means link only.

    Transient API errors and invalid output are retried once, then None.
    Permanent API errors (4xx other than 408/409/429) and a missing key
    propagate so a revoked key never looks like an unreadable page.
    """
    system = prompt_file(prompt_version).read_text(encoding="utf-8")
    # A literal <page> or </page> in the text must not close or open the wrapper.
    safe = _PAGE_TAG.sub(r"&lt;\1>", text)
    messages = [{"role": "user", "content": f"<page>\n{safe}\n</page>"}]
    for attempt in range(1, ATTEMPTS + 1):
        try:
            out = client.parse(messages, SaveOutput, system=system)
        except anthropic.APIError as err:
            if is_permanent_error(err):
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


def _link_only_fields(url: str, url_clean: str, private: bool = False) -> dict:
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
        "prev_folder": None,
        "private": private,
        "opened_count": 0,
    }


def _ok_fields(
    url: str, url_clean: str, out: SaveOutput, folder: str | None = None
) -> dict:
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
        "folder": folder,
        "prev_folder": config.UNSORTED if folder is not None else None,
        "private": False,
        "opened_count": 0,
    }


def _link_only(url: str, url_clean: str, private: bool = False) -> dict:
    return store.add_bookmark(
        _link_only_fields(url, url_clean, private), page_text=None
    )


def _floor_for(source: str) -> int:
    if source == "pasted":
        return config.MIN_TEXT_CHARS_PASTED
    if source == "github":
        return config.MIN_TEXT_CHARS_GITHUB
    return config.MIN_TEXT_CHARS_HTML


def preview(
    url: str,
    text: str | None,
    folder_choice: list[str | None] | None = None,
    prompt_version: str | None = None,
) -> dict:
    """Return the record fields save() would store for this text, writing nothing.

    Runs the same floor check, Claude call (one retry) and code checks as
    save(). text=None, or text under the floor, gives the link-only fields.
    The text floor follows the fetcher: the GitHub floor for a URL that
    fetcher.parse_repo reads as a repo, else the HTML floor.
    Permanent API errors and a missing key propagate (see _summarise).

    `folder_choice` is an optional one-item sink for the eval: it receives the
    folder name the model returned, before code resolves or rejects it, so a
    made-up name can be scored as a miss.
    """
    url_clean = urlclean.clean_url(url)
    if text is None:
        if folder_choice is not None:
            folder_choice.append(None)
        return _link_only_fields(url, url_clean)
    floor = _floor_for("github" if fetcher.parse_repo(url) else "web")
    norm = normalise_text(text)
    if not norm or len(norm) < floor:
        if folder_choice is not None:
            folder_choice.append(None)
        return _link_only_fields(url, url_clean)
    out = _summarise(norm, prompt_version)
    if out is None:
        if folder_choice is not None:
            folder_choice.append(None)
        return _link_only_fields(url, url_clean)
    if folder_choice is not None:
        folder_choice.append(out.folder)
    folder, _ = resolve_folder(out.folder)
    return _ok_fields(url, url_clean, out, folder)


def save(
    url: str,
    pasted_text: str | None = None,
    private: bool = False,
    prompt_version: str | None = None,
) -> dict:
    """Save a bookmark and return the stored record.

    A private link is saved as link only before any fetch or Claude call, so
    nothing about its page leaves the machine (F-19, D-017).

    pasted_text skips the fetcher and must reach MIN_TEXT_CHARS_PASTED (a
    one-character paste must not produce an invented summary). Without it, the
    page is fetched. If the page cannot be read, is too short, or Claude gives
    invalid output or a transient error twice, the link is saved with
    page_status unreadable and no summary. Permanent API errors and a missing
    key propagate (see _summarise).
    """
    url_clean = urlclean.clean_url(url)
    if private:
        return _link_only(url, url_clean, private=True)

    if pasted_text is not None:
        raw = pasted_text
        floor = _floor_for("pasted")
    else:
        result = fetcher.fetch(url)
        if isinstance(result, fetcher.FetchFail):
            return _link_only(url, url_clean)
        raw = result.text
        floor = _floor_for(result.source)

    text = normalise_text(raw)
    if not text or len(text) < floor:
        return _link_only(url, url_clean)

    out = _summarise(text, prompt_version)
    if out is None:
        return _link_only(url, url_clean)

    folder, rejected = resolve_folder(out.folder)
    record = store.add_bookmark(_ok_fields(url, url_clean, out, folder), page_text=text)
    if rejected is not None:
        store.log_event(
            {
                "event": "folder_rejected",
                "id": record["id"],
                "url_clean": url_clean,
                "folder": rejected,
            }
        )
    return record


class FillInError(Exception):
    """A fill-in was refused. `code` is the API error code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def fill_in(bookmark_id: int, pasted_text: str, write_lock=None) -> dict:
    """Fill in an unreadable bookmark from pasted text and return the record.

    The same bookmark is updated: id, saved_at, opened_count, folder and a
    user-written reason are kept. The Claude call runs first and outside
    write_lock; only the store update runs inside it. Raises store.NotFound
    (unknown id) or FillInError: already_read, text_too_short, summary_failed.
    Permanent API errors and a missing key propagate (see _summarise).
    """
    lock = write_lock if write_lock is not None else contextlib.nullcontext()
    current = store.get_bookmark(bookmark_id)
    if current is None:
        raise store.NotFound(f"no bookmark with id {bookmark_id}")
    if current["page_status"] != "unreadable":
        raise FillInError("already_read", "This page was already read.")

    text = normalise_text(pasted_text)
    if len(text) < config.MIN_TEXT_CHARS_PASTED:
        raise FillInError("text_too_short", "The pasted text is too short.")

    out = _summarise(text)
    if out is None:
        raise FillInError("summary_failed", "Could not summarise the pasted text.")

    with lock:
        # Re-check: another request may have changed the bookmark meanwhile.
        current = store.get_bookmark(bookmark_id)
        if current is None:
            raise store.NotFound(f"no bookmark with id {bookmark_id}")
        if current["page_status"] != "unreadable":
            raise FillInError("already_read", "This page was already read.")
        fields = {
            "type": out.type,
            "title": out.title.strip(),
            "page_status": "ok",
            "summary": out.summary.strip(),
            "tags": out.tags,
        }
        if current["reason_source"] != "user":
            fields["reason"] = out.reason.strip()
            fields["reason_source"] = "guess"
        return store.update_bookmark_with_page(bookmark_id, fields, text)
