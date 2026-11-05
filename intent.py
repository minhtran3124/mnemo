"""Decide link versus question with plain code, never Claude (F-03).

docs/feature-specs/chat-and-intent.md. No network and no model call here.
"""

import re

# A link runs to the next whitespace, angle bracket or quote.
_LINK = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_PUNCTUATION = ".,;:!?"
_CLOSERS = {")": "(", "]": "[", "}": "{"}


def _trim(link: str) -> str:
    """Strip trailing punctuation and closing brackets that have no opener in the link."""
    while link:
        last = link[-1]
        if last in _PUNCTUATION or (
            last in _CLOSERS and link.count(last) > link.count(_CLOSERS[last])
        ):
            link = link[:-1]
        else:
            break
    return link


def find_links(text: str) -> list[str]:
    """Return the distinct http(s) links in the text, in order."""
    links: list[str] = []
    for match in _LINK.finditer(text):
        link = _trim(match.group())
        if re.match(r"https?://.", link, re.IGNORECASE) and link not in links:
            links.append(link)
    return links
