import pytest
from fastapi.testclient import TestClient

import store

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def seed(**overrides):
    record = {
        "url": "https://www.example.com/a?x=1",
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
    return store.add_bookmark(record, page_text="page body")


def test_page_is_served_with_header_and_no_move_or_banner(client):
    seed()

    response = client.get("/bookmarks")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert 'class="site-header"' in response.text
    assert "Move" not in response.text
    assert "Needs a look" not in response.text


def test_row_shows_fields_and_escapes_text(client):
    seed(title="<script>alert(1)</script>", tags=["alpha", "beta", "gamma"])

    text = client.get("/bookmarks").text

    assert "<script>alert(1)</script>" not in text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    assert "article" in text
    assert "www.example.com" in text
    for tag in ("alpha", "beta", "gamma"):
        assert tag in text
    assert store.list_bookmarks()[0]["saved_at"][:10] in text


def test_guess_reason_is_flagged_and_user_reason_is_not(client):
    seed(reason="Looks useful for login work", reason_source="guess")
    guess_text = client.get("/bookmarks").text
    assert "Looks useful for login work" in guess_text
    assert "guess" in guess_text.lower()

    store.delete_bookmark(1)
    seed(reason="Needed for my talk", reason_source="user")
    user_text = client.get("/bookmarks").text
    assert "Needed for my talk" in user_text
    assert "guess" not in user_text.lower()


def test_unreadable_bookmark_shows_badge_and_banner(client):
    seed(page_status="unreadable", summary=None, title="Locked page")

    text = client.get("/bookmarks").text

    assert "page not read" in text
    assert "Needs a look" in text


def test_title_link_carries_the_open_url(client):
    saved = seed()

    text = client.get("/bookmarks").text

    assert f'data-open-url="/api/bookmarks/{saved["id"]}/open"' in text
    assert 'href="https://www.example.com/a?x=1"' in text.replace("&amp;", "&")


def test_delete_button_carries_delete_url_and_confirm_text(client):
    saved = seed(title="Quarterly plan")

    text = client.get("/bookmarks").text

    assert f'data-delete-url="/api/bookmarks/{saved["id"]}"' in text
    assert 'data-confirm="' in text
    confirm = text.split('data-confirm="', 1)[1].split('"', 1)[0]
    assert "Quarterly plan" in confirm


def test_unknown_type_still_shows_under_other(client, monkeypatch):
    seed(title="Known one")
    odd = seed(title="Odd one")
    odd["type"] = "podcast"
    monkeypatch.setattr(store, "list_bookmarks", lambda *a, **k: [odd])

    response = client.get("/bookmarks")

    assert "Odd one" in response.text
    assert 'data-type="other"' in response.text


def test_record_missing_optional_fields_does_not_break_the_page(client, monkeypatch):
    bare = {"id": 7, "url": "https://example.com/bare", "reason": "why"}
    monkeypatch.setattr(store, "list_bookmarks", lambda *a, **k: [bare])

    response = client.get("/bookmarks")

    assert response.status_code == 200
    assert "https://example.com/bare" in response.text


def test_open_and_tags_survive_a_bare_record(client, monkeypatch):
    bare = {"id": 7, "url": "https://example.com/bare", "tags": "abc"}
    stored = {}
    monkeypatch.setattr(store, "list_bookmarks", lambda *a, **k: [bare])
    monkeypatch.setattr(store, "get_bookmark", lambda i: bare)
    monkeypatch.setattr(
        store, "update_bookmark", lambda i, f: stored.update(f) or {**bare, **f}
    )
    monkeypatch.setattr(store, "log_event", lambda e: None)

    page = client.get("/bookmarks")
    response = client.post("/api/bookmarks/7/open")

    assert "<li>a</li>" not in page.text
    assert response.status_code == 200
    assert stored == {"opened_count": 1}


def test_page_gives_the_script_what_it_needs_after_a_delete(client):
    seed(page_status="unreadable", summary=None, title="Locked page")
    seed(url="https://example.com/b", url_clean="https://example.com/b")

    text = client.get("/bookmarks").text

    assert 'id="bm-banner"' in text
    assert text.count('data-unreadable="true"') == 1
    assert '<p class="empty" id="bm-empty" hidden>' in text


def test_empty_page_shows_the_empty_message_unhidden(client):
    text = client.get("/bookmarks").text

    assert '<p class="empty" id="bm-empty">' in text
    assert 'id="bm-banner"' not in text


NODE_HARNESS = """
const fs = require("fs");
let handler;
const status = { textContent: "", hidden: true };
const button = {
  disabled: false,
  textContent: "Delete",
  getAttribute: (n) => (n === "data-confirm" ? "Sure?" : "/x"),
  closest: () => row,
};
const row = { closest: () => null, remove() {} };
global.window = { confirm: () => true };
global.fetch = () => Promise.resolve({ ok: true });
global.document = {
  getElementById: (id) => (id === "bm-status" ? status : { remove() {}, hidden: false }),
  querySelector: () => {
    throw new Error("cleanup fault");
  },
  addEventListener: (_, fn) => (handler = fn),
};
eval(fs.readFileSync(process.argv[2], "utf8"));
process.on("unhandledRejection", () => {});
handler({ target: { closest: (sel) => (sel.startsWith("button") ? button : null) } });
setTimeout(() => {
  console.log(JSON.stringify({ status: status.textContent, disabled: button.disabled }));
}, 20);
"""


def test_cleanup_fault_after_a_good_delete_does_not_show_a_false_error(tmp_path):
    import json
    import shutil
    import subprocess
    from pathlib import Path

    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed")
    harness = tmp_path / "harness.js"
    harness.write_text(NODE_HARNESS)
    script = Path(__file__).resolve().parent.parent / "web" / "js" / "bookmarks.js"

    result = subprocess.run(
        [node, str(harness), str(script)],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout.strip().splitlines()[-1]) == {
        "status": "",
        "disabled": True,
    }
