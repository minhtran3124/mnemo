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


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (403, "forbidden"),
        (409, "conflict"),
        (413, "payload_too_large"),
        (415, "unsupported_media_type"),
        (422, "unprocessable_entity"),
    ],
)
def test_http_statuses_get_a_matching_error_code(app, status, code):
    from fastapi import HTTPException

    @app.get(f"/_test/status/{status}")
    def raise_status() -> None:
        raise HTTPException(status_code=status, detail="Nope.")

    response = TestClient(app).get(f"/_test/status/{status}")

    assert response.status_code == status
    assert response.json() == {"error": {"code": code, "message": "Nope."}}


@pytest.mark.parametrize("detail", [{"path": "/etc/secret"}, ["a", "b"], 42])
def test_non_text_http_detail_never_reaches_the_response(app, detail):
    from fastapi import HTTPException

    @app.get("/_test/odd-detail")
    def raise_odd() -> None:
        raise HTTPException(status_code=409, detail=detail)

    response = TestClient(app).get("/_test/odd-detail")

    assert response.status_code == 409
    assert response.json() == {
        "error": {"code": "conflict", "message": "The request could not be completed."}
    }


def test_unhandled_error_logs_type_and_frames_but_never_the_message(app, caplog):
    @app.get("/_test/boom")
    def boom() -> None:
        detail = "secret cause " + "detail " + FAKE_KEY
        raise ValueError(detail)

    with caplog.at_level("ERROR", logger="server"):
        response = TestClient(app, raise_server_exceptions=False).get("/_test/boom")

    assert response.status_code == 500
    assert "ValueError" not in response.text
    assert "secret cause detail" not in response.text
    records = [r for r in caplog.records if r.name == "server"]
    assert len(records) == 1
    assert records[0].exc_info is None
    assert "ValueError" in caplog.text
    assert "boom" in caplog.text
    assert "secret cause detail" not in caplog.text
    assert FAKE_KEY not in caplog.text


def test_unhandled_error_gives_500_error_format(app):
    @app.get("/_test/crash")
    def crash() -> None:
        raise RuntimeError("internal detail")

    response = TestClient(app, raise_server_exceptions=False).get("/_test/crash")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "server_error",
            "message": "Something went wrong on the server.",
        }
    }


def test_unhandled_error_message_holding_the_api_key_never_reaches_the_response(app):
    @app.get("/_test/key-in-error")
    def leak() -> None:
        raise RuntimeError(f"upstream rejected key {FAKE_KEY}")

    response = TestClient(app, raise_server_exceptions=False).get("/_test/key-in-error")

    assert response.status_code == 500
    assert FAKE_KEY not in response.text
    assert "upstream rejected" not in response.text


def test_http_exception_message_holding_the_api_key_is_not_a_route_message_leak(app):
    from fastapi import HTTPException

    @app.get("/_test/odd-key")
    def raise_key() -> None:
        raise HTTPException(status_code=409, detail={"key": FAKE_KEY})

    response = TestClient(app).get("/_test/odd-key")

    assert response.status_code == 409
    assert FAKE_KEY not in response.text


def test_wrong_method_gives_405_error_format(client):
    response = client.post("/_test/items/1")

    assert response.status_code == 405
    assert response.json() == {
        "error": {
            "code": "method_not_allowed",
            "message": "Method Not Allowed",
        }
    }


def test_http_exception_with_plain_text_detail_passes_through(app):
    from fastapi import HTTPException

    @app.get("/_test/teapot")
    def teapot() -> None:
        raise HTTPException(status_code=400, detail="Bad link.")

    response = TestClient(app).get("/_test/teapot")

    assert response.status_code == 400
    assert response.json() == {"error": {"code": "bad_request", "message": "Bad link."}}


def test_every_mapped_status_has_a_row_in_the_server_api_spec():
    import re
    from pathlib import Path

    import server

    spec = Path(__file__).parent.parent / "docs/feature-specs/server-api.md"
    text = spec.read_text()
    for status in server._HTTP_CODES:
        assert re.search(rf"^\| {status} \|", text, re.MULTILINE), status


@pytest.mark.parametrize("status", [500, 502, 503])
def test_server_error_http_detail_never_reaches_the_response(app, status):
    from fastapi import HTTPException

    @app.get("/_test/server-detail")
    def raise_server() -> None:
        raise HTTPException(status_code=status, detail="failed at /home/x/data.json")

    response = TestClient(app).get("/_test/server-detail")

    assert response.status_code == status
    assert "/home/x" not in response.text
    assert response.json() == {
        "error": {
            "code": "server_error",
            "message": "Something went wrong on the server.",
        }
    }


def test_wrong_method_keeps_the_allow_header(client):
    response = client.post("/_test/items/1")

    assert response.status_code == 405
    assert "GET" in response.headers["allow"]


def test_http_exception_headers_are_kept(app):
    from fastapi import HTTPException

    @app.get("/_test/locked")
    def locked() -> None:
        raise HTTPException(
            status_code=401, detail="Sign in.", headers={"WWW-Authenticate": "Bearer"}
        )

    response = TestClient(app).get("/_test/locked")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
