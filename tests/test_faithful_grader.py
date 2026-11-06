"""The faithful-summary model grader, with Claude mocked (no network)."""

from pathlib import Path

import client
import config
from evals import faithful

PAGE = "Mnemo saves links. It stores them as plain files."
SUMMARY = "Mnemo saves links as plain files."
KEY_FACTS = ["saves links", "uses a database", "plain files"]
USAGE = client.Usage(10, 5)


def fake_parse(outputs, calls):
    queue = list(outputs)

    def parse_with_usage(messages, output_format, system=None, model=None):
        calls.append({"messages": messages, "system": system, "model": model})
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item, USAGE

    return parse_with_usage


def test_no_unsupported_statements_passes(monkeypatch):
    out = faithful.FaithfulOutput(unsupported=[], key_fact_results=[True, False, True])
    monkeypatch.setattr(client, "parse_with_usage", fake_parse([out], []))
    result = faithful.grade_faithful(PAGE, SUMMARY, KEY_FACTS)
    assert result.passed is True
    assert result.unsupported_count == 0
    assert result.grader_failed is False


def test_two_unsupported_statements_fail_with_reasons(monkeypatch):
    reasons = ["It is free: not in the page.", "It uses AI: not in the page."]
    out = faithful.FaithfulOutput(
        unsupported=reasons, key_fact_results=[True, False, True]
    )
    monkeypatch.setattr(client, "parse_with_usage", fake_parse([out], []))
    result = faithful.grade_faithful(PAGE, SUMMARY, KEY_FACTS)
    assert result.passed is False
    assert result.unsupported_count == 2
    assert result.unsupported == reasons


def test_key_fact_answers_follow_key_fact_order(monkeypatch):
    out = faithful.FaithfulOutput(unsupported=[], key_fact_results=[True, False, True])
    monkeypatch.setattr(client, "parse_with_usage", fake_parse([out], []))
    result = faithful.grade_faithful(PAGE, SUMMARY, KEY_FACTS)
    assert result.key_facts == [True, False, True]


def test_call_uses_grader_model_and_prompt_has_screenshot_rule(monkeypatch):
    calls = []
    out = faithful.FaithfulOutput(unsupported=[], key_fact_results=[True, False, True])
    monkeypatch.setattr(client, "parse_with_usage", fake_parse([out], calls))
    faithful.grade_faithful(PAGE, SUMMARY, KEY_FACTS)
    assert calls[0]["model"] == config.EVAL_GRADER_MODEL
    prompt = Path(faithful.PROMPT_FILE).read_text(encoding="utf-8")
    assert "not visible in the image text" in prompt
    assert calls[0]["system"] == prompt


def test_invalid_output_twice_gives_grader_failed(monkeypatch):
    calls = []
    errors = [client.InvalidOutput("bad"), client.InvalidOutput("bad")]
    monkeypatch.setattr(client, "parse_with_usage", fake_parse(errors, calls))
    result = faithful.grade_faithful(PAGE, SUMMARY, KEY_FACTS)
    assert result.grader_failed is True
    assert result.passed is False
    assert result.unsupported_count is None
    assert len(calls) == 2
