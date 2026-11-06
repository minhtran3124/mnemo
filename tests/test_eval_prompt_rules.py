"""The faithful grader prompt carries the hosting-fact and index-page rules."""

from pathlib import Path

PROMPT = Path(__file__).resolve().parent.parent / "prompts" / "eval_faithful.txt"

PAGE_KIND_RULE = (
    "The kind of page is supported by its address and layout: a repository page "
    "supports 'a repository', and a page that is a list supports 'a list' or 'an index'."
)
LIST_ITEM_RULE = "A claim about an item in a list is supported only when the list shows that item."


def test_prompt_has_page_kind_rule():
    assert PAGE_KIND_RULE in PROMPT.read_text(encoding="utf-8")


def test_prompt_has_list_item_rule():
    assert LIST_ITEM_RULE in PROMPT.read_text(encoding="utf-8")
