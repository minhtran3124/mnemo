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


def seed(**overrides):
    return store.add_bookmark(make_record(**overrides), page_text="page body")


def test_list_returns_saved_bookmarks(client):
    first = seed()
    second = seed(url_clean="https://example.com/b")

    response = client.get("/api/bookmarks")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [first["id"], second["id"]]


def test_open_raises_opened_count_by_one(client):
    saved = seed()

    response = client.post(f"/api/bookmarks/{saved['id']}/open")

    assert response.status_code == 200
    assert response.json()["opened_count"] == 1
    assert store.get_bookmark(saved["id"])["opened_count"] == 1


def test_open_writes_one_open_log_line(client, tmp_path):
    saved = seed()

    client.post(f"/api/bookmarks/{saved['id']}/open")

    lines = store._read_lines(tmp_path / "log.jsonl")
    assert len(lines) == 1
    assert lines[0]["event"] == "open"
    assert lines[0]["id"] == saved["id"]


def test_open_unknown_id_gives_404(client):
    response = client.post("/api/bookmarks/99/open")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "bookmark_not_found"


def test_delete_removes_the_bookmark(client):
    saved = seed()

    response = client.delete(f"/api/bookmarks/{saved['id']}")

    assert response.status_code == 200
    assert response.json() == {"deleted": saved["id"]}
    assert store.get_bookmark(saved["id"]) is None


def test_delete_removes_the_page_text_file(client, tmp_path):
    saved = seed()
    page = tmp_path / "pages" / f"{saved['id']}.txt"
    assert page.exists()

    client.delete(f"/api/bookmarks/{saved['id']}")

    assert store.read_page(saved["id"]) is None
    assert not page.exists()


def test_delete_unknown_id_gives_404(client):
    response = client.delete("/api/bookmarks/99")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "bookmark_not_found"


@pytest.fixture
def slow_load(monkeypatch):
    """Pause after every read so unlocked read-modify-write steps must overlap."""
    import time

    real_load = store._load

    def load():
        data = real_load()
        time.sleep(0.02)
        return data

    monkeypatch.setattr(store, "_load", load)


def test_concurrent_opens_do_not_lose_updates(client, slow_load):
    from concurrent.futures import ThreadPoolExecutor

    item = seed()
    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(
            pool.map(
                lambda _: client.post(f"/api/bookmarks/{item['id']}/open").status_code,
                range(10),
            )
        )

    assert set(codes) == {200}
    assert store.get_bookmark(item["id"])["opened_count"] == 10


def test_concurrent_deletes_do_not_bring_a_bookmark_back(client, slow_load):
    from concurrent.futures import ThreadPoolExecutor

    items = [seed(url_clean=f"https://example.com/{n}") for n in range(6)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        codes = list(
            pool.map(
                lambda item: client.delete(f"/api/bookmarks/{item['id']}").status_code,
                items,
            )
        )

    assert set(codes) == {200}
    assert store.list_bookmarks() == []


def test_concurrent_delete_and_open_keep_both_changes(client, slow_load):
    from concurrent.futures import ThreadPoolExecutor

    gone, kept = seed(), seed(url_clean="https://example.com/b")
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [
            pool.submit(client.delete, f"/api/bookmarks/{gone['id']}"),
            pool.submit(client.post, f"/api/bookmarks/{kept['id']}/open"),
        ]
        codes = [job.result().status_code for job in jobs]

    assert codes == [200, 200]
    assert store.get_bookmark(gone["id"]) is None
    assert store.get_bookmark(kept["id"])["opened_count"] == 1


def test_unhandled_store_error_returns_json_500(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    def corrupt():
        raise store.StoreError("bookmarks.json is corrupt at /secret/path")

    monkeypatch.setattr(store, "list_bookmarks", corrupt)
    client = TestClient(server.app, raise_server_exceptions=False)
    response = client.get("/api/bookmarks")
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "server_error",
            "message": "Something went wrong on the server.",
        }
    }


def test_wrong_method_gives_405_with_allow_header(client):
    response = client.put("/api/bookmarks")

    assert response.status_code == 405
    assert "GET" in response.headers["allow"]
    assert response.json()["error"]["code"] == "http_405"
