from types import SimpleNamespace

import pytest
from pydantic import BaseModel

import client
import config

FAKE_KEY = "sk-ant-fake-key-for-tests"


class Note(BaseModel):
    title: str


class FakeAnthropic:
    last: "FakeAnthropic | None" = None

    def __init__(self, **kwargs):
        self.calls: list[dict] = []
        self.stop_reason = "end_turn"
        self.messages = SimpleNamespace(parse=self._parse)
        FakeAnthropic.last = self

    def _parse(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            stop_reason=self.stop_reason,
            parsed_output=Note(title="t"),
            usage=SimpleNamespace(input_tokens=11, output_tokens=7),
        )


@pytest.fixture(autouse=True)
def fake_sdk(monkeypatch):
    monkeypatch.setattr(client.anthropic, "Anthropic", FakeAnthropic)
    monkeypatch.setattr(client, "_client", None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(config, "get_settings", lambda: config.Settings(_env_file=None))


MSGS = [{"role": "user", "content": "hi"}]


def test_parse_with_usage_returns_object_and_token_counts():
    parsed, usage = client.parse_with_usage(MSGS, Note)
    assert parsed == Note(title="t")
    assert usage == client.Usage(input_tokens=11, output_tokens=7)


def test_model_argument_reaches_sdk_and_default_is_config_model():
    client.parse_with_usage(MSGS, Note, model="other-model")
    assert FakeAnthropic.last.calls[0]["model"] == "other-model"
    client.parse_with_usage(MSGS, Note)
    assert FakeAnthropic.last.calls[1]["model"] == config.MODEL


def test_parse_returns_only_object_and_refusal_still_raises():
    assert client.parse(MSGS, Note) == Note(title="t")
    FakeAnthropic.last.stop_reason = "refusal"
    with pytest.raises(client.InvalidOutput):
        client.parse(MSGS, Note)
