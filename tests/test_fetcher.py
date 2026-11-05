import json

import httpx2
import pytest
import trafilatura

import config
import fetcher
from fetcher import FetchFail, FetchOk, guard, page

HTML = b"<html><body><article><p>Hello reader, this is the page text.</p></article></body></html>"
HTML_HEADERS = {"content-type": "text/html; charset=utf-8"}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No real DNS, no real sleep, no token from a local .env."""
    monkeypatch.setattr(guard, "resolve", lambda host, port: ["93.184.216.34"])
    monkeypatch.setattr(page.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(config, "get_github_token", lambda: None)
    monkeypatch.setattr(trafilatura, "extract", lambda body, **kw: body.decode("utf-8"))


def transport(handler):
    return httpx2.MockTransport(handler)


def test_plain_page_returns_text():
    def handler(request):
        return httpx2.Response(200, headers=HTML_HEADERS, content=HTML)

    result = fetcher.fetch_page("https://example.com/a", transport(handler))
    assert isinstance(result, FetchOk)
    assert result.source == "web"
    assert "Hello reader" in result.text


def test_body_over_size_limit_fails(monkeypatch):
    monkeypatch.setattr(config, "FETCH_MAX_BYTES", 100)

    def handler(request):
        return httpx2.Response(200, headers=HTML_HEADERS, content=b"x" * 500)

    result = fetcher.fetch_page("https://example.com/big", transport(handler))
    assert result == FetchFail("page is too large")


def test_redirect_limit():
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx2.Response(302, headers={"location": f"/next{len(calls)}"})

    result = fetcher.fetch_page("https://example.com/start", transport(handler))
    assert result == FetchFail("too many redirects")
    assert len(calls) == config.FETCH_MAX_REDIRECTS + 1


def test_timeout_is_retried_then_fails():
    calls = []

    def handler(request):
        calls.append(1)
        raise httpx2.ReadTimeout("slow", request=request)

    result = fetcher.fetch_page("https://example.com/slow", transport(handler))
    assert isinstance(result, FetchFail)
    assert len(calls) == 2


def test_loopback_and_private_addresses_rejected(monkeypatch):
    hits = []

    def handler(request):
        hits.append(str(request.url))
        return httpx2.Response(200, headers=HTML_HEADERS, content=HTML)

    for address in (
        "127.0.0.1",
        "10.0.0.5",
        "169.254.169.254",
        "::1",
        "::ffff:192.168.1.1",
    ):
        monkeypatch.setattr(guard, "resolve", lambda host, port, a=address: [a])
        result = fetcher.fetch_page("https://example.com/x", transport(handler))
        assert result == FetchFail("address is not allowed"), address
    assert hits == []

    # A redirect hop to a private address is refused too.
    def resolve(host, port):
        return ["10.0.0.5"] if host == "internal.test" else ["93.184.216.34"]

    monkeypatch.setattr(guard, "resolve", resolve)

    def redirecting(request):
        hits.append(str(request.url))
        return httpx2.Response(
            302, headers={"location": "https://internal.test/secret"}
        )

    result = fetcher.fetch_page("https://example.com/r", transport(redirecting))
    assert result == FetchFail("address is not allowed")
    assert hits == ["https://example.com/r"]


def test_non_http_scheme_rejected():
    def handler(request):
        raise AssertionError("no request should be made")

    for url in (
        "ftp://example.com/a",
        "file:///etc/passwd",
        "https://user:pw@example.com/",
        "https://example.com:8080/",
    ):
        assert isinstance(fetcher.fetch_page(url, transport(handler)), FetchFail), url


def test_github_repo_uses_api_and_returns_description_and_readme():
    seen = []

    def handler(request):
        seen.append(request.url.path)
        assert request.url.host == "api.github.com"
        if request.url.path == "/repos/octo/hello":
            return httpx2.Response(
                200, content=json.dumps({"description": "A greeter"}).encode()
            )
        return httpx2.Response(200, content=b"# Hello\nUsage notes")

    result = fetcher.github.fetch_repo("octo", "hello", transport(handler))
    assert result == FetchOk(text="A greeter\n\n# Hello\nUsage notes", source="github")
    assert seen == ["/repos/octo/hello", "/repos/octo/hello/readme"]
    assert fetcher.github.parse_repo("https://github.com/octo/hello") == (
        "octo",
        "hello",
    )
    assert fetcher.github.parse_repo("https://github.com/octo/hello/issues") is None


def test_transient_error_retried_once():
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) == 1:
            return httpx2.Response(503)
        return httpx2.Response(200, headers=HTML_HEADERS, content=HTML)

    result = fetcher.fetch_page("https://example.com/flaky", transport(handler))
    assert isinstance(result, FetchOk)
    assert len(calls) == 2


def test_second_failure_returns_failure_and_404_is_not_retried():
    calls = []

    def handler(request):
        calls.append(1)
        return httpx2.Response(503)

    result = fetcher.fetch_page("https://example.com/down", transport(handler))
    assert result == FetchFail("server error 503")
    assert len(calls) == 2

    calls.clear()

    def missing(request):
        calls.append(1)
        return httpx2.Response(404)

    assert isinstance(
        fetcher.fetch_page("https://example.com/none", transport(missing)), FetchFail
    )
    assert len(calls) == 1


def test_trafilatura_receives_our_bytes_not_a_url(monkeypatch):
    received = []

    def extract(source, **kwargs):
        received.append(source)
        return "extracted text"

    monkeypatch.setattr(trafilatura, "extract", extract)

    def handler(request):
        return httpx2.Response(200, headers=HTML_HEADERS, content=HTML)

    result = fetcher.fetch_page("https://example.com/a", transport(handler))
    assert result == FetchOk(text="extracted text", source="web")
    assert received == [HTML]
