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
        ("see https://", []),
        (
            "see https://en.wikipedia.org/wiki/Foo_(bar).",
            ["https://en.wikipedia.org/wiki/Foo_(bar)"],
        ),
        ("https://example.com/a and https://example.com/a.", ["https://example.com/a"]),
    ],
)
def test_find_links(text, expected):
    assert intent.find_links(text) == expected
