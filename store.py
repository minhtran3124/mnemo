"""The only reader and writer of Mnemo's data files (NF-03, D-012).

Files: data/bookmarks.json, data/pages/<id>.txt, data/chat.jsonl, data/log.jsonl.
Record shape: docs/feature-specs/data-model.md. Rules: docs/feature-specs/storage.md.

bookmarks.json holds {"next_id": n, "bookmarks": [...]}. The counter only goes
up, so an id is never reused after a delete. No lock yet: two writers at once
is an open question in storage.md.
"""

import json
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Read at call time, so tests can point it at a temp folder.
DATA_DIR = Path(__file__).resolve().parent / "data"

TYPES = {"github_repo", "article", "video_page", "tool", "pdf", "image", "note"}
PAGE_STATUSES = {"ok", "unreadable"}
REASON_SOURCES = {"user", "guess"}
MIN_TAGS = 3
MAX_TAGS = 6
MAX_SUMMARY_WORDS = 60

# Fields the caller gives. The server adds id, saved_at and page_file.
CALLER_FIELDS = (
    "url",
    "url_clean",
    "type",
    "title",
    "page_status",
    "summary",
    "tags",
    "reason",
    "reason_source",
    "folder",
    "opened_count",
)
SERVER_FIELDS = ("id", "saved_at", "page_file")
ALL_FIELDS = SERVER_FIELDS + CALLER_FIELDS


class StoreError(Exception):
    """Base class for storage failures."""


class InvalidRecord(StoreError, ValueError):
    """A record does not match data-model.md. Nothing was written."""


class NotFound(StoreError):
    """No bookmark has this id."""


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S")


def _paths() -> tuple[Path, Path, Path, Path]:
    return (
        DATA_DIR / "bookmarks.json",
        DATA_DIR / "pages",
        DATA_DIR / "chat.jsonl",
        DATA_DIR / "log.jsonl",
    )


def _atomic_write(path: Path, text: str) -> None:
    """Write a temp file in the same folder, fsync, then rename over the target."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_record(record: dict[str, Any]) -> None:
    """Raise InvalidRecord if the record breaks data-model.md."""
    if not isinstance(record, dict):
        raise InvalidRecord("record must be a dict")
    missing = [name for name in ALL_FIELDS if name not in record]
    if missing:
        raise InvalidRecord(f"missing fields: {', '.join(missing)}")
    unknown = sorted(set(record) - set(ALL_FIELDS))
    if unknown:
        raise InvalidRecord(f"unknown fields: {', '.join(unknown)}")

    if not _is_int(record["id"]):
        raise InvalidRecord("id must be an integer")
    for name in ("url", "url_clean", "saved_at", "title", "reason", "page_file"):
        if not isinstance(record[name], str):
            raise InvalidRecord(f"{name} must be a string")
    if record["type"] not in TYPES:
        raise InvalidRecord(f"type must be one of {sorted(TYPES)}")
    if record["page_status"] not in PAGE_STATUSES:
        raise InvalidRecord("page_status must be 'ok' or 'unreadable'")
    if record["reason_source"] not in REASON_SOURCES:
        raise InvalidRecord("reason_source must be 'user' or 'guess'")
    if record["folder"] is not None and not isinstance(record["folder"], str):
        raise InvalidRecord("folder must be a string or null")
    if not _is_int(record["opened_count"]) or record["opened_count"] < 0:
        raise InvalidRecord("opened_count must be an integer, 0 or more")

    tags = record["tags"]
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise InvalidRecord("tags must be a list of strings")
    if any(t != t.lower() for t in tags):
        raise InvalidRecord("tags must be lowercase")

    summary = record["summary"]
    if record["page_status"] == "unreadable":
        if summary is not None:
            raise InvalidRecord("an unreadable record must have a null summary")
        if len(tags) > MAX_TAGS:
            raise InvalidRecord(f"at most {MAX_TAGS} tags")
    else:
        if not isinstance(summary, str):
            raise InvalidRecord("a readable record needs a summary string")
        if len(summary.split()) > MAX_SUMMARY_WORDS:
            raise InvalidRecord(f"summary is over {MAX_SUMMARY_WORDS} words")
        if not MIN_TAGS <= len(tags) <= MAX_TAGS:
            raise InvalidRecord(
                f"a readable record needs {MIN_TAGS} to {MAX_TAGS} tags"
            )


def _load() -> dict[str, Any]:
    path = _paths()[0]
    if not path.exists():
        return {"next_id": 1, "bookmarks": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not (
            isinstance(data, dict)
            and _is_int(data.get("next_id"))
            and isinstance(data.get("bookmarks"), list)
        ):
            raise ValueError("unexpected layout")
    except ValueError as exc:
        raise StoreError(
            f"{path} is corrupt ({exc}). Restore it from a backup; it was not changed."
        ) from exc
    return data


def _save(data: dict[str, Any]) -> None:
    _atomic_write(_paths()[0], json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def _page_path(bookmark_id: int) -> Path:
    return _paths()[1] / f"{bookmark_id}.txt"


def add_bookmark(
    record: dict[str, Any], page_text: str | None = None
) -> dict[str, Any]:
    """Validate and add a bookmark. The server sets id, saved_at and page_file."""
    unknown = sorted(set(record) - set(CALLER_FIELDS))
    if unknown:
        raise InvalidRecord(f"caller may not set: {', '.join(unknown)}")
    data = _load()
    new_id = data["next_id"]
    full = {
        "id": new_id,
        "saved_at": _now(),
        "page_file": f"data/pages/{new_id}.txt",
        **record,
    }
    validate_record(full)
    if page_text is not None:
        _atomic_write(_page_path(new_id), page_text)
    data["bookmarks"].append(full)
    data["next_id"] = new_id + 1
    _save(data)
    return full


def get_bookmark(bookmark_id: int) -> dict[str, Any] | None:
    for item in _load()["bookmarks"]:
        if item["id"] == bookmark_id:
            return item
    return None


def list_bookmarks(filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return records in saved order. Filters: folder, type, tag."""
    filters = filters or {}
    unknown = sorted(set(filters) - {"folder", "type", "tag"})
    if unknown:
        raise ValueError(f"unknown filters: {', '.join(unknown)}")
    result = []
    for item in _load()["bookmarks"]:
        if "folder" in filters and item["folder"] != filters["folder"]:
            continue
        if "type" in filters and item["type"] != filters["type"]:
            continue
        if "tag" in filters and filters["tag"] not in item["tags"]:
            continue
        result.append(item)
    return result


