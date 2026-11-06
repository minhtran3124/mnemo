import pytest

import config
import save
import store

URL = "https://example.com/post?utm_source=x&id=1"
RAW = "word   \n" * 100  # collapses to 499 chars, over the HTML floor


def good(**overrides):
    fields = {
        "title": "A post",
        "type": "article",
        "summary": "A short summary of the post.",
        "tags": ["Python", "testing", "web"],
        "reason": "Looks useful.",
    }
    fields.update(overrides)
    return save.SaveOutput(**fields)


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    return tmp_path


@pytest.fixture
def parse_calls(monkeypatch):
    state = {"replies": [good()], "calls": []}

    def fake(messages, output_format, system=None):
        state["calls"].append(messages)
        reply = state["replies"].pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(save.client, "parse", fake)
    return state


def assert_link_only(record):
    assert record["page_status"] == "unreadable"
    assert record["summary"] is None
    assert record["tags"] == []


def test_good_page_gives_ok_record_and_writes_nothing(parse_calls, data_dir):
    record = save.preview(URL, RAW)
    assert record["page_status"] == "ok"
    assert record["summary"]
    assert 3 <= len(record["tags"]) <= 6
    assert record["url_clean"] == "https://example.com/post?id=1"
    assert list(data_dir.iterdir()) == []


def test_short_text_and_none_give_link_only_without_claude(parse_calls):
    short = "x" * (config.MIN_TEXT_CHARS_HTML - 1)
    assert_link_only(save.preview(URL, short))
    assert_link_only(save.preview(URL, None))
    assert parse_calls["calls"] == []


def test_invalid_output_twice_gives_link_only(parse_calls, data_dir):
    parse_calls["replies"] = [good(tags=[]), good(tags=[])]
    assert_link_only(save.preview(URL, RAW))
    assert len(parse_calls["calls"]) == 2
    assert list(data_dir.iterdir()) == []


def test_saved_page_text_equals_normalise_text(parse_calls, monkeypatch):
    stored = {}

    def fake_add(fields, page_text):
        stored["text"] = page_text
        return fields

    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: save.fetcher.FetchOk(text=RAW, source="web")
    )
    monkeypatch.setattr(save.store, "add_bookmark", fake_add)
    save.save(URL)
    assert stored["text"] == save.normalise_text(RAW)
