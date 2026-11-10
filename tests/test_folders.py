"""The starter folder list and the one allowed-name check (FO-01 to FO-04)."""

from pathlib import Path

import config
import server


def test_starter_folders_are_the_five_names():
    assert config.STARTER_FOLDERS == (
        "Work",
        "Learning",
        "Reference",
        "Personal",
        "Ideas",
    )
    assert config.UNSORTED == "Unsorted"


def test_each_starter_folder_and_unsorted_are_allowed():
    for name in (*config.STARTER_FOLDERS, config.UNSORTED):
        assert config.is_allowed_folder(name) is True


def test_made_up_names_and_wrong_case_are_rejected():
    for name in ("Archive", "work", "WORK", "Unsorted ", "", None, 5):
        assert config.is_allowed_folder(name) is False


def test_server_uses_the_config_folder_list_and_the_doc_names_it():
    assert not hasattr(server, "UNSORTED_FOLDER")
    assert server.config.UNSORTED is config.UNSORTED
    doc = (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "feature-specs"
        / "folders.md"
    ).read_text(encoding="utf-8")
    for name in config.STARTER_FOLDERS:
        assert name in doc
    assert "Your final list: Open question" not in doc
