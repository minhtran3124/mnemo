---
paths:
  - "**/*.{py,js,mjs,ts,tsx,jsx,html,css,sql,toml,yaml,yml,json}"
---

# Technical rules (all code)

## Secrets and config
- Read secrets from environment variables or a gitignored `.env`. Never hardcode them, log them, return them in a response, or put them in client code.
- Keep tunable values (model names, limits, timeouts, sizes) in one config module. No magic numbers scattered through the code.
- Commit a `.env.example` with placeholder values whenever a new variable is added.

## Structure
- One module, one job. Keep I/O (network, disk, external APIs) at the edges and business logic in plain functions that are easy to test.
- Depend on interfaces you own. Wrap third-party clients in a thin module so they can be swapped or faked in tests.
- Do not add a dependency for something a few lines of standard library can do. Pin versions in a lockfile.

## Errors
- Fail loudly at the boundary that can act on the error. Never swallow an exception with a bare `except` or an empty `catch`.
- Validate input where it enters the system. Reject invalid data with a clear message; do not silently repair it.
- Every external call has a timeout. Retries are bounded, with backoff, and only for errors that are safe to retry.

## Logging
- Use the logging library, not `print`. Log events with context (ids, durations), never secrets or full user content.
- Structured logs (one JSON object per line) for anything a script will read later.

## Testing
- Test behavior, not implementation. Every bug fix starts with a failing test.
- Unit tests must not call the network or paid APIs. Fake external clients at the wrapper boundary.
- Test the unhappy path as well as the happy one: bad input, timeout, empty result, partial failure.
- Keep tests deterministic: fixed fixtures on disk, no dependence on today's web content, time or random seeds.

## Change hygiene
- One logical change per commit. Run the tests and linter before committing.
- When behavior changes, update the doc that describes it in the same change.
