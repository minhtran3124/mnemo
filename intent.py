"""Decide link versus question with plain code, never Claude (F-03).

docs/feature-specs/chat-and-intent.md. No network and no model call here.
"""

import re

# A link runs to the next whitespace, angle bracket or quote.
_LINK = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
# Punctuation that ends a sentence or closes a bracket, not part of the link.
_TRAILING = ".,)]!?;"
_PAIRS = {")": "(", "]": "["}


def _trim(link: str) -> str:
    """Strip trailing punctuation, keeping a closing bracket that has its opener."""
    while link and link[-1] in _TRAILING:
        end = link[-1]
        if end in _PAIRS and link.count(end) <= link.count(_PAIRS[end]):
            break
        link = link[:-1]
    return link


def find_links(text: str) -> list[str]:
    """Return the distinct http(s) links in the text, in order, without trailing punctuation."""
    links: list[str] = []
    for match in _LINK.finditer(text):
        link = _trim(match.group())
        if re.match(r"https?://.", link, re.IGNORECASE) and link not in links:
            links.append(link)
    return links


_EMPTY_BRACKETS = re.compile(r"\(\s*\)|\[\s*\]")
_COMMAND_WORD = re.compile(r"^(save|add)\b[\s:,-]*", re.IGNORECASE)


def find_reason(text: str) -> str | None:
    """Return the text around the links as the user's reason, or None if there is none.

    Links are removed, a leading "save" or "add" is dropped, and white space is
    collapsed to one line.
    """
    # Cut out only the trimmed link, as find_links reports it, so a closing
    # bracket or full stop after it stays with the sentence.
    stripped = _LINK.sub(
        lambda match: " " + match.group()[len(_trim(match.group())) :], text
    )
    stripped = _EMPTY_BRACKETS.sub(" ", stripped)
    rest = _COMMAND_WORD.sub("", stripped.strip())
    reason = " ".join(rest.split()).strip(" ,;:-.!?")
    return reason or None
