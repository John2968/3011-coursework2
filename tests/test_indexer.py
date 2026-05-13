from src.indexer import InvertedIndexBuilder, make_document_id, tokenize
from src.models import CrawledPage


def test_tokenize_is_case_insensitive_and_handles_punctuation() -> None:
    assert tokenize("Good, GOOD! friend's 42") == ["good", "good", "friend's", "42"]


def test_build_index_stores_frequency_positions_and_document_metadata() -> None:
    pages = [
        CrawledPage(
            url="https://quotes.toscrape.com/",
            title="Home",
            text="Good friends are good company.",
        ),
        CrawledPage(
            url="https://quotes.toscrape.com/page/2/",
            title="Second",
            text="Friends make life good.",
        ),
    ]

    index = InvertedIndexBuilder().build(pages)
    first_doc_id = make_document_id("https://quotes.toscrape.com/")

    assert index.document_count == 2
    assert index.documents[first_doc_id].token_count == 5
    assert index.terms["good"].doc_freq == 2
    assert index.terms["good"].postings[first_doc_id].frequency == 2
    assert index.terms["good"].postings[first_doc_id].positions == [0, 3]
    assert "created_at" in index.metadata
    assert index.to_dict()["metadata"]["average_document_length"] == 4.5


def test_build_index_handles_empty_text() -> None:
    page = CrawledPage(url="https://example.com", title="", text="")

    index = InvertedIndexBuilder().build([page])

    doc_id = make_document_id("https://example.com")
    assert index.documents[doc_id].title == "https://example.com"
    assert index.documents[doc_id].preview == ""
    assert index.terms == {}

