# Phase 1 parity check

Date: 2026-11-05 · Ticket: #42 · Reference: [UI reference](../feature-specs/ui-reference.md) and the boards in [docs/design/v3-mockup/](../design/v3-mockup/README.md).

Method: each built page was opened from the running app with sample data, next to its board rendered from the `.dc.html` source, at the width and theme of the row. Type sizes, line heights, weights, column starts and wording were read from both sides with computed styles. The Ledger view was compared; the Cards view was read from CSS values only. Screenshots are not committed; their paths are in the PR body.

Result column: `match` means no difference was found; `accepted` means the remaining differences are listed in "Accepted differences" in the UI reference (the A numbers in the note). Differences that a fix could close were fixed in the same PR.

| Page | Width | Theme | Board | Result | Note |
| --- | --- | --- | --- | --- | --- |
| Chat | 1280px | light | `V3LightChat` | accepted | See A1 to A5. |
| Chat | 1280px | dark | `V3DarkChat` | accepted | See A1 to A5. |
| Bookmarks | 1280px | light | `V3LightBookmarks` | accepted | See A1, A6 to A9, A12. |
| Bookmarks | 1280px | dark | `V3DarkBookmarks` | accepted | See A1, A6 to A9, A12. |
| Chat | 390px | light | `V3LightPhoneChat` | accepted | See A1 to A5. |
| Chat | 390px | dark | `V3DarkPhoneChat` | accepted | See A1 to A5. |
| Bookmarks | 390px | light | `V3LightPhoneList` | accepted | See A1, A6 to A9, A12. |
| Bookmarks | 390px | dark | `V3DarkPhoneList` | accepted | See A1, A6 to A9, A12. |
| Settings | 390px | light | `V3LightSettings` | accepted | See A1, A10. |
| Settings | 390px | dark | `V3DarkSettings` | accepted | See A1, A10. |
| Settings | 1280px | light | none | accepted | No laptop board; compared with the phone board and the measurement tables. See A1, A10, A11. |
| Settings | 1280px | dark | none | accepted | No laptop board; compared with the phone board and the measurement tables. See A1, A10, A11. |
