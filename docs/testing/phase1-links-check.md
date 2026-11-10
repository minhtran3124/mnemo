# Phase 1 links check
Status: Draft v0.1 · Owner: KhoiTran · Phase: 1

The 5 links in "Phase 1 test set" of [sample links](../reference/sample-links.md) were pasted into the running app (`uv run python server.py`, bound to 127.0.0.1, run on 2026-11-05). The chat route `POST /api/chat` was called with the same body the page sends. Each saved title, type, tags and summary was read against the page text the app stored in `data/pages/<id>.txt`. A row is `ok` only when the summary holds no invented fact. For the unreadable case, `ok` means saved as link only with a null summary, then filled in through `POST /api/bookmarks/{id}/paste` with the same bookmark id.

## Results

| # | Link | What was checked | Result | Note |
| --- | --- | --- | --- | --- |
| 1 | Instagram login `instagram.com/accounts/login/` | Saved as link only, summary null, paste text fills it in | ok | Saved with `page_status` unreadable, `summary` null, empty tags. `POST /api/bookmarks/1/paste` with a 177-character note kept id 1 (no second copy), set `page_status` ok and wrote a summary that restates only the pasted text. |
| 2 | dev.to Pocket guide | Promotional article: summary holds only facts from the page | ok | Pocket shutdown on July 8, 2025, the October 2025 export deadline, Raindrop.io, Readwise Reader, Instapaper, Wallabag, Karakeep, the 24-hour timer, AI digests and the MCP server all appear in the page. The summary says "founder"; the page says "I built Burn 451", so this is a light paraphrase of the author, and the summary says the post promotes Burn 451. |
| 3 | Hugging Face blog `sionic-ai/claude-code-skills-training` | Normal article: title, type, tags, summary | ok | `/retrospective`, `/advise`, the shared registry, working code, parameters, failed attempts, templates, trigger conditions and PR validation all appear in the page. The 1,000+ experiments a day is in the title. |
| 4 | GitHub `subframe7536/maple-font` | Repo through the GitHub API: type `github_repo`, tags not forced into AI topics | ok | Tags are monospace-font, open-source, coding-font, nerd-font, terminal. Round corners, ligatures, Nerd-Font icons, variable weights, the CN 2:1 alignment, Scoop, Homebrew, Arch Linux, Nix and the browser, GitHub Actions, Docker and local builds all appear in the page. |
| 5 | GitHub `gyoridavid/ai_agents_az` | Repo: summary, and the same link with `?fbclid=abc` | ok | n8n templates for the AI Agents A-Z series, the Season 1 episodes named, and the short video maker MCP/REST and narrated story creator servers all appear in the page. The `fbclid` check is below. |

## Unreadable link: what was tried

The X post (`x.com/addyosmani/article/2117512471930167377`) was the first choice for row 1, but the app read it in full, so it could not show link only. An earlier run recorded that. The owner decided to replace it with a link that really cannot be read. Candidates, all public login pages (D-018):

| Link | What the app did |
| --- | --- |
| `https://www.instagram.com/accounts/login/` | Link only: `page_status` unreadable, `summary` null. Used as row 1. |
| `https://www.linkedin.com/login` | Link only: `page_status` unreadable, `summary` null. Not used. |
| `https://www.facebook.com/login/` | Read: `page_status` ok, a summary of the login page. Does not test the unreadable path. |

All three were pasted in one pass, so LinkedIn and Facebook were saved although Instagram had already worked. Their test bookmarks were deleted.

## `fbclid` check

`https://github.com/gyoridavid/ai_agents_az?fbclid=abc` was pasted after row 5. The saved record kept `url` as pasted and its `url_clean` was `https://github.com/gyoridavid/ai_agents_az`, equal to the `url_clean` of the first save. Result: same `url_clean`.

It was still saved as a new bookmark (id 8 next to id 7), so there is no "You saved this already" reply yet. The spec in [chat and intent](../feature-specs/chat-and-intent.md) lists that reply for an exact duplicate. **Open question:** which phase builds the cross-message duplicate check.

## Outcome

All 5 rows are fine: no summary held an invented fact. The `reason` fields on all bookmarks are marked `guess` by the app, as the rule requires. **Unverified:** that Instagram keeps returning an unreadable login page on later runs.
