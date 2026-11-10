"""The ask tool loop (ticket #122). The Claude client is faked; no network."""

import copy
from types import SimpleNamespace

import pytest

import ask
import config
import store


@pytest.fixture(autouse=True)
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DATA_DIR", tmp_path)
    return tmp_path


def text_block(text: str):
    return SimpleNamespace(type="text", text=text)


def tool_block(tool_id: str, name: str, inputs: dict):
    return SimpleNamespace(type="tool_use", id=tool_id, name=name, input=inputs)


def response(stop_reason: str, blocks: list):
    return SimpleNamespace(stop_reason=stop_reason, content=blocks)


def fake_client(monkeypatch, responses: list) -> list:
    calls: list = []

    def create(messages, *, tools=None, system=None, model=None):
        calls.append(copy.deepcopy(messages))
        return responses.pop(0)

    monkeypatch.setattr(ask.client, "create_message", create)
    return calls


def test_one_tool_then_answer_makes_two_calls(monkeypatch):
    calls = fake_client(
        monkeypatch,
        [
            response(
                "tool_use", [tool_block("t1", "search_bookmarks", {"query": "brotli"})]
            ),
            response("end_turn", [text_block("Found one bookmark.")]),
        ],
    )

    result = ask.run_ask("What did I save about brotli?")

    assert len(calls) == 2
    assert result.text == "Found one bookmark."
    assert result.tool_calls == [
        {"name": "search_bookmarks", "input": {"query": "brotli"}}
    ]
    assert result.error is None


def test_two_tool_use_blocks_get_matching_results(monkeypatch):
    calls = fake_client(
        monkeypatch,
        [
            response(
                "tool_use",
                [
                    tool_block("t1", "search_bookmarks", {"query": "python"}),
                    tool_block("t2", "list_tags", {}),
                ],
            ),
            response("end_turn", [text_block("Done.")]),
        ],
    )

    ask.run_ask("Which tags do I have?")

    results = [
        block for block in calls[1][-1]["content"] if block["type"] == "tool_result"
    ]
    assert [block["tool_use_id"] for block in results] == ["t1", "t2"]
    assert all("is_error" not in block for block in results)


def test_tool_error_becomes_is_error_and_the_loop_ends(monkeypatch):
    calls = fake_client(
        monkeypatch,
        [
            response("tool_use", [tool_block("t1", "get_bookmark", {"id": 99})]),
            response("end_turn", [text_block("I could not find it.")]),
        ],
    )

    result = ask.run_ask("Show bookmark 99.")

    failed = calls[1][-1]["content"][0]
    assert failed["type"] == "tool_result"
    assert failed["tool_use_id"] == "t1"
    assert failed["is_error"] is True
    assert "no bookmark with id 99" in failed["content"]
    assert result.text == "I could not find it."


def test_unknown_tool_becomes_is_error(monkeypatch):
    calls = fake_client(
        monkeypatch,
        [
            response("tool_use", [tool_block("t1", "nope", {})]),
            response("end_turn", [text_block("I cannot do that.")]),
        ],
    )

    ask.run_ask("Try an unknown tool.")

    failed = calls[1][-1]["content"][0]
    assert failed["is_error"] is True
    assert "unknown tool: nope" in failed["content"]


def test_round_cap_stops_an_endless_tool_loop(monkeypatch):
    responses = [
        response("tool_use", [tool_block(f"t{i}", "list_tags", {})])
        for i in range(config.ASK_MAX_ROUNDS)
    ]
    calls = fake_client(monkeypatch, responses)

    result = ask.run_ask("Keep looking forever.")

    assert result.error == "too_many_rounds"
    assert len(calls) == config.ASK_MAX_ROUNDS
    assert len(result.tool_calls) == config.ASK_MAX_ROUNDS


def test_empty_question_is_refused_without_a_call(monkeypatch):
    def must_not_call(*args, **kwargs):
        pytest.fail("create_message must not be called")

    monkeypatch.setattr(ask.client, "create_message", must_not_call)

    with pytest.raises(ask.AskError, match="question is empty"):
        ask.run_ask("   ")
