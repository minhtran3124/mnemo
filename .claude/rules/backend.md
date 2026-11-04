---
paths:
  - "**/*.py"
---

# Backend rules (Python)

## Code style
- Python 3 with type hints on every public function. Use `dataclasses` or Pydantic models for structured data, not loose dicts passed around.
- Format and lint with the project's tools (default: `ruff format` and `ruff check`). Test with `pytest`.
- Use `pathlib` for paths and `with` blocks for files and connections. Read and write text as UTF-8 explicitly.
- No mutable default arguments. No global state that changes at runtime.

## HTTP API
- Handlers stay thin: parse and validate the request, call a service function, shape the response. No business logic or file access in the handler.
- Validate every request body and query parameter against a schema. Return `400` for bad input, `401`/`403` for auth, `404` for missing resources, `409` for conflicts, `429` for limits, `5xx` only for server faults.
- Use one error shape for every error response (a stable machine `code` plus a human `message`). Never leak stack traces, file paths or secrets in a response.
- Use correct methods: `GET` is safe and has no side effects; `PUT`/`PATCH`/`DELETE` are idempotent where possible.
- Dev servers bind to `127.0.0.1` by default. Exposing a server beyond localhost requires authentication.
- Any endpoint that costs money or changes data must be authenticated once the server is reachable from a network.

## External APIs and LLM calls
- Wrap each provider in one client module: timeouts, bounded retries, and rate-limit handling live there, not at call sites.
- Set an explicit output token limit and cap input size before every model call. Check size before sending, not after an error.
- Treat model output as untrusted input: parse it, validate it against a schema, and reject or fall back when it does not match. Never `eval` or execute it.
- Never present generated content as fact when the source was missing or unreadable. Return an explicit "unknown" or empty result instead.
- Keep prompts in versioned files or constants, not built ad hoc inside handlers, so a change can be measured.
- Log token usage and latency per call; never log full prompts that contain private content.

## Fetching web content
- Set a user agent, a timeout and a max response size. Follow redirects with a limit.
- Treat all fetched HTML/text as untrusted: strip scripts, never render it raw, guard against SSRF (no requests to private or loopback addresses from user-supplied URLs).

## Concurrency
- Long work (batch imports, many API calls) runs in bounded batches with progress, not one unbounded request.
- Protect shared files or resources against concurrent writers (a lock or a single writer).
