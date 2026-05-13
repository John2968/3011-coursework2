import json

from src.indexer import InvertedIndexBuilder
from src.models import CrawledPage
from src.storage import IndexStorageError, load_index, save_index


def test_save_and_load_round_trip(tmp_path) -> None:
    index = InvertedIndexBuilder().build(
        [CrawledPage(url="https://example.com", title="Example", text="Good friends")]
    )
    path = tmp_path / "index.json"

    save_index(index, path)
    loaded = load_index(path)

    assert loaded.document_count == 1
    assert loaded.terms["good"].doc_freq == 1


def test_load_missing_file_reports_build_hint(tmp_path) -> None:
    try:
        load_index(tmp_path / "missing.json")
    except IndexStorageError as exc:
        assert "Run 'build'" in str(exc)
    else:
        raise AssertionError("Expected IndexStorageError")


def test_load_rejects_invalid_json(tmp_path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")

    try:
        load_index(path)
    except IndexStorageError as exc:
        assert "valid JSON" in str(exc)
    else:
        raise AssertionError("Expected IndexStorageError")


def test_load_rejects_unsupported_schema(tmp_path) -> None:
    path = tmp_path / "old-index.json"
    path.write_text(json.dumps({"metadata": {"schema_version": "0.1"}}), encoding="utf-8")

    try:
        load_index(path)
    except IndexStorageError as exc:
        assert "Unsupported index schema" in str(exc)
    else:
        raise AssertionError("Expected IndexStorageError")

