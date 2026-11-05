import pytest
from fastapi.testclient import TestClient

import store


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake-key-for-tests")
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    import server

    return TestClient(server.app)


def test_foreign_host_is_refused_so_dns_rebinding_cannot_read_the_list(client):
    response = client.get("/api/bookmarks", headers={"Host": "evil.example:8000"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden_host"


def test_foreign_origin_cannot_delete_or_open(client):
    headers = {"Host": "127.0.0.1:8000", "Origin": "http://evil.example:8000"}

    deleted = client.delete("/api/bookmarks/1", headers=headers)
    opened = client.post("/api/bookmarks/1/open", headers=headers)

    assert deleted.status_code == 403
    assert opened.status_code == 403
    assert deleted.json()["error"]["code"] == "forbidden_origin"


def test_loopback_host_and_origin_pass_the_check(client):
    headers = {"Host": "localhost:8000", "Origin": "http://localhost:8000"}

    response = client.post("/api/bookmarks/999999/open", headers=headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "bookmark_not_found"
