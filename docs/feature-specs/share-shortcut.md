# iPhone Share Shortcut

Status: Draft v0.1 · Owner: KhoiTran · Phase: B

This file describes the iPhone Shortcut that sends a shared link to your server.

## Purpose

Give you a Share button in Safari or another app, such as X, without a native app. Supports F-12 and D-008. Unverified: that this works. Test it with one link early.

## Scope

In: steps, token, endpoint, fallback, early test.
Out: a native iPhone app (not planned; needs Swift code and a paid Apple account for a stable install).

## Requirements

| ID | Requirement |
| --- | --- |
| SS-01 | The Shortcut appears in the Share menu. |
| SS-02 | It sends the shared link to `POST /api/share` ([server-api.md](server-api.md)). |
| SS-03 | The request carries your token. |
| SS-04 | The server saves it like a chat message and the card appears in the chat page. |
| SS-05 | No Apple developer account and no Swift code are needed. |
| SS-06 | If it fails, the fallback is to open the chat page in Safari and paste the link. |

## Steps in words

1. Open the Shortcuts app on the iPhone.
2. Create a new shortcut.
3. Set it to accept links from the Share menu.
4. Add a step that sends a web request to your server's share address, with the link and your token.
5. Add a step that shows the answer (for example "saved" or an error).
6. Name it and turn on "Show in Share Sheet".

Exact menu names in the Shortcuts app: Open question. Check on the device.

## Behavior and rules

- The server must be online and reachable from the phone, so phase A comes first.
- The token is long and random. Treat it like a password. If the phone is lost, change the token on the server.
- Failure cases: no internet, wrong token, server down. The Shortcut should show a short message. Wording: Open question.
- Shared text that is not a link (for example from X): Open question what the Shortcut sends.

## Edge cases

| Case | Behavior |
| --- | --- |
| Link with tracking parts | Cleaned by the server. |
| Duplicate link | Duplicate warning in the answer. |
| Server cannot read the page | "Page not read" result, link saved. |

## Acceptance criteria

| # | Check |
| --- | --- |
| 1 | From Safari, Share, then the Shortcut: the card appears in the chat page. |
| 2 | The same from another app, such as X. |
| 3 | A wrong token gives a clear failure on the phone. |
| 4 | The fallback (paste in Safari) works. |

## Tests

Phone test: `manual-testing`. Do one early test with one link before relying on it.

## Open questions

- Does the Shortcut work as planned (unverified).
- What happens when the Shortcut is shared from an app that sends text, not a link.
- Token rotation steps.
