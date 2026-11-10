"""NAT64 unwrapping and the DNS time limit in the fetch address guard."""

import time

from mnemo.core import config
from mnemo.fetcher import guard


def test_nat64_loopback_is_refused():
    assert guard.is_allowed_address("64:ff9b::7f00:1") is False


def test_nat64_private_is_refused():
    assert guard.is_allowed_address("64:ff9b::a00:1") is False


def test_nat64_public_is_allowed():
    assert guard.is_allowed_address("64:ff9b::808:808") is True


def test_stalled_lookup_returns_a_reason(monkeypatch):
    def slow_resolve(host, port):
        time.sleep(0.5)
        return ["93.184.216.34"]

    monkeypatch.setattr(guard, "resolve", slow_resolve)
    monkeypatch.setattr(config, "FETCH_DNS_TIMEOUT", 0.05, raising=False)
    assert guard.check_host("https://example.com/") == "host lookup took too long"
