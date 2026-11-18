"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

import html
import logging
import re
import threading
from pathlib import Path
from urllib.parse import urlparse, urlsplit

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from mnemo.chat import ask, importer, intent
from mnemo.core import config, store, urlclean
from mnemo.save import pipeline as save

# Only this computer can reach the server (NF-01, D-021).
HOST = "127.0.0.1"

# Found from this file, so it works from any working directory.
WEB_DIR = Path(__file__).resolve().parent / "web"

# Host names the server answers to. A DNS-rebinding page reaches the loopback
# server under its own name, so any other Host is refused. "testserver" is the
# name Starlette's test client sends; a browser cannot reach us under it.
ALLOWED_HOSTS = frozenset({"127.0.0.1", "localhost", "[::1]", "testserver"})
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})

app = FastAPI()

_log = logging.getLogger("mnemo.server")

# Only these folders are public. Pages and partials hold unrendered
# placeholders, so they are never served as files.
for _folder in ("css", "js", "fonts"):
    app.mount(
        f"/static/{_folder}",
        StaticFiles(directory=WEB_DIR / _folder),
        name=f"static-{_folder}",
    )


def render_page(name: str) -> str:
    """Read a page from mnemo/api/web/ and put the shared header where it says <!--HEADER-->."""
    header = (WEB_DIR / "partials" / "header.html").read_text(encoding="utf-8")
    page = (WEB_DIR / name).read_text(encoding="utf-8")
    return page.replace("<!--HEADER-->", header)


@app.get("/", response_class=HTMLResponse)
def chat_page() -> str:
    return render_page("index.html")


@app.get("/settings", response_class=HTMLResponse)
def settings() -> str:
    return render_page("settings.html")


# Groups on the Bookmark page, in a fixed order. Empty groups are skipped.
TYPE_ORDER = ("github_repo", "article", "video_page", "tool", "pdf", "image", "note")
TYPE_LABELS = {
    "github_repo": "GitHub repos",
    "article": "Articles",
    "video_page": "Videos",
    "tool": "Tools",
    "pdf": "PDFs",
    "image": "Images",
    "note": "Notes",
}


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _folder_name(item: dict) -> str:
    """The folder to show. A null folder is Unsorted."""
    return item.get("folder") or config.UNSORTED


def _folder_options(selected: str) -> str:
    names = (*config.STARTER_FOLDERS, config.UNSORTED)
    return "".join(
        f'<option value="{_esc(name)}"'
        + (" selected" if name == selected else "")
        + f">{_esc(name)}</option>"
        for name in names
    )


def _bookmark_row(item: dict) -> str:
    title = item.get("title") or item["url"]
    host = urlparse(item["url"]).hostname or ""
    unreadable = item.get("page_status") == "unreadable"
    bid = int(item["id"])
    folder = _folder_name(item)
    parts = [
        f'<li class="bm-row" data-id="{bid}"'
        + (' data-unreadable="true"' if unreadable else "")
        + ">",
        '<div class="bm-main">',
        (
            f'<a class="bm-title" href="{_esc(item["url"])}" target="_blank" '
            f'rel="noopener noreferrer" data-open-url="/api/bookmarks/{bid}/open">'
            f"{_esc(title)}</a>"
        ),
        (
            f'<p class="bm-meta"><span>{_esc(item.get("type", ""))}</span> '
            f"<span>{_esc(host)}</span> "
            f"<span>{_esc(str(item.get('saved_at') or '')[:10])}</span></p>"
        ),
        f'<p class="bm-filed">Filed in: <strong>{_esc(folder)}</strong></p>',
    ]
    if unreadable:
        parts.append('<p><span class="badge badge-warn">page not read</span></p>')
    elif item.get("summary"):
        parts.append(f'<p class="bm-summary">{_esc(item["summary"])}</p>')
    if item.get("reason"):
        flag = ""
        if item.get("reason_source") == "guess":
            flag = ' <span class="badge">guess</span>'
        parts.append(f'<p class="bm-reason">{_esc(item["reason"])}{flag}</p>')
    raw_tags = item.get("tags")
    if isinstance(raw_tags, list) and raw_tags:
        tags = "".join(f"<li>{_esc(tag)}</li>" for tag in raw_tags)
        parts.append(f'<ul class="bm-tags" aria-label="Tags">{tags}</ul>')
    parts.append("</div>")
    undo = ""
    if item.get("prev_folder") is not None:
        undo = (
            f'<button type="button" class="bm-undo" '
            f'data-undo-url="/api/bookmarks/{bid}/undo">Undo</button>'
        )
    parts.append(
        '<div class="bm-actions">'
        f'<label class="visually-hidden" for="bm-move-{bid}">Move to folder</label>'
        f'<select class="bm-move-select" id="bm-move-{bid}">'
        f"{_folder_options(folder)}</select>"
        f'<button type="button" class="bm-move" '
        f'data-move-url="/api/bookmarks/{bid}">Move</button>'
        f"{undo}"
        f'<button type="button" class="bm-delete" '
        f'data-delete-url="/api/bookmarks/{bid}" '
        f'data-confirm="{_esc(f"Delete {title}? This cannot be undone.")}">Delete</button>'
        "</div>"
    )
    parts.append("</li>")
    return "".join(parts)


