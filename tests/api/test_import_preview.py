"""The import preview: link count and cost estimate before any API call (IM-04)."""

import pytest
from fastapi.testclient import TestClient

from mnemo.core import store
from mnemo.save import pipeline as save

FAKE_KEY = "sk-ant-fake-key-for-tests"

EXPORT_5 = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><A HREF="https://example.com/one">One</A>
    <DT><A HREF="https://example.com/two?utm_source=mail">Two</A>
    <DT><A HREF="https://example.com/three">Three</A>
    <DT><A HREF="http://example.com/four">Four</A>
    <DT><A HREF="https://example.com/five#top">Five</A>
</DL><p>
"""


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    from mnemo.api import server

    return TestClient(server.app)


def make_record(**overrides):
    record = {
        "url": "https://example.com/two?utm_source=mail",
        "url_clean": "https://example.com/two",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["testing", "import", "python"],
        "reason": "",
        "reason_source": "guess",
        "folder": None,
        "opened_count": 0,
    }
    record.update(overrides)
    return record


def test_five_link_export_returns_the_count_and_a_numeric_estimate(client):
    response = client.post("/api/import/preview", json={"file": EXPORT_5})

    assert response.status_code == 200
    body = response.json()
    assert body["found"] == 5
    assert body["new"] == 5
    assert body["already_saved"] == 0
    assert body["slack"] == 0
    assert isinstance(body["estimate"], int | float)
    assert body["estimate"] == pytest.approx(0.03)


def test_pasted_text_with_two_links_returns_two(client):
    text = "two reads: https://example.com/a and http://example.com/b, the rest is chat"

    response = client.post("/api/import/preview", json={"text": text})

    assert response.status_code == 200
    assert response.json()["found"] == 2


def test_a_saved_link_is_counted_as_already_saved_not_new(client):
    store.add_bookmark(make_record(), page_text="page body")

    response = client.post("/api/import/preview", json={"file": EXPORT_5})

    body = response.json()
    assert body["found"] == 5
    assert body["already_saved"] == 1
    assert body["new"] == 4
    assert body["estimate"] == pytest.approx(0.024)


def test_the_preview_makes_no_fetch_and_no_claude_call(client, monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("the import preview must not fetch or call Claude")

    monkeypatch.setattr(save.fetcher, "fetch", fail)
    monkeypatch.setattr(save.client, "parse", fail)

    response = client.post("/api/import/preview", json={"file": EXPORT_5})

    assert response.status_code == 200
    assert response.json()["found"] == 5


def test_text_with_no_link_returns_no_links_found(client):
    response = client.post(
        "/api/import/preview", json={"text": "what is a bookmark? no links here"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "found": 0,
        "new": 0,
        "already_saved": 0,
        "slack": 0,
        "estimate": 0.0,
        "message": "No links found.",
    }
