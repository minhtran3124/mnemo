import pytest
from fastapi.testclient import TestClient

FAKE_KEY = "sk-ant-fake-key-for-tests"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    import server

    app = server.create_app()

    @app.get("/_test/items/{item_id}")
    def item(item_id: int) -> dict:
        return {"id": item_id}

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


def test_host_is_loopback_and_start_passes_it_to_uvicorn(monkeypatch):
    import config
    import server

    calls = []
    monkeypatch.setattr(server.uvicorn, "run", lambda *a, **kw: calls.append((a, kw)))

    server.main()

    assert server.HOST == "127.0.0.1"
    assert len(calls) == 1
    assert calls[0][1]["host"] == "127.0.0.1"
    assert calls[0][1]["port"] == config.PORT


def test_unknown_route_gives_404_error_format(client):
    response = client.get("/no/such/route")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert isinstance(body["error"]["message"], str)
    assert set(body) == {"error"}


def test_validation_error_gives_400_error_format(client):
    response = client.get("/_test/items/not-a-number")

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "bad_request"
    assert isinstance(body["error"]["message"], str)
    assert set(body) == {"error"}


def test_error_bodies_never_contain_the_api_key(client):
    not_found = client.get("/no/such/route")
    bad_request = client.get("/_test/items/not-a-number")

    assert FAKE_KEY not in not_found.text
    assert FAKE_KEY not in bad_request.text
