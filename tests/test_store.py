import json
import os

import pytest

import store


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    return tmp_path


def make_record(**overrides):
    record = {
        "url": "https://example.com/a",
        "url_clean": "https://example.com/a",
        "type": "article",
        "title": "An article",
        "page_status": "ok",
        "summary": "A short summary.",
        "tags": ["testing", "login", "python"],
        "reason": "",
        "reason_source": "guess",
        "folder": None,
        "opened_count": 0,
    }
    record.update(overrides)
    return record


def test_create_and_get(data_dir):
    saved = store.add_bookmark(make_record(), page_text="page body")
    assert saved["id"] == 1
    assert saved["page_file"] == "data/pages/1.txt"
    assert saved["saved_at"]
    assert store.get_bookmark(1) == saved
    assert store.get_bookmark(99) is None
    assert store.find_by_url_clean("https://example.com/a") == saved
    assert store.find_by_url_clean("") is None
    stored = json.loads((data_dir / "bookmarks.json").read_text(encoding="utf-8"))
    assert stored["next_id"] == 2


def test_list_in_order_with_filters():
    store.add_bookmark(make_record(title="one", folder="Work"))
    store.add_bookmark(make_record(title="two", type="tool", tags=["a", "b", "c"]))
    store.add_bookmark(make_record(title="three", folder="Work"))
    assert [b["title"] for b in store.list_bookmarks()] == ["one", "two", "three"]
    assert [b["title"] for b in store.list_bookmarks({"folder": "Work"})] == [
        "one",
        "three",
    ]
    assert [b["title"] for b in store.list_bookmarks({"type": "tool"})] == ["two"]
    assert [b["title"] for b in store.list_bookmarks({"tag": "a"})] == ["two"]
    assert store.list_folders() == [{"folder": "Work", "count": 2}]


def test_update_fields():
    store.add_bookmark(make_record())
    updated = store.update_bookmark(1, {"folder": "Work", "opened_count": 3})
    assert updated["folder"] == "Work"
    assert store.get_bookmark(1)["opened_count"] == 3
    with pytest.raises(store.InvalidRecord):
        store.update_bookmark(1, {"tags": ["Upper", "b", "c"]})
    with pytest.raises(store.InvalidRecord):
        store.update_bookmark(1, {"id": 7})
    with pytest.raises(store.NotFound):
        store.update_bookmark(42, {"folder": "Work"})
    assert store.get_bookmark(1)["tags"] == ["testing", "login", "python"]


def test_delete_removes_page_and_id_not_reused(data_dir):
    store.add_bookmark(make_record(), page_text="one")
    store.add_bookmark(make_record(), page_text="two")
    store.delete_bookmark(2)
    assert store.get_bookmark(2) is None
    assert not (data_dir / "pages" / "2.txt").exists()
    assert (data_dir / "pages" / "1.txt").exists()
    third = store.add_bookmark(make_record())
    assert third["id"] == 3
    with pytest.raises(store.NotFound):
        store.delete_bookmark(2)


def test_page_text_round_trip():
    store.add_bookmark(make_record(), page_text="café text\nline two")
    assert store.read_page(1) == "café text\nline two"
    store.add_bookmark(make_record())
    assert store.read_page(2) is None


def test_chat_append_and_read(data_dir):
    first = store.append_chat({"role": "user", "text": "hello"})
    second = store.append_chat({"role": "app", "text": "saved", "bookmark_ids": [1]})
    assert (first["id"], second["id"]) == (1, 2)
    assert second["bookmark_ids"] == [1]
    store.append_chat({"role": "user", "text": "third"})
    assert [m["text"] for m in store.list_chat(2)] == ["saved", "third"]
    assert len(store.list_chat()) == 3
    lines = (data_dir / "chat.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["id"] for line in lines] == [1, 2, 3]
    with pytest.raises(store.InvalidRecord):
        store.append_chat({"role": "bot", "text": "x"})


def test_log_append(data_dir):
    store.log_event({"event": "open", "id": 1})
    store.log_event({"event": "save", "id": 2})
    lines = (data_dir / "log.jsonl").read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in lines]
    assert [e["event"] for e in events] == ["open", "save"]
    assert all(e["time"] for e in events)
    with pytest.raises(store.InvalidRecord):
        store.log_event({"id": 1})


def test_atomic_write_keeps_old_file_whole(data_dir, monkeypatch):
    store.add_bookmark(make_record(title="first"))
    path = data_dir / "bookmarks.json"
    before = path.read_text(encoding="utf-8")

    def fail(*args, **kwargs):
        raise OSError("disk gone")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        store.add_bookmark(make_record(title="second"))
    monkeypatch.undo()
    assert path.read_text(encoding="utf-8") == before
    assert json.loads(before)["bookmarks"][0]["title"] == "first"
    assert not [p for p in data_dir.iterdir() if p.suffix == ".tmp"]


def test_stored_fields_match_data_model_and_bad_records_rejected(data_dir):
    saved = store.add_bookmark(make_record())
    assert set(saved) == set(store.ALL_FIELDS)

    bad_cases = [
        {"title": None},
        {"type": "podcast"},
        {"tags": ["Login", "b", "c"]},
        {"page_status": "unreadable", "summary": "I made this up"},
        {"summary": " ".join(["word"] * 61)},
        {"tags": ["a", "b"]},
        {"tags": ["a", "b", "c", "d", "e", "f", "g"]},
        {"reason_source": "maybe"},
        {"id": 5},
    ]
    for overrides in bad_cases:
        with pytest.raises(store.InvalidRecord):
            store.add_bookmark(make_record(**overrides))
    missing = make_record()
    del missing["folder"]
    with pytest.raises(store.InvalidRecord):
        store.add_bookmark(missing)
    assert len(store.list_bookmarks()) == 1
    assert store.get_bookmark(2) is None

    link_only = store.add_bookmark(
        make_record(page_status="unreadable", summary=None, tags=[])
    )
    assert link_only["summary"] is None
    assert link_only["id"] == 2

    (data_dir / "bookmarks.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(store.StoreError):
        store.add_bookmark(make_record())
    assert (data_dir / "bookmarks.json").read_text(encoding="utf-8") == "{not json"


def test_failed_add_leaves_no_orphan_page(data_dir, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("disk gone")

    with monkeypatch.context() as m:
        m.setattr(store, "_save", fail)
        with pytest.raises(OSError):
            store.add_bookmark(make_record(), page_text="text the app saw")
    assert store.read_page(1) is None
    store.add_bookmark(make_record(page_status="unreadable", summary=None))
    assert store.read_page(1) is None


def test_chat_survives_torn_last_line(data_dir):
    store.append_chat({"role": "user", "text": "one"})
    with (data_dir / "chat.jsonl").open("a", encoding="utf-8") as f:
        f.write('{"id": 2, "time": "2026')  # crash mid-append
    assert [m["text"] for m in store.list_chat()] == ["one"]
    added = store.append_chat({"role": "app", "text": "two"})
    assert added["id"] == 2
    assert [m["text"] for m in store.list_chat()] == ["one", "two"]


def test_chat_bad_middle_line_still_raises(data_dir):
    (data_dir / "chat.jsonl").write_text('not json\n{"id": 2}\n', encoding="utf-8")
    with pytest.raises(store.StoreError):
        store.list_chat()
