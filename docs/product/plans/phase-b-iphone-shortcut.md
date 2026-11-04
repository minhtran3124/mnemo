# Phase B: iPhone Shortcut
Status: Draft v0.1 · Owner: KhoiTran · Phase: B

Add a Share menu entry on iPhone using the Shortcuts app. No Swift code and no Apple developer account.

## Goal
F-12.

## You can now
Share a link from the iPhone with a Shortcut.

## Sessions and lessons
1 session. No lessons (outside the course). The time estimate is a guess.

## Inputs
Phase A done (server online with login). Test early with one link, because it is Unverified that the Shortcut works.

## Tasks
1. Add a server route that accepts a link and a login token and saves it like a chat message (`source: shortcut`, proposed).
2. Create a Shortcut that appears in the Share menu and sends the shared link with a web request and your token.
3. Test with one link from Safari.
4. Test from another app (for example X).
5. Test a bad token (must fail) and no network (must show an error).
6. Write the fallback: open the chat page in Safari and paste the link.

## Done when
- [ ] In Safari you tap Share, choose the shortcut, and the card appears in the chat.
- [ ] A bad token is rejected.
- [ ] The fallback steps are written in [phone and shortcut test](../../manual-testing/phone-and-shortcut-test.md).

## Risks
Shortcut may fail; token stored on the phone. See [risk review](../../reviews/risk-review.md).

## If time runs short
Use the fallback. Decide after the 2-week test; phase B can be cut if the web page is enough.

## Links to specs
[share shortcut](../../feature-specs/share-shortcut.md) · [server API](../../feature-specs/server-api.md) · [privacy and security](../../feature-specs/privacy-and-security.md)
