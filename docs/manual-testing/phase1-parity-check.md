# Phase 1 parity check

Date: 2026-11-05 · Ticket: #42 · Reference: [UI reference](../feature-specs/ui-reference.md) and the boards in [docs/design/v3-mockup/](../design/v3-mockup/README.md).

Method: each built page was opened from the running app with sample data, next to its board rendered from the `.dc.html` source, at the width and theme of the row. Type sizes, line heights, weights, column starts and wording were read from both sides with computed styles. Both views were compared: the Ledger view, and the Cards view, which each Bookmarks board shows when its Cards option is selected. For Cards, the app (Cards selected, sample data) and the board were opened at 1280px and 390px in light and dark and the card box, grid and text sizes were read with computed styles; screenshots were taken of both sides (paths in the PR body). The comparison found that on the phone the row title and meta line were 21px and 14px against 19px and 13px on the board, in both views; this was fixed in `web/css/base.css` and `web/css/bookmarks.css` and re-measured. Each board is drawn at one width, so a row at the other width was read against the measurement table (A13). Screenshots are not committed; their paths are in the PR body.

Result column: `match` means no difference was found; `accepted` means the remaining differences are listed in "Accepted differences" in the UI reference (the A numbers in the note). Every Bookmarks row below covers the Ledger and the Cards views. Differences that a fix could close were fixed in the same PR.

| Screen | Width | Theme | Board | Result | Note |
| --- | --- | --- | --- | --- | --- |
| Chat laptop | 1280px | light | `V3LightChat` | accepted | See A1 to A5. |
| Chat laptop | 1280px | dark | `V3DarkChat` | accepted | See A1 to A5. |
| Chat laptop | 390px | light | `V3LightChat` | accepted | See A1 to A5. Other width: measurement table only, A13. |
| Chat laptop | 390px | dark | `V3DarkChat` | accepted | See A1 to A5. Other width: measurement table only, A13. |
| Bookmarks laptop | 1280px | light | `V3LightBookmarks` | accepted | See A1, A6 to A9, A12, A14. |
| Bookmarks laptop | 1280px | dark | `V3DarkBookmarks` | accepted | See A1, A6 to A9, A12, A14. |
| Bookmarks laptop | 390px | light | `V3LightBookmarks` | accepted | See A1, A6 to A9, A12, A14. Other width: measurement table only, A13. |
| Bookmarks laptop | 390px | dark | `V3DarkBookmarks` | accepted | See A1, A6 to A9, A12, A14. Other width: measurement table only, A13. |
| Chat phone | 390px | light | `V3LightPhoneChat` | accepted | See A1 to A5. |
| Chat phone | 390px | dark | `V3DarkPhoneChat` | accepted | See A1 to A5. |
| Chat phone | 1280px | light | `V3LightPhoneChat` | accepted | See A1 to A5. Other width: measurement table only, A13. |
| Chat phone | 1280px | dark | `V3DarkPhoneChat` | accepted | See A1 to A5. Other width: measurement table only, A13. |
| Bookmarks phone | 390px | light | `V3LightPhoneList` | accepted | See A1, A6 to A9, A12, A14. |
| Bookmarks phone | 390px | dark | `V3DarkPhoneList` | accepted | See A1, A6 to A9, A12, A14. |
| Bookmarks phone | 1280px | light | `V3LightPhoneList` | accepted | See A1, A6 to A9, A12, A14. Other width: measurement table only, A13. |
| Bookmarks phone | 1280px | dark | `V3DarkPhoneList` | accepted | See A1, A6 to A9, A12, A14. Other width: measurement table only, A13. |
| Settings | 390px | light | `V3LightSettings` | accepted | See A1, A10. |
| Settings | 390px | dark | `V3DarkSettings` | accepted | See A1, A10. |
| Settings | 1280px | light | none | accepted | No laptop board; compared with the phone board and the measurement tables. See A1, A10, A11. |
| Settings | 1280px | dark | none | accepted | No laptop board; compared with the phone board and the measurement tables. See A1, A10, A11. |
