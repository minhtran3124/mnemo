import importlib.util
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

import pytest

import client
import config

FAKE_KEY = "sk-ant-fake-key-for-tests"
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "check_memory.py"

spec = importlib.util.spec_from_file_location("check_memory", SCRIPT)
check_memory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_memory)


class FakeAnthropic:
    """Stands in for the SDK. Replies come from `replies`, one per request."""

    replies: ClassVar[list[str]] = []
    calls: ClassVar[list[dict]] = []

    def __init__(self, **kwargs):
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        # Copy the messages: the script reuses one list for both calls.
        FakeAnthropic.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        text = FakeAnthropic.replies[len(FakeAnthropic.calls) - 1]
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=text)],
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        )


@pytest.fixture(autouse=True)
def fake_sdk(monkeypatch):
    FakeAnthropic.calls = []
    FakeAnthropic.replies = []
    monkeypatch.setattr(client.anthropic, "Anthropic", FakeAnthropic)
    monkeypatch.setattr(client, "_client", None)
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(config, "get_settings", lambda: config.Settings(_env_file=None))


def test_pass_when_second_answer_has_the_word(capsys):
    FakeAnthropic.replies = ["Got it.", f"It was {check_memory.CODE_WORD}."]
    assert check_memory.main() == 0
    out = capsys.readouterr().out
    assert "call 1: Got it." in out
    assert "memory check: PASS" in out


def test_fail_when_second_answer_lacks_the_word(capsys):
    FakeAnthropic.replies = ["Got it.", "I do not know."]
    assert check_memory.main() == 1
    assert "memory check: FAIL" in capsys.readouterr().out


def test_exactly_two_requests_with_max_tokens():
    FakeAnthropic.replies = ["Got it.", check_memory.CODE_WORD]
    check_memory.main()
    assert len(FakeAnthropic.calls) == 2
    assert all(c["max_tokens"] == config.MAX_TOKENS for c in FakeAnthropic.calls)


def test_call_two_carries_call_one_history():
    FakeAnthropic.replies = ["Got it.", check_memory.CODE_WORD]
    check_memory.main()
    first, second = FakeAnthropic.calls
    assert check_memory.CODE_WORD in first["messages"][0]["content"]
    assert second["messages"][:2] == [
        {"role": "user", "content": check_memory.TELL},
        {"role": "assistant", "content": "Got it."},
    ]
    assert second["messages"][2] == {"role": "user", "content": check_memory.ASK}


def test_no_key_exits_2_without_an_sdk_call(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY")
    assert check_memory.main() == 2
    out = capsys.readouterr()
    assert "ANTHROPIC_API_KEY" in out.out
    assert FAKE_KEY not in out.out + out.err
    assert FakeAnthropic.calls == []


def test_other_runtime_error_is_not_swallowed(monkeypatch):
    def boom(messages):
        raise RuntimeError("Claude returned no text")

    monkeypatch.setattr(client, "ask", boom)
    with pytest.raises(RuntimeError, match="no text"):
        check_memory.main()
