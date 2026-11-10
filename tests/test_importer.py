import pytest

from importer import links_from_browser_export, links_from_text

EXPORT = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><A HREF="https://example.com/one" ADD_DATE="1">One</A>
    <DT><A HREF="https://example.com/two?utm_source=mail">Two</A>
    <DT><H3>Folder</H3>
    <DL><p>
        <DT><A HREF="https://example.com/three">Three</A>
        <DT><A HREF="http://example.com/four">Four</A>
    </DL><p>
    <DT><A HREF="https://example.com/five#top">Five</A>
</DL><p>
"""


def test_browser_export_finds_all_links():
    found = links_from_browser_export(EXPORT)
    assert [item["url"] for item in found] == [
        "https://example.com/one",
        "https://example.com/two?utm_source=mail",
        "https://example.com/three",
        "http://example.com/four",
        "https://example.com/five#top",
    ]


def test_pasted_slack_text_returns_both_links():
    text = "two reads: https://example.com/a and http://example.com/b. the rest is chat"
    found = links_from_text(text)
    assert [item["url_clean"] for item in found] == [
        "https://example.com/a",
        "http://example.com/b",
    ]


def test_duplicate_in_export_returns_one_cleaned_link():
    html = """
    <DL><p>
        <DT><A HREF="https://example.com/a?utm_source=mail">First</A>
        <DT><A HREF="https://example.com/a?utm_source=chat">Again</A>
    </DL><p>
    """
    found = links_from_browser_export(html)
    assert len(found) == 1
    assert found[0]["url"] == "https://example.com/a?utm_source=mail"
    assert found[0]["url_clean"] == "https://example.com/a"


def test_non_web_links_are_rejected():
    html = """
    <DL><p>
        <DT><A HREF="about:blank#blocked">Blocked</A>
        <DT><A HREF="javascript:alert(1)">Script</A>
        <DT><A HREF="file:///home/me/notes.txt">Local</A>
        <DT><A HREF="https://example.com/ok">Ok</A>
    </DL><p>
    """
    found = links_from_browser_export(html)
    assert [item["url"] for item in found] == ["https://example.com/ok"]


def test_text_with_no_link_returns_empty_list():
    assert links_from_text("what is a bookmark? no links here") == []


def test_slack_archive_link_is_flagged():
    text = "see https://team.slack.com/archives/C123/p456 for the thread"
    found = links_from_text(text)
    assert len(found) == 1
    assert found[0]["slack"] is True


def test_order_and_tracking_cleaning():
    text = (
        "https://example.com/b?fbclid=z "
        "https://example.com/a?b=2&utm_medium=x&a=1 "
        "https://example.com/b?fbclid=other"
    )
    found = links_from_text(text)
    assert [item["url_clean"] for item in found] == [
        "https://example.com/b",
        "https://example.com/a?b=2&a=1",
    ]


def test_slack_pages_outside_archives_are_not_flagged():
    found = links_from_text(
        "https://team.slack.com/ and https://example.com/archives/C123"
    )
    assert [item["slack"] for item in found] == [False, False]


def test_empty_text_is_empty_and_non_string_raises():
    assert links_from_text("") == []
    assert links_from_browser_export("") == []
    with pytest.raises(ValueError):
        links_from_text(None)
    with pytest.raises(ValueError):
        links_from_browser_export(None)
