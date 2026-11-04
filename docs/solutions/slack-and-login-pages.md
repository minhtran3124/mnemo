# Solution: Slack and Login Pages
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1, 4

How Mnemo handles pages that need a sign-in, especially Slack message links.

## Problem
The app fetches pages from the internet without your login. A page behind a sign-in cannot be read. Unverified: whether Slack links can be read in any way. The plan's test tool got a client error.

## Context
- Sample: a Slack message link (secretboth.slack.com). The fetch tool could not open it.
- A Slack link points to one message. The real link is inside that message.
- Your Slack is a personal workspace, so pasting is fine.
- The plan does not plan a Slack connection in version 1, because it needs an app approval and extra work.
- "about:blank#blocked" is not a link. It is a placeholder a browser shows for a blocked link.

## Solution
1. If the page is unreadable, follow [honest failure](honest-failure.md).
2. For a Slack link, show: "I cannot open Slack links. Paste the message text."
3. Accept the pasted message text.
4. Find the links inside it with the same code used by import (phase 4).
5. Save each found link. Open question: whether to keep the Slack link as the `source` note.
6. Do not ask for a Slack password or token.

For other login pages (members-only), show the honest failure card. Do not store a login for a site.

## Why
- NF-04: no summary of text the app did not see.
- The same paste path serves import (F-06), so no extra code path.
- Personal data stays under your control.

## Where used
F-02, F-06. See [import](../feature-specs/import.md) and [page reading](../feature-specs/page-reading.md).

## Tests
| Test | Expected |
| --- | --- |
| Paste the Slack link | Card says it cannot open Slack links and asks for message text |
| Paste message text with 2 links | Both are found and processed |
| Paste text with no link | A clear message, nothing saved |
| Paste "about:blank#blocked" | Not accepted as a link |