def _empty_message(hidden: bool) -> str:
    return (
        f'<p class="empty" id="bm-empty"{" hidden" if hidden else ""}>'
        "Nothing saved yet. Paste a link in the chat to save your first bookmark.</p>"
    )


def _bookmark_groups(items: list[dict]) -> str:
    if not items:
        return _empty_message(hidden=False)
    sections: list[str] = []
    known = set(TYPE_ORDER)
    # A record with a type outside TYPE_ORDER (hand-edited data) must still show.
    groups = [(kind, TYPE_LABELS[kind], kind) for kind in TYPE_ORDER]
    groups.append(("other", "Other", None))
    for kind, label, match in groups:
        if match is None:
            rows = [item for item in items if item.get("type") not in known]
        else:
            rows = [item for item in items if item.get("type") == match]
        if not rows:
            continue
        sections.append(
            f'<section class="bm-group" data-type="{kind}">'
            f'<h2>{label} <span class="count">{len(rows)}</span></h2>'
            f'<ul class="bm-list">{"".join(_bookmark_row(r) for r in rows)}</ul>'
            "</section>"
        )
    # Hidden until the page script removes the last row after a delete.
    sections.append(_empty_message(hidden=True))
    return "".join(sections)


@app.get("/bookmarks", response_class=HTMLResponse)
def bookmarks_page() -> str:
    items = store.list_bookmarks()
    banner = ""
    if any(item.get("page_status") == "unreadable" for item in items):
        banner = (
            '<p class="banner" id="bm-banner" role="note"><strong>Needs a look.</strong> '
            "Some pages could not be read. They are saved as links only.</p>"
        )
    page = render_page("bookmarks.html")
    return page.replace("<!--BANNER-->", banner).replace(
        "<!--BOOKMARKS-->", _bookmark_groups(items)
    )


# Sync routes run in a threadpool. This lock makes each read-modify-write on
# bookmarks.json one step, so two requests cannot lose an update.
_write_lock = threading.Lock()


def error_response(
    status: int, code: str, message: str, headers: dict[str, str] | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message}},
        headers=headers,
    )


def _not_found(bookmark_id: int) -> JSONResponse:
    return error_response(404, "bookmark_not_found", "No bookmark with that id.")


def _host_name(netloc: str) -> str:
    """The host part of a Host header or URL netloc, lower case, without the port."""
    host = netloc.rsplit("@", 1)[-1].lower()
    if host.startswith("["):
        return host.split("]", 1)[0] + "]"
    return host.split(":", 1)[0]


@app.middleware("http")
async def check_host_and_origin(request: Request, call_next):
    host = _host_name(request.headers.get("host", ""))
    if host not in ALLOWED_HOSTS:
        return error_response(403, "forbidden_host", "This host is not allowed.")
    origin = request.headers.get("origin")
    if request.method not in _SAFE_METHODS and origin is not None:
        origin_host = _host_name(urlsplit(origin).netloc)
        if origin_host not in ALLOWED_HOSTS:
            return error_response(
                403, "forbidden_origin", "This origin is not allowed."
            )
    return await call_next(request)


