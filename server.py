"""The Mnemo web server. Binds to the loopback address only (D-021).

Every error response, including unknown routes and validation errors, uses one
JSON shape: {"error": {"code": ..., "message": ...}}. No response carries a
stack trace, a path or the API key.
"""

import logging
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import config

# Only this computer can reach the server (NF-01, D-021).
HOST = "127.0.0.1"

logger = logging.getLogger(__name__)

_HTTP_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    413: "payload_too_large",
    415: "unsupported_media_type",
    422: "unprocessable_entity",
    429: "rate_limited",
}


def error_response(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status, content={"error": {"code": code, "message": message}}
    )


async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    code = _HTTP_CODES.get(exc.status_code, "server_error")
    if exc.status_code == 404:
        return error_response(404, code, "Not found.")
    # Only a plain-text detail on a client error (below 500) is a message a
    # route wrote on purpose. A dict, list or other object never goes into the
    # body, and a 5xx detail can hold a path or upstream error text.
    if exc.status_code >= 500:
        return error_response(
            exc.status_code, code, "Something went wrong on the server."
        )
    if isinstance(exc.detail, str) and exc.detail:
        message = exc.detail
    else:
        message = "The request could not be completed."
    return error_response(exc.status_code, code, message)


async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(400, "bad_request", "The request is not valid.")


async def _unhandled_error(_: Request, exc: Exception) -> JSONResponse:
    # The log gets the exception type and the call frames, never the message:
    # a message can hold the API key or a token (exc_info would print it).
    frames = "".join(traceback.format_list(traceback.extract_tb(exc.__traceback__)))
    logger.error("unhandled error: %s\n%s", type(exc).__name__, frames)
    return error_response(500, "server_error", "Something went wrong on the server.")


def create_app() -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_exception_handler(StarletteHTTPException, _http_error)
    app.add_exception_handler(RequestValidationError, _validation_error)
    app.add_exception_handler(Exception, _unhandled_error)
    return app


app = create_app()


def main() -> None:
    uvicorn.run(app, host=HOST, port=config.PORT)


if __name__ == "__main__":
    main()
