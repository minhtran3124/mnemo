# Page reading

Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

This file says how the server gets the text of a page, and what it does when that fails.

## Purpose

Claude can only summarize what it sees. The fetcher (a small program that downloads a page and takes out its text) gives Claude that text. Page fetching is not in the course, so expect failures. Supports F-01, F-02, NF-02, NF-04.

## Scope

In: fetcher, GitHub API, retry, text limits, honest failure, YouTube, link cleaning, language.
Out: PDFs and screenshots (see [pdf-and-screenshots.md](pdf-and-screenshots.md)).

## Requirements

| ID | Requirement |
| --- | --- |
| PR-01 | The fetcher is code in `fetcher/`. Claude Code writes it. |
| PR-02 | For GitHub repos, use the official GitHub API: description and README. |
| PR-03 | If a fetch fails with a transient error (timeout, connection error, HTTP 500, 502, 503, 504), retry once. Do not retry other errors (4xx, too many redirects, a refused address, a refused type or size). Then show the honest failure card. |
| PR-04 | If the text is shorter than a minimum length, treat the page as unreadable. |
| PR-05 | Cut page text at a maximum page length (NF-02). Both limits live in `config.py`. |
| PR-06 | An unreadable page is saved as link only: `page_status` = `unreadable`, `summary` = `null`. |
| PR-07 | For YouTube, use only the video description. The card says so. |
| PR-08 | Clean tracking parts from the link before saving (see below). |
| PR-09 | The fetcher refuses unsafe targets and oversized or non-text responses (see "Fetch limits"). |

The limits are in "Fetch limits" below. They are starting values: put each in `config.py` and tune them in phase 1.

## Behavior and rules

