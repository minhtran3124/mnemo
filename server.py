"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

import html
import logging
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

import intent
import save
import store
import urlclean

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
    """Read a page from web/ and put the shared header where it says <!--HEADER-->."""
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


# Phase 1 has no folder picker, so the page names the one folder every bookmark
# is in. A null folder in the data means Unsorted (docs/feature-specs/storage.md).
UNSORTED_FOLDER = "Unsorted"


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _bookmark_row(item: dict) -> str:
    title = item.get("title") or item["url"]
    host = urlparse(item["url"]).hostname or ""
    unreadable = item.get("page_status") == "unreadable"
    bid = int(item["id"])
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
    parts.append(
        f'<button type="button" class="bm-delete" '
        f'data-delete-url="/api/bookmarks/{bid}" '
        f'data-confirm="{_esc(f"Delete {title}? This cannot be undone.")}">Delete</button>'
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
    sections = [
        f'<p class="bm-folder" id="bm-folder">Folder: <strong>{UNSORTED_FOLDER}</strong></p>'
    ]
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


class ReasonBody(BaseModel):
    reason: str | None = None


def _set_reason(bookmark_id: int, text: str) -> dict | None:
    """Set the user's own reason. Return None when the bookmark does not exist."""
    with _write_lock:
        if store.get_bookmark(bookmark_id) is None:
            return None
        return store.update_bookmark(
            bookmark_id, {"reason": text, "reason_source": "user"}
        )


@app.patch("/api/bookmarks/{bookmark_id}", response_model=None)
def patch_bookmark(bookmark_id: int, body: ReasonBody) -> dict | JSONResponse:
    text = (body.reason or "").strip()
    if not text:
        return error_response(400, "empty_reason", "The reason is empty.")
    updated = _set_reason(bookmark_id, text)
    if updated is None:
        return _not_found(bookmark_id)
    return updated


class ChatBody(BaseModel):
    message: str
    pasted_text: str | None = None


LINKS_ONLY_TEXT = "I can only save links for now. Asking comes later."


def _note_reply(bookmark_id: int | None, text: str | None) -> str:
    if bookmark_id is None or text is None:
        return "What should the reason say? Write note <id> <text>."
    if _set_reason(bookmark_id, text) is None:
        return "I do not have a bookmark with that number."
    return "Reason updated."


def _fill_in(old: dict, fields: dict, page: str | None) -> dict:
    """Move what the app read (`fields`, `page`) into the saved record `old`.

    The record keeps its id, saved_at, folder, opened_count and any reason the
    user wrote: the app never deletes or replaces a bookmark on its own.
    """
    # store.py has no public page writer yet; reuse its own private helpers.
    store._atomic_write(store._page_path(old["id"]), page or "")
    update = {
        key: fields[key] for key in ("type", "title", "page_status", "summary", "tags")
    }
    if old["reason_source"] != "user":
        update["reason"] = fields["reason"]
        update["reason_source"] = fields["reason_source"]
    return store.update_bookmark(old["id"], update)


def _save_link(link: str, url_clean: str, pasted: str | None) -> dict:
    """Save one link. Pasted text for a link already saved as link only fills
    that entry in place: same id, no duplicate, no delete of the user's record.
    Nothing is written for a paste that is too short to read."""
    old = store.find_by_url_clean(url_clean) if pasted is not None else None
    if old is None or old["page_status"] == "ok":
        return save.save(link, pasted_text=pasted)
    fields, page = save.prepare(link, pasted_text=pasted)
    if fields["page_status"] == "ok":
        return _fill_in(old, fields, page)
    # The paste was too short to read: keep the first record, write nothing.
    return old


@app.post("/api/chat", response_model=None)
def chat(body: ChatBody) -> dict | JSONResponse:
    if not body.message.strip():
        return error_response(400, "empty_message", "The message is empty.")
    note = intent.parse_note(body.message)
    if note is not None:
        return {"kind": "text", "text": _note_reply(*note)}
    links = intent.find_links(body.message)
    if not links:
        _record_exchange(body.message, LINKS_ONLY_TEXT, [])
        return {"kind": "text", "text": LINKS_ONLY_TEXT}
    cards = []
    failed = []
    last_error = None
    seen = set()
    for index, link in enumerate(links):
        key = urlclean.clean_url(link)
        if key in seen:
            continue
        seen.add(key)
        # Pasted text belongs to the first link in the message only.
        pasted = body.pasted_text if index == 0 else None
        try:
            with _write_lock:
                cards.append(_save_link(link, key, pasted))
        except (store.StoreError, OSError) as exc:
            # Only a storage failure is reported per link. Key, auth and other
            # errors propagate to the global handler (a JSON 500). Log the class
            # only: the text can hold paths or page content.
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


def _record_exchange(user_text: str, app_text: str, bookmark_ids: list[int]) -> None:
    with _write_lock:
        store.append_chat({"role": "user", "text": user_text})
        store.append_chat(
            {"role": "app", "text": app_text, "bookmark_ids": bookmark_ids}
        )


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
