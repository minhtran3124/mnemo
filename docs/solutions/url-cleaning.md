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
3. Remove query parameters that start with `utm_`.
4. Keep every other part of the link.
5. Save the clean link. The record field `url_clean` is proposed; the plan stores `url`. Open question: whether to keep the original link as well.
6. Compare clean links to find an exact duplicate.

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
| Two Brotli news articles | Not exact; flagged as similar in phase 5 |