- Honest failure text: "I could not read this page. I saved the link only." Never a made-up summary.
- Known cases: X post (not readable by the plan's test tool), Slack link (needs sign-in), bleepingcomputer.com (fetch error, cause unknown), pages built with JavaScript, paywalls, logins.
- Cutting long text: the card says when text was cut: "Text cut: the summary uses only the first 20,000 characters of this page." (the number is `MAX_PAGE_CHARS`). Wording can still change.
- Saved text goes to `data/pages/<id>.txt`. The same text is used by the eval, so each run sees the same input.

### Fetch limits (starting values)

Researched on 2026-11-05 by a read-only sub-agent. **Every number is a starting value and Unverified as a fact.** Tune them in phase 1 and write the final values in `config.py`. Sources: the [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), the [GitHub REST API rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) and the Python [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) docs. The httpx2 defaults were read from its wheel source, not from its docs site, so check them with a test fetch.

| Item | Starting value |
| --- | --- |
| Minimum text, HTML page | 300 characters after whitespace is collapsed (PR-04). Trafilatura passes almost any text, so this floor is ours. |
| Minimum text, GitHub | 40 characters, description and README together |
| Calibrate | Run the links in [sample-links.md](../reference/sample-links.md), log the extracted length of each, and set the floor between the shortest readable page and the longest unreadable one |
| Maximum text | `MAX_PAGE_CHARS` = 20,000 (already in `config.py`) |
| Timeouts | connect 5 s, read 10 s, write 5 s, pool 5 s, and an own 15 s cap per attempt. httpx has no total timeout, so the read loop checks elapsed time |
| Retry | Once, after 1 s, same GET (PR-03). A 429 is not retried |
| Maximum download | 2,000,000 decoded bytes. Refuse early if `Content-Length` is larger. Stream and stop at the cap |
| Content types | `text/html`, `application/xhtml+xml`, `text/plain`. Anything else, or none: "not a web page", saved as link only. PDFs are phase 6 |
| Redirects | Follow, at most 5. Set `follow_redirects` explicitly |
| Schemes | `http` and `https` only. No user name or password in the link. Ports 80 and 443. Link at most 2048 characters |
| Address check | Resolve the host; check every IPv4 and IPv6 address; refuse if any is not allowed. Allow only `ip.is_global` (unwrap IPv4-mapped IPv6 first). Also refuse loopback, private, link-local (including 169.254.169.254), 100.64.0.0/10 and unique-local ranges |
| Every redirect hop | Run the scheme and address checks again on each hop |
| Environment | `trust_env=False` (no proxy from the environment), a new client per fetch, no cookies. Never send a GitHub token to another host |
| Text extraction | Pass our own downloaded bytes to `trafilatura.extract()`. Do not use `trafilatura.fetch_url`: it would skip these guards |
| User agent | `Mnemo/0.1 (personal bookmark app)` plus a contact if the owner wants one. Not a browser string |
| GitHub API | 60 requests per hour without a token; enough for the 5 test links. An optional `GITHUB_TOKEN` in `.env` raises it to 5,000 per hour. On 429, or a 403 with `X-RateLimit-Remaining: 0` or `Retry-After`, do not retry: save link only and say the rate limit was reached. Any other 403 is saved link only and reported as a refusal, never as a rate limit |

GitHub README rules: a repo with no README (404) keeps its description. A README larger than the maximum download is cut at that size, and the description plus the cut README are used. A transient README error (5xx or timeout) is retried once on the README call alone, so the repo call is never repeated and the hourly rate limit is not spent twice. Any other README failure, or a transient one that fails again, fails the whole fetch with a reason (the bookmark is saved link only). It is never treated as a missing README and the description is not used alone.

Constants in `config.py` (built in `fetcher/`, #30): `FETCH_CONNECT_TIMEOUT`, `FETCH_READ_TIMEOUT`, `FETCH_WRITE_TIMEOUT`, `FETCH_POOL_TIMEOUT`, `FETCH_ATTEMPT_SECONDS`, `FETCH_RETRY_DELAY`, `FETCH_MAX_BYTES`, `FETCH_CONTENT_TYPES`, `FETCH_MAX_REDIRECTS`, `FETCH_ALLOWED_PORTS`, `FETCH_MAX_URL_CHARS`, `MIN_TEXT_CHARS_HTML`, `MIN_TEXT_CHARS_GITHUB`, `USER_AGENT`, `GITHUB_API_BASE`. `fetch(url)` returns `FetchOk(text, source)` or `FetchFail(reason)` and does not raise for expected failures. It does not cut text to `MAX_PAGE_CHARS` and does not judge "too short": `save.py` does both, using the two `MIN_TEXT_CHARS_*` floors. Redirects are followed by hand so the checks run on every hop. The calibration of the text floors against the sample links is still **Unverified**.

**Decision (phase 1):** the DNS rebinding gap below is accepted. The app is local, single-user and bound to `127.0.0.1`. Revisit before the server is reachable from a network.

Known gap: after the address check, the connection could still go to a different address if DNS changes in between (DNS rebinding). Pinning the connection to the checked address was not verified for httpx2. Phase 1 may accept this for a local, single-user app; log the decision when you build it.

### Link cleaning (short)

Remove tracking parts such as `fbclid` and `utm_*` before comparing or saving `url_clean`. Full rules: [duplicates.md](duplicates.md).

### Language rule

Version 1 writes English summaries only (D-011). A Vietnamese page gets an English summary. No language badge in version 1. The Vietnamese tutorial stays in the set as an extra case and is not scored.

## Edge cases

| Case | Behavior |
| --- | --- |
| Page is a marketing page | Summary stays general, no invented product details. |
| Math shown as raw markup (arXiv) | Summary must not copy the raw markup. |
| Code only in images (Uber blog) | Summary may miss those facts. Accepted. |
| Site name wrongly guessed by a tool | Faithful-summary grader catches it. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | A failed fetch is retried once (checked in logs). |
| 2 | Text below the minimum gives `unreadable` and a null summary. |
| 3 | Text above the maximum is cut before the API call. |
| 4 | A YouTube card says the summary uses the description only. |
| 5 | A link with `fbclid` is saved with `url_clean` free of it. |
| 6 | Links to `localhost`, `127.0.0.1`, `169.254.169.254` and a private address are refused before any request. A redirect to such an address is refused too. |
| 7 | A response over the byte cap, or a content type that is not text, is refused and saved as link only. |
| 8 | A 404 is not retried; a timeout is retried once. |

## Tests

[hard-cases.md](test-cases/hard-cases.md), [save-golden-set.md](test-cases/save-golden-set.md). Links: [sample-links.md](../reference/sample-links.md).

## Open questions

- Whether to pin the connection to the checked address (DNS rebinding).
- Do the rules of a site (terms of use) limit saving its text? The plan says: keep text on your disk and do not share it.
