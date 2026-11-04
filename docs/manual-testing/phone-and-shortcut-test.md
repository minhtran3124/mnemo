# Phone and Shortcut Test
Status: Draft v0.1 · Owner: KhoiTran · Phase: A, B

This file lists the checks for the phone browser, the login, and the iPhone Share Shortcut. It also gives the early test and the fallback.

Unverified: whether the iPhone Shortcut works as planned. The plan says "fairly sure". Test it early with one link.

## Phone browser checks (phase 1 on the laptop, phase A online)
Phase 1 can be tested on a phone only if the phone can reach your laptop. Otherwise test the narrow layout at 390 px width in the laptop browser, and test the phone for real in phase A.

| # | Check | Expected |
| --- | --- | --- |
| 1 | Open the chat page | No sideways scroll |
| 2 | Tap the link box | Keyboard opens; the box stays visible |
| 3 | Paste a link and send | Card appears and fits the screen |
| 4 | Tap Move and Undo | Each button is at least 44 px high and easy to hit |
| 5 | Open the bookmark page | List is readable; folders reachable |
| 6 | Read all text | Contrast is clear; nothing is cut off |
| 7 | Rotate the phone | Layout still works |

These come from NF-05 in the [frontend UI spec](../feature-specs/frontend-ui.md).

## Login checks (phase A)
| # | Check | Expected |
| --- | --- | --- |
| 1 | Open the online address without logging in | Login page only; no bookmarks visible |
| 2 | Wrong password | Rejected; no hint about which part was wrong |
| 3 | Right password | Chat page opens |
| 4 | Look at page source and network tab | No API key anywhere (NF-01) |
| 5 | Try to open a data address directly | Not served without login |

See [privacy and security](../feature-specs/privacy-and-security.md) and [phase A plan](../product/plans/phase-a-online-host.md).

## Shortcut early test (phase B)
Do this with one link before you rely on it.
1. Open the Shortcuts app on the iPhone and make a new shortcut that accepts links from the Share menu.
2. Add a web request action that sends the link to your server address with your login token.
3. Open Safari on a public article and tap Share.
4. Choose your shortcut.
5. Open the chat page. Check that the card appears.
6. Repeat from another app, for example X.
7. Share a link with `utm_*` in it. Check that the saved link is clean.
8. Share while the server is off. Note what the phone shows.

Steps and rules are in [share shortcut spec](../feature-specs/share-shortcut.md) and [phase B plan](../product/plans/phase-b-iphone-shortcut.md).

## Fallback
If the Shortcut fails, open the chat page in Safari and paste the link. This is the planned fallback. Do not build a native iPhone app (decision D-008).

## Results
| Test | Pass / Fail | Note |
| --- | --- | --- |
| Share from Safari | | |
| Share from another app | | |
| Wrong token | | |
| Server off | | |

## Open questions
- Open question: which iPhone and iOS version you test on.
- Unverified: Apple free-account 7-day expiry. It matters only for a native app, which is not planned.
