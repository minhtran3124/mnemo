"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

# Only this computer can reach the server (NF-01, D-021).
HOST = "127.0.0.1"

# Found from this file, so it works from any working directory.
WEB_DIR = Path(__file__).resolve().parent / "web"

app = FastAPI()
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


def render_page(name: str) -> str:
    """Read a page from web/ and put the shared header where it says <!--HEADER-->."""
    header = (WEB_DIR / "partials" / "header.html").read_text(encoding="utf-8")
    page = (WEB_DIR / name).read_text(encoding="utf-8")
    return page.replace("<!--HEADER-->", header)


@app.get("/settings", response_class=HTMLResponse)
def settings() -> str:
    return render_page("settings.html")


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status, content={"error": {"code": code, "message": message}}
    )


@app.exception_handler(StarletteHTTPException)
async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    if exc.status_code == 404:
        return error_response(404, "not_found", "Not found.")
    code = f"http_{exc.status_code}"
    return error_response(exc.status_code, code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(400, "bad_request", "The request is not valid.")


def main() -> None:
    uvicorn.run(app, host=HOST)


if __name__ == "__main__":
    main()
