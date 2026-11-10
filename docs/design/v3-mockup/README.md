# V3 mockup snapshot

Source files of the ten V3 "final" artboards (five screens, light and dark) from the section "Version 3 final: the ledger in light and dark" of the Claude design canvas, saved on 2026-11-05 so the build can read exact values without opening the private canvas: https://claude.ai/artifact/7Q93Na93mLjP5FCbWbeYwz (title "Bookmark Brain Mockup", file `project/<name>.dc.html`).

A clean canvas with only these ten boards, titled "Mnemo V3 Final Design": https://claude.ai/artifact/9uvrP6gXgdiZDnge4nbu6U#page-dcb81aee8d83. Whether its boards equal the files here is **Unverified**.

| Screen | Light board | Dark board | Size |
| --- | --- | --- | --- |
| Chat (laptop) | `V3LightChat.dc.html` | `V3DarkChat.dc.html` | 1280 wide |
| Bookmark page (laptop) | `V3LightBookmarks.dc.html` | `V3DarkBookmarks.dc.html` | 1280 wide |
| Chat (iPhone) | `V3LightPhoneChat.dc.html` | `V3DarkPhoneChat.dc.html` | 390 x 844 |
| Bookmarks (iPhone) | `V3LightPhoneList.dc.html` | `V3DarkPhoneList.dc.html` | 390 x 844 |
| Settings (iPhone) | `V3LightSettings.dc.html` | `V3DarkSettings.dc.html` | 390 x 844 |

- **Light and dark are one design.** After the ids, board names and the checked theme radio are set aside, each dark board has the same markup as its light board (checked on 2026-11-05 for all five pairs; the only other difference is the radio group name in Settings). The dark look comes from the dark token set in the `.th` block at the top of every file, not from different layout. The token values match the table in [theming and design tokens](../../feature-specs/theming-and-design-tokens.md).
- **Default is System.** In the boards one theme option is fixed so light and dark can be compared. In the app, System is the default and follows the device (D-019).
- These are Design Component files (`<x-dc>`, a `support.js` that is not here). They do not open in a browser on their own. Read them as a source of exact sizes, spacing and wording.
- They load fonts from Google Fonts. The build does not (D-026: self-host).
- Do not edit these files and do not copy their markup into `mnemo/api/web/`. How the build must follow them is in [UI reference](../../feature-specs/ui-reference.md).
- The earlier boards V1, V2, V4 and V5, and the first V3 boards without a theme control, are dropped (D-016) and are not saved here.
