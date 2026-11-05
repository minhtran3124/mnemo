import anthropic
import httpx2
import pytest

import config
import fetcher
import save
import store
import urlclean

URL = "https://example.com/post?utm_source=x&id=1"
LONG = "word " * 100  # 499 chars once collapsed, over the HTML floor


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
def fetch_calls(monkeypatch):
    calls = []

    def fake(url):
        calls.append(url)
        return fetcher.FetchOk(text=LONG, source="web")

    monkeypatch.setattr(save.fetcher, "fetch", fake)
    return calls


@pytest.fixture
def parse_calls(monkeypatch):
    """Queue of replies: an output, or an exception to raise. Returns call log."""
    state = {"replies": [good()], "calls": []}

    def fake(messages, output_format, system=None):
        state["calls"].append({"messages": messages, "system": system})
        reply = state["replies"].pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(save.client, "parse", fake)
    return state


def assert_link_only(record, data_dir):
    assert record["page_status"] == "unreadable"
    assert record["summary"] is None
    assert record["tags"] == []
    assert record["reason_source"] == "guess"
    assert record["title"] == "example.com"
    assert not (data_dir / "pages").exists() or not list((data_dir / "pages").iterdir())


def test_valid_output_is_saved(fetch_calls, parse_calls):
    record = save.save(URL)
    assert record["url"] == URL
    assert record["url_clean"] == urlclean.clean_url(URL)
    assert record["page_status"] == "ok"
    assert record["reason_source"] == "guess"
    assert record["folder"] is None
    assert record["tags"] == ["python", "testing", "web"]
    assert len(record["summary"].split()) <= 60
    assert store.get_bookmark(record["id"]) == record
    assert (store.DATA_DIR / "pages" / f"{record['id']}.txt").exists()
    assert "page" in parse_calls["calls"][0]["system"].lower()


def test_wrong_tag_count_retries_once(fetch_calls, parse_calls):
    parse_calls["replies"] = [good(tags=["a", "b"]), good()]
    record = save.save(URL)
    assert len(parse_calls["calls"]) == 2
    assert record["page_status"] == "ok"


def test_duplicate_tags_after_lowercasing_do_not_count(fetch_calls, parse_calls):
    parse_calls["replies"] = [good(tags=["Python", "python", "PYTHON"]), good()]
    record = save.save(URL)
    assert len(parse_calls["calls"]) == 2
    assert record["tags"] == ["python", "testing", "web"]


def test_invalid_twice_saves_link_only(fetch_calls, parse_calls, data_dir):
    parse_calls["replies"] = [good(tags=["a"]), good(summary="word " * 61)]
    record = save.save(URL)
    assert len(parse_calls["calls"]) == 2
    assert_link_only(record, data_dir)


def test_runtime_error_retries_then_link_only(fetch_calls, parse_calls, data_dir):
    parse_calls["replies"] = [RuntimeError("refused"), RuntimeError("refused")]
    record = save.save(URL)
    assert len(parse_calls["calls"]) == 2
    assert_link_only(record, data_dir)


def test_api_error_retries_then_link_only(fetch_calls, parse_calls, data_dir):
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    error = anthropic.APIConnectionError(request=request)
    parse_calls["replies"] = [error, error]
    record = save.save(URL)
    assert len(parse_calls["calls"]) == 2
    assert_link_only(record, data_dir)


@pytest.mark.parametrize("status", [400, 401, 403])
def test_permanent_api_error_retries_then_link_only(
    fetch_calls, parse_calls, data_dir, status
):
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx2.Response(status, request=request)
    error_cls = {
        400: anthropic.BadRequestError,
        401: anthropic.AuthenticationError,
        403: anthropic.PermissionDeniedError,
    }[status]
    error = error_cls("denied", response=response, body=None)
    parse_calls["replies"] = [error, error]
    record = save.save(URL)
    assert len(parse_calls["calls"]) == 2
    assert_link_only(record, data_dir)


def test_fetch_failure_saves_link_only(monkeypatch, parse_calls, data_dir):
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchFail("timed out")
    )
    record = save.save(URL)
    assert_link_only(record, data_dir)


def test_text_under_floor_saves_link_only(monkeypatch, parse_calls, data_dir):
    short = "x" * (config.MIN_TEXT_CHARS_HTML - 1)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=short, source="web")
    )
    record = save.save(URL)
    assert_link_only(record, data_dir)
    assert parse_calls["calls"] == []


def test_pasted_text_skips_fetcher(fetch_calls, parse_calls):
    record = save.save(URL, pasted_text="a" * config.MIN_TEXT_CHARS_GITHUB)
    assert fetch_calls == []
    assert record["page_status"] == "ok"
    assert len(parse_calls["calls"]) == 1


def test_page_text_wrapped_and_capped(monkeypatch, parse_calls):
    big = "z" * (config.MAX_PAGE_CHARS * 2)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=big, source="web")
    )
    save.save(URL)
    content = parse_calls["calls"][0]["messages"][0]["content"]
    assert content.startswith("<page>") and content.rstrip().endswith("</page>")
    assert content.count("z") == config.MAX_PAGE_CHARS


def test_github_floor_and_no_parse_for_unreadable(monkeypatch, parse_calls, data_dir):
    monkeypatch.setattr(
        save.fetcher,
        "fetch",
        lambda url: fetcher.FetchOk(
            text="y" * config.MIN_TEXT_CHARS_GITHUB, source="github"
        ),
    )
    assert save.save("https://github.com/a/b")["page_status"] == "ok"
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchFail("not found")
    )
    before = len(parse_calls["calls"])
    parse_calls["replies"] = []
    save.save(URL)
    assert len(parse_calls["calls"]) == before


def test_tiny_pasted_text_saves_link_only(fetch_calls, parse_calls, data_dir):
    record = save.save(URL, pasted_text="x")
    assert fetch_calls == []
    assert_link_only(record, data_dir)
    assert parse_calls["calls"] == []


def test_stored_page_text_keeps_layout_and_is_capped(
    data_dir, monkeypatch, parse_calls
):
    code = "def f():\n    return 1\n"
    raw = code * 50 + "z" * (config.MAX_PAGE_CHARS * 2)
    monkeypatch.setattr(
        save.fetcher, "fetch", lambda url: fetcher.FetchOk(text=raw, source="web")
    )
    record = save.save(URL)
    stored = next(data_dir.rglob("*.txt")).read_text(encoding="utf-8")
    assert stored.startswith("def f():\n    return 1\n")
    assert len(stored) == config.MAX_PAGE_CHARS
    assert record["page_status"] == "ok"