@app.exception_handler(StarletteHTTPException)
async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Keep exc.headers: a 405 must carry Allow (RFC 9110).
    if exc.status_code == 404:
        return error_response(404, "not_found", "Not found.", exc.headers)
    code = f"http_{exc.status_code}"
    return error_response(exc.status_code, code, str(exc.detail), exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(400, "bad_request", "The request is not valid.")


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    # The cause goes to the server log only, so it survives outside uvicorn.
    _log.error(
        "Unhandled error on %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    # Never echo the exception text: it can hold file paths or page content.
    return error_response(500, "server_error", "Something went wrong on the server.")


@app.get("/api/bookmarks")
def list_bookmarks() -> list[dict]:
    return store.list_bookmarks()


@app.post("/api/bookmarks/{bookmark_id}/open", response_model=None)
def open_bookmark(bookmark_id: int) -> dict | JSONResponse:
    with _write_lock:
        item = store.get_bookmark(bookmark_id)
        if item is None:
            return _not_found(bookmark_id)
        updated = store.update_bookmark(
            bookmark_id, {"opened_count": item["opened_count"] + 1}
        )
    store.log_event({"event": "open", "id": bookmark_id})
    return updated


@app.delete("/api/bookmarks/{bookmark_id}", response_model=None)
def delete_bookmark(bookmark_id: int) -> dict | JSONResponse:
    with _write_lock:
        try:
            store.delete_bookmark(bookmark_id)
        except store.NotFound:
            return _not_found(bookmark_id)
    return {"deleted": bookmark_id}


class PasteBody(BaseModel):
    text: str


@app.post("/api/bookmarks/{bookmark_id}/paste", response_model=None)
def paste_bookmark(bookmark_id: int, body: PasteBody) -> dict | JSONResponse:
    # The Claude call runs outside the lock; save.fill_in takes it for the write.
    try:
        return save.fill_in(bookmark_id, body.text, write_lock=_write_lock)
    except store.NotFound:
        return _not_found(bookmark_id)
    except save.FillInError as err:
        status = {"already_read": 409, "text_too_short": 400, "summary_failed": 502}
        return error_response(status[err.code], err.code, str(err))


class PatchBody(BaseModel):
    reason: str | None = None
    folder: str | None = None


def _set_reason(bookmark_id: int, text: str) -> dict | None:
    """Set the user's own reason. Return None when the bookmark does not exist."""
    with _write_lock:
        if store.get_bookmark(bookmark_id) is None:
            return None
        return store.update_bookmark(
            bookmark_id, {"reason": text, "reason_source": "user"}
        )


def _move_bookmark(bookmark_id: int, folder: str) -> dict | None:
    """Move one bookmark and keep its old folder for one Undo.

    Return None when the bookmark does not exist. The caller checks the folder
    name first, so an unknown folder never reaches this function.
    """
    with _write_lock:
        item = store.get_bookmark(bookmark_id)
        if item is None:
            return None
        previous = item["folder"] if item["folder"] is not None else config.UNSORTED
        new_folder = None if folder == config.UNSORTED else folder
        return store.update_bookmark(
            bookmark_id, {"folder": new_folder, "prev_folder": previous}
        )


@app.patch("/api/bookmarks/{bookmark_id}", response_model=None)
def patch_bookmark(bookmark_id: int, body: PatchBody) -> dict | JSONResponse:
    if body.folder is not None:
        if not config.is_allowed_folder(body.folder):
            return error_response(400, "folder_not_found", "Folder does not exist.")
        updated = _move_bookmark(bookmark_id, body.folder)
        if updated is None:
            return _not_found(bookmark_id)
        return updated
    text = (body.reason or "").strip()
    if not text:
        return error_response(400, "empty_reason", "The reason is empty.")
    updated = _set_reason(bookmark_id, text)
    if updated is None:
        return _not_found(bookmark_id)
    return updated


@app.post("/api/bookmarks/{bookmark_id}/undo", response_model=None)
def undo_bookmark(bookmark_id: int) -> dict | JSONResponse:
    with _write_lock:
        item = store.get_bookmark(bookmark_id)
        if item is None:
            return _not_found(bookmark_id)
        previous = item["prev_folder"]
        if previous is None:
            return error_response(409, "nothing_to_undo", "There is nothing to undo.")
        folder = None if previous == config.UNSORTED else previous
        return store.update_bookmark(
            bookmark_id, {"folder": folder, "prev_folder": None}
        )


class ImportPreviewBody(BaseModel):
    # `file` is the browser export HTML; `text` is pasted text. `file` wins.
    file: str | None = None
    text: str | None = None


def _import_estimate(new: int) -> float:
    """The cost estimate in dollars for `new` links (IM-04).

    Unverified: the token figure and the price live in mnemo/core/config.py and must be
    checked against the current Claude API prices.
    """
    return round(
        new
        * config.IMPORT_TOKENS_PER_LINK
        * config.IMPORT_PRICE_PER_MILLION_TOKENS
        / 1_000_000,
        6,
    )


def _links_message(count: int) -> str:
    return f"{count} link{'' if count == 1 else 's'} found."


@app.post("/api/import/preview")
def import_preview(body: ImportPreviewBody) -> dict:
    """Count the links and estimate the cost before any import API call (IM-04).

    Reads the browser export (`file`) or the pasted text (`text`); `file` wins
    when both are present. Links already saved are counted but left out of
    `new`. `slack` counts found Slack archive links, saved or not. No page is
    fetched and no Claude call is made.
    """
    if body.file is not None:
        links = importer.links_from_browser_export(body.file)
    elif body.text is not None:
        links = importer.links_from_text(body.text)
    else:
        links = []

    found = len(links)
    if found == 0:
        return {
            "found": 0,
            "new": 0,
            "already_saved": 0,
            "slack": 0,
            "estimate": 0.0,
            "message": "No links found.",
        }
    already_saved = sum(
        1 for link in links if store.find_by_url_clean(link["url_clean"]) is not None
    )
    new = found - already_saved
    return {
        "found": found,
        "new": new,
        "already_saved": already_saved,
        "slack": sum(1 for link in links if link["slack"]),
        "estimate": _import_estimate(new),
        "message": _links_message(found),
    }


class ChatBody(BaseModel):
    message: str
    pasted_text: str | None = None


def _note_reply(bookmark_id: int | None, text: str | None) -> str:
    if bookmark_id is None or text is None:
        return "What should the reason say? Write note <id> <text>."
    if _set_reason(bookmark_id, text) is None:
        return "I do not have a bookmark with that number."
    return "Reason updated."


# Claude is asked to name each bookmark as #<id>. Accept the common variants too.
_ANSWER_REF = re.compile(r"(?:#|\bbookmark\s+|\bno\.\s*)\s*(\d+)", re.IGNORECASE)


def _answer_bookmarks(text: str) -> list[dict]:
    """Turn the numbers Claude named into up to ASK_ANSWER_LIMIT stored bookmarks.

    Numbers that do not exist are skipped here; ticket #127 adds the check that
    reports them. The answer keeps the model's text, so the numbers stay visible.
    """
    found: list[dict] = []
    seen: set[int] = set()
    for match in _ANSWER_REF.finditer(text):
        bookmark_id = int(match.group(1))
        if bookmark_id in seen:
            continue
        item = store.get_bookmark(bookmark_id)
        if item is None:
            continue
        seen.add(bookmark_id)
        found.append(
            {
                "id": item["id"],
                "title": item.get("title") or item["url"],
                "type": item.get("type", ""),
                "reason": item.get("reason", ""),
                "reason_source": item.get("reason_source", "guess"),
            }
        )
        if len(found) >= config.ASK_ANSWER_LIMIT:
            break
    return found


def _ask_reply(question: str) -> dict:
    """Run the ask loop and turn its text into up to 3 bookmark results."""
    result = ask.run_ask(question)
    if result.error:
        _record_exchange(question, result.text, [])
        return {"kind": "answer", "text": result.text, "bookmarks": []}
    bookmarks = _answer_bookmarks(result.text)
    text = result.text.strip() if bookmarks else "nothing found"
    if not text:
        text = f"{len(bookmarks)} bookmarks fit." if bookmarks else "nothing found"
    _record_exchange(question, text, [item["id"] for item in bookmarks])
    return {"kind": "answer", "text": text, "bookmarks": bookmarks}


@app.post("/api/chat", response_model=None)
def chat(body: ChatBody) -> dict | JSONResponse:
    if not body.message.strip():
        return error_response(400, "empty_message", "The message is empty.")
    links = intent.find_links(body.message)
    # A message with a link is a save, even when it starts with "note" (CI-02).
    note = None if links else intent.parse_note(body.message)
    if note is not None:
        reply = _note_reply(*note)
        _record_exchange(body.message, reply, [])
        return {"kind": "text", "text": reply}
    if not links:
        return _ask_reply(body.message)
    cards = []
    failed = []
    last_error = None
    seen = set()
    private = intent.is_private(body.message)
    for index, link in enumerate(links):
        key = urlclean.clean_url(link)
        if key in seen:
            continue
        seen.add(key)
        # Pasted text belongs to the first link in the message only.
        pasted = body.pasted_text if index == 0 else None
        try:
            with _write_lock:
                cards.append(save.save(link, pasted_text=pasted, private=private))
        except Exception as exc:
            # Auth and config errors (save.is_permanent_error) always propagate
            # to the global handler, a JSON 500, whatever the link order. With
            # nothing saved yet, any other non-storage error propagates too.
            # Once a card is saved, the rest are reported per link so the saved
            # cards are returned and recorded (a retry would save them again).
            # Log the class only: the text can hold paths or page content.
            if save.is_permanent_error(exc):
                raise
            if not cards and not isinstance(exc, (store.StoreError, OSError)):
                raise
            _log.error("Could not save a link: %s", type(exc).__name__)
            failed.append(link)
            last_error = exc
    if last_error is not None and not cards:
        raise last_error  # nothing saved: a plain 500 is honest and safe to retry
    result: dict = {"kind": "cards", "cards": cards}
    if failed:
        result["failed"] = failed
    _record_exchange(
        body.message,
        _cards_reply_text(len(cards), len(failed)),
        [c["id"] for c in cards],
        failed,
    )
    return result


def _cards_reply_text(saved: int, failed: int) -> str:
    if saved == 0 and failed:
        n = f"{failed} link{'' if failed == 1 else 's'}"
        return f"I could not save {'it' if failed == 1 else 'any of the ' + n}."
    text = f"Saved {saved} bookmark{'' if saved == 1 else 's'}."
    if failed:
        text += f" {failed} could not be saved."
    return text


def _record_exchange(
    user_text: str,
    app_text: str,
    bookmark_ids: list[int],
    failed: list[str] | None = None,
) -> None:
    app_message: dict = {
        "role": "app",
        "text": app_text,
        "bookmark_ids": bookmark_ids,
    }
    if failed:
        app_message["failed"] = failed
    with _write_lock:
        store.append_chat({"role": "user", "text": user_text})
        store.append_chat(app_message)


@app.get("/api/chat/history", response_model=None)
def chat_history(limit: int = 50) -> dict | JSONResponse:
    if limit < 1:
        return error_response(400, "bad_request", "limit must be at least 1.")
    messages = []
    for message in store.list_chat(limit):
        cards = []
        for bookmark_id in message.get("bookmark_ids", []):
            card = store.get_bookmark(bookmark_id)
            cards.append(
                card if card is not None else {"id": bookmark_id, "deleted": True}
            )
        messages.append({**message, "cards": cards})
    return {"messages": messages}


def main() -> None:
    uvicorn.run(app, host=HOST)


if __name__ == "__main__":
    main()