def update_bookmark(bookmark_id: int, fields: dict[str, Any]) -> dict[str, Any]:
    """Change fields and re-validate. id, saved_at and page_file cannot change."""
    locked = sorted(set(fields) & set(SERVER_FIELDS))
    if locked:
        raise InvalidRecord(f"cannot change: {', '.join(locked)}")
    data = _load()
    for index, item in enumerate(data["bookmarks"]):
        if item["id"] == bookmark_id:
            updated = {**item, **fields}
            validate_record(updated)
            data["bookmarks"][index] = updated
            _save(data)
            return updated
    raise NotFound(f"no bookmark with id {bookmark_id}")


def delete_bookmark(bookmark_id: int) -> None:
    """Remove the record and its page file. The id is not given out again."""
    data = _load()
    kept = [item for item in data["bookmarks"] if item["id"] != bookmark_id]
    if len(kept) == len(data["bookmarks"]):
        raise NotFound(f"no bookmark with id {bookmark_id}")
    data["bookmarks"] = kept
    _save(data)
    _page_path(bookmark_id).unlink(missing_ok=True)


def list_folders() -> list[dict[str, Any]]:
    """Named folders with counts, sorted by name. Unsorted (null) is not listed."""
    counts: dict[str, int] = {}
    for item in _load()["bookmarks"]:
        if item["folder"] is not None:
            counts[item["folder"]] = counts.get(item["folder"], 0) + 1
    return [{"folder": name, "count": counts[name]} for name in sorted(counts)]


def find_by_url_clean(url_clean: str) -> dict[str, Any] | None:
    """Return the first bookmark with this cleaned link, or None. Empty never matches."""
    if not url_clean:
        return None
    for item in _load()["bookmarks"]:
        if item["url_clean"] == url_clean:
            return item
    return None


def read_page(bookmark_id: int) -> str | None:
    """Return the saved page text, or None if the file is missing."""
    path = _page_path(bookmark_id)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _read_lines(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        return [json.loads(line) for line in lines if line.strip()]
    except ValueError as exc:
        raise StoreError(f"{path} has a line that is not JSON ({exc}).") from exc


def _append_line(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def append_chat(message: dict[str, Any]) -> dict[str, Any]:
    """Append one chat line. The server sets id (counts on from the last line) and time."""
    if message.get("role") not in {"user", "app"}:
        raise InvalidRecord("role must be 'user' or 'app'")
    if not isinstance(message.get("text"), str):
        raise InvalidRecord("text must be a string")
    ids = message.get("bookmark_ids", [])
    if not isinstance(ids, list) or not all(_is_int(i) for i in ids):
        raise InvalidRecord("bookmark_ids must be a list of integers")
    path = _paths()[2]
    existing = _read_lines(path)
    next_id = existing[-1]["id"] + 1 if existing else 1
    line = {
        "id": next_id,
        "time": _now(),
        "role": message["role"],
        "text": message["text"],
        "bookmark_ids": ids,
    }
    _append_line(path, line)
    return line


def list_chat(limit: int = 50) -> list[dict[str, Any]]:
    """Return the latest messages, oldest first."""
    if limit <= 0:
        return []
    return _read_lines(_paths()[2])[-limit:]


def log_event(event: dict[str, Any]) -> dict[str, Any]:
    """Append one event line. The server sets time."""
    if not isinstance(event.get("event"), str) or not event["event"]:
        raise InvalidRecord("event needs an 'event' name")
    line = {**event, "time": _now()}
    _append_line(_paths()[3], line)
    return line
