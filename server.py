"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

import html
import logging
import threading
from pathlib import Path
from urllib.parse import urlparse

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

import store

# Only this computer can reach the server (NF-01, D-021).
HOST = "127.0.0.1"

# Found from this file, so it works from any working directory.
WEB_DIR = Path(__file__).resolve().parent / "web"

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


def _bookmark_row(item: dict) -> str:
    title = item["title"] or item["url"]
    host = urlparse(item["url"]).hostname or ""
    unreadable = item["page_status"] == "unreadable"
    bid = int(item["id"])
    parts = [
        f'<li class="bm-row" data-id="{bid}">',
        '<div class="bm-main">',
        (
            f'<a class="bm-title" href="{_esc(item["url"])}" target="_blank" '
            f'rel="noopener noreferrer" data-open-url="/api/bookmarks/{bid}/open">'
            f"{_esc(title)}</a>"
        ),
        (
            f'<p class="bm-meta"><span>{_esc(item["type"])}</span> '
            f"<span>{_esc(host)}</span> "
            f"<span>{_esc(str(item['saved_at'])[:10])}</span></p>"
        ),
    ]
    if unreadable:
        parts.append('<p><span class="badge badge-warn">page not read</span></p>')
    elif item.get("summary"):
        parts.append(f'<p class="bm-summary">{_esc(item["summary"])}</p>')
    if item.get("reason"):
        flag = ""
        if item["reason_source"] == "guess":
            flag = ' <span class="badge">guess</span>'
        parts.append(f'<p class="bm-reason">{_esc(item["reason"])}{flag}</p>')
    if item.get("tags"):
        tags = "".join(f"<li>{_esc(tag)}</li>" for tag in item["tags"])
        parts.append(f'<ul class="bm-tags" aria-label="Tags">{tags}</ul>')
    parts.append("</div>")
    parts.append(
        f'<button type="button" class="bm-delete" '
        f'data-delete-url="/api/bookmarks/{bid}" '
        f'data-confirm="{_esc(f"Delete {title}? This cannot be undone.")}">Delete</button>'
    )
    parts.append("</li>")
    return "".join(parts)


def _bookmark_groups(items: list[dict]) -> str:
    if not items:
        return (
            '<p class="empty">Nothing saved yet. Paste a link in the chat '
            "to save your first bookmark.</p>"
        )
    sections = []
    for kind in TYPE_ORDER:
        rows = [item for item in items if item["type"] == kind]
        if not rows:
            continue
        sections.append(
            f'<section class="bm-group" data-type="{kind}">'
            f'<h2>{TYPE_LABELS[kind]} <span class="count">{len(rows)}</span></h2>'
            f'<ul class="bm-list">{"".join(_bookmark_row(r) for r in rows)}</ul>'
            "</section>"
        )
    return "".join(sections)


@app.get("/bookmarks", response_class=HTMLResponse)
def bookmarks_page() -> str:
    items = store.list_bookmarks()
    banner = ""
    if any(item["page_status"] == "unreadable" for item in items):
        banner = (
            '<p class="banner" role="note"><strong>Needs a look.</strong> '
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


def main() -> None:
    uvicorn.run(app, host=HOST)


if __name__ == "__main__":
    main()
