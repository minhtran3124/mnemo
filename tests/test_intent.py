from pathlib import Path

import pytest

import intent


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("see https://example.com/a", ["https://example.com/a"]),
        ("(https://example.com/a).", ["https://example.com/a"]),
        ("wow https://example.com/a?x=1!", ["https://example.com/a?x=1"]),
        (
            "http://a.com/x, then https://b.com/y; done",
            ["http://a.com/x", "https://b.com/y"],
        ),
        ("what is a bookmark?", []),
        ("", []),
        ("see https://", []),
        ("[x](https://example.com/a)", ["https://example.com/a"]),
        (
            "see https://en.wikipedia.org/wiki/Foo_(bar).",
            ["https://en.wikipedia.org/wiki/Foo_(bar)"],
        ),
        (
            "(https://en.wikipedia.org/wiki/Foo_(bar))",
            ["https://en.wikipedia.org/wiki/Foo_(bar)"],
        ),
        (
            "https://example.com/a and again https://example.com/a.",
            ["https://example.com/a"],
        ),
    ],
)
def test_find_links(text, expected):
    assert intent.find_links(text) == expected


def test_intent_imports_no_client_or_fetcher():
    source = Path(intent.__file__).read_text(encoding="utf-8")
    for name in ("import client", "anthropic", "import fetcher"):
        assert name not in source


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("https://a.com for login tests", "for login tests"),
        ("for login tests https://a.com/x.", "for login tests"),
        ("save https://a.com", None),
        ("https://a.com https://b.com", None),
        ("  https://a.com  ", None),
        ("[docs](https://a.com/x) for tests", "[docs] for tests"),
        ("see (https://a.com/x) for tests", "see for tests"),
        ("wiki https://a.com/w_(x) page", "wiki page"),
    ],
)
def test_find_reason(text, expected):
    assert intent.find_reason(text) == expected
