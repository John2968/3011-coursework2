"""Persistence helpers for compiled index files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SCHEMA_VERSION, InvertedIndex


DEFAULT_INDEX_PATH = Path("data") / "index.json"


class IndexStorageError(RuntimeError):
    """Raised when an index file cannot be saved or loaded safely."""


def save_index(index: InvertedIndex, path: Path | str = DEFAULT_INDEX_PATH) -> Path:
    """Save an inverted index as readable JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_path.write_text(
            json.dumps(index.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError as exc:
        raise IndexStorageError(f"Could not save index to {output_path}: {exc}") from exc
    return output_path


def load_index(path: Path | str = DEFAULT_INDEX_PATH) -> InvertedIndex:
    """Load an inverted index and validate the expected schema version."""

    input_path = Path(path)
    if not input_path.exists():
        raise IndexStorageError(
            f"Index file not found at {input_path}. Run 'build' before 'load'."
        )

    try:
        data: dict[str, Any] = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise IndexStorageError(f"Index file is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise IndexStorageError(f"Could not read index from {input_path}: {exc}") from exc

    metadata = data.get("metadata", {})
    schema_version = metadata.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise IndexStorageError(
            f"Unsupported index schema '{schema_version}'. Expected '{SCHEMA_VERSION}'."
        )

    return InvertedIndex.from_dict(data)

