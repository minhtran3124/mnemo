"""Tests for .githooks/pre-commit, run against a throwaway git repo."""

import subprocess
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / ".githooks" / "pre-commit"


def fake_key() -> str:
    # Built at runtime so no key-like literal exists in this file.
    return "sk-" + "ant-" + "A1b2C3d4" * 4


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=False, capture_output=True, text=True
    )


def run_hook(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["sh", str(HOOK)], cwd=repo, check=False, capture_output=True, text=True
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "t")
    return tmp_path


def stage(repo: Path, name: str, text: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    git(repo, "add", name)


def test_key_on_added_line_is_blocked_without_echoing_it(repo):
    key = fake_key()
    stage(repo, "a.txt", f"ok\nsecret = {key}\n")
    result = run_hook(repo)
    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "a.txt:2" in output
    assert key not in output
    assert "sk-ant" not in output


@pytest.mark.parametrize(
    "name",
    [
        ".env",
        ".env.example",
        ".env.example.bak",
        "sub/dir/.env.local",
        "sub/dir/.env.example",
    ],
)
def test_env_files_are_blocked(repo, name):
    stage(repo, name, "NOTHING=1\n")
    result = run_hook(repo)
    assert result.returncode != 0
    assert name in result.stderr


def test_clean_commit_passes(repo):
    stage(repo, "a.txt", "hello\n")
    stage(repo, "env.txt", "not an env file\n")
    result = run_hook(repo)
    assert result.returncode == 0


def test_removing_a_key_passes(repo):
    key = fake_key()
    stage(repo, "a.txt", f"{key}\n")
    git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "seed")
    stage(repo, "a.txt", "clean\n")
    result = run_hook(repo)
    assert result.returncode == 0


def test_key_on_line_starting_with_plus_plus_space_is_blocked(repo):
    # The added line "++ <key>" shows up in the diff as "+++ <key>", which must
    # not be mistaken for a file header.
    key = fake_key()
    stage(repo, "a.txt", f"++ {key}\n")
    result = run_hook(repo)
    assert result.returncode != 0
    assert "a.txt:1" in result.stderr
    assert key not in result.stdout + result.stderr


def test_location_is_right_with_noprefix_and_odd_names(repo):
    git(repo, "config", "diff.noprefix", "true")
    key = fake_key()
    stage(repo, "dir/my café file.txt", f"ok\n{key}\n")
    result = run_hook(repo)
    assert result.returncode != 0
    assert "dir/my café file.txt:2" in result.stderr
    assert key not in result.stdout + result.stderr


def test_tech_stack_doc_says_hook_is_implemented() -> None:
    doc = HOOK.parent.parent / "docs" / "product" / "tech-stack.md"
    secrets = next(
        line
        for line in doc.read_text().splitlines()
        if line.startswith("- **Secrets:**")
    )
    assert ".githooks/pre-commit" in secrets
    assert "is listed in" not in secrets


@pytest.mark.parametrize(
    "name",
    ["tài liệu/.env", "tài liệu/.env.example", "dir/.env\tbak", 'q"uote/.env'],
)
def test_env_files_with_odd_paths_are_blocked(repo, name):
    # Git C-quotes a path with a tab, a quote or non-ASCII letters unless the
    # hook reads raw names with -z, and a quoted basename would not match.
    stage(repo, name, "ANTHROPIC_API_KEY=\n")
    result = run_hook(repo)
    assert result.returncode != 0
    assert f"staged file name starts with .env: {name}" in result.stderr


def test_staged_deletion_of_env_file_is_blocked(repo):
    stage(repo, ".env", "NOTHING=1\n")
    git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "seed")
    git(repo, "rm", "-q", "--cached", ".env")
    result = run_hook(repo)
    assert result.returncode != 0
    assert "staged file name starts with .env: .env\n" in result.stderr


def test_rename_of_env_file_is_blocked(repo):
    stage(repo, ".env", "NOTHING=1\n")
    git(repo, "-c", "core.hooksPath=/dev/null", "commit", "-qm", "seed")
    git(repo, "mv", ".env", "config.bak")
    result = run_hook(repo)
    assert result.returncode != 0
    assert "staged file name starts with .env: .env\n" in result.stderr
