# Git and Secrets
Status: Draft v0.1 · Owner: KhoiTran · Phase: 0

This file explains how to keep your API key private. An API key is a secret string that lets a program use your Claude account and spend your money.

## Rules
| # | Rule |
| --- | --- |
| 1 | The key lives only in `.env` on the server. |
| 2 | `.env` is listed in `.gitignore` before the first commit. |
| 3 | Never print the key in logs, errors, chat or screenshots. |
| 4 | Never put the key in a web page, a Shortcut or a desktop app (NF-01). |
| 5 | Set a monthly spending limit in the Claude Console. |
| 6 | Bind the local server to `127.0.0.1`, never `0.0.0.0`. |

## .gitignore
Make `.gitignore` with at least these lines before you commit anything:

```text
.env
data/
__pycache__/
```

Open question: whether `data/` should be committed. It holds your bookmarks and page text. The plan says keep saved text on your disk and do not share it, so ignoring it is the safe start.

## Check before every commit
1. Run `git status` and read the list of files.
2. Make sure `.env` is not in the list.
3. Search the staged changes for the start of your key.

## Pre-commit check
The hook is `.githooks/pre-commit` (POSIX sh). It runs before each commit and stops it when:
- A staged file has a name starting with `.env`, in any folder. That includes `.env.example` and the deletion of such a file.
- An added line of the staged diff matches `sk-ant-[A-Za-z0-9_-]{20,}`. Only added lines are checked, so a commit that removes a key passes.

The message names the file and line, never the matched text. Old git history is not scanned.

Turn it on once per clone:

```bash
git config core.hooksPath .githooks
```

Known limit: `git commit --no-verify` skips the hook. The check is a safety net, not a guarantee. A CI secret scan is planned for phase A. Tests are in `tests/test_pre_commit.py` and build the fake key at runtime. Do not show Claude the real key to test it.

## If the key leaks
Do these steps in order, quickly:
1. Open the Claude Console and delete the leaked key.
2. Create a new key.
3. Put the new key in `.env` only.
4. Check the Console usage page for spending you do not recognize.
5. If the key was committed, treat it as public even if you delete the file later. Git history keeps old versions. The old key must stay deleted.
6. Check that the spending limit is still set.

## Spending limit
In the Claude Console, set a monthly limit. Your budget is about $10 per month for hosting and the API together. Unverified: current prices and how the limit works on your account. Check the Console and the [API notes](../reference/api-notes.md).

## Common mistakes
- Committing `.env`.
- Starting the server on `0.0.0.0` on a shared network (see [local vs online](../research/local-vs-online.md)).
- Pasting an error message that contains the key into a chat.

Related: [privacy and security spec](../feature-specs/privacy-and-security.md), [smoke checklist](../manual-testing/smoke-checklist.md).
