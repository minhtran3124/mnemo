"""The filing step: Claude names a folder, code checks it (FO-01 to FO-04)."""

import pytest

import config
import fetcher
import save
import store

URL = "https://example.com/post"
LONG = "word " * 100


def output(**overrides):
    fields = {
        "title": "A post",
        "type": "article",
        "summary": "A short summary of the post.",
        "tags": ["python", "testing", "web"],
        "reason": "Looks useful.",
        "folder": config.UNSORTED,
    }
    fields.update(overrides)
    return save.SaveOutput(**fields)


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=LONG, source="web")
    )
    return tmp_path


@pytest.fixture
def parse_calls(monkeypatch):
    state = {"calls": [], "replies": [output()]}

    def fake(messages, output_format, system=None):
        state["calls"].append(output_format)
        reply = state["replies"].pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(save.client, "parse", fake)
    return state


def test_a_starter_folder_is_stored(parse_calls):
    parse_calls["replies"] = [output(folder="Learning")]

    record = save.save(URL)

    assert record["folder"] == "Learning"
    assert len(parse_calls["calls"]) == 1


def test_a_made_up_folder_is_rejected_and_logged(parse_calls, data_dir):
    parse_calls["replies"] = [output(folder="Archive")]

    record = save.save(URL)

    assert record["folder"] is None
    lines = store._read_lines(data_dir / "log.jsonl")
    rejected = [line for line in lines if line["event"] == "folder_rejected"]
    assert len(rejected) == 1
    assert rejected[0]["id"] == record["id"]
    assert rejected[0]["folder"] == "Archive"
    assert rejected[0]["url_clean"] == record["url_clean"]


def test_unsorted_stores_null_and_is_not_logged(parse_calls, data_dir):
    parse_calls["replies"] = [output(folder="Unsorted")]

    record = save.save(URL)

    assert record["folder"] is None
    lines = store._read_lines(data_dir / "log.jsonl")
    assert not [line for line in lines if line["event"] == "folder_rejected"]


def test_link_only_save_makes_no_filing_call(parse_calls, monkeypatch, data_dir):
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchFail("timed out")
    )

    record = save.save(URL)

    assert record["folder"] is None
    assert record["page_status"] == "unreadable"
    assert parse_calls["calls"] == []
    assert not (data_dir / "log.jsonl").exists()


def test_wrong_case_is_rejected_and_the_prompt_names_every_folder(parse_calls):
    parse_calls["replies"] = [output(folder="learning")]

    record = save.save(URL)

    assert record["folder"] is None
    assert len(parse_calls["calls"]) == 1
    prompt = save.PROMPT_FILE.read_text(encoding="utf-8")
    for name in (*config.STARTER_FOLDERS, config.UNSORTED):
        assert name in prompt
    assert "folder" in save.SaveOutput.model_json_schema()["properties"]
