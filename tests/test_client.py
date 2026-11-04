import logging
from types import SimpleNamespace
from typing import ClassVar

import pytest

import client
import config

FAKE_KEY = "sk-ant-fake-key-for-tests"


class FakeAnthropic:
    instances: ClassVar[list["FakeAnthropic"]] = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.calls: list[dict] = []
        self.response = make_response([text_block("hello")])
        self.messages = SimpleNamespace(create=self._create)
        FakeAnthropic.instances.append(self)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


def text_block(text):
    return SimpleNamespace(type="text", text=text)


def make_response(blocks, input_tokens=11, output_tokens=7, stop_reason="end_turn"):
    return SimpleNamespace(
        content=blocks,
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


@pytest.fixture(autouse=True)
def fake_sdk(monkeypatch):
    FakeAnthropic.instances = []
    monkeypatch.setattr(client.anthropic, "Anthropic", FakeAnthropic)
    monkeypatch.setattr(client, "_client", None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    # No .env file is read: settings come from the environment only.
    monkeypatch.setattr(config, "get_settings", lambda: config.Settings(_env_file=None))


def msgs(text="hi"):
    return [{"role": "user", "content": text}]


def test_import_creates_no_client():
    assert FakeAnthropic.instances == []
    assert client._client is None


def test_first_ask_creates_one_client_and_reuses_it():
    client.ask(msgs())
    client.ask(msgs())
    assert len(FakeAnthropic.instances) == 1
    assert len(FakeAnthropic.instances[0].calls) == 2


def test_constructor_has_timeout_and_bounded_retries():
    client.ask(msgs())
    kwargs = FakeAnthropic.instances[0].init_kwargs
    assert kwargs["timeout"] == client.TIMEOUT_SECONDS
    assert kwargs["max_retries"] == 2
    assert kwargs["api_key"] == FAKE_KEY


def test_request_kwargs_omit_optional_values_when_none():
    client.ask(msgs())
    call = FakeAnthropic.instances[0].calls[0]
    assert call["model"] == config.MODEL
    assert call["max_tokens"] == config.MAX_TOKENS
    assert call["messages"] == msgs()
    assert "temperature" not in call
    assert "system" not in call
    assert "stop_sequences" not in call


def test_request_kwargs_include_optional_values_when_given():
    client.ask(msgs(), system="be brief", temperature=0.0, stop_sequences=["END"])
    call = FakeAnthropic.instances[0].calls[0]
    assert call["system"] == "be brief"
    assert call["temperature"] == 0.0
    assert call["stop_sequences"] == ["END"]


def test_missing_key_raises_clear_error_without_key_text(monkeypatch, caplog):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        client.ask(msgs())
    assert FakeAnthropic.instances == []
    assert FAKE_KEY not in caplog.text


@pytest.mark.parametrize("blank", ["", "   "])
def test_empty_key_raises_clear_error(monkeypatch, blank):
    monkeypatch.setenv("ANTHROPIC_API_KEY", blank)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        client.ask(msgs())
    assert FakeAnthropic.instances == []
    assert client._client is None


def test_key_never_in_logs_or_errors(caplog):
    caplog.set_level(logging.DEBUG)
    client.ask(msgs())
    FakeAnthropic.instances[0].response = make_response([])
    with pytest.raises(RuntimeError) as exc:
        client.ask(msgs())
    assert FAKE_KEY not in str(exc.value)
    assert FAKE_KEY not in caplog.text


def test_text_blocks_are_concatenated_and_others_skipped():
    client.ask(msgs())
    fake = FakeAnthropic.instances[0]
    fake.response = make_response(
        [
            text_block("foo"),
            SimpleNamespace(type="thinking", text="x"),
            text_block("bar"),
        ]
    )
    assert client.ask(msgs()) == "foobar"


def test_empty_content_raises():
    client.ask(msgs())
    FakeAnthropic.instances[0].response = make_response([])
    with pytest.raises(RuntimeError, match="no text"):
        client.ask(msgs())


def test_max_tokens_stop_reason_raises_instead_of_returning_partial_text():
    client.ask(msgs())
    FakeAnthropic.instances[0].response = make_response(
        [text_block("cut off mid")], stop_reason="max_tokens"
    )
    with pytest.raises(RuntimeError, match="max_tokens"):
        client.ask(msgs())


def test_non_text_only_content_raises():
    client.ask(msgs())
    FakeAnthropic.instances[0].response = make_response(
        [SimpleNamespace(type="tool_use", id="t1")]
    )
    with pytest.raises(RuntimeError, match="no text"):
        client.ask(msgs())


def test_usage_log_has_tokens_and_latency_but_not_prompt(caplog):
    caplog.set_level(logging.INFO, logger="mnemo.client")
    client.ask(msgs("SECRET PROMPT TEXT"), system="SECRET SYSTEM TEXT")
    text = caplog.text
    assert "input_tokens=11" in text
    assert "output_tokens=7" in text
    assert "latency_ms=" in text
    assert "SECRET PROMPT TEXT" not in text
    assert "SECRET SYSTEM TEXT" not in text
