import time

import pytest

from src.indexer import InvertedIndexBuilder
from src.models import CrawledPage
from src.search import SearchEngine


@pytest.mark.performance
def test_indexing_and_search_are_fast_for_simulated_pages() -> None:
    pages = [
        CrawledPage(
            url=f"https://quotes.toscrape.com/page/{page_number}/",
            title=f"Page {page_number}",
            text=(
                "good friends courage wisdom "
                f"unique{page_number} "
                "good search data structure"
            ),
        )
        for page_number in range(300)
    ]

    start = time.perf_counter()
    index = InvertedIndexBuilder().build(pages)
    results = SearchEngine(index).find("good friends")
    elapsed = time.perf_counter() - start

    assert len(results) == 10
    assert index.document_count == 300
    assert elapsed < 2.0

