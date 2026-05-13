"""Build an inverted index from crawled pages."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime

from .models import CrawledPage, Document, InvertedIndex, Posting, TermEntry


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
PREVIEW_LENGTH = 160


def tokenize(text: str) -> list[str]:
    """Normalise text into lowercase tokens suitable for case-insensitive search."""

    return TOKEN_PATTERN.findall(text.lower())


def make_document_id(url: str) -> str:
    """Create a stable compact identifier for an indexed URL."""

    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


class InvertedIndexBuilder:
    """Constructs an inverted index with frequency and position statistics."""

    def build(self, pages: list[CrawledPage]) -> InvertedIndex:
        index = InvertedIndex(
            metadata={
                "source_site": "https://quotes.toscrape.com/",
                "created_at": datetime.now(UTC).isoformat(),
            }
        )

        for page in pages:
            self._add_page(index, page)

        return index

    def _add_page(self, index: InvertedIndex, page: CrawledPage) -> None:
        tokens = tokenize(page.text)
        doc_id = make_document_id(page.url)
        index.documents[doc_id] = Document(
            doc_id=doc_id,
            url=page.url,
            title=page.title.strip() or page.url,
            preview=self._make_preview(page.text),
            token_count=len(tokens),
        )

        seen_terms: set[str] = set()
        for position, token in enumerate(tokens):
            entry = index.terms.setdefault(token, TermEntry())
            posting = entry.postings.setdefault(doc_id, Posting(doc_id=doc_id))
            posting.add_position(position)
            if token not in seen_terms:
                entry.doc_freq += 1
                seen_terms.add(token)

    @staticmethod
    def _make_preview(text: str) -> str:
        collapsed = " ".join(text.split())
        if len(collapsed) <= PREVIEW_LENGTH:
            return collapsed
        return f"{collapsed[: PREVIEW_LENGTH - 3].rstrip()}..."

