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
    ],
)
def test_find_links(text, expected):
    assert intent.find_links(text) == expected


def test_intent_imports_no_client_or_fetcher():
    source = open(intent.__file__, encoding="utf-8").read()
    for name in ("import client", "anthropic", "import fetcher"):
        assert name not in source
