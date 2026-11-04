# Hosting Check
Status: Draft v0.1 · Owner: KhoiTran · Phase: A

This file lists what to verify about Render before phase A. Render is the host you plan to use (D-007). Nothing in it is verified. The plan says it did not check Render's price or storage rules.

Unverified: Render price and disk persistence.

## Questions

| # | Question | Why it matters | Answer | Source and session checked |
| --- | --- | --- | --- | --- |
| 1 | What is the price of the smallest plan that runs a Python server all day? | Budget is about $10 per month for hosting and API together | | |
| 2 | Does the disk keep files between deploys and restarts? | Bookmarks are plain files in `data/` | | |
| 3 | Is a persistent disk a paid extra, and what does it cost? | May break the budget | | |
| 4 | Does the server sleep when idle? How long does the first request take after sleep? | The Shortcut and the phone page need a quick answer | | |
| 5 | How do you set environment variables so `.env` is not needed on the host? | The key must not be in git | | |
| 6 | Can you cap spending on the host? | NF-02 needs cost limits | | |
| 7 | Does the host give a secure (HTTPS) address by default? | Login and token must not travel in plain text | | |
| 8 | How do you export or back up the data? | Pocket's shutdown is the reason for owning your files | | |
| 9 | Where is the server located, and does this matter for your data? | Privacy | | |

Also check the Claude Console spending limit (see [API notes](../reference/api-notes.md)).

## If the disk is not persistent
The plan says: replace the inside of `store.py` with a database, and change nothing else (D-012, NF-03).
1. Ask Claude Code for a plan to swap the storage in `store.py` only.
2. Keep the same functions, so no other file changes.
3. Run the whole [smoke checklist](../manual-testing/smoke-checklist.md).
4. Add a backup step: export `bookmarks.json` and pages before each deploy.
5. Re-run the cost check; a database may cost extra.

Alternative hosts are not studied here. Open question: whether to compare other hosts if Render's price is too high.

Related: [phase A plan](../product/plans/phase-a-online-host.md), [local vs online](local-vs-online.md), [storage spec](../feature-specs/storage.md).
