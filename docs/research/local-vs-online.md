# Local vs Online
Status: Draft v0.1 · Owner: KhoiTran · Phase: 0, A

This file compares three ways to run Mnemo and says what data leaves your computer in each.

## Options

| Option | Storage | Model | What leaves your machine | Course fit |
| --- | --- | --- | --- | --- |
| 1. Local storage plus Claude API | Your computer, plain files | Claude API | Page text, URL and questions go to Anthropic. The server also fetches pages from the internet. | Full |
| 2. Fully local model (for example Ollama) | Your computer | A model on your computer | Only the page fetch from the internet | Outside the course; contradicts D-001 |
| 3. Online host (phase A) | On the host | Claude API | Everything in option 1, plus your bookmarks live on the host | Partly (key rule only) |

Karakeep is said to support a local Ollama model (see [competitors](../reference/competitors.md)). Open question: whether a local model is good enough for Mnemo. It is not tested and is not planned.

## What each choice means for privacy
- With the Claude API, page text, URL and questions are sent to Anthropic. Unverified: Anthropic's data retention policy for the API. See [API notes](../reference/api-notes.md).
- Local storage keeps your bookmark file on your own disk. It does not stop the API call.
- A private link in private mode (F-19) is saved as link only and nothing is sent to the API.
- Check your company's AI policy before saving work links (D-018).

## Trade-offs

| Topic | Option 1 | Option 2 | Option 3 |
| --- | --- | --- | --- |
| Setup effort | Low | High (outside the course) | Medium |
| Works from phone | Only on your network if you allow it | Same | Yes |
| Cost | API use only | Hardware and time | Host plus API |
| Privacy | Page text goes to Anthropic | Best | Same as option 1, plus host risk |
| Spending risk | Low | None | Higher; needs login and cap |

## Recommendation
Use option 1 with a private switch (F-19). Build local first (D-007). Move to option 3 only in phase A, after the two-week test. Keep option 2 as an idea only. Open question: what you fear leaking, links or content (Q-11 in [open questions](open-questions.md)).

## Common mistakes
| Mistake | What happens | How to avoid it |
| --- | --- | --- |
| Binding the server to `0.0.0.0` | Other devices on the network can reach your server and your bookmarks | Bind to `127.0.0.1` |
| Committing `.env` | The key becomes public in git history | `.gitignore` before the first commit; see [git and secrets](../process/git-and-secrets.md) |
| Putting the key in a page or Shortcut | Anyone can read it | Key stays on the server (NF-01) |
| Going online with no login | Anyone can spend your money | Login, `max_tokens`, page length limit, spending cap (NF-02) |

Related: [privacy and security spec](../feature-specs/privacy-and-security.md), [phase A plan](../product/plans/phase-a-online-host.md).
