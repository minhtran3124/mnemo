"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

import logging
import threading
from pathlib import Path

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


class ChatBody(BaseModel):
    message: str
    pasted_text: str | None = None


LINKS_ONLY_TEXT = "I can only save links for now. Asking comes later."


@app.post("/api/chat", response_model=None)
def chat(body: ChatBody) -> dict | JSONResponse:
    if not body.message.strip():
        return error_response(400, "empty_message", "The message is empty.")
    links = intent.find_links(body.message)
    if not links:
        return {"kind": "text", "text": LINKS_ONLY_TEXT}
    cards = []
    failed = []
    for index, link in enumerate(links):
        # Pasted text belongs to the first link in the same message only.
        pasted = body.pasted_text if index == 0 else None
        try:
            with _write_lock:
                cards.append(save.save(link, pasted_text=pasted))
        except Exception:
            if not cards:
                raise  # nothing saved yet: a plain 500 is honest and safe to retry
            # Cards already saved must not be hidden by a later failure, or a
            # retry would save them twice. Report the links that did not save.
            _log.exception("Could not save %s", link)
            failed.append(link)
    result: dict = {"kind": "cards", "cards": cards}
    if failed:
        result["failed"] = failed
    return result


def main() -> None:
    uvicorn.run(app, host=HOST)


if __name__ == "__main__":
    main()
