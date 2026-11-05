"""Decide link versus question with plain code, never Claude (F-03).

docs/feature-specs/chat-and-intent.md. No network and no model call here.
"""

import re

# A link runs to the next whitespace, angle bracket or quote.
_LINK = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
# Punctuation that ends a sentence or closes a bracket, not part of the link.
_TRAILING = ".,)]!?;"


def find_links(text: str) -> list[str]:
    """Return the http(s) links in the text, in order, without trailing punctuation."""
    links = []
    for match in _LINK.finditer(text):
        link = match.group().rstrip(_TRAILING)
        if re.match(r"https?://.", link, re.IGNORECASE):
            links.append(link)
    return links
