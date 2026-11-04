# Phase C: Ubuntu .deb App
Status: Draft v0.1 · Owner: KhoiTran · Phase: C

Optional. A .deb file (the Ubuntu install package) that opens the chat page in its own window. The value is low because a browser tab does the same job.

## Goal
F-16. The Mac .dmg is not planned (D-010).

## You can now
Install a .deb app on Ubuntu.

## Sessions and lessons
2 sessions. No lessons (outside the course). The estimate is a guess.

## Inputs
Phase A done (an online chat page to open). An Ubuntu machine.

## Tasks
1. Choose a small window tool with Claude Code.
2. Make the window open your chat page URL. It holds no API key (NF-01).
3. Package the app as a .deb.
4. Install it on Ubuntu and open it.
5. Test login inside the window.
6. Remove it and check nothing is left over.

## Done when
- [ ] The .deb installs on Ubuntu.
- [ ] The app opens the chat page in its own window.
- [ ] No API key is in the package (search the files).
- [ ] Uninstall works.

## Risks
Outside the course; low value. See [risk review](../../reviews/risk-review.md).

## If time runs short
Cut the whole phase first (D-009).

## Links to specs
[server API](../../feature-specs/server-api.md) · [privacy and security](../../feature-specs/privacy-and-security.md) · [roadmap](../roadmap.md)
