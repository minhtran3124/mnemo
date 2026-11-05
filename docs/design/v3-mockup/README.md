# V3 mockup snapshot

Source files of the five V3 "final" artboards (light theme) from the Claude design canvas, saved on 2026-11-05 so the build can read exact values without opening the private canvas: https://claude.ai/artifact/7Q93Na93mLjP5FCbWbeYwz (title "Bookmark Brain Mockup", file `project/<name>.dc.html`).

| File | Screen | Size |
| --- | --- | --- |
| `V3LightChat.dc.html` | Chat (laptop) | 1280 wide |
| `V3LightBookmarks.dc.html` | Bookmark page (laptop) | 1280 wide |
| `V3LightPhoneChat.dc.html` | Chat (iPhone) | 390 x 844 |
| `V3LightPhoneList.dc.html` | Bookmarks (iPhone) | 390 x 844 |
| `V3LightSettings.dc.html` | Settings (iPhone) | 390 x 844 |

- The dark boards (`V3Dark*.dc.html`) are the same markup with the `thr-dark` radio checked. The colours come from the `.th` token block in each file; they match the token table in [theming and design tokens](../../feature-specs/theming-and-design-tokens.md).
- These are Design Component files (`<x-dc>`, a `support.js` that is not here). They do not open in a browser on their own. Read them as a source of exact sizes, spacing and wording.
- They load fonts from Google Fonts. The build does not (D-026: self-host).
- Do not edit these files and do not copy their markup into `web/`. How the build must follow them is in [UI reference](../../feature-specs/ui-reference.md).
- The earlier boards V1, V2, V4 and V5 are dropped (D-016) and are not saved here.
