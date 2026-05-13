from src.indexer import InvertedIndexBuilder
from src.models import CrawledPage
from src.search import SearchEngine


def make_engine() -> SearchEngine:
    index = InvertedIndexBuilder().build(
        [
            CrawledPage(
                url="https://quotes.toscrape.com/",
                title="Home",
                text="good good friends kindness",
            ),
            CrawledPage(
                url="https://quotes.toscrape.com/page/2/",
                title="Second",
                text="good choices courage",
            ),
        ]
    )
    return SearchEngine(index)


def test_find_returns_pages_containing_all_query_terms() -> None:
    results = make_engine().find("GOOD friends")

    assert len(results) == 1
    assert results[0].document.url == "https://quotes.toscrape.com/"
    assert results[0].term_frequencies == {"good": 2, "friends": 1}
    assert results[0].score > 0


def test_find_returns_empty_for_missing_or_empty_query() -> None:
    engine = make_engine()

    assert engine.find("not-in-index") == []
    assert engine.find("!!!") == []


def test_explain_term_lists_frequency_and_positions() -> None:
    lines = make_engine().explain_term("good")

    assert lines[0] == "Term: good"
    assert "Document frequency: 2" in lines
    assert any("freq=2" in line and "positions=[0, 1]" in line for line in lines)


def test_format_results_handles_empty_and_missing_queries() -> None:
    engine = make_engine()

    assert engine.format_results("!!!") == ["Please provide at least one search term."]
    assert engine.format_results("missing") == [
        "No pages found containing all terms: missing"
    ]


def test_search_requires_loaded_index() -> None:
    engine = SearchEngine()

    try:
        engine.find("good")
    except ValueError as exc:
        assert "No index loaded" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

