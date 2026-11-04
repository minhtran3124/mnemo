# Phase A: Online Host
Status: Draft v0.1 · Owner: KhoiTran · Phase: A

Put the server online so your phone can reach it, safely. An online server holds your API key, so it can spend your money if someone finds it.

## Goal
F-11: online host, login, spending cap.

## You can now
Use it from your phone browser and from anywhere.

## Sessions and lessons
4 sessions. Lessons 1, 2.

## Inputs
Phase 4 and the 2-week test done. Budget about 0 per month for hosting and API together (Unverified). Until now the server ran on your computer, bound to 127.0.0.1.

## Tasks
1. Host and storage check first. You plan to deploy to Render (Unverified: price and whether the disk keeps files after a deploy). Read the current docs. See [hosting check](../../research/hosting-check.md) and [local vs online](../../research/local-vs-online.md).
2. If files are not kept, replace the inside of `store.py` with a database. Nothing else may change (D-012).
3. Add login. Do not skip it.
4. Add limits: `max_tokens`, maximum page length, request rate limit. Set a spending cap in the Claude Console if offered (Unverified).
5. Keep the key in the host's secret settings, not in code or the page.
6. Change the bind address only for the host. Locally keep 127.0.0.1.
7. Make the chat and bookmark pages work at 390px width on a phone (NF-05).
8. Decide private mode online: private links must still send nothing to the API.
9. Run [phone and shortcut test](../../manual-testing/phone-and-shortcut-test.md).

## Done when
- [ ] The server runs online and asks for a login.
- [ ] A wrong password and no password both fail.
- [ ] The spending cap or your own limits are set and written down.
- [ ] Chat page works in your iPhone browser.
- [ ] Your data survives a redeploy (test it).
- [ ] The key is not visible in any page source.

## Risks
Public server spends money; data lost on redeploy. See [risk review](../../reviews/risk-review.md).

## If time runs short
Never cut login or the cap. Cut polish on the phone layout.

## Links to specs
[privacy and security](../../feature-specs/privacy-and-security.md) · [storage](../../feature-specs/storage.md) · [server API](../../feature-specs/server-api.md) · [frontend UI](../../feature-specs/frontend-ui.md)
