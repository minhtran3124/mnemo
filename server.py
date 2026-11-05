"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

import logging
import threading

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import store

# Only this computer can reach the server (NF-01, D-021).
HOST = "127.0.0.1"

app = FastAPI()

_log = logging.getLogger("mnemo.server")

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
