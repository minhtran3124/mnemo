# Solution: URL Cleaning
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 5

How Mnemo removes tracking parts from links before it saves or compares them.

## Problem
The same page can have two different links because of tracking text added by apps. Without cleaning, the duplicate check misses exact duplicates.

## Context
Your sample list had one repeat: the same GitHub repo (`gyoridavid/ai_agents_az`), once with a long `fbclid` tracking part. Code must remove tracking parts before it compares links.

## Solution
1. Take the link the user pastes.
2. Remove the query parameter `fbclid`.
3. Remove query parameters that start with `utm_`. Names match ignoring case (`UTM_Source` and `FBCLID` are removed too).
4. Keep every other part of the link: other parameters stay as written and in order, and the fragment (`#...`) is kept.
5. Save both: `url` keeps the link as pasted, and `url_clean` holds the clean link (decided). Fetching, opening and the duplicate check use `url_clean`.
6. If no parameter is left, the link has no `?`.
7. If the link cannot be parsed (for example `http://[abc`), return it unchanged. It must not turn `/api/chat` into a 500.
8. Compare clean links to find an exact duplicate.

## Code
The function is `clean_url(url)` in `urlclean.py`. It is pure and makes no network call. Tests: `tests/test_url_clean.py`.

## Other parameters
The plan names only `fbclid` and `utm_*`. Other tracking parameters exist, but this file does not list any the plan did not name. Open question: which other parameters to remove. Decide from real links you save. Removing a parameter that the page needs would break the link, so add one only when you can show it is safe.

## Why
- Exact duplicates must be caught by code, not by a model.
- Near-duplicates (different links, same news) are a different case: the warning text differs ("you saved this already" versus "you saved something similar").

## Where used
F-01, F-09, F-12 (a shared link may carry tracking text). See [duplicates](../feature-specs/duplicates.md) and [data model](../feature-specs/data-model.md).

## Tests
| Test | Expected |
| --- | --- |
| Save the repo link without `fbclid`, then with it | Second save is flagged as an exact duplicate |
| Link with `utm_source` and `utm_campaign` | Both removed |
| Link with a parameter that is not named | Left unchanged, until an open question is closed |
| Link that cannot be parsed (`http://[abc`) | Returned unchanged, no error |
| Two Brotli news articles | Not exact; flagged as similar in phase 5 |
