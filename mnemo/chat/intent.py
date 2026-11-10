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


# `note`, then an optional id of digits, then optional text.
_NOTE = re.compile(r"note(?:\s+(\d+))?(?:\s+(.*))?", re.IGNORECASE | re.DOTALL)


def parse_note(message: str) -> tuple[int | None, str | None] | None:
    """Read a `note <id> <text>` command.

    Return None when the message is not a note command. Otherwise return
    (id or None, text or None); a missing part gets the "what should it say" reply.
    """
    match = _NOTE.fullmatch(message.strip())
    if match is None:
        return None
    raw_id, raw_text = match.groups()
    if raw_id is None and raw_text is not None:
        return None  # `note abc x` is not a note command
    text = raw_text.strip() if raw_text else None
    return (int(raw_id) if raw_id else None, text or None)


_PRIVATE = re.compile(r"private\s+", re.IGNORECASE)


def is_private(message: str) -> bool:
    """True when the message starts with the `private` prefix (F-19).

    The caller checks for a link first: `private` with no link is a question.
    """
    return _PRIVATE.match(message.strip()) is not None
