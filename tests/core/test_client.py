import inspect
import logging
from types import SimpleNamespace
from typing import ClassVar

import anthropic
import pytest
from pydantic import BaseModel

from mnemo.core import client, config

FAKE_KEY = "sk-ant-fake-key-for-tests"


class FakeAnthropic:
    instances: ClassVar[list["FakeAnthropic"]] = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.calls: list[dict] = []
        self.response = make_response([text_block("hello")])
        self.parse_response = make_parse_response(Note(title="t"))
        self.messages = SimpleNamespace(create=self._create, parse=self._parse)
        FakeAnthropic.instances.append(self)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self.response

    def _parse(self, **kwargs):
        self.calls.append(kwargs)
        return self.parse_response


class Note(BaseModel):
    title: str


def text_block(text):
    return SimpleNamespace(type="text", text=text)


def make_response(blocks, input_tokens=11, output_tokens=7, stop_reason="end_turn"):
    return SimpleNamespace(
        content=blocks,
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
    )


def make_parse_response(parsed, stop_reason="end_turn"):
    resp = make_response([], stop_reason=stop_reason)
    resp.parsed_output = parsed
    return resp


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


def test_ask_kwargs_match_real_signature():
    dummies = {
        "messages": msgs(),
        "system": "be brief",
        "stop_sequences": ["END"],
        "temperature": 0.0,
    }
    ask_params = inspect.signature(client.ask).parameters
    client.ask(**{name: dummies[name] for name in ask_params})
    sent = FakeAnthropic.instances[0].calls[0]
    real = inspect.signature(anthropic.resources.messages.Messages.create).parameters
    assert set(sent) <= set(real)
    # Current models reject a temperature argument, so ask() must never send one.
    assert "temperature" not in sent


def test_request_kwargs_include_optional_values_when_given():
    client.ask(msgs(), system="be brief", stop_sequences=["END"])
    call = FakeAnthropic.instances[0].calls[0]
    assert call["system"] == "be brief"
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


def test_max_tokens_stop_reason_returns_text_and_logs_a_warning(caplog):
    client.ask(msgs())
    FakeAnthropic.instances[0].response = make_response(
        [text_block("cut off mid")], stop_reason="max_tokens"
    )
    with caplog.at_level("WARNING", logger="mnemo.client"):
        assert client.ask(msgs()) == "cut off mid"
    assert "max_tokens" in caplog.text


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


def _parse_fake():
    client.parse(msgs(), Note)
    return FakeAnthropic.instances[0]


def test_parse_returns_parsed_output(caplog):
    caplog.set_level(logging.INFO, logger="mnemo.client")
    result = client.parse(msgs(), Note, system="be brief")
    assert result == Note(title="t")
    call = FakeAnthropic.instances[0].calls[0]
    assert call["output_format"] is Note
    assert call["system"] == "be brief"
    assert "input_tokens=11" in caplog.text


@pytest.mark.parametrize("reason", ["refusal", "max_tokens"])
def test_parse_bad_stop_reason_raises_without_key(reason, caplog):
    caplog.set_level(logging.DEBUG)
    _parse_fake()
    FakeAnthropic.instances[0].parse_response = make_parse_response(
        Note(title="t"), stop_reason=reason
    )
    with pytest.raises(RuntimeError, match="refused|max_tokens") as exc:
        client.parse(msgs(), Note)
    assert FAKE_KEY not in str(exc.value)
    assert FAKE_KEY not in caplog.text


def test_parse_sends_no_prefill_stop_sequences_or_beta_header():
    fake = _parse_fake()
    call = fake.calls[0]
    assert "system" not in call
    assert "stop_sequences" not in call
    assert "extra_headers" not in call
    assert "betas" not in call
    assert call["messages"][-1]["role"] == "user"
    assert "anthropic-beta" not in fake.init_kwargs.get("default_headers", {})


def test_parse_kwargs_match_real_signature():
    parse_params = inspect.signature(client.parse).parameters
    dummies = {"messages": msgs(), "output_format": Note, "system": "be brief"}
    client.parse(**{name: dummies[name] for name in parse_params})
    sent = FakeAnthropic.instances[0].calls[0]
    real = inspect.signature(anthropic.resources.messages.Messages.parse).parameters
    assert set(sent) <= set(real)
