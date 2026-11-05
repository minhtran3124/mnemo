"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response uses one JSON shape: {"error": {"code": ..., "message": ...}}.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Only this computer can reach the server (NF-01, D-021).
HOST = "127.0.0.1"

app = FastAPI()


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
